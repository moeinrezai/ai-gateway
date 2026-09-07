import pytest
from httpx import AsyncClient

from app.core.config.settings import settings


@pytest.mark.asyncio
async def test_admin_endpoint_access_with_admin_role(admin_client: AsyncClient):
    """
    تست دسترسی موفق به endpoint admin-only با کاربر admin
    """
    response = await admin_client.get(f"{settings.APP_API_V1_PREFIX}/users/admin-only")
    
    assert response.status_code == 200
    assert response.json()["message"] == "Admin access granted"


@pytest.mark.asyncio
async def test_admin_endpoint_access_denied_for_regular_user(authenticated_client: AsyncClient):
    """
    تست رد دسترسی کاربر عادی به endpoint admin-only
    باید 403 Forbidden برگرداند
    """
    response = await authenticated_client.get(f"{settings.APP_API_V1_PREFIX}/users/admin-only")
    
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "PERMISSION_DENIED"
    assert "Insufficient permissions" in response.json()["error"]["message"]


@pytest.mark.asyncio
async def test_session_list_access_with_valid_user(authenticated_client: AsyncClient):
    """
    تست دسترسی کاربر احراز هویت شده به لیست sessionهای خود
    """
    response = await authenticated_client.get(f"{settings.APP_API_V1_PREFIX}/sessions/")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_session_list_access_denied_without_auth(client: AsyncClient):
    """
    تست رد دسترسی به لیست sessionها بدون احراز هویت
    باید 401 Unauthorized برگرداند
    """
    response = await client.get(f"{settings.APP_API_V1_PREFIX}/sessions/")
    
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_ERROR"


@pytest.mark.asyncio
async def test_user_can_only_see_own_sessions(authenticated_client: AsyncClient, test_user):
    """
    تست اینکه کاربر فقط می‌تواند sessionهای خود را ببیند
    """
    response = await authenticated_client.get(f"{settings.APP_API_V1_PREFIX}/sessions/")
    
    assert response.status_code == 200
    sessions = response.json()
    
    for session in sessions:
        assert session["user_id"] == str(test_user.id)


@pytest.mark.asyncio
async def test_error_response_structure_for_permission_denied(authenticated_client: AsyncClient):
    """
    تست ساختار استاندارد Error Response برای خطای Permission Denied
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