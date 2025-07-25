from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.database import get_db
from ..core.utils import get_current_user
from ..models.session import Session as Session_History
from ..models.user import User
from ..models.message import Message

router = APIRouter()

@router.get("/messages/", response_model=List[dict])
async def list_user_messages(
    db: AsyncSession = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    """
    获取某个用户的最新10条历史会话信息，包括Session_History和Message表内容
    返回格式: List[{"session_id": int, "session_name": str, "messages": List[{"id": int, "content": str, "role": str, "created_at": datetime}]}]
    """
    # 获取用户最新的10条会话，按创建时间倒序排列
    sessions = (await db.execute(
        select(Session_History)
        .filter_by(user_id=user.id)
        .order_by(Session_History.created_at.desc())
        .limit(10)
    )).scalars().all()
    
    result = []
    for session in sessions:
        messages = (await db.execute(
            select(Message)
            .filter_by(session_id=session.session_id)
            .order_by(Message.created_at)
        )).scalars().all()
        
        msg_list = [
            {
                "id": msg.message_id,
                "content": msg.content,
                "role": msg.role,
                "created_at": msg.created_at
            }
            for msg in messages
        ]
        result.append({
            "session_id": session.session_id,
            "session_name": getattr(session, "session_name", ""),
            "messages": msg_list
        })
    return result