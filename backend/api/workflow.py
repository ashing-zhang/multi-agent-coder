from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..agents.agent_workflow import AgentWorkflow
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
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

@router.post("/run", response_model=WorkflowResponse)
async def run_workflow(data: WorkflowRequest, token: str = Depends(oauth2_scheme)):
    # 可扩展token校验
    workflow = AgentWorkflow()
    result = await workflow.run(data.requirement)
    return result
