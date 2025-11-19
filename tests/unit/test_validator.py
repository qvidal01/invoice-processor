"""Tests for invoice validator."""

from datetime import date
from decimal import Decimal

import pytest

from invoice_processor.core.validator import InvoiceValidator
from invoice_processor.models import InvoiceData, InvoiceStatus


class TestInvoiceValidator:
    """Tests for InvoiceValidator class."""

    def test_validate_valid_invoice(self, sample_invoice_data: InvoiceData) -> None:
        """Test validation of a valid invoice."""
        validator = InvoiceValidator()
        result = validator.validate_invoice(sample_invoice_data)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_missing_vendor_name(self, sample_invoice_data: InvoiceData) -> None:
        """Test validation fails when vendor name is missing."""
        sample_invoice_data.vendor_name = ""

        validator = InvoiceValidator()
        result = validator.validate_invoice(sample_invoice_data)

        assert result.is_valid is False
        assert any("vendor name" in error.lower() for error in result.errors)

    def test_validate_amount_exceeds_maximum(self, sample_invoice_data: InvoiceData) -> None:
        """Test validation fails when amount exceeds maximum."""
        validator = InvoiceValidator(config={"max_amount": Decimal("100.00")})
        result = validator.validate_invoice(sample_invoice_data)

        assert result.is_valid is False
        assert any("exceeds maximum" in error.lower() for error in result.errors)

    def test_validate_low_confidence_warning(self, sample_invoice_data: InvoiceData) -> None:
        """Test that low confidence generates a warning."""
        sample_invoice_data.confidence_score = 0.5

        validator = InvoiceValidator()
        result = validator.validate_invoice(sample_invoice_data)

        assert len(result.warnings) > 0
        assert any("confidence" in warning.lower() for warning in result.warnings)

    def test_require_po_number(self, sample_invoice_data: InvoiceData) -> None:
        """Test validation fails when PO is required but missing."""
        sample_invoice_data.po_number = None

        validator = InvoiceValidator(config={"require_po": True})
        result = validator.validate_invoice(sample_invoice_data)

        assert result.is_valid is False
        assert any("purchase order" in error.lower() for error in result.errors)
