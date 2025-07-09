import random
from backend.core.database import SessionLocal, engine
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

def main():
    db = SessionLocal()
    for user in users:
        db.add(user)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
    db.close()

if __name__ == "__main__":
    main()
