import logging
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.session import Session as Session_History
from ..models.message import Message
from ..agents.langgraph_workflow import LangGraphWorkflow
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
    
    # 实例化LangGraphWorkflow
    workflow = LangGraphWorkflow(llm)
    logger.info("准备初始化 LangGraphWorkflow。")
    try:
        await workflow.initialize()
        logger.info("LangGraphWorkflow 初始化成功。")
    except Exception as e:
        logger.error(f"LangGraphWorkflow 初始化失败: {e}", exc_info=True)
        raise
    # 检查 workflow 是否创建成功并记录日志
    if workflow:
        logger.info("LangGraphWorkflow 实例创建成功。")
    else:
        logger.error("LangGraphWorkflow 实例创建失败。")
    
    # 由于LangGraphWorkflow不是异步上下文管理器，我们不需要使用async with语句
    # 直接使用workflow.run_stream方法
    # 1. 创建新的Session_History记录
    new_session = Session_History(
        user_id=current_user.id,
        session_name=f"Agent Workflow: {requirement[:30]}"
    )
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    session_id = new_session.session_id
    logger.info(f"数据库会话已创建，Session ID: {session_id}")

    # 2. 创建用户问题的Message记录
    user_message = Message(
        session_id=session_id,
        content=requirement,
        role="user"
    )
    db.add(user_message)
    await db.commit()
    await db.refresh(user_message)
    logger.info("用户消息已存入数据库。")

    # 3. 生成AI回答并流式返回，同时收集完整回答
    async def event_stream():
        logger.info("event_stream: 生成器已创建。等待客户端拉取数据...")
        answer_chunks = []
        try:
            # 只有当客户端开始读取响应时，下面的代码才会执行
            logger.info("event_stream: 客户端已连接，开始迭代 workflow.run_stream。")
            async for content in workflow.run_stream(requirement):
                logger.info(f"event_stream: 从 workflow 收到数据块: {content}")
                if isinstance(content, str):
                    answer_chunks.append(content)
                    yield content
                else:
                    logger.warning(f"event_stream: 收到非字符串类型的数据块: {type(content)}，已忽略。")
            
            logger.info("event_stream: workflow.run_stream 迭代完成。")
        except Exception as e:
            logger.error(f"event_stream: 在流式处理中发生异常: {e}", exc_info=True)
            yield f"Error: {str(e)}"
        finally:
            # 4. 回答生成完毕后，使用摘要agent处理完整回答并生成摘要
            full_answer = "".join(answer_chunks)
            if full_answer:
                # 使用摘要agent处理完整回答并生成摘要
                summary_agent = SummaryAgent(llm)
                summary_content = await summary_agent.process_and_store(session_id, full_answer, db)
                logger.info(f"event_stream: 摘要已生成并存入数据库。")
                
                # 存储摘要内容
                assistant_message = Message(
                    session_id=session_id,
                    content=summary_content,
                    role="assistant"
                )
                logger.info(f"event_stream: 助手回答摘要内容: {summary_content}")
                db.add(assistant_message)
                await db.commit()
                logger.info(f"event_stream: 助手回答摘要已成功存入数据库。")
            else:
                logger.warning("event_stream: 未生成任何有效内容，无需存入数据库。")

    logger.info("准备返回 StreamingResponse 对象。FastAPI 将接管后续流程。")
    return StreamingResponse(event_stream(), media_type="text/plain")
