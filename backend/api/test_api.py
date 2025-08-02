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
from backend.core.config import settings
from ..agents.single_agent import SingleNode
from ..agents.agent_prompts import coder_prompt

# --- 新增：设置日志 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


router = APIRouter()

@router.post("/stream")
async def test_stream(
    request: Request,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """流式测试生成API，返回内容并存入数据库（sessions和messages表）"""
    logger.info("API /stream 被调用。")
    data = await request.json()
    code = data.get("requirement", "")
    logger.info(f"收到的代码 (前50字符): {code[:50]}...")
    
    # 用当前用户的api_key创建model_client
    llm = create_langchain_llm(current_user.api_key, settings.DEEPSEEK_BASE_URL)
    agent = SingleNode(llm=llm, system_message=coder_prompt)

    # 1. 创建新的Session_History记录
    new_session = Session_History(
        user_id=current_user.id,
        session_name=f"测试生成: {code[:30]}"  # 取前30字符作为会话名
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
            
            # 将完整回答存入Message表
            assistant_message = Message(
                session_id=session_id,
                content=full_response,
                role="assistant"
            )
            db.add(assistant_message)
            await db.commit()
            logger.info("测试代码消息已存入数据库。")
        except Exception as e:
            logger.error(f"处理流式响应时发生错误: {e}", exc_info=True)
            yield f"Error: {e}"

    return StreamingResponse(event_stream(), media_type="text/plain")