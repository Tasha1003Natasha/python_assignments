from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks, Request, Response
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.repository import users as repositories_users
from src.schemas.user import UserSchema, TokenSchema, UserResponse, RequestEmail, ResetPassword
from src.services.auth import auth_service
from src.services.email import send_email, send_password_reset_email

router = APIRouter(prefix='/auth', tags=['auth'])
get_refresh_token = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED,)
async def signup(body: UserSchema, bt: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)):
    """Register a new user and send an email confirmation message.

    :param body: The registration data with username, email, and password.
    :type body: UserSchema
    :param bt: FastAPI background task manager used to send confirmation email.
    :type bt: BackgroundTasks
    :param request: The incoming request, used to build the application base URL.
    :type request: Request
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :return: The newly created user.
    :rtype: UserResponse
    :raises HTTPException: If an account with the same email already exists.
    """
    exist_user = await repositories_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repositories_users.create_user(body, db)
    bt.add_task(send_email, new_user.email,
                new_user.username, str(request.base_url))
    return new_user


@router.post("/login",  response_model=TokenSchema)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """Authenticate a confirmed user and issue JWT tokens.

    :param body: OAuth2 form data containing the user's email and password.
    :type body: OAuth2PasswordRequestForm
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :return: Access token, refresh token, and token type.
    :rtype: TokenSchema
    :raises HTTPException: If the email, password, or confirmation status is invalid.
    """
    user = await repositories_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repositories_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token',  response_model=TokenSchema)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(get_refresh_token),
                        db: AsyncSession = Depends(get_db)):
    """Refresh the user's access and refresh tokens.

    :param credentials: Bearer credentials containing the current refresh token.
    :type credentials: HTTPAuthorizationCredentials
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :return: A new access token, refresh token, and token type.
    :rtype: TokenSchema
    :raises HTTPException: If the refresh token is invalid or does not match the stored token.
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repositories_users.update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repositories_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """Confirm a user's email address using a verification token.

    :param token: JWT token generated for email confirmation.
    :type token: str
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :return: A message describing the confirmation result.
    :rtype: dict[str, str]
    :raises HTTPException: If the token is valid but no user exists for its email.
    """
    email = await auth_service.get_email_from_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repositories_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: AsyncSession = Depends(get_db)):
    """Request a new email confirmation message.

    :param body: Request body containing the user's email address.
    :type body: RequestEmail
    :param background_tasks: FastAPI background task manager used to send email.
    :type background_tasks: BackgroundTasks
    :param request: The incoming request, used to build the application base URL.
    :type request: Request
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :return: A generic confirmation email response message.
    :rtype: dict[str, str]
    """
    user = await repositories_users.get_user_by_email(body.email, db)

    if user is None:
        return {"message": "Check your email for confirmation."}

    if user.confirmed:
        return {"message": "Your email is already confirmed"}

    background_tasks.add_task(
        send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}


@router.post("/request_password_reset")
async def request_password_reset(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Request password reset instructions for an email address.

    The response is intentionally generic so that unknown email addresses are
    not revealed to clients.

    :param body: Request body containing the user's email address.
    :type body: RequestEmail
    :param background_tasks: FastAPI background task manager used to send email.
    :type background_tasks: BackgroundTasks
    :param request: The incoming request, used to build the application base URL.
    :type request: Request
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :return: A generic password reset response message.
    :rtype: dict[str, str]
    """
    user = await repositories_users.get_user_by_email(body.email, db)

    if user:
        background_tasks.add_task(
            send_password_reset_email,
            user.email,
            user.username,
            str(request.base_url)
        )

    return {"message": "If this email exists, password reset instructions were sent."}


@router.post("/reset_password")
async def reset_password(
    body: ResetPassword,
    db: AsyncSession = Depends(get_db)
):
    """Reset a user's password using a password reset token.

    :param body: Request body containing a reset token and the new password.
    :type body: ResetPassword
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :return: A message confirming that the password was changed.
    :rtype: dict[str, str]
    :raises HTTPException: If the token points to a user that does not exist.
    """
    email = await auth_service.get_email_from_password_reset_token(body.token)
    user = await repositories_users.get_user_by_email(email, db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )

    new_password_hash = auth_service.get_password_hash(body.password)
    await repositories_users.update_password(user, new_password_hash, db)

    return {"message": "Password successfully changed"}
