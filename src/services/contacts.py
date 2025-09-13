from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactRepository
from src.schemas.contacts import ContactModel
from src.database.models import User


class ContactService:
    def __init__(self, db: AsyncSession):
        self.contact_repository = ContactRepository(db)

    async def create_contact(self, body: ContactModel, user: User):
        try:
            return await self.contact_repository.create_contact(body, user)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def get_contacts(self, skip: int, limit: int, params: dict, user: User):
        return await self.contact_repository.get_contacts(skip, limit, params, user)

    async def get_contact(self, contact_id: int, user: User):
        return await self.contact_repository.get_contact_by_id(contact_id, user)

    async def update_contact(self, contact_id: int, body: ContactModel, user: User):
        return await self.contact_repository.update_contact(contact_id, body, user)

    async def remove_contact(self, contact_id: int, user: User):
        return await self.contact_repository.remove_contact(contact_id, user)

    async def get_contacts_with_upcoming_birthdays(self, user: User):
        return await self.contact_repository.get_contacts_with_upcoming_birthdays(user)
