from backend.auth.process_token import decode_access_token
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends, HTTPException
from .database import get_db, oauth2_scheme
from backend.models.user import User as UserModel

async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    username = payload.get("sub")
    result = await db.execute(select(UserModel).filter(UserModel.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="无效token")
    return user