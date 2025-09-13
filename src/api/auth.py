from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Security,
    BackgroundTasks,
    Request,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas.users import User, UserCreate, Token, RequestEmail
from src.services.users import UserService
from src.services.auth import Hash, create_access_token, get_email_from_token
from src.services.email import send_mail

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/sign_up/", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
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
        send_mail, new_user.email, new_user.username, request.base_url
    )
    return new_user


@router.post("/login/", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
) -> Token:
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

    access_token = await create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Your email already confirmed"}
    await user_service.confirmed_email(email)
    return {"message": "Email success confirmed"}


@router.get("/request_email/")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
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
            send_mail, user.email, user.username, request.base_url
        )
    return {"message": "Check your email post"}
