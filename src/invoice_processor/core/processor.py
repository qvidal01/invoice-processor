"""
Main InvoiceProcessor class - orchestrates the complete processing pipeline.

This is the primary entry point for invoice processing.
"""

import logging
import time
from pathlib import Path
from typing import List, Optional

from invoice_processor.core.extractor import DataExtractor
from invoice_processor.core.ocr import OCREngine
from invoice_processor.core.validator import InvoiceValidator
from invoice_processor.models import InvoiceData, ProcessingResult

logger = logging.getLogger(__name__)


class InvoiceProcessor:
    """
    Main invoice processing pipeline.

    Orchestrates OCR, extraction, validation, and storage operations.
    """

    def __init__(
        self,
        openai_api_key: str,
        ocr_language: str = "eng",
        validator_config: Optional[dict] = None,
    ) -> None:
        """
        Initialize invoice processor.

        Args:
            openai_api_key: OpenAI API key for data extraction
            ocr_language: Tesseract language code (default: 'eng')
            validator_config: Optional validator configuration

        Raises:
            ValueError: If configuration is invalid
        """
        self.ocr_engine = OCREngine(language=ocr_language)
        self.extractor = DataExtractor(openai_api_key=openai_api_key)
        self.validator = InvoiceValidator(config=validator_config)
        logger.info("Invoice Processor initialized")

    def process_invoice(
        self, file_path: Path, validate: bool = True, po_number: Optional[str] = None
    ) -> ProcessingResult:
        """
        Process a single invoice file.

        Steps:
        1. Extract text via OCR
        2. Parse structured data with AI
        3. Validate against rules and PO
        4. Store results

        Args:
            file_path: Path to invoice PDF or image
            validate: Whether to perform validation (default: True)
            po_number: Optional PO number for validation

        Returns:
            Processing result with invoice data and validation

        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If processing fails
        """
        start_time = time.time()
        logger.info(f"Processing invoice: {file_path}")

        try:
            # Step 1: Extract text
            text = self._extract_text(file_path)
            logger.debug(f"Extracted {len(text)} characters of text")

            # Step 2: Extract structured data
            invoice_data = self.extractor.extract_invoice_data(text, file_name=file_path.name)
            if po_number:
                invoice_data.po_number = po_number

            # Step 3: Validate
            validation_result = None
            if validate:
                po_data = self._fetch_po_data(po_number) if po_number else None
                validation_result = self.validator.validate_invoice(invoice_data, po_data)
                logger.info(
                    f"Validation: {'PASS' if validation_result.is_valid else 'FAIL'} "
                    f"({len(validation_result.errors)} errors)"
                )

            processing_time = time.time() - start_time

            return ProcessingResult(
                success=True,
                invoice=invoice_data,
                validation=validation_result,
                processing_time=processing_time,
                metadata={"file_path": str(file_path)},
            )

        except Exception as e:
            logger.error(f"Processing failed: {e}", exc_info=True)
            processing_time = time.time() - start_time
            return ProcessingResult(
                success=False,
                error=str(e),
                processing_time=processing_time,
                metadata={"file_path": str(file_path)},
            )

    def process_batch(
        self, directory: Path, validate: bool = True, file_pattern: str = "*.pdf"
    ) -> List[ProcessingResult]:
        """
        Process all invoices in a directory.

        Args:
            directory: Directory containing invoice files
            validate: Whether to validate each invoice
            file_pattern: Glob pattern for files (default: '*.pdf')

        Returns:
            List of processing results
        """
        logger.info(f"Processing batch from directory: {directory}")

        results = []
        files = list(directory.glob(file_pattern))
        logger.info(f"Found {len(files)} files matching pattern: {file_pattern}")

        for file_path in files:
            result = self.process_invoice(file_path, validate=validate)
            results.append(result)

        successful = sum(1 for r in results if r.success)
        logger.info(f"Batch complete: {successful}/{len(results)} successful")

        return results

    def _extract_text(self, file_path: Path) -> str:
        """
        Extract text from invoice file.

        Args:
            file_path: Path to invoice file

        Returns:
            Extracted text
        """
        suffix = file_path.suffix.lower()

        if suffix == ".pdf":
            return self.ocr_engine.extract_text_from_pdf(file_path)
        elif suffix in [".png", ".jpg", ".jpeg", ".tiff"]:
            return self.ocr_engine.extract_text_from_image(file_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

    def _fetch_po_data(self, po_number: str) -> Optional[dict]:
        """
        Fetch purchase order data from database.

        Args:
            po_number: PO number to fetch

        Returns:
            PO data or None if not found
        """
        # TODO: Implement database lookup
        logger.debug(f"Fetching PO data for: {po_number}")
        return None
