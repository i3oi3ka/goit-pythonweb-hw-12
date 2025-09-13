"""
models
"""

from datetime import datetime, date
from email_validator import validate_email, EmailNotValidError

from sqlalchemy import Integer, String, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import mapped_column, Mapped, validates, relationship
from sqlalchemy.sql.sqltypes import DateTime, Date
from src.database.models import Base

import re


class Contact(Base):
    __tablename__ = "contacts"

    __table_args__ = (
        UniqueConstraint("user_id", "email", name="uq_user_contact_email"),
        UniqueConstraint("user_id", "phone_number", name="uq_user_contact_phone"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(15), nullable=False)
    birthday: Mapped[date] = mapped_column(Date)
    description: Mapped[str] = mapped_column(String(150), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        "created_at", DateTime, default=func.now()
    )

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="contacts")

    @validates("email")
    def validate_email_with_library(self, key, address):
        try:
            validate_email(address)
        except EmailNotValidError as e:
            raise ValueError(f"Invalid email: {e}")
        return address

    @validates("phone_number")
    def validate_phone_number(self, key, value):
        if not re.match(r"^\+?\d{10,15}$", value):
            raise ValueError("Invalid phone number format.")
        return value

    def __repr__(self):
        return f"<Contact(id={self.id}, name={self.first_name} {self.last_name}, email={self.email})>"

    def __str__(self):
        return f"Contact(id={self.id}, name={self.first_name} {self.last_name}, email={self.email})"
