from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AIProviderType(str, Enum):
    OPENAI = "openai"
    MOCK = "mock"


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(system|user|assistant)$")
    content: str = Field(..., min_length=1, max_length=10000)


class ChatRequest(BaseModel):
    model: str = Field(..., min_length=1, max_length=100)
    messages: list[ChatMessage] = Field(..., min_length=1, max_length=50)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, ge=1, le=4000)


class ChatResponse(BaseModel):
    id: str
    provider: str
    model: str
    message: ChatMessage
    usage: dict[str, int]
    finish_reason: str


class GenerationRequest(BaseModel):
    model: str = Field(..., min_length=1, max_length=100)
    prompt: str = Field(..., min_length=1, max_length=10000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, ge=1, le=4000)


class GenerationResponse(BaseModel):
    id: str
    provider: str
    model: str
    text: str
    usage: dict[str, int]
    finish_reason: str