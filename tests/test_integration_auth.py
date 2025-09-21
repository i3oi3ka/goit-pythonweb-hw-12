from unittest.mock import Mock
from unittest.mock import AsyncMock
import pytest
from sqlalchemy import select

from src.database.models import User
from tests.conftest import TestingSessionLocal

user_data = {
    "username": "agent007",
    "email": "agent007@gmail.com",
    "password": "12345678",
}


def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_mail", mock_send_email)
    response = client.post("api/auth/sign_up/", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "password" not in data
    assert "avatar" in data


def test_repeat_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_mail", mock_send_email)
    response = client.post("api/auth/sign_up/", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert (
        data["detail"] == f"User with username: {user_data["username"]} already exists"
    )


def test_not_confirmed_login(client):
    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email address not confirmed"


@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == user_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data


def test_wrong_password_login(client):
    response = client.post(
        "api/auth/login",
        data={"username": user_data.get("username"), "password": "password"},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Incorrect login or password"


def test_wrong_username_login(client):
    response = client.post(
        "api/auth/login",
        data={"username": "username", "password": user_data.get("password")},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Incorrect login or password"


def test_validation_error_login(client):
    response = client.post(
        "api/auth/login", data={"password": user_data.get("password")}
    )
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data


def test_signup_email_already_exists(client, monkeypatch):
    """Try to register with an email that already exists but a different username."""
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_mail", mock_send_email)
    user_data2 = {
        "username": "agent008",
        "email": "agent007@gmail.com",  # same email as user_data
        "password": "87654321",
    }
    response = client.post("api/auth/sign_up/", json=user_data2)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == f"User with email: {user_data2['email']} already exists"


def test_signup_validation_error(client, monkeypatch):
    """Try to register with missing required fields."""
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_mail", mock_send_email)
    incomplete_data = {
        "username": "agent009",
        "email": "agent009@gmail.com",
        # missing password
    }
    response = client.post("api/auth/sign_up/", json=incomplete_data)
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data


def test_confirmed_email_invalid_token(client):
    """Try to confirm email with an invalid token."""
    response = client.get("api/auth/confirmed_email/invalidtoken")
    assert response.status_code == 422
    data = response.json()
    assert data["detail"] == "Uncorrect token for email check"


def test_request_email_not_found(client, monkeypatch):
    """Try to request email confirmation for a non-existent email."""
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_mail", mock_send_email)
    body = {"email": "notfound@gmail.com"}
    response = client.post("api/auth/request_email/", json=body)
    assert response.status_code == 404, response.text
    data = response.json()
    assert "User with this email not found" in data["detail"]


def test_request_email_already_confirmed(client):
    """Try to request email confirmation for an already confirmed user."""
    body = {"email": user_data["email"]}
    response = client.post("api/auth/request_email/", json=body)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Your email already confirmed"


def test_request_email_success(client, monkeypatch):
    """Request email confirmation for an unconfirmed user."""
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_mail", mock_send_email)

    # First, create an unconfirmed user
    unconfirmed_user = {
        "username": "unconfirmed",
        "email": "unconfirmed@gmail.com",
        "password": "password",
    }
    response = client.post("api/auth/sign_up/", json=unconfirmed_user)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] in unconfirmed_user["username"]
    assert data["email"] in unconfirmed_user["email"]

    body = {"email": unconfirmed_user["email"]}
    response = client.post("api/auth/request_email/", json=body)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Check your email post"


def test_request_reset_password_not_found(client, monkeypatch):
    """Try to request password reset for a non-existent email."""
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_mail", mock_send_email)
    body = {"email": "notfound@gmail.com"}
    response = client.post("api/auth/request_reset_password/", json=body)
    assert response.status_code == 404, response.text
    data = response.json()
    assert (
        "User with this email not found, please check entered email." in data["detail"]
    )


def test_request_reset_password_success(client, monkeypatch):
    """Request password reset for an existing user."""
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_mail", mock_send_email)
    body = {"email": user_data["email"]}
    response = client.post("api/auth/request_reset_password/", json=body)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Check your email post"


def test_reset_password_invalid_token(client):
    """Try to reset password with an invalid token."""
    body = {"token": "invalidtoken", "new_password": "newpassword"}
    response = client.post("api/auth/reset_password/", json=body)
    assert response.status_code == 422, response.text
    data = response.json()
    assert data["detail"] == "Uncorrect token for email check"


def test_reset_password_success(client, monkeypatch):
    """Reset password with a valid token."""
    mock_get_email_from_token = AsyncMock(return_value=user_data["email"])
    monkeypatch.setattr("src.api.auth.get_email_from_token", mock_get_email_from_token)
    # monkeypatch.setattr(
    #     "src.services.auth.get_email_from_token", Mock(return_value="validtoken")
    # )
    body = {"token": "validtoken", "new_password": "newpassword"}
    response = client.post("api/auth/reset_password/", json=body)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "password successfully saved"
