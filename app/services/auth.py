import hashlib
import hmac

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidCredentialsError, TokenError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.user import User
from app.schemas.user import TokenPair
from app.services.passwords import verify_password
from app.services.users import get_user_by_email, get_user_by_id


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_token_pair(user: User) -> TokenPair:
    return TokenPair(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> User:
    user = await get_user_by_email(db, email)
    if user is None or not user.is_active:
        raise InvalidCredentialsError("Incorrect email or password")
    if not await verify_password(password, user.hashed_password):
        raise InvalidCredentialsError("Incorrect email or password")
    return user


async def issue_token_pair(
    db: AsyncSession,
    user: User,
) -> TokenPair:
    token_pair = create_token_pair(user)
    user.refresh_token_hash = hash_refresh_token(token_pair.refresh_token)
    await db.commit()
    return token_pair


async def rotate_refresh_token(
    db: AsyncSession,
    token: str,
) -> TokenPair:
    try:
        payload = decode_token(token, "refresh")
        user_id = int(payload["sub"])
    except (TokenError, ValueError, TypeError, KeyError) as exc:
        raise TokenError("Invalid or expired refresh token") from exc

    user = await get_user_by_id(db, user_id)
    stored_hash = user.refresh_token_hash if user is not None else None
    token_hash = hash_refresh_token(token)
    if (
        user is None
        or not user.is_active
        or stored_hash is None
        or not hmac.compare_digest(stored_hash, token_hash)
    ):
        raise TokenError("Invalid or expired refresh token")

    return await issue_token_pair(db, user)
