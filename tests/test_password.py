import pytest
from httpx import AsyncClient

from app.core.config.settings import settings


@pytest.mark.asyncio
async def test_change_password_success(authenticated_client: AsyncClient, test_user):
    """
    تست تغییر رمز عبور موفق
    باید 200 OK برگرداند و پیام موفقیت نمایش دهد
    """
    payload = {
        "old_password": "SecurePass123!",
        "new_password": "NewSecurePass456!",
        "new_password_confirm": "NewSecurePass456!",
    }
    
    response = await authenticated_client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/change-password", json=payload
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Password changed successfully" in data["message"]


@pytest.mark.asyncio
async def test_change_password_with_wrong_old_password(authenticated_client: AsyncClient):
    """
    تست رد درخواست با رمز قدیمی اشتباه
    باید 401 Unauthorized برگرداند
    """
    payload = {
        "old_password": "WrongOldPassword!",
        "new_password": "NewSecurePass456!",
        "new_password_confirm": "NewSecurePass456!",
    }
    
    response = await authenticated_client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/change-password", json=payload
    )
    
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_change_password_with_mismatched_confirmation(authenticated_client: AsyncClient):
    """
    تست رد درخواست با عدم تطابق تأیید رمز جدید
    باید 422 Unprocessable Entity برگرداند (Validation Error)
    """
    payload = {
        "old_password": "SecurePass123!",
        "new_password": "NewSecurePass456!",
        "new_password_confirm": "DifferentPassword!",
    }
    
    response = await authenticated_client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/change-password", json=payload
    )
    
    assert response.status_code == 422
    # Pydantic Validation Error ساختار متفاوتی دارد
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_change_password_with_weak_password(authenticated_client: AsyncClient):
    """
    تست رد درخواست با رمز عبور ضعیف (کمتر از 8 کاراکتر)
    باید 422 Unprocessable Entity برگرداند
    """
    payload = {
        "old_password": "SecurePass123!",
        "new_password": "weak",
        "new_password_confirm": "weak",
    }
    
    response = await authenticated_client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/change-password", json=payload
    )
    
    assert response.status_code == 422
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_change_password_revokes_other_sessions(
    client: AsyncClient, test_user
):
    """
    تست اینکه تغییر رمز عبور، سایر Sessionها را Revoke می‌کند
    1. دو بار Login می‌کنیم (دو Session مختلف)
    2. با Session اول رمز را تغییر می‌دهیم
    3. Session دوم باید دیگر معتبر نباشد
    """
    # Login اول
    login_payload = {"email": test_user.email, "password": "SecurePass123!"}
    login_response_1 = await client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/login", json=login_payload
    )
    assert login_response_1.status_code == 200
    client.cookies.update(login_response_1.cookies)
    
    # استخراج CSRF Token برای Session اول
    csrf_token = login_response_1.cookies.get(settings.CSRF_COOKIE_NAME)
    client.headers[settings.CSRF_HEADER_NAME] = csrf_token
    
    # Login دوم (Session جدید)
    login_response_2 = await client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/login", json=login_payload
    )
    assert login_response_2.status_code == 200
    second_session_cookies = login_response_2.cookies
    
    # تغییر رمز با Session اول
    change_payload = {
        "old_password": "SecurePass123!",
        "new_password": "NewSecurePass456!",
        "new_password_confirm": "NewSecurePass456!",
    }
    change_response = await client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/change-password", json=change_payload
    )
    assert change_response.status_code == 200
    
    # تلاش برای دسترسی با Session دوم (باید 401 بدهد)
    client.cookies.clear()
    client.cookies.update(second_session_cookies)
    client.headers.pop(settings.CSRF_HEADER_NAME, None)
    
    response = await client.get(f"{settings.APP_API_V1_PREFIX}/users/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_ERROR"


@pytest.mark.asyncio
async def test_change_password_error_response_structure(authenticated_client: AsyncClient):
    """
    تست ساختار استاندارد Error Response برای خطای تغییر رمز
    """
    payload = {
        "old_password": "WrongPassword!",
        "new_password": "NewSecurePass456!",
        "new_password_confirm": "NewSecurePass456!",
    }
    
    response = await authenticated_client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/change-password", json=payload
    )
    
    assert response.status_code == 401
    data = response.json()
    
    # بررسی ساختار استاندارد Error Response
    assert "success" in data
    assert data["success"] is False
    assert "error" in data
    assert "code" in data["error"]
    assert "message" in data["error"]
    assert "details" in data["error"]
    assert data["error"]["code"] == "INVALID_CREDENTIALS"