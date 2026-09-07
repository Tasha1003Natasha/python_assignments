from fastapi import Request, Depends, HTTPException, status

from src.entity.models import Role, User
from src.services.auth import auth_service


class RoleAccess:
    """FastAPI dependency that restricts access by user role."""

    def __init__(self, allowed_roles: list[Role]):
        """Store the roles allowed to access a route.

        :param allowed_roles: Roles that are allowed to use the endpoint.
        :type allowed_roles: list[Role]
        """
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, user: User = Depends(auth_service.get_current_user)):
        """Validate that the current user has one of the allowed roles.

        :param request: The incoming FastAPI request.
        :type request: Request
        :param user: The authenticated user.
        :type user: User
        :raises HTTPException: If the user's role is not allowed.
        """
        print(user.role, self.allowed_roles)
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="FORBIDDEN"
            )
