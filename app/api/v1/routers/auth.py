from fastapi import APIRouter, Depends, Request, Response
from app.api.dependencies.auth import get_current_session, get_refresh_token_from_cookie
from app.api.dependencies.rate_limit import LoginRateLimiter, RegisterRateLimiter
from app.api.dependencies.services import get_auth_service, get_session_service, get_user_service
from app.core.config.settings import settings
from app.models.session import Session
from app.models.user import User
from app.schemas.auth import ChangePasswordRequest, LoginRequest, RegisterRequest
from app.schemas.common import SuccessResponse
from app.schemas.user import UserRead
from app.services.auth import AuthService
from app.services.session import SessionService
from app.services.user import UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _set_auth_cookies(
    response: Response, 
    access_token: str, 
    refresh_token: str,
    csrf_token: str,
) -> None:
    is_secure = settings.APP_ENV == "production"
    # The CSRF cookie must outlive the refresh token; otherwise the client
    # loses the ability to refresh after its idle period.
    refresh_max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=is_secure,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=is_secure,
        samesite="lax", 
        max_age=refresh_max_age,
        path=f"{settings.APP_API_V1_PREFIX}", 
    )
    
    response.set_cookie(
        key=settings.CSRF_COOKIE_NAME,
        value=csrf_token,
        httponly=False,
        secure=settings.CSRF_COOKIE_SECURE,
        samesite=settings.CSRF_COOKIE_SAMESITE,
        max_age=refresh_max_age,
        path=settings.CSRF_COOKIE_PATH,
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path=f"{settings.APP_API_V1_PREFIX}")
    response.delete_cookie(
        key=settings.CSRF_COOKIE_NAME,
        path=settings.CSRF_COOKIE_PATH,
    )

def _get_client_ip(request: Request) -> str:
    ip = getattr(request.state, "client_ip", None)
    if not ip and request.client:
        ip = request.client.host
    return ip or "unknown"


@router.post("/register", response_model=UserRead, status_code=201)
async def register(
    payload: RegisterRequest,
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
    _: None = Depends(RegisterRateLimiter()),
):
    user, _, access_token, refresh_token, csrf_token = await auth_service.register(
        email=payload.email,
        password=payload.password,
        ip=_get_client_ip(request),
        user_agent=request.headers.get("user-agent"),
    )
    _set_auth_cookies(response, access_token, refresh_token, csrf_token)
    return user


@router.post("/login", response_model=UserRead)
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
    _: None = Depends(LoginRateLimiter()),
):
    user, _, access_token, refresh_token, csrf_token = await auth_service.login(
        email=payload.email,
        password=payload.password,
        ip=_get_client_ip(request),
        user_agent=request.headers.get("user-agent"),
    )
    _set_auth_cookies(response, access_token, refresh_token, csrf_token)
    return user


@router.post("/logout", response_model=SuccessResponse)
async def logout(
    response: Response,
    session_data: tuple[User, Session] = Depends(get_current_session),
    session_service: SessionService = Depends(get_session_service),
):
    user, current_session = session_data
    await session_service.revoke_session(user.id, current_session.id)
    _clear_auth_cookies(response)
    return SuccessResponse(message="Logged out successfully.")


@router.post("/refresh", response_model=SuccessResponse)
async def refresh(
    request: Request,
    response: Response,
    refresh_token_str: str = Depends(get_refresh_token_from_cookie),
    auth_service: AuthService = Depends(get_auth_service),
):
    # The CSRF token stays stable per session: rotating it on every refresh
    # would invalidate the token the client already has in its header.
    csrf_token = request.cookies.get(settings.CSRF_COOKIE_NAME)
    new_access_token, new_refresh_token, csrf_token = await auth_service.refresh_tokens(
        refresh_token_str,
        current_csrf_token=csrf_token,
    )
    _set_auth_cookies(response, new_access_token, new_refresh_token, csrf_token)
    return SuccessResponse(message="Tokens refreshed successfully.")


@router.post("/change-password", response_model=SuccessResponse)
async def change_password(
    payload: ChangePasswordRequest,
    session_data: tuple[User, Session] = Depends(get_current_session),
    user_service: UserService = Depends(get_user_service),
    session_service: SessionService = Depends(get_session_service),
):
    user, current_session = session_data
    await user_service.change_password(user, payload.old_password, payload.new_password)
    await session_service.revoke_other_sessions(user.id, current_session.id)
    return SuccessResponse(message="Password changed successfully. Other sessions have been logged out.")