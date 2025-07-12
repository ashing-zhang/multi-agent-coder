from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.models.user import User as UserModel
from fastapi.security import OAuth2PasswordBearer
from backend.auth.process_token import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    username = payload.get("sub")
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="无效token")
    return user

router = APIRouter()

@router.get("/list")
def list_agents():
    """获取所有Agent类型"""
    return [
        "需求分析Agent", "代码生成Agent", "代码审查Agent", "代码整合Agent", "文档Agent", "测试Agent"
    ]
