"""
SQLAlchemy ORM model for User entity.
Defines fields, relationships, and user attributes.
"""

import enum
from sqlalchemy import Integer, String, Boolean, DateTime, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models import Base


class Role(enum.Enum):
    admin = "admin"
    moderator = "moderator"
    user = "user"


class User(Base):
    """
    SQLAlchemy ORM model for a user.

    Attributes:
        id (int): Primary key.
        username (str): Unique username.
        email (str): Unique email address.
        password (str): Hashed password.
        confirmed (bool): Email confirmation status.
        avatar (str): Avatar image URL or path.
        created_at (datetime): Timestamp of user creation.
        contacts (list[Contact]): List of user's contacts.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    avatar: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[int] = mapped_column(DateTime, default=func.now())
    roles: Mapped[Role] = mapped_column(Enum(Role, name="role_enum"), default=Role.user)

    contacts = relationship("Contact", back_populates="user", cascade="all, delete")
