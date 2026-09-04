from unittest.mock import Mock, patch, AsyncMock

import pytest

from src.services.auth import auth_service


def test_get_me(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr(
            "fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr(
            "fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr(
            "fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("api/users/me", headers=headers)
        assert response.status_code == 200, response.text


def test_update_avatar(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        redis_mock.set.return_value = True
        redis_mock.expire.return_value = True
        monkeypatch.setattr(
            "fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr(
            "fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr(
            "fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        monkeypatch.setattr(
            "src.routes.users.cloudinary.uploader.upload",
            Mock(return_value={"version": "123456"}),
        )
        cloudinary_image_mock = Mock()
        cloudinary_image_mock.build_url.return_value = "https://example.com/avatar.jpg"
        monkeypatch.setattr(
            "src.routes.users.cloudinary.CloudinaryImage",
            Mock(return_value=cloudinary_image_mock),
        )

        headers = {"Authorization": f"Bearer {get_token}"}
        files = {"file": ("avatar.jpg", b"test image", "image/jpeg")}

        response = client.patch("api/users/avatar", headers=headers, files=files)

        assert response.status_code == 200, response.text
        data = response.json()
        assert data["avatar"] == "https://example.com/avatar.jpg"
