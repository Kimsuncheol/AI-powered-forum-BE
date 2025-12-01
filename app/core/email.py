import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

async def send_reset_password_email(to_email: str, token: str) -> None:
    if not settings.SMTP_HOST or not settings.SMTP_PORT or not settings.EMAILS_FROM_EMAIL:
        print("SMTP settings not configured. Skipping email send.")
        return

    message = MIMEMultipart("alternative")
    message["Subject"] = "Reset Your Password"
    message["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
    message["To"] = to_email

    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    
    html = f"""
    <html>
        <body>
            <p>Hello,</p>
            <p>You requested a password reset. Click the link below to reset your password:</p>
            <p><a href="{reset_link}">Reset Password</a></p>
            <p>If you didn't request this, please ignore this email.</p>
        </body>
    </html>
    """
    
    part = MIMEText(html, "html")
    message.attach(part)

    await aiosmtplib.send(
        message,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        use_tls=True,
    )
