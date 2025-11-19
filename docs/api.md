# API Reference

Complete API reference for Invoice Processor.

## Table of Contents

- [Core Classes](#core-classes)
- [Data Models](#data-models)
- [Configuration](#configuration)
- [Utilities](#utilities)
- [CLI](#cli)
- [MCP Server](#mcp-server)

---

## Core Classes

### InvoiceProcessor

Main class for invoice processing operations.

```python
from invoice_processor import InvoiceProcessor

processor = InvoiceProcessor(
    openai_api_key="sk-...",
    ocr_language="eng",
    validator_config={"max_amount": Decimal("100000")}
)
```

#### Constructor Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `openai_api_key` | `str` | Yes | OpenAI API key for GPT-4 extraction |
| `ocr_language` | `str` | No | Tesseract language code (default: "eng") |
| `validator_config` | `dict` | No | Validation configuration |

#### Methods

##### `process_invoice()`

Process a single invoice file.

```python
result = processor.process_invoice(
    file_path=Path("invoice.pdf"),
    validate=True,
    po_number="PO-12345"
)
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_path` | `Path` | Yes | - | Path to invoice PDF or image |
| `validate` | `bool` | No | `True` | Whether to perform validation |
| `po_number` | `str | None` | No | `None` | PO number for validation |

**Returns:** `ProcessingResult`

**Raises:**
- `FileNotFoundError` - If file does not exist
- `ValueError` - If file format is unsupported

---

##### `process_batch()`

Process all invoices in a directory.

```python
results = processor.process_batch(
    directory=Path("./invoices"),
    validate=True,
    file_pattern="*.pdf"
)
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `directory` | `Path` | Yes | - | Directory containing invoices |
| `validate` | `bool` | No | `True` | Whether to validate each invoice |
| `file_pattern` | `str` | No | `"*.pdf"` | Glob pattern for files |

**Returns:** `List[ProcessingResult]`

---

### OCREngine

Optical Character Recognition engine.

```python
from invoice_processor.core import OCREngine

ocr = OCREngine(language="eng")
text = ocr.extract_text_from_pdf(Path("invoice.pdf"))
```

#### Methods

##### `extract_text_from_pdf()`

Extract text from PDF file.

```python
text = ocr.extract_text_from_pdf(file_path=Path("invoice.pdf"))
```

**Parameters:**
- `file_path` (`Path`) - Path to PDF file

**Returns:** `str` - Extracted text

**Raises:**
- `FileNotFoundError` - If file does not exist
- `ValueError` - If file is not a valid PDF

---

##### `extract_text_from_image()`

Extract text from image file using OCR.

```python
text = ocr.extract_text_from_image(file_path=Path("invoice.png"))
```

**Parameters:**
- `file_path` (`Path`) - Path to image file

**Returns:** `str` - Extracted text

---

### DataExtractor

AI-powered data extraction from invoice text.

```python
from invoice_processor.core import DataExtractor

extractor = DataExtractor(openai_api_key="sk-...")
invoice_data = extractor.extract_invoice_data(text)
```

#### Methods

##### `extract_invoice_data()`

Extract structured invoice data from text.

```python
invoice = extractor.extract_invoice_data(
    text="Invoice text...",
    file_name="invoice.pdf"
)
```

**Parameters:**
- `text` (`str`) - Raw invoice text
- `file_name` (`str | None`) - Optional filename for reference

**Returns:** `InvoiceData`

**Raises:**
- `ValueError` - If extraction fails or confidence is too low

---

### InvoiceValidator

Validate invoice data against business rules.

```python
from invoice_processor.core import InvoiceValidator

validator = InvoiceValidator(config={"max_amount": Decimal("10000")})
result = validator.validate_invoice(invoice_data)
```

#### Methods

##### `validate_invoice()`

Perform comprehensive invoice validation.

```python
result = validator.validate_invoice(
    invoice=invoice_data,
    po_data={"po_number": "PO-123", "amount": 1000}
)
```

**Parameters:**
- `invoice` (`InvoiceData`) - Invoice to validate
- `po_data` (`dict | None`) - Optional PO data for matching

**Returns:** `ValidationResult`

---

## Data Models

### InvoiceData

Complete invoice data model.

```python
from invoice_processor.models import InvoiceData

invoice = InvoiceData(
    id="INV-001",
    vendor_name="Acme Corp",
    invoice_number="INV-123",
    invoice_date=date(2024, 1, 15),
    due_date=date(2024, 2, 15),
    total_amount=Decimal("1250.00"),
    tax_amount=Decimal("92.50"),
    currency="USD",
    line_items=[...],
    status=InvoiceStatus.PENDING,
    confidence_score=0.95
)
```

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `str` | Yes | Unique invoice identifier |
| `vendor_name` | `str` | Yes | Vendor/supplier name |
| `vendor_id` | `str | None` | No | Vendor ID in accounting system |
| `invoice_number` | `str` | Yes | Invoice number from vendor |
| `invoice_date` | `date` | Yes | Invoice date |
| `due_date` | `date` | Yes | Payment due date |
| `total_amount` | `Decimal` | Yes | Total invoice amount |
| `tax_amount` | `Decimal` | No | Tax amount (default: 0) |
| `currency` | `str` | No | Currency code (default: "USD") |
| `line_items` | `List[LineItem]` | No | Invoice line items |
| `status` | `InvoiceStatus` | No | Processing status |
| `confidence_score` | `float` | Yes | Extraction confidence (0-1) |
| `po_number` | `str | None` | No | Purchase order number |
| `notes` | `str | None` | No | Additional notes |

#### Validation Rules

- `due_date` must be after `invoice_date`
- `total_amount` must match sum of `line_items` + `tax_amount`
- `confidence_score` must be between 0 and 1

---

### LineItem

Individual invoice line item.

```python
from invoice_processor.models import LineItem

item = LineItem(
    description="Widget A",
    quantity=Decimal("10"),
    unit_price=Decimal("25.50"),
    amount=Decimal("255.00"),
    account_code="4000"
)
```

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `description` | `str` | Yes | Item description |
| `quantity` | `Decimal` | Yes | Quantity (must be > 0) |
| `unit_price` | `Decimal` | Yes | Price per unit |
| `amount` | `Decimal` | Yes | Line total (quantity × unit_price) |
| `account_code` | `str | None` | No | Accounting code |

---

### ValidationResult

Result of invoice validation.

```python
from invoice_processor.models import ValidationResult

result = ValidationResult(
    is_valid=True,
    errors=[],
    warnings=["Low confidence score"],
    confidence=0.85,
    validated_fields=["amounts", "dates", "vendor"]
)
```

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| `is_valid` | `bool` | Whether validation passed |
| `errors` | `List[str]` | Critical validation errors |
| `warnings` | `List[str]` | Non-critical warnings |
| `confidence` | `float` | Overall confidence score |
| `validated_fields` | `List[str]` | Fields that were validated |

---

### ProcessingResult

Result of invoice processing operation.

```python
@dataclass
class ProcessingResult:
    success: bool
    invoice: Optional[InvoiceData] = None
    validation: Optional[ValidationResult] = None
    error: Optional[str] = None
    processing_time: float = 0.0
    metadata: dict = field(default_factory=dict)
```

---

## Configuration

### Settings

Application settings loaded from environment variables.

```python
from invoice_processor.config import get_settings

settings = get_settings()
print(settings.openai_api_key)
print(settings.database_url)
```

#### Configuration Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `openai_api_key` | `str` | Required | OpenAI API key |
| `database_url` | `str` | `"sqlite:///./invoices.db"` | Database URL |
| `storage_path` | `Path` | `"./data/invoices"` | Invoice storage path |
| `max_file_size_mb` | `int` | `10` | Maximum file size in MB |
| `ocr_language` | `str` | `"eng"` | Tesseract language |
| `confidence_threshold` | `float` | `0.7` | Minimum confidence threshold |
| `log_level` | `str` | `"INFO"` | Logging level |

See `.env.example` for complete list of configuration options.

---

## Utilities

### Security Functions

```python
from invoice_processor.utils.security import (
    hash_content,
    sanitize_filename,
    validate_file_path
)

# Hash content
content_hash = hash_content("sensitive data")

# Sanitize filename
safe_name = sanitize_filename("../../etc/passwd")  # Returns "passwd"

# Validate file path
is_safe = validate_file_path(
    file_path=Path("/uploads/invoice.pdf"),
    allowed_directory=Path("/uploads")
)
```

---

### Logging Configuration

```python
from invoice_processor.utils.logging_config import setup_logging

setup_logging(level="DEBUG", format_type="json")
```

---

## CLI

### Commands

#### `process`

Process a single invoice file.

```bash
invoice-processor process INVOICE.pdf [OPTIONS]
```

**Options:**
- `--validate / --no-validate` - Enable/disable validation (default: validate)
- `--po-number TEXT` - Purchase order number for validation

---

#### `batch`

Process directory of invoices.

```bash
invoice-processor batch DIRECTORY [OPTIONS]
```

**Options:**
- `--pattern TEXT` - File pattern to match (default: "*.pdf")
- `--validate / --no-validate` - Enable/disable validation

---

## MCP Server

See [MCP Server Documentation](../src/invoice_processor/mcp_server/README.md) for details on the Model Context Protocol implementation.

### Tools

- `process_invoice` - Extract and validate invoice data
- `validate_invoice` - Validate against PO and rules
- `get_processing_status` - Query invoice status

### Resources

- `invoice://{invoice_id}` - Access invoice data

---

## Type Hints

All public APIs use type hints for better IDE support:

```python
from pathlib import Path
from typing import Optional, List
from decimal import Decimal

def process_invoice(
    file_path: Path,
    validate: bool = True,
    po_number: Optional[str] = None
) -> ProcessingResult:
    ...
```

---

## Error Handling

Common exceptions:

- `FileNotFoundError` - File does not exist
- `ValueError` - Invalid input or processing error
- `pydantic.ValidationError` - Data validation error

Example:

```python
from pydantic import ValidationError

try:
    result = processor.process_invoice(Path("invoice.pdf"))
except FileNotFoundError:
    print("Invoice file not found")
except ValueError as e:
    print(f"Processing error: {e}")
except ValidationError as e:
    print(f"Data validation error: {e}")
```

---

## Examples

See the [examples/](../examples/) directory for complete, runnable code examples.
