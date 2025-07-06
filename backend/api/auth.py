from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

class User(BaseModel):
    username: str
    role: str

# 简单模拟用户数据库
dummy_users = {
    "admin": {"username": "admin", "password": "admin123", "role": "admin"},
    "user": {"username": "user", "password": "user123", "role": "user"}
}

@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = dummy_users.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    return {"access_token": user["username"] + "-token", "token_type": "bearer"}

@router.get("/me", response_model=User)
def get_me(token: str = Depends(oauth2_scheme)):
    # 简单token解析
    username = token.replace("-token", "")
    user = dummy_users.get(username)
    if not user:
        raise HTTPException(status_code=401, detail="无效token")
    return {"username": user["username"], "role": user["role"]}
