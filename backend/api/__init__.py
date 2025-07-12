from fastapi import APIRouter
from backend.api import agent, auth, workflow
from .requirement import router as requirement_router
from .set_key import router as set_key_router
from .doc_agent import router as doc_agent_router
from .coder_agent import router as coder_agent_router
from .reviewer_agent import router as reviewer_agent_router
from .test_agent import router as test_agent_router
from .finalizer_agent import router as finalizer_agent_router

router = APIRouter()

# 注册各子路由
router.include_router(agent.router, prefix="/agent", tags=["Agent"])
router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(workflow.router, prefix="/workflow", tags=["Workflow"])

# 注册需求相关API (包含流式接口)
router.include_router(requirement_router)

# 注册各个Agent的独立路由
router.include_router(doc_agent_router, prefix="/agent/doc", tags=["DocAgent"])
router.include_router(coder_agent_router, prefix="/agent/coder", tags=["CoderAgent"])
router.include_router(reviewer_agent_router, prefix="/agent/reviewer", tags=["ReviewerAgent"])
router.include_router(test_agent_router, prefix="/agent/test", tags=["TestAgent"])
router.include_router(finalizer_agent_router, prefix="/agent/finalizer", tags=["FinalizerAgent"])

# 注册API Key设置路由
routers = [
    set_key_router,
]
for r in routers:
    router.include_router(r)
