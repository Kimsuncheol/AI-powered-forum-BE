from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.core.config import settings
from app.models.user import User
from app.schemas.msg import Msg
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse, ForgotPasswordRequest, ResetPasswordRequest

router = APIRouter()

@router.post("/signup", response_model=UserResponse)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
) -> Any:
    """
    Create new user.
    """
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        name=user_in.name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.get("/me", response_model=UserResponse)
def read_users_me(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

from app.core import email as email_utils

@router.post("/forgot-password", response_model=Msg)
async def forgot_password(
    email: ForgotPasswordRequest,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Password Recovery
    """
    user = db.query(User).filter(User.email == email.email).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    
    # Generate a reset token (reusing access token logic for now as per plan)
    reset_token = security.create_access_token(user.id, expires_delta=timedelta(minutes=15))
    
    try:
        await email_utils.send_reset_password_email(to_email=user.email, token=reset_token)
    except Exception as e:
        print(f"Failed to send email: {e}")
        # In a real app, we might want to raise 500, but for now we'll log and return success to avoid leaking info
        # or raise 500 as requested by prompt
        raise HTTPException(
            status_code=500,
            detail="Failed to send password recovery email.",
        )

    return {"msg": "Password recovery email sent"}
