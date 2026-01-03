# Invoice Processor

Lightweight invoice processing pipeline with OCR, deterministic extraction, and validation. This repository is production-ready scaffolding: the core flows run locally without external services, while seams remain for future LLM-based extraction and accounting system integrations.

## What’s included

- OCR pipeline: PyPDF2 text extraction with pdf2image+pytesseract fallback for scanned PDFs and images.
- Deterministic data extraction: regex/date parsing to build `InvoiceData` models without network calls.
- Validation engine: amount/date checks, PO requirements, and business-rule hooks.
- CLI: process single files or directories with Rich output.
- MCP server: stdio server exposing processing tools for AI assistants (still minimal).
- Security helpers: filename sanitization, path validation, and SHA-256 hashing.

### Current limitations

- LLM extraction and accounting system sync are not yet implemented; the extractor currently uses offline heuristics.
- API/web server layers are intentionally stubbed.
- OCR quality depends on your local Tesseract setup; see INSTALL.md for tips.

## Quick start

### Prerequisites

- Python 3.9+
- Tesseract OCR and Poppler utilities for best results:
  - Debian/Ubuntu: `sudo apt-get install tesseract-ocr poppler-utils`
  - macOS (Homebrew): `brew install tesseract poppler`

### Installation

```bash
git clone https://github.com/qvidal01/invoice-processor.git
cd invoice-processor
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e .
# Optional: install dev/test tooling
pip install -r requirements-dev.txt
# Set at least a non-empty OPENAI_API_KEY to satisfy config parsing
export OPENAI_API_KEY=dummy-key
```

See [INSTALL.md](INSTALL.md) for detailed platform guidance.

### CLI usage

```bash
# Process a single invoice
invoice-processor process ./sample_invoice.pdf

# Process a directory (PDFs by default)
invoice-processor batch ./invoices --pattern "*.pdf"
```

### Python API

```python
from invoice_processor import InvoiceProcessor

processor = InvoiceProcessor(openai_api_key="dummy-key")
result = processor.process_invoice("invoice.pdf", validate=True)

if result.success and result.invoice:
    print(f"Vendor: {result.invoice.vendor_name}")
    print(f"Total: {result.invoice.total_amount}")
    print(f"Confidence: {result.invoice.confidence_score:.1%}")
else:
    print(f"Failed: {result.error}")
```

### MCP server

```bash
invoice-mcp-server  # exposes process_invoice over stdio
```

MCP usage details live in `src/invoice_processor/mcp_server/README.md`.

## Testing

```bash
pytest
pytest --cov=invoice_processor --cov-report=term-missing
```

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) – current module layout and flow.
- [INSTALL.md](INSTALL.md) – prerequisites, virtualenv/Poetry, and OCR tips.
- [IMPLEMENTATION_NOTES.md](IMPLEMENTATION_NOTES.md) – rationale and future hooks.
- [CHANGELOG.md](CHANGELOG.md) – release history.
- [docs/api.md](docs/api.md) – API reference for core classes.
- [examples/](examples) – runnable snippets.

## Support

Issues and suggestions are welcome via GitHub issues or contact@aiqso.io. Please see [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) and [CONTRIBUTING.md](CONTRIBUTING.md) before opening a PR.
