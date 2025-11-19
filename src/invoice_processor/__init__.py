"""
Invoice Processor - Automated invoice extraction and processing using OCR and AI.

This package provides tools for extracting data from invoices, validating them,
and integrating with accounting systems like QuickBooks and Xero.
"""

__version__ = "0.1.0"
__author__ = "AIQSO"
__email__ = "contact@aiqso.io"

from invoice_processor.core.processor import InvoiceProcessor
from invoice_processor.models import InvoiceData, LineItem, ValidationResult

__all__ = [
    "InvoiceProcessor",
    "InvoiceData",
    "LineItem",
    "ValidationResult",
]
