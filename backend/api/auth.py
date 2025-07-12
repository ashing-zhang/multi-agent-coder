from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.models.user import User as UserModel
from backend.auth import decode_access_token,create_access_token
from backend.core.database import get_db
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt as pyjwt
from .set_key import get_current_user

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

class UserOut(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    api_key: Optional[str] = None
    avatar: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    class Config:
        orm_mode = True

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str
    full_name: Optional[str] = None
    avatar: Optional[str] = None
    phone: Optional[str] = None


@router.post("/register", response_model=UserOut)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    user = UserModel(
        username=data.username,
        password=data.password,
        email=data.email,
        full_name=data.full_name,
        avatar=data.avatar,
        phone=data.phone,
        is_active=True
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="用户名或邮箱已存在")
    return user

@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.username == form_data.username).first()
    if not user or user.password != form_data.password:
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    access_token = create_access_token(data={"sub": user.username})
    # print('access_token:',access_token)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/userinfo", response_model=UserOut)
def get_userinfo(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return get_current_user(db,token)

@router.get("/validate_token")
def validate_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="无效token")
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="无效token")
    return {"valid": True, "username": username}
