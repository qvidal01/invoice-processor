# Contributing to Invoice Processor

Thank you for your interest in contributing to Invoice Processor! This document provides guidelines and instructions for contributing.

## Code of Conduct

This project adheres to a Code of Conduct (see [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior** vs **actual behavior**
- **Environment details** (OS, Python version, dependencies)
- **Sample invoice files** if applicable (remove sensitive data)
- **Error messages and stack traces**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear use case** - Why is this enhancement useful?
- **Detailed description** of the proposed feature
- **Examples** of how it would work
- **Alternative approaches** you've considered

### Pull Requests

1. **Fork** the repository
2. **Create a branch** from `develop` (not `main`)
3. **Make your changes** following our coding standards
4. **Add tests** for new functionality
5. **Update documentation** as needed
6. **Run the test suite** to ensure everything passes
7. **Submit a pull request** with a clear description

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Poetry for dependency management
- Tesseract OCR
- Poppler utils (for PDF processing)

### Installation

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/invoice-processor.git
cd invoice-processor

# Install system dependencies (Ubuntu/Debian)
sudo apt-get install tesseract-ocr poppler-utils

# Install system dependencies (macOS)
brew install tesseract poppler

# Create virtual environment and install dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with Poetry
pip install poetry
poetry install --with dev

# Set up pre-commit hooks
poetry run pre-commit install

# Copy environment file
cp .env.example .env
# Edit .env with your configuration
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=invoice_processor --cov-report=html

# Run specific test file
poetry run pytest tests/unit/test_models.py

# Run tests matching a pattern
poetry run pytest -k "test_validate"
```

### Code Quality

```bash
# Format code with Black
poetry run black .

# Lint with Ruff
poetry run ruff check .
poetry run ruff check --fix .  # Auto-fix issues

# Type checking with mypy
poetry run mypy src/invoice_processor

# Run all pre-commit hooks
poetry run pre-commit run --all-files
```

## Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use **Black** for code formatting (line length: 100)
- Use **Ruff** for linting
- Use **type hints** for all function parameters and return values
- Write **docstrings** for all public functions and classes (Google style)

### Example Function

```python
def process_invoice(
    file_path: Path,
    validate: bool = True,
    po_number: Optional[str] = None
) -> ProcessingResult:
    """
    Process a single invoice file.

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
    # Implementation here
    pass
```

### Testing Standards

- Write tests for all new features
- Maintain **80%+ code coverage**
- Use **pytest** for testing
- Use **fixtures** for test data
- Mock external API calls
- Test error conditions and edge cases

### Documentation

- Update README.md for user-facing changes
- Add docstrings to all public APIs
- Update ANALYSIS_SUMMARY.md for architectural changes
- Add examples for new features
- Keep CHANGELOG.md updated

## Git Workflow

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring
- `test/description` - Test additions

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short summary>

<detailed description>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Build/tooling changes

**Examples:**

```bash
feat(ocr): add support for TIFF images

Implement TIFF image support in OCR engine with preprocessing
for better accuracy on scanned documents.

Closes #123
```

```bash
fix(validator): correct amount validation logic

Fix decimal comparison issue in line item total validation
that was causing false negatives.

Fixes #456
```

## Project Structure

```
invoice-processor/
├── src/invoice_processor/       # Main package
│   ├── core/                    # Core processing modules
│   │   ├── ocr.py              # OCR engine
│   │   ├── extractor.py        # Data extraction
│   │   ├── validator.py        # Validation logic
│   │   └── processor.py        # Main processor
│   ├── integrations/           # External integrations
│   ├── api/                    # REST API
│   ├── mcp_server/             # MCP server
│   ├── db/                     # Database models
│   ├── utils/                  # Utilities
│   ├── models.py               # Data models
│   ├── config.py               # Configuration
│   └── cli.py                  # CLI interface
├── tests/                       # Test suite
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── fixtures/               # Test fixtures
├── docs/                        # Documentation
├── examples/                    # Usage examples
└── .github/workflows/          # CI/CD workflows
```

## Good First Issues

Looking for a place to start? Check out issues labeled `good first issue`:

### Potential Contributions

1. **Add support for additional image formats** (TIFF, BMP)
2. **Improve OCR preprocessing** (deskewing, noise reduction)
3. **Add more validation rules** (custom business rules)
4. **Enhance CLI output** (progress bars, better error messages)
5. **Add example notebooks** (Jupyter examples)
6. **Improve documentation** (API docs, tutorials)
7. **Add integration tests** (end-to-end workflows)
8. **Performance optimizations** (caching, async processing)

## Questions?

- **General questions**: Open a GitHub Discussion
- **Bug reports**: Open a GitHub Issue
- **Security issues**: Email contact@aiqso.io (do not open public issues)

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Acknowledged in release notes
- Eligible for maintainer roles based on contributions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Invoice Processor! 🎉**
