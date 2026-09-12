from datetime import datetime
from typing import ClassVar, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = Field(default=None, max_length=100)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()

    @field_validator("full_name")
    @classmethod
    def normalize_full_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = " ".join(value.split())
        return normalized or None


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)

    _common_passwords: ClassVar[frozenset[str]] = frozenset(
        {
            "password",
            "password123",
            "12345678",
            "123456789",
            "1234567890",
            "qwertyui",
            "qwerty123",
            "letmein",
            "admin123",
            "welcome1",
            "password1",
        }
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        stripped = value.strip()
        if len(stripped) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if stripped.lower() in cls._common_passwords:
            raise ValueError("Password is too common, choose a stronger one")
        return value


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str
