import pytest
from httpx import AsyncClient

from app.core.config import settings


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    payload = {
        "email": f"newuser_{uuid.uuid4()}@example.com",
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!",
    }
    response = await client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/register", json=payload
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert "id" in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    payload = {"email": test_user.email, "password": "SecurePass123!"}
    response = await client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/login", json=payload
    )

    assert response.status_code == 200
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies
    assert response.cookies["access_token"] != ""


@pytest.mark.asyncio
async def test_get_profile_unauthorized(client: AsyncClient):
    response = await client.get(f"{settings.APP_API_V1_PREFIX}/users/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_ERROR"


@pytest.mark.asyncio
async def test_get_profile_authorized(client: AsyncClient, test_user):
    login_payload = {"email": test_user.email, "password": "SecurePass123!"}
    login_response = await client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/login", json=login_payload
    )

    cookies = login_response.cookies

    response = await client.get(
        f"{settings.APP_API_V1_PREFIX}/users/me", cookies=cookies
    )

    assert response.status_code == 200
    assert response.json()["email"] == test_user.email
