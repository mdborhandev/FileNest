# FileNest — Project Stack

iLovePDF-style online PDF utility SaaS.

## Frontend

* React
* Vite
* Tailwind CSS
* Axios

Purpose:

* Modern interactive PDF tool interface
* Drag-and-drop file upload
* PDF preview
* File selection
* Page reordering
* Processing progress
* Download results
* User dashboard
* Authentication UI

## Backend

* Python
* FastAPI
* SQLAlchemy 2.x
* Pydantic
* Alembic

Backend responsibilities:

* REST APIs
* Authentication
* User management
* PDF upload management
* PDF processing requests
* Job/status management
* File management
* Subscription-related APIs in future versions

## Database

PostgreSQL is the fixed database for this project.

Development database:

* Database: `filenest_dev`
* Host: `localhost`
* Port: `5432`
* User: `postgres`

Store secrets in `.env`. Never commit passwords or API keys to Git.

## PDF Processing Libraries

Use specialized libraries for different PDF operations:

### PyMuPDF

Use for:

* PDF reading
* PDF rendering
* page rendering/thumbnails
* text extraction
* metadata
* PDF manipulation

### pypdf

Use for:

* Merge PDF
* Split PDF
* Rotate PDF
* Page manipulation

### ReportLab

Use for:

* PDF generation
* Creating PDFs from generated content

### LibreOffice

Use when required for document conversion such as:

* DOCX → PDF
* PPTX → PDF
* XLSX → PDF

## Storage

For the MVP, store uploaded and generated files inside the project/server filesystem.

Suggested structure:

```text
storage/
├── uploads/
├── processed/
└── temp/
```

Do NOT store PDF binary data directly inside PostgreSQL for the MVP.

PostgreSQL should store file metadata, for example:

* file ID
* user ID
* original filename
* stored filename
* file size
* MIME type
* file path
* processing status
* created date
* expiration date

Design the storage service so that it can later be replaced with S3-compatible storage such as MinIO, Cloudflare R2, or Amazon S3 without changing the business logic.

## Background Processing

Do not add Celery/Redis unnecessarily during the initial MVP implementation.

Design the application so background processing can be introduced later.

Future stack:

* Redis
* Celery
* Dedicated PDF workers

These should be documented as future infrastructure rather than required MVP dependencies.

## MVP PDF Tools

The initial MVP should focus on these tools:

1. Merge PDF
2. Split PDF
3. Compress PDF
4. PDF → Images
5. Images → PDF
6. Rotate PDF

Future tools:

7. PDF → Word
8. Word → PDF
9. PDF → Excel
10. PDF → PowerPoint
11. Watermark PDF
12. Protect PDF
13. Unlock PDF
14. OCR PDF

## Backend Architecture

Use a feature/service-oriented architecture.

Suggested structure:

```text
backend/
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── auth.py
│   │   ├── pdf.py
│   │   ├── files.py
│   │   └── users.py
│   │
│   ├── services/
│   │   ├── pdf_merge.py
│   │   ├── pdf_split.py
│   │   ├── pdf_compress.py
│   │   ├── pdf_rotate.py
│   │   └── pdf_convert.py
│   │
│   ├── models/
│   ├── schemas/
│   ├── repositories/
│   ├── core/
│   └── workers/
│
├── tests/
├── requirements.txt
└── Dockerfile
```

Keep PDF processing logic separate from API route handlers.

Example flow:

1. React
2. FastAPI API
3. PDF Service
4. PDF Processing Library
5. Output File

## API Design

Use REST-style endpoints.

Examples:

```text
POST /api/pdf/merge
POST /api/pdf/split
POST /api/pdf/compress
POST /api/pdf/rotate
POST /api/pdf/to-images
POST /api/pdf/from-images
```

Keep the API structure consistent so additional PDF tools can be added easily.

## Database Entities

Initially plan for entities such as:

### users

* id
* email
* password_hash
* created_at
* updated_at

### pdf_files

* id
* user_id
* original_name
* stored_name
* file_size
* mime_type
* file_path
* status
* created_at
* expires_at

### pdf_jobs

* id
* user_id
* tool
* status
* input_file
* output_file
* error_message
* started_at
* completed_at

Future:

### subscriptions

* id
* user_id
* plan
* status
* started_at
* expires_at

## Environment Configuration

Use `.env` for development configuration.

Example structure:

```env
APP_ENV=development

DATABASE_URL=postgresql://postgres:<PASSWORD>@localhost:5432/filenest_dev

STORAGE_PATH=./storage

MAX_UPLOAD_SIZE_MB=100
```

Never place the real database password in source-controlled files.

Also create/update `.env.example` with placeholder values.

## Security Requirements

* Never commit `.env`
* Never hard-code passwords
* Never expose database credentials to React
* Validate uploaded file types
* Validate file sizes
* Generate safe server-side filenames
* Prevent path traversal
* Store uploaded files outside public/static directories
* Delete temporary files after processing
* Add authentication before associating files with users
* Do not trust the original uploaded filename

## Deployment

Initial deployment should support:

* Docker
* Nginx
* FastAPI
* React
* PostgreSQL

Keep the architecture deployable as separate frontend/backend services.

## Important Architecture Principle

Keep the PDF processing engine independent from the API layer.

For example:

```text
Frontend
   ↓
API
   ↓
PDF Service
   ↓
Processing Engine
   ↓
Storage
```

This will allow future migration from synchronous processing to:

```text
API
 ↓
Redis Queue
 ↓
Celery Worker
 ↓
PDF Processing
 ↓
Storage
```

without redesigning the entire application.

## Development Rules

Before adding new dependencies:

1. Check whether an existing dependency can solve the problem.
2. Prefer stable and actively maintained libraries.
3. Keep MVP dependencies minimal.
4. Keep business logic separate from framework-specific code.
5. Keep PDF processing services independently testable.
6. Use environment variables for configuration and secrets.
7. Write tests for core PDF operations.
8. Keep the frontend and backend independently deployable.

## Documentation Goal

This file is the source of truth for the project's initial stack and architecture.

If future implementation decisions change the stack, update `PROJECT_STACK.md` accordingly.

Do not implement the entire application just from this task.
