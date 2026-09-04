import unittest
from unittest.mock import AsyncMock, patch

from src.services.email import send_email, send_password_reset_email


class TestEmailService(unittest.IsolatedAsyncioTestCase):

    async def test_send_email(self):
        with patch("src.services.email.FastMail") as mock_fast_mail:
            mock_fast_mail.return_value.send_message = AsyncMock()

            await send_email(
                "test@example.com",
                "test_user",
                "http://testserver/",
            )

            mock_fast_mail.return_value.send_message.assert_called_once()
            _, kwargs = mock_fast_mail.return_value.send_message.call_args
            self.assertEqual(kwargs["template_name"], "verify_email.html")

    async def test_send_password_reset_email(self):
        with patch("src.services.email.FastMail") as mock_fast_mail:
            mock_fast_mail.return_value.send_message = AsyncMock()

            await send_password_reset_email(
                "test@example.com",
                "test_user",
                "http://testserver/",
            )

            mock_fast_mail.return_value.send_message.assert_called_once()
            _, kwargs = mock_fast_mail.return_value.send_message.call_args
            self.assertEqual(kwargs["template_name"], "reset_password.html")
