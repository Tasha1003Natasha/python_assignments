import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User
from src.repository.users import (
    confirmed_email,
    create_user,
    get_user_by_email,
    update_avatar_url,
    update_password,
    update_token,
)
from src.schemas.user import UserSchema


class TestAsyncUser(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.user = User(
            id=1,
            username="test_user",
            email="test_user@example.com",
            password="qwerty",
            avatar="https://example.com/avatar.png",
            confirmed=False,
        )
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_user_by_email(self):
        email = "test_user@example.com"
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = self.user
        self.session.execute.return_value = mocked_user

        result = await get_user_by_email(email, self.session)

        self.assertEqual(result, self.user)

    async def test_create_user(self):
        body = UserSchema(
            username="test_user",
            email="test_user@example.com",
            password="12345678",
        )

        with patch("src.repository.users.Gravatar") as mock_gravatar:
            mock_gravatar.return_value.get_image.return_value = "https://example.com/avatar.png"

            result = await create_user(body, self.session)

        self.assertIsInstance(result, User)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)
        self.assertEqual(result.avatar, "https://example.com/avatar.png")
        self.session.add.assert_called_once()
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(result)

    async def test_update_token(self):
        token = "refresh_token"

        await update_token(self.user, token, self.session)

        self.assertEqual(self.user.refresh_token, token)
        self.session.commit.assert_called_once()

    async def test_confirmed_email(self):
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = self.user
        self.session.execute.return_value = mocked_user

        await confirmed_email(self.user.email, self.session)

        self.assertTrue(self.user.confirmed)
        self.session.commit.assert_called_once()

    async def test_update_avatar_url(self):
        url = "https://example.com/new-avatar.png"
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = self.user
        self.session.execute.return_value = mocked_user

        result = await update_avatar_url(self.user.email, url, self.session)

        self.assertEqual(result, self.user)
        self.assertEqual(self.user.avatar, url)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(self.user)

    async def test_update_password(self):
        new_password = "new_password_hash"
        self.user.refresh_token = "old_refresh_token"

        await update_password(self.user, new_password, self.session)

        self.assertEqual(self.user.password, new_password)
        self.assertIsNone(self.user.refresh_token)
        self.session.commit.assert_called_once()
