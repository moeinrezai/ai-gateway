import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.auth import AuthenticationError, InvalidTokenError
from app.core.security.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
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

    async def register(
        self,
        email: str,
        password: str,
        ip: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[User, Session, str, str]:
        user = await self.user_service.create_user(email, password)

        ip_hash = hash_ip(ip) if ip else None

        session = await self.session_repo.create(
            {
                "user_id": user.id,
                "ip_hash": ip_hash,
                "user_agent": user_agent,
                "is_active": True,
            }
        )

        access_token = create_access_token(user.id, session.id, user.role.name)
        refresh_token = create_refresh_token(user.id, session.id)

        refresh_payload = decode_token(refresh_token, "refresh")

        await self.refresh_token_repo.create(
            {
                "session_id": session.id,
                "jti": refresh_payload["jti"],
                "expires_at": datetime.fromtimestamp(
                    refresh_payload["exp"], tz=timezone.utc
                ),
            }
        )

        return user, session, access_token, refresh_token

    async def login(
        self,
        email: str,
        password: str,
        ip: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[User, Session, str, str]:
        user = await self.user_service.get_user_by_email(email)
        if not user:
            raise AuthenticationError("Invalid email or password.")

        verify_password(user.hashed_password, password)

        ip_hash = hash_ip(ip) if ip else None

        session = await self.session_repo.create(
            {
                "user_id": user.id,
                "ip_hash": ip_hash,
                "user_agent": user_agent,
                "is_active": True,
            }
        )

        access_token = create_access_token(user.id, session.id, user.role.name)
        refresh_token = create_refresh_token(user.id, session.id)

        refresh_payload = decode_token(refresh_token, "refresh")

        await self.refresh_token_repo.create(
            {
                "session_id": session.id,
                "jti": refresh_payload["jti"],
                "expires_at": datetime.fromtimestamp(
                    refresh_payload["exp"], tz=timezone.utc
                ),
            }
        )

        return user, session, access_token, refresh_token

    async def refresh_tokens(self, refresh_token_str: str) -> tuple[str, str]:
        # 1. Decode and validate signature/expiration
        payload = decode_token(refresh_token_str, "refresh")
        jti = payload["jti"]
        session_id = payload["sid"]
        user_id = payload["sub"]

        # 2. Find token record in DB
        token_record = await self.refresh_token_repo.get_by_jti(jti)
        if not token_record:
            raise InvalidTokenError("Refresh token not found.")

        # 3. Replay Attack Detection
        if token_record.revoked_at is not None:
            await self.session_repo.revoke(session_id)
            await self.refresh_token_repo.revoke_by_session_id(session_id)
            raise InvalidTokenError("Refresh token reuse detected. Session revoked.")

        # 4. Check if session is still active
        session = await self.session_repo.get_by_id(session_id)
        if not session or not session.is_active:
            raise InvalidTokenError("Session is no longer active.")

        # 5. Rotate: Revoke the old token
        await self.refresh_token_repo.revoke(jti)

        # 6. Fetch user to get current role
        user = await self.user_service.get_user_by_id(uuid.UUID(user_id))
        if not user:
            raise InvalidTokenError("User not found.")

        # 7. Generate new tokens
        new_access_token = create_access_token(user.id, session.id, user.role.name)
        new_refresh_token = create_refresh_token(user.id, session.id)

        # 8. Save new refresh token in DB (FIXED: No hashed_token)
        new_payload = decode_token(new_refresh_token, "refresh")
        await self.refresh_token_repo.create({
            "session_id": session.id,
            "jti": new_payload["jti"],
            "expires_at": datetime.fromtimestamp(new_payload["exp"], tz=timezone.utc),
        })

        return new_access_token, new_refresh_token