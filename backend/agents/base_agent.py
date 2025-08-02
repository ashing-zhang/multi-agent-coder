from typing import AsyncGenerator
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from typing import Annotated, Sequence, TypedDict
from abc import ABC, abstractmethod

class AgentState(TypedDict):
    messages: Annotated[Sequence[HumanMessage | AIMessage], add_messages]

class BaseAgent(ABC):
    """
    所有Agent的抽象基类，提供通用的方法和属性。
    使用LangChain和LangGraph实现。
    """

    def __init__(self, llm: ChatOpenAI):
        """
        初始化BaseAgent。
        
        Args:
            llm: LLM模型实例
        """
        self.llm = llm

    @abstractmethod
    async def handle_message(self, content: str) -> str:
        """
        处理消息并返回响应。
        """
        pass

    @abstractmethod
    async def handle_message_stream(self, content: str) -> AsyncGenerator[str, None]:
        """
        流式处理消息并返回响应。
        """
        pass
