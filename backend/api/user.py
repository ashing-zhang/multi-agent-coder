from fastapi import APIRouter, Depends
from backend.api.auth import get_me, UserOut
from backend.models.user import User

router = APIRouter()

@router.get("/profile", response_model=UserOut)
def get_profile(current_user: User = Depends(get_me)):
    return current_user
