import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import PermissionDeniedError
from app.repositories.refresh_token import RefreshTokenRepository
from app.repositories.session import SessionRepository


class SessionService:
    def __init__(self, db: AsyncSession):
        self.session_repo = SessionRepository(db)
        self.token_repo = RefreshTokenRepository(db)

    async def get_user_sessions(self, user_id: uuid.UUID, current_session_id: uuid.UUID) -> list[dict]:
        sessions = await self.session_repo.get_active_by_user_id(user_id)
        result = []
        for s in sessions:
            result.append({
                "id": s.id,
                "user_agent": s.user_agent,
                "ip_hash": s.ip_hash,
                "created_at": s.created_at,
                "updated_at": s.updated_at,
                "is_active": s.is_active,
                "is_current": s.id == current_session_id,
            })
        return result

    async def revoke_session(self, user_id: uuid.UUID, session_id: uuid.UUID) -> None:
        session = await self.session_repo.get_by_id(session_id)
        if not session or session.user_id != user_id:
            raise PermissionDeniedError("Session not found or access denied.")

        await self.session_repo.revoke(session_id)
        await self.token_repo.revoke_by_session_id(session_id)

    async def revoke_all_sessions(self, user_id: uuid.UUID) -> None:
        sessions = await self.session_repo.get_active_by_user_id(user_id)
        for session in sessions:
            await self.session_repo.revoke(session.id)
            await self.token_repo.revoke_by_session_id(session.id)