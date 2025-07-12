from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend.core.database import SessionLocal
from backend.models.user import User
from backend.models.session import Session as Session_History
from backend.models.message import Message
from pydantic import BaseModel
from ..agents.agent_workflow import AgentWorkflow
from fastapi.security import OAuth2PasswordBearer
from backend.models.user import User as UserModel
from .set_key import get_current_user
from backend.agents.set_key import set_deepseek_api_key
from backend.auth.process_token import decode_access_token
from backend.core.database import get_db
from fastapi import HTTPException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
router = APIRouter()

class WorkflowRequest(BaseModel):
    requirement: str

class WorkflowResponse(BaseModel):
    tasks: list
    codes: list
    suggestions: str
    final_code: str
    doc: str
    test_code: str

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    username = payload.get("sub")
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="无效token")
    return user

@router.post("/workflow/stream")
async def workflow_stream(
    request: Request, 
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """流式Agent Workflow API，返回内容并存入数据库（sessions和messages表）"""
    data = await request.json()
    requirement = data.get("requirement", "")
    
    # 用当前用户的api_key创建model_client
    client = set_deepseek_api_key(current_user.api_key)
    workflow = AgentWorkflow(client)

    # 1. 创建新的Session_History记录
    new_session = Session_History(
        user_id=current_user.id,
        session_name=f"Agent Workflow: {requirement[:30]}"  # 取前30字符作为会话名
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    session_id = new_session.session_id

    # 2. 创建用户问题的Message记录
    user_message = Message(
        session_id=session_id,
        content=requirement,
        role="user"
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    # 3. 生成AI回答并流式返回，同时收集完整回答
    async def event_stream():
        answer_chunks = []
        async for token in workflow.run_stream(requirement):
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
