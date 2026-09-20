# FileNest — Product Requirements Document

**Version:** 0.2.0  
**Date:** 2026-09-20  
**Status:** MVP in development (Auth complete; file infrastructure and PDF tools next)  
**Companion docs:** `ANALYSIS.md` (why this changed), `design.md`, `rules.md`, `tasks.md`, `memory.md`

> **Conventions.** Requirement IDs (`FR-…`, `NFR-…`) are stable; reference them in tasks, tests and PRs. Numbers marked *(proposed)* are defaults I chose so the requirement is testable — confirm or change them (see §14).

---

## 1. Product Overview

FileNest is an online PDF tools platform in the spirit of iLovePDF: users sign in, upload documents, run an operation (merge, split, compress, rotate, convert) and download the result — from any browser, with nothing to install.

**Problem.** People need everyday PDF operations without installing desktop software, but existing free services carry ads, restrictive file-size limits, and vague privacy promises.

**Value proposition.**

1. **Private by design** — files are deleted automatically after a short, published retention window; users can delete them immediately.
2. **Ad-free and honest limits** — limits are shown before upload, not discovered after a failure.
3. **Fast and focused** — six core tools done well, small-file jobs return in seconds.
4. **Secure sessions** — JWT with refresh-token rotation and reuse detection.

**Positioning statement:** *"The PDF toolkit that deletes your files in an hour and never shows ads."* (Competitive rationale: `ANALYSIS.md` §5.)

---

## 2. Users

| Persona | Needs | Success looks like | Design implication |
| --- | --- | --- | --- |
| **Student / job seeker** (Amina, 21) — occasional use, mobile-heavy | Merge CV + certificates, compress to fit a portal's upload limit, turn phone photos into a PDF | Done in < 2 minutes on a phone, no confusing options | Mobile-first tool pages, big touch targets, size-reduction shown clearly |
| **Office professional** (Rafi, 34) — weekly use | Split scanned bundles, rotate mis-scanned pages, send smaller PDFs | Trusts the tool with work documents | Visible retention message, delete-now button, no ads |
| **Privacy-conscious user** (Dr. Nusrat, 45) — rare use, high sensitivity | Knows what happens to her files | Can verify the claim | Plain-language privacy page; auto-delete evidence (expiry shown on every file) |
| **Small-team lead** (future) | Shared workflows, history | — | Out of MVP; accounts/history are groundwork |

---

## 3. Features (MoSCoW)

### 3.1 MVP — Must have

| ID | Feature | Description | Acceptance summary |
| --- | --- | --- | --- |
| FR-A1 | Register | Email, password, optional full name | Duplicate email → `409`; weak password → field error; password never returned |
| FR-A2 | Login | Email + password → access/refresh pair | Wrong credentials → `401` with generic message |
| FR-A3 | Token refresh | Rotate refresh token on every use | Reuse of a revoked token revokes the whole family (see FR-A8 for the multi-tab exception) |
| FR-A4 | Logout | Revoke refresh token and its family | Token unusable afterwards |
| FR-A5 | Current user | `GET /auth/me` | `401` without/with bad token |
| FR-A6 | Password reset | Emailed single-use link, 30-minute expiry | Response identical whether or not the email exists; all sessions revoked on success |
| FR-A7 | Health check | DB connectivity | `200` when healthy, `503` when DB down |
| FR-A8 | Multi-tab safety | Two tabs refreshing simultaneously must not log the user out | Verified by test/manual script (tasks 2.06) |
| FR-F1 | Upload | Multi-file upload with validation | Rejects wrong type/oversize with specific error codes; stores by UUID |
| FR-F2 | Download | Owner-only download | Other user's file → `404` |
| FR-F3 | Delete + auto-expiry | User delete; scheduled cleanup | Files gone from disk and DB after expiry |
| FR-P1 | Rotate | Rotate all/selected pages by 90/180/270° | Output page rotation verified in tests |
| FR-P2 | Merge | Combine 2–10 PDFs in a chosen order | Page count = sum of inputs; order respected |
| FR-P3 | Split | By ranges, every N pages, or extract pages | Output pages match requested ranges; delivered as a ZIP when multiple |
| FR-P4 | PDF → Images | Render pages as PNG/JPG | One image per selected page at requested DPI; delivered as ZIP |
| FR-P5 | Images → PDF | Combine JPG/PNG into one PDF | One page per image in the chosen order |
| FR-P6 | Compress | Reduce file size at 3 levels | Result never larger than input (else return original with `reduced=false`) |
| FR-U1 | Web UI | Landing, login, register, forgot/reset, dashboard, one page per tool | Every tool usable end-to-end without touching the API directly |
| FR-U2 | Limits shown | File/page/count limits visible before upload | Text on every tool page reflects live config |

### 3.2 Should have (MVP if time allows, else v1.1)

- Settings page: change password, update name, "sign out everywhere".
- Recent files list (inside the retention window).
- Page thumbnails for reorder/rotate (needs rendering; lightweight).
- Login throttling UI feedback (`429` with retry-after).

### 3.3 Could have (post-MVP)

- Background processing + progress (Milestone 8).
- React frontend if vanilla JS becomes limiting (Milestone 9).
- Watermark, protect (add password), unlock, page numbers, reorder pages tool.
- API keys for developers.

### 3.4 Won't have (MVP) — see §12

---

## 4. User Stories and Acceptance Criteria

Format: *As a … I want … so that …* → **Given / When / Then**.

### Authentication

| # | Story | Acceptance |
| --- | --- | --- |
| 1 | As a new user, I want to register so I can use the tools. | **Given** a new email and a valid password, **when** I submit, **then** I am logged in and land on the dashboard. **Given** an existing email, **then** I see "An account with this email already exists." |
| 2 | As a returning user, I want to log in. | Correct credentials → dashboard; wrong → single generic error, no hint which field was wrong. |
| 3 | As a user, I want my session to persist safely. | Refresh happens silently; if it fails I am sent to `/login` with a "session expired" notice. |
| 4 | As a user, I want stolen refresh tokens to be useless. | Replaying a rotated token revokes the family and logs out attackers. |
| 5 | As a user, I want to log out fully. | Logout revokes the server-side token family and clears local storage. |
| 6 | As a user who forgot my password, I want to reset it. | Enter email → generic confirmation → email link → new password → all sessions revoked → login. Link works once, expires in 30 min. |
| 7 | As a user with several tabs open, I don't want random logouts. | Simultaneous 401s in two tabs result in **one** refresh call; no forced logout. |

### PDF tools

| # | Story | Acceptance |
| --- | --- | --- |
| 8 | Merge multiple PDFs | Upload 2–10 PDFs, reorder, click Merge → one PDF, pages in the chosen order. |
| 9 | Split by range | Enter `1-3,5,8-` → pages extracted accordingly; invalid range shows an inline error before submit and a `422` from the API. |
| 10 | Compress | Choose level → result shows "X MB → Y MB (−Z%)". If no saving is possible, tell the user honestly. |
| 11 | Rotate | Choose angle and pages → correct pages rotated; others untouched. |
| 12 | PDF → images | Choose format/DPI → ZIP with `page-001.png…`. |
| 13 | Images → PDF | Add images, reorder, choose page size → PDF with one image per page, correct orientation (EXIF respected). |
| 14 | Privacy | Every upload and result shows "Deleted automatically at 14:32" and a **Delete now** button. |
| 15 | Bad input | Encrypted, corrupt, oversize, or too-many-pages files produce a specific, human-readable error (see §6.3). |

---

## 5. Positioning Summary

Full analysis lives in `ANALYSIS.md` §5. In short: compete on **privacy, honesty of limits, no ads, and speed** for six core tools; do **not** compete on breadth (Word/Excel conversion, OCR, e-signature) in the MVP.

---

## 6. API Design

Base path: `/api/v1`. JSON unless stated. Bearer token = `Authorization: Bearer <access_token>`.

### 6.1 Auth and health

| Method | Path | Auth | Success | Description |
| --- | --- | --- | --- | --- |
| `POST` | `/auth/register` | — | `201` | Create user |
| `POST` | `/auth/login` | — | `200` | Access + refresh token |
| `POST` | `/auth/refresh` | — | `200` | Rotate refresh token (new pair) |
| `POST` | `/auth/logout` | — | `204` | Revoke refresh token family |
| `GET` | `/auth/me` | Bearer | `200` | Current user |
| `POST` | `/auth/forgot-password` | — | `202` | Always the same response |
| `POST` | `/auth/reset-password` | — | `204` | Consume token, set password, revoke all sessions |
| `GET` | `/health` | — | `200`/`503` | DB connectivity *(split into live/ready in M7)* |

*Later (Should):* `PATCH /auth/me`, `POST /auth/change-password`, `POST /auth/logout-all`.

### 6.2 Files and tools (two-step contract)

**Step 1 — upload** (`multipart/form-data`, field `files`, repeatable):

```
POST /api/v1/files/upload            → 201
[
  {
    "id": "6f1c…-uuid",
    "original_name": "cv.pdf",
    "content_type": "application/pdf",
    "size_bytes": 482113,
    "page_count": 3,
    "kind": "upload",
    "created_at": "2026-09-20T10:00:00Z",
    "expires_at": "2026-09-20T11:00:00Z"
  }
]
```

**Step 2 — run a tool** with file IDs. The order of `file_ids` is the processing order.

| Method | Path | Request body (JSON) | Result |
| --- | --- | --- | --- |
| `POST` | `/pdf/merge` | `{"file_ids": [id, id, …], "output_name": "merged.pdf"}` | one PDF |
| `POST` | `/pdf/split` | `{"file_id": id, "mode": "ranges" \| "every_n" \| "extract", "ranges": "1-3,5,8-", "every_n": 2}` | PDF, or ZIP if multiple outputs |
| `POST` | `/pdf/compress` | `{"file_id": id, "level": "low" \| "recommended" \| "extreme"}` | PDF + `original_bytes`, `result_bytes`, `reduced` |
| `POST` | `/pdf/rotate` | `{"file_id": id, "angle": 90 \| 180 \| 270, "pages": "all" \| "1-3,7"}` | one PDF |
| `POST` | `/pdf/to-images` | `{"file_id": id, "format": "png" \| "jpg", "dpi": 150, "pages": "all"}` | ZIP |
| `POST` | `/pdf/from-images` | `{"file_ids": [id, …], "page_size": "a4" \| "letter" \| "fit", "margin": "none" \| "small"}` | one PDF |

**MVP response (`200`)** — synchronous (D1):

```json
{
  "file": { "id": "…", "original_name": "merged.pdf", "size_bytes": 912004, "kind": "result", "expires_at": "…" },
  "download_url": "/api/v1/files/<id>/download"
}
```

**Post-MVP (M8)** the same request returns `202 {"job_id": "…"}` and the result is fetched from `GET /jobs/{id}`. Clients should treat the tool response as "either a result or a job" from day one.

**File management**

| Method | Path | Success | Description |
| --- | --- | --- | --- |
| `GET` | `/files` | `200` | My non-expired files (paginated) |
| `GET` | `/files/{id}` | `200` | Metadata (owner only; otherwise `404`) |
| `GET` | `/files/{id}/download` | `200` | Streams file; `Content-Disposition: attachment`, `X-Content-Type-Options: nosniff` |
| `DELETE` | `/files/{id}` | `204` | Delete file from disk and DB |

### 6.3 Errors

Every error body: `{"detail": "<human message>", "code": "<MACHINE_CODE>"}` (validation errors from FastAPI keep their standard list shape under `detail`).

| HTTP | `code` | When |
| --- | --- | --- |
| 401 | `NOT_AUTHENTICATED` / `TOKEN_EXPIRED` / `TOKEN_INVALID` | Missing/invalid access token |
| 401 | `INVALID_CREDENTIALS` | Login failure |
| 404 | `NOT_FOUND` | Missing **or not owned** |
| 409 | `EMAIL_TAKEN` | Duplicate registration |
| 413 | `FILE_TOO_LARGE` | Exceeds per-file or total size |
| 415 | `UNSUPPORTED_MEDIA_TYPE` | Not a PDF / allowed image (magic-byte check) |
| 422 | `INVALID_PDF` | Corrupt or unparsable |
| 422 | `ENCRYPTED_PDF` | Password-protected input |
| 422 | `TOO_MANY_PAGES` | Over page limit |
| 422 | `INVALID_RANGE` / `INVALID_OPTION` | Bad tool parameters |
| 429 | `RATE_LIMITED` | Includes `Retry-After` |
| 503 | `SERVICE_UNAVAILABLE` | Dependency down |
| 504 | `PROCESSING_TIMEOUT` | Exceeded processing limit |

Status-code conventions live in `rules.md` §12.

---

## 7. Functional Requirements

### 7.1 Authentication and sessions

- **FR-A-Password:** minimum 8 characters, maximum 128; reject a small blocklist of very common passwords *(proposed)*; Argon2 via `pwdlib`.
- **FR-A-Tokens:** access token HS256, 30 min; refresh token HS256, 7 days; separate secrets; `type` claim validated; refresh tokens stored only as SHA-256 hashes; each has a `family_id`.
- **FR-A-Rotate:** each `/auth/refresh` revokes the presented token and issues a new pair in the same family. Presenting an already-revoked token revokes the family.
- **FR-A8 (multi-tab):** the browser client serialises refreshes with `navigator.locks` and re-reads stored tokens after acquiring the lock. Optionally the server accepts a just-rotated token for a short grace period (≤ 10 s) and returns the existing successor rather than treating it as theft.

### 7.2 Account-security behaviours

- `POST /auth/forgot-password` **always** returns `202` with the same body and comparable timing, whether or not the email exists.
- Reset tokens: random ≥ 32 bytes, SHA-256 hashed at rest, expire in 30 minutes, single use; on success, **revoke all refresh-token families** for the user.
- Login and forgot-password are throttled per email **and** per IP (M6).
- Registration necessarily reveals duplicate emails (`409`); this is an accepted trade-off for usability and is rate-limited.
- Never log passwords, tokens or reset links (in production the email backend must not write links to logs).

### 7.3 File lifecycle, limits and privacy

**Lifecycle:** `uploaded → (processed → result created) → expired/deleted`. Both uploads and results expire.

**Limits (proposed defaults; all configurable via settings, and surfaced to the UI):**

| Setting | Default | Notes |
| --- | --- | --- |
| `MAX_UPLOAD_MB` (per file) | 25 | Nginx `client_max_body_size` must match |
| `MAX_TOTAL_UPLOAD_MB` (per request) | 100 | |
| `MAX_FILES_PER_JOB` | 10 | Merge / images→PDF |
| `MAX_PDF_PAGES` | 300 | |
| `MAX_IMAGE_PIXELS` | 50 000 000 | Guards decompression bombs |
| `PROCESS_TIMEOUT_SECONDS` | 60 | → `504 PROCESSING_TIMEOUT` |
| `MAX_CONCURRENT_JOBS` | 2 × CPU cores | Semaphore around processing |
| `FILE_RETENTION_MINUTES` | 60 | Applies to uploads and results |
| `USER_STORAGE_QUOTA_MB` | 200 | Prevents hoarding within retention window |

**Validation rules (all enforced server-side):**

1. Determine type from **magic bytes** (`%PDF-`, PNG/JPEG signatures), not from extension or `Content-Type`.
2. Enforce size while **streaming** to disk; abort early on overflow.
3. Parse to count pages; detect encryption; reject over limits.
4. Images: verify with Pillow, enforce pixel cap, respect EXIF orientation.
5. Store under a server-generated UUID key; **never** use the client filename for any filesystem path. The original name is display metadata only (sanitised).
6. Every file query is filtered by `user_id` (no IDOR).

**Retention enforcement:** a periodic cleanup (in-process background loop for MVP; Celery beat in M8) plus a startup sweep deletes expired rows and their files. The UI shows the expiry time on every file.

### 7.4 Tool behaviour details

| Tool | Notes |
| --- | --- |
| Rotate | Adds to any existing `/Rotate` value modulo 360; untouched pages preserved |
| Merge | Preserves bookmarks where feasible; output name sanitised |
| Split | `ranges` grammar: `1-3,5,8-` (open end = last page), 1-based, overlapping ranges allowed; `every_n` ≥ 1; results zipped when > 1 output |
| Compress | Levels map to concrete techniques (stream compression, object dedup, image downsampling/recompression where the library supports it); report before/after size; never return a larger file |
| PDF → Images | DPI 72–300 (default 150); page-count × pixel cap enforced *before* rendering |
| Images → PDF | JPG/PNG (WebP optional); `fit` sizes each page to its image |

---

## 8. Data Model

`TimestampMixin` = `created_at`, `updated_at` (server-side `func.now()`).

### users

| Column | Type | Constraints |
| --- | --- | --- |
| id | Integer | PK |
| email | String(320) | Unique (case-insensitive index on `lower(email)`), not null |
| hashed_password | String(255) | Not null |
| full_name | String(100) | Nullable |
| is_active | Boolean | Default true |
| is_superuser | Boolean | Default false |
| last_login_at | DateTime(tz) | Nullable |
| created_at / updated_at | DateTime(tz) | Auto |

### refresh_tokens

| Column | Type | Constraints |
| --- | --- | --- |
| id | Integer | PK |
| user_id | Integer | FK → users(id) ON DELETE CASCADE, indexed |
| token_hash | String(64) | Unique, not null |
| family_id | UUID | Not null, indexed |
| expires_at | DateTime(tz) | Not null, indexed |
| revoked_at | DateTime(tz) | Nullable |
| **created_at** | DateTime(tz) | **New** — needed for auditing and grace window |
| **replaced_by_id** | Integer | **New**, nullable, self-FK — supports the multi-tab grace window |

### password_resets

| Column | Type | Constraints |
| --- | --- | --- |
| id | Integer | PK |
| user_id | Integer | FK → users(id) ON DELETE CASCADE, indexed |
| token_hash | String(64) | Unique, not null |
| **expires_at** | DateTime(tz) | **New**, not null — **without it a token never expires** |
| used_at | DateTime(tz) | Nullable |
| **created_at** | DateTime(tz) | **New** |

### pdf_files *(new, Milestone 3)*

| Column | Type | Constraints |
| --- | --- | --- |
| id | UUID | PK |
| user_id | Integer | FK → users(id) ON DELETE CASCADE, indexed |
| kind | Enum(`upload`,`result`) | Not null |
| original_name | String(255) | Sanitised display name |
| storage_key | String(255) | Unique; server-generated; relative to storage root |
| content_type | String(100) | Detected type |
| size_bytes | BigInteger | Not null |
| sha256 | String(64) | Nullable (integrity/dedup) |
| page_count | Integer | Nullable (images: null) |
| source_file_ids | JSON | Nullable (provenance for results) |
| created_at | DateTime(tz) | Auto |
| expires_at | DateTime(tz) | Not null, indexed (cleanup) |
| deleted_at | DateTime(tz) | Nullable |

### pdf_jobs *(post-MVP, Milestone 8)*

`id UUID`, `user_id`, `tool`, `status` (`queued|running|succeeded|failed`), `options JSON`, `input_file_ids JSON`, `result_file_id`, `error_code`, `created_at`, `started_at`, `finished_at`.

---

## 9. Success Metrics *(proposed targets — measure from the first beta)*

| Metric | Target | How measured |
| --- | --- | --- |
| Activation: register → first successful tool run | ≥ 70 % of registrants; median ≤ 90 s | Server events |
| Tool success rate (non-user-error) | ≥ 98 % | Structured logs |
| Latency p95, merge of 5 × 2 MB PDFs | ≤ 3 s | Load test / logs |
| Latency p95, compress 10 MB PDF | ≤ 15 s | Load test / logs |
| Retention compliance | 100 % of expired files deleted within 10 minutes of expiry | Cleanup job metrics |
| Auth correctness | 0 false forced-logouts in the multi-tab test | Automated/manual test |
| Test coverage | ≥ 85 % services, ≥ 75 % overall | CI |
| Open High-severity security findings at launch | 0 | `ANALYSIS.md` / issue tracker |
| Accessibility | Lighthouse a11y ≥ 95; axe: 0 serious/critical; keyboard-only path for each tool | CI + manual |

---

## 10. Non-Functional Requirements

### Security (details in `ANALYSIS.md` §7)

- NFR-S1: Argon2 passwords; JWT with `exp`, `type`, separate secrets.
- NFR-S2: Refresh rotation with reuse detection and multi-tab tolerance.
- NFR-S3: Strict CSP (`script-src 'self'`), `X-Content-Type-Options: nosniff`, `frame-ancestors 'none'`, `Referrer-Policy`, HSTS (production).
- NFR-S4: No inline JS/CSS event handlers; DOM writes use `textContent` or `escapeHTML`.
- NFR-S5: Rate limiting on auth, upload and tool endpoints.
- NFR-S6: File validation, ownership checks, UUID storage keys, no shell-outs on user input.
- NFR-S7: Secrets only in environment; secret scanning in CI; log redaction.
- NFR-S8: Dependency audit (`pip-audit`) in CI.

### Performance and scalability

- NFR-P1: Async I/O; PDF work runs in `asyncio.to_thread` behind a semaphore (never on the event loop).
- NFR-P2: DB pool `pool_size=5`, `max_overflow=10`.
- NFR-P3: Stateless API tier (JWT). Storage behind an interface (`LocalStorage` → S3/MinIO).
- NFR-P4: Service functions are pure (`Path/bytes in → Path/bytes out`) so they run unchanged inside Celery later.

### Reliability and operability

- NFR-R1: Health endpoints (live/ready split before launch); graceful shutdown via lifespan; rollback on error.
- NFR-R2: Temp files always cleaned up (`try/finally` or context manager), including on timeout.
- NFR-R3: Structured logs with request IDs; no PII/tokens.
- NFR-R4: Postgres backups and a tested restore before launch.

### Accessibility and UX

- NFR-A1: WCAG 2.2 AA (details in `design.md` §8).
- NFR-A2: Works on a 360 px-wide phone and with keyboard only.

---

## 11. Technical Stack and Dependency Policy

| Layer | Technology | Note |
| --- | --- | --- |
| Backend | Python 3.12+, FastAPI | |
| Database | PostgreSQL 14+ via `asyncpg` | |
| ORM / migrations | SQLAlchemy 2.x async, Alembic | Alembic must read the URL from app settings |
| Auth | PyJWT, `pwdlib[argon2]` | |
| Config | `pydantic-settings`, `.env` | |
| **PDF (decision D3)** | `pypdf` (merge/split/rotate/basic compress), `pypdfium2` (render), `Pillow` + `ReportLab` (images→PDF) | Permissive licences. **Avoid PyMuPDF / Ghostscript** unless AGPL is accepted or a commercial licence is bought |
| Background (post-MVP) | Celery + Redis | Not required for MVP |
| Frontend (MVP) | Server-rendered HTML + vanilla JS, tokens as CSS variables | React + Vite is post-MVP (D2) |
| Testing | pytest, pytest-asyncio, httpx | In `requirements-dev.txt` |
| Quality | Ruff (lint + format), mypy | Config in `pyproject.toml` |

**Dependency policy:** before adding a library, record its licence and why an existing one cannot do the job (in the PR). Verify licences yourself — this document is not legal advice.

---

## 12. Out of Scope (MVP)

PDF ↔ Word/Excel/PowerPoint · OCR · e-signature · in-browser PDF editing/annotation · watermark/protect/unlock · mobile and desktop apps · teams/sharing · subscriptions/billing · S3 storage · public developer API/keys · guest (no-account) usage · multi-language UI.

---

## 13. Constraints, Assumptions and Risks

**Constraints**

1. PostgreSQL is the database.
2. MVP stores files on the server filesystem (`storage/`), never in PostgreSQL; access through a storage interface.
3. Celery/Redis are **not** required for MVP (D1); the configuration may exist but nothing in MVP depends on it.
4. All secrets come from `.env` / environment; nothing hard-coded, nothing in docs.
5. Every dependency must have a compatible licence (D3).

**Assumptions**

- Single-region deployment; one app instance is enough for beta.
- Typical inputs are ≤ 25 MB and ≤ 300 pages.
- A transactional email provider (or SMTP) is available before launch.

**Top risks** (full register: `ANALYSIS.md` §8): AGPL exposure (R1), scope creep (R2), compression quality (R3), solo-developer bandwidth (R6).

---

## 14. Open Questions

| # | Question | Default used in this PRD |
| --- | --- | --- |
| Q1 | Allow **guest** use (no account) for small files, like iLovePDF? | No — login required in MVP |
| Q2 | Are the limits in §7.3 right for your hosting budget? | As listed |
| Q3 | Which email provider (SES, Postmark, Resend, SMTP)? | SMTP-agnostic interface; console backend in dev |
| Q4 | Which hosting region / data-residency statement? | Undecided — needed for the privacy page |
| Q5 | Business model: subscription, ads, or donation? | Ad-free free tier; billing is future |
| Q6 | Is a commercial PyMuPDF licence acceptable if quality demands it? | No — permissive stack |

---

## 15. Release Plan

| Phase | Scope | Exit criteria |
| --- | --- | --- |
| **Alpha** (internal) | M2–M3 + Rotate & Merge with minimal UI | Upload/validate/expire works; multi-tab test passes |
| **Beta** (invite) | All six tools, full web UI, rate limiting, CSP | Metrics in §9 measured; 0 open High findings |
| **v1.0** (public) | Docker/Nginx, privacy page, backups, monitoring | Release checklist (tasks M7) complete |
| **v1.1+** | Settings, history, Celery jobs, more tools | Driven by beta feedback |
