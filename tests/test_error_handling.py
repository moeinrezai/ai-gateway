import uuid
import pytest
from httpx import AsyncClient

from app.core.config.settings import settings


@pytest.mark.asyncio
async def test_error_response_standard_format_unauthorized(client: AsyncClient):
    """
    تست فرمت استاندارد Error Response برای خطای 401
    """
    response = await client.get(f"{settings.APP_API_V1_PREFIX}/users/me")
    
    assert response.status_code == 401
    data = response.json()
    
    assert "success" in data
    assert data["success"] is False
    assert "error" in data
    assert "code" in data["error"]
    assert "message" in data["error"]
    assert "details" in data["error"]
    assert data["error"]["code"] == "AUTHENTICATION_ERROR"
    assert isinstance(data["error"]["message"], str)
    assert isinstance(data["error"]["details"], dict)


@pytest.mark.asyncio
async def test_error_response_standard_format_forbidden(authenticated_client: AsyncClient):
    """
    تست فرمت استاندارد Error Response برای خطای 403
    """
    response = await authenticated_client.get(f"{settings.APP_API_V1_PREFIX}/users/admin-only")
    
    assert response.status_code == 403
    data = response.json()
    
    assert "success" in data
    assert data["success"] is False
    assert "error" in data
    assert "code" in data["error"]
    assert "message" in data["error"]
    assert "details" in data["error"]
    assert data["error"]["code"] == "PERMISSION_DENIED"


@pytest.mark.asyncio
async def test_error_response_standard_format_conflict(client: AsyncClient, test_user):
    """
    تست فرمت استاندارد Error Response برای خطای 409 (Conflict)
    """
    payload = {
        "email": test_user.email,
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!",
    }
    response = await client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/register", json=payload
    )
    
    assert response.status_code == 409
    data = response.json()
    
    assert "success" in data
    assert data["success"] is False
    assert "error" in data
    assert data["error"]["code"] == "USER_ALREADY_EXISTS"


@pytest.mark.asyncio
async def test_error_response_standard_format_validation_error(client: AsyncClient):
    """
    تست فرمت Error Response برای خطای 422 (Validation Error)
    """
    payload = {
        "email": "not-a-valid-email",
        "password": "short",
    }
    response = await client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/login", json=payload
    )
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_no_sensitive_data_in_error_response(client: AsyncClient):
    """
    تست عدم افشای اطلاعات حساس در Error Response
    Stack Trace, SQL Query, Secret, Internal Path نباید در Response باشد
    """
    response = await client.get(f"{settings.APP_API_V1_PREFIX}/users/me")
    
    assert response.status_code == 401
    response_text = response.text.lower()
    
    sensitive_patterns = [
        "traceback",
        "sqlalchemy",
        "asyncpg",
        "select ",
        "insert ",
        "password",
        "secret",
        "api_key",
        "jwt_secret",
        "/app/",
        "file \"/",
        "line ",
        "database_url",
        "redis_url",
    ]
    
    for pattern in sensitive_patterns:
        assert pattern not in response_text, f"Sensitive data leaked: '{pattern}' found in error response"


@pytest.mark.asyncio
async def test_no_internal_provider_error_leaked(authenticated_client: AsyncClient):
    """
    تست عدم نشت اطلاعات داخلی Provider در Error Response
    اگر مدل نامعتبر باشد، نباید خطای داخلی OpenAI برگردانده شود
    """
    payload = {
        "model": "invalid-model-xyz",
        "messages": [{"role": "user", "content": "Hello"}],
        "temperature": 0.7,
        "max_tokens": 10,
    }
    response = await authenticated_client.post(
        f"{settings.APP_API_V1_PREFIX}/ai/chat", json=payload
    )
    
    assert response.status_code == 400
    data = response.json()
    response_text = response.text.lower()
    
    assert data["error"]["code"] == "AI_INVALID_MODEL"
    assert "openai" not in response_text or "provider" in response_text
    assert "api key" not in response_text
    assert "traceback" not in response_text


@pytest.mark.asyncio
async def test_request_id_in_response_headers(client: AsyncClient):
    """
    تست وجود Request ID در هدرهای Response
    """
    response = await client.get(f"{settings.APP_API_V1_PREFIX}/users/me")
    
    assert "x-request-id" in response.headers
    request_id = response.headers["x-request-id"]
    assert request_id is not None
    assert len(request_id) > 0
    
    try:
        uuid.UUID(request_id)
    except ValueError:
        pytest.fail(f"Request ID is not a valid UUID: {request_id}")


@pytest.mark.asyncio
async def test_request_id_unique_per_request(client: AsyncClient):
    """
    تست اینکه هر درخواست Request ID یکتا دارد
    """
    response1 = await client.get(f"{settings.APP_API_V1_PREFIX}/users/me")
    response2 = await client.get(f"{settings.APP_API_V1_PREFIX}/users/me")
    
    id1 = response1.headers.get("x-request-id")
    id2 = response2.headers.get("x-request-id")
    
    assert id1 is not None
    assert id2 is not None
    assert id1 != id2


@pytest.mark.asyncio
async def test_http_status_code_authentication_error(client: AsyncClient):
    """
    تست کد HTTP صحیح برای خطای احراز هویت (401 نه 403)
    """
    response = await client.get(f"{settings.APP_API_V1_PREFIX}/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_http_status_code_authorization_error(authenticated_client: AsyncClient):
    """
    تست کد HTTP صحیح برای خطای مجوز (403 نه 401)
    """
    response = await authenticated_client.get(f"{settings.APP_API_V1_PREFIX}/users/admin-only")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_http_status_code_not_found(authenticated_client: AsyncClient):
    """
    تست کد HTTP صحیح برای منبع ناموجود (404)
    """
    fake_session_id = str(uuid.uuid4())
    response = await authenticated_client.delete(
        f"{settings.APP_API_V1_PREFIX}/sessions/{fake_session_id}"
    )
    assert response.status_code in [403, 404]


@pytest.mark.asyncio
async def test_http_status_code_rate_limit(client: AsyncClient, test_user):
    """
    تست کد HTTP صحیح برای Rate Limit (429)
    """
    payload = {"email": test_user.email, "password": "SecurePass123!"}
    
    for _ in range(5):
        await client.post(
            f"{settings.APP_API_V1_PREFIX}/auth/login", json=payload
        )
    
    response = await client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/login", json=payload
    )
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"