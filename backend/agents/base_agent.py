from typing import AsyncGenerator
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from typing import Annotated, Sequence, TypedDict


class AgentState(TypedDict):
    messages: Annotated[Sequence[HumanMessage | AIMessage], add_messages]


class BaseAgent:
    """
    所有Agent的基类，提供通用的方法和属性。
    使用LangChain和LangGraph实现。
    """
    def __init__(self, model_client, name, system_message):
        self.name = name
        self.system_message = system_message
        self.model_client = model_client
        
        # 创建提示模板
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("placeholder", "{messages}"),
        ])
        
        # 创建Agent
        self.agent = self.prompt | self.model_client
        
        # 创建工作流
        self.workflow = StateGraph(AgentState)
        self.workflow.add_node("agent", self.agent)
        self.workflow.add_edge(START, "agent")
        self.workflow.add_edge("agent", END)
        
        # 编译工作流
        self.memory = MemorySaver()
        self.app = self.workflow.compile(checkpointer=self.memory)

    async def handle_message(self, content: str) -> str:
        """
        处理消息并返回响应。
        """
        initial_state = {"messages": [HumanMessage(content=content)]}
        config = {"configurable": {"thread_id": self.name}}
        result = await self.app.ainvoke(initial_state, config=config)
        return result["messages"][-1].content

    async def handle_message_stream(self, content: str) -> AsyncGenerator[str, None]:
        """
        流式处理消息并返回响应。
        """
        initial_state = {"messages": [HumanMessage(content=content)]}
        config = {"configurable": {"thread_id": self.name}}
        async for event in self.app.astream_events(initial_state, version="v2", config=config):
            if event["event"] == "on_chat_model_stream":
                chunk_content = event["data"]["chunk"].content
                if chunk_content:
                    yield chunk_content