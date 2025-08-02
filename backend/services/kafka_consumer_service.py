from kafka_service import KafkaService
from agents.single_agent import SingleNode
from agents.set_key import create_langchain_llm
from core.config import settings
from models.user import User as UserModel
from models.session import Session as Session_History
from models.message import Message
from core.database import AsyncSessionLocal
from agents.summary_agent import SummaryAgent
from sqlalchemy import select
import asyncio
import json
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KafkaConsumerService:
    """
    Kafka消费者服务类，用于处理来自Kafka的消息。
    """
    def __init__(self):
        self.kafka_service = KafkaService()
    
    async def process_message(self, message: dict, agent):
        """
        处理来自Kafka的消息。
        :param message: 消息内容
        :param agent: 已经实例化的BaseAgent对象
        """
        try:
            requirement = message.get("requirement", "")
            user_id = message.get("user_id", "")
            
            # 创建数据库会话
            db = AsyncSessionLocal()
            
            # 获取用户信息和API密钥
            result = await db.execute(select(UserModel).filter(UserModel.id == user_id))
            user = result.scalar_one_or_none()
            if not user:
                logger.error(f"未找到用户ID: {user_id}")
                await db.close()
                return
            
            # 创建LLM实例
            llm = create_langchain_llm(user.api_key, settings.DEEPSEEK_BASE_URL)
            
            # 使用传入的Agent实例
            workflow = agent(llm)
            
            # 初始化工作流
            await workflow.initialize()
            
            # 1. 创建新的Session_History记录
            from .agent_service import AgentService
            session_id = await AgentService.create_session_record(db, user_id, requirement)

            # 2. 创建用户问题的Message记录
            await AgentService.create_user_message_record(db, session_id, requirement)

            # 3. 生成AI回答并流式返回，同时收集完整回答
            full_response = ""
            async for token in workflow.handle_message_stream(requirement):
                full_response += token
                # 将token发送到Kafka
                self.kafka_service.produce_message(settings.KAFKA_TOPIC_RESPONSE, {"token": token, "session_id": session_id})
            
            # 4. 创建AI回答的Message记录
            await AgentService.create_ai_message_record(db, session_id, full_response)
            
            # 5. 使用摘要agent处理完整回答并生成摘要
            summary_content = await AgentService.process_summary(db, llm, session_id, full_response)
            
            # 6. 将完整响应和摘要发送到Kafka
            self.kafka_service.produce_message(settings.KAFKA_TOPIC_RESPONSE, {"full_response": full_response, "summary": summary_content, "session_id": session_id, "finished": True})
            
            # 关闭数据库会话
            await db.close()
            
        except Exception as e:
            logger.error(f"处理消息时发生错误: {e}", exc_info=True)
            # 发送错误信息到Kafka
            self.kafka_service.produce_message(settings.KAFKA_TOPIC_RESPONSE, {"error": str(e), "finished": True})
    
    def start_consuming(self):
        """
        开始消费Kafka消息。
        """
        print("开始消费Kafka消息...")
        # 传入SingleNode作为默认agent
        self.kafka_service.consume_messages(settings.KAFKA_TOPIC_REQUEST, lambda message: asyncio.run(self.process_message(message, SingleNode)))