from fastapi import APIRouter, Depends, Request, UploadFile, File, HTTPException, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

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
    return user


@router.patch("/avatar", response_model=User)
async def update_avatar_user(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        avatar_url = UploadFileService(
            settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
        ).upload_file(file, user.username)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Cloudinary authentication failed",
        )

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user
