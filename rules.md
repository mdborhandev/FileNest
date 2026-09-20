# FileNest — Coding Rules

These rules are mandatory for all code in this project. Violations will be caught by CI and code review.

---

## 1. Language & Runtime

- **Python 3.12+** — use modern syntax (type hints, `| None`, `match`, etc.)
- All source files must pass `ruff` linting and `mypy` type checking (if configured)

---

## 2. Import Order

Follow this order, separated by blank lines:

1. Standard library imports
2. Third-party imports
3. Local application imports (`app.*`)

Within each group, sort alphabetically by module name.

```python
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import Depends, HTTPException
from sqlalchemy import select

from app.core.config import settings
from app.services.users import get_user_by_id
```

---

## 3. Type Hints

- **Every function parameter must be type-hinted** (no untyped params except `self`/`cls`)
- **Every function return type must be type-hinted**
- Use `from __future__ import annotations` is **not** required (Python 3.12)
- Use `Annotated[...]` for FastAPI `Depends()` patterns (see `app/api/deps.py`)
- Use `AsyncGenerator[T, None]` for async generators
- Use `Sequence`, `Mapping`, `list`, `dict`, `set` from `collections.abc` where appropriate

### Do

```python
async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    ...

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    ...
```

### Don't

```python
async def get_user_by_id(db, user_id):  # missing type hints
    ...
```

---

## 4. String Quotes

- **Python code**: double quotes `"..."` for strings, single quotes `'...'` for characters and dict keys
- **Templates/HTML**: double quotes in attributes
- **Regular expressions**: raw strings `r"..."`

---

## 5. Formatting

- Follow **PEP 8** with 4-space indentation
- Max line length: **88 characters** (or 100 if configured in project linter)
- Use `ruff format` for automatic formatting (if configured)
- Trailing commas in multi-line collections (enforce with ruff)

---

## 6. Docstrings

- **Public functions/classes**: docstring with description, params, returns, raises
- **Private functions**: brief docstring if logic is non-obvious
- **Modules**: one-line description at the top

### Style

```python
def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> User:
    """Verify credentials and return the user.

    Raises:
        InvalidCredentialsError: If email or password is incorrect.

    Returns:
        The authenticated User object.
    """
```

---

## 7. Error Handling

### Domain Exceptions

Use `app/core/exceptions.py` for business logic errors:

```python
from app.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError

raise InvalidCredentialsError("Incorrect email or password")
```

### HTTP Exceptions

Map domain errors to HTTP exceptions in route handlers:

```python
except UserAlreadyExistsError as exc:
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=str(exc),
    ) from exc
```

### Database Sessions

Always rollback on exception in `get_db()`:

```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
```

### Never swallow exceptions silently

```python
# Don't
try:
    something()
except:
    pass

# Do
except SomeError as exc:
    logger.warning("Something failed: %s", exc)
    raise
```

---

## 8. Async Patterns

- Use `async/await` throughout — never use `time.sleep()` in async code (use `asyncio.sleep`)
- CPU-bound work in async context: use `await asyncio.to_thread()`
- Use `AsyncSession` for all database operations
- Use `select()` from `sqlalchemy` for queries, not `execute()` text strings for ORM operations
- Avoid blocking I/O in route handlers — delegate to background workers

---

## 9. SQLAlchemy Rules

- Use SQLAlchemy 2.x style: `select()`, `session.execute()`, `scalar()`, `get()`
- Never use `session.query()` (legacy)
- Use `mapped_column()` and `Mapped[T]` type annotations in models
- Use `async_sessionmaker` with `expire_on_commit=False` for API use cases
- Use `func.now()` for server-side timestamps (don't set in Python)
- Use `server_default` for boolean defaults (`true()`, `false()`)
- Use `ondelete="CASCADE"` on ForeignKeys that should cascade

### Do

```python
result = await db.execute(
    select(User).where(func.lower(User.email) == email.strip().lower())
)
user = result.scalar_one_or_none()
```

### Don't

```python
result = await db.execute(text("SELECT * FROM users WHERE email = :email"))  # raw SQL when ORM suffices
```

---

## 10. Pydantic Rules

- Use Pydantic v2 style (`model_config = ConfigDict(...)`, `field_validator`, `Field(...)`)
- Use `from_attributes=True` for schemas that read from ORM models
- Normalize data in validators (trim, lowercase emails)
- Use `EmailStr` for email fields
- Use `Field(default=None, ...)` for optional fields
- Use `field_validator` (not `validator`)

### Do

```python
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_active: bool

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()
```

### Don't

```python
# Legacy Pydantic v1 style
validator = ...
fields = ...
```

---

## 11. JWT & Security Rules

- **Never** log or print tokens
- **Never** store plaintext refresh tokens in the database (hash before storing)
- **Always** validate `type` claim when decoding tokens
- **Always** use separate secrets for access and refresh tokens
- **Always** use HTTPS in production
- **Never** expose `hashed_password` in API responses (use `UserRead`, not raw model)
- **Always** set token expiration (`exp` claim)

---

## 12. API Design Rules

- Use REST conventions: nouns for resources, verbs in HTTP methods
- Prefix API routes with `/api/v1`
- Use consistent response formats (JSON)
- Return appropriate HTTP status codes:
  - `200 OK` — successful GET/update
  - `201 Created` — successful POST (resource creation)
  - `204 No Content` — successful DELETE/logout
  - `400 Bad Request` — validation errors (FastAPI handles automatically)
  - `401 Unauthorized` — missing/invalid auth
  - `409 Conflict` — duplicate resource
  - `422 Unprocessable Entity` — validation failure (auto)
  - `503 Service Unavailable` — dependency down (DB, etc.)
- Use `response_model` on all endpoints that return data
- Tag routes consistently (`tags=["auth"]`, `tags=["health"]`)
- Never commit `.env` to version control

---

## 13. Model & Schema Rules

- Models live in `app/models/`, schemas in `app/schemas/`
- **Models** = database representation (SQLAlchemy ORM)
- **Schemas** = API contracts (Pydantic)
- Never expose database models directly as API responses — always use schemas
- Use `TimestampMixin` for all models that need `created_at`/`updated_at`
- Use `__table_args__` for unique constraints
- Index foreign keys and frequently queried columns

---

## 14. Testing Rules

- All tests in `tests/` directory
- Use `pytest-asyncio` with `asyncio_mode = auto` (see `pytest.ini`)
- Tests run against a separate database (`filenest_test`)
- Clean database before/after each test session (see `conftest.py` pattern)
- Use `httpx.AsyncClient` with `ASGITransport` for integration tests
- Write tests for:
  - All auth flows (register, login, refresh, logout, me)
  - All CRUD operations
  - Edge cases (duplicate, unauthorized, invalid input)
  - PDF processing operations (when implemented)
- Test names: `test_<action>_<scenario>` (e.g., `test_login_rejects_wrong_password`)

---

## 15. Frontend Rules

- Static HTML files live in `app/static/`
- CSS in `app/static/css/styles.css`
- JavaScript modules in `app/static/js/`
- Keep JS modular (separate API layer from UI logic)
- Use `localStorage` only for tokens (not sensitive data)
- All API calls go through `FileNestAPI` object in `api.js`
- HTML pages link CSS and JS with absolute paths (`/static/...`)
- Use `data-*` attributes for JS hooks in HTML (avoid inline JS)

---

## 16. Commit Rules

- Never commit `.env`, `.venv/`, `__pycache__/`, or `*.pyc` files
- Commit `requirements.txt` and `alembic/` migrations
- Commit `.env.example` with placeholder values
- Write meaningful commit messages describing what and why

---

## 17. Dependency Rules

- **Never add a dependency** without checking if an existing one can solve the problem
- Prefer stable, actively maintained libraries
- Keep dependencies minimal (check `PROJECT_STACK.md`)
- Pin version ranges in `requirements.txt` (e.g., `fastapi>=0.116,<1.0`)
- Add PDF processing libraries only to `requirements.txt` when implementing

---

## 18. File Naming Conventions

- Python files: `snake_case.py` (e.g., `auth_service.py`)
- Python modules: lowercase (e.g., `main.py`, `config.py`)
- Models: `PascalCase` class names, `snake_case` filenames (`user.py`, `refresh_token.py`)
- Schemas: `PascalCase` class names (e.g., `UserRead`)
- Tests: `test_*.py` (e.g., `test_auth.py`)
- Migrations: `alembic/versions/<hash>_<name>.py`
- Static assets: `lowercase` with proper extensions (e.g., `styles.css`, `api.js`)
