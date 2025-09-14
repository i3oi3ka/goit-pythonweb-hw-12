from datetime import date, timedelta
from typing import List

from sqlalchemy import select, extract, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas.contacts import ContactModel


class ContactRepository:
    """
    Repository class for managing Contact entities in the database.
    Provides CRUD operations and additional queries for contacts.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with a database session.
        Args:
            session (AsyncSession): SQLAlchemy async session.
        """
        self.db = session

    async def get_contacts(
        self, skip: int, limit: int, params: dict, user: User
    ) -> List[Contact]:
        """
        Retrieve a list of contacts for a user with optional filters and pagination.
        Args:
            skip (int): Number of records to skip.
            limit (int): Maximum number of records to return.
            params (dict): Filter parameters for contacts.
            user (User): The user whose contacts to retrieve.
        Returns:
            List[Contact]: List of Contact objects.
        """
        stmt = select(Contact).filter_by(**params, user=user).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return list(contacts.scalars().all())

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        """
        Get a contact by its ID for a specific user.
        Args:
            contact_id (int): The contact's ID.
            user (User): The user who owns the contact.
        Returns:
            Contact | None: The Contact object or None if not found.
        """
        stmt = select(Contact).filter_by(id=contact_id, user=user)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def get_contacts_by_filter(self, query: dict, user: User) -> Contact | None:
        """
        Get a contact by filter parameters for a specific user.
        Args:
            query (dict): Filter parameters.
            user (User): The user who owns the contact.
        Returns:
            Contact | None: The Contact object or None if not found.
        """
        stmt = select(Contact).filter_by(**query, user=user)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def check_contact_duplicate(self, body: ContactModel, user: User) -> bool:
        """
        Check if a contact with the same email or phone number exists for the user.
        Args:
            body (ContactModel): Contact data to check.
            user (User): The user to check for duplicates.
        Returns:
            bool: True if duplicate exists, False otherwise.
        """
        stmt = (
            select(Contact)
            .filter_by(user=user)
            .where(
                (Contact.email == body.email)
                | (Contact.phone_number == body.phone_number)
            )
        )
        result = await self.db.execute(stmt)
        existing_contact = result.scalar_one_or_none()
        return existing_contact is not None

    async def create_contact(self, body: ContactModel, user: User) -> Contact:
        """
        Create a new contact for the user.
        Args:
            body (ContactModel): Data for the new contact.
            user (User): The user to associate the contact with.
        Returns:
            Contact: The created Contact object.
        Raises:
            ValueError: If a duplicate contact exists.
        """
        if await self.check_contact_duplicate(body, user):
            raise ValueError("Contact with this email or phone number already exists.")

        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
        """
        Remove a contact by its ID for a specific user.
        Args:
            contact_id (int): The contact's ID.
            user (User): The user who owns the contact.
        Returns:
            Contact | None: The removed Contact object or None if not found.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def update_contact(
        self, note_id: int, body: ContactModel, user: User
    ) -> Contact | None:
        """
        Update an existing contact for a user.
        Args:
            note_id (int): The contact's ID.
            body (ContactModel): Updated contact data.
            user (User): The user who owns the contact.
        Returns:
            Contact | None: The updated Contact object or None if not found.
        """
        contact = await self.get_contact_by_id(note_id, user)
        if contact:
            for key, value in body.model_dump(exclude_unset=True).items():
                setattr(contact, key, value)

            await self.db.commit()
            await self.db.refresh(contact)

        return contact

    async def get_contacts_with_upcoming_birthdays(self, user: User) -> List[Contact]:
        """
        Get contacts with birthdays in the next 7 days for a user.
        Args:
            user (User): The user whose contacts to check.
        Returns:
            List[Contact]: List of contacts with upcoming birthdays.
        """
        today = date.today()
        future_date = today + timedelta(days=7)
        stmt = (
            select(Contact)
            .filter_by(user=user)
            .filter(
                and_(
                    extract("month", Contact.birthday) >= today.month,
                    extract("day", Contact.birthday) >= today.day,
                    extract("month", Contact.birthday) <= future_date.month,
                    extract("day", Contact.birthday) <= future_date.day,
                )
            )
        )
        contacts = await self.db.execute(stmt)
        return list(contacts.scalars().all())
