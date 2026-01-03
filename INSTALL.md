# Installation Guide

This project runs locally with Python 3.9+ and optional OCR system packages. No external services are required for the default deterministic extractor.

## 1) System prerequisites

- Python 3.9 or later
- Recommended OCR tooling:
  - **Debian/Ubuntu**: `sudo apt-get install tesseract-ocr poppler-utils`
  - **macOS (Homebrew)**: `brew install tesseract poppler`
  - **Windows**: install Tesseract from the official installer and ensure it is on `PATH`

## 2) Create an isolated environment

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
```

## 3) Install dependencies

```bash
pip install --upgrade pip
pip install -e .
# Optional: install dev/test tooling (pytest, ruff, mypy, etc.)
pip install -r requirements-dev.txt
```

If you prefer Poetry:

```bash
pip install poetry
poetry install
```

## 4) Configure environment

The extractor currently requires a non-empty `OPENAI_API_KEY` even though it operates offline. Set a placeholder value for local use:

```bash
export OPENAI_API_KEY=dummy-key
```

Optional settings (see `config.py` for defaults):
- `OCR_LANGUAGE` (default: `eng`)
- `MAX_FILE_SIZE_MB`
- `LOG_LEVEL`, `LOG_FORMAT`
- `STORAGE_PATH`

## 5) Validate the setup

```bash
pytest
```

If OCR system packages are missing, PDF/image extraction will raise a clear ImportError; install Tesseract/pdf2image dependencies as noted above.

## 6) Run the tools

- CLI: `invoice-processor process ./invoice.pdf`
- MCP server: `invoice-mcp-server`

Refer to `README.md` and `ARCHITECTURE.md` for usage and design details.
