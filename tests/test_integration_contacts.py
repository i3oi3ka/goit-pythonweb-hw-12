def test_create_contact(client, get_token):
    response = client.post(
        "/api/contacts",
        json={
            "first_name": "test_first_name",
            "last_name": "test_last_name",
            "email": "test_email@gmail.com",
            "phone_number": "380935057017",
            "birthday": "1989-01-01",
            "description": "test_contact",
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["first_name"] == "test_first_name"
    assert "id" in data


def test_create_contact_invalid_email(client, get_token):
    response = client.post(
        "/api/contacts",
        json={
            "first_name": "test_first_name",
            "last_name": "test_last_name",
            "email": "not-an-email",
            "phone_number": "380935057018",
            "birthday": "1989-01-01",
            "description": "test_contact",
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )

    assert response.status_code == 422
    data = response.json()
    assert any("email" in str(err["loc"]) for err in data["detail"])


def test_create_contact_duplicate_email(client, get_token):
    # Create first contact
    response1 = client.post(
        "/api/contacts",
        json={
            "first_name": "dup_first_name",
            "last_name": "dup_last_name",
            "email": "dup_email@gmail.com",
            "phone_number": "380935057019",
            "birthday": "1990-01-01",
            "description": "dup_contact",
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response1.status_code == 201
    # Try to create duplicate
    response2 = client.post(
        "/api/contacts",
        json={
            "first_name": "dup_first_name2",
            "last_name": "dup_last_name2",
            "email": "dup_email@gmail.com",
            "phone_number": "380935057020",
            "birthday": "1991-01-01",
            "description": "dup_contact2",
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response2.status_code in (400, 409)
    data = response2.json()
    assert "already exists" in data["detail"]


def test_create_contact_unauthorized(client):
    response = client.post(
        "/api/contacts",
        json={
            "first_name": "unauth_first_name",
            "last_name": "unauth_last_name",
            "email": "unauth_email@gmail.com",
            "phone_number": "380935057020",
            "birthday": "1992-01-01",
            "description": "unauth_contact",
        },
    )
    assert response.status_code == 401


def test_get_contact(client, get_token):
    response = client.get(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == "test_first_name"
    assert "id" in data


def test_get_contact_not_found(client, get_token):
    response = client.get(
        "/api/contacts/505", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_get_contacts(client, get_token):
    response = client.get(
        "/api/contacts", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["first_name"] == "test_first_name"
    assert "id" in data[0]


def test_update_contact(client, get_token):
    response = client.put(
        "/api/contacts/1",
        json={
            "first_name": "new_test_first_name",
            "last_name": "test_last_name",
            "email": "test_email@gmail.com",
            "phone_number": "380935057017",
            "birthday": "1989-01-01",
            "description": "test_contact",
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == "new_test_first_name"
    assert "id" in data


def test_update_contact_not_found(client, get_token):
    response = client.put(
        "/api/contacts/505",
        json={
            "first_name": "new_test_first_name",
            "last_name": "test_last_name",
            "email": "test_email@gmail.com",
            "phone_number": "380935057017",
            "birthday": "1989-01-01",
            "description": "test_contact",
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_delete_contact(client, get_token):
    response = client.delete(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == "new_test_first_name"
    assert "id" in data


def test_repeat_delete_contact(client, get_token):
    response = client.delete(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_get_contacts_with_upcoming_birthdays(client, get_token):
    # Create a contact with birthday in next 7 days
    from datetime import date, timedelta

    upcoming_birthday = (date.today() + timedelta(days=3)).strftime("%Y-%m-%d")
    response = client.post(
        "/api/contacts",
        json={
            "first_name": "birthday_first_name",
            "last_name": "birthday_last_name",
            "email": "birthday_email@gmail.com",
            "phone_number": "380935057021",
            "birthday": upcoming_birthday,
            "description": "birthday_contact",
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 201
    # Get contacts with upcoming birthdays
    response = client.get(
        "/api/contacts/upcoming_birthdays/",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert any(contact["first_name"] == "birthday_first_name" for contact in data)
