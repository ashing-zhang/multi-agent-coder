from typing import AsyncGenerator
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from .base_agent import BaseAgent, AgentState
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_openai import ChatOpenAI

class SingleNode(BaseAgent):
    """
    单节点Agent，继承自BaseAgent。
    """

    def __init__(self, llm: ChatOpenAI, system_message="You are a helpful AI assistant."):
        """
        初始化SingleNode。
        
        Args:
            llm: LLM模型实例
            system_message: 系统消息
        """
        super().__init__(llm)   
        self.system_message = system_message
        
        # 创建提示模板
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("placeholder", "{messages}"),
        ])
        
        # 初始化工作流组件
        self.memory = MemorySaver()
        self.app = None  # 将在initialize方法中编译
        self.tools = None
        self.llm_with_tools = None
        self.agent = None
        self.workflow = None
    
    async def initialize(self):
        """
        初始化工作流，编译图，并预热LLM连接。
        """
        print("开始初始化 SingleNode。")
        # 加载context7工具
        print("准备加载 context7 工具。")
        self.tools = await self._load_context7_tools_async()
        print("工具加载成功:")
        for tool in self.tools:
            print(f"  - {tool.name}")
        # 将工具绑定到LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # 更新Agent以使用带有工具的LLM
        self.agent = self.prompt | self.llm_with_tools
        
        # 更新工作流中的节点
        self.workflow = StateGraph(AgentState)
        self.workflow.add_node("agent", self.agent)
        self.workflow.add_edge(START, "agent")
        self.workflow.add_edge("agent", END)
        
        self.memory = MemorySaver()
        self.app = self.workflow.compile(checkpointer=self.memory)
        print("SingleNode 初始化完成。")
    
    async def _load_context7_tools_async(self):
        """异步加载context7工具"""
        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@upstash/context7-mcp"]
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await load_mcp_tools(session)
                return tools

    async def handle_message(self, content: str) -> str:
        """
        处理消息并返回响应。
        
        Args:
            content: 用户输入的消息内容
            
        Returns:
            str: Agent的响应
        """
        if not self.app:
            raise ValueError("工作流未初始化")
            
        initial_state = {"messages": [HumanMessage(content=content)]}
        config = {"configurable": {"thread_id": "SingleNode"}}
        result = await self.app.ainvoke(initial_state, config=config)
        return result["messages"][-1].content

    async def handle_message_stream(self, content: str) -> AsyncGenerator[str, None]:
        """
        流式处理消息并返回响应。
        
        Args:
            content: 用户输入的消息内容
            
        Yields:
            str: Agent的流式响应
        """
        if not self.app:
            raise ValueError("工作流未初始化")
            
        initial_state = {"messages": [HumanMessage(content=content)]}
        config = {"configurable": {"thread_id": "SingleNode"}}
        async for event in self.app.astream_events(initial_state, version="v2", config=config):
            if event["event"] == "on_chat_model_stream":
                chunk_content = event["data"]["chunk"].content
                if chunk_content:
                    yield chunk_content