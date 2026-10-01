"""Format conversion logic for FileNest.

Supported conversions (no authentication required):

| From  | To    | Method                                             |
| ----- | ----- | -------------------------------------------------- |
| pdf   | txt   | Extract text with pypdf                            |
| pdf   | html  | Wrap extracted text in a simple HTML document      |
| pdf   | docx  | Create a docx with one paragraph per page          |
| txt   | pdf   | Render text to PDF with reportlab                  |
| docx  | txt   | Extract paragraphs with python-docx               |
| docx  | pdf   | Re-serialize paragraphs to PDF with reportlab      |

All conversions run synchronously in-process. Large files may be offloaded
to Celery by the route layer.
"""

from __future__ import annotations

import io
import logging
from collections.abc import Callable
from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Font handling
# ---------------------------------------------------------------------------

_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSansMono.ttf",
]

_font_registered = False


def _register_font() -> str:
    """Register the first available TrueType font and return its name."""
    global _font_registered
    if _font_registered:
        return "DejaVuSans"
    for candidate in _FONT_CANDIDATES:
        path = Path(candidate)
        if path.exists():
            try:
                pdfmetrics.registerFont(TTFont("DejaVuSans", str(path)))
                pdfmetrics.registerFont(TTFont("DejaVuSansMono", str(path)))
                _font_registered = True
                return "DejaVuSans"
            except Exception:
                logger.debug("Failed to register font at %s", candidate, exc_info=True)
    _font_registered = True
    return "Helvetica"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_pdf_text(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages)


def _as_text(data: bytes | str) -> str:
    """Coerce ``data`` to ``str``, decoding bytes as UTF-8 when needed."""
    if isinstance(data, str):
        return data
    return data.decode("utf-8", errors="replace")


def _to_bytes(text: str, encoding: str = "utf-8") -> bytes:
    """Encode ``text`` to bytes, returning the input unchanged if already bytes."""
    if isinstance(text, bytes):
        return text
    return text.encode(encoding)


def _escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _wrap_html(text: str, title: str = "FileNest conversion") -> str:
    body = "\n".join(
        f"<p>{_escape_html(block)}</p>" for block in text.split("\n\n")
    )
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '    <meta charset="utf-8">\n'
        f"    <title>{_escape_html(title)}</title>\n"
        "    <style>\n"
        "        body { font-family: sans-serif; max-width: 800px; margin: 2rem auto; line-height: 1.5; }\n"
        "        p { white-space: pre-wrap; }\n"
        "    </style>\n"
        "</head>\n"
        "<body>\n"
        f"{body}\n"
        "</body>\n"
        "</html>"
    )


def _text_to_pdf(text: bytes | str) -> bytes:
    text = _as_text(text)
    font_name = _register_font()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72,
    )
    styles = getSampleStyleSheet()
    style: ParagraphStyle = styles["Normal"]
    style.fontName = font_name
    story = [
        Paragraph(_escape_html(block), style)
        for block in text.split("\n\n")
    ]
    doc.build(story)
    return buffer.getvalue()


def _docx_to_text(data: bytes) -> str:
    doc = DocxDocument(io.BytesIO(data))
    paragraphs = [p.text for p in doc.paragraphs if p.text]
    return "\n\n".join(paragraphs)


def _text_to_docx(text: bytes | str) -> bytes:
    text = _as_text(text)
    doc = DocxDocument()
    for block in text.split("\n\n"):
        doc.add_paragraph(block)
    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


def _text_to_html(text: bytes | str) -> bytes:
    return _to_bytes(_wrap_html(_as_text(text)))


def _pdf_to_docx(data: bytes) -> bytes:
    return _text_to_docx(_read_pdf_text(data))


def _docx_to_pdf(data: bytes) -> bytes:
    return _text_to_pdf(_docx_to_text(data))


def _text_to_bytes(fn: ConversionFn) -> ConversionFn:
    """Wrap a converter that returns ``str`` so it returns ``bytes``."""

    def _wrapper(data: bytes) -> bytes:
        return _to_bytes(fn(data))

    return _wrapper


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

ConversionFn = Callable[[bytes], bytes]

_CONVERSIONS: dict[tuple[str, str], ConversionFn] = {
    ("pdf", "txt"): _text_to_bytes(_read_pdf_text),
    ("pdf", "html"): _text_to_bytes(lambda d: _wrap_html(_read_pdf_text(d))),
    ("pdf", "docx"): _pdf_to_docx,
    ("txt", "pdf"): _text_to_pdf,
    ("txt", "html"): _text_to_html,
    ("txt", "docx"): _text_to_docx,
    ("docx", "txt"): _text_to_bytes(_docx_to_text),
    ("docx", "pdf"): _docx_to_pdf,
    ("docx", "html"): _text_to_bytes(lambda d: _wrap_html(_docx_to_text(d))),
}


def supported_conversions() -> list[tuple[str, str]]:
    """Return the list of supported (from, to) pairs."""
    return sorted(_CONVERSIONS.keys())


def convert(data: bytes, from_format: str, to_format: str) -> bytes:
    """Convert ``data`` from ``from_format`` to ``to_format``.

    Raises ``ValueError`` for unsupported format pairs.
    """
    from_fmt = from_format.lower().lstrip(".")
    to_fmt = to_format.lower().lstrip(".")
    key = (from_fmt, to_fmt)
    if from_fmt == to_fmt:
        raise ValueError("Source and target formats must differ")
    if key not in _CONVERSIONS:
        supported = ", ".join(f"{f}->{t}" for f, t in supported_conversions())
        raise ValueError(
            f"Unsupported conversion {from_fmt}->{to_fmt}. "
            f"Supported: {supported}"
        )
    return _CONVERSIONS[key](data)