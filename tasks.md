# FileNest — Tasks & Progress

**Version:** 0.1.0  
**Date:** 2026-09-20  
**Status:** Auth MVP complete, PDF tools pending

---

## Status Legend

| Symbol | Meaning |
| --- | --- |
| ✅ | Done — implemented and working |
| ⚠️ | Partial — needs completion step |
| ❌ | Not started |
| 🔄 | In progress |

---

## Milestones

### Milestone 1: Auth & Infrastructure — ✅ Complete

- [x] FastAPI application setup (`app/main.py`)
- [x] Async SQLAlchemy 2.x configuration
- [x] Database models (User, RefreshToken, PasswordReset)
- [x] Alembic migrations (`alembic/versions/7697cdbf4561_init.py`)
- [x] JWT authentication (access + refresh tokens)
- [x] Refresh token rotation with reuse detection
- [x] Password hashing (Argon2 via pwdlib)
- [x] CORS middleware
- [x] Static file serving
- [x] Environment configuration (`.env`, `.env.example`)
- [x] Integration tests for auth API

---

### Milestone 2: PDF Tools — 🔄 In Progress

#### Infrastructure

| Task | Status | Notes |
| --- | --- | --- |
| Install PyMuPDF | ❌ | Add to requirements.txt |
| Install pypdf | ❌ | Add to requirements.txt |
| Install ReportLab | ❌ | Add to requirements.txt |
| Storage service abstraction | ❌ | `app/services/storage.py` |
| File upload endpoint | ❌ | `POST /api/v1/files/upload` |
| File download endpoint | ❌ | `GET /api/v1/files/{id}` |
| File metadata model (`PdfFile`) | ❌ | `app/models/pdf_file.py` |
| File metadata schema | ❌ | `app/schemas/pdf_file.py` |
| File migration | ❌ | Alembic version |
| Storage directories (`uploads/`, `processed/`, `temp/`) | ❌ | Create at project root |

#### PDF Merge

| Task | Status | Notes |
| --- | --- | --- |
| Merge service | ❌ | `app/services/pdf_merge.py` |
| Merge route | ❌ | `POST /api/v1/pdf/merge` |
| Merge schema (request/response) | ❌ | `app/schemas/pdf_merge.py` |
| Merge tests | ❌ | `tests/test_pdf_merge.py` |

#### PDF Split

| Task | Status | Notes |
| --- | --- | --- |
| Split service | ❌ | `app/services/pdf_split.py` |
| Split route | ❌ | `POST /api/v1/pdf/split` |
| Split schema | ❌ | `app/schemas/pdf_split.py` |
| Split tests | ❌ | `tests/test_pdf_split.py` |

#### PDF Compress

| Task | Status | Notes |
| --- | --- | --- |
| Compress service | ❌ | `app/services/pdf_compress.py` |
| Compress route | ❌ | `POST /api/v1/pdf/compress` |
| Compress schema | ❌ | `app/schemas/pdf_compress.py` |
| Compress tests | ❌ | `tests/test_pdf_compress.py` |

#### PDF Rotate

| Task | Status | Notes |
| --- | --- | --- |
| Rotate service | ❌ | `app/services/pdf_rotate.py` |
| Rotate route | ❌ | `POST /api/v1/pdf/rotate` |
| Rotate schema | ❌ | `app/schemas/pdf_rotate.py` |
| Rotate tests | ❌ | `tests/test_pdf_rotate.py` |

#### PDF Convert

| Task | Status | Notes |
| --- | --- | --- |
| PDF to Images service | ❌ | `app/services/pdf_to_images.py` |
| Images to PDF service | ❌ | `app/services/images_to_pdf.py` |
| Convert routes | ❌ | `POST /api/v1/pdf/to-images`, `POST /api/v1/pdf/from-images` |
| Convert schemas | ❌ | `app/schemas/pdf_convert.py` |
| Convert tests | ❌ | `tests/test_pdf_convert.py` |

---

### Milestone 3: Frontend (React + Vite) — ❌ Not Started

- [ ] React + Vite project setup
- [ ] Tailwind CSS configured
- [ ] Axios installed and configured
- [ ] Dashboard page
- [ ] PDF tool pages (merge, split, compress, rotate, convert)
- [ ] File manager page
- [ ] Drag-and-drop file upload component
- [ ] PDF preview component
- [ ] File selection UI
- [ ] Page reordering UI
- [ ] Processing progress indicators
- [ ] Download results component
- [ ] User dashboard with file history
- [ ] Forgot password page
- [ ] Reset password page

---

### Milestone 4: Background Processing — ❌ Not Started

- [ ] Redis setup and configuration
- [ ] Celery worker processes
- [ ] Job queue integration
- [ ] PDF worker processes
- [ ] Job status endpoints (`GET /api/v1/jobs/{id}`)
- [ ] Job result endpoints

---

### Milestone 5: Deployment — ❌ Not Started

- [ ] Dockerfile (backend)
- [ ] Dockerfile (frontend)
- [ ] Docker Compose (all services)
- [ ] Nginx configuration
- [ ] Production deployment guide
- [ ] CI/CD setup (GitHub Actions / GitLab CI)

---

### Milestone 6: Security Hardening — ❌ Not Started

- [ ] File type validation (PDF, images only)
- [ ] File size limits
- [ ] Rate limiting (per endpoint or per IP)
- [ ] Request logging/audit
- [ ] CSRF protection
- [ ] Content Security Policy headers

---

### Milestone 7: Testing — ⚠️ Partial

- [x] Auth integration tests (`tests/test_auth.py`)
- [x] Test fixtures (`tests/conftest.py`)
- [ ] PDF processing unit tests
- [ ] API endpoint tests for PDF tools
- [ ] Frontend tests
- [ ] Security tests (auth bypass, injection)

---

### Milestone 8: Documentation — ⚠️ Partial

- [x] `README.md` — quick start, stop instructions
- [x] `PROJECT_STACK.md` — technology stack and architecture
- [x] `prd.md` — Product Requirements Document
- [x] `architecture.md` — Project Architecture
- [x] `rules.md` — Coding Rules
- [x] `design.md` — UI/UX Direction
- [x] `tasks.md` — Tasks & Progress
- [x] `memory.md` — Project Context
- [ ] API docs (auto at `/docs`)
- [ ] Setup guide
- [ ] Deployment guide

---

## Summary

| Milestone | Status |
| --- | --- |
| 1. Auth & Infrastructure | ✅ Complete |
| 2. PDF Tools | 🔄 In Progress |
| 3. Frontend (React) | ❌ Not Started |
| 4. Background Processing | ❌ Not Started |
| 5. Deployment | ❌ Not Started |
| 6. Security Hardening | ❌ Not Started |
| 7. Testing | ⚠️ Partial |
| 8. Documentation | ⚠️ Partial |

**MVP Completion: ~25%**
