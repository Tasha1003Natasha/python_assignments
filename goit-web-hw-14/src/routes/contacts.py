from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.repository import contacts as repositories_contacts
from src.schemas.contact import ContactSchema, ContactUpdateSchema, ContactResponse
from src.services.roles import RoleAccess
from src.entity.models import User, Role
from src.services.auth import auth_service
from src.services.rate_limiter import RateLimiter

router = APIRouter(prefix='/contacts', tags=['contacts'])

access_to_route_all = RoleAccess([Role.admin, Role.moderator])


@router.get("/", response_model=list[ContactResponse], dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def get_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                       query: str | None = Query(None),
                       db: AsyncSession = Depends(get_db),
                       user: User = Depends(auth_service.get_current_user)):
    """Return the current user's contacts with pagination and optional search.

    :param limit: Maximum number of contacts to return.
    :type limit: int
    :param offset: Number of contacts to skip.
    :type offset: int
    :param query: Optional search text for name, surname, or email.
    :type query: str | None
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :param user: The authenticated user.
    :type user: User
    :return: A list of contacts owned by the user.
    :rtype: list[ContactResponse]
    """
    contacts = await repositories_contacts.get_contacts(limit, offset, query, db,  user)
    return contacts


@router.get("/birthdays", response_model=list[ContactResponse],
            dependencies=[
    Depends(access_to_route_all),
    Depends(RateLimiter(times=5, seconds=60)),
],
)
async def get_birthdays(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)
):
    """Return contacts with birthdays in the next seven days.

    :param db: The asynchronous database session.
    :type db: AsyncSession
    :param user: The authenticated user.
    :type user: User
    :return: Contacts whose birthday is today or within the next six days.
    :rtype: list[ContactResponse]
    """
    contacts = await repositories_contacts.get_birthdays(db, user)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def get_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),  user: User = Depends(auth_service.get_current_user)):
    """Return one contact by identifier.

    :param contact_id: The identifier of the contact.
    :type contact_id: int
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :param user: The authenticated user.
    :type user: User
    :return: The requested contact.
    :rtype: ContactResponse
    :raises HTTPException: If the contact does not exist for the user.
    """
    contact = await repositories_contacts.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db),  user: User = Depends(auth_service.get_current_user)):
    """Create a new contact for the authenticated user.

    :param body: The validated contact data.
    :type body: ContactSchema
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :param user: The authenticated user.
    :type user: User
    :return: The created contact.
    :rtype: ContactResponse
    """
    contact = await repositories_contacts.create_contact(body, db, user)
    return contact


@router.put("/{contact_id}")
async def update_contact(body: ContactUpdateSchema, contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),  user: User = Depends(auth_service.get_current_user)):
    """Update a contact owned by the authenticated user.

    :param body: The validated contact data.
    :type body: ContactUpdateSchema
    :param contact_id: The identifier of the contact to update.
    :type contact_id: int
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :param user: The authenticated user.
    :type user: User
    :return: The updated contact.
    :rtype: ContactResponse
    :raises HTTPException: If the contact does not exist for the user.
    """
    contact = await repositories_contacts.update_contact(contact_id, body, db, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def delete_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),  user: User = Depends(auth_service.get_current_user)):
    """Delete a contact owned by the authenticated user.

    :param contact_id: The identifier of the contact to delete.
    :type contact_id: int
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :param user: The authenticated user.
    :type user: User
    :return: The deleted contact object, if it existed.
    :rtype: ContactResponse | None
    """
    contact = await repositories_contacts.delete_contact(contact_id, db, user)
    return contact
