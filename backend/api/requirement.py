from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend.core.database import SessionLocal
from backend.models.user import User
from pydantic import BaseModel
from typing import List
from backend.agents.requirement_agent import RequirementAgent
from datetime import datetime
from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse
from ..agents.requirement_agent import RequirementAgent
from ..models.user import User
from ..models.session import Session as Session_History
from ..models.message import Message
from .set_key import get_current_user
from fastapi import Depends, Request, HTTPException
from backend.models.user import User as UserModel
from backend.core.database import get_db
from fastapi.security import OAuth2PasswordBearer
from backend.auth.process_token import decode_access_token
from backend.agents.requirement_agent import RequirementAgent
from backend.agents.set_key import set_deepseek_api_key
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    username = payload.get("sub")
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="无效token")
    return user

router = APIRouter()

class RequirementCreate(BaseModel):
    description: str

class RequirementOut(BaseModel):
    id: int
    description: str
    requirement_analysis: str
    status: str
    created_at: datetime
    class Config:
        orm_mode = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/userinfo")
async def get_userinfo(user: User = Depends(get_current_user)):
    return {"username": user.username, "api_key": user.api_key, "email": user.email, "full_name": user.full_name}

@router.post("/requirements/stream")
async def requirement_stream(
    request: Request,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """流式需求分析API，返回内容并存入数据库（sessions和messages表）"""
    data = await request.json()
    requirement = data.get("description", "")
    # 用当前用户的api_key创建model_client
    client = set_deepseek_api_key(current_user.api_key)
    agent = RequirementAgent(client)

    # 1. 创建新的Session_History记录
    new_session = Session_History(
        user_id=current_user.id,
        session_name=requirement[:30]  # 取前30字符作为会话名，可根据实际需求调整
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    session_id = new_session.session_id  # 立即取出

    # 2. 创建用户问题的Message记录
    user_message = Message(
        session_id=session_id,
        content=requirement,
        role="user"
    )
    db.add(user_message)
    db.commit()
    # 刷新user_message对象以获取数据库自动生成的字段（如id、created_at等）
    db.refresh(user_message)

    # 3. 生成AI回答并流式返回，同时收集完整回答
    async def event_stream():
        answer_chunks = []
        async for token in agent.handle_message_stream(requirement):
            answer_chunks.append(token)
            yield token
        # 4. 回答生成完毕后，存入Message表
        full_answer = "".join(answer_chunks)
        assistant_message = Message(
            session_id=session_id,
            content=full_answer,
            role="assistant"
        )
        db.add(assistant_message)
        db.commit()

    return StreamingResponse(event_stream(), media_type="text/plain")

@router.get("/messages/", response_model=List[dict])
def list_user_messages(
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    """
    获取某个用户的最新10条历史会话信息，包括Session_History和Message表内容
    返回格式: List[{"session_id": int, "session_name": str, "messages": List[{"id": int, "content": str, "role": str, "created_at": datetime}]}]
    """
    # 获取用户最新的10条会话，按创建时间倒序排列
    sessions = db.query(Session_History).filter_by(user_id=user.id).order_by(Session_History.created_at.desc()).limit(10).all()
    result = []
    for session in sessions:
        messages = db.query(Message).filter_by(session_id=session.session_id).order_by(Message.created_at).all()
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