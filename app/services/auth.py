import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions.auth import AuthenticationError, InvalidTokenError
from app.core.security.csrf import generate_csrf_token
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

    async def register(
        self, 
        email: str, 
        password: str,
        ip: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[User, Session, str, str, str]:
        user = await self.user_service.create_user(email, password)
        
        ip_hash = hash_ip(ip) if ip else None
        
        session = await self.session_repo.create({
            "user_id": user.id,
            "ip_hash": ip_hash,
            "user_agent": user_agent,
            "is_active": True,
        })

       
        csrf_token = generate_csrf_token()

        access_token = create_access_token(user.id, session.id, user.role.name, csrf_token)
        refresh_token = create_refresh_token(user.id, session.id)

        refresh_payload = decode_token(refresh_token, "refresh")
        
        await self.refresh_token_repo.create({
            "session_id": session.id,
            "jti": refresh_payload["jti"],
            "expires_at": datetime.fromtimestamp(refresh_payload["exp"], tz=timezone.utc),
        })

        return user, session, access_token, refresh_token, csrf_token

    async def login(
        self, 
        email: str, 
        password: str, 
        ip: str | None = None, 
        user_agent: str | None = None
    ) -> tuple[User, Session, str, str, str]:
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

       
        csrf_token = generate_csrf_token()

        access_token = create_access_token(user.id, session.id, user.role.name, csrf_token)
        refresh_token = create_refresh_token(user.id, session.id)

        refresh_payload = decode_token(refresh_token, "refresh")
        
        await self.refresh_token_repo.create({
            "session_id": session.id,
            "jti": refresh_payload["jti"],
            "expires_at": datetime.fromtimestamp(refresh_payload["exp"], tz=timezone.utc),
        })

        return user, session, access_token, refresh_token, csrf_token

    async def refresh_tokens(self, refresh_token_str: str) -> tuple[str, str, str]:
      
        payload = decode_token(refresh_token_str, "refresh")
        jti = payload["jti"]
        session_id = payload["sid"]
        user_id = payload["sub"]

       
        token_record = await self.refresh_token_repo.get_by_jti(jti)
        if not token_record:
            raise InvalidTokenError("Refresh token not found.")

       
        if token_record.revoked_at is not None:
            await self.session_repo.revoke(session_id)
            await self.refresh_token_repo.revoke_by_session_id(session_id)
            raise InvalidTokenError("Refresh token reuse detected. Session revoked.")

   
        session = await self.session_repo.get_by_id(session_id)
        if not session or not session.is_active:
            raise InvalidTokenError("Session is no longer active.")

        await self.refresh_token_repo.revoke(jti)

      
        user = await self.user_service.get_user_by_id(uuid.UUID(user_id))
        if not user:
            raise InvalidTokenError("User not found.")

     
        new_csrf_token = generate_csrf_token()

       
        new_access_token = create_access_token(user.id, session.id, user.role.name, new_csrf_token)
        new_refresh_token = create_refresh_token(user.id, session.id)

 
        new_payload = decode_token(new_refresh_token, "refresh")
        await self.refresh_token_repo.create({
            "session_id": session.id,
            "jti": new_payload["jti"],
            "expires_at": datetime.fromtimestamp(new_payload["exp"], tz=timezone.utc),
        })

        return new_access_token, new_refresh_token, new_csrf_token