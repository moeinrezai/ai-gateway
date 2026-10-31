import pytest
from httpx import AsyncClient

from app.core.config.settings import settings


@pytest.mark.asyncio
async def test_login_rate_limit(client: AsyncClient, test_user):
    """
    تست محدودیت نرخ در Login
    باید بعد از 5 درخواست موفق، درخواست ششم با 429 مسدود شود
    """
    payload = {"email": test_user.email, "password": "SecurePass123!"}
    
    # 5 درخواست موفق
    for i in range(5):
        response = await client.post(
            f"{settings.APP_API_V1_PREFIX}/auth/login", json=payload
        )
        assert response.status_code == 200, f"Request {i+1} should succeed"
    
    # درخواست ششم باید مسدود شود
    response = await client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/login", json=payload
    )
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"


@pytest.mark.asyncio
async def test_register_rate_limit(client: AsyncClient):
    """
    تست محدودیت نرخ در Register
    باید بعد از 3 درخواست، درخواست چهارم با 429 مسدود شود
    """
    import uuid
    
    # 3 درخواست موفق
    for i in range(3):
        payload = {
            "email": f"ratelimit_{i}_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
        }
        response = await client.post(
            f"{settings.APP_API_V1_PREFIX}/auth/register", json=payload
        )
        assert response.status_code == 201, f"Request {i+1} should succeed"
    
    # درخواست چهارم باید مسدود شود
    payload = {
        "email": f"ratelimit_blocked_{uuid.uuid4()}@example.com",
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!",
    }
    response = await client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/register", json=payload
    )
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"


@pytest.mark.asyncio
async def test_ai_chat_rate_limit(authenticated_client: AsyncClient):
    """
    تست محدودیت نرخ در AI Chat
    باید بعد از 20 درخواست، درخواست بیست و یکم با 429 مسدود شود
    """
    payload = {
        "model": "mock-model",
        "messages": [{"role": "user", "content": "Hello"}],
        "temperature": 0.7,
        "max_tokens": 10,
    }
    
    # 20 درخواست موفق
    for i in range(20):
        response = await authenticated_client.post(
            f"{settings.APP_API_V1_PREFIX}/ai/chat", json=payload
        )
        assert response.status_code == 200, f"Request {i+1} should succeed"
    
    # درخواست بیست و یکم باید مسدود شود
    response = await authenticated_client.post(
        f"{settings.APP_API_V1_PREFIX}/ai/chat", json=payload
    )
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"


@pytest.mark.asyncio
async def test_rate_limit_error_response_structure(client: AsyncClient, test_user):
    """
    تست ساختار پاسخ خطای Rate Limit
    باید فرمت استاندارد Error Response را داشته باشد
    """
    payload = {"email": test_user.email, "password": "SecurePass123!"}
    
    # رسیدن به سقف Rate Limit
    for _ in range(5):
        await client.post(
            f"{settings.APP_API_V1_PREFIX}/auth/login", json=payload
        )
    
    # درخواست مسدود شده
    response = await client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/login", json=payload
    )
    
    assert response.status_code == 429
    data = response.json()
    
    # بررسی ساختار استاندارد Error Response
    assert "success" in data
    assert data["success"] is False
    assert "error" in data
    assert "code" in data["error"]
    assert "message" in data["error"]
    assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"