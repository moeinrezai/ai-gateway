from fastapi import APIRouter, Depends

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.authorization import RequirePermission
from app.models.user import User
from app.schemas.user import UserRead

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserRead)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/admin-only", response_model=dict)
async def admin_only_endpoint(
    current_user: User = Depends(RequirePermission("admin:manage-users")),
):
    return {"message": f"Welcome Admin! Your email is {current_user.email}"}
