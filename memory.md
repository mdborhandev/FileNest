# FileNest — Project Memory

**Auto-generated context for AI assistants working on this project.**

---

## Environment Details

- **Project root:** `/home/borhan-uddin-fahim/DRIVE A/Projects/FileNest`
- **Current time:** 2026-09-20T22:22:50+06:00
- **Platform:** Linux
- **Git repo:** Yes
- **Python version:** 3.12+
- **Virtual environment:** `.venv/` (already created and populated)
- **Dependencies installed:** Yes (from `requirements.txt`)

---

## What This Project Is

FileNest is a **PDF tools SaaS platform** backend built with FastAPI. It provides:
- User authentication (register, login, refresh, logout, password reset)
- JWT-based auth with refresh token rotation and reuse detection
- Database persistence (PostgreSQL via async SQLAlchemy)
- Background job infrastructure (Celery + Redis — configured but not actively used in MVP)
- Server-rendered frontend (HTML/CSS/JS landing, login, register pages)

---

## Key File Locations

| What | Where |
| --- | --- |
| Application entry point | `app/main.py` |
| Configuration | `app/core/config.py` |
| Database engine/session | `app/core/database.py` |
| JWT security | `app/core/security.py` |
| Domain exceptions | `app/core/exceptions.py` |
| Auth routes | `app/api/v1/routes/auth.py` |
| Health route | `app/api/v1/routes/health.py` |
| API router | `app/api/v1/router.py` |
| Shared deps (current user) | `app/api/deps.py` |
| User model | `app/models/user.py` |
| Refresh token model | `app/models/refresh_token.py` |
| Password reset model | `app/models/password_reset.py` |
| User schemas | `app/schemas/user.py` |
| Auth service | `app/services/auth.py` |
| Password service | `app/services/passwords.py` |
| User service | `app/services/users.py` |
| Celery app | `app/workers/celery_app.py` |
| Tasks | `app/workers/tasks.py` |
| Static HTML | `app/static/index.html`, `login.html`, `register.html` |
| Static CSS | `app/static/css/styles.css` |
| Static JS | `app/static/js/api.js`, `auth-forms.js`, `main.js` |
| Migrations | `alembic/versions/` |
| Tests | `tests/conftest.py`, `tests/test_auth.py` |
| Environment | `.env`, `.env.example` |
| Requirements | `requirements.txt` |
| Project stack doc | `PROJECT_STACK.md` |
| Checklist | `CHECKLIST.md` |
| Product requirements | `prd.md` |
| Architecture | `architecture.md` |
| Coding rules | `rules.md` |
| UI/UX design | `design.md` |
| Tasks & progress | `tasks.md` |
| Project context (this file) | `memory.md` |

---

## Key Configuration

- **Database URL:** `postgresql+asyncpg://postgres:fahim123@localhost:5432/filenest_dev`
- **Test database:** `filenest_test` (auto-derived or via `TEST_DATABASE_URL`)
- **Redis:** `redis://localhost:6379/0` (broker), `redis://localhost:6379/1` (backend)
- **JWT access token expiry:** 30 minutes
- **JWT refresh token expiry:** 7 days
- **JWT algorithm:** HS256
- **CORS origins:** `["http://localhost:3000"]`
- **CORS:** Allows all methods and headers, credentials enabled

---

## How to Run

```bash
# Ensure virtual environment is active
source .venv/bin/activate

# Ensure PostgreSQL and Redis are running

# Run migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload

# Start the Celery worker (if needed)
celery -A app.workers.celery_app:celery_app worker --logloglevel=info

# Run tests
TEST_DATABASE_URL="postgresql+asyncpg://postgres:fahim123@localhost:5432/filenest_test" pytest
```

---

## Architecture Decisions (Important)

1. **Async everywhere** — SQLAlchemy async, FastAPI async, async session factory. Never use sync DB calls in routes.
2. **Server-rendered frontend for MVP** — Static HTML/JS served by FastAPI. React frontend planned for future.
3. **PDF processing independent from API** — Service layer pattern, designed for future Celery migration.
4. **File storage on filesystem for MVP** — Not in DB. Abstracted for future S3/MinIO.
5. **Celery configured but not required for MVP** — Redis dependency deferred. Workers configured and ping task exists.
6. **Separate access/refresh secrets** — Compromising one doesn't compromise both.
7. **Refresh tokens hashed (SHA-256) in DB** — Never stored in plaintext.
8. **Refresh token family rotation** — Tokens from one login share a `family_id`. Reuse revokes entire family.
9. **Models ≠ Schemas** — SQLAlchemy models in `app/models/`, Pydantic schemas in `app/schemas/`. Always use schemas for API responses.
10. **`get_db` dependency override in tests** — `conftest.py` uses `TestSessionLocal` with `NullPool` and clean DB per test.

---

## Known Gaps (Not Yet Implemented)

- PDF processing services and routes (PDF merge, split, compress, rotate, convert)
- File upload/download endpoints
- `PdfFile` model, schema, and migration
- `PdfJob` model and schema
- Frontend React app
- Rate limiting
- File type/size validation
- Request logging/audit
- Docker/CI/CD
- Email sending service for password reset
- `PdfFile` model, schema, and migration
- User dashboard

---

## Dependencies (requirements.txt)

- `fastapi>=0.116,<1.0` — Web framework
- `uvicorn[standard]>=0.35,<1.0` — ASGI server
- `SQLAlchemy>=2.0,<3.0` — ORM
- `asyncpg>=0.30,<1.0` — PostgreSQL driver
- `alembic>=1.15,<2.0` — Migrations
- `pydantic>=2.11,<3.0` — Validation
- `pydantic-settings>=2.9,<3.0` — Settings
- `python-dotenv>=1.0,<2.0` — Env loading
- `PyJWT>=2.10,<3.0` — JWT tokens
- `pwdlib[argon2]>=0.3,<0.4` — Password hashing
- `email-validator>=2.2,<3.0` — Email validation
- `celery[redis]>=5.5,<6.0` — Background jobs
- `redis>=5.2,<6.0` — Redis client
- `pytest>=8.3,<9.0` — Testing
- `pytest-asyncio>=0.24,<1.0` — Async tests
- `httpx>=0.27,<1.0` — HTTP client for tests

---

## Linting

- `ruff` is used (`.ruff_cache/` exists with version `0.16.7`)
- No `pyproject.toml`, `ruff.toml`, or `.mypy.ini` found — linting config may be IDE-only or default
- `.mypy_cache/` exists — mypy has been run but config not in repo

---

## Database Details

- **Development DB:** `filenest_dev` on `localhost:5432`
- **Test DB:** `filenest_test` on `localhost:5432`
- **User:** `postgres` (dev), password in `.env`
- **Driver:** `asyncpg` (async)
- **Tables:** `users`, `refresh_tokens`, `password_resets` (current)
- **Migration tool:** Alembic with `alembic/versions/7697cdbf4561_init.py` as head
- **Migration config:** `alembic.ini` has hardcoded `sqlalchemy.url = postgresql+asyncpg://filenest:filenest@localhost:5432/filenest` (note: this differs from app config)

---

## Frontend Token Flow

1. Tokens stored in `localStorage` as `filenest_access_token` and `filenest_refresh_token`
2. `apiFetch` automatically attaches access token to requests
3. On 401, `apiFetch` auto-refreshes via `POST /api/v1/auth/refresh`
4. If refresh fails, `filenest:logout` event dispatched, tokens cleared, redirect to `/login`
5. `main.js` renders auth state in nav from `FileNestAPI.me()` on page load
6. `auth-forms.js` handles login/register forms with client-side validation
