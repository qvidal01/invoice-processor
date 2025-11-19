"""Pytest configuration and shared fixtures."""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from invoice_processor.models import InvoiceData, InvoiceStatus, LineItem


@pytest.fixture
def sample_line_item() -> LineItem:
    """Create a sample line item for testing."""
    return LineItem(
        description="Widget A",
        quantity=Decimal("10"),
        unit_price=Decimal("25.50"),
        amount=Decimal("255.00"),
        account_code="4000",
    )


@pytest.fixture
def sample_invoice_data(sample_line_item: LineItem) -> InvoiceData:
    """Create sample invoice data for testing."""
    return InvoiceData(
        id="INV-2024-001",
        vendor_name="Acme Corp",
        vendor_id="V-12345",
        invoice_number="INV-9876",
        invoice_date=date(2024, 1, 15),
        due_date=date(2024, 2, 15),
        total_amount=Decimal("275.00"),
        tax_amount=Decimal("20.00"),
        currency="USD",
        line_items=[sample_line_item],
        status=InvoiceStatus.PENDING,
        confidence_score=0.95,
    )


@pytest.fixture
def temp_invoice_dir(tmp_path: Path) -> Path:
    """Create temporary directory for invoice files."""
    invoice_dir = tmp_path / "invoices"
    invoice_dir.mkdir()
    return invoice_dir
