import pytest
from app.services.email_service import EmailService
from app.core import email as email_utils
from app.core.config import settings

@pytest.mark.asyncio
async def test_send_reset_password_email(monkeypatch):
    # Mock settings
    monkeypatch.setattr(settings, "SMTP_HOST", "localhost")
    monkeypatch.setattr(settings, "SMTP_PORT", 587)
    monkeypatch.setattr(settings, "EMAILS_FROM_EMAIL", "admin@example.com")
    
    # Mock aiosmtplib.send
    class MockSend:
        called = False
        kwargs = {}
        
        async def __call__(self, message, **kwargs):
            self.called = True
            self.kwargs = kwargs
            return {}, "OK"
            
    mock_send = MockSend()
    monkeypatch.setattr("aiosmtplib.send", mock_send)
    
    # We need to mock UserService.get_by_email to return a user since EmailService uses it
    class MockUser:
        id = 1
        email = "user@example.com"
    
    monkeypatch.setattr("app.services.user_service.UserService.get_by_email", lambda db, email: MockUser())

    await EmailService.send_password_reset(None, "user@example.com")
    
    assert mock_send.called
    assert mock_send.kwargs["hostname"] == "localhost"
    assert mock_send.kwargs["port"] == 587
