"""
Service layer for Contact entity operations.
Handles business logic and error handling for contacts.
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactRepository
from src.schemas.contacts import ContactModel
from src.database.models import User


class ContactService:
    """
    Service class for managing contacts.
    Provides methods for CRUD operations and birthday queries.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the service with a database session.
        Args:
            db (AsyncSession): SQLAlchemy async session.
        """
        self.contact_repository = ContactRepository(db)

    async def create_contact(self, body: ContactModel, user: User):
        """
        Create a new contact for the user.
        Args:
            body (ContactModel): Data for the new contact.
            user (User): The user to associate the contact with.
        Returns:
            Contact: The created contact object.
        Raises:
            HTTPException: If a duplicate contact exists.
        """
        try:
            return await self.contact_repository.create_contact(body, user)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def get_contacts(self, skip: int, limit: int, params: dict, user: User):
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
        return await self.contact_repository.get_contacts(skip, limit, params, user)

    async def get_contact(self, contact_id: int, user: User):
        """
        Get a contact by its ID for a specific user.
        Args:
            contact_id (int): The contact's ID.
            user (User): The user who owns the contact.
        Returns:
            Contact | None: The Contact object or None if not found.
        """
        return await self.contact_repository.get_contact_by_id(contact_id, user)

    async def update_contact(self, contact_id: int, body: ContactModel, user: User):
        """
        Update an existing contact for a user.
        Args:
            contact_id (int): The contact's ID.
            body (ContactModel): Updated contact data.
            user (User): The user who owns the contact.
        Returns:
            Contact | None: The updated Contact object or None if not found.
        """
        return await self.contact_repository.update_contact(contact_id, body, user)

    async def remove_contact(self, contact_id: int, user: User):
        """
        Remove a contact by its ID for a specific user.
        Args:
            contact_id (int): The contact's ID.
            user (User): The user who owns the contact.
        Returns:
            Contact | None: The removed Contact object or None if not found.
        """
        return await self.contact_repository.remove_contact(contact_id, user)

    async def get_contacts_with_upcoming_birthdays(self, user: User):
        """
        Get contacts with birthdays in the next 7 days for a user.
        Args:
            user (User): The user whose contacts to check.
        Returns:
            List[Contact]: List of contacts with upcoming birthdays.
        """
        return await self.contact_repository.get_contacts_with_upcoming_birthdays(user)
