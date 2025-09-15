from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas.users import UserCreate


class UserRepository:
    """
    Repository class for managing User entities in the database.
    Provides CRUD operations and additional queries for users.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with a database session.

        Args:
            session (AsyncSession): SQLAlchemy async session.
        """
        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Retrieve a user by their ID.

        Args:
            user_id (int): The user's ID.

        Returns:
            User or None: The User object or None if not found.
        """
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Retrieve a user by their username.

        Args:
            username (str): The user's username.

        Returns:
            User or None: The User object or None if not found.
        -------
        User or None
            The User object or None if not found.
        """
        stmt = select(User).filter_by(username=username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Retrieve a user by their email address.

        Args:
            email (str): The user's email address.

        Returns:
            User or None: The User object or None if not found.
        """
        stmt = select(User).filter_by(email=email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: str | None = None) -> User:
        """
        Create a new user in the database.

        Args:
            body (UserCreate): Data for the new user.
            avatar (str, optional): URL or path to the user's avatar image.

        Returns:
            User: The created User object.
        """
        user = User(**body.model_dump(exclude_unset=True), avatar=avatar)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def confirmed_email(self, email: str) -> None:
        """
        Mark a user's email as confirmed.

        Args:
            email (str): The user's email address.

        Returns:
            None
        None
        """
        user = await self.get_user_by_email(email)
        if user is not None:
            user.confirmed = True
            await self.db.commit()

    async def update_avatar_url(self, email: str, url: str) -> User | None:
        """
        Update the avatar URL for a user.

        Args:
            email (str): The user's email address.
            url (str): The new avatar URL.

        Returns:
            User or None: The updated User object or None if user not found.
        """
        user = await self.get_user_by_email(email)
        if user is not None:
            user.avatar = url
            await self.db.commit()
            await self.db.refresh(user)
            return user
        return None
