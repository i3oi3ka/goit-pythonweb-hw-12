from typing import Any
from fastapi import Depends, HTTPException, Request, status

from src.database.models import Role, User
from src.services.auth import get_current_user


class RoleAccess:
    def __init__(self, allowed_roles: list[Role]):
        self.allowed_roles = allowed_roles

    def __call__(
        self, request: Request, current_user: User = Depends(get_current_user)
    ) -> User:
        if current_user.roles not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Operation forbidden"
            )
        return current_user
