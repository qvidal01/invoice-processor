"""
Data models for invoice processing.

This module defines the core data structures used throughout the application.
"""

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class InvoiceStatus(str, Enum):
    """Invoice processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    EXTRACTED = "extracted"
    VALIDATED = "validated"
    APPROVED = "approved"
    REJECTED = "rejected"
    SYNCED = "synced"
    FAILED = "failed"


class LineItem(BaseModel):
    """Individual line item in an invoice."""

    description: str = Field(..., description="Item description")
    quantity: Decimal = Field(..., gt=0, description="Quantity ordered")
    unit_price: Decimal = Field(..., description="Price per unit")
    amount: Decimal = Field(..., description="Line total (quantity × unit_price)")
    account_code: Optional[str] = Field(None, description="Accounting code")

    @validator("amount")
    def validate_amount(cls, v: Decimal, values: dict) -> Decimal:
        """Validate that amount matches quantity × unit_price."""
        if "quantity" in values and "unit_price" in values:
            expected = values["quantity"] * values["unit_price"]
            if abs(v - expected) > Decimal("0.01"):
                raise ValueError(f"Amount {v} does not match quantity × unit_price {expected}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "description": "Widget A",
                "quantity": 10,
                "unit_price": 25.50,
                "amount": 255.00,
                "account_code": "4000",
            }
        }


class InvoiceData(BaseModel):
    """Complete invoice data extracted from document."""

    id: str = Field(..., description="Unique invoice ID")
    vendor_name: str = Field(..., description="Vendor/supplier name")
    vendor_id: Optional[str] = Field(None, description="Vendor ID in accounting system")
    invoice_number: str = Field(..., description="Invoice number from vendor")
    invoice_date: date = Field(..., description="Invoice date")
    due_date: date = Field(..., description="Payment due date")
    total_amount: Decimal = Field(..., gt=0, description="Total invoice amount")
    tax_amount: Decimal = Field(Decimal(0), ge=0, description="Tax amount")
    currency: str = Field("USD", description="Currency code (ISO 4217)")
    line_items: List[LineItem] = Field(default_factory=list, description="Invoice line items")
    status: InvoiceStatus = Field(
        InvoiceStatus.PENDING, description="Current processing status"
    )
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Extraction confidence")
    po_number: Optional[str] = Field(None, description="Purchase order number")
    notes: Optional[str] = Field(None, description="Additional notes")

    @validator("due_date")
    def validate_due_date(cls, v: date, values: dict) -> date:
        """Ensure due date is after invoice date."""
        if "invoice_date" in values and v < values["invoice_date"]:
            raise ValueError("Due date must be after invoice date")
        return v

    @validator("line_items")
    def validate_line_items_total(cls, v: List[LineItem], values: dict) -> List[LineItem]:
        """Validate that line items sum to total (within tolerance)."""
        if v and "total_amount" in values and "tax_amount" in values:
            subtotal = sum(item.amount for item in v)
            expected_total = subtotal + values["tax_amount"]
            actual_total = values["total_amount"]
            if abs(actual_total - expected_total) > Decimal("0.01"):
                raise ValueError(
                    f"Total amount {actual_total} does not match "
                    f"line items + tax {expected_total}"
                )
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "id": "INV-2024-001",
                "vendor_name": "Acme Corp",
                "vendor_id": "V-12345",
                "invoice_number": "INV-9876",
                "invoice_date": "2024-01-15",
                "due_date": "2024-02-15",
                "total_amount": 275.00,
                "tax_amount": 20.00,
                "currency": "USD",
                "line_items": [
                    {
                        "description": "Widget A",
                        "quantity": 10,
                        "unit_price": 25.50,
                        "amount": 255.00,
                    }
                ],
                "status": "pending",
                "confidence_score": 0.95,
            }
        }


class ValidationResult(BaseModel):
    """Result of invoice validation."""

    is_valid: bool = Field(..., description="Whether invoice passed all validations")
    errors: List[str] = Field(default_factory=list, description="Critical validation errors")
    warnings: List[str] = Field(default_factory=list, description="Non-critical warnings")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence score")
    validated_fields: List[str] = Field(
        default_factory=list, description="Fields that were validated"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "is_valid": False,
                "errors": ["Amount exceeds PO by $750"],
                "warnings": ["Vendor address not verified"],
                "confidence": 0.85,
                "validated_fields": ["amount", "vendor", "po_match"],
            }
        }


@dataclass
class ProcessingResult:
    """Result of invoice processing operation."""

    success: bool
    invoice: Optional[InvoiceData] = None
    validation: Optional[ValidationResult] = None
    error: Optional[str] = None
    processing_time: float = 0.0
    metadata: dict = field(default_factory=dict)
