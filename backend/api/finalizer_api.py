import logging
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.session import Session as Session_History
from ..models.message import Message
from ..agents.set_key import create_langchain_llm
from ..models.user import User as UserModel
from ..core.database import get_db
from ..core.utils import get_current_user
from ..agents.summary_agent import SummaryAgent
from backend.core.config import settings
from ..agents.single_agent import SingleNode
from ..agents.agent_prompts import finalizer_prompt
from ..services.kafka_service import KafkaService

# --- 新增：设置日志 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 初始化Kafka服务
kafka_service = KafkaService()

router = APIRouter()

@router.post("/stream")
async def finalizer_stream(
    request: Request,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """流式代码整合API，返回内容并存入数据库（sessions和messages表）"""
    logger.info("API /stream 被调用。")
    data = await request.json()
    code = data.get("description", "")
    logger.info(f"收到的代码 (前50字符): {code[:50]}...")
    
    # 将请求发送到Kafka
    kafka_service.produce_message("agent_request", {"code": code, "user_id": current_user.id})
    
    # 用当前用户的api_key创建model_client
    llm = create_langchain_llm(current_user.api_key, settings.DEEPSEEK_BASE_URL)
    agent = SingleNode(llm=llm, system_message=finalizer_prompt)

    # 1. 创建新的Session_History记录
    new_session = Session_History(
        user_id=current_user.id,
        session_name=f"代码整合: {code[:30]}"  # 取前30字符作为会话名
    )
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    session_id = new_session.session_id
    logger.info(f"数据库会话已创建，Session ID: {session_id}")

    # 2. 创建用户问题的Message记录
    user_message = Message(
        session_id=session_id,
        content=code,
        role="user"
    )
    db.add(user_message)
    await db.commit()
    await db.refresh(user_message)
    logger.info("用户消息已存入数据库。")

    # 3. 生成AI回答并流式返回，同时收集完整回答
    async def event_stream():
        full_response = ""
        try:
            async for token in agent.handle_message_stream(code):
                full_response += token
                yield token
            
            # 4. 创建AI回答的Message记录
            ai_message = Message(
                session_id=session_id,
                content=full_response,
                role="assistant"
            )
            db.add(ai_message)
            await db.commit()
            await db.refresh(ai_message)
            logger.info("AI消息已存入数据库。")
            
            # 使用摘要agent处理完整回答并生成摘要
            summary_agent = SummaryAgent(llm)
            summary_content = await summary_agent.process_and_store(session_id, full_response, db)
            
            # 将摘要内容存入Message表
            summary_message = Message(
                session_id=session_id,
                content=summary_content,
                role="assistant"
            )
            db.add(summary_message)
            await db.commit()
            logger.info("摘要消息已存入数据库。")
        except Exception as e:
            logger.error(f"处理流式响应时发生错误: {e}", exc_info=True)
            yield f"Error: {e}"

    return StreamingResponse(event_stream(), media_type="text/plain")