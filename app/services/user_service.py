from sqlalchemy.orm import Session
from app.db.models import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

class UserService:
    @staticmethod
    def get_by_email(db: Session, email: str) -> User | None:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def create(db: Session, user_in: UserCreate) -> User:
        user = User(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            name=user_in.name,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
