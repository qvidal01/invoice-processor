# 💰 Invoice Processor

[![CI](https://github.com/qvidal01/invoice-processor/workflows/CI/badge.svg)](https://github.com/qvidal01/invoice-processor/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Automated invoice extraction and processing using OCR and AI. Extract data from PDFs, validate against purchase orders, and integrate with accounting systems like QuickBooks and Xero.

**🎯 Perfect for:** Accounts payable teams, small businesses, accounting firms, and enterprises looking to automate invoice processing.

---

## ✨ Features

- **🔍 Smart OCR** - Extract text from PDF and image invoices using Tesseract OCR
- **🤖 AI-Powered Extraction** - Parse structured data with GPT-4 for 95%+ accuracy
- **✅ Validation Engine** - Verify against purchase orders and business rules
- **📊 QuickBooks & Xero Integration** - Seamlessly sync with accounting systems
- **⚡ Batch Processing** - Handle hundreds of invoices automatically
- **🔄 Approval Workflows** - Route invoices based on configurable rules
- **📈 Analytics & Reporting** - Track processing metrics and audit trails
- **🔌 MCP Server** - Enable AI assistants like Claude to process invoices
- **🛡️ Enterprise Security** - Input validation, encryption, audit logging

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.9 or higher
python --version

# Install system dependencies (Ubuntu/Debian)
sudo apt-get install tesseract-ocr poppler-utils

# Install system dependencies (macOS)
brew install tesseract poppler
```

### Installation

```bash
# Clone the repository
git clone https://github.com/qvidal01/invoice-processor.git
cd invoice-processor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with pip
pip install -e .

# Or install with Poetry (recommended)
pip install poetry
poetry install
```

### Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# Required: OPENAI_API_KEY
# Optional: QuickBooks/Xero credentials
nano .env
```

### Usage

#### Command Line

```bash
# Process a single invoice
invoice-processor process invoice.pdf

# Process a directory of invoices
invoice-processor batch --input ./invoices

# With validation
invoice-processor process invoice.pdf --po-number PO-12345

# View help
invoice-processor --help
```

#### Python API

```python
from invoice_processor import InvoiceProcessor
from invoice_processor.config import get_settings

# Initialize processor
settings = get_settings()
processor = InvoiceProcessor(openai_api_key=settings.openai_api_key)

# Process invoice
result = processor.process_invoice("invoice.pdf")

if result.success:
    invoice = result.invoice
    print(f"Vendor: {invoice.vendor_name}")
    print(f"Amount: ${invoice.total_amount}")
    print(f"Confidence: {invoice.confidence_score:.1%}")

    # Validation results
    if result.validation and result.validation.is_valid:
        print("✓ Invoice validated successfully")
    else:
        print("✗ Validation errors:", result.validation.errors)
```

#### MCP Server (AI Assistant Integration)

```bash
# Start MCP server
invoice-mcp-server

# Configure with Claude Desktop (see MCP docs)
```

See [MCP Server Documentation](src/invoice_processor/mcp_server/README.md) for detailed setup.

## 📖 Documentation

- **[Analysis & Design](ANALYSIS_SUMMARY.md)** - Architecture, technical decisions, and API design
- **[Issues Inventory](ISSUES_FOUND.md)** - Known issues and future improvements
- **[Improvement Plan](IMPROVEMENT_PLAN.md)** - Prioritized roadmap and milestones
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to the project
- **[Code of Conduct](CODE_OF_CONDUCT.md)** - Community guidelines
- **[API Documentation](docs/api.md)** - Complete API reference
- **[Examples](examples/)** - Runnable code examples

## 🎯 Use Cases

### 1. Automated AP Processing

```bash
# Process daily invoice batch
invoice-processor batch --input /shared/invoices/inbox --validate

# Invoices are:
# - Extracted and validated
# - Flagged for approval if needed
# - Ready to sync to accounting system
```

### 2. PO Matching & Validation

```python
# Validate invoice against purchase order
result = processor.process_invoice("vendor_invoice.pdf", po_number="PO-5678")

if result.validation.errors:
    # Amount mismatch, wrong vendor, etc.
    route_for_review(result.invoice, result.validation.errors)
else:
    # Auto-approve and sync
    sync_to_quickbooks(result.invoice)
```

### 3. AI-Assisted Processing

```
User (in Claude): Process the invoices in /invoices/2024-11/

Claude: [Uses MCP server to process 25 invoices]
I've processed 25 invoices totaling $45,230.
- 20 passed validation ✓
- 5 need review (amount discrepancies)

Would you like me to sync the approved ones to QuickBooks?
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  (CLI, Python API, MCP Client, REST API)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      Core Processing Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   OCR        │→ │  Extraction  │→ │  Validation  │         │
│  │   Engine     │  │  (GPT-4)     │  │   Engine     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    Integration & Storage                         │
│  - QuickBooks / Xero - Database - File Storage                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🧪 Testing

```bash
# Run test suite
pytest

# With coverage report
pytest --cov=invoice_processor --cov-report=html

# Run specific tests
pytest tests/unit/test_models.py

# Run integration tests
pytest tests/integration/
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

**Good First Issues:**
- Add support for TIFF images
- Improve OCR preprocessing
- Add more validation rules
- Enhance CLI output with progress bars
- Write additional examples

## 📊 Project Status

- ✅ **Phase 1-3**: Foundation, core modules, and testing complete
- ✅ **Phase 4**: MCP server proof-of-concept implemented
- 🚧 **Phase 5**: Full implementation in progress
- 📅 **Target v1.0**: Q2 2024

See [IMPROVEMENT_PLAN.md](IMPROVEMENT_PLAN.md) for detailed roadmap.

## 🔒 Security

- **Input Validation**: All inputs sanitized and validated
- **Secret Management**: API keys via environment variables only
- **Encryption**: OAuth tokens encrypted at rest
- **Audit Logging**: Complete audit trail of all operations
- **Security Scanning**: Automated checks in CI/CD

For security issues, email contact@aiqso.io (do not open public issues).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - OCR engine
- [OpenAI GPT-4](https://openai.com/) - AI-powered extraction
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Model Context Protocol](https://modelcontextprotocol.io/) - AI integration standard
- [Contributor Covenant](https://www.contributor-covenant.org/) - Code of Conduct

## 📞 Support

- **Documentation**: See [docs/](docs/) directory
- **Issues**: [GitHub Issues](https://github.com/qvidal01/invoice-processor/issues)
- **Discussions**: [GitHub Discussions](https://github.com/qvidal01/invoice-processor/discussions)
- **Email**: contact@aiqso.io

## 🌟 Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Made with ❤️ by [AIQSO](https://aiqso.io)**
