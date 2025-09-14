"""
Pydantic schemas for Contact entity.
Defines models for contact creation and response.
"""

from datetime import datetime, date
from pydantic import BaseModel, Field, ConfigDict, EmailStr


class ContactModel(BaseModel):
    """
    Schema for creating or updating a contact.
    Fields:
        first_name (str): Contact's first name.
        last_name (str): Contact's last name.
        email (EmailStr): Contact's email address.
        phone_number (str): Contact's phone number.
        birthday (date): Contact's birthday.
        description (str): Additional description.
    """

    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: EmailStr
    phone_number: str = Field(max_length=15)
    birthday: date
    description: str = Field(max_length=150)


class ContactResponse(ContactModel):
    """
    Schema for returning contact data in API responses.
    Extends ContactModel with id and created_at fields.
    Fields:
        id (int): Unique contact ID.
        created_at (datetime): Timestamp of creation.
    """

    id: int
    model_config = ConfigDict(from_attributes=True)
    created_at: datetime
