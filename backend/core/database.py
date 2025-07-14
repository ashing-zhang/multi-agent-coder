from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer

# 自动加载.env文件（当前工作目录）
load_dotenv('.env')

POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "ashing-great")
POSTGRES_DB = os.getenv("POSTGRES_DB", "multiagent")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
# SessionLocal 是一个可以用来生成 Session 实例的类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#  返回一个基类，所有数据库模型类都需要继承该基类
Base = declarative_base()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


