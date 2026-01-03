"""Tests for OCR engine safety checks."""

from pathlib import Path

import pytest

from invoice_processor.core.ocr import OCREngine


def test_pdf_extraction_missing_file() -> None:
    """Missing PDF should raise a clear error."""
    engine = OCREngine()
    with pytest.raises(FileNotFoundError):
        engine.extract_text_from_pdf(Path("missing.pdf"))


def test_pdf_extraction_wrong_extension(tmp_path: Path) -> None:
    """Non-PDF files should be rejected."""
    fake_pdf = tmp_path / "not_a_pdf.txt"
    fake_pdf.write_text("hi")

    engine = OCREngine()
    with pytest.raises(ValueError):
        engine.extract_text_from_pdf(fake_pdf)
