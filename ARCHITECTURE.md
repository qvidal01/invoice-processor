# Architecture

This repository is a modular, locally runnable scaffold for automated invoice processing. It favors clear seams for future services (LLMs, databases, accounting integrations) while keeping today’s code deterministic and testable.

## High-level flow

```
CLI / MCP tools
        │
        ▼
InvoiceProcessor (core/processor.py)
   ├─ OCREngine (core/ocr.py)        → Extract text from PDFs/images
   ├─ DataExtractor (core/extractor.py) → Parse text into InvoiceData
   ├─ InvoiceValidator (core/validator.py) → Business rules/PO checks
   └─ Models (models.py)             → Typed domain objects
```

### Entry points
- `invoice_processor.cli:main` exposes `process` and `batch` commands.
- `invoice_processor.mcp_server.server:main` exposes MCP tools (`process_invoice`, `validate_invoice`, status lookup stub).
- Python import: `from invoice_processor import InvoiceProcessor`.

### Core modules
- **core/ocr.py**  
  - Uses PyPDF2 for text-first extraction, falling back to pdf2image+pytesseract for scanned PDFs.  
  - Image preprocessing (grayscale, denoise, autocontrast, orientation detection) before OCR.
- **core/extractor.py**  
  - Regex/date parsing to build `InvoiceData` without network access.  
  - Fallback line item generation when structured tables are missing.  
  - Confidence scoring based on parse signals; currency/dates/amount parsing helpers.
- **core/validator.py**  
  - Completeness checks, amount/date validation, optional PO enforcement, low-confidence warnings.  
  - Stub hooks for PO lookup and duplicate detection.
- **core/processor.py**  
  - Orchestrates OCR → extraction → validation with strict file validation (size, extension, optional trusted base path).  
  - Returns `ProcessingResult` objects suitable for CLI and MCP consumers.
- **utils/security.py**  
  - Filename sanitization, path traversal protection, SHA-256 hashing.
- **utils/logging_config.py**  
  - Simple stdout logging with optional JSON-ready formatter.

### Configuration
- `config.py` uses `pydantic-settings` to load environment variables (`OPENAI_API_KEY`, database URLs, logging, limits).
- Storage path is created on load to avoid runtime surprises.
- `InvoiceProcessor` accepts runtime overrides for max file size, allowed extensions, and trusted directories.

### Testing
- Unit tests cover models, validation rules, security helpers, extraction heuristics, OCR/processor guardrails.
- Pytest configuration lives in `pyproject.toml`; run with `pytest` (coverage flags enabled by default).

### Extensibility map
- **LLM extraction**: replace or augment `DataExtractor.extract_invoice_data` with an OpenAI/LangChain implementation; keep deterministic fallback for resilience.
- **Storage/database**: fill `src/invoice_processor/db/` with SQLAlchemy models/migrations; wire `_fetch_po_data` to the chosen store.
- **Accounting integrations**: add concrete clients under `src/invoice_processor/integrations/` and expose sync methods from `InvoiceProcessor`.
- **API server**: implement FastAPI routers under `src/invoice_processor/api/`, reusing `InvoiceProcessor` orchestrations.
