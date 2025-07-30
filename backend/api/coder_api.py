from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.session import Session as Session_History
from ..models.message import Message
from ..agents.coder_agent import CoderAgent
from ..agents.set_key import set_deepseek_api_key
from ..models.user import User as UserModel
from ..core.database import get_db
from ..core.utils import get_current_user
from ..agents.summary_agent import SummaryAgent
from backend.core.config import settings

router = APIRouter()

@router.post("/stream")
async def coder_stream(
    request: Request,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """流式代码生成API，返回内容并存入数据库（sessions和messages表）"""
    data = await request.json()
    task = data.get("description", "")
    
    # 用当前用户的api_key创建model_client
    client = set_deepseek_api_key(current_user.api_key, settings.DEEPSEEK_BASE_URL)
    agent = CoderAgent(client)

    # 1. 创建新的Session_History记录
    new_session = Session_History(
        user_id=current_user.id,
        session_name=f"代码生成: {task[:30]}"  # 取前30字符作为会话名
    )
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    session_id = new_session.session_id

    # 2. 创建用户问题的Message记录
    user_message = Message(
        session_id=session_id,
        content=task,
        role="user"
    )
    db.add(user_message)
    await db.commit()
    await db.refresh(user_message)

    # 3. 生成AI回答并流式返回，同时收集完整回答
    async def event_stream():
        answer_chunks = []
        async for token in agent.handle_message_stream(task):
            answer_chunks.append(token)
            yield token
        # 4. 回答生成完毕后，使用摘要agent处理完整回答并生成摘要
        full_answer = "".join(answer_chunks)
        summary_agent = SummaryAgent(client)
        summary_content = await summary_agent.process_and_store(session_id, full_answer, db)
        
        # 将摘要内容存入Message表
        assistant_message = Message(
            session_id=session_id,
            content=summary_content,
            role="assistant"
        )
        db.add(assistant_message)
        await db.commit()

    return StreamingResponse(event_stream(), media_type="text/plain")