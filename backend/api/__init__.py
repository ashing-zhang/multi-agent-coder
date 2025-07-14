from fastapi import APIRouter
from .messages import router as messages_router
from .auth import router as auth_router
from .workflow_api import router as workflow_router
from .requirement_api import router as requirement_router
from .set_key import router as set_key_router
from .doc_api import router as doc_agent_router
from .coder_api import router as coder_agent_router
from .reviewer_api import router as reviewer_agent_router
from .test_api import router as test_agent_router
from .finalizer_api import router as finalizer_agent_router

router = APIRouter()

# 注册各子路由
router.include_router(messages_router, tags=['Messages'])
router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(workflow_router, prefix="/workflow", tags=["Workflow"])

# 注册需求相关API (包含流式接口)
router.include_router(requirement_router, prefix="/agent/requirement", tags=["RequirementAgent"])

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
