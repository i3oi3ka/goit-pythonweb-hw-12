"""
Users API routes for profile and avatar management.
Uses FastAPI, SQLAlchemy async session, and Cloudinary for avatar uploads.
"""

from fastapi import APIRouter, Depends, Request, UploadFile, File, HTTPException, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

# from src.database.models import User

from src.schemas.users import User
from src.services.auth import get_current_user
from src.database.db import get_db
from src.services.upload_file import UploadFileService
from src.services.users import UserService
from src.conf.settings import settings

router = APIRouter(tags=["Users"], prefix="/users")
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/me/", response_model=User, description="No more than 10 requests per minute"
)
@limiter.limit("10/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    """
    Get the current authenticated user's profile information.
    Args:
        request (Request): FastAPI request object.
        user (User): Current authenticated user.
    Returns:
        User: The user's profile data.
    """
    return user


@router.patch("/avatar", response_model=User)
async def update_avatar_user(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """
    Update the current user's avatar image using Cloudinary.
    Args:
        file (UploadFile): Uploaded avatar image file.
        user (User): Current authenticated user.
        db (AsyncSession): SQLAlchemy async session.
    Returns:
        User: The updated user profile with new avatar URL.
    Raises:
        HTTPException: If Cloudinary authentication fails.
    """
    try:
        avatar_url = UploadFileService(
            settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
        ).upload_file(file, user.username)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Cloudinary authentication failed",
        ) from exc

    user_service = UserService(db)
    db_user = await user_service.update_avatar_url(user.email, avatar_url)

    return User.model_validate(db_user)
