# FileNest — Tasks & Progress

**Version:** 0.2.0  
**Date:** 2026-09-20  
**Status:** Auth complete · hardening and file infrastructure next  
**Companion docs:** `prd.md` (requirements `FR-*`), `rules.md` (Definition of Done §21), `ANALYSIS.md` (findings `F-*`, decisions `D1–D6`)

**What changed from 0.1.0:** re-baselined around a *usable* MVP (tool UI is now inside the MVP; React moved post-MVP), added a Hardening milestone that must precede file code, attached tests to each feature instead of a separate testing milestone, added IDs/priorities/sizes/dependencies/acceptance, and replaced the guessed "~25 %" with progress computed from the rows below.

---

## Legend

| Symbol | Meaning |
| --- | --- |
| ✅ | Done — implemented and verified |
| 🔄 | In progress |
| ⚠️ | Unverified / partial — needs a check before it can be called done |
| ❌ | Not started |

**Priority:** `P0` blocks everything after it (or is a security issue) · `P1` required for MVP · `P2` nice for MVP, can slip to v1.1.  
**Size:** `S` ≤ 2 h · `M` ≤ 1 day · `L` > 1 day (split if it grows).  
**MVP scope = Milestones 1–7.** Milestones 8–9 are post-MVP.

---

## Critical Path (do in this order)

1. **2.01 → 2.02 → 2.03** — rotate the exposed password, fix the Alembic URL, add the missing migration columns.
2. **2.04, 2.05** — lint/type config + CI, so the rules are enforced from now on.
3. **2.06** — cross-tab refresh lock (prevents random logouts).
4. **M3** — storage, `PdfFile`, upload/download, validation, retention, processing guard.
5. **M4 in this order:** Rotate → Merge → Split → PDF→Images → Images→PDF → Compress (each with its UI page from M5 as a vertical slice).
6. **M6** — rate limiting, CSP, security tests (before any public beta).
7. **M7** — Docker, Nginx, privacy page, docs → public beta.

---

## Milestone 1: Auth & Infrastructure — ✅ Complete

| ID | Task | Status | Pri | Size | Depends | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| 1.01 | FastAPI application setup (`app/main.py`) | ✅ | P0 | M | — | |
| 1.02 | Async SQLAlchemy 2.x configuration | ✅ | P0 | M | 1.01 | |
| 1.03 | Models: User, RefreshToken, PasswordReset | ✅ | P0 | M | 1.02 | Missing columns tracked in 2.03 |
| 1.04 | Alembic init migration (`7697cdbf4561_init.py`) | ✅ | P0 | S | 1.03 | |
| 1.05 | JWT auth (access + refresh) | ✅ | P0 | M | 1.03 | |
| 1.06 | Refresh rotation with reuse detection | ✅ | P0 | M | 1.05 | Multi-tab false positive: 2.06 |
| 1.07 | Password hashing (Argon2 / pwdlib) | ✅ | P0 | S | 1.03 | |
| 1.08 | CORS middleware | ✅ | P1 | S | 1.01 | Origins from env |
| 1.09 | Static file serving + landing/login/register pages | ✅ | P1 | M | 1.01 | |
| 1.10 | Environment configuration (`.env`, `.env.example`) | ✅ | P0 | S | 1.01 | Audit in 2.11 |
| 1.11 | Auth integration tests (`tests/test_auth.py`, `conftest.py`) | ✅ | P0 | M | 1.05 | |

---

## Milestone 2: Hardening & Housekeeping — ❌ Not started

*Purpose: close the High findings from `ANALYSIS.md` before any file/PDF code exists.*

| ID | Task | Status | Pri | Size | Depends | Acceptance / notes |
| --- | --- | --- | --- | --- | --- | --- |
| 2.01 | **Rotate the exposed DB password**; remove it from any doc; confirm `.env` is git-ignored; scan git history | ✅ | P0 | S | — | F-01. New password in Postgres + `.env` only; defaults cleaned (641f490); working tree clean; 9/9 tests pass. History rewrite **declined by decision** — old credential is rotated/dead, so it can no longer be used |
| 2.02 | `alembic/env.py` reads DB URL from `settings`; remove/neutralise the hard-coded URL in `alembic.ini` | ✅ | P0 | S | — | F-16. Hard-coded `filenest:filenest@…/filenest` URL removed from `alembic.ini` (replaced with comment); `env.py` already read from `settings`; `current`, `upgrade head`, and offline `--sql` verified against the real DB |
| 2.03 | Migration: `password_resets.expires_at, created_at`; `refresh_tokens.created_at, replaced_by_id`; indexes on FKs, `family_id`, `expires_at`; unique `lower(email)` index | ❌ | P0 | M | 2.02 | F-04. Downgrade works; existing tests still pass |
| 2.04 | Add `pyproject.toml` (ruff + mypy per `rules.md` §19) and fix reported issues; add `.pre-commit-config.yaml` | ❌ | P1 | M | — | `ruff check`, `ruff format --check`, `mypy app` all clean |
| 2.05 | CI workflow (GitHub Actions): lint → type check → migrate → pytest (Postgres service) → `pip-audit` | ❌ | P1 | M | 2.04 | Required check on PRs |
| 2.06 | **Cross-tab refresh lock** in `api.js` (`navigator.locks` + re-read after lock) and `storage`-event logout; optional server grace window (≤ 10 s, uses `replaced_by_id`) | ❌ | P0 | M | 2.03 | F-02. Test: two tabs get 401 simultaneously → exactly one `/auth/refresh` call, no logout (FR-A8) |
| 2.07 | Verify forgot/reset-password endpoints exist and behave per PRD §7.2 (generic `202`, 30-min expiry, single use, revoke all sessions); add tests | ⚠️ | P1 | M | 2.03, 2.08 | Not listed as done in v0.1.0 — confirm in code |
| 2.08 | Email service abstraction `app/services/email.py` (console backend for dev, SMTP backend for prod); reset email template | ❌ | P1 | M | — | Links never logged in production mode |
| 2.09 | Central `AppError` hierarchy + exception handler returning `{detail, code}` | ❌ | P1 | M | — | `rules.md` §7; existing auth routes migrated |
| 2.10 | Structured logging with request ID and token/PII redaction | ❌ | P2 | M | — | No tokens/passwords in any log line (test) |
| 2.11 | Settings for limits/retention/storage (`MAX_UPLOAD_MB`, `MAX_TOTAL_UPLOAD_MB`, `MAX_FILES_PER_JOB`, `MAX_PDF_PAGES`, `MAX_IMAGE_PIXELS`, `PROCESS_TIMEOUT_SECONDS`, `MAX_CONCURRENT_JOBS`, `FILE_RETENTION_MINUTES`, `USER_STORAGE_QUOTA_MB`, `STORAGE_DIR`); update `.env.example`; secrets as `SecretStr` | ❌ | P1 | S | — | PRD §7.3 defaults |
| 2.12 | Split dev tools into `requirements-dev.txt` | ❌ | P2 | S | — | F-17 |
| 2.13 | Confirm decisions **D1–D6** (edit `ANALYSIS.md` if you change any) | ❌ | P0 | S | — | Decision only, no code |
| 2.14 | Align `architecture.md` and `PROJECT_STACK.md` with D1–D6 (not provided for this review) | ❌ | P2 | S | 2.13 | Send them and I will update |

---

## Milestone 3: File Infrastructure — ❌ Not started

*Purpose: safe upload → validate → store → download → expire. No PDF operations yet.*

| ID | Task | Status | Pri | Size | Depends | Acceptance / notes |
| --- | --- | --- | --- | --- | --- | --- |
| 3.01 | Add `pypdf` and `Pillow` to `requirements.txt` (licence noted in PR) | ❌ | P0 | S | 2.13 | D3 |
| 3.02 | Storage abstraction `app/services/storage.py` (`LocalStorage`: save stream, open, delete, exists; UUID keys; base-dir confinement) | ❌ | P0 | M | 2.11 | Traversal attempts impossible by construction; interface allows S3 later |
| 3.03 | `PdfFile` model + schema + Alembic migration (PRD §8) | ❌ | P0 | M | 2.03 | `user_id`, `kind`, `storage_key`, `expires_at`, indexes |
| 3.04 | Storage directories (`storage/uploads`, `storage/results`, `storage/tmp`) created at startup and git-ignored | ❌ | P1 | S | 3.02 | |
| 3.05 | Validation service `app/services/file_validation.py`: magic bytes, size (streamed), page count, encryption, image verify + pixel cap | ❌ | P0 | L | 3.01 | Error codes per PRD §6.3; F-06 |
| 3.06 | `POST /api/v1/files/upload` (multi-file, streaming, quota check) | ❌ | P0 | M | 3.02, 3.03, 3.05 | `201` list of `FileRead` with page count and `expires_at` |
| 3.07 | `GET /files`, `GET /files/{id}`, `GET /files/{id}/download`, `DELETE /files/{id}` | ❌ | P0 | M | 3.06 | Owner-only (`404` otherwise); `nosniff`, `Content-Disposition` |
| 3.08 | Retention cleanup: startup sweep + periodic lifespan task deleting expired rows **and** files | ❌ | P0 | M | 3.03 | Files gone ≤ 10 min after `expires_at`; tolerant of missing files |
| 3.09 | Per-user storage quota enforcement | ❌ | P2 | S | 3.06 | `QuotaExceededError` → `413`/`422` per PRD |
| 3.10 | `run_pdf_job()` helper: `asyncio.to_thread` + semaphore + timeout + temp-dir cleanup | ❌ | P0 | M | 2.11 | Timeout → `504 PROCESSING_TIMEOUT`; temp files removed on cancel |
| 3.11 | Tests: type spoofing (rename `.exe`→`.pdf`), oversize, too many pages, encrypted, corrupt, traversal filename, IDOR, expiry cleanup, quota | ❌ | P0 | L | 3.06–3.10 | Included in each task's PR; listed here as the acceptance gate for M3 |

---

## Milestone 4: PDF Tools — ❌ Not started

*Each tool = pure service + schema/route + tests. Order: simplest/lowest risk first. Each task's PR also adds the tool's UI page from M5 (vertical slice) where practical.*

| ID | Task | Status | Pri | Size | Depends | Acceptance / notes |
| --- | --- | --- | --- | --- | --- | --- |
| 4.01 | Shared: `ToolResult` schema, page-range parser (`1-3,5,8-`), result-file creation helper, PDF test factories | ❌ | P0 | M | M3 | Range parser fully unit-tested (invalid, open-ended, overlapping) |
| 4.02 | **Rotate** service (`pdf_rotate.py`) | ❌ | P0 | S | 4.01 | FR-P1 |
| 4.03 | Rotate route + schema (`POST /pdf/rotate`) | ❌ | P0 | S | 4.02 | |
| 4.04 | Rotate tests (`test_pdf_rotate.py`) | ❌ | P0 | S | 4.03 | Angles, page subsets, modulo 360 |
| 4.05 | **Merge** service (`pdf_merge.py`) | ❌ | P0 | M | 4.01 | FR-P2 |
| 4.06 | Merge route + schema | ❌ | P0 | S | 4.05 | 2–10 files; order respected |
| 4.07 | Merge tests | ❌ | P0 | M | 4.06 | Page count/order; one encrypted input rejects whole job |
| 4.08 | **Split** service (`pdf_split.py`) with ZIP output | ❌ | P1 | M | 4.01 | FR-P3 |
| 4.09 | Split route + schema | ❌ | P1 | S | 4.08 | |
| 4.10 | Split tests | ❌ | P1 | M | 4.09 | Ranges, every-N, extract, out-of-range |
| 4.11 | **PDF → Images** service (`pdf_to_images.py`, pypdfium2) | ❌ | P1 | M | 4.01 | FR-P4; pixel × pages cap before rendering |
| 4.12 | To-images route + schema | ❌ | P1 | S | 4.11 | |
| 4.13 | To-images tests | ❌ | P1 | M | 4.12 | Format, DPI bounds, ZIP naming |
| 4.14 | **Images → PDF** service (`images_to_pdf.py`, Pillow + ReportLab) | ❌ | P1 | M | 4.01 | FR-P5; EXIF orientation |
| 4.15 | From-images route + schema | ❌ | P1 | S | 4.14 | |
| 4.16 | From-images tests | ❌ | P1 | M | 4.15 | Page size modes, order, huge image rejection |
| 4.17 | **Compress** — benchmark corpus + approach decision (pypdf stream/object compression vs image recompression via Pillow/pikepdf; verify licences) | ❌ | P1 | M | 4.01 | Written result in PR; realistic expectations documented (F-15, R3) |
| 4.18 | Compress service (`pdf_compress.py`) | ❌ | P1 | L | 4.17 | FR-P6; never larger than input |
| 4.19 | Compress route + schema | ❌ | P1 | S | 4.18 | Returns `original_bytes`, `result_bytes`, `reduced` |
| 4.20 | Compress tests | ❌ | P1 | M | 4.19 | Levels; no-saving case; image-heavy and text-only fixtures |

---

## Milestone 5: MVP Web UI (server-rendered) — ❌ Not started

*Vanilla JS + CSS tokens per `design.md`. Replaces the old "React" milestone for the MVP (D2).*

| ID | Task | Status | Pri | Size | Depends | Acceptance / notes |
| --- | --- | --- | --- | --- | --- | --- |
| 5.01 | Refactor `styles.css` to `design.md` v0.2 tokens: `--border-strong`, `--on-accent`, `:focus-visible`, reduced motion, skip link | ❌ | P0 | M | — | Contrast table in design §2.3 holds; F-20/F-22/F-24 |
| 5.02 | Landing/login/register accessibility pass (labels, `aria-*`, live regions, toast semantics, show-password) | ❌ | P1 | M | 5.01 | axe: no serious issues |
| 5.03 | Forgot-password and reset-password pages + `auth-forms.js` modes | ❌ | P1 | M | 2.07 | Generic message; token stripped from URL |
| 5.04 | Authenticated dashboard: tool grid + recent files (expiry + delete) | ❌ | P1 | M | 3.07 | Empty state; delete works |
| 5.05 | Shared tool-page shell + `tool.js` state machine | ❌ | P0 | L | 3.06 | `idle→uploading→ready→processing→done/error` |
| 5.06 | `dropzone.js`: native input + drag-drop, client pre-checks, per-file errors | ❌ | P0 | M | 5.05 | Keyboard operable; limits from config |
| 5.07 | File-row list with Up/Down reorder buttons (+ optional drag) and remove | ❌ | P0 | M | 5.06 | Screen-reader labels; mobile layout |
| 5.08 | `messages.js`: error `code` → message table (design §7.4); status/progress component | ❌ | P1 | S | 5.05 | |
| 5.09 | Result panel: download, delete now, start over, compress before/after | ❌ | P1 | M | 5.05 | Focus moves to result heading |
| 5.10 | Rotate tool page | ❌ | P0 | S | 4.03, 5.09 | |
| 5.11 | Merge tool page | ❌ | P0 | M | 4.06, 5.07 | |
| 5.12 | Split tool page (range validation) | ❌ | P1 | M | 4.09 | |
| 5.13 | PDF → Images tool page | ❌ | P1 | S | 4.12 | |
| 5.14 | Images → PDF tool page | ❌ | P1 | M | 4.15, 5.07 | |
| 5.15 | Compress tool page | ❌ | P1 | S | 4.19 | |
| 5.16 | 404/error pages; nav truncation and mobile rules | ❌ | P2 | S | 5.01 | |
| 5.17 | Settings page + `PATCH /auth/me`, `POST /auth/change-password`, `POST /auth/logout-all` | ❌ | P2 | L | 2.03 | v1.1 if time-boxed |
| 5.18 | Accessibility audit: keyboard-only run, Lighthouse ≥ 95, screen-reader smoke test, 320/768/1280 px | ❌ | P1 | M | 5.10–5.15 | Checklist in `design.md` §8 |
| 5.19 | Browser smoke tests (Playwright): register → merge → download; two-tab refresh | ❌ | P2 | L | 5.11, 2.06 | Runs in CI |

---

## Milestone 6: Security Hardening (before public beta) — ❌ Not started

| ID | Task | Status | Pri | Size | Depends | Acceptance / notes |
| --- | --- | --- | --- | --- | --- | --- |
| 6.01 | Rate limiting (per IP + per user; strict on auth, upload, tools); `429` + `Retry-After` | ❌ | P0 | M | M3 | NFR-S5 |
| 6.02 | Login throttling per email + IP; uniform forgot-password response and timing | ❌ | P0 | M | 6.01 | F-07 |
| 6.03 | Security-headers middleware: CSP (`script-src 'self'`), `nosniff`, `frame-ancestors 'none'`, `Referrer-Policy`, HSTS (prod) | ❌ | P0 | M | 5.01 | Site works with CSP enabled (no inline JS) |
| 6.04 | XSS review: remove any inline JS/`innerHTML` of untrusted data; enforce `textContent` | ❌ | P0 | M | 6.03 | F-03 |
| 6.05 | Security tests: auth bypass, IDOR on every file endpoint, path traversal, zip/pixel bombs, malformed PDFs, oversize | ❌ | P0 | L | M3, M4 | All pass in CI |
| 6.06 | Move refresh token to `httpOnly; Secure; SameSite=Strict; Path=/api/v1/auth` cookie; access token in memory; CSRF review | ❌ | P1 | L | 6.03 | D4 target state |
| 6.07 | Request logging/audit (auth events, tool runs; IDs only) | ❌ | P1 | M | 2.10 | No PII/tokens |
| 6.08 | Dependency audit: `pip-audit` gate + Dependabot | ❌ | P1 | S | 2.05 | |
| 6.09 | Secret scanning (`gitleaks`) in pre-commit and CI | ❌ | P1 | S | 2.05 | |
| 6.10 | Password policy: max 128, common-password blocklist | ❌ | P2 | S | — | |

---

## Milestone 7: Release Readiness — ❌ Not started

| ID | Task | Status | Pri | Size | Depends | Acceptance / notes |
| --- | --- | --- | --- | --- | --- | --- |
| 7.01 | Backend Dockerfile (slim, non-root, healthcheck) | ❌ | P1 | M | — | |
| 7.02 | Docker Compose: api + Postgres (+ Redis optional profile) | ❌ | P1 | M | 7.01 | `docker compose up` works from clean checkout |
| 7.03 | Nginx: TLS, `client_max_body_size` = `MAX_TOTAL_UPLOAD_MB`, timeouts, gzip, static caching | ❌ | P1 | M | 7.02 | |
| 7.04 | Health split: `/health/live` and `/health/ready` | ❌ | P2 | S | — | |
| 7.05 | Production configuration checklist (secrets, CORS, debug off, HTTPS-only) | ❌ | P1 | S | 7.02 | |
| 7.06 | Postgres backup + tested restore procedure | ❌ | P1 | M | 7.02 | |
| 7.07 | Privacy page & terms: retention (60 min), no ads/trackers, hosting region | ❌ | P1 | M | PRD Q4 | Statement matches actual behaviour |
| 7.08 | Docs: README quick start, setup guide, deployment guide, OpenAPI descriptions/examples at `/docs` | ❌ | P1 | M | M4 | Fresh machine can run the app from README |
| 7.09 | Load test vs PRD §9 targets (k6/Locust) | ❌ | P2 | M | M4 | Results recorded |
| 7.10 | Error tracking/monitoring hook (privacy-preserving) | ❌ | P2 | M | 7.04 | |

---

## Milestone 8: Background Processing — ❌ Post-MVP

| ID | Task | Status | Pri | Size | Depends | Acceptance / notes |
| --- | --- | --- | --- | --- | --- | --- |
| 8.01 | Redis in Compose; Celery worker configuration | ❌ | P1 | M | 7.02 | |
| 8.02 | `PdfJob` model, schema, migration | ❌ | P1 | M | — | PRD §8 |
| 8.03 | Wrap existing service functions in Celery tasks (no logic change) | ❌ | P1 | L | 8.01, 8.02 | |
| 8.04 | Tool endpoints return `202 {job_id}`; `GET /jobs/{id}`, result endpoint | ❌ | P1 | L | 8.03 | Client handles "result or job" |
| 8.05 | Celery beat for retention cleanup (replaces in-process loop) | ❌ | P1 | S | 8.01 | |
| 8.06 | Progress reporting UI (polling/SSE) | ❌ | P2 | M | 8.04 | |
| 8.07 | Worker limits: time limits, retries, concurrency, failure handling | ❌ | P1 | M | 8.03 | |
| 8.08 | Tests: eager-mode unit tests + one real-broker integration test | ❌ | P1 | M | 8.03 | |

---

## Milestone 9: React Frontend — ❌ Post-MVP, conditional

*Start only if vanilla JS becomes limiting (page thumbnails, drag reordering, file manager). Decision recorded in `ANALYSIS.md` D2.*

| ID | Task | Status | Pri | Size | Depends | Acceptance / notes |
| --- | --- | --- | --- | --- | --- | --- |
| 9.01 | Go/no-go review against adoption criteria (`design.md` §9.2) | ❌ | P1 | S | M5 | Written decision |
| 9.02 | Vite + React (+ TypeScript) scaffold; tokens as CSS variables (Tailwind optional, mapped to tokens) | ❌ | P1 | M | 9.01 | |
| 9.03 | Port API client incl. cross-tab lock | ❌ | P1 | M | 9.02 | |
| 9.04 | Page-preview + reorder components | ❌ | P1 | L | 9.02 | Keyboard accessible |
| 9.05 | Migrate tool pages one by one; parity checklist | ❌ | P1 | L | 9.03 | |
| 9.06 | File history / file manager page | ❌ | P2 | L | 9.03 | |

---

## Future Backlog (unscheduled)

Watermark · Protect/Unlock PDF · Page numbers · Reorder pages tool · OCR · PDF ↔ Word/Excel/PowerPoint · API keys · Teams/sharing · Subscription & billing · S3/MinIO storage · Guest mode (PRD Q1) · Multi-language UI.

---

## Progress

*(Counts are computed from the task rows above — update by re-running the counting command in `memory.md` §Commands.)*

| Milestone | Scope | Done | Total | Status |
| --- | --- | --- | --- | --- |
| 1. Auth & Infrastructure | MVP | 11 | 11 | ✅ Complete |
| 2. Hardening & Housekeeping | MVP | 2 | 14 | 🔄 In progress |
| 3. File Infrastructure | MVP | 0 | 11 | ❌ Not started |
| 4. PDF Tools | MVP | 0 | 20 | ❌ Not started |
| 5. MVP Web UI (server-rendered) | MVP | 0 | 19 | ❌ Not started |
| 6. Security Hardening (before public beta) | MVP | 0 | 10 | ❌ Not started |
| 7. Release Readiness | MVP | 0 | 10 | ❌ Not started |
| 8. Background Processing | Post-MVP | 0 | 8 | ❌ Post-MVP |
| 9. React Frontend | Post-MVP | 0 | 6 | ❌ Post-MVP (conditional) |
| **MVP total (M1–M7)** | | **13** | **95** | **14 %** |
| Post-MVP (M8–M9) | | 0 | 14 | — |
| All milestones | | 11 | 109 | 10 % |

**MVP completion: 13 of 95 tasks (14 %).** The previous "~25 %" was not derived from the task list: it counted finished documentation files as progress and mixed in post-MVP work. The new plan is also more granular and adds the hardening, security and release work the old plan lacked, so the two numbers are not directly comparable — the honest reading is that the auth foundation is done and most of the product is still ahead. Task count is not effort: the remaining MVP work is dominated by M3–M5 (L-sized tasks). P0 tasks in MVP scope: 11 of 41 done.

---

## Working Agreement

- One task ≈ one PR; update this file (status + notes) in the same PR.
- A task is ✅ only when the **Definition of Done** (`rules.md` §21) is met, including tests.
- Do not start M4 until M2 P0 tasks and M3 P0 tasks are ✅.
- Keep work-in-progress ≤ 2 tasks; finish before starting new work.
- If scope grows, split the task or move it to the backlog — do not silently expand the MVP.
