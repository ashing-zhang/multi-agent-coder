from coder_agents_demo import model_client
from fastapi import APIRouter
from pydantic import BaseModel
from backend.agents.set_key import set_deepseek_api_key

router = APIRouter()

class APIKeyIn(BaseModel):
    api_key: str

@router.post("/api/set_deepseek_key")
def set_deepseek_key_api(data: APIKeyIn):
    try:
        model_client = set_deepseek_api_key(data.api_key)
        return {"success": True, "model_client": model_client}
    except Exception as e:
        return {"success": False, "error": str(e)} 