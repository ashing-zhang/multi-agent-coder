from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.api import router as api_router
import os

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

# 挂载前端静态文件（frontend/src 作为根目录）
frontend_path = 'frontend/src'
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
