# FileNest — Project Architecture

**Version:** 0.1.0  
**Date:** 2026-09-20

---

## 1. System Architecture

```
┌──────────────┐       ┌──────────────────┐       ┌──────────────┐
│   Frontend    │──────▶│   FastAPI App     │──────▶│  PostgreSQL  │
│  (HTML/JS)    │◀──────│  (Python 3.12)    │◀──────│  (filenest)  │
└──────────────┘       └────────┬─────────┘       └──────────────┘
                                │
                     ┌──────────┴──────────┐
                     │                     │
                     ▼                     ▼
              ┌────────────┐      ┌─────────────┐
              │  Redis     │      │  Storage     │
              │  (Celery   │      │  (filesystem │
              │   broker)  │      │   uploads/   │
              └────────────┘      │   processed/ │
                                  │   temp/      │
                                  └──────────────┘
```

### Layer Diagram

```
┌──────────────────────────────────────────────────────────┐
│  Presentation Layer                                       │
│  ├── Static HTML (index.html, login.html, register.html)  │
│  ├── CSS (styles.css)                                     │
│  └── JavaScript (api.js, auth-forms.js, main.js)          │
├──────────────────────────────────────────────────────────┤
│  API Layer (FastAPI)                                      │
│  ├── app/main.py          — Application factory, lifespan │
│  ├── app/api/v1/router.py — Router registration            │
│  ├── app/api/deps.py      — Shared dependencies            │
│  ├── routes/health.py     — Health check                  │
│  └── routes/auth.py       — Auth endpoints                │
├──────────────────────────────────────────────────────────┤
│  Service Layer (Business Logic)                           │
│  ├── services/auth.py      — Login, tokens, refresh       │
│  ├── services/users.py     — User CRUD                    │
│  ├── services/passwords.py — Hashing & verification       │
│  └── (services/pdf_*.py — planned)                        │
├──────────────────────────────────────────────────────────┤
│  Data Access Layer                                        │
│  ├── app/core/database.py  — Async engine & session       │
│  ├── app/models/*.py       — SQLAlchemy ORM models        │
│  ├── app/schemas/*.py      — Pydantic validation          │
│  └── alembic/              — Database migrations          │
├──────────────────────────────────────────────────────────┤
│  Infrastructure Layer                                     │
│  ├── app/core/config.py    — Settings (pydantic-settings) │
│  ├── app/core/security.py  — JWT token lifecycle          │
│  ├── app/core/exceptions.py— Domain exceptions            │
│  ├── app/workers/celery_app.py — Celery configuration     │
│  └── app/workers/tasks.py  — Background tasks             │
└──────────────────────────────────────────────────────────┘
```

---

## 2. Technology Stack

| Component | Technology | Purpose |
| --- | --- | --- |
| Language | Python 3.12 | Backend runtime |
| Framework | FastAPI | Web framework, async support |
| ORM | SQLAlchemy 2.x (async) | Database abstraction |
| Database | PostgreSQL 14+ | Persistent storage |
| Driver | asyncpg | Async PostgreSQL driver |
| Migrations | Alembic | Schema versioning |
| Validation | Pydantic v2 | Request/response validation |
| Settings | pydantic-settings | Environment configuration |
| Auth | PyJWT, pwdlib[argon2] | Token management, password hashing |
| Email | Email-validator | Input validation |
| Background | Celery + Redis | Async job processing |
| Testing | pytest, pytest-asyncio, httpx | Test suite |
| Frontend | HTML5, CSS3, Vanilla JS | Server-rendered pages |

---

## 3. Request Lifecycle

### Example: Authenticated Request (`GET /api/v1/auth/me`)

```
Browser                         FastAPI App                    Database
   │                                │                             │
   │── GET /api/v1/auth/me ───────▶│                             │
   │   Authorization: Bearer <tok>  │                             │
   │                                │                             │
   │                                │── decode JWT (security.py)  │
   │                                │                             │
   │                                │── get_current_user (deps)   │
   │                                │   │                         │
   │                                │   ▼                         │
   │                                │── SELECT user WHERE id=?    │
   │                                │◀── user row                 │
   │                                │                             │
   │                                │── serialize (UserRead)      │
   │                                │                             │
   │◀── 200 OK (UserRead) ─────────│                             │
```

### Example: Unauthenticated Request (`POST /api/v1/auth/login`)

```
Browser                         FastAPI App                    Database
   │                                │                             │
   │── POST /api/v1/auth/login ───▶│                             │
   │   {email, password}           │                             │
   │                                │                             │
   │                                │── validate credentials      │
   │                                │   │                         │
   │                                │   ▼                         │
   │                                │── SELECT user WHERE email=? │
   │                                │◀── user row                 │
   │                                │                             │
   │                                │── verify password           │
   │                                │                             │
   │                                │── create access+refresh     │
   │                                │── persist refresh token     │
   │                                │   │                         │
   │                                │   ▼                         │
   │                                │── INSERT refresh_tokens     │
   │                                │◀── OK                       │
   │                                │                             │
   │◀── 200 OK (TokenPair) ────────│                             │
```

---

## 4. Component Details

### 4.1 Application Factory (`app/main.py`)

- FastAPI app created with `lifespan` context manager
- CORS middleware: origins from `settings.cors_origins`, all methods/headers allowed
- API router mounted at `/api/v1` prefix
- Static files mounted at `/static`
- Routes `/`, `/login`, `/register` serve server-rendered HTML pages
- On shutdown: `dispose_db()` closes the connection pool

### 4.2 Configuration (`app/core/config.py`)

- `Settings` class extends `BaseSettings` (pydantic-settings)
- Loads from `.env` file (UTF-8, case-insensitive keys)
- `extra="ignore"` — unknown env vars are silently dropped
- All secrets default to dev placeholders; must be overridden via `.env`

### 4.3 Database Layer (`app/core/database.py`)

- `create_async_engine()` with connection pooling
  - `pool_size=5`, `max_overflow=10`
  - `pool_pre_ping=True` — checks connections before reuse
- `AsyncSessionLocal` — session factory with `expire_on_commit=False`
- `get_db()` — async dependency injection for route handlers
- `dispose_db()` — called on app shutdown

### 4.4 Security Layer (`app/core/security.py`)

- `create_token(user_id, token_type, expires_delta)` — generic token creator
- `create_access_token(user_id)` — access token (30 min)
- `create_refresh_token(user_id)` — refresh token (7 days)
- `decode_token(token, expected_type)` — validates and decodes JWT
- Tokens contain: `sub` (user ID), `type` (access/refresh), `iat`, `exp`, `jti` (unique ID)
- Separate secrets for access and refresh tokens (`jwt_secret_key`, `jwt_refresh_secret_key`)

### 4.5 Authentication Service (`app/services/auth.py`)

- `authenticate_user()` — verifies email/password
- `issue_token_pair()` — creates tokens + persists refresh token in DB
- `rotate_refresh_token()` — validates old refresh token, revokes it, issues new pair
  - On reuse (already revoked): revokes **entire family**
  - Same `family_id` groups all tokens from one login session
- `revoke_refresh_token()` — revokes single token's family
- `revoke_token_family()` — marks all tokens in family as revoked
- Refresh tokens stored as SHA-256 hashes (never plaintext)

### 4.6 User Service (`app/services/users.py`)

- `get_user_by_email()` — case-insensitive lookup
- `get_user_by_id()` — direct primary key lookup
- `create_user()` — creates user with hashed password, handles duplicate email (409)

### 4.7 Route Dependencies (`app/api/deps.py`)

- `get_current_user()` — HTTP Bearer token → decode → lookup user → return User
- Raises `401 Unauthorized` for missing, invalid, expired tokens or inactive users

### 4.8 Models (`app/models/`)

All models extend `Base` (DeclarativeBase) and optionally `TimestampMixin`:

- **User** — core user data, email unique, soft-delete via `is_active`
- **RefreshToken** — persisted refresh sessions with family_id for rotation
- **PasswordReset** — one-time reset tokens with `used_at` tracking

### 4.9 Schemas (`app/schemas/`)

Pydantic v2 models for request/response validation:

- **UserCreate** — email, password (min 8 chars, not common), optional full_name
- **UserRead** — full user representation (from_attributes=True)
- **UserLogin** — email + password
- **TokenPair** — access_token, refresh_token, token_type="bearer"
- **HealthResponse** — status, version

### 4.10 Celery Workers (`app/workers/`)

- `celery_app.py` — Celery app configured with Redis broker/backend, UTC timezone
- `tasks.py` — `ping` task (example/health check); PDF tasks planned

---

## 5. Data Flow: PDF Tool (Planned Architecture)

```
User Upload
    │
    ▼
┌─────────────────┐
│ API Route        │  POST /api/v1/pdf/merge (auth required)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Service Layer    │  pdf_merge_service.merge(file_list)
│ (business logic) │  Validates inputs, orchestrates processing
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ PDF Libraries    │  PyMuPDF / pypdf / ReportLab
│ (processing)     │  Pure Python processing, no framework deps
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Storage Service  │  Saves to storage/uploads/, storage/processed/
│ (abstraction)    │  Designed for future S3/MinIO swap
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Response         │  Returns download URL or file data
└─────────────────┘
```

---

## 6. Database Design

### Current Schema (from `alembic/versions/7697cdbf4561_init.py`)

**3 tables:** `users`, `refresh_tokens`, `password_resets`

Key relationships:
- `refresh_tokens.user_id` → `users.id` (CASCADE on delete)
- `password_resets.user_id` → `users.id` (CASCADE on delete)
- All tables use `TimestampMixin` (`created_at`, `updated_at` with `server_default=func.now()`)
- All timestamps use `DateTime(timezone=True)`

### Planned Schema Additions

**pdf_files** — file metadata per user  
**pdf_jobs** — processing job records with status, error messages, timestamps  
**subscriptions** (future) — user subscription plans

---

## 7. Environment Configuration

All configuration lives in `.env` (git-ignored) with `.env.example` as the template.

| Variable | Default | Description |
| --- | --- | --- |
| `DATABASE_URL` | `postgresql+asyncpg://...` | PostgreSQL connection string |
| `DATABASE_POOL_SIZE` | `5` | Connection pool size |
| `DATABASE_MAX_OVERFLOW` | `10` | Max overflow connections |
| `JWT_SECRET_KEY` | dev placeholder | Access token signing secret |
| `JWT_REFRESH_SECRET_KEY` | dev placeholder | Refresh token signing secret |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token TTL |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed CORS origins |
| `CELERY_BROKER_URL` | `redis://localhost:6379/0` | Redis broker URL |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/1` | Redis result backend |
| `DEBUG` | `False` | Debug mode (enables SQL logging) |

---

## 8. Testing Architecture

- **Test DB**: Separate database (`filenest_test`), specified via `TEST_DATABASE_URL` env var
- **Overrides**: `conftest.py` overrides `get_db` dependency with test database session
- **Isolation**: Each test runs with a clean database (drop all + create all before, drop after)
- **Connection**: `NullPool` for tests (no pooling overhead)
- **Client**: `httpx.AsyncClient` with `ASGITransport` (in-process, no HTTP needed)
- **Coverage**: Integration tests for auth API in `tests/test_auth.py`

---

## 9. Key Architectural Decisions

| Decision | Rationale |
| --- | --- |
| Async SQLAlchemy over sync | Non-blocking I/O, matches FastAPI's async nature |
| Refresh tokens persisted in DB | Enables rotation, revocation, and reuse detection |
| SHA-256 hash of refresh token stored | Token theft doesn't expose usable token |
| `family_id` UUID on refresh tokens | Groups tokens from one login; replay revokes all |
| Server-rendered HTML for MVP | No React build step; works immediately |
| File storage on filesystem for MVP | Simpler than S3; easily swappable later |
| Celery configured but not used in MVP | Avoids Redis dependency for MVP; ready when needed |
| Separate access/refresh secrets | Compromising one doesn't compromise both |
| Pydantic v2 `from_attributes` | Direct ORM-to-schema mapping without manual transforms |

---

## 10. Deployment Architecture (Planned)

```
┌─────────────┐     ┌─────────────┐
│  Nginx      │────▶│  FastAPI    │ (Docker container)
│  (reverse   │     │  (uvicorn)  │
│   proxy)    │◀────│             │
└─────────────┘     └──────┬──────┘
                           │
                     ┌─────┴──────┐
                     │ PostgreSQL  │
                     └────────────┘
                           │
                     ┌─────┴──────┐
                     │  Redis      │ (Celery broker + backend)
                     └────────────┘
                           │
                     ┌─────┴──────┐
                     │ Celery      │ (worker containers)
                     │ Workers     │
                     └────────────┘
```
