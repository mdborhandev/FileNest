"""Celery tasks for FileNest."""

from __future__ import annotations

import base64
import logging
import tempfile
from pathlib import Path
from uuid import uuid4

from app.services.converter import convert
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)

# Where converted files are stored temporarily before download.
CONVERT_DIR = Path(tempfile.gettempdir()) / "filenest_conversions"
CONVERT_DIR.mkdir(parents=True, exist_ok=True)


def _store(data: bytes, to_format: str) -> str:
    """Persist converted bytes and return a download token (filename)."""
    token = f"{uuid4().hex}.{to_format.lower()}"
    (CONVERT_DIR / token).write_bytes(data)
    return token


def _read(token: str) -> bytes:
    return (CONVERT_DIR / token).read_bytes()


def _cleanup(token: str) -> None:
    try:
        (CONVERT_DIR / token).unlink(missing_ok=True)
    except OSError:
        logger.warning("Failed to cleanup conversion file %s", token, exc_info=True)


def convert_document(
    data: bytes,
    from_format: str,
    to_format: str,
) -> str:
    """Synchronously convert a document and return a download token."""
    result = convert(data, from_format, to_format)
    return _store(result, to_format)


@celery_app.task(name="app.workers.tasks.convert_document_async")
def convert_document_async(
    data_b64: str,
    from_format: str,
    to_format: str,
) -> str:
    """Async conversion task.

    ``data_b64`` is a base64-encoded string of the source file so the task
    payload stays JSON-serializable.
    """
    data = base64.b64decode(data_b64)
    token = convert_document(data, from_format, to_format)
    return token


def get_download_token(data: bytes, from_format: str, to_format: str) -> str:
    """Run conversion synchronously and return a download token."""
    return convert_document(data, from_format, to_format)


def fetch_conversion(token: str) -> bytes:
    """Retrieve a converted file by token and clean it up."""
    data = _read(token)
    _cleanup(token)
    return data