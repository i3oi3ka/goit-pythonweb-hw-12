"""
Authentication API routes for user registration, login, email confirmation, and email request.
Uses FastAPI and SQLAlchemy async session.
"""

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    BackgroundTasks,
    Request,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas.users import (
    User,
    UserCreate,
    Token,
    TokenRefresh,
    RequestEmail,
    ResetPasswordRequest,
)
from src.services.users import UserService
from src.services.auth import (
    Hash,
    create_token_pair,
    get_email_from_token,
    get_username_from_token_refresh,
)
from src.services.email import send_mail

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/sign_up/", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Register a new user and send a confirmation email.
    Args:
        user_data (UserCreate): Data for the new user.
        background_tasks (BackgroundTasks): FastAPI background tasks manager.
        request (Request): FastAPI request object.
        db (AsyncSession): SQLAlchemy async session.
    Returns:
        User: The created user object.
    Raises:
        HTTPException: If username or email already exists.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_username(user_data.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with username: {user_data.username} already exists",
        )

    if await user_service.get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email: {user_data.email} already exists",
        )

    user_data.password = await Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)
    background_tasks.add_task(
        send_mail, new_user.email, new_user.username, str(request.base_url)
    )
    return User.model_validate(new_user)


@router.post("/login/", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
) -> Token:
    """
    Authenticate user and return JWT access token.
    Args:
        form_data (OAuth2PasswordRequestForm): Login form data.
        db (AsyncSession): SQLAlchemy async session.
    Returns:
        Token: JWT access token and token type.
    Raises:
        HTTPException: If login credentials are incorrect or email not confirmed.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)
    if not user or not await Hash().verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email address not confirmed",
        )

    return await create_token_pair(data={"sub": user.username})


@router.post("/refresh_token/")
async def refresh_token(refresh_token: TokenRefresh):
    """
    Refresh access token using a refresh token.
    Args:
        refresh_token (str): Refresh token from request.
    Returns:
        Token: New access token and refresh token.
    Raises:
        HTTPException: If refresh token is invalid or expired.
    """

    username = await get_username_from_token_refresh(refresh_token.refresh_token)
    return await create_token_pair(data={"sub": username})


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Confirm user's email using a token.
    Args:
        token (str): Email confirmation token.
        db (AsyncSession): SQLAlchemy async session.
    Returns:
        dict: Confirmation message.
    Raises:
        HTTPException: If verification fails or user not found.
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None or email is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Your email already confirmed"}
    await user_service.confirmed_email(email)
    return {"message": "Email success confirmed"}


@router.post("/request_email/")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Request a confirmation email to be sent to the user.
    Args:
        body (RequestEmail): Email request data.
        background_tasks (BackgroundTasks): FastAPI background tasks manager.
        request (Request): FastAPI request object.
        db (AsyncSession): SQLAlchemy async session.
    Returns:
        dict: Message about email confirmation status.
    Raises:
        HTTPException: If user not found.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email not found, please check entered email.",
        )

    if user.confirmed:
        return {"message": "Your email already confirmed"}

    if user:
        background_tasks.add_task(
            send_mail, user.email, user.username, str(request.base_url)
        )
    return {"message": "Check your email post"}


@router.post("/request_reset_password/")
async def request_reset_password(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Request a password reset email to be sent to the user.
    Args:
        email (str): User's email address.
        background_tasks (BackgroundTasks): FastAPI background tasks manager.
        request (Request): FastAPI request object.
        db (AsyncSession): SQLAlchemy async session.
    Returns:
        dict: Message about password reset email status.
    Raises:
        HTTPException: If user not found.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email not found, please check entered email.",
        )

    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address not confirmed",
        )
    background_tasks.add_task(
        send_mail,
        user.email,
        user.username,
        str(request.base_url),
        template="reset_password_email.html",
        subject="Reset your password",
    )
    return {"message": "Check your email post"}


@router.post("/reset_password/", response_model=dict)
async def reset_password(
    body: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Resets the user's password using a provided token and new password.
    Args:
        token (str): The password reset token.
        new_password (str): The new password to set.
        request (Request): FastAPI request object.
        db (AsyncSession): SQLAlchemy async session.
    Returns:
        dict: A message indicating the password was successfully saved.
    Raises:
        HTTPException: If verification fails or user not found.
    """
    email = await get_email_from_token(body.token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None or email is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    hashed_new_password = await Hash().get_password_hash(body.new_password)
    await user_service.update_user_password(user, hashed_new_password)
    return {"message": "password successfully saved"}
