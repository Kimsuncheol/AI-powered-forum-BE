from app.core import email as email_utils
from app.core import security
from app.services.user_service import UserService
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import timedelta

class EmailService:
    @staticmethod
    async def send_password_reset(db: Session, email: str):
        user = UserService.get_by_email(db, email)
        if not user:
            raise HTTPException(
                status_code=404,
                detail="The user with this username does not exist in the system.",
            )
        
        reset_token = security.create_access_token(user.id, expires_delta=timedelta(minutes=15))
        
        try:
            await email_utils.send_reset_password_email(to_email=user.email, token=reset_token)
        except Exception as e:
            print(f"Failed to send email: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to send password recovery email.",
            )
