from typing import Any
from fastapi import Depends, HTTPException, Request, status

from src.database.models import Role, User
from src.services.auth import get_current_user


class RoleAccess:
    """Decorator to enforce role-based access control.

    Args:
        allowed_roles (list[Role]): List of roles permitted to access the endpoint.
    Usage:
        @router.get("/admin-only", dependencies=[Depends(RoleAccess([Role.admin]))])
        async def admin_only_endpoint():
            return {"message": "This is an admin-only endpoint."}

    """

    def __init__(self, allowed_roles: list[Role]):
        self.allowed_roles = allowed_roles

    def __call__(
        self, request: Request, current_user: User = Depends(get_current_user)
    ) -> User:
        """
        Enforce role-based access control.

        Args:
            request (Request): The request object.
            current_user (User, optional): The current user. Defaults to Depends(get_current_user).

        Raises:
            HTTPException: If the current user's role is not allowed.

        Returns:
            User: The current user.
        """
        if current_user.roles not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Operation forbidden"
            )
        return current_user
