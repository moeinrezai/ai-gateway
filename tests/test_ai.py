import pytest
from httpx import AsyncClient

from app.core.config.settings import settings


@pytest.mark.asyncio
async def test_ai_chat_success(authenticated_client: AsyncClient):
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Hello"}],
        "temperature": 0.7,
        "max_tokens": 50
    }
    response = await authenticated_client.post(
        f"{settings.APP_API_V1_PREFIX}/ai/chat", json=payload
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["provider"] == "openai"


@pytest.mark.asyncio
async def test_ai_chat_invalid_model(authenticated_client: AsyncClient):
    payload = {
        "model": "invalid-model-name",
        "messages": [{"role": "user", "content": "Hello"}],
        "temperature": 0.7,
        "max_tokens": 50
    }
    response = await authenticated_client.post(
        f"{settings.APP_API_V1_PREFIX}/ai/chat", json=payload
    )
    
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "AI_INVALID_MODEL"


@pytest.mark.asyncio
async def test_ai_chat_without_csrf(client: AsyncClient, test_user):
    # 1. لاگین برای دریافت کوکی‌ها
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
        "max_tokens": 50
    }
    

    print(f"\n[DEBUG] Headers being sent: {dict(client.headers)}")
    
    response = await client.post(
        f"{settings.APP_API_V1_PREFIX}/ai/chat", json=payload
    )
    
    print(f"[DEBUG] Response status code: {response.status_code}")
    print(f"[DEBUG] Response body: {response.text}\n")
    

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "PERMISSION_DENIED"