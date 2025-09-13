from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas.contacts import ContactModel, ContactResponse
from src.schemas.users import User
from src.services.contacts import ContactService
from src.services.auth import get_current_user

router = APIRouter(tags=["Contacts"], prefix="/contacts")


@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
    first_name: str | None = None,
    last_name: str | None = None,
    email: EmailStr | None = None,
    phone_number: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact_service = ContactService(db)
    params = {}
    if first_name:
        params["first_name"] = first_name
    if last_name:
        params["last_name"] = last_name
    if email:
        params["email"] = email
    if phone_number:
        params["phone_number"] = phone_number
    contacts = await contact_service.get_contacts(skip, limit, params, user)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactModel,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact_service = ContactService(db)
    return await contact_service.create_contact(body, user)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactModel,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    note_service = ContactService(db)
    contact = await note_service.remove_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.get("/upcoming_birthdays/", response_model=List[ContactResponse])
async def coming_birthday_contacts(
    db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)
):
    contact_service = ContactService(db)
    return await contact_service.get_contacts_with_upcoming_birthdays(user)
