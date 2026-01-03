"""Tests for processor-level safeguards."""

from pathlib import Path

from invoice_processor.core.processor import InvoiceProcessor


def test_process_invoice_rejects_unsupported_extension(tmp_path: Path) -> None:
    """Unsupported extensions should fail fast and return an error result."""
    file_path = tmp_path / "invoice.txt"
    file_path.write_text("dummy")

    processor = InvoiceProcessor(openai_api_key="test-key")
    result = processor.process_invoice(file_path, validate=False)

    assert result.success is False
    assert "Unsupported file extension" in (result.error or "")


def test_process_invoice_rejects_large_files(tmp_path: Path) -> None:
    """Files larger than the configured threshold should be blocked early."""
    file_path = tmp_path / "oversized.pdf"
    file_path.write_bytes(b"0" * 2_000_000)  # ~2 MB

    processor = InvoiceProcessor(openai_api_key="test-key", max_file_size_mb=1)
    result = processor.process_invoice(file_path, validate=False)

    assert result.success is False
    assert "exceeds maximum size" in (result.error or "")
