import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.auth import AuthenticationError, UserAlreadyExistsError
from app.core.security.password import hash_password, verify_password
from app.models.user import User
from app.repositories.role import RoleRepository
from app.repositories.user import UserRepository


class UserService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.user_repo.get_by_email(email)

    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        return await self.user_repo.get_by_id(user_id)

    async def create_user(self, email: str, password: str, role_name: str = "user") -> User:
        existing_user = await self.get_user_by_email(email)
        if existing_user:
            raise UserAlreadyExistsError()

        role = await self.role_repo.get_by_name(role_name)
        if not role:
            raise ValueError(f"Role '{role_name}' not found in database. Please seed the database first.")

        hashed_password = hash_password(password)
        user_data = {
            "email": email,
            "hashed_password": hashed_password,
            "role_id": role.id,
        }
        
        return await self.user_repo.create(user_data)

    async def change_password(self, user: User, old_password: str, new_password: str) -> None:
        # 1. Verify old password
        # Note: verify_password raises AuthenticationError if invalid
        verify_password(user.hashed_password, old_password)

        # 2. Hash new password
        new_hashed_password = hash_password(new_password)

        # 3. Update in DB
        user.hashed_password = new_hashed_password
        # Since we are using the same session, and object is attached, 
        # we just need to ensure it's flushed. 
        # However, our Repository pattern usually handles updates. 
        # Let's add an update method to UserRepository or handle it here.
        # For simplicity and keeping logic in Service:
        await self.user_repo.update(user)

    async def update_user(self, user_id: uuid.UUID, data: dict) -> User | None:
        return await self.user_repo.update_by_id(user_id, data)