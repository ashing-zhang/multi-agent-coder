from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.core.database import SessionLocal
from backend.models.requirement import Requirement
from backend.models.generated_code import GeneratedCode
from backend.models.user import User
from pydantic import BaseModel
from typing import List, Optional
from backend.api.auth import get_me  # 假设 get_me 返回当前用户

router = APIRouter()

class RequirementCreate(BaseModel):
    title: str
    description: str

class RequirementOut(BaseModel):
    id: int
    title: str
    description: str
    status: str
    created_at: str
    class Config:
        orm_mode = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/requirements/", response_model=RequirementOut)
def create_requirement(req: RequirementCreate, db: Session = Depends(get_db), user: User = Depends(get_me)):
    requirement = Requirement(user_id=user.id, title=req.title, description=req.description)
    db.add(requirement)
    db.commit()
    db.refresh(requirement)
    return requirement

@router.get("/requirements/", response_model=List[RequirementOut])
def list_requirements(db: Session = Depends(get_db), user: User = Depends(get_me)):
    return db.query(Requirement).filter_by(user_id=user.id).all() 