from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.auth import AuthenticationError
from app.core.security.jwt import create_access_token, create_refresh_token, decode_token
from app.core.security.password import verify_password
from app.core.security.utils import hash_ip
from app.models.session import Session
from app.models.user import User
from app.repositories.refresh_token import RefreshTokenRepository
from app.repositories.session import SessionRepository
from app.services.user import UserService


class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_service = UserService(db)
        self.session_repo = SessionRepository(db)
        self.refresh_token_repo = RefreshTokenRepository(db)

    async def register(self, email: str, password: str) -> User:
        return await self.user_service.create_user(email, password)

    async def login(
        self, 
        email: str, 
        password: str, 
        ip: str | None = None, 
        user_agent: str | None = None
    ) -> tuple[User, Session, str, str]:
        user = await self.user_service.get_user_by_email(email)
        if not user:
            raise AuthenticationError("Invalid email or password.")

        verify_password(user.hashed_password, password)

        ip_hash = hash_ip(ip) if ip else None
        
        session = await self.session_repo.create({
            "user_id": user.id,
            "ip_hash": ip_hash,
            "user_agent": user_agent,
            "is_active": True,
        })

        access_token = create_access_token(user.id, session.id, user.role.name)
        refresh_token = create_refresh_token(user.id, session.id)

        refresh_payload = decode_token(refresh_token, "refresh")
        
        await self.refresh_token_repo.create({
            "session_id": session.id,
            "jti": refresh_payload["jti"],
            "hashed_token": refresh_token,
            "expires_at": datetime.fromtimestamp(refresh_payload["exp"], tz=timezone.utc),
        })

        return user, session, access_token, refresh_token