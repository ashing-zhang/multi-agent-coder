from ..models.session import Session as Session_History
from ..models.message import Message
from ..agents.summary_agent import SummaryAgent
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AgentService:
    """
    Agent服务类，用于处理与Agent相关的公共逻辑。
    """
    
    @staticmethod
    async def create_session_record(db, user_id, requirement, session_name_prefix="Agent处理"):
        """
        创建会话记录
        :param db: 数据库会话
        :param user_id: 用户ID
        :param requirement: 用户需求
        :param session_name_prefix: 会话名称前缀
        :return: session_id
        """
        try:
            new_session = Session_History(
                user_id=user_id,
                session_name=f"{session_name_prefix}: {requirement[:30]}"  # 取前30字符作为会话名
            )
            db.add(new_session)
            await db.commit()
            await db.refresh(new_session)
            session_id = new_session.session_id
            logger.info(f"数据库会话已创建，Session ID: {session_id}")
            return session_id
        except Exception as e:
            logger.error(f"创建会话记录时发生错误: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def create_user_message_record(db, session_id, requirement):
        """
        创建用户消息记录
        :param db: 数据库会话
        :param session_id: 会话ID
        :param requirement: 用户需求
        """
        try:
            user_message = Message(
                session_id=session_id,
                content=requirement,
                role="user"
            )
            db.add(user_message)
            await db.commit()
            await db.refresh(user_message)
            logger.info("用户消息已存入数据库。")
        except Exception as e:
            logger.error(f"创建用户消息记录时发生错误: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def create_ai_message_record(db, session_id, full_response):
        """
        创建AI消息记录
        :param db: 数据库会话
        :param session_id: 会话ID
        :param full_response: 完整的AI响应
        """
        try:
            ai_message = Message(
                session_id=session_id,
                content=full_response,
                role="assistant"
            )
            db.add(ai_message)
            await db.commit()
            await db.refresh(ai_message)
            logger.info("AI消息已存入数据库。")
        except Exception as e:
            logger.error(f"创建AI消息记录时发生错误: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def process_summary(db, llm, session_id, full_response):
        """
        处理摘要
        :param db: 数据库会话
        :param llm: LLM实例
        :param session_id: 会话ID
        :param full_response: 完整的AI响应
        """
        try:
            summary_agent = SummaryAgent(llm)
            summary_content = await summary_agent.process_and_store(session_id, full_response, db)
            logger.info("摘要消息已存入数据库。")
            return summary_content
        except Exception as e:
            logger.error(f"处理摘要时发生错误: {e}", exc_info=True)
            raise