"""
Authentication and authorization services for FastAPI application.
Includes password hashing, JWT token creation, and user retrieval.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt, JWTError

from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, UTC

from src.conf.settings import settings
from src.database.db import get_db
from src.schemas.users import User
from src.services.users import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


class Hash:
    """
    Utility class for password hashing and verification using bcrypt.
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def verify_password(self, plain_password, hashed_password) -> bool:
        """
        Verify a plain password against a hashed password.
        Args:
            plain_password (str): The plain text password.
            hashed_password (str): The hashed password.
        Returns:
            bool: True if passwords match, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    async def get_password_hash(self, password: str) -> str:
        """
        Hash a password using bcrypt.
        Args:
            password (str): The plain text password.
        Returns:
            str: The hashed password.
        """
        return self.pwd_context.hash(password)


async def create_access_token(data: dict, expires_delta: int | None = None) -> str:
    """
    Create a JWT access token for authentication.
    Args:
        data (dict): Data to encode in the token.
        expires_delta (int, optional): Expiration time in minutes.
    Returns:
        str: Encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta is None:
        expires_delta = settings.JWT_EXP_MIN
    expire = datetime.now() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encode_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    """
    Retrieve the current authenticated user from JWT token.
    Args:
        token (str): JWT token from request.
        db (AsyncSession): SQLAlchemy async session.
    Returns:
        User: The authenticated user object.
    Raises:
        HTTPException: If credentials are invalid or user not found.
    """
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username = payload.get("sub")
        if username is None:
            raise credential_exception
    except JWTError as e:
        raise credential_exception

    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)
    if user is None:
        raise credential_exception
    return User.model_validate(user)


async def create_email_token(data: dict) -> str:
    """
    Create a JWT token for email confirmation.
    Args:
        data (dict): Data to encode in the token.
    Returns:
        str: Encoded JWT token for email confirmation.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


async def get_email_from_token(token: str) -> str:
    """
    Decode email address from JWT token.
    Args:
        token (str): JWT token containing email.
    Returns:
        str: Email address from token.
    Raises:
        HTTPException: If token is invalid or cannot be processed.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=settings.JWT_ALGORITHM
        )
        email = payload["sub"]
        return email
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uncorrect token for email check",
        )
