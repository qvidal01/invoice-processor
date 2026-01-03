# Invoice Processor - Claude Reference

## Quick Overview
AI-powered invoice processing system. OCR extraction, GPT-4 parsing, validation, and accounting system integration (QuickBooks, Xero).

## Tech Stack
- **Framework:** FastAPI + Uvicorn
- **Language:** Python 3.9+
- **OCR:** Tesseract
- **AI:** OpenAI GPT-4 + LangChain
- **Database:** SQLAlchemy + Alembic
- **Package:** Poetry
- **CLI:** Click
- **AI:** MCP Server for Claude

## Project Structure
```
src/invoice_processor/
├── ocr/                 # OCR engine (Tesseract)
├── extraction/          # GPT-4 extraction
├── validation/          # Validation engine
├── integrations/        # QuickBooks/Xero APIs
├── mcp_server/          # MCP server for Claude
├── api/                 # FastAPI endpoints
├── models/              # Data models
└── cli/                 # Command-line interface

tests/                   # Unit & integration tests
docs/                    # API documentation
examples/                # Usage examples
```

## Quick Commands
```bash
# Install
poetry install

# Run API
poetry run uvicorn src.invoice_processor.api:app --reload

# Run CLI
poetry run invoice-processor process invoice.pdf

# Test
poetry run pytest
```

## Processing Pipeline
1. **OCR** - Extract text from PDF/images
2. **Extraction** - Parse with GPT-4 (95%+ accuracy)
3. **Validation** - PO matching, business rules
4. **Integration** - Sync to accounting systems

## Key Features
- Smart OCR (Tesseract)
- AI extraction (GPT-4)
- Validation (PO matching, rules)
- QuickBooks & Xero integration
- Batch processing
- Approval workflows
- Analytics & reporting
- MCP Server for Claude

## Requirements
- Python 3.9+
- Tesseract OCR
- Poppler utilities
- OpenAI API key

## Environment Variables
```
OPENAI_API_KEY=
QUICKBOOKS_CLIENT_ID=
QUICKBOOKS_CLIENT_SECRET=
XERO_CLIENT_ID=
XERO_CLIENT_SECRET=
DATABASE_URL=
```

## Status: Alpha (v0.1)
- Core OCR & extraction
- Basic validation
- API endpoints
- MCP server (in progress)

## Documentation
- `ANALYSIS_SUMMARY.md` - Architecture
- `ISSUES_FOUND.md` - Known issues
- `IMPROVEMENT_PLAN.md` - Roadmap
