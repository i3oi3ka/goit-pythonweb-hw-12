"""
SQLAlchemy ORM model for User entity.
Defines fields, relationships, and user attributes.
"""

from sqlalchemy import Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models import Base


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

    contacts = relationship("Contact", back_populates="user", cascade="all, delete")
