# FileNest — Product Requirements Document

**Version:** 0.1.0  
**Date:** 2026-09-20  
**Status:** MVP in development

---

## 1. Product Overview

FileNest is an online PDF tools platform — an iLovePDF-style SaaS application that lets users manage, convert, and process PDF documents through a web interface. Users register, log in, and access a suite of PDF utilities (merge, split, compress, rotate, convert) with file upload/download and background processing.

### Problem Statement

Users need a secure, fast, browser-based tool for everyday PDF operations without installing desktop software. The platform must handle sensitive documents with privacy-first design and provide reliable background processing for large files.

### Target Users

- Individuals who need occasional PDF manipulation (students, professionals)
- Small teams sharing PDF workflows
- Users who value privacy and do not want to upload sensitive files to unknown services

### Core Value Proposition

- Free-to-use core tools with no credit card required
- JWT-based secure authentication with refresh-token rotation
- Fast async processing pipeline
- Background job processing for long-running operations
- Clean, focused UI for PDF workflows

---

## 2. Features

### MVP Features

| Feature | Description | Priority |
| --- | --- | --- |
| User registration | Create account with email, password, optional full name | High |
| User login | Email/password authentication, returns JWT pair | High |
| Token refresh | Rotate refresh tokens, revoke on reuse | High |
| Logout | Revoke refresh token and its family | High |
| Profile lookup | Get current user info (`GET /api/v1/auth/me`) | High |
| Password reset | Email token-based password reset flow | High |
| Health check | Database connectivity check (`GET /api/v1/health`) | High |
| Landing page | Public landing with feature cards and CTA | High |
| Login page | Email/password form with validation | High |
| Register page | Multi-field form with validation | High |
| PDF Merge | Combine multiple PDFs into one | Medium |
| PDF Split | Split PDF by pages or ranges | Medium |
| PDF Compress | Reduce PDF file size | Medium |
| PDF Rotate | Rotate pages by angle | Medium |
| PDF to Images | Render PDF pages as images | Medium |
| Images to PDF | Combine images into a PDF | Medium |

### Future Features

- PDF to Word / Word to PDF conversion
- PDF to Excel / PowerPoint conversion
- Watermark, protect, unlock PDF
- OCR processing
- User dashboard with file history
- Drag-and-drop file upload
- File selection UI, page reordering UI
- Processing progress indicators
- Subscription and billing
- S3-compatible cloud storage

---

## 3. User Stories

### Authentication

1. As a new user, I want to register with email and password so I can access the platform.
2. As a returning user, I want to log in so I can use PDF tools.
3. As a logged-in user, I want my session to persist via refresh tokens so I don't lose auth state.
4. As a user, I want my refresh token to rotate on use so stolen tokens expire quickly.
5. As a user, I want to log out so my session is fully revoked.
6. As a user who forgot my password, I want to reset it via email.

### PDF Tools (MVP)

7. As a user, I want to merge multiple PDFs so I can combine documents.
8. As a user, I want to split a PDF by page range so I can extract sections.
9. As a user, I want to compress a PDF so it's smaller for sharing.
10. As a user, I want to rotate PDF pages so they're in the correct orientation.
11. As a user, I want to convert PDF to images so I can preview or extract pages.
12. As a user, I want to combine images into a PDF so I can create PDFs from photos.

---

## 4. Non-Functional Requirements

### Security

- Passwords hashed with Argon2 (via `pwdlib`)
- JWT access tokens (HS256, 30-min expiry) and refresh tokens (HS256, 7-day expiry)
- Refresh tokens stored as SHA-256 hashes in the database
- Refresh-token rotation with reuse detection (replay revokes entire family)
- CORS configured via environment variables
- `.env` never committed to version control
- Input validation on all user-facing endpoints
- File type and size validation (upcoming)
- Rate limiting (upcoming)

### Performance

- Async I/O throughout (async SQLAlchemy, async endpoints)
- Database connection pooling (pool_size=5, max_overflow=10)
- Background processing via Celery + Redis for long-running PDF operations
- File processing outside the request/response cycle where possible

### Scalability

- Stateless API tier (JWT-based, no server-side sessions)
- Storage service abstracted for future S3/MinIO migration
- Celery workers can be horizontally scaled
- Database: PostgreSQL 14+

### Reliability

- Database health check endpoint
- Graceful shutdown via FastAPI lifespan
- Refresh-token family revocation on reuse
- Transaction rollback on errors in database sessions

---

## 5. Technical Stack

| Layer | Technology |
| --- | --- |
| Backend framework | Python 3.12+, FastAPI |
| Database | PostgreSQL 14+ (async via `asyncpg`) |
| ORM | SQLAlchemy 2.x (async) |
| Migrations | Alembic |
| Authentication | JWT (PyJWT), pwdlib Argon2 |
| Configuration | pydantic-settings, `.env` |
| Background jobs | Celery + Redis |
| Frontend | Server-rendered HTML + vanilla JS (MVP), React + Vite (future) |
| Testing | pytest, pytest-asyncio, httpx |
| Linting | Ruff (implied by `.ruff_cache`) |

---

## 6. API Design

All endpoints are prefixed with `/api/v1`.

### Auth endpoints

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/auth/register` | No | Create user |
| `POST` | `/auth/login` | No | Returns access + refresh token |
| `POST` | `/auth/refresh` | No | Rotate refresh token |
| `POST` | `/auth/logout` | No | Revoke refresh token |
| `GET` | `/auth/me` | Bearer token | Get current user |
| `POST` | `/auth/forgot-password` | No | Initiate password reset |
| `POST` | `/auth/reset-password` | No | Reset password with token |

### Health endpoint

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/health` | No | Database connectivity check |

### PDF tool endpoints (planned)

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/pdf/merge` | Bearer token | Merge PDFs |
| `POST` | `/pdf/split` | Bearer token | Split PDF |
| `POST` | `/pdf/compress` | Bearer token | Compress PDF |
| `POST` | `/pdf/rotate` | Bearer token | Rotate pages |
| `POST` | `/pdf/to-images` | Bearer token | PDF to images |
| `POST` | `/pdf/from-images` | Bearer token | Images to PDF |

---

## 7. Data Model

### users

| Column | Type | Constraints |
| --- | --- | --- |
| id | Integer | PK |
| email | String(320) | Unique, not null |
| hashed_password | String(255) | Not null |
| full_name | String(100) | Nullable |
| is_active | Boolean | Default true |
| is_superuser | Boolean | Default false |
| last_login_at | DateTime | Nullable |
| created_at | DateTime | Auto-set |
| updated_at | DateTime | Auto-set |

### refresh_tokens

| Column | Type | Constraints |
| --- | --- | --- |
| id | Integer | PK |
| user_id | Integer | FK → users(id), CASCADE |
| token_hash | String(64) | Unique, not null (SHA-256 of token) |
| family_id | UUID | Not null (groups tokens from one login) |
| expires_at | DateTime | Not null |
| revoked_at | DateTime | Nullable |

### password_resets

| Column | Type | Constraints |
| --- | --- | --- |
| id | Integer | PK |
| user_id | Integer | FK → users(id), CASCADE |
| token_hash | String(64) | Unique, not null |
| used_at | DateTime | Nullable |

---

## 8. Constraints & Assumptions

1. PostgreSQL is the fixed database — no migration to other databases planned.
2. Redis is required for Celery background processing.
3. Files are stored on the server filesystem in `storage/` directories (not in PostgreSQL) for MVP.
4. PDF processing libraries (PyMuPDF, pypdf, ReportLab) are planned but not yet installed.
5. Frontend in MVP is server-rendered static HTML/JS; React frontend is planned as a future separate service.
6. All secrets are loaded from `.env`; never hard-coded.
7. Celery/Redis should NOT be implemented in MVP per `PROJECT_STACK.md` — infrastructure is designed for future introduction.

---

## 9. Success Criteria

- Users can register, log in, and access protected endpoints with JWT.
- Refresh token rotation prevents replay attacks (reuse revokes the whole family).
- Database health check returns accurate status.
- PDF tools process files correctly and return downloadable results.
- All API responses are consistent (JSON with appropriate HTTP status codes).
- Test coverage for core auth flows and PDF operations.
