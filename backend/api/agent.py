from fastapi import APIRouter

router = APIRouter()

@router.get("/list")
def list_agents():
    """获取所有Agent类型"""
    return [
        "需求分析Agent", "代码生成Agent", "代码审查Agent", "代码整合Agent", "文档Agent", "测试Agent"
    ]
