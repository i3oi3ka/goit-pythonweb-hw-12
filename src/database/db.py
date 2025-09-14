"""
Database session management for SQLAlchemy async engine.
Provides context manager and dependency for FastAPI.
"""

import contextlib

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from src.conf.settings import settings


class DatabaseSessionManager:
    """
    Manages SQLAlchemy async database sessions.
    Provides a context manager for session lifecycle and error handling.
    """

    def __init__(self, url: str):
        """
        Initialize the session manager with a database URL.
        Args:
            url (str): Database connection URL.
        """
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
        Async context manager for database session.
        Yields:
            AsyncSession: SQLAlchemy async session.
        Raises:
            Exception: If session maker is not initialized.
            SQLAlchemyError: On database errors, rolls back session.
        """
        if self._session_maker is None:
            raise Exception("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise  # Re-raise the original error
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(settings.DB_URL)


async def get_db():
    """
    FastAPI dependency for providing a database session.
    Yields:
        AsyncSession: SQLAlchemy async session.
    """
    async with sessionmanager.session() as session:
        yield session
