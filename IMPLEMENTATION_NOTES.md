# Implementation Notes

This document explains the practical decisions made to keep the project runnable today while leaving clear seams for future production features.

## Extraction strategy
- **Deterministic-first**: `core/extractor.py` uses regex/date parsing and conservative defaults. This avoids network calls and keeps unit tests fast.
- **LLM seam**: The constructor still accepts an OpenAI API key; replacing `extract_invoice_data` with an LLM-backed path can reuse the same output shape (`InvoiceData`).
- **Fallback line items**: When tables cannot be parsed, a single summary `LineItem` is created so downstream validation still has structured data.
- **Confidence scoring**: Lightweight heuristic (signal count) to avoid overstating quality until an ML model is available.

## OCR pipeline
- **Text-first**: PyPDF2 is used before OCR; this short-circuits work for digital PDFs.
- **OCR fallback**: pdf2image + pytesseract provide a cross-platform fallback. Import errors are surfaced with clear guidance.
- **Preprocessing**: Grayscale, denoise, autocontrast, and optional deskewing improve accuracy without heavy dependencies.
- **Orientation**: Orientation detection is best-effort; failure results in zero rotation instead of raising.

## Processor safeguards
- `InvoiceProcessor` validates file existence, allowed extensions, optional trusted base directory, and size limits before invoking OCR.
- Errors surface through `ProcessingResult.error` so CLI/MCP callers can return actionable messages without stack traces.

## Validation
- `InvoiceValidator` covers completeness, amount/date checks, PO enforcement, and low-confidence warnings.
- TODO hooks remain for purchase-order lookup and duplicate detection; these are expected to integrate with a database layer.

## Configuration
- `pydantic-settings` loads environment variables and eagerly creates the storage path to avoid runtime surprises.
- CLI now fails fast with a human-readable configuration error if required settings are missing.

## Testing philosophy
- Unit tests exercise parsing heuristics, guardrails, and validation logic without requiring OCR binaries.
- OCR-dependent paths are covered by negative tests (missing files, wrong extensions) to avoid CI flakiness where Tesseract may be unavailable.
