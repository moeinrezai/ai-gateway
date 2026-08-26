import uuid

from app.ai.providers.base import BaseAIProvider
from app.ai.schemas import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    GenerationRequest,
    GenerationResponse,
)


class MockProvider(BaseAIProvider):
    async def chat(self, request: ChatRequest) -> ChatResponse:
        return ChatResponse(
            id=str(uuid.uuid4()),
            provider="mock",
            model=request.model,
            message=ChatMessage(
                role="assistant",
                content=f"[Mock Response] You said: {request.messages[-1].content}",
            ),
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            finish_reason="stop",
        )

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        return GenerationResponse(
            id=str(uuid.uuid4()),
            provider="mock",
            model=request.model,
            text=f"[Mock Response] You prompted: {request.prompt}",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            finish_reason="stop",
        )

    async def is_healthy(self) -> bool:
        return True
