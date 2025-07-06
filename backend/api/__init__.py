from fastapi import APIRouter
from backend.api import agent, auth, user, workflow

router = APIRouter()

# 注册各子路由
router.include_router(agent.router, prefix="/agent", tags=["Agent"])
router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(user.router, prefix="/user", tags=["User"])
router.include_router(workflow.router, prefix="/workflow", tags=["Workflow"])
