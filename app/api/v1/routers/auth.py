from fastapi import APIRouter, Depends, Request, Response

from app.api.dependencies.services import get_auth_service
from app.core.config import settings
from app.schemas.auth import LoginRequest, RegisterRequest
from app.schemas.user import UserRead
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    is_secure = settings.APP_ENV == "production"
    
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
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path=f"{settings.APP_API_V1_PREFIX}/auth/refresh",
    )


def _get_client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


@router.post("/register", response_model=UserRead, status_code=201)
async def register(
    payload: RegisterRequest,
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    user, _, access_token, refresh_token = await auth_service.register(
        email=payload.email,
        password=payload.password,
        ip=_get_client_ip(request),
        user_agent=request.headers.get("user-agent"),
    )
    
    _set_auth_cookies(response, access_token, refresh_token)
    return user


@router.post("/login", response_model=UserRead)
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    user, _, access_token, refresh_token = await auth_service.login(
        email=payload.email,
        password=payload.password,
        ip=_get_client_ip(request),
        user_agent=request.headers.get("user-agent"),
    )
    
    _set_auth_cookies(response, access_token, refresh_token)
    return user