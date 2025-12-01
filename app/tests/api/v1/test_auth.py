from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core import security
from app.db.models import User

def create_test_user(db: Session, email: str, password: str) -> User:
    user = User(
        email=email,
        hashed_password=security.get_password_hash(password),
        name="Test User",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def test_signup(client: TestClient, db: Session) -> None:
    data = {"email": "signup@example.com", "password": "password", "name": "Signup User"}
    response = client.post(f"{settings.API_V1_STR}/auth/signup", json=data)
    assert response.status_code == 200
    content = response.json()
    assert content["email"] == data["email"]
    assert "id" in content

def test_login(client: TestClient, db: Session) -> None:
    email = "login@example.com"
    password = "password"
    create_test_user(db, email, password)
    
    login_data = {"username": email, "password": password}
    response = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert tokens["token_type"] == "bearer"

def test_read_users_me(client: TestClient, db: Session) -> None:
    email = "me@example.com"
    password = "password"
    create_test_user(db, email, password)
    
    login_data = {"username": email, "password": password}
    response = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    token = response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"{settings.API_V1_STR}/auth/me", headers=headers)
    assert response.status_code == 200
    content = response.json()
    assert content["email"] == email

def test_forgot_password(client: TestClient, db: Session, monkeypatch) -> None:
    email = "forgot@example.com"
    password = "password"
    create_test_user(db, email, password)

    # Mock email sending
    async def mock_send_email(to_email, token):
        return None
    
    from app.core import email as email_module
    monkeypatch.setattr(email_module, "send_reset_password_email", mock_send_email)
    
    data = {"email": email}
    response = client.post(f"{settings.API_V1_STR}/auth/forgot-password", json=data)
    assert response.status_code == 200
    assert response.json()["msg"] == "Password recovery email sent"
