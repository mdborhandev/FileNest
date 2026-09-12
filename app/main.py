from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api.v1.router import router as api_router
from app.core.config import settings
from app.core.database import dispose_db


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield
    await dispose_db()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)

STATIC_DIR = Path(__file__).resolve().parent / "static"
LANDING_PAGE = STATIC_DIR / "index.html"


@app.get("/", include_in_schema=False)
async def root() -> FileResponse:
    return FileResponse(LANDING_PAGE)
