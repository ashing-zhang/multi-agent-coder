from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from backend.core.database import SessionLocal
from backend.models.requirement import Requirement
from backend.models.generated_code import GeneratedCode
from backend.models.user import User
from pydantic import BaseModel
from typing import List, Optional
from backend.api.auth import get_me  # 假设 get_me 返回当前用户
from backend.agents.requirement_agent import RequirementAgent
import asyncio
from datetime import datetime
from backend.agents import set_key

router = APIRouter()

class RequirementCreate(BaseModel):
    description: str

class RequirementOut(BaseModel):
    id: int
    description: str
    requirement_analysis: str
    status: str
    created_at: datetime
    class Config:
        orm_mode = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/requirements/", response_model=RequirementOut)
async def create_requirement(req: RequirementCreate, db: Session = Depends(get_db), user: User = Depends(get_me)):
    agent = RequirementAgent()
    requirement_analysis = await agent.handle_message(req.description)
    requirement = Requirement(user_id=user.id, description=req.description, requirement_analysis=requirement_analysis)
    db.add(requirement)
    db.commit()
    db.refresh(requirement)
    return requirement

@router.get("/requirements/", response_model=List[str])
def list_requirements(db: Session = Depends(get_db), user: User = Depends(get_me)):
    return [r.requirement_analysis for r in db.query(Requirement).filter_by(user_id=user.id).all() if r.requirement_analysis is not None] 