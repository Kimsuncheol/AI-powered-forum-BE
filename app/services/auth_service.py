from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.core import security
from app.core.config import settings
from app.services.user_service import UserService
from app.schemas.token import Token

class AuthService:
    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> Token:
        user = UserService.get_by_email(db, email)
        if not user or not security.verify_password(password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Incorrect email or password")
        
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
            
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return Token(
            access_token=security.create_access_token(
                user.id, expires_delta=access_token_expires
            ),
            token_type="bearer",
        )
