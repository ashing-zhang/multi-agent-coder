from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.models.user import User as UserModel
from ..core.database import get_db
from ..core.utils import get_current_user
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

class SetKeyRequest(BaseModel):
    api_key: str

@router.post("/set_key")
def set_api_key(
    data: SetKeyRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    current_user.api_key = data.api_key
    db.commit()
    return {"api_key": current_user.api_key}
