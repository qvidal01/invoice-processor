# Examples

This directory contains runnable examples demonstrating various invoice processing scenarios.

## Prerequisites

1. **Install invoice-processor**:
   ```bash
   pip install -e ..
   ```

2. **Configure environment**:
   ```bash
   cp ../.env.example ../.env
   # Edit .env and add your OPENAI_API_KEY
   ```

3. **Prepare sample invoices**:
   - Place sample PDF invoices in `sample_invoices/` directory
   - Or use a single file named `sample_invoice.pdf` for basic examples

## Examples

### 1. Basic Usage (`basic_usage.py`)

Process a single invoice and display detailed results.

```bash
python basic_usage.py
```

**What it demonstrates:**
- Initializing the processor
- Processing a single invoice file
- Extracting invoice data (vendor, amount, line items)
- Validation results
- Error handling

**Sample output:**
```
📄 Processing invoice: sample_invoice.pdf

✅ Invoice processed successfully!

============================================================
INVOICE DETAILS
============================================================
Invoice Number:    INV-2024-001
Vendor:            Acme Corp
Invoice Date:      2024-01-15
Due Date:          2024-02-15
Total Amount:      $1,250.00
Tax Amount:        $92.50
Currency:          USD
Status:            pending
Confidence Score:  95.0%
```

### 2. Batch Processing (`batch_processing.py`)

Process multiple invoices from a directory with a summary report.

```bash
# Create sample directory
mkdir sample_invoices
cp path/to/your/invoices/*.pdf sample_invoices/

# Run batch processing
python batch_processing.py
```

**What it demonstrates:**
- Processing multiple files
- Progress indicators
- Summary statistics
- Error aggregation
- Rich terminal output with tables

**Sample output:**
```
📁 Found 10 files matching pattern: *.pdf

         📊 Batch Processing Summary
┌─────────────────┬────────┬──────────┬──────────┬────────────┬──────┐
│ File            │ Status │ Vendor   │   Amount │ Validation │ Time │
├─────────────────┼────────┼──────────┼──────────┼────────────┼──────┤
│ invoice_001.pdf │   ✅   │ Acme     │ $1,250.00│     ✅     │ 2.3s │
│ invoice_002.pdf │   ✅   │ Widgets  │ $  850.00│     ✅     │ 2.1s │
└─────────────────┴────────┴──────────┴──────────┴────────────┴──────┘

Total Files:           10
Successfully Processed: 9 (90.0%)
Validation Passed:     8 (80.0%)
Total Invoice Value:   $15,430.00
```

### 3. Advanced Validation (Coming Soon)

Demonstrates:
- Custom validation rules
- PO matching
- Duplicate detection
- Approval workflows

### 4. QuickBooks Integration (Coming Soon)

Demonstrates:
- OAuth authentication
- Syncing invoices
- Vendor management
- Error handling

### 5. MCP Server Usage (Coming Soon)

Demonstrates:
- Using MCP server with Claude
- AI-assisted batch processing
- Natural language queries

## Creating Your Own Examples

Use these examples as templates for your own use cases:

```python
from pathlib import Path
from invoice_processor import InvoiceProcessor
from invoice_processor.config import get_settings

# Initialize
settings = get_settings()
processor = InvoiceProcessor(openai_api_key=settings.openai_api_key)

# Process
result = processor.process_invoice(Path("your_invoice.pdf"))

# Use the results
if result.success:
    # Do something with result.invoice
    print(f"Processed {result.invoice.invoice_number}")
```

## Troubleshooting

### "File not found" errors

Make sure you've created the `sample_invoices/` directory and added PDF files, or provided a `sample_invoice.pdf` file.

### "OpenAI API key not set" errors

Configure your `.env` file with a valid `OPENAI_API_KEY`.

### OCR errors

Ensure Tesseract and Poppler are installed:

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr poppler-utils

# macOS
brew install tesseract poppler
```

### Import errors

Make sure you've installed the package:

```bash
pip install -e ..  # From examples/ directory
```

## Next Steps

- Review the [API Documentation](../docs/api.md)
- Check the [Contributing Guide](../CONTRIBUTING.md) to add your own examples
- Read the [Analysis Summary](../ANALYSIS_SUMMARY.md) for architecture details
