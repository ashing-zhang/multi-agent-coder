import logging
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.session import Session as Session_History
from ..models.message import Message
from ..agents.agent_workflow import MultiNode
from ..agents.summary_agent import SummaryAgent
from ..models.user import User as UserModel
from ..agents.set_key import create_langchain_llm
from ..core.database import get_db
from ..core.utils import get_current_user
from .set_key import get_current_user
from pydantic import BaseModel

# --- 新增：设置日志 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter()


class WorkflowRequest(BaseModel):
    requirement: str

class WorkflowResponse(BaseModel):
    tasks: list
    codes: list
    suggestions: str
    final_code: str
    doc: str
    test_code: str

@router.post("/stream")
async def workflow_stream(
    request: Request, 
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """流式Agent Workflow API，返回内容并存入数据库（sessions和messages表）"""
    logger.info("API /stream 被调用。")
    data = await request.json()
    requirement = data.get("description", "")
    logger.info(f"收到的需求 (前50字符): {requirement[:50]}...")
    
    # 用当前用户的api_key创建model_client和llm
    from ..core.config import settings
    llm = create_langchain_llm(current_user.api_key, settings.DEEPSEEK_BASE_URL)
    logger.info("llm实例化成功")
    
    # 实例化MultiNode
    workflow = MultiNode(llm)
    logger.info("准备初始化 MultiNode。")
    try:
        await workflow.initialize()
        logger.info("MultiNode 初始化成功。")
    except Exception as e:
        logger.error(f"MultiNode 初始化失败: {e}", exc_info=True)
        raise
    # 检查 workflow 是否创建成功并记录日志
    if workflow:
        logger.info("MultiNode 实例创建成功。")
    else:
        logger.error("MultiNode 实例创建失败。")

    # 由于MultiNode不是异步上下文管理器，我们不需要使用async with语句
    # 直接使用workflow.run_stream方法
    # 1. 创建新的Session_History记录
    from ..services.agent_service import AgentService
    session_id = await AgentService.create_session_record(db, current_user.id, requirement, "Agent Workflow")

    # 2. 创建用户问题的Message记录
    await AgentService.create_user_message_record(db, session_id, requirement)

    # 3. 生成AI回答并流式返回，同时收集完整回答
    async def generate_response():
        full_response = ""
        try:
            async for content in workflow.handle_message_stream(requirement):
                full_response += content
                yield content
            
            # 4. 创建AI回答的Message记录
            await AgentService.create_ai_message_record(db, session_id, full_response)
        except Exception as e:
            logger.error(f"处理流式响应时发生错误: {e}", exc_info=True)
            yield f"Error: {e}"
    
    return StreamingResponse(generate_response(), media_type="text/plain")
