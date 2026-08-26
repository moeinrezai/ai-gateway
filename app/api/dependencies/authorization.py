from fastapi import Depends
from app.api.dependencies.auth import get_current_user
from app.core.exceptions import PermissionDeniedError
from app.models.user import User


class RequirePermission:
    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    async def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if not current_user.role:
            raise PermissionDeniedError("User role is not assigned.")

        # Superadmin bypass (if we implement this role in the future)
        if current_user.role.name == "superadmin":
            return current_user
        user_permissions = {perm.codename for perm in current_user.role.permissions}

        if self.required_permission not in user_permissions:
            raise PermissionDeniedError(
                message=f"Missing required permission: {self.required_permission}"
            )

        return current_user
