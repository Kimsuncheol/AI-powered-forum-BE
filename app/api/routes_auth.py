from typing import Any
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse, ForgotPasswordRequest
from app.schemas.msg import Msg
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.email_service import EmailService
from fastapi import HTTPException

router = APIRouter()

@router.post("/signup", response_model=UserResponse)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
) -> Any:
    user = UserService.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    return UserService.create(db, user_in)

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    return AuthService.authenticate(db, email=form_data.username, password=form_data.password)

@router.post("/forgot-password", response_model=Msg)
async def forgot_password(
    email: ForgotPasswordRequest,
    db: Session = Depends(deps.get_db),
) -> Any:
    await EmailService.send_password_reset(db, email.email)
    return {"msg": "Password recovery email sent"}
