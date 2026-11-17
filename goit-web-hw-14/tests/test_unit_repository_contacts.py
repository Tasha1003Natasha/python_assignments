import unittest
from unittest.mock import MagicMock, AsyncMock, Mock
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.schemas.contact import ContactSchema, ContactUpdateSchema
from src.repository.contacts import create_contact, get_contacts, update_contact, delete_contact, get_birthdays


class TestAsyncContact(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.user = User(id=1, username='test_user',
                         email='test_user@example.com', password="qwerty", confirmed=True)
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_contacts(self):
        limit = 10
        offset = 0
        query = None
        contacts = [
            Contact(id=1, name='test_name_1', surname='test_surname_1',
                    email='test_email_1@example.com', phone='1234567890',
                    birthday=date(2000, 1, 1), user=self.user),
            Contact(id=2, name='test_name_2', surname='test_surname_2',
                    email='test_email_2@example.com', phone='1234567891',
                    birthday=date(2000, 1, 2), user=self.user)
        ]
        mocked_contacts = Mock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts(limit, offset, query, self.session, self.user)
        self.assertEqual(result, contacts)

    async def test_get_birthdays(self):
        today = date.today()
        birthday_soon = today.replace(year=2000)
        birthday_later = date(2000, 1, 1)
        if birthday_later.month == today.month and birthday_later.day == today.day:
            birthday_later = date(2000, 2, 1)

        contacts = [
            Contact(id=1, name='test_name_1', surname='test_surname_1',
                    email='test_email_1@example.com', phone='1234567890',
                    birthday=birthday_soon, user=self.user),
            Contact(id=2, name='test_name_2', surname='test_surname_2',
                    email='test_email_2@example.com', phone='1234567891',
                    birthday=birthday_later, user=self.user)
        ]
        mocked_contacts = Mock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_birthdays(self.session, self.user)
        self.assertEqual(result, [contacts[0]])

    async def test_create_contact(self):
        body = ContactSchema(name='test_name', surname='test_surname',
                             email='test_email@example.com',
                             phone='1234567890', birthday=date(2000, 1, 1))
        result = await create_contact(body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.surname, body.surname)
        self.assertEqual(result.email, body.email)

    async def test_update_contact(self):
        body = ContactUpdateSchema(
            name='test_name', surname='test_surname',
            email='test_email@example.com', phone='1234567890',
            birthday=date(2000, 1, 1), completed=True)
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(
            id=1, name='old_name', surname='old_surname',
            email='old_email@example.com', phone='0987654321',
            birthday=date(1999, 1, 1), user=self.user)
        self.session.execute.return_value = mocked_contact
        result = await update_contact(1, body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.surname, body.surname)
        self.assertEqual(result.email, body.email)

    async def test_delete_contact(self):
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(
            id=1, name='test_name', surname='test_surname',
            email='test_email@example.com', phone='1234567890',
            birthday=date(2000, 1, 1), user=self.user)
        self.session.execute.return_value = mocked_contact
        result = await delete_contact(1, self.session, self.user)
        self.session.delete.assert_called_once()
        self.session.commit.assert_called_once()

        self.assertIsInstance(result, Contact)
