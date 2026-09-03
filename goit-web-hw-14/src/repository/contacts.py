from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta
from src.entity.models import Contact, User
from src.schemas.contact import ContactSchema, ContactUpdateSchema


async def get_contacts(limit: int, offset: int, query: str | None,
                       db: AsyncSession, user: User):
    """
    Retrieve contacts belonging to a user with pagination and an optional search.

    :param limit: The maximum number of contacts to return.
    :type limit: int
    :param offset: The number of contacts to skip before collecting results.
    :type offset: int
    :param query: Optional text to search in the name, surname, or email.
    :type query: str | None
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :param user: The user whose contacts should be retrieved.
    :type user: User
    :return: The matching contacts.
    :rtype: list[Contact]
    """
    stmt = select(Contact).filter_by(user=user)

    if query:
        stmt = stmt.where(
            Contact.name.ilike(f"%{query}%") |
            Contact.surname.ilike(f"%{query}%") |
            Contact.email.ilike(f"%{query}%")
        )

    stmt = stmt.offset(offset).limit(limit)

    contacts = await db.execute(stmt)

    return contacts.scalars().all()


async def get_birthdays(db: AsyncSession, user: User):
    """Retrieve the user's contacts with birthdays in the next seven days.

    :param db: The asynchronous database session.
    :type db: AsyncSession
    :param user: The user whose contacts should be checked.
    :type user: User
    :return: Contacts with birthdays from today through six days from today.
    :rtype: list[Contact]
    """
    today = date.today()

    stmt = select(Contact).filter_by(user=user)
    result = await db.execute(stmt)
    contacts = result.scalars().all()

    birthdays = []

    for contact in contacts:
        for i in range(7):
            current_date = today + timedelta(days=i)

            if (
                contact.birthday.month == current_date.month
                and contact.birthday.day == current_date.day
            ):
                birthdays.append(contact)
                break

    return birthdays


async def get_contact(contact_id: int, db: AsyncSession, user: User):
    """Retrieve one contact belonging to a user.

    :param contact_id: The identifier of the contact.
    :type contact_id: int
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :param user: The user who owns the contact.
    :type user: User
    :return: The contact, or ``None`` if it does not exist for the user.
    :rtype: Contact | None
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession, user: User):
    """Create and persist a contact for a user.

    :param body: The validated contact data.
    :type body: ContactSchema
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :param user: The user who will own the new contact.
    :type user: User
    :return: The newly created contact.
    :rtype: Contact
    """
    contact = Contact(**body.model_dump(exclude_unset=True), user=user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactUpdateSchema, db: AsyncSession, user: User):
    """Update an existing contact belonging to a user.

    :param contact_id: The identifier of the contact to update.
    :type contact_id: int
    :param body: The validated replacement contact data.
    :type body: ContactUpdateSchema
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :param user: The user who owns the contact.
    :type user: User
    :return: The updated contact, or ``None`` if it was not found.
    :rtype: Contact | None
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        contact.name = body.name
        contact.surname = body.surname
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        contact.info = body.info
        contact.completed = body.completed
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession, user: User):
    """Delete a contact belonging to a user.

    :param contact_id: The identifier of the contact to delete.
    :type contact_id: int
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :param user: The user who owns the contact.
    :type user: User
    :return: The deleted contact, or ``None`` if it was not found.
    :rtype: Contact | None
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    contact = contact.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact
