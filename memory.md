# FileNest — Project Memory

**Version:** 0.2.0 · **As of:** 2026-09-20  
**Audience:** AI assistants and new contributors. Read this first, then `rules.md` and the task you are given in `tasks.md`.

> **Sensitive-information policy.** This file must **never** contain passwords, tokens, API keys, connection strings with credentials, or personal paths. Use placeholders like `<user>`, `<password>`, `<project-root>`. (v0.1.0 contained the dev DB password twice — that password must be rotated; see `tasks.md` 2.01.)

**How to keep this file useful:** §1 is *volatile* (update it whenever a milestone changes); everything else is *stable* (change only when a decision changes). Update it in the same PR as the change.

---

## 1. Snapshot (volatile)

| Item | Value |
| --- | --- |
| Product version | 0.1.0 (auth MVP) — docs are at 0.2.0 |
| Milestone status | M1 Auth ✅ · M2 Hardening 🔄 (2.01–2.03 ✅) · M3 File infra ❌ · M4 PDF tools ❌ · M5 Web UI ❌ · M6 Security ❌ · M7 Release ❌ |
| MVP progress | 14 of 95 tasks (see `tasks.md` → Progress) |
| Current focus | **M2:** 2.06 cross-tab refresh lock → 2.04/2.05 lint + CI → 2.13 confirm D1–D6 |
| Blocked on decisions | D1–D6 confirmation (`ANALYSIS.md` §4); open questions Q1–Q6 (`prd.md` §14) |
| Not provided to the last review | `architecture.md`, `PROJECT_STACK.md`, `CHECKLIST.md` (may be stale vs D1–D6) |

---

## 2. What This Project Is

FileNest is an **iLovePDF-style PDF tools web app**: users register, upload PDFs/images, run a tool (merge, split, compress, rotate, PDF↔images), and download the result. Positioning: **files are deleted automatically after 60 minutes, no ads, honest limits.**

Today the repo contains a working **auth backend** and three static pages (landing, login, register). PDF processing, file storage and tool UI are **not built yet**.

---

## 3. Stack and Environment

| Item | Value |
| --- | --- |
| Language | Python 3.12+ |
| Web | FastAPI (async), served with uvicorn |
| DB | PostgreSQL 14+ via SQLAlchemy 2.x async + `asyncpg`; migrations with Alembic |
| Auth | PyJWT (HS256, separate access/refresh secrets), `pwdlib[argon2]` |
| Config | `pydantic-settings` reading `.env` |
| Frontend (MVP) | Server-rendered static HTML + vanilla JS + CSS tokens (`design.md`) |
| Background (post-MVP) | Celery + Redis — installed/configured, **not required or used by MVP** (D1) |
| PDF libs (planned, D3) | `pypdf`, `pypdfium2`, `Pillow`, `ReportLab` — **not yet installed**; avoid PyMuPDF/Ghostscript (AGPL) |
| Tests | pytest, pytest-asyncio, httpx |
| Quality | `ruff` and `mypy` (config to be added — task 2.04) |
| Platform | Linux; virtualenv at `<project-root>/.venv` (created, dependencies installed) |

---

## 4. Repository Map

**Existing**

```
app/
  main.py                    # app entry, lifespan, CORS, static mount
  core/{config,database,security,exceptions}.py
  api/deps.py                # current-user dependency (Annotated)
  api/v1/router.py
  api/v1/routes/{auth,health}.py
  models/{user,refresh_token,password_reset}.py
  schemas/user.py
  services/{auth,passwords,users}.py
  workers/{celery_app,tasks}.py          # ping task only
  static/{index,login,register}.html
  static/css/styles.css
  static/js/{api,auth-forms,main}.js
alembic/versions/7697cdbf4561_init.py, 7c8294d5dcf2_add_reset_token_and_refresh_token_.py    # 7c8294d5dcf2 is head
tests/{conftest,test_auth}.py
.env, .env.example, requirements.txt, alembic.ini, pytest.ini
docs: prd.md design.md rules.md tasks.md memory.md ANALYSIS.md (+ architecture.md, PROJECT_STACK.md, CHECKLIST.md, README.md)
```

**Planned (see `tasks.md`)**

```
app/services/{storage,file_validation,pdf_jobs,email,pdf_merge,pdf_split,pdf_compress,
              pdf_rotate,pdf_to_images,images_to_pdf,page_ranges}.py
app/models/pdf_file.py            app/schemas/{pdf_file,tool_result,pdf_*}.py
app/api/v1/routes/{files,pdf}.py
app/static/{forgot-password,reset-password,dashboard}.html + tools/*.html
app/static/js/{tool,dropzone,messages}.js
storage/{uploads,results,tmp}/    # git-ignored
pyproject.toml  requirements-dev.txt  .pre-commit-config.yaml  .github/workflows/ci.yml
```

---

## 5. Configuration (names and non-secret defaults only)

| Setting | Value / default | Notes |
| --- | --- | --- |
| `DATABASE_URL` | `postgresql+asyncpg://<user>:<password>@localhost:5432/filenest_dev` | Secret — from `.env` |
| `TEST_DATABASE_URL` | `postgresql+asyncpg://<user>:<password>@localhost:5432/filenest_test` | Optional; derived from the dev URL if unset |
| Redis (post-MVP) | `redis://localhost:6379/0` broker, `/1` result backend | Not needed for MVP |
| JWT access / refresh secrets | *(in `.env`, two different values)* | Never reuse one for both |
| Access token TTL | 30 min | |
| Refresh token TTL | 7 days | |
| JWT algorithm | HS256 | |
| CORS origins | `["http://localhost:3000"]` | Static pages are same-origin; this matters for a future dev server |
| Limits (planned) | `MAX_UPLOAD_MB=25`, `MAX_TOTAL_UPLOAD_MB=100`, `MAX_FILES_PER_JOB=10`, `MAX_PDF_PAGES=300`, `MAX_IMAGE_PIXELS=50000000`, `PROCESS_TIMEOUT_SECONDS=60`, `FILE_RETENTION_MINUTES=60`, `USER_STORAGE_QUOTA_MB=200` | Proposed defaults (`prd.md` §7.3) |

Database: dev `filenest_dev`, test `filenest_test` on `localhost:5432`. Tables today: `users`, `refresh_tokens`, `password_resets`. Planned: `pdf_files` (M3), `pdf_jobs` (M8).

---

## 6. Commands

```bash
# Activate the virtualenv
source .venv/bin/activate

# Make sure PostgreSQL is running (Redis only if working on Celery)

# Migrations
alembic upgrade head
alembic revision --autogenerate -m "describe_change"

# Run the app
uvicorn app.main:app --reload

# Celery worker (post-MVP only)          ↓ note: --loglevel (v0.1.0 had a typo)
celery -A app.workers.celery_app:celery_app worker --loglevel=info

# Tests (use your own credentials)
TEST_DATABASE_URL="postgresql+asyncpg://<user>:<password>@localhost:5432/filenest_test" pytest

# Quality (once pyproject.toml exists — task 2.04)
ruff check . && ruff format --check . && mypy app

# Progress counter for tasks.md
grep -cE '^\| [0-9]+\.[0-9]+ .*\| ✅ \|' tasks.md    # done
grep -cE '^\| [0-9]+\.[0-9]+ ' tasks.md               # total (all milestones)
```

---

## 7. Architecture Decisions (important)

**Existing**

1. **Async everywhere** — async SQLAlchemy/FastAPI; never sync DB calls in routes.
2. **Server-rendered frontend for MVP** — static HTML/JS served by FastAPI (now includes tool pages; React is post-MVP, D2).
3. **PDF processing independent from the API** — pure service functions (paths/bytes in → out), so they can move into Celery unchanged.
4. **Files on the filesystem** (not in the DB), behind a storage interface for a future S3/MinIO move.
5. **Separate access/refresh secrets.**
6. **Refresh tokens hashed (SHA-256)**; never stored in plaintext.
7. **Refresh-token families:** tokens from one login share a `family_id`; reuse revokes the family.
8. **Models ≠ Schemas** — never return an ORM model from a route.
9. **`get_db` override in tests** — `conftest.py` uses a `NullPool` test session and a clean DB per test.

**New in this revision (`ANALYSIS.md` §4 — confirm or change)**

- **D1** MVP processes PDFs synchronously via `asyncio.to_thread` + semaphore + timeout; Celery/Redis in M8.
- **D2** MVP UI is server-rendered vanilla JS including tool pages; React only if needed later.
- **D3** Permissive-licence PDF stack; no PyMuPDF/Ghostscript without an explicit licence decision.
- **D4** Tokens: `localStorage` + CSP + cross-tab lock now; `httpOnly` cookie for the refresh token before public launch.
- **D5** Two-step tool API: upload → tools take `file_ids` → result file.
- **D6** Uploads and results auto-delete after 60 minutes; users can delete sooner.

---

## 8. Conventions Cheat-Sheet (full text: `rules.md`)

- Type-hint everything; `X | None`; `Annotated` for `Depends`; Google-style docstrings on public code.
- Double quotes; 88 columns; `ruff format` is the formatter of record.
- Domain errors in `app/core/exceptions.py` with a stable `code`; one exception handler maps them to `{detail, code}`.
- SQLAlchemy 2.x `select()` only; `func.now()`/`server_default`; index FKs and filter columns.
- Pydantic v2; validators normalise (trim, lowercase email).
- **Every user-owned query filters by `user_id`; other users' resources are `404`.**
- **Never** use client filenames on disk; detect type by magic bytes; enforce limits while streaming.
- Never log tokens/passwords/reset links; no secrets in docs or tests.
- Frontend: no inline JS, `FileNestAPI` for all calls, `textContent` for untrusted text.
- Tests: `test_<action>_<scenario>`; generate PDFs programmatically; ownership/edge cases required.
- Conventional Commits; docs updated in the same PR.

---

## 9. Data Model

**Current tables:** `users` (id, email, hashed_password, full_name, is_active, is_superuser, last_login_at, timestamps) · `refresh_tokens` (id, user_id, token_hash, family_id, expires_at, revoked_at, replaced_by_id, timestamps) · `password_resets` (id, user_id, token_hash, used_at, expires_at, timestamps).

**Applied (task 2.03 ✅, migration `7c8294d5dcf2`):** `password_resets.expires_at` (not null, 30-min server default, indexed) · `refresh_tokens.replaced_by_id` (nullable self-FK, `ON DELETE SET NULL`) · `expires_at` indexes on both tables · unique functional index `uq_users_email_lower` on `lower(email)` (replaces `uq_users_email`).

**Planned:** `pdf_files` (M3), `pdf_jobs` (M8) — columns in `prd.md` §8.

---

## 10. Frontend Token Flow

**Current**
1. Tokens in `localStorage` as `filenest_access_token` and `filenest_refresh_token`.
2. `apiFetch` attaches the access token.
3. On `401`, `apiFetch` calls `POST /api/v1/auth/refresh` (deduplicated **within a tab only**).
4. On refresh failure: clear tokens, dispatch `filenest:logout`, redirect to `/login`.
5. `main.js` renders the nav from `FileNestAPI.me()`.
6. `auth-forms.js` handles login/register with client-side validation.

**Known defect:** two tabs refreshing at once look like token reuse → family revoked → forced logout (`ANALYSIS.md` F-02; task 2.06 adds a `navigator.locks` lock and a `storage`-event logout).

**Target (task 6.06):** refresh token in an `httpOnly; Secure; SameSite=Strict; Path=/api/v1/auth` cookie; access token in memory only.

---

## 11. Known Gaps and Issues

**Not implemented yet**
- Storage service, `PdfFile` model/schema/migration, upload/download/delete endpoints, retention cleanup (M3)
- All PDF tools and their tests (M4)
- Tool UI, dashboard, forgot/reset pages, settings (M5)
- Rate limiting, CSP/security headers, file validation, audit logging (M6)
- Email sending for password reset (2.08); password-reset endpoints/tests need verification (2.07)
- Docker, Nginx, CI/CD, backups, privacy page (M7)
- Celery jobs (M8) and React (M9, conditional)

**Known issues / risks**

| # | Issue | Task |
| --- | --- | --- |
| I-1 | Dev DB password was written in the v0.1.0 memory file → rotate | 2.01 ✅ (old credential is dead; history rewrite declined by decision) |
| I-2 | `alembic.ini` has a hard-coded URL that differs from the app's real DB (user and database name) | 2.02 ✅ (URL removed; runtime source of truth is app settings) |
| I-3 | `password_resets` has no `expires_at` | 2.03 ✅ (also `replaced_by_id`, expiry indexes, unique `lower(email)` index) |
| I-4 | Multi-tab refresh causes false reuse detection | 2.06 |
| I-5 | No `pyproject.toml`/CI, so `rules.md` was not enforced (`ruff` cache exists; version reported as 0.16.7 — verify) | 2.04, 2.05 |
| I-6 | Dev/test packages are in runtime `requirements.txt` | 2.12 |
| I-7 | `PROJECT_STACK.md` may still say "no Celery/Redis in MVP" while `prd.md` v0.1.0 also said Redis is required — now resolved by D1 | 2.14 |

---

## 12. Gotchas

- **Do not** run blocking PDF/image code on the event loop — use `run_pdf_job()` (once it exists).
- The test suite needs `TEST_DATABASE_URL` or a derivable `filenest_test` database that already exists.
- Alembic always uses the app's settings for the DB URL (`alembic.ini` carries no URL — see 2.02); never re-add a hard-coded URL.
- CORS only allows `http://localhost:3000`; static pages are same-origin, so it does not affect them.
- Never trust file extensions or `Content-Type`; always sniff magic bytes.
- Check licences before adding any PDF library (AGPL trap: PyMuPDF/MuPDF, Ghostscript).
- White text on `--accent-strong` fails contrast; use `--on-accent`.

---

## 13. Working Agreement for AI Assistants

**Do**
- Read the task in `tasks.md`, its acceptance criteria, and the relevant `prd.md` requirement before coding.
- Keep changes small (one task ≈ one PR) and include tests, typing, and docstrings.
- Update `tasks.md` status and this file's §1 when work completes.
- Prefer existing dependencies; when a new one is unavoidable, state its licence and why.
- Ask before changing a recorded decision (D1–D6), the data model, or the public API contract.
- Match the surrounding code style; run lint/type/tests before declaring done.

**Don't**
- Don't put secrets, tokens, or credentials in code, docs, tests, logs, or commit messages.
- Don't add PyMuPDF/Ghostscript or other AGPL/GPL libraries.
- Don't introduce a frontend framework, CDN scripts, or inline JS.
- Don't return ORM models from routes or expose `hashed_password`.
- Don't write client-supplied filenames to disk.
- Don't mark a task ✅ without tests and the Definition of Done (`rules.md` §21).

---

## 14. Glossary

| Term | Meaning |
| --- | --- |
| Family | All refresh tokens issued from one login (`family_id`) |
| Reuse detection | Presenting a revoked refresh token revokes its whole family |
| Result file | A `PdfFile` with `kind = "result"` created by a tool run |
| Retention | Time after which uploads/results are deleted (`FILE_RETENTION_MINUTES`) |
| D1–D6 | Decisions recorded in `ANALYSIS.md` §4 |
| F-nn | Findings in `ANALYSIS.md` §3 |
| FR/NFR | Functional / non-functional requirement IDs in `prd.md` |

---

## 15. Change Log of This File

- **0.2.0 (2026-09-20):** removed credentials and personal paths; removed stale timestamp; fixed Celery flag typo (`--loglevel`); merged duplicate "Known Gaps" entries; split volatile snapshot from stable facts; added decisions D1–D6, known issues with task links, assistant working agreement, glossary.
- **0.1.0:** initial auto-generated context.
