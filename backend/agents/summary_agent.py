from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.message import Message
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from .agent_prompts import summary_prompt

class SummaryAgent:
    """
    摘要Agent，负责处理其他Agent生成的内容，生成摘要并存入数据库
    """
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", summary_prompt),
            ("user", "请为以下内容生成摘要:\n{content}")
        ])
        self.chain = self.prompt | self.llm
    
    async def process_and_store(self, session_id: int, full_content: str, db: AsyncSession) -> str:
        """
        处理完整内容，生成摘要并存入数据库
        :param session_id: 会话ID
        :param full_content: 完整内容
        :param db: 数据库会话
        :return: 生成的摘要
        """
        # 生成摘要
        summary = await self.chain.ainvoke({"content": full_content})
        summary_content = summary.content if hasattr(summary, 'content') else str(summary)
        
        # 将摘要存入数据库
        summary_message = Message(
            session_id=session_id,
            content=summary_content,
            role="assistant_summary"
        )
        db.add(summary_message)
        await db.commit()
        await db.refresh(summary_message)
        
        return summary_content