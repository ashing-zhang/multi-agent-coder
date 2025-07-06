from fastapi import APIRouter, Depends
from backend.api.auth import get_me, User

router = APIRouter()

@router.get("/profile", response_model=User)
def get_profile(current_user: User = Depends(get_me)):
    return current_user
