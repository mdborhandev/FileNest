# FileNest Backend

FastAPI backend base for FileNest, a PDF tools platform. The service uses asynchronous SQLAlchemy with PostgreSQL, Alembic migrations, JWT authentication, pydantic-settings, and a Celery worker backed by Redis.

## Quick Start

```bash
uvicorn app.main:app --reload
```

Press `Ctrl+C` to stop the server.

## Features

- Async FastAPI application with API versioning under `/api/v1`
- PostgreSQL persistence through SQLAlchemy 2.x async sessions
- Alembic migrations for the `users` and `refresh_tokens` tables
- User registration, login, access-token refresh, logout, and authenticated profile endpoint
- Password hashing with `pwdlib` Argon2 and password-strength validation
- JWT access and refresh tokens with persisted, rotating refresh sessions
- Refresh-token reuse detection: replaying a rotated token revokes the whole family
- Login tracking through `last_login_at`
- CORS configuration loaded from environment variables
- Database health check at `/api/v1/health`
- Celery application and task module configured for Redis
- Server-rendered frontend (landing, login, sign-up) served from FastAPI static files
- Pytest integration test suite for the auth API

## Stop the server

In the same terminal, press `Ctrl+C`.

If you don't have access to that terminal:

```bash
pgrep -f "uvicorn app.main:app" | xargs kill
```

## Project structure

```text
app/
  api/
    deps.py
    v1/
      routes/
        auth.py
        health.py
      router.py
  core/
    config.py
    database.py
    exceptions.py
    security.py
  models/
    base.py
    refresh_token.py
    user.py
  schemas/
    health.py
    user.py
  services/
    auth.py
    passwords.py
    users.py
  static/
    css/styles.css
    js/api.js
    js/auth-forms.js
    js/main.js
    index.html
    login.html
    register.html
  workers/
    celery_app.py
    tasks.py
  main.py
alembic/
  versions/
    0001_create_users.py
    0002_create_refresh_tokens.py
tests/
  conftest.py
  test_auth.py
.env.example
pytest.ini
requirements.txt
```

## Requirements

- Python 3.12+
- PostgreSQL 14+
- Redis 6+

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Copy the example environment file and replace the development secrets:

```bash
cp .env.example .env
```

Generate strong secrets for `JWT_SECRET_KEY` and `JWT_REFRESH_SECRET_KEY`. Keep the two values different and never commit `.env`.

Start PostgreSQL and Redis, create the database and role used by `DATABASE_URL`, then run migrations:

```bash
alembic upgrade head
```

## Run the API

```bash
uvicorn app.main:app --reload
```

The interactive API documentation is available at `http://localhost:8000/docs`.

## Run the worker

```bash
celery -A app.workers.celery_app:celery_app worker --loglevel=info
```

The sample task can be exercised from a Python shell:

```python
from app.workers.tasks import ping

ping.delay()
```

## API endpoints

| Method | Path | Authentication | Description |
| --- | --- | --- | --- |
| `GET` | `/api/v1/health` | No | Checks database connectivity |
| `POST` | `/api/v1/auth/register` | No | Creates a user |
| `POST` | `/api/v1/auth/login` | No | Returns an access and refresh token |
| `POST` | `/api/v1/auth/refresh` | No | Rotates a refresh token |
| `POST` | `/api/v1/auth/logout` | No | Revokes the refresh token and its family |
| `GET` | `/api/v1/auth/me` | Bearer token | Returns the current user |

## Frontend

The landing page, login and sign-up pages are static HTML/CSS/JS served by FastAPI (`app/static`). They call the API directly and store the JWT pair in `localStorage`; when an access token expires the client transparently refreshes it once and retries the request.

```text
/          → landing page
/login     → login form
/register  → sign-up form
/docs      → interactive API documentation
```

## Tests

```bash
pytest
```

Tests run against a separate database. Create it up front and point pytest at it:

```bash
createdb filenest_test
TEST_DATABASE_URL="postgresql+asyncpg://admin:Admin444@localhost:5433/filenest_test" pytest
```

Example registration and login requests:

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"change-me-123","full_name":"FileNest User"}'

curl -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"change-me-123"}'
```

Use the returned `access_token` as:

```text
Authorization: Bearer <access_token>
```

## Configuration

All runtime settings are defined in `app/core/config.py` and can be overridden through `.env` or environment variables. Important values include:

- `DATABASE_URL`: async SQLAlchemy database URL
- `JWT_SECRET_KEY`: access-token signing secret
- `JWT_REFRESH_SECRET_KEY`: refresh-token signing secret
- `CORS_ORIGINS`: JSON array of allowed browser origins
- `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND`: Redis URLs

The checked-in defaults are intended for local development only. Use unique production secrets and restrict `CORS_ORIGINS` before deploying.
