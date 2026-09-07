import pytest
from httpx import AsyncClient

from app.core.config.settings import settings


@pytest.mark.asyncio
async def test_csrf_protected_endpoint_without_token(client: AsyncClient, test_user):
    """
    تست رد درخواست به اندپوینت محافظت‌شده بدون هدر CSRF Token
    """
    # 1. لاگین برای دریافت کوکی‌ها (شامل csrf_token)
    login_payload = {"email": test_user.email, "password": "SecurePass123!"}
    login_response = await client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/login", json=login_payload
    )
    assert login_response.status_code == 200
    client.cookies.update(login_response.cookies)
    
    # 2. حذف صریح هدر CSRF برای شبیه‌سازی حمله یا فراموشی کلاینت
    client.headers.pop(settings.CSRF_HEADER_NAME, None)
    
    # 3. ارسال درخواست به اندپوینت محافظت‌شده (مثلاً logout)
    response = await client.post(f"{settings.APP_API_V1_PREFIX}/auth/logout")
    
    # 4. بررسی پاسخ 403 Forbidden
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "PERMISSION_DENIED"
    assert "CSRF token missing" in response.json()["error"]["message"]


@pytest.mark.asyncio
async def test_csrf_protected_endpoint_with_invalid_token(client: AsyncClient, test_user):
    """
    تست رد درخواست با هدر CSRF Token نامعتبر (عدم تطابق با کوکی)
    """
    # 1. لاگین
    login_payload = {"email": test_user.email, "password": "SecurePass123!"}
    login_response = await client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/login", json=login_payload
    )
    assert login_response.status_code == 200
    client.cookies.update(login_response.cookies)
    
    # 2. تنظیم یک توکن CSRF جعلی در هدر
    client.headers[settings.CSRF_HEADER_NAME] = "invalid-csrf-token-12345"
    
    # 3. ارسال درخواست به اندپوینت محافظت‌شده
    response = await client.post(f"{settings.APP_API_V1_PREFIX}/auth/logout")
    
    # 4. بررسی پاسخ 403 Forbidden
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "PERMISSION_DENIED"
    assert "CSRF token validation failed" in response.json()["error"]["message"]


@pytest.mark.asyncio
async def test_csrf_bypass_for_safe_methods(client: AsyncClient):
    """
    تست عبور درخواست‌های Safe (مانند GET) از اعتبارسنجی CSRF
    """
    # ارسال درخواست GET به یک اندپوینت عمومی بدون هیچ کوکی یا هدر CSRF
    response = await client.get(f"{settings.APP_API_V1_PREFIX}/users/me")
    
    # باید 401 Unauthorized بدهد (به دلیل نبود JWT)، نه 403 Forbidden (به دلیل CSRF)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_ERROR"


@pytest.mark.asyncio
async def test_csrf_bypass_for_initial_auth_endpoints(client: AsyncClient):
    """
    تست عبور اندپوینت‌های اولیه احراز هویت (Login/Register) از اعتبارسنجی CSRF
    """
    import uuid
    
    # تست Register بدون CSRF Token
    payload = {
        "email": f"csrf_test_{uuid.uuid4()}@example.com",
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!",
    }
    response = await client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/register", json=payload
    )
    
    # باید 201 Created بدهد، نه 403 Forbidden
    assert response.status_code == 201
    assert "id" in response.json()