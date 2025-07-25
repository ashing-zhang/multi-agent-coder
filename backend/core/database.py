from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import os
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer

# 自动加载.env文件（当前工作目录）
load_dotenv('backend/.env')

POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "ashing-great")
POSTGRES_DB = os.getenv("POSTGRES_DB", "multiagent")
POSTGRES_HOST_PRO = os.getenv("POSTGRES_HOST_PRO", "postgres")
POSTGRES_HOST_DEV = os.getenv("POSTGRES_HOST_DEV", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

# Use DATABASE_URL from environment if available
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    if os.getenv("ENV") == "dev":
        SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST_DEV}:{POSTGRES_PORT}/{POSTGRES_DB}"
    else:
        SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST_PRO}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL)

# 创建异步会话的 sessionmaker
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

#  返回一个基类，所有数据库模型类都需要继承该基类
Base = declarative_base()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# 将依赖项改为 async def
async def get_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            # async with 会自动处理关闭
            pass


