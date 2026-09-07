import pickle
from datetime import datetime, timedelta, timezone
from typing import Optional

import redis
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from jose import JWTError, jwt

from src.database.db import get_db
from src.conf.config import config
from src.repository import users as repository_users


class Auth:
    """Service for password hashing, JWT handling, and current-user loading."""

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    SECRET_KEY = config.SECRET_KEY
    ALGORITHM = config.ALGORITHM

    cache = redis.Redis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=0,
        password=config.REDIS_PASSWORD,
    )

    def verify_password(self, plain_password, hashed_password):
        """Verify a plain password against a stored password hash.

        :param plain_password: The password provided by the user.
        :type plain_password: str
        :param hashed_password: The stored hashed password.
        :type hashed_password: str
        :return: ``True`` if the password matches the hash, otherwise ``False``.
        :rtype: bool
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """Hash a plain text password.

        :param password: The password to hash.
        :type password: str
        :return: The hashed password.
        :rtype: str
        """
        return self.pwd_context.hash(password)

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

    # define a function to generate a new access token
    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """Create a JWT access token.

        :param data: Payload data to encode into the token.
        :type data: dict
        :param expires_delta: Optional lifetime of the token in seconds.
        :type expires_delta: float | None
        :return: Encoded access token.
        :rtype: str
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + \
                timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update(
            {"iat": datetime.now(timezone.utc), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    # define a function to generate a new refresh token
    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """Create a JWT refresh token.

        :param data: Payload data to encode into the token.
        :type data: dict
        :param expires_delta: Optional lifetime of the token in seconds.
        :type expires_delta: float | None
        :return: Encoded refresh token.
        :rtype: str
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + \
                timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=7)
        to_encode.update(
            {"iat": datetime.now(timezone.utc), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """Decode and validate a refresh token.

        :param refresh_token: The refresh token to decode.
        :type refresh_token: str
        :return: The email address stored in the token subject.
        :rtype: str
        :raises HTTPException: If the token is invalid or has the wrong scope.
        """
        try:
            payload = jwt.decode(
                refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
        """Resolve the authenticated user from an access token.

        The user is loaded from Redis cache when possible and from the database
        otherwise.

        :param token: Bearer access token from the Authorization header.
        :type token: str
        :param db: The asynchronous database session.
        :type db: AsyncSession
        :return: The authenticated user.
        :rtype: User
        :raises HTTPException: If the token is invalid or the user does not exist.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY,
                                 algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user_hash = str(email)

        user = self.cache.get(user_hash)

        if user is None:
            print("User from database")
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.cache.set(user_hash, pickle.dumps(user))
            self.cache.expire(user_hash, 300)
        else:
            print("User from cache")
            user = pickle.loads(user)
        return user

    def create_email_token(self, data: dict):
        """Create a JWT token for email verification.

        :param data: Payload data to encode into the token.
        :type data: dict
        :return: Encoded email verification token.
        :rtype: str
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=1)
        to_encode.update({"iat": datetime.now(timezone.utc),
                         "exp": expire, "scope": "email_verification"})
        token = jwt.encode(to_encode, self.SECRET_KEY,
                           algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """Extract an email address from an email verification token.

        :param token: Email verification JWT token.
        :type token: str
        :return: The email address stored in the token subject.
        :rtype: str
        :raises HTTPException: If the token is invalid or has the wrong scope.
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY,
                                 algorithms=[self.ALGORITHM])
            if payload.get("scope") != "email_verification":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token scope"
                )

            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid token for email verification",
            )

    def create_password_reset_token(self, data: dict):
        """Create a JWT token for password reset.

        :param data: Payload data to encode into the token.
        :type data: dict
        :return: Encoded password reset token.
        :rtype: str
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
        to_encode.update({
            "iat": datetime.now(timezone.utc),
            "exp": expire,
            "scope": "password_reset"
        })
        token = jwt.encode(to_encode, self.SECRET_KEY,
                           algorithm=self.ALGORITHM)
        return token

    async def get_email_from_password_reset_token(self, token: str):
        """Extract an email address from a password reset token.

        :param token: Password reset JWT token.
        :type token: str
        :return: The email address stored in the token subject.
        :rtype: str
        :raises HTTPException: If the token is invalid or has the wrong scope.
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY,
                                 algorithms=[self.ALGORITHM])
            if payload.get("scope") != "password_reset":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token scope"
                )
            return payload["sub"]
        except JWTError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid token for password reset",
            )


auth_service = Auth()
