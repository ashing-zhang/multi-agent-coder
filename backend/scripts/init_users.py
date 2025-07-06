import random
from backend.core.database import SessionLocal, engine
from backend.models.user import User
from sqlalchemy.exc import IntegrityError

# 生成100个用户
roles = ["user", "admin"]
users = [
    User(username=f"user{i}", password=f"pass{i}", role=random.choice(roles))
    for i in range(1, 101)
]

def main():
    # 创建表
    User.metadata.create_all(bind=engine)
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
