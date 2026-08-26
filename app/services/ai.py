from structlog import get_logger

from app.ai.router import ai_router
from app.ai.schemas import (
    ChatRequest,
    ChatResponse,
    GenerationRequest,
    GenerationResponse,
)
from app.core.exceptions.ai import AIPromptTooLargeError

logger = get_logger(__name__)

MAX_PROMPT_TOKENS = 4000


class AIService:
    def __init__(self):
        self.provider_router = ai_router

    async def chat(self, request: ChatRequest) -> ChatResponse:
        provider = self.provider_router.get_provider(request.model)

        logger.info(
            "ai_chat_request",
            provider=provider.__class__.__name__,
            model=request.model,
            messages_count=len(request.messages),
        )

        response = await provider.chat(request)

        logger.info(
            "ai_chat_response",
            provider=response.provider,
            model=response.model,
            usage=response.usage,
        )

        return response

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        provider = self.provider_router.get_provider(request.model)

        estimated_tokens = len(request.prompt.split()) * 1.3
        if estimated_tokens > MAX_PROMPT_TOKENS:
            raise AIPromptTooLargeError(MAX_PROMPT_TOKENS)

        logger.info(
            "ai_generation_request",
            provider=provider.__class__.__name__,
            model=request.model,
            prompt_length=len(request.prompt),
        )

        response = await provider.generate(request)

        logger.info(
            "ai_generation_response",
            provider=response.provider,
            model=response.model,
            usage=response.usage,
        )

        return response
