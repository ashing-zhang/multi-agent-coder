import asyncio
import random
from backend.core.database import AsyncSessionLocal, engine
from backend.models.user import User
from backend.models.requirement import Requirement
from backend.models.generated_code import GeneratedCode
from sqlalchemy.exc import IntegrityError
from datetime import datetime

# 生成100个用户，补全所有必需字段
users = [
    User(
        username=f"user{i}",
        password=f"ashing_great{i}",
        email=f"user{i}@example.com",
        full_name=f"User {i}",
        avatar=None,
        phone=None,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        last_login=None
    )
    for i in range(1, 101)
]

async def main():
    async with AsyncSessionLocal() as db:
        for user in users:
            db.add(user)
            try:
                await db.commit()
            except IntegrityError:
                await db.rollback()

if __name__ == "__main__":
    asyncio.run(main())
