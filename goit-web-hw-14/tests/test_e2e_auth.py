from unittest.mock import Mock

import pytest
from sqlalchemy import select

from src.entity.models import User
from tests.conftest import TestingSessionLocal
from src.services.auth import auth_service

user_data = {"username": "agent007",
             "email": "agent007@gmail.com", "password": "12345678"}


def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("api/auth/signup", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "password" not in data
    assert "avatar" in data


def test_repeat_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("api/auth/signup", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Account already exists"


def test_not_confirmed_login(client):
    response = client.post("api/auth/login",
                           data={"username": user_data.get("email"), "password": user_data.get("password")})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email not confirmed"


@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(User).where(User.email == user_data.get("email")))
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post("api/auth/login",
                           data={"username": user_data.get("email"), "password": user_data.get("password")})
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data


def test_wrong_password_login(client):
    response = client.post("api/auth/login",
                           data={"username": user_data.get("email"), "password": "password"})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid password"


def test_wrong_email_login(client):
    response = client.post("api/auth/login",
                           data={"username": "email", "password": user_data.get("password")})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid email"


def test_validation_error_login(client):
    response = client.post("api/auth/login",
                           data={"password": user_data.get("password")})
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_refresh_token(client):
    refresh_token = await auth_service.create_refresh_token(
        data={"sub": user_data.get("email")}
    )

    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == user_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        current_user.refresh_token = refresh_token
        await session.commit()

    headers = {"Authorization": f"Bearer {refresh_token}"}

    response = client.get("api/auth/refresh_token", headers=headers)

    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_confirmed_email(client):
    email = "confirm-user@example.com"
    password = auth_service.get_password_hash("12345678")

    async with TestingSessionLocal() as session:
        user = User(
            username="confirm_user",
            email=email,
            password=password,
            avatar="https://example.com/avatar.png",
            confirmed=False,
        )
        session.add(user)
        await session.commit()

    token = auth_service.create_email_token(data={"sub": email})

    response = client.get(f"api/auth/confirmed_email/{token}")

    assert response.status_code == 200, response.text
    assert response.json()["message"] == "Email confirmed"


def test_request_email_for_confirmed_user(client):
    response = client.post(
        "api/auth/request_email",
        json={"email": "deadpool@example.com"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["message"] == "Your email is already confirmed"


def test_request_password_reset(client, monkeypatch):
    mock_send_password_reset_email = Mock()
    monkeypatch.setattr(
        "src.routes.auth.send_password_reset_email",
        mock_send_password_reset_email,
    )

    response = client.post(
        "api/auth/request_password_reset",
        json={"email": "deadpool@example.com"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["message"] == "If this email exists, password reset instructions were sent."


@pytest.mark.asyncio
async def test_reset_password(client):
    token = auth_service.create_password_reset_token(
        data={"sub": "deadpool@example.com"}
    )

    response = client.post(
        "api/auth/reset_password",
        json={"token": token, "password": "87654321"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["message"] == "Password successfully changed"
