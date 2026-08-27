import pytest
from httpx import AsyncClient

from app.core.config.settings import settings


@pytest.mark.asyncio
async def test_logout_success(authenticated_client: AsyncClient):
    response = await authenticated_client.post(f"{settings.APP_API_V1_PREFIX}/auth/logout")
    
    assert response.status_code == 200
    assert response.json()["success"] is True
    
    assert "access_token" not in response.cookies
    assert "refresh_token" not in response.cookies
    assert "csrf_token" not in response.cookies


@pytest.mark.asyncio
async def test_refresh_token_success_and_rotation(authenticated_client: AsyncClient):
    old_refresh_token = authenticated_client.cookies.get("refresh_token")
    
    response = await authenticated_client.post(f"{settings.APP_API_V1_PREFIX}/auth/refresh")
    
    assert response.status_code == 200
    assert response.json()["success"] is True
    
    new_refresh_token = response.cookies.get("refresh_token")
    new_access_token = response.cookies.get("access_token")
    
    assert new_refresh_token is not None
    assert new_access_token is not None
    assert new_refresh_token != old_refresh_token


@pytest.mark.asyncio
async def test_refresh_token_replay_attack(authenticated_client: AsyncClient):
    old_refresh_token = authenticated_client.cookies.get("refresh_token")
    
    response1 = await authenticated_client.post(f"{settings.APP_API_V1_PREFIX}/auth/refresh")
    assert response1.status_code == 200
    
    response2 = await authenticated_client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/refresh",
        cookies={"refresh_token": old_refresh_token}
    )
    
    assert response2.status_code == 401
    assert response2.json()["error"]["code"] == "INVALID_TOKEN"