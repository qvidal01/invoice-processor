"""Tests for data models."""

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from invoice_processor.models import InvoiceData, InvoiceStatus, LineItem


class TestLineItem:
    """Tests for LineItem model."""

    def test_create_valid_line_item(self) -> None:
        """Test creating a valid line item."""
        item = LineItem(
            description="Widget A",
            quantity=Decimal("10"),
            unit_price=Decimal("25.50"),
            amount=Decimal("255.00"),
        )

        assert item.description == "Widget A"
        assert item.quantity == Decimal("10")
        assert item.amount == Decimal("255.00")

    def test_line_item_amount_validation(self) -> None:
        """Test that amount must match quantity × unit_price."""
        with pytest.raises(ValidationError) as exc_info:
            LineItem(
                description="Widget A",
                quantity=Decimal("10"),
                unit_price=Decimal("25.50"),
                amount=Decimal("100.00"),  # Incorrect amount
            )

        assert "does not match quantity × unit_price" in str(exc_info.value)

    def test_line_item_positive_quantity(self) -> None:
        """Test that quantity must be positive."""
        with pytest.raises(ValidationError):
            LineItem(
                description="Widget A",
                quantity=Decimal("-5"),
                unit_price=Decimal("25.50"),
                amount=Decimal("-127.50"),
            )


class TestInvoiceData:
    """Tests for InvoiceData model."""

    def test_create_valid_invoice(self, sample_invoice_data: InvoiceData) -> None:
        """Test creating a valid invoice."""
        assert sample_invoice_data.invoice_number == "INV-9876"
        assert sample_invoice_data.vendor_name == "Acme Corp"
        assert sample_invoice_data.total_amount == Decimal("275.00")
        assert len(sample_invoice_data.line_items) == 1

    def test_invoice_due_date_after_invoice_date(self) -> None:
        """Test that due date must be after invoice date."""
        with pytest.raises(ValidationError) as exc_info:
            InvoiceData(
                id="INV-001",
                vendor_name="Test Vendor",
                invoice_number="INV-123",
                invoice_date=date(2024, 2, 15),
                due_date=date(2024, 1, 15),  # Before invoice date
                total_amount=Decimal("100.00"),
                tax_amount=Decimal("0.00"),
                confidence_score=0.9,
            )

        assert "Due date must be after invoice date" in str(exc_info.value)

    def test_invoice_line_items_total_validation(self, sample_line_item: LineItem) -> None:
        """Test that line items must sum to total."""
        with pytest.raises(ValidationError) as exc_info:
            InvoiceData(
                id="INV-001",
                vendor_name="Test Vendor",
                invoice_number="INV-123",
                invoice_date=date(2024, 1, 15),
                due_date=date(2024, 2, 15),
                total_amount=Decimal("100.00"),  # Doesn't match line items + tax
                tax_amount=Decimal("20.00"),
                line_items=[sample_line_item],  # Total should be 275.00
                confidence_score=0.9,
            )

        assert "does not match line items + tax" in str(exc_info.value)

    def test_invoice_status_enum(self, sample_invoice_data: InvoiceData) -> None:
        """Test invoice status enum."""
        assert sample_invoice_data.status == InvoiceStatus.PENDING

        sample_invoice_data.status = InvoiceStatus.APPROVED
        assert sample_invoice_data.status == InvoiceStatus.APPROVED

    def test_invoice_confidence_score_range(self) -> None:
        """Test that confidence score must be between 0 and 1."""
        with pytest.raises(ValidationError):
            InvoiceData(
                id="INV-001",
                vendor_name="Test Vendor",
                invoice_number="INV-123",
                invoice_date=date(2024, 1, 15),
                due_date=date(2024, 2, 15),
                total_amount=Decimal("100.00"),
                tax_amount=Decimal("0.00"),
                confidence_score=1.5,  # Invalid: > 1
            )
