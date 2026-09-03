from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.database.db import get_db
from src.entity.models import User
from src.schemas.user import UserSchema


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """Retrieve a user by email address.

    :param email: The email address to search for.
    :type email: str
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :return: The matching user, or ``None`` if no user was found.
    :rtype: User | None
    """
    stmt = select(User).filter_by(email=email)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    return user


async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)):
    """Create and persist a user with a Gravatar avatar when available.

    :param body: The validated user registration data.
    :type body: UserSchema
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :return: The newly created user.
    :rtype: User
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as err:
        print(err)

    new_user = User(**body.model_dump(),  avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession):
    """Update or clear a user's refresh token.

    :param user: The user whose token should be updated.
    :type user: User
    :param token: The new refresh token, or ``None`` to clear it.
    :type token: str | None
    :param db: The asynchronous database session.
    :type db: AsyncSession
    """
    user.refresh_token = token
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession) -> None:
    """Mark the user with the given email address as confirmed.

    :param email: The email address of the user to confirm.
    :type email: str
    :param db: The asynchronous database session.
    :type db: AsyncSession
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()


async def update_avatar_url(email: str, url: str | None, db: AsyncSession) -> User:
    """Update a user's avatar URL.

    :param email: The email address of the user to update.
    :type email: str
    :param url: The new avatar URL, or ``None`` to remove it.
    :type url: str | None
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :return: The updated user.
    :rtype: User
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user


async def update_password(user: User, password: str, db: AsyncSession):
    """Update a user's password and invalidate the refresh token.

    :param user: The user whose password should be updated.
    :type user: User
    :param password: The new password hash.
    :type password: str
    :param db: The asynchronous database session.
    :type db: AsyncSession
    """
    user.password = password
    user.refresh_token = None
    await db.commit()