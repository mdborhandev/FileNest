import hashlib
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import InvalidCredentialsError, TokenError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.user import TokenPair
from app.services.passwords import verify_password
from app.services.users import get_user_by_email, get_user_by_id


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


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


def _persist_token(
    db: AsyncSession,
    user: User,
    refresh_token: str,
    family_id: UUID,
) -> None:
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(refresh_token),
            family_id=family_id,
            expires_at=_utcnow() + timedelta(days=settings.refresh_token_expire_days),
        )
    )


async def issue_token_pair(
    db: AsyncSession,
    user: User,
    *,
    family_id: UUID | None = None,
    update_last_login: bool = False,
) -> TokenPair:
    token_pair = create_token_pair(user)
    _persist_token(db, user, token_pair.refresh_token, family_id or uuid4())
    if update_last_login:
        user.last_login_at = _utcnow()
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

    stored = await db.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == hash_refresh_token(token))
    )

    if stored is None:
        raise TokenError("Invalid or expired refresh token")

    if stored.revoked_at is not None:
        await revoke_token_family(db, stored.family_id)
        raise TokenError("Invalid or expired refresh token")

    if stored.expires_at <= _utcnow():
        stored.revoked_at = _utcnow()
        await db.commit()
        raise TokenError("Invalid or expired refresh token")

    user = await get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        raise TokenError("Invalid or expired refresh token")

    stored.revoked_at = _utcnow()
    return await issue_token_pair(db, user, family_id=stored.family_id)


async def revoke_token_family(db: AsyncSession, family_id: UUID) -> None:
    await db.execute(
        update(RefreshToken)
        .where(RefreshToken.family_id == family_id)
        .where(RefreshToken.revoked_at.is_(None))
        .values(revoked_at=_utcnow())
    )
    await db.commit()


async def revoke_refresh_token(db: AsyncSession, token: str) -> bool:
    stored = await db.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == hash_refresh_token(token))
    )
    if stored is None:
        return False
    await revoke_token_family(db, stored.family_id)
    return True
