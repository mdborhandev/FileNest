# FileNest — Coding Rules

**Version:** 0.2.0  
**Date:** 2026-09-20  
**Companion docs:** `prd.md`, `design.md`, `tasks.md`, `ANALYSIS.md`

These rules are mandatory for all code in this project. They are enforced by tooling (§19) — a rule that a tool cannot check is a review-time rule and is marked **[review]**.

**What changed from 0.1.0:** contradictions removed (quote style, line length, "tokens aren't sensitive", "delegate to workers"), a broken docstring example fixed, new sections for file/PDF handling, logging, ownership checks and Definition of Done, and a ready-to-paste `pyproject.toml`.

---

## 1. Language and Runtime

- **Python 3.12+**; use modern syntax (`X | None`, `match`, `type` aliases, f-strings).
- All code must pass `ruff check`, `ruff format --check` and `mypy` (configured in §19). CI blocks merges on failure.

---

## 2. Import Order

Three groups separated by a blank line: standard library → third-party → local (`app.*`). Sorted alphabetically inside each group. Ruff's isort rules enforce this (`known-first-party = ["app"]`).

```python
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import Depends, HTTPException
from sqlalchemy import select

from app.core.config import settings
from app.services.users import get_user_by_id
```

- No wildcard imports. No imports inside functions except to break a genuine circular import (comment why).

---

## 3. Type Hints

- **Every** parameter and return type is annotated (except `self`/`cls`). `-> None` is written explicitly.
- Use built-in generics and `collections.abc`: `list[str]`, `dict[str, int]`, `Sequence`, `Mapping`, `Iterable`.
- Use `Annotated[...]` for FastAPI dependencies (see `app/api/deps.py`).
- Use `AsyncGenerator[T, None]` for async generators.
- No bare `Any` without a `# reason:` comment. Prefer `Protocol` / `TypedDict` over `dict[str, Any]` for structured data.

```python
# Do
async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None: ...

CurrentUser = Annotated[User, Depends(get_current_user)]

# Don't
async def get_user_by_id(db, user_id): ...     # missing hints
```

---

## 4. Strings and Quotes

- **Python:** double quotes everywhere (`"..."`), including dict keys — this is what `ruff format` produces, so there is nothing to argue about. Single quotes only when the string itself contains a double quote and escaping would hurt readability (ruff does this automatically).
- **Regular expressions:** raw strings `r"..."`.
- **HTML/templates:** double quotes in attributes.
- **Logging:** use lazy `%s` formatting (`logger.info("Created %s", user_id)`), not f-strings.

---

## 5. Formatting

- PEP 8, 4-space indentation, **maximum line length 88** (single value; no "or 100").
- `ruff format` is the formatter of record — never hand-format against it.
- Trailing commas in multi-line collections and calls (Ruff `COM`/formatter "magic trailing comma").
- One blank line between methods, two between top-level definitions.

---

## 6. Docstrings

- **Modules:** one-line description at the top.
- **Public functions/classes:** Google-style docstring — summary line, then `Args`, `Returns`, `Raises` as applicable.
- **Private functions:** a brief docstring if the logic is not obvious. **[review]**
- Comments explain *why*, not *what*.

```python
async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> User:
    """Verify credentials and return the matching user.

    Args:
        db: Active database session.
        email: Email address supplied by the client (case-insensitive).
        password: Plaintext password supplied by the client.

    Returns:
        The authenticated ``User``.

    Raises:
        InvalidCredentialsError: If the email or password is incorrect, or the
            user is inactive. The message never says which one.
    """
```

*(0.1.0 showed this function as synchronous with an `AsyncSession` — it must be `async`.)*

---

## 7. Error Handling

### 7.1 Domain exceptions

Business errors live in `app/core/exceptions.py`. Each has a stable machine `code` and a default message; services **raise** them, services never import FastAPI.

```python
class AppError(Exception):
    code: str = "APP_ERROR"

class InvalidCredentialsError(AppError):
    code = "INVALID_CREDENTIALS"

class FileTooLargeError(AppError):
    code = "FILE_TOO_LARGE"
```

Required PDF/file errors: `UnsupportedMediaTypeError`, `FileTooLargeError`, `InvalidPdfError`, `EncryptedPdfError`, `TooManyPagesError`, `InvalidRangeError`, `ProcessingTimeoutError`, `QuotaExceededError`.

### 7.2 Mapping to HTTP

Register **one** exception handler that maps `AppError` subclasses to `(status, code, detail)` using a table (see PRD §6.3). Route handlers do not repeat `try/except` blocks unless they need to do something special.

```python
# app/main.py (sketch)
@app.exception_handler(AppError)
async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    status_code = STATUS_BY_ERROR.get(type(exc), status.HTTP_400_BAD_REQUEST)
    return JSONResponse(
        status_code=status_code,
        content={"detail": str(exc), "code": exc.code},
    )
```

If a route does map locally, chain the cause: `raise HTTPException(...) from exc`.

### 7.3 Database sessions

Roll back on exception; the session dependency owns the transaction boundary.

```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
```

### 7.4 Never swallow errors

```python
# Don't
try:
    something()
except:            # bare except — also flagged by ruff
    pass

# Do
try:
    something()
except SomeError as exc:
    logger.warning("Something failed: %s", exc)
    raise
```

Use `logger.exception(...)` when logging inside an `except` block that does not re-raise. Convert third-party library errors (pypdf, Pillow) into domain errors at the service boundary — never let library exception text reach the client.

---

## 8. Async Patterns

- `async/await` throughout; **never** call blocking functions in async code (`time.sleep`, `requests`, synchronous file or PDF-library calls).
- **CPU-bound or blocking work** (PDF parsing, rendering, image processing, hashing large files): `await asyncio.to_thread(func, ...)`, wrapped by the shared `run_pdf_job()` helper that adds a concurrency semaphore and a timeout (`PROCESS_TIMEOUT_SECONDS`).
- MVP has no background workers (PRD D1), so "offload" means `to_thread` today and Celery in Milestone 8. Keep service functions pure (paths/bytes in → paths/bytes out, no FastAPI, no `Request`) so they move to Celery unchanged.
- Use `AsyncSession` for all DB work; never mix sync engines into request paths.
- Do not create fire-and-forget tasks without keeping a reference and handling exceptions (`asyncio.create_task` + `add_done_callback`) — use the lifespan-managed cleanup loop as the template.
- Use `async with`/`try/finally` so temp files and locks are released on cancellation.

---

## 9. SQLAlchemy Rules

- SQLAlchemy 2.x style: `select()`, `await session.execute()`, `.scalar_one_or_none()`, `session.get()`. **Never** `session.query()`.
- Models use `Mapped[T]` and `mapped_column()`.
- `async_sessionmaker(..., expire_on_commit=False)` for API use.
- `func.now()` / `server_default` for timestamps and boolean defaults — do not set them in Python.
- `ondelete="CASCADE"` on foreign keys that should cascade; **index** every foreign key and every column used in `WHERE`/`ORDER BY` (`expires_at`, `family_id`, `user_id`).
- Case-insensitive email uniqueness via a unique index on `lower(email)`.
- Raw SQL (`text()`) only for things the ORM cannot express; comment why. Never build SQL with string formatting.
- Migrations: one logical change per Alembic revision; run `alembic upgrade head` on an empty DB in CI; never edit a merged migration. `alembic/env.py` reads the URL from `app.core.config.settings` — **the URL in `alembic.ini` must not be relied on**.

```python
# Do
result = await db.execute(
    select(User).where(func.lower(User.email) == email.strip().lower())
)
user = result.scalar_one_or_none()

# Don't
result = await db.execute(text("SELECT * FROM users WHERE email = :email"))
```

---

## 10. Pydantic Rules

- Pydantic v2: `model_config = ConfigDict(...)`, `field_validator`, `Field(...)`. No v1 `validator`/`Config` classes.
- `from_attributes=True` on schemas read from ORM objects.
- Normalise in validators (trim, lowercase emails).
- `EmailStr` for emails; `Field(default=None, ...)` for optionals; explicit `min_length`/`max_length` on every string that comes from a client (password ≤ 128, full name ≤ 100).
- Request schemas forbid unknown fields where practical (`extra="forbid"`).
- Settings: `pydantic-settings`; secrets typed as `SecretStr` so they do not appear in `repr`.

```python
class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()
```

---

## 11. Security Rules

**Tokens and passwords**

- **Never** log or print tokens, passwords, reset links or `Authorization` headers.
- **Never** store plaintext refresh or reset tokens — store SHA-256 hashes; compare with `hmac.compare_digest` where comparing secrets.
- **Always** validate the `type` claim and `exp` when decoding; **always** set `exp`.
- Separate secrets for access and refresh tokens; secrets come from the environment.
- **Never** expose `hashed_password` — API responses use `UserRead`.
- Login, forgot-password and reset paths return uniform responses/timing so they do not reveal whether an email exists (PRD §7.2).
- Reset success **revokes all refresh-token families** for that user.

**Frontend token note:** `localStorage` tokens are *sensitive* — an XSS bug exposes them. That is why CSP, no inline JS and output encoding are mandatory (§15).

**Authorisation**

- **Every query for a user-owned resource filters by `user_id`** (or uses a helper that does). A resource you don't own returns `404`, not `403`. Each such endpoint has an ownership test (§16).

**Secrets and config**

- No secrets in code, docs, tests, logs, screenshots or `memory.md`. Use `.env` locally; `.env.example` has placeholders only.
- Secret scanning runs in pre-commit and CI (§19).
- **HTTPS only** in production; CORS origins come from configuration and are never `*` with credentials.

**Logging**

- Use `logging` (not `print` — ruff `T20`). Structured logs with a request ID. Log events (`login_failed`, `tool_run`) with IDs, never payloads or PII.

---

## 12. API Design Rules

- REST: nouns for resources, verbs via HTTP methods; prefix `/api/v1`; tag routes (`tags=["auth"]`, `["files"]`, `["pdf"]`, `["health"]`).
- JSON everywhere except multipart upload and file download. `response_model` on every endpoint that returns data.
- Status codes:

| Code | Use |
| --- | --- |
| 200 | Successful GET/update/tool run (MVP synchronous) |
| 201 | Resource created (register, upload) |
| 202 | Accepted for background processing (forgot-password; jobs in M8) |
| 204 | Successful DELETE/logout/reset with no body |
| 400 | Malformed request not caught by validation |
| 401 | Missing/invalid authentication or credentials |
| 403 | Authenticated but forbidden (rare — prefer 404 for other users' resources) |
| 404 | Not found **or not owned** |
| 409 | Duplicate resource |
| 413 | Payload too large |
| 415 | Unsupported media type |
| 422 | Validation failure (FastAPI) or semantically invalid PDF/options |
| 429 | Rate limited (include `Retry-After`) |
| 503 | Dependency down |
| 504 | Processing timeout |

- Error body: `{"detail": "...", "code": "MACHINE_CODE"}` (§7.2). Never include stack traces or library messages.
- Downloads: `Content-Disposition: attachment; filename*=UTF-8''<sanitised>`, `X-Content-Type-Options: nosniff`.
- Uploads: stream to disk with an enforced size cap; never read a whole upload into memory.
- Pagination on list endpoints (`limit` ≤ 100).

---

## 13. Model and Schema Rules

- Models in `app/models/` (SQLAlchemy); schemas in `app/schemas/` (Pydantic). **Never** return a model directly from a route.
- `TimestampMixin` on every model needing `created_at`/`updated_at`.
- `__table_args__` for composite/unique constraints and indexes.
- One model per file, `snake_case.py`; one schema module per resource or tool.
- Storage keys and identifiers exposed to clients are UUIDs, not sequential integers, for user-visible resources (files/jobs).

---

## 14. File and PDF Handling Rules (new)

1. **Filenames:** never use a client-supplied name in any filesystem path. Store by server-generated key (`uuid4().hex`), keep the sanitised original as display metadata. Reject or strip path separators, control characters, and leading dots in display names.
2. **Type detection:** determine type from magic bytes (`%PDF-`, PNG `89 50 4E 47`, JPEG `FF D8 FF`) — never from the extension or `Content-Type` header.
3. **Size:** enforce while streaming (abort early). Limits come from `settings` (PRD §7.3), never literals in code.
4. **Untrusted parsing:** wrap every library call in try/except → domain errors; enforce page-count and pixel-count limits **before** rendering/processing; detect encrypted PDFs and reject with `EncryptedPdfError`.
5. **No shell-outs** with user-derived arguments. If an external binary is ever added, use argument lists (never `shell=True`), fixed paths, timeouts, and a non-root sandbox — and get it reviewed.
6. **Temp files:** create with `tempfile`/the storage `tmp/` area, always cleaned in `finally`, including on timeout/cancel.
7. **Processing:** run through `run_pdf_job()` (semaphore + timeout + `to_thread`). Services take and return paths/bytes; they do not touch the DB or HTTP objects.
8. **Ownership & lifecycle:** every `PdfFile` has `user_id` and `expires_at`; cleanup deletes both DB row and file; delete storage first, then the row, and tolerate "already gone".
9. **Results:** never return a compressed file larger than its input; tools are idempotent for the same inputs.
10. **Licences:** do not add PyMuPDF/MuPDF, Ghostscript or other AGPL/GPL libraries without an explicit decision recorded in the PR (PRD D3).

---

## 15. Frontend Rules

- HTML in `app/static/`; CSS in `app/static/css/styles.css`; JS modules in `app/static/js/`. Absolute asset paths (`/static/...`).
- Keep JS modular: `api.js` (network) is separate from UI modules. **All API calls go through `FileNestAPI`.**
- **No inline `<script>`, no `onclick=`-style attributes, no inline styles that need `unsafe-inline`** — use `data-*` hooks. This is a CSP requirement.
- Untrusted text goes into the DOM via `textContent`/`setAttribute`; use `escapeHTML` only when constructing HTML strings. **[review]**
- Third-party scripts/fonts/CDNs are not allowed (privacy promise + CSP). Self-host anything needed.
- `localStorage` is used **only** for the two auth tokens (until the cookie migration) and holds nothing else. Tokens are treated as sensitive.
- Follow `design.md` tokens; no raw colour values in components. Meet the accessibility checklist in `design.md` §8.
- Validate redirect targets (`?next=`) — same-origin relative paths only.

---

## 16. Testing Rules

- All tests under `tests/`; `pytest-asyncio` with `asyncio_mode = auto` (in `pytest.ini`).
- Tests run against the separate `filenest_test` database; the DB is cleaned per test (`NullPool`, override of `get_db` as in `conftest.py`).
- Use `httpx.AsyncClient` with `ASGITransport` for API tests.
- **Test names:** `test_<action>_<scenario>` (e.g. `test_login_rejects_wrong_password`).
- **Fixtures:** generate PDFs/images programmatically (pypdf/ReportLab/Pillow helpers in `tests/factories.py`) instead of committing binary files, except tiny purpose-built malformed samples.
- **Every feature ships with tests in the same PR.** Required categories:
  - Happy path and validation edge cases.
  - Auth: unauthenticated → `401`; other user's resource → `404` (ownership/IDOR).
  - Files: wrong type by magic bytes, oversize, too many pages, encrypted, corrupt, path-traversal filename, expired file cleanup.
  - Tools: output correctness (page count/order/rotation), option validation, "never larger" for compress.
  - Sessions: rotation, reuse detection, and the multi-tab grace behaviour.
- Coverage targets: ≥ 85 % for `app/services`, ≥ 75 % overall (`pytest --cov=app`).
- Tests must be deterministic: freeze time (`time-machine`/`freezegun`) for expiry tests; no sleeps.

---

## 17. Git and Commit Rules

- Never commit `.env`, `.venv/`, `__pycache__/`, `*.pyc`, `storage/`, or any file containing a secret.
- Commit `requirements*.txt`, `alembic/versions/`, `.env.example` (placeholders only), `pyproject.toml`.
- Commit messages: Conventional Commits — `feat(pdf): add merge service`, `fix(auth): serialise refresh across tabs`, `docs: update PRD`. Explain *why* in the body when not obvious.
- Small, single-purpose PRs; update the relevant docs (`tasks.md`, `memory.md`, PRD/design) **in the same PR** as the code.
- If a secret is ever committed: rotate it first, then clean history.

---

## 18. Dependency Rules

- Do not add a dependency if an existing one can do the job. Record in the PR: what it is for, **its licence**, and maintenance status.
- Prefer stable, actively maintained, permissively licensed libraries (MIT/BSD/Apache/MPL). AGPL/GPL requires an explicit decision (PRD D3).
- Pin ranges (`fastapi>=0.116,<1.0`). Runtime deps in `requirements.txt`; test/lint/type tools in `requirements-dev.txt`.
- PDF libraries are added only in the PR that first uses them (see `tasks.md` M3/M4).
- `pip-audit` runs in CI; act on High findings promptly.

---

## 19. Tooling Configuration

Add to `pyproject.toml` (this did not exist in 0.1.0, so the rules were not actually enforceable):

```toml
[tool.ruff]
line-length = 88
target-version = "py312"
src = ["app", "tests"]

[tool.ruff.lint]
select = [
  "E", "W", "F",   # pycodestyle, pyflakes
  "I",             # import order
  "B",             # bugbear
  "UP",            # pyupgrade
  "ASYNC",         # async pitfalls (blocking calls in async)
  "S",             # security (bandit)
  "SIM", "C4",     # simplifications
  "PT",            # pytest style
  "T20",           # no print
  "RUF",
]

[tool.ruff.lint.isort]
known-first-party = ["app"]

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101", "S105", "S106"]   # assert and fake passwords are fine in tests

[tool.ruff.format]
quote-style = "double"

[tool.mypy]
python_version = "3.12"
strict = true
plugins = ["pydantic.mypy"]
exclude = ["alembic/versions/"]
```

`pre-commit` (`.pre-commit-config.yaml`): `ruff` (with `--fix`), `ruff-format`, `gitleaks`, trailing-whitespace/EOF fixers.

CI (GitHub Actions) on every PR: install → `ruff check` → `ruff format --check` → `mypy app` → `alembic upgrade head` on a Postgres service → `pytest --cov` → `pip-audit`.

---

## 20. Naming Conventions

- Python files/modules: `snake_case.py` (`auth.py`, `pdf_merge.py`); classes `PascalCase`; functions/variables `snake_case`; constants `UPPER_SNAKE`.
- Models: `PascalCase` class, `snake_case` filename (`refresh_token.py`).
- Schemas: `PascalCase` with role suffix — `UserCreate`, `UserRead`, `MergeRequest`, `ToolResult`.
- Routes: plural nouns for resources (`/files`), verbs only for actions on tools (`/pdf/merge`).
- Tests: `test_*.py`, functions `test_<action>_<scenario>`.
- Migrations: `alembic/versions/<hash>_<name>.py` with a descriptive message (`add_pdf_files`).
- Static assets: lowercase with proper extensions; CSS classes are kebab-case (`.file-row`); JS hooks use `data-*`.
- Environment variables: `UPPER_SNAKE`, grouped by prefix (`JWT_…`, `MAX_…`, `FILE_…`).

---

## 21. Definition of Done

A task is done only when **all** apply:

- [ ] Behaviour matches the acceptance criteria in `prd.md`/`tasks.md`.
- [ ] Tests added/updated and passing locally and in CI (including ownership/edge cases).
- [ ] `ruff check`, `ruff format --check`, `mypy` clean.
- [ ] No secrets, tokens or PII in code, logs, tests or docs.
- [ ] New settings documented in `.env.example`; migrations included and reversible (or noted).
- [ ] UI changes pass the accessibility checklist (`design.md` §8).
- [ ] `tasks.md` status updated and, if a decision changed, `memory.md` / `prd.md` updated in the same PR.

---

## 22. Changing These Rules

Rules can be changed — but by editing this file in a PR that states the reason and updates tooling config to match. Do not silently violate a rule; if an exception is needed, add a one-line comment explaining it (`# rules: <section> exception — <reason>`).
