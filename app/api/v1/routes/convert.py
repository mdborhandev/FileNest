"""Public conversion endpoints (no authentication required)."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response

from app.services.converter import supported_conversions
from app.workers import tasks

logger = logging.getLogger(__name__)

router = APIRouter(tags=["convert"])


@router.get(
    "/convert/formats",
    status_code=status.HTTP_200_OK,
)
async def list_formats() -> dict:
    """Return the list of supported conversions."""
    conversions = supported_conversions()
    return {
        "conversions": [f"{f}->{t}" for f, t in conversions],
        "from_formats": sorted({f for f, _ in conversions}),
        "to_formats": sorted({t for _, t in conversions}),
    }


@router.post(
    "/convert",
    status_code=status.HTTP_200_OK,
)
async def convert_document(
    file: Annotated[UploadFile, File(...)],
    to_format: Annotated[str, Form(...)],
    from_format: Annotated[str | None, Form()] = None,
) -> dict:
    """Convert an uploaded file to ``to_format`` and return a download token.

    The converted file is stored server-side and can be fetched via
    ``GET /api/v1/convert/{token}``.

    ``from_format`` may be omitted; it defaults to the file extension.
    """
    detected = (file.filename or "").rsplit(".", 1)[-1] if "." in (file.filename or "") else ""
    src_format = (from_format or detected or "").lower().lstrip(".")
    if not src_format:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not determine source format. Provide from_format or name the file with an extension.",
        )

    data = await file.read()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file uploaded",
        )

    try:
        token = tasks.get_download_token(data, src_format, to_format)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return {"token": token, "download_url": f"/api/v1/convert/{token}"}


@router.get(
    "/convert/{token}",
    status_code=status.HTTP_200_OK,
)
async def download_conversion(token: str) -> Response:
    """Download a previously converted file by token (single-use)."""
    try:
        data = tasks.fetch_conversion(token)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversion not found or already downloaded",
        ) from exc

    suffix = token.rsplit(".", 1)[-1] if "." in token else "bin"
    filename = f"converted.{suffix}"
    return Response(
        content=data,
        media_type=_media_type(suffix),
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _media_type(suffix: str) -> str:
    return {
        "pdf": "application/pdf",
        "txt": "text/plain",
        "html": "text/html",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }.get(suffix, "application/octet-stream")