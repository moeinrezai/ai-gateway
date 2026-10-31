import re
import uuid

import jwt as pyjwt
import pytest
from httpx import AsyncClient

from app.core.config.settings import settings


def _cookie_max_age(set_cookie_header: str) -> str | None:
    match = re.search(r"max-age=(\d+)", set_cookie_header, re.IGNORECASE)
    return f"max-age={match.group(1)}" if match else None


async def _login(client: AsyncClient, email: str, password: str):
    response = await client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return response


@pytest.mark.asyncio
async def test_csrf_error_response_is_standard_json(client: AsyncClient, test_user):
    """CSRF middleware must return the app error format, not a raw 500."""
    login_response = await _login(client, test_user.email, test_user.password)
    client.cookies.update(login_response.cookies)
    client.headers.pop(settings.CSRF_HEADER_NAME, None)

    response = await client.post(f"{settings.APP_API_V1_PREFIX}/auth/logout")

    assert response.status_code == 403
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "PERMISSION_DENIED"
    assert "CSRF token missing" in data["error"]["message"]


@pytest.mark.asyncio
async def test_csrf_403_includes_cors_headers_for_allowed_origin(
    client: AsyncClient, test_user
):
    """The browser must be able to read the CSRF 403 on cross-origin requests."""
    login_response = await _login(client, test_user.email, test_user.password)
    client.cookies.update(login_response.cookies)
    client.headers.pop(settings.CSRF_HEADER_NAME, None)
    client.headers["Origin"] = "http://localhost:3000"

    response = await client.post(f"{settings.APP_API_V1_PREFIX}/auth/logout")

    assert response.status_code == 403
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


@pytest.mark.asyncio
async def test_state_changing_request_without_auth_cookies_skips_csrf(
    client: AsyncClient,
):
    """No authentication cookies means no credentials to forge; the request
    must reach authentication and fail with 401, not CSRF 403."""
    payload = {
        "model": "mock-model",
        "messages": [{"role": "user", "content": "Hello"}],
    }
    response = await client.post(f"{settings.APP_API_V1_PREFIX}/ai/chat", json=payload)

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_ERROR"


@pytest.mark.asyncio
async def test_login_sets_single_canonical_csrf_cookie(client: AsyncClient, test_user):
    """Regression: duplicate CSRF cookie names (csrf-token / csrftoken)
    must never be introduced."""
    response = await _login(client, test_user.email, test_user.password)

    set_cookie_headers = response.headers.get_list("set-cookie")
    csrf_cookies = [
        name
        for name in ("csrf_token", "csrf-token", "csrftoken")
        for header in set_cookie_headers
        if header.lower().startswith(f"{name}=")
    ]
    assert response.cookies.get(settings.CSRF_COOKIE_NAME)
    assert csrf_cookies == [settings.CSRF_COOKIE_NAME]


@pytest.mark.asyncio
async def test_csrf_cookie_lifetime_matches_refresh_token(
    client: AsyncClient, test_user
):
    """The CSRF cookie must live at least as long as the refresh token,
    otherwise refresh fails with 'CSRF token missing' after idling."""
    response = await _login(client, test_user.email, test_user.password)

    refresh_max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    csrf_max_age = [
        _cookie_max_age(header)
        for header in response.headers.get_list("set-cookie")
        if header.startswith(f"{settings.CSRF_COOKIE_NAME}=")
    ]

    assert csrf_max_age == [f"max-age={refresh_max_age}"]


@pytest.mark.asyncio
async def test_refresh_missing_refresh_token(authenticated_client: AsyncClient):
    authenticated_client.cookies.pop("refresh_token", None)

    response = await authenticated_client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/refresh"
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_ERROR"


@pytest.mark.asyncio
async def test_refresh_with_malformed_refresh_token(authenticated_client: AsyncClient):
    authenticated_client.cookies.set("refresh_token", "not-a-jwt")

    response = await authenticated_client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/refresh"
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_TOKEN"


@pytest.mark.asyncio
async def test_refresh_rejects_access_token_as_refresh_token(
    authenticated_client: AsyncClient, test_user
):
    access_token = authenticated_client.cookies["access_token"]
    old_refresh_token = authenticated_client.cookies["refresh_token"]
    authenticated_client.cookies.set("refresh_token", access_token)

    response = await authenticated_client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/refresh"
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_TOKEN"

    # Session and tokens are untouched by a failed refresh.
    authenticated_client.cookies.set("refresh_token", old_refresh_token)
    me = await authenticated_client.get(f"{settings.APP_API_V1_PREFIX}/users/me")
    assert me.status_code == 200
    assert me.json()["email"] == test_user.email


@pytest.mark.asyncio
async def test_refresh_with_expired_refresh_token(authenticated_client: AsyncClient):
    login_seed = authenticated_client.cookies["refresh_token"]
    payload = pyjwt.decode(
        login_seed,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithms=[settings.JWT_ALGORITHM],
    )
    expired_token = pyjwt.encode(
        {
            "sub": payload["sub"],
            "sid": payload["sid"],
            "type": "refresh",
            "jti": payload["jti"],
            "iat": payload["iat"],
            "nbf": payload["nbf"],
            "exp": payload["iat"] - 60,
        },
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )
    authenticated_client.cookies.set("refresh_token", expired_token)

    response = await authenticated_client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/refresh"
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_TOKEN"
    assert "expired" in response.json()["error"]["message"]


@pytest.mark.asyncio
async def test_refresh_rotation_revoked_old_token_and_session(
    authenticated_client: AsyncClient,
):
    old_refresh_token = authenticated_client.cookies["refresh_token"]
    old_csrf_token = authenticated_client.cookies[settings.CSRF_COOKIE_NAME]

    response = await authenticated_client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/refresh"
    )

    assert response.status_code == 200

    # New refresh token is issued and the CSRF token stays stable per session.
    assert response.cookies["refresh_token"] != old_refresh_token
    assert response.cookies[settings.CSRF_COOKIE_NAME] == old_csrf_token

    replay = await authenticated_client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/refresh",
        cookies={"refresh_token": old_refresh_token},
    )
    assert replay.status_code == 401
    assert replay.json()["error"]["code"] == "INVALID_TOKEN"

    # Reuse detection revokes the whole session.
    me = await authenticated_client.get(f"{settings.APP_API_V1_PREFIX}/users/me")
    assert me.status_code == 401
    assert me.json()["error"]["code"] == "INVALID_TOKEN"


@pytest.mark.asyncio
async def test_refresh_without_csrf_header_is_rejected(
    authenticated_client: AsyncClient,
):
    authenticated_client.headers.pop(settings.CSRF_HEADER_NAME, None)

    response = await authenticated_client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/refresh"
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "PERMISSION_DENIED"


@pytest.mark.asyncio
async def test_refresh_replaces_all_cookies(authenticated_client: AsyncClient):
    response = await authenticated_client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/refresh"
    )

    assert response.status_code == 200
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies
    assert settings.CSRF_COOKIE_NAME in response.cookies

    me = await authenticated_client.get(f"{settings.APP_API_V1_PREFIX}/users/me")
    assert me.status_code == 200


@pytest.mark.asyncio
async def test_refresh_token_not_accepted_by_access_token_flow(
    client: AsyncClient, test_user
):
    login_response = await _login(client, test_user.email, test_user.password)
    client.cookies.clear()
    client.cookies.set("access_token", login_response.cookies["refresh_token"])
    client.headers[settings.CSRF_HEADER_NAME] = login_response.cookies[
        settings.CSRF_COOKIE_NAME
    ]

    response = await client.get(f"{settings.APP_API_V1_PREFIX}/users/me")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_TOKEN"


@pytest.mark.asyncio
async def test_login_does_not_set_csrf_on_failed_login(client: AsyncClient):
    response = await client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/login",
        json={"email": f"ghost_{uuid.uuid4()}@example.com", "password": "Whatever123!"},
    )

    assert response.status_code == 401
    assert "access_token" not in response.cookies
    assert "refresh_token" not in response.cookies
    assert settings.CSRF_COOKIE_NAME not in response.cookies
