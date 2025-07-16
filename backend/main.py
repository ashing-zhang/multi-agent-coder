import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .api import router as api_router

app = FastAPI(title="Multi-Agent 协作平台")

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router)

# 根据环境变量 ENV 判断前端静态目录
env = os.environ.get('ENV', 'dev')
if env == 'dev':
    frontend_path = 'frontend/src'
else:
    frontend_path = 'frontend_dist'

app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")