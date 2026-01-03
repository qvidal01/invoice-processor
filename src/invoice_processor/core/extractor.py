"""
Data Extractor for parsing structured data from invoice text.

Uses light-weight parsing and heuristics so the library works offline while
keeping a clean seam for future LLM-powered extraction.
"""

import logging
import re
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from typing import List, Optional

from dateutil import parser as date_parser

from invoice_processor.models import InvoiceData, InvoiceStatus, LineItem

logger = logging.getLogger(__name__)


class DataExtractor:
    """
    Extract structured data from raw invoice text.

    Combines deterministic parsing with sensible defaults to avoid hard
    failures when upstream OCR is imperfect.
    """

    def __init__(self, openai_api_key: str, model: str = "gpt-4") -> None:
        """
        Initialize data extractor.

        Args:
            openai_api_key: OpenAI API key for GPT-4 access
            model: OpenAI model to use (default: 'gpt-4')

        Raises:
            ValueError: If API key is invalid
        """
        if not openai_api_key:
            raise ValueError("openai_api_key must be provided")

        self.api_key = openai_api_key
        self.model = model
        logger.info("Data Extractor initialized with offline parsing fallback")

    def extract_invoice_data(self, text: str, file_name: Optional[str] = None) -> InvoiceData:
        """
        Extract complete invoice data from text.

        Args:
            text: Raw text extracted from invoice
            file_name: Optional filename for reference

        Returns:
            Structured invoice data

        Raises:
            ValueError: If extraction fails or confidence is too low
        """
        logger.info("Extracting invoice data from text")
        normalized_text = text.strip()
        if not normalized_text:
            raise ValueError("No text provided for extraction")

        vendor_name, vendor_id = self.identify_vendor(normalized_text)
        invoice_number = self._extract_invoice_number(normalized_text, file_name)
        invoice_date, due_date = self.extract_dates(normalized_text)
        total_amount, tax_amount = self.extract_amounts(normalized_text)
        line_items = self.extract_line_items(normalized_text, total_amount=total_amount)
        confidence_score = self._estimate_confidence(normalized_text, line_items)

        invoice_id = invoice_number or file_name or "invoice"

        return InvoiceData(
            id=invoice_id,
            vendor_name=vendor_name,
            vendor_id=vendor_id,
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            due_date=due_date,
            total_amount=total_amount,
            tax_amount=tax_amount,
            currency=self._extract_currency(normalized_text) or "USD",
            line_items=line_items,
            status=InvoiceStatus.PENDING,
            confidence_score=confidence_score,
        )

    def identify_vendor(self, text: str) -> tuple[str, Optional[str]]:
        """
        Identify vendor name and ID from invoice text.

        Args:
            text: Invoice text

        Returns:
            Tuple of (vendor_name, vendor_id)
        """
        logger.debug("Identifying vendor from text")
        for line in text.splitlines():
            clean = line.strip()
            if not clean:
                continue

            if clean.lower().startswith("vendor:"):
                vendor_name = clean.split(":", 1)[1].strip()
                return vendor_name or "Unknown Vendor", None

            if "invoice" not in clean.lower():
                return clean, None

        return "Unknown Vendor", None

    def extract_line_items(
        self, text: str, total_amount: Optional[Decimal] = None
    ) -> List[LineItem]:
        """
        Extract line items from invoice text.

        Args:
            text: Invoice text containing line items table
            total_amount: Optional total amount for fallback line item

        Returns:
            List of line items

        Raises:
            ValueError: If line items cannot be parsed
        """
        logger.debug("Extracting line items from text")
        line_items: List[LineItem] = []

        line_item_pattern = re.compile(
            r"(?P<idx>\d+)[\).\s-]+(?P<desc>.+?)\s+qty\s+(?P<qty>[\d.,]+)\s*@\s*"
            r"(?P<price>[\d.,]+)\s+(amount|total)\s+(?P<amount>[\d.,]+)",
            re.IGNORECASE,
        )

        for line in text.splitlines():
            match = line_item_pattern.search(line)
            if not match:
                continue

            try:
                quantity = Decimal(match.group("qty").replace(",", ""))
                unit_price = Decimal(match.group("price").replace(",", ""))
                amount = Decimal(match.group("amount").replace(",", ""))
            except InvalidOperation:
                logger.debug("Skipping line item due to invalid number parsing: %s", line)
                continue

            description = match.group("desc").strip()
            line_items.append(
                LineItem(
                    description=description,
                    quantity=quantity,
                    unit_price=unit_price,
                    amount=amount,
                )
            )

        if line_items:
            return line_items

        # Fallback: create a single line item using total_amount if available
        if total_amount is not None:
            fallback_amount = total_amount
            line_items.append(
                LineItem(
                    description="Invoice Total",
                    quantity=Decimal("1"),
                    unit_price=fallback_amount,
                    amount=fallback_amount,
                )
            )
            return line_items

        raise ValueError("Unable to parse any line items from text")

    def extract_dates(self, text: str) -> tuple[date, date]:
        """
        Extract invoice date and due date.

        Args:
            text: Invoice text

        Returns:
            Tuple of (invoice_date, due_date)

        Raises:
            ValueError: If dates cannot be parsed
        """
        logger.debug("Extracting dates from text")
        invoice_date = self._parse_date(text, ["invoice date", "date"])
        due_date = self._parse_date(text, ["due date", "payment due"])

        if not invoice_date:
            invoice_date = date.today()
            logger.warning("Invoice date not found; defaulting to today: %s", invoice_date)

        if not due_date:
            due_date = invoice_date + timedelta(days=30)
            logger.warning("Due date not found; defaulting to +30 days: %s", due_date)

        return invoice_date, due_date

    def extract_amounts(self, text: str) -> tuple[Decimal, Decimal]:
        """
        Extract total amount and tax amount.

        Args:
            text: Invoice text

        Returns:
            Tuple of (total_amount, tax_amount)

        Raises:
            ValueError: If amounts cannot be parsed
        """
        logger.debug("Extracting amounts from text")
        total = self._parse_amount(text, ["total", "amount due"])
        tax = self._parse_amount(text, ["tax", "vat"])

        if total is None:
            raise ValueError("Unable to locate total amount in invoice text")

        if tax is None:
            tax = Decimal("0.00")

        return total, tax

    def _parse_date(self, text: str, labels: List[str]) -> Optional[date]:
        """Find the first parseable date following any of the labels."""
        for line in text.splitlines():
            lower = line.lower()
            if not any(label in lower for label in labels):
                continue
            try:
                return date_parser.parse(line, fuzzy=True).date()
            except (ValueError, OverflowError):
                logger.debug("Failed to parse date from line: %s", line)
        return None

    def _parse_amount(self, text: str, labels: List[str]) -> Optional[Decimal]:
        """Parse a currency amount following any of the provided labels."""
        amount_pattern = r"([-+]?[0-9]{1,3}(?:[,0-9]*)(?:\.[0-9]{2})?)"
        for line in text.splitlines():
            lower = line.lower()
            if not any(re.search(rf"\b{re.escape(label)}\b", lower) for label in labels):
                continue
            sanitized = re.sub(r"[^\d\.,-]", " ", line)
            match = re.search(amount_pattern, sanitized.replace(",", ""))
            if match:
                try:
                    return Decimal(match.group(1))
                except InvalidOperation:
                    logger.debug("Failed to parse amount from line: %s", line)
        return None

    def _extract_invoice_number(self, text: str, file_name: Optional[str]) -> str:
        """Attempt to extract an invoice number from text or filename."""
        match = re.search(r"(invoice number|inv)[\s:]*([A-Za-z0-9\-_/]+)", text, re.IGNORECASE)
        if match:
            return match.group(2).strip()

        if file_name:
            stem = file_name.split(".")[0]
            return stem

        return "UNKNOWN-INVOICE"

    def _extract_currency(self, text: str) -> Optional[str]:
        """Extract ISO currency code if present."""
        for line in text.splitlines():
            lower = line.lower()
            if "currency" in lower:
                match = re.search(r"\b([A-Z]{3})\b", line)
                if match:
                    return match.group(1)

        # Fallback: look for common currency codes preceded by symbol cues
        symbol_hints = {"$": "USD", "€": "EUR", "£": "GBP"}
        for symbol, code in symbol_hints.items():
            if symbol in text:
                return code
        return None

    def _estimate_confidence(self, text: str, line_items: List[LineItem]) -> float:
        """
        Provide a lightweight confidence estimate based on parse signals.

        This is intentionally simple to avoid pretending to have LLM quality.
        """
        signals = 0
        if len(text) > 100:
            signals += 1
        if line_items:
            signals += 1
        if "due" in text.lower():
            signals += 1

        return min(1.0, 0.6 + signals * 0.1)
