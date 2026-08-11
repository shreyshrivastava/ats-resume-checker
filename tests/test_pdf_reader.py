from io import BytesIO

import fitz
import pytest

from utils import pdf_reader
from utils.pdf_reader import (
    PDFEncryptedError,
    PDFPageLimitError,
    PDFReadError,
    PDFTooLargeError,
    extract_text_from_pdf,
    get_max_pdf_pages,
)


def make_pdf(text: str) -> BytesIO:
    document = fitz.open()
    page = document.new_page()
    if text:
        page.insert_text((72, 72), text)
    data = document.tobytes()
    document.close()
    file_obj = BytesIO(data)
    file_obj.name = "synthetic_resume.pdf"
    return file_obj


def make_multi_page_pdf(page_texts: list[str]) -> BytesIO:
    document = fitz.open()
    for text in page_texts:
        page = document.new_page()
        if text:
            page.insert_text((72, 72), text)
    data = document.tobytes()
    document.close()
    file_obj = BytesIO(data)
    file_obj.name = "multi_page_resume.pdf"
    return file_obj


def make_encrypted_pdf(text: str) -> BytesIO:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    data = document.tobytes(
        encryption=fitz.PDF_ENCRYPT_AES_256,
        owner_pw="owner-password",
        user_pw="user-password",
    )
    document.close()
    file_obj = BytesIO(data)
    file_obj.name = "encrypted_resume.pdf"
    return file_obj


def test_extract_text_from_valid_pdf():
    pdf = make_pdf("Summary Python FastAPI LLM evaluation")

    text = extract_text_from_pdf(pdf)

    assert "Python FastAPI" in text


def test_extract_text_resets_seekable_file_position():
    pdf = make_pdf("Skills pytest CI deployment")
    pdf.seek(5)

    text = extract_text_from_pdf(pdf)

    assert "pytest CI deployment" in text


def test_malformed_pdf_returns_controlled_error():
    bad_pdf = BytesIO(b"not a real pdf")
    bad_pdf.name = "bad.pdf"

    with pytest.raises(PDFReadError, match="valid PDF"):
        extract_text_from_pdf(bad_pdf)


def test_empty_pdf_returns_controlled_error():
    empty_pdf = BytesIO(b"")
    empty_pdf.name = "empty.pdf"

    with pytest.raises(PDFReadError, match="empty"):
        extract_text_from_pdf(empty_pdf)


def test_image_only_pdf_returns_controlled_error():
    pdf = make_pdf("")

    with pytest.raises(PDFReadError, match="No extractable text"):
        extract_text_from_pdf(pdf)


def test_pdf_size_limit_is_enforced():
    pdf = make_pdf("Summary Python")

    with pytest.raises(PDFTooLargeError, match="10 bytes"):
        extract_text_from_pdf(pdf, max_bytes=10)


def test_encrypted_pdf_returns_controlled_error():
    pdf = make_encrypted_pdf("Summary Python")

    with pytest.raises(PDFEncryptedError, match="password protected"):
        extract_text_from_pdf(pdf)


def test_pdf_page_limit_is_enforced():
    pdf = make_multi_page_pdf(["one", "two", "three"])

    with pytest.raises(PDFPageLimitError, match="3 pages"):
        extract_text_from_pdf(pdf, max_pages=2)


def test_invalid_page_limit_env_falls_back(monkeypatch):
    monkeypatch.setenv("ATS_MAX_PDF_PAGES", "not-a-number")

    assert get_max_pdf_pages() == pdf_reader.DEFAULT_MAX_PDF_PAGES


def test_partial_page_extraction_returns_available_text(monkeypatch):
    class FakePage:
        def __init__(self, text: str, should_fail: bool = False):
            self.text = text
            self.should_fail = should_fail

        def get_text(self, mode: str) -> str:
            assert mode == "text"
            if self.should_fail:
                raise RuntimeError("bad page")
            return self.text

    class FakeDoc:
        page_count = 2
        is_encrypted = False
        needs_pass = False

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def load_page(self, page_number: int) -> FakePage:
            return [FakePage("Summary Python"), FakePage("", should_fail=True)][page_number]

    monkeypatch.setattr(pdf_reader.fitz, "open", lambda **kwargs: FakeDoc())

    text = extract_text_from_pdf(BytesIO(b"%PDF fake enough for mocked fitz"))

    assert "Summary Python" in text


def test_all_page_extraction_failures_return_controlled_error(monkeypatch):
    class FakePage:
        def get_text(self, mode: str) -> str:
            raise RuntimeError("bad page")

    class FakeDoc:
        page_count = 1
        is_encrypted = False
        needs_pass = False

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def load_page(self, page_number: int) -> FakePage:
            return FakePage()

    monkeypatch.setattr(pdf_reader.fitz, "open", lambda **kwargs: FakeDoc())

    with pytest.raises(PDFReadError, match="every page"):
        extract_text_from_pdf(BytesIO(b"%PDF fake enough for mocked fitz"))
