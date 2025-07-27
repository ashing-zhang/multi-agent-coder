from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt as pyjwt
from backend.models.user import User as UserModel


SECRET_KEY = "your_secret_key_here"
# 定义JWT编码和解码时使用的算法，HS256是HMAC-SHA256的缩写，
# 这是一种对称加密算法，使用相同的密钥进行签名和验证
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # 使用pyjwt库的encode方法，将待编码的数据（to_encode）、密钥（SECRET_KEY）和算法（ALGORITHM）生成JWT字符串
    encoded_jwt = pyjwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 定义一个名为decode_access_token的函数，用于解码JWT访问令牌
# 参数token为待解码的JWT字符串
def decode_access_token(token: str):
    try:
        # 使用pyjwt库的decode方法对令牌进行解码
        # 需要传入待解码的令牌token、密钥SECRET_KEY和支持的算法列表[ALGORITHM]
        # 若解码成功，返回解码后的负载数据payload
        payload = pyjwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    # 捕获令牌签名过期的异常
    except pyjwt.ExpiredSignatureError:
        # 若令牌已过期，抛出HTTP 401错误，提示"Token已过期"
        raise HTTPException(status_code=401, detail="Token已过期")
    # 捕获令牌无效的异常，包含格式错误、签名不匹配等情况
    except pyjwt.InvalidTokenError:
        # 若令牌无效，抛出HTTP 401错误，提示"无效Token"
        raise HTTPException(status_code=401, detail="无效Token")
