"""
Invoice Validator for checking data against business rules and POs.

Validates invoice data for accuracy, completeness, and compliance.
"""

import logging
from decimal import Decimal
from typing import List, Optional

from invoice_processor.models import InvoiceData, ValidationResult

logger = logging.getLogger(__name__)


class InvoiceValidator:
    """
    Validate invoice data against business rules and purchase orders.

    Performs:
    - Data completeness checks
    - PO matching validation
    - Amount verification
    - Business rule compliance
    """

    def __init__(self, config: Optional[dict] = None) -> None:
        """
        Initialize validator with configuration.

        Args:
            config: Optional validation rules configuration
        """
        self.config = config or {}
        self.max_amount = self.config.get("max_amount", Decimal("100000.00"))
        self.require_po = self.config.get("require_po", False)
        logger.info("Invoice Validator initialized")

    def validate_invoice(
        self, invoice: InvoiceData, po_data: Optional[dict] = None
    ) -> ValidationResult:
        """
        Perform comprehensive invoice validation.

        Args:
            invoice: Invoice data to validate
            po_data: Optional purchase order data for matching

        Returns:
            Validation result with errors and warnings
        """
        logger.info(f"Validating invoice: {invoice.invoice_number}")

        errors: List[str] = []
        warnings: List[str] = []
        validated_fields: List[str] = []

        # Validate required fields
        errors.extend(self._validate_required_fields(invoice))
        validated_fields.append("required_fields")

        # Validate amounts
        amount_errors = self._validate_amounts(invoice)
        errors.extend(amount_errors)
        validated_fields.append("amounts")

        # Validate dates
        date_errors = self._validate_dates(invoice)
        errors.extend(date_errors)
        validated_fields.append("dates")

        # Validate against PO if provided
        if po_data:
            po_errors, po_warnings = self._validate_against_po(invoice, po_data)
            errors.extend(po_errors)
            warnings.extend(po_warnings)
            validated_fields.append("po_match")

        # Apply business rules
        rule_errors, rule_warnings = self._apply_business_rules(invoice)
        errors.extend(rule_errors)
        warnings.extend(rule_warnings)
        validated_fields.append("business_rules")

        is_valid = len(errors) == 0
        confidence = invoice.confidence_score if is_valid else invoice.confidence_score * 0.5

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            confidence=confidence,
            validated_fields=validated_fields,
        )

    def _validate_required_fields(self, invoice: InvoiceData) -> List[str]:
        """Check that all required fields are present."""
        errors = []

        if not invoice.vendor_name:
            errors.append("Missing vendor name")
        if not invoice.invoice_number:
            errors.append("Missing invoice number")
        if invoice.total_amount <= 0:
            errors.append("Invalid total amount")

        return errors

    def _validate_amounts(self, invoice: InvoiceData) -> List[str]:
        """Validate amount calculations and consistency."""
        errors = []

        # Check that total matches line items + tax
        if invoice.line_items:
            subtotal = sum(item.amount for item in invoice.line_items)
            expected_total = subtotal + invoice.tax_amount
            if abs(invoice.total_amount - expected_total) > Decimal("0.01"):
                errors.append(
                    f"Total amount {invoice.total_amount} does not match "
                    f"line items + tax {expected_total}"
                )

        # Check maximum amount threshold
        if invoice.total_amount > self.max_amount:
            errors.append(f"Amount ${invoice.total_amount} exceeds maximum ${self.max_amount}")

        return errors

    def _validate_dates(self, invoice: InvoiceData) -> List[str]:
        """Validate date fields."""
        errors = []

        if invoice.due_date < invoice.invoice_date:
            errors.append("Due date cannot be before invoice date")

        return errors

    def _validate_against_po(
        self, invoice: InvoiceData, po_data: dict
    ) -> tuple[List[str], List[str]]:
        """
        Validate invoice against purchase order.

        Args:
            invoice: Invoice to validate
            po_data: Purchase order data

        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []

        # TODO: Implement PO matching logic
        # - Check vendor matches
        # - Verify amounts
        # - Match line items
        # - Check PO status (open/closed)

        return errors, warnings

    def _apply_business_rules(self, invoice: InvoiceData) -> tuple[List[str], List[str]]:
        """
        Apply custom business rules.

        Args:
            invoice: Invoice to validate

        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []

        # Check if PO is required
        if self.require_po and not invoice.po_number:
            errors.append("Purchase order number is required")

        # Low confidence warning
        if invoice.confidence_score < 0.7:
            warnings.append(f"Low extraction confidence: {invoice.confidence_score:.1%}")

        return errors, warnings

    def check_duplicate(self, invoice: InvoiceData) -> bool:
        """
        Check if invoice is a duplicate.

        Args:
            invoice: Invoice to check

        Returns:
            True if duplicate found
        """
        # TODO: Implement duplicate detection
        # - Check invoice number + vendor combination in database
        # - Calculate content hash and compare
        # - Check for near-duplicates (fuzzy matching)
        return False
