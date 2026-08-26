from abc import ABC, abstractmethod

from app.ai.schemas import (
    ChatRequest,
    ChatResponse,
    GenerationRequest,
    GenerationResponse,
)


class BaseAIProvider(ABC):
    @abstractmethod
    async def chat(self, request: ChatRequest) -> ChatResponse:
        pass

    @abstractmethod
    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        pass

    @abstractmethod
    async def is_healthy(self) -> bool:
        pass
