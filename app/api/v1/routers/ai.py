from fastapi import APIRouter, Depends

from app.ai.schemas import (
    ChatRequest,
    ChatResponse,
    GenerationRequest,
    GenerationResponse,
)
from app.api.dependencies.authorization import RequirePermission
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.rate_limit import AIRateLimiter
from app.api.dependencies.services import get_ai_service
from app.models.user import User
from app.services.ai import AIService

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    _: None = Depends(RequirePermission("ai:chat")),
    __: None = Depends(AIRateLimiter()),
    ai_service: AIService = Depends(get_ai_service),
):
    return await ai_service.chat(payload)


@router.post("/generate", response_model=GenerationResponse)
async def generate(
    payload: GenerationRequest,
    current_user: User = Depends(get_current_user),
    _: None = Depends(RequirePermission("ai:chat")),
    __: None = Depends(AIRateLimiter()),
    ai_service: AIService = Depends(get_ai_service),
):
    return await ai_service.generate(payload)