import uuid

import httpx

from app.ai.providers.base import BaseAIProvider
from app.ai.schemas import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    GenerationRequest,
    GenerationResponse,
)
from app.core.config import settings
from app.core.exceptions.ai import (
    AIInvalidModelError,
    AIProviderAuthenticationError,
    AIProviderTimeoutError,
    AIProviderUnavailableError,
)


class OpenAIProvider(BaseAIProvider):
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY.get_secret_value()
        self.base_url = settings.OPENAI_BASE_URL
        self.timeout = settings.AI_REQUEST_TIMEOUT
        self.default_model = settings.AI_DEFAULT_MODEL

        if not self.api_key:
            raise AIProviderAuthenticationError(
                "openai", "OpenAI API key is not configured."
            )

    def _get_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def chat(self, request: ChatRequest) -> ChatResponse:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._get_headers(),
                    json={
                        "model": request.model,
                        "messages": [
                            {"role": msg.role, "content": msg.content}
                            for msg in request.messages
                        ],
                        "temperature": request.temperature,
                        "max_tokens": request.max_tokens,
                    },
                )

                if response.status_code == 401:
                    raise AIProviderAuthenticationError("openai")
                elif response.status_code == 404:
                    raise AIInvalidModelError(request.model)
                elif response.status_code >= 500:
                    raise AIProviderUnavailableError("openai")
                elif response.status_code != 200:
                    raise AIProviderUnavailableError(
                        "openai", f"Unexpected status code: {response.status_code}"
                    )

                data = response.json()
                choice = data["choices"][0]

                return ChatResponse(
                    id=data.get("id", str(uuid.uuid4())),
                    provider="openai",
                    model=data["model"],
                    message=ChatMessage(
                        role=choice["message"]["role"],
                        content=choice["message"]["content"],
                    ),
                    usage=data.get("usage", {}),
                    finish_reason=choice.get("finish_reason", "stop"),
                )

        except httpx.TimeoutException:
            raise AIProviderTimeoutError("openai")
        except httpx.ConnectError:
            raise AIProviderUnavailableError("openai", "Connection failed")

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/completions",
                    headers=self._get_headers(),
                    json={
                        "model": request.model,
                        "prompt": request.prompt,
                        "temperature": request.temperature,
                        "max_tokens": request.max_tokens,
                    },
                )

                if response.status_code == 401:
                    raise AIProviderAuthenticationError("openai")
                elif response.status_code == 404:
                    raise AIInvalidModelError(request.model)
                elif response.status_code >= 500:
                    raise AIProviderUnavailableError("openai")
                elif response.status_code != 200:
                    raise AIProviderUnavailableError(
                        "openai", f"Unexpected status code: {response.status_code}"
                    )

                data = response.json()
                choice = data["choices"][0]

                return GenerationResponse(
                    id=data.get("id", str(uuid.uuid4())),
                    provider="openai",
                    model=data["model"],
                    text=choice["text"].strip(),
                    usage=data.get("usage", {}),
                    finish_reason=choice.get("finish_reason", "stop"),
                )

        except httpx.TimeoutException:
            raise AIProviderTimeoutError("openai")
        except httpx.ConnectError:
            raise AIProviderUnavailableError("openai", "Connection failed")

    async def is_healthy(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=self._get_headers(),
                )
                return response.status_code == 200
        except Exception:
            return False
