"""
Service layer for User entity operations.
Handles business logic for user creation, retrieval, and avatar updates.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.repository.users import UserRepository
from src.schemas.users import UserCreate
from src.database.models import User


class UserService:
    """
    Service class for managing users.
    Provides methods for user CRUD operations and avatar management.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the service with a database session.
        Args:
            db (AsyncSession): SQLAlchemy async session.
        """
        self.user_repository = UserRepository(db)

    async def create_user(self, body: UserCreate) -> User | None:
        """
        Create a new user and set avatar using Gravatar.
        Args:
            body (UserCreate): Data for the new user.
        Returns:
            User: The created user object.
        """
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)
        return await self.user_repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Retrieve a user by their ID.
        Args:
            user_id (int): The user's ID.
        Returns:
            User: The user object.
        """
        return await self.user_repository.get_user_by_id(user_id)  # type: ignore

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Retrieve a user by their username.
        Args:
            username (str): The user's username.
        Returns:
            User: The user object.
        """
        return await self.user_repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Retrieve a user by their email address.
        Args:
            email (str): The user's email address.
        Returns:
            User: The user object.
        """
        return await self.user_repository.get_user_by_email(email)

    async def confirmed_email(self, email: str) -> None:
        """
        Mark a user's email as confirmed.
        Args:
            email (str): The user's email address.
        Returns:
            None
        """
        await self.user_repository.confirmed_email(email)

    async def update_avatar_url(self, email: str, url: str) -> User | None:
        """
        Update the avatar URL for a user.
        Args:
            email (str): The user's email address.
            url (str): The new avatar URL.
        Returns:
            User: The updated user object.
        """
        return await self.user_repository.update_avatar_url(email, url)

    async def update_user_password(self, user: User, new_password: str):
        return await self.user_repository.update_user_password(user, new_password)
