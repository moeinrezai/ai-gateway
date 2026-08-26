from app.ai.providers.base import BaseAIProvider
from app.ai.providers.mock import MockProvider
from app.ai.providers.openai import OpenAIProvider
from app.ai.schemas import AIProviderType
from app.core.config import settings
from app.core.exceptions.ai import AIInvalidModelError


ALLOWED_MODELS = {
    "gpt-3.5-turbo": AIProviderType.OPENAI,
    "gpt-4": AIProviderType.OPENAI,
    "gpt-4-turbo": AIProviderType.OPENAI,
    "mock-model": AIProviderType.MOCK,
}


class AIProviderRouter:
    def __init__(self):
        self._providers: dict[AIProviderType, BaseAIProvider] = {}

    def get_provider(self, model: str) -> BaseAIProvider:
        if model not in ALLOWED_MODELS:
            raise AIInvalidModelError(model)

        provider_type = ALLOWED_MODELS[model]

        if provider_type not in self._providers:
            if provider_type == AIProviderType.OPENAI:
                self._providers[provider_type] = OpenAIProvider()
            elif provider_type == AIProviderType.MOCK:
                self._providers[provider_type] = MockProvider()

        return self._providers[provider_type]


ai_router = AIProviderRouter()