import pytest
from app.core import email
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
    
    await email.send_reset_password_email("user@example.com", "token")
    
    assert mock_send.called
    assert mock_send.kwargs["hostname"] == "localhost"
    assert mock_send.kwargs["port"] == 587
