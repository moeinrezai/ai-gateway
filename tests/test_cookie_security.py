import pytest
from httpx import AsyncClient

from app.core.config.settings import settings


@pytest.mark.asyncio
async def test_access_token_httponly_flag(client: AsyncClient, test_user):
    login_payload = {"email": test_user.email, "password": "SecurePass123!"}
    response = await client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/login", json=login_payload
    )
    
    assert response.status_code == 200
    set_cookie_header = response.headers.get("set-cookie", "")
    
    access_token_part = None
    for cookie in set_cookie_header.split(","):
        if "access_token=" in cookie:
            access_token_part = cookie
            break
    
    assert access_token_part is not None
    assert "httponly" in access_token_part.lower()


@pytest.mark.asyncio
async def test_refresh_token_httponly_flag(client: AsyncClient, test_user):
    login_payload = {"email": test_user.email, "password": "SecurePass123!"}
    response = await client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/login", json=login_payload
    )
    
    assert response.status_code == 200
    set_cookie_header = response.headers.get("set-cookie", "")
    
    refresh_token_part = None
    for cookie in set_cookie_header.split(","):
        if "refresh_token=" in cookie:
            refresh_token_part = cookie
            break
    
    assert refresh_token_part is not None
    assert "httponly" in refresh_token_part.lower()


@pytest.mark.asyncio
async def test_csrf_token_not_httponly(client: AsyncClient, test_user):
    login_payload = {"email": test_user.email, "password": "SecurePass123!"}
    response = await client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/login", json=login_payload
    )
    
    assert response.status_code == 200
    set_cookie_header = response.headers.get("set-cookie", "")
    
    csrf_token_part = None
    for cookie in set_cookie_header.split(","):
        if "csrf_token=" in cookie:
            csrf_token_part = cookie
            break
    
    assert csrf_token_part is not None
    assert "httponly" not in csrf_token_part.lower()


@pytest.mark.asyncio
async def test_cookies_samesite_attribute(client: AsyncClient, test_user):
    login_payload = {"email": test_user.email, "password": "SecurePass123!"}
    response = await client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/login", json=login_payload
    )
    
    assert response.status_code == 200
    set_cookie_header = response.headers.get("set-cookie", "").lower()
    
    assert "samesite=" in set_cookie_header


@pytest.mark.asyncio
async def test_refresh_token_path_restriction(client: AsyncClient, test_user):
    login_payload = {"email": test_user.email, "password": "SecurePass123!"}
    response = await client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/login", json=login_payload
    )
    
    assert response.status_code == 200
    set_cookie_header = response.headers.get("set-cookie", "")
    
    refresh_token_part = None
    for cookie in set_cookie_header.split(","):
        if "refresh_token=" in cookie:
            refresh_token_part = cookie
            break
    
    assert refresh_token_part is not None
    assert f"path={settings.APP_API_V1_PREFIX}" in refresh_token_part.lower()


@pytest.mark.asyncio
async def test_tokens_not_in_response_body(client: AsyncClient, test_user):
    login_payload = {"email": test_user.email, "password": "SecurePass123!"}
    response = await client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/login", json=login_payload
    )
    
    assert response.status_code == 200
    response_body = response.json()
    
    assert "access_token" not in response_body
    assert "refresh_token" not in response_body
    assert "token" not in str(response_body).lower() or "csrf" in str(response_body).lower()


@pytest.mark.asyncio
async def test_cookies_cleared_after_logout(authenticated_client: AsyncClient):
    response = await authenticated_client.post(f"{settings.APP_API_V1_PREFIX}/auth/logout")
    
    assert response.status_code == 200
    set_cookie_header = response.headers.get("set-cookie", "")
    
    assert "access_token=;" in set_cookie_header or "access_token=" in set_cookie_header
    assert "refresh_token=;" in set_cookie_header or "refresh_token=" in set_cookie_header


@pytest.mark.asyncio
async def test_cookie_max_age_access_token(client: AsyncClient, test_user):
    login_payload = {"email": test_user.email, "password": "SecurePass123!"}
    response = await client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/login", json=login_payload
    )
    
    assert response.status_code == 200
    set_cookie_header = response.headers.get("set-cookie", "")
    
    access_token_part = None
    for cookie in set_cookie_header.split(","):
        if "access_token=" in cookie:
            access_token_part = cookie
            break
    
    assert access_token_part is not None
    expected_max_age = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    assert f"max-age={expected_max_age}" in access_token_part.lower()


@pytest.mark.asyncio
async def test_cookie_max_age_refresh_token(client: AsyncClient, test_user):
    login_payload = {"email": test_user.email, "password": "SecurePass123!"}
    response = await client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/login", json=login_payload
    )
    
    assert response.status_code == 200
    set_cookie_header = response.headers.get("set-cookie", "")
    
    refresh_token_part = None
    for cookie in set_cookie_header.split(","):
        if "refresh_token=" in cookie:
            refresh_token_part = cookie
            break
    
    assert refresh_token_part is not None
    expected_max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    assert f"max-age={expected_max_age}" in refresh_token_part.lower()


@pytest.mark.asyncio
async def test_all_three_cookies_set_on_login(client: AsyncClient, test_user):
    login_payload = {"email": test_user.email, "password": "SecurePass123!"}
    response = await client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/login", json=login_payload
    )
    
    assert response.status_code == 200
    
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies
    assert "csrf_token" in response.cookies


@pytest.mark.asyncio
async def test_register_sets_cookies(client: AsyncClient):
    import uuid
    payload = {
        "email": f"cookie_test_{uuid.uuid4()}@example.com",
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!",
    }
    response = await client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/register", json=payload
    )
    
    assert response.status_code == 201
    
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies
    assert "csrf_token" in response.cookies