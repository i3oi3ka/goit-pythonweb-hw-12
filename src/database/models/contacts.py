"""
SQLAlchemy ORM model for Contact entity.
Defines fields, relationships, and validation logic for contacts.
"""

from datetime import datetime, date
from email_validator import validate_email, EmailNotValidError

from sqlalchemy import Integer, String, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import mapped_column, Mapped, validates, relationship
from sqlalchemy.sql.sqltypes import DateTime, Date
from src.database.models import Base

import re


class Contact(Base):
    """
    SQLAlchemy ORM model for a contact.
    Represents a contact entity with validation for email and phone number.
    """

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
        """
        Validate the email address using email_validator library.
        Args:
            key (str): Field name.
            address (str): Email address to validate.
        Returns:
            str: Validated email address.
        Raises:
            ValueError: If email is not valid.
        """
        try:
            validate_email(address)
        except EmailNotValidError as e:
            raise ValueError(f"Invalid email: {e}")
        return address

    @validates("phone_number")
    def validate_phone_number(self, key, value):
        """
        Validate the phone number format.
        Args:
            key (str): Field name.
            value (str): Phone number to validate.
        Returns:
            str: Validated phone number.
        Raises:
            ValueError: If phone number format is invalid.
        """
        if not re.match(r"^\+?\d{10,15}$", value):
            raise ValueError("Invalid phone number format.")
        return value

    def __repr__(self):
        """
        Return a string representation for debugging.
        """
        return f"<Contact(id={self.id}, name={self.first_name} {self.last_name}, email={self.email})>"

    def __str__(self):
        """
        Return a human-readable string representation.
        """
        return f"Contact(id={self.id}, name={self.first_name} {self.last_name}, email={self.email})"
