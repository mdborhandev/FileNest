from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import jwt
from jwt import InvalidTokenError

from app.core.config import settings
from app.core.exceptions import TokenError


def _secret_for(token_type: str) -> str:
    if token_type == "refresh":
        return settings.jwt_refresh_secret_key
    return settings.jwt_secret_key


def create_token(user_id: int, token_type: str, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
        "jti": str(uuid4()),
    }
    return jwt.encode(
        payload,
        _secret_for(token_type),
        algorithm=settings.jwt_algorithm,
    )


def create_access_token(user_id: int) -> str:
    return create_token(
        user_id,
        "access",
        timedelta(minutes=settings.access_token_expire_minutes),
    )


def create_refresh_token(user_id: int) -> str:
    return create_token(
        user_id,
        "refresh",
        timedelta(days=settings.refresh_token_expire_days),
    )


def decode_token(token: str, expected_type: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            _secret_for(expected_type),
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "type", "iat", "exp"]},
        )
    except (InvalidTokenError, ValueError) as exc:
        raise TokenError("Token is invalid or expired") from exc

    if payload.get("type") != expected_type:
        raise TokenError("Token type is invalid")

    return payload
