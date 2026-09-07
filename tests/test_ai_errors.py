import pytest
from httpx import AsyncClient

from app.core.config.settings import settings


@pytest.mark.asyncio
async def test_ai_chat_invalid_model(authenticated_client: AsyncClient):
    payload = {
        "model": "invalid-model-xyz-123",
        "messages": [{"role": "user", "content": "Hello"}],
        "temperature": 0.7,
        "max_tokens": 10,
    }
    response = await authenticated_client.post(
        f"{settings.APP_API_V1_PREFIX}/ai/chat", json=payload
    )
    
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "AI_INVALID_MODEL"
    assert "success" in data
    assert data["success"] is False


@pytest.mark.asyncio
async def test_ai_chat_empty_messages(authenticated_client: AsyncClient):
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [],
        "temperature": 0.7,
        "max_tokens": 10,
    }
    response = await authenticated_client.post(
        f"{settings.APP_API_V1_PREFIX}/ai/chat", json=payload
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_ai_chat_missing_model(authenticated_client: AsyncClient):
    payload = {
        "messages": [{"role": "user", "content": "Hello"}],
        "temperature": 0.7,
        "max_tokens": 10,
    }
    response = await authenticated_client.post(
        f"{settings.APP_API_V1_PREFIX}/ai/chat", json=payload
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_ai_chat_invalid_temperature(authenticated_client: AsyncClient):
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Hello"}],
        "temperature": 5.0,
        "max_tokens": 10,
    }
    response = await authenticated_client.post(
        f"{settings.APP_API_V1_PREFIX}/ai/chat", json=payload
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_ai_chat_invalid_max_tokens(authenticated_client: AsyncClient):
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Hello"}],
        "temperature": 0.7,
        "max_tokens": -10,
    }
    response = await authenticated_client.post(
        f"{settings.APP_API_V1_PREFIX}/ai/chat", json=payload
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_ai_chat_invalid_message_role(authenticated_client: AsyncClient):
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "invalid_role", "content": "Hello"}],
        "temperature": 0.7,
        "max_tokens": 10,
    }
    response = await authenticated_client.post(
        f"{settings.APP_API_V1_PREFIX}/ai/chat", json=payload
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_ai_chat_empty_message_content(authenticated_client: AsyncClient):
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": ""}],
        "temperature": 0.7,
        "max_tokens": 10,
    }
    response = await authenticated_client.post(
        f"{settings.APP_API_V1_PREFIX}/ai/chat", json=payload
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_ai_chat_no_sensitive_data_in_error(authenticated_client: AsyncClient):
    payload = {
        "model": "invalid-model",
        "messages": [{"role": "user", "content": "Hello"}],
        "temperature": 0.7,
        "max_tokens": 10,
    }
    response = await authenticated_client.post(
        f"{settings.APP_API_V1_PREFIX}/ai/chat", json=payload
    )
    
    assert response.status_code == 400
    response_text = response.text.lower()
    
    sensitive_patterns = [
        "openai",
        "api key",
        "api_key",
        "sk-",
        "traceback",
        "exception",
        "timeout",
        "connection",
        "httpx",
    ]
    
    for pattern in sensitive_patterns:
        assert pattern not in response_text, f"Sensitive data leaked: '{pattern}'"


@pytest.mark.asyncio
async def test_ai_chat_error_response_structure(authenticated_client: AsyncClient):
    payload = {
        "model": "invalid-model",
        "messages": [{"role": "user", "content": "Hello"}],
        "temperature": 0.7,
        "max_tokens": 10,
    }
    response = await authenticated_client.post(
        f"{settings.APP_API_V1_PREFIX}/ai/chat", json=payload
    )
    
    assert response.status_code == 400
    data = response.json()
    
    assert "success" in data
    assert data["success"] is False
    assert "error" in data
    assert "code" in data["error"]
    assert "message" in data["error"]
    assert "details" in data["error"]


@pytest.mark.asyncio
async def test_ai_chat_request_id_in_error(authenticated_client: AsyncClient):
    payload = {
        "model": "invalid-model",
        "messages": [{"role": "user", "content": "Hello"}],
        "temperature": 0.7,
        "max_tokens": 10,
    }
    response = await authenticated_client.post(
        f"{settings.APP_API_V1_PREFIX}/ai/chat", json=payload
    )
    
    assert response.status_code == 400
    assert "x-request-id" in response.headers
    assert len(response.headers["x-request-id"]) > 0


@pytest.mark.asyncio
async def test_ai_chat_unauthorized_without_token(client: AsyncClient):
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Hello"}],
        "temperature": 0.7,
        "max_tokens": 10,
    }
    response = await client.post(
        f"{settings.APP_API_V1_PREFIX}/ai/chat", json=payload
    )
    
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_ERROR"


@pytest.mark.asyncio
async def test_ai_chat_forbidden_without_csrf(client: AsyncClient, test_user):
    login_payload = {"email": test_user.email, "password": "SecurePass123!"}
    login_response = await client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/login", json=login_payload
    )
    client.cookies.update(login_response.cookies)
    client.headers.pop(settings.CSRF_HEADER_NAME, None)
    
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Hello"}],
        "temperature": 0.7,
        "max_tokens": 10,
    }
    response = await client.post(
        f"{settings.APP_API_V1_PREFIX}/ai/chat", json=payload
    )
    
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "PERMISSION_DENIED"