"""
Contacts API routes for CRUD operations and birthday queries.
Uses FastAPI and SQLAlchemy async session.
"""

from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import User
from src.schemas.contacts import ContactModel, ContactResponse
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
    """
    Retrieve a list of contacts for the current user with optional filters and pagination.
    Args:
        first_name (str, optional): Filter by first name.
        last_name (str, optional): Filter by last name.
        email (EmailStr, optional): Filter by email.
        phone_number (str, optional): Filter by phone number.
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return.
        db (AsyncSession): SQLAlchemy async session.
        user (User): Current authenticated user.
    Returns:
        List[ContactResponse]: List of contacts.
    """
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
    """
    Retrieve a contact by its ID for the current user.
    Args:
        contact_id (int): The contact's ID.
        db (AsyncSession): SQLAlchemy async session.
        user (User): Current authenticated user.
    Returns:
        ContactResponse: The contact object.
    Raises:
        HTTPException: If contact not found.
    """
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
    """
    Create a new contact for the current user.
    Args:
        body (ContactModel): Data for the new contact.
        db (AsyncSession): SQLAlchemy async session.
        user (User): Current authenticated user.
    Returns:
        ContactResponse: The created contact object.
    """
    contact_service = ContactService(db)
    return await contact_service.create_contact(body, user)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactModel,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Update an existing contact for the current user.
    Args:
        body (ContactModel): Updated contact data.
        contact_id (int): The contact's ID.
        db (AsyncSession): SQLAlchemy async session.
        user (User): Current authenticated user.
    Returns:
        ContactResponse: The updated contact object.
    Raises:
        HTTPException: If contact not found.
    """
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
    """
    Remove a contact by its ID for the current user.
    Args:
        contact_id (int): The contact's ID.
        db (AsyncSession): SQLAlchemy async session.
        user (User): Current authenticated user.
    Returns:
        ContactResponse: The removed contact object.
    Raises:
        HTTPException: If contact not found.
    """
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
    """
    Get contacts with upcoming birthdays in the next 7 days for the current user.
    Args:
        db (AsyncSession): SQLAlchemy async session.
        user (User): Current authenticated user.
    Returns:
        List[ContactResponse]: List of contacts with upcoming birthdays.
    """
    contact_service = ContactService(db)
    return await contact_service.get_contacts_with_upcoming_birthdays(user)
