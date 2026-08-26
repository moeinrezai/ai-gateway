import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.session import Session
from app.repositories.base import BaseRepository


class SessionRepository(BaseRepository[Session]):
    def __init__(self, db: AsyncSession):
        super().__init__(Session, db)

    async def get_active_by_user_id(self, user_id: uuid.UUID) -> list[Session]:
        result = await self.db.execute(
            select(Session).where(Session.user_id == user_id, Session.is_active == True)
        )
        return result.scalars().all()

    async def get_active_by_id_with_user(self, session_id: uuid.UUID) -> Session | None:
        result = await self.db.execute(
            select(Session)
            .options(joinedload(Session.user))
            .where(Session.id == session_id, Session.is_active == True)
        )
        return result.scalars().first()

    async def revoke(self, session_id: uuid.UUID) -> None:
        await self.db.execute(
            update(Session)
            .where(Session.id == session_id)
            .values(is_active=False, revoked_at=datetime.now(timezone.utc))
        )
        await self.db.flush()
