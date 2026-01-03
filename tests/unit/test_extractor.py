"""Tests for the DataExtractor."""

from decimal import Decimal

import pytest

from invoice_processor.core.extractor import DataExtractor

SAMPLE_TEXT = """
Vendor: Acme Corp
Invoice Number: INV-1001
Invoice Date: 2024-01-15
Due Date: 2024-02-14
Currency: USD

Line Items:
1) Widget A qty 10 @ 25.50 amount 255.00

Subtotal: 255.00
Tax: 20.00
Total: 275.00
"""


def test_extract_invoice_data_parses_core_fields() -> None:
    """End-to-end parse of a structured invoice text."""
    extractor = DataExtractor(openai_api_key="test-key")

    invoice = extractor.extract_invoice_data(SAMPLE_TEXT, file_name="INV-1001.pdf")

    assert invoice.vendor_name == "Acme Corp"
    assert invoice.invoice_number == "INV-1001"
    assert invoice.total_amount == Decimal("275.00")
    assert invoice.tax_amount == Decimal("20.00")
    assert invoice.currency == "USD"
    assert len(invoice.line_items) == 1
    assert invoice.line_items[0].description == "Widget A"
    assert 0.6 <= invoice.confidence_score <= 1.0


def test_extract_invoice_data_requires_total() -> None:
    """Missing totals should raise a user-friendly error."""
    extractor = DataExtractor(openai_api_key="test-key")
    text = "Vendor: Example Co\nInvoice Number: INV-001"

    with pytest.raises(ValueError):
        extractor.extract_invoice_data(text)


def test_extract_invoice_data_fallback_line_item() -> None:
    """When line items are not parseable, a safe fallback is created."""
    extractor = DataExtractor(openai_api_key="test-key")
    text = """
    Vendor: Example Co
    Invoice Number: INV-002
    Invoice Date: 2024-01-01
    Due Date: 2024-02-01
    Total: 100.00
    """

    invoice = extractor.extract_invoice_data(text)

    assert len(invoice.line_items) == 1
    assert invoice.line_items[0].amount == Decimal("100.00")
    assert invoice.invoice_number == "INV-002"
