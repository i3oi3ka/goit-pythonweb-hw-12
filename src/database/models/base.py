"""
Base SQLAlchemy declarative class for all ORM models.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for SQLAlchemy ORM models.
    All models should inherit from this class.
    """

    pass
