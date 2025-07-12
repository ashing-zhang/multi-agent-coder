from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.models.user import User as UserModel
from backend.core.database import get_db
from fastapi.security import OAuth2PasswordBearer
from backend.auth.process_token import decode_access_token

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

class SetKeyRequest(BaseModel):
    api_key: str

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    username = payload.get("sub")
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="无效token")
    return user

@router.post("/set_key")
def set_api_key(
    data: SetKeyRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    current_user.api_key = data.api_key
    db.commit()
    return {"api_key": current_user.api_key}
