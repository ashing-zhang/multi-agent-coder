from backend.auth.process_token import decode_access_token
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from .database import get_db, oauth2_scheme
from backend.models.user import User as UserModel

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    username = payload.get("sub")
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="无效token")
    return user