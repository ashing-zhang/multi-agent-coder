from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import Optional
from ..models.user import User as UserModel
from ..auth import decode_access_token,create_access_token
from ..core.database import get_db
from ..core.utils import get_current_user

router = APIRouter()

# 创建一个 OAuth2PasswordBearer 实例，用于处理 OAuth2 的密码授权流程。
# tokenUrl 参数指定了获取令牌的端点 URL，客户端会向该 URL 发送请求以获取访问令牌。
# 此处设置为 "/auth/token"，表示获取令牌的接口路径为 "/auth/token"。
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
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
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
        await db.commit()
        await db.refresh(user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="用户名或邮箱已存在")
    return user

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    # 执行异步数据库查询，使用 SQLAlchemy 的 select 语句从 UserModel 对应的表中筛选数据。
    # 通过 filter 方法指定筛选条件为用户名等于表单中提交的用户名。
    # 最后将查询结果赋值给变量 result。
    result = await db.execute(select(UserModel).filter(UserModel.username == form_data.username))
    user = result.scalars().first()
    if not user or user.password != form_data.password:
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    # 调用 create_access_token 函数生成访问令牌。
    # 传入的数据为一个字典，其中 "sub" 键对应的值为当前登录用户的用户名。
    # "sub" 是 JWT（JSON Web Token）中常用的声明，用于表示令牌的主题，这里通常代表用户身份。
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/userinfo", response_model=UserOut)
async def get_userinfo(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    return await get_current_user(db,token)

@router.get("/validate_token")
async def validate_token(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    payload = decode_access_token(token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="无效token")
    result = await db.execute(select(UserModel).filter(UserModel.username == username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="无效token")
    return {"valid": True, "username": username}
