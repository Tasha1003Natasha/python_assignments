from unittest.mock import Mock, patch
from datetime import date
from uuid import uuid4

import pytest

from src.services.auth import auth_service


def auth_headers(get_token):
    return {"Authorization": f"Bearer {get_token}"}


def unique_email(prefix="contact"):
    return f"{prefix}-{uuid4().hex}@example.com"


def contact_payload(email=None, birthday="2000-01-01"):
    return {
        "name": "test",
        "surname": "test",
        "email": email or unique_email(),
        "phone": "1234567890",
        "birthday": birthday,
    }


def test_get_contacts(client, get_token):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        headers = auth_headers(get_token)
        response = client.get("api/contacts", headers=headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)


def test_create_contact(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        headers = auth_headers(get_token)
        email = unique_email("create-contact")
        response = client.post(
            "api/contacts",
            headers=headers,
            json=contact_payload(email),
        )
        assert response.status_code == 201, response.text
        data = response.json()
        assert "id" in data
        assert data["name"] == "test"
        assert data["surname"] == "test"
        assert data["email"] == email


def test_get_contact(client, get_token):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        headers = auth_headers(get_token)
        email = unique_email("get-contact")
        created_contact = client.post(
            "api/contacts",
            headers=headers,
            json=contact_payload(email),
        ).json()

        response = client.get(
            f"api/contacts/{created_contact['id']}",
            headers=headers,
        )

        assert response.status_code == 200, response.text
        data = response.json()
        assert data["id"] == created_contact["id"]
        assert data["email"] == email


def test_get_contact_not_found(client, get_token):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        headers = auth_headers(get_token)

        response = client.get("api/contacts/999999", headers=headers)

        assert response.status_code == 404, response.text
        assert response.json()["detail"] == "NOT FOUND"


def test_get_birthdays(client, get_token):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        headers = auth_headers(get_token)
        birthday = date.today().replace(year=2000).isoformat()
        email = unique_email("birthday")
        client.post(
            "api/contacts",
            headers=headers,
            json=contact_payload(email, birthday),
        )

        response = client.get("api/contacts/birthdays", headers=headers)

        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) >= 1
        assert any(contact["email"] == email for contact in data)


def test_update_contact(client, get_token):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        headers = auth_headers(get_token)
        created_contact = client.post(
            "api/contacts",
            headers=headers,
            json=contact_payload(unique_email("update-contact")),
        ).json()
        email = unique_email("updated-contact")
        update_data = contact_payload(email)
        update_data["name"] = "updated"
        update_data["surname"] = "contact"
        update_data["completed"] = True

        response = client.put(
            f"api/contacts/{created_contact['id']}",
            headers=headers,
            json=update_data,
        )

        assert response.status_code == 200, response.text
        data = response.json()
        assert data["id"] == created_contact["id"]
        assert data["name"] == "updated"
        assert data["surname"] == "contact"
        assert data["email"] == email
        assert data["completed"] is True


def test_update_contact_not_found(client, get_token):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        headers = auth_headers(get_token)
        update_data = contact_payload(unique_email("not-found-update"))
        update_data["completed"] = True

        response = client.put(
            "api/contacts/999999",
            headers=headers,
            json=update_data,
        )

        assert response.status_code == 404, response.text
        assert response.json()["detail"] == "NOT FOUND"


def test_delete_contact(client, get_token):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        headers = auth_headers(get_token)
        created_contact = client.post(
            "api/contacts",
            headers=headers,
            json=contact_payload(unique_email("delete-contact")),
        ).json()

        response = client.delete(
            f"api/contacts/{created_contact['id']}",
            headers=headers,
        )

        assert response.status_code == 204, response.text
