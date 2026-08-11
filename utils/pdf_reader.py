from __future__ import annotations

import os
from typing import BinaryIO

import fitz  # PyMuPDF

DEFAULT_MAX_PDF_BYTES = 8 * 1024 * 1024
DEFAULT_MAX_PDF_PAGES = 10


class PDFReadError(ValueError):
    """Raised when an uploaded PDF cannot be read safely."""


class PDFTooLargeError(PDFReadError):
    """Raised when an uploaded PDF exceeds the configured size limit."""


class PDFPageLimitError(PDFReadError):
    """Raised when an uploaded PDF has too many pages for the public demo."""


class PDFEncryptedError(PDFReadError):
    """Raised when an uploaded PDF requires a password."""


def get_max_pdf_bytes() -> int:
    raw_limit = os.getenv("ATS_MAX_PDF_BYTES")
    if not raw_limit:
        return DEFAULT_MAX_PDF_BYTES
    try:
        return max(1, int(raw_limit))
    except ValueError:
        return DEFAULT_MAX_PDF_BYTES


def get_max_pdf_pages() -> int:
    raw_limit = os.getenv("ATS_MAX_PDF_PAGES")
    if not raw_limit:
        return DEFAULT_MAX_PDF_PAGES
    try:
        return max(1, int(raw_limit))
    except ValueError:
        return DEFAULT_MAX_PDF_PAGES


def _format_byte_limit(limit: int) -> str:
    if limit >= 1024 * 1024:
        return f"{limit / (1024 * 1024):.1f} MB"
    if limit >= 1024:
        return f"{limit / 1024:.1f} KB"
    return f"{limit} bytes"


def _read_uploaded_bytes(uploaded_file: BinaryIO) -> bytes:
    if hasattr(uploaded_file, "getvalue"):
        data = uploaded_file.getvalue()
    else:
        try:
            uploaded_file.seek(0)
        except (AttributeError, OSError):
            pass
        data = uploaded_file.read()
        try:
            uploaded_file.seek(0)
        except (AttributeError, OSError):
            pass

    if isinstance(data, str):
        data = data.encode("utf-8")
    return data or b""


def _document_is_encrypted(doc: fitz.Document) -> bool:
    return bool(getattr(doc, "is_encrypted", False) or getattr(doc, "needs_pass", False))


def extract_text_from_pdf(
    uploaded_file: BinaryIO,
    max_bytes: int | None = None,
    max_pages: int | None = None,
) -> str:
    pdf_bytes = _read_uploaded_bytes(uploaded_file)
    limit = max_bytes if max_bytes is not None else get_max_pdf_bytes()
    page_limit = max_pages if max_pages is not None else get_max_pdf_pages()

    if not pdf_bytes:
        raise PDFReadError("The uploaded PDF is empty.")
    if len(pdf_bytes) > limit:
        raise PDFTooLargeError(
            f"The uploaded PDF is too large. Limit: {_format_byte_limit(limit)}."
        )

    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            if _document_is_encrypted(doc):
                raise PDFEncryptedError(
                    "The uploaded PDF is encrypted or password protected. "
                    "Export an unlocked text-based PDF and try again."
                )
            if doc.page_count == 0:
                raise PDFReadError("The uploaded PDF does not contain any pages.")
            if doc.page_count > page_limit:
                raise PDFPageLimitError(
                    f"The uploaded PDF has {doc.page_count} pages. Limit: {page_limit} pages."
                )

            page_text = []
            failed_pages = []
            for page_number in range(doc.page_count):
                try:
                    page = doc.load_page(page_number)
                    page_text.append(page.get_text("text"))
                except Exception:
                    failed_pages.append(page_number + 1)

            text = "\n".join(page_text)
    except Exception as exc:
        if isinstance(exc, PDFReadError):
            raise
        raise PDFReadError("The uploaded file could not be read as a valid PDF.") from exc

    if failed_pages and not text.strip():
        raise PDFReadError(
            "Text extraction failed for every page in this PDF. Export a fresh text-based PDF "
            "from your resume editor and try again."
        )

    if not text.strip():
        raise PDFReadError(
            "No extractable text was found. Scanned or image-only PDFs are not supported yet."
        )
    return text
