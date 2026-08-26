from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.auth import UserAlreadyExistsError
from app.core.security.password import hash_password
from app.models.user import User
from app.repositories.role import RoleRepository
from app.repositories.user import UserRepository


class UserService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.user_repo.get_by_email(email)

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