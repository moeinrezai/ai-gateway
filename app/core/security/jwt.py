import uuid
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config.settings import settings
from app.core.exceptions.auth import InvalidTokenError


def _create_token(
    subject: uuid.UUID,
    session_id: uuid.UUID,
    token_type: str,
    expires_delta: timedelta,
    extra_claims: dict | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    to_encode = {
        "sub": str(subject),
        "sid": str(session_id),
        "type": token_type,
        "jti": str(uuid.uuid4()),
        "iat": now,
        "nbf": now,
        "exp": now + expires_delta,
    }
    if extra_claims:
        to_encode.update(extra_claims)

    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )


def create_access_token(
    subject: uuid.UUID,
    session_id: uuid.UUID,
    role: str,
    csrf_token: str | None = None,
) -> str:
    extra_claims = {"role": role}
    if csrf_token:
        extra_claims["csrf"] = csrf_token
    
    return _create_token(
        subject=subject,
        session_id=session_id,
        token_type="access",
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        extra_claims=extra_claims,
    )


def create_refresh_token(
    subject: uuid.UUID,
    session_id: uuid.UUID,
) -> str:
    return _create_token(
        subject=subject,
        session_id=session_id,
        token_type="refresh",
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str, expected_type: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_exp": True},
        )
        
        if payload.get("type") != expected_type:
            raise InvalidTokenError("Invalid token type.")
            
        return payload
        
    except jwt.ExpiredSignatureError:
        raise InvalidTokenError("Token has expired.")
    except jwt.InvalidTokenError:
        raise InvalidTokenError("Invalid token.")