from fastapi import Cookie, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.db import get_db
from app.core.exceptions import AuthenticationError, InvalidTokenError
from app.core.security.jwt import decode_token
from app.models.user import User
from app.repositories.session import SessionRepository


async def get_current_user(
    access_token: str | None = Cookie(None, alias="access_token"),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not access_token:
        raise AuthenticationError("Not authenticated. No access token provided.")

    payload = decode_token(access_token, "access")
    session_id = payload.get("sid")
    
    if not session_id:
        raise InvalidTokenError("Invalid token payload.")

    session_repo = SessionRepository(db)
    session = await session_repo.get_active_by_id_with_user(session_id)

    if not session:
        raise InvalidTokenError("Session is invalid, expired, or revoked.")

    return session.user