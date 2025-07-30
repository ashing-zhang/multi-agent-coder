from typing import Annotated, Sequence, TypedDict, AsyncGenerator
import asyncio
import logging
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from .agent_prompts import requirement_prompt, coder_prompt, reviewer_prompt, finalizer_prompt, doc_prompt, summary_prompt
from .summary_agent import SummaryAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    # 定义 `messages` 字段，其类型为 `BaseMessage` 序列。
    # `Annotated` 用于为类型添加额外的元数据，这里使用 `add_messages` 作为注解，
    # 表明该字段在某些场景下可能会使用 `add_messages` 函数来处理消息。
    messages: Annotated[Sequence[BaseMessage], add_messages]

class LangGraphWorkflow:
    """
    使用LangGraph框架实现的多Agent协作工作流
    """
    def __init__(self, llm):
        # 配置LLM模型参数
        self.llm = llm
        
        # 初始化其他属性
        self.tools = None
        self.llm_with_tools = None
        self.requirement_agent = None
        self.coder_agent = None
        self.reviewer_agent = None
        self.finalizer_agent = None
        self.doc_agent = None
        self.summary_agent = None
        self.workflow = None
        self.memory = None
        self.app = None
    
    async def initialize(self):
        """
        初始化工作流，编译图，并预热LLM连接。
        """
        # 预热/测试 LLM 连接，确保其可用
        try:
            logger.info("正在预热 LLM 连接...")
            await self.llm.ainvoke("ping") # 发送一个简单的、无意义的调用来建立连接
            logger.info("LLM 连接已准备就绪。")
        except Exception as e:
            logger.error(f"LLM 连接预热失败: {e}", exc_info=True)
            raise  # 抛出异常，防止工作流在不健康的状态下继续运行
        print("开始初始化 LangGraphWorkflow。")
        # 加载context7工具
        print("准备加载 context7 工具。")
        self.tools = await self._load_context7_tools_async()
        print("工具加载成功:")
        for tool in self.tools:
            print(f"  - {tool.name}")
        # 将工具绑定到LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # 创建专业Agent
        print("准备创建专业 Agent。")
        self.requirement_agent = self._create_requirement_agent()
        self.coder_agent = self._create_coder_agent()
        self.reviewer_agent = self._create_reviewer_agent()
        self.finalizer_agent = self._create_finalizer_agent()
        self.doc_agent = self._create_doc_agent()
        self.summary_agent = SummaryAgent(self.llm)
        
        # 构建工作流图
        print("准备构建工作流图。")
        self.workflow = self._build_workflow()
        self.memory = MemorySaver()
        self.app = self.workflow.compile(checkpointer=self.memory)
        print("LangGraphWorkflow 初始化完成。")
    # 每个node包含llm（with tools）、prompt和message占位符
    def _create_requirement_agent(self):
        """创建需求分析Agent"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", requirement_prompt),
            ("placeholder", "{messages}"),
        ])
        # 使用管道操作符将提示模板与LLM模型连接，当输入数据时，
        # 数据会先经过提示模板处理，然后将处理后的结果传递给LLM模型进行推理，最后返回推理结果。
        return prompt | self.llm_with_tools
    
    def _create_coder_agent(self):
        """创建编码Agent"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", coder_prompt),
            ("placeholder", "{messages}"),
        ])
        return prompt | self.llm_with_tools
    
    def _create_reviewer_agent(self):
        """创建代码审查Agent"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", reviewer_prompt),
            ("placeholder", "{messages}"),
        ])
        return prompt | self.llm_with_tools
    
    def _create_finalizer_agent(self):
        """创建代码整合Agent"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", finalizer_prompt),
            ("placeholder", "{messages}"),
        ])
        return prompt | self.llm_with_tools
    
    def _create_doc_agent(self):
        """创建文档生成Agent"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", doc_prompt),
            ("placeholder", "{messages}"),
        ])
        return prompt | self.llm_with_tools
    
    def _build_workflow(self):
        """构建LangGraph工作流"""
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("requirement", self.requirement_agent)
        workflow.add_node("coder", self.coder_agent)
        workflow.add_node("reviewer", self.reviewer_agent)
        workflow.add_node("finalizer", self.finalizer_agent)
        workflow.add_node("doc", self.doc_agent)
        
        # 添加边
        workflow.add_edge(START, "requirement")
        workflow.add_edge("requirement", "coder")
        workflow.add_edge("coder", "reviewer")
        workflow.add_edge("reviewer", "finalizer")
        workflow.add_edge("finalizer", "doc")
        # 传递到 END 的任何数据都会被作为最终结果返回
        # ​内容构成​：输出为结束节点执行后的完整 State 对象（可自定义精简）
        workflow.add_edge("doc", END)
        
        return workflow
    
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

    async def run_stream(self, user_requirement: str) -> AsyncGenerator[str, None]:
        """
        流式运行LangGraph多Agent工作流，实现token级别流式输出
        :param user_requirement: 用户需求
        :return: 流式结果
        """
        print('进入workflow的run_stream方法')
        if not self.app:
            print("Error: workflow.app 未初始化")
            return
        initial_state = {"messages": [HumanMessage(content=user_requirement)]}
        # 添加检查点配置
        config = {"configurable": {"thread_id": "1"}}
        print('准备进入流式生成逻辑')
        # 使用async for迭代器逐个处理每个事件
        try:
            async for event in self.app.astream_events(initial_state, version="v2", config=config):
                # 检查事件类型并提取内容
                if event["event"] == "on_chat_model_stream":
                    content = event["data"]["chunk"].content
                    if content:
                        yield content
        except Exception as e:
            print(f"Error in run_stream: {e}")
            raise