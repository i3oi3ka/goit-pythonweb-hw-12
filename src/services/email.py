"""
Email service for sending confirmation emails using FastAPI-Mail.
Configures mail connection and provides async send_mail function.
"""

from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import create_email_token
from src.conf.settings import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def send_mail(
    email: EmailStr,
    username: str,
    host: str,
    template: str = "verify_email.html",
    subject: str = "Confirm your email",
) -> None:
    """
    Send a confirmation email to the user with a verification token.
    Args:
        email (EmailStr): Recipient's email address.
        username (str): Recipient's username.
        host (str): Host URL for verification link.
    Returns:
        None
    Raises:
        ConnectionErrors: If email sending fails.
    """
    try:
        token_verification = await create_email_token({"sub": email})
        message = MessageSchema(
            subject=subject,
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )
        fm = FastMail(conf)
        await fm.send_message(message, template_name=template)
    except ConnectionErrors as err:
        print(err)
