import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.repository.contacts import ContactRepository
from src.schemas.contacts import ContactModel

from datetime import date


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def contact_repository(mock_session):
    return ContactRepository(mock_session)


@pytest.fixture
def user():
    return User(id=1, username="testuser")


@pytest.mark.asyncio
async def test_get_contacts(contact_repository, mock_session, user):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        Contact(
            first_name="test_first_name",
            last_name="test_last_name",
            email="test_email@gmail.com",
            phone_number="380935057017",
            birthday="1989-01-01",
            description="test_contact",
            user_id=user.id,
        )
    ]
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    contacts = await contact_repository.get_contacts(
        params={}, skip=0, limit=10, user=user
    )

    # Assertions
    assert len(contacts) == 1
    assert contacts[0].first_name == "test_first_name"


@pytest.mark.asyncio
async def test_get_contact_by_id(contact_repository, mock_session, user):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = Contact(
        id=1,
        first_name="test_first_name",
        last_name="test_last_name",
        email="test_email@gmail.com",
        phone_number="380935057017",
        birthday="1989-01-01",
        description="test_contact",
        user_id=user.id,
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    contact = await contact_repository.get_contact_by_id(contact_id=1, user=user)

    # Assertions
    assert contact is not None
    assert contact.id == 1
    assert contact.first_name == "test_first_name"


@pytest.mark.asyncio
async def test_create_contact(contact_repository, mock_session, user):
    # Setup
    contact_data = ContactModel(
        first_name="test_first_name",
        last_name="test_last_name",
        email="test@gmail.com",
        phone_number="380915057018",
        birthday=date.today(),
        description="test_contact",
    )
    contact_repository.check_contact_duplicate = AsyncMock(return_value=False)
    # Call method
    result = await contact_repository.create_contact(body=contact_data, user=user)

    # Assertions
    assert isinstance(result, Contact)
    assert result.first_name == "test_first_name"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_remove_contact(contact_repository, mock_session, user):
    # Setup
    existing_contact = Contact(
        first_name="contact to delete",
        last_name="test_last_name",
        email="test_email@gmail.com",
        phone_number="380935057017",
        birthday="1989-01-01",
        description="test_contact",
        user_id=user.id,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.remove_contact(contact_id=1, user=user)

    # Assertions
    assert result is not None
    assert result.first_name == "contact to delete"
    mock_session.delete.assert_awaited_once_with(existing_contact)
    mock_session.commit.assert_awaited_once()
