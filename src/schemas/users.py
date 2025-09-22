"""
Pydantic schemas for User entity and authentication.
Defines models for user creation, response, token, and email requests.
"""

from pydantic import BaseModel, ConfigDict, EmailStr, SecretStr
from src.database.models import Role


class UserCreate(BaseModel):
    """
    Schema for creating a new user.
    Fields:
        email (EmailStr): User's email address.
        username (str): User's username.
        password (str): User's password.
    """

    email: EmailStr
    username: str
    password: str


class User(BaseModel):
    """
    Schema for returning user data in API responses.
    Fields:
        id (int): Unique user ID.
        email (EmailStr): User's email address.
        username (str): User's username.
        avatar (str): URL or path to user's avatar image.
    """

    id: int
    email: EmailStr
    username: str
    avatar: str
    roles: Role
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """
    Schema for JWT access token response.
    Fields:
        access_token (str): JWT token string.
        token_type (str): Type of token (e.g., 'bearer').
    """

    access_token: str
    refresh_token: str
    token_type: str


class TokenRefresh(BaseModel):
    """
    Schema for JWT token refresh request.
    Fields:
        refresh_token (str): JWT refresh token string.
    """

    refresh_token: str


class RequestEmail(BaseModel):
    """
    Schema for requesting email confirmation.
    Fields:
        email (EmailStr): User's email address.
    """

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """
    Schema for requesting password reset.

    Fields:
        token (str): Password reset token.
        new_password (str): New password for the user.
    """

    token: str
    new_password: str
