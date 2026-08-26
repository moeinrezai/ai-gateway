from fastapi import APIRouter, Depends
from uuid import UUID

from app.api.dependencies.auth import get_current_session
from app.api.dependencies.services import get_session_service
from app.models.session import Session
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.session import SessionRead
from app.services.session import SessionService

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.get("/", response_model=list[SessionRead])
async def get_active_sessions(
    session_data: tuple[User, Session] = Depends(get_current_session),
    session_service: SessionService = Depends(get_session_service),
):
    user, current_session = session_data
    return await session_service.get_user_sessions(user.id, current_session.id)


@router.delete("/{session_id}", response_model=SuccessResponse)
async def revoke_session(
    session_id: UUID,
    session_data: tuple[User, Session] = Depends(get_current_session),
    session_service: SessionService = Depends(get_session_service),
):
    user, _ = session_data
    await session_service.revoke_session(user.id, session_id)
    return SuccessResponse(message="Session revoked successfully.")


@router.delete("/", response_model=SuccessResponse)
async def revoke_all_sessions(
    session_data: tuple[User, Session] = Depends(get_current_session),
    session_service: SessionService = Depends(get_session_service),
):
    user, _ = session_data
    await session_service.revoke_all_sessions(user.id)
    return SuccessResponse(message="All sessions revoked successfully.")