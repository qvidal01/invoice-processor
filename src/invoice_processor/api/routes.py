"""API routes for invoice processing."""

import logging
import tempfile
import time
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from invoice_processor.config import get_settings
from invoice_processor.core.processor import InvoiceProcessor

logger = logging.getLogger(__name__)
router = APIRouter()

# Allowed file extensions
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tiff"}
MAX_FILE_SIZE_MB = 10


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    service: str
    version: str


class LineItemResponse(BaseModel):
    """Line item in invoice response."""

    description: str
    quantity: float
    unit_price: float
    amount: float
    account_code: Optional[str] = None


class InvoiceResponse(BaseModel):
    """Invoice data response."""

    id: str
    vendor_name: str
    vendor_id: Optional[str] = None
    invoice_number: str
    invoice_date: str
    due_date: str
    total_amount: float
    tax_amount: float
    currency: str
    line_items: list[LineItemResponse]
    confidence_score: float
    po_number: Optional[str] = None
    notes: Optional[str] = None


class ValidationResponse(BaseModel):
    """Validation result response."""

    is_valid: bool
    errors: list[str]
    warnings: list[str]
    confidence: float


class ProcessResponse(BaseModel):
    """Invoice processing response."""

    success: bool
    data: Optional[InvoiceResponse] = None
    validation: Optional[ValidationResponse] = None
    error: Optional[str] = None
    processing_time: float
    filename: str


class ErrorResponse(BaseModel):
    """Error response."""

    success: bool = False
    error: str
    detail: Optional[str] = None


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        service="invoice-processor",
        version="0.1.0",
    )


@router.post("/process", response_model=ProcessResponse)
async def process_invoice(
    file: UploadFile = File(..., description="Invoice PDF or image file"),
    validate: bool = Form(True, description="Whether to validate the invoice"),
    po_number: Optional[str] = Form(None, description="Purchase order number for validation"),
) -> ProcessResponse:
    """
    Process an invoice file and extract data.

    Accepts PDF, PNG, JPG, JPEG, or TIFF files up to 10MB.
    Returns extracted invoice data with confidence scores.
    """
    start_time = time.time()

    # Validate file extension
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Validate file size
    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large: {file_size_mb:.2f}MB. Maximum: {MAX_FILE_SIZE_MB}MB",
        )

    # Save to temp file for processing
    try:
        settings = get_settings()

        with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as tmp:
            tmp.write(content)
            tmp_path = Path(tmp.name)

        try:
            # Initialize processor
            processor = InvoiceProcessor(
                openai_api_key=settings.openai_api_key,
                ocr_language=settings.ocr_language,
                max_file_size_mb=MAX_FILE_SIZE_MB,
            )

            # Process invoice
            result = processor.process_invoice(
                file_path=tmp_path,
                validate=validate,
                po_number=po_number,
            )

            processing_time = time.time() - start_time

            if result.success and result.invoice:
                # Convert to response format
                invoice_data = InvoiceResponse(
                    id=result.invoice.id,
                    vendor_name=result.invoice.vendor_name,
                    vendor_id=result.invoice.vendor_id,
                    invoice_number=result.invoice.invoice_number,
                    invoice_date=result.invoice.invoice_date.isoformat(),
                    due_date=result.invoice.due_date.isoformat(),
                    total_amount=float(result.invoice.total_amount),
                    tax_amount=float(result.invoice.tax_amount),
                    currency=result.invoice.currency,
                    line_items=[
                        LineItemResponse(
                            description=item.description,
                            quantity=float(item.quantity),
                            unit_price=float(item.unit_price),
                            amount=float(item.amount),
                            account_code=item.account_code,
                        )
                        for item in result.invoice.line_items
                    ],
                    confidence_score=result.invoice.confidence_score,
                    po_number=result.invoice.po_number,
                    notes=result.invoice.notes,
                )

                validation_data = None
                if result.validation:
                    validation_data = ValidationResponse(
                        is_valid=result.validation.is_valid,
                        errors=result.validation.errors,
                        warnings=result.validation.warnings,
                        confidence=result.validation.confidence,
                    )

                return ProcessResponse(
                    success=True,
                    data=invoice_data,
                    validation=validation_data,
                    processing_time=processing_time,
                    filename=file.filename,
                )
            else:
                return ProcessResponse(
                    success=False,
                    error=result.error or "Processing failed",
                    processing_time=processing_time,
                    filename=file.filename,
                )

        finally:
            # Clean up temp file
            tmp_path.unlink(missing_ok=True)

    except Exception as e:
        logger.exception(f"Error processing invoice: {e}")
        processing_time = time.time() - start_time
        return ProcessResponse(
            success=False,
            error=str(e),
            processing_time=processing_time,
            filename=file.filename or "unknown",
        )
