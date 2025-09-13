from datetime import datetime, date
from pydantic import BaseModel, Field, ConfigDict, EmailStr


class ContactModel(BaseModel):
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: EmailStr
    phone_number: str = Field(max_length=15)
    birthday: date
    description: str = Field(max_length=150)


class ContactResponse(ContactModel):
    id: int
    model_config = ConfigDict(from_attributes=True)
    created_at: datetime
