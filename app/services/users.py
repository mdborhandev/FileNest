from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UserAlreadyExistsError
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.passwords import hash_password


async def get_user_by_email(
    db: AsyncSession,
    email: str,
) -> User | None:
    result = await db.execute(
        select(User).where(func.lower(User.email) == email.strip().lower())
    )
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    return await db.get(User, user_id)


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    email = str(user_in.email).strip().lower()
    user = User(
        email=email,
        full_name=user_in.full_name,
        hashed_password=await hash_password(user_in.password),
    )
    db.add(user)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise UserAlreadyExistsError("A user with this email already exists") from exc
    await db.refresh(user)
    return user
