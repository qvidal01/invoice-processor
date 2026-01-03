# TODO (next session)

- [ ] Install system OCR binaries: `tesseract-ocr` and `poppler-utils`; verify with `tesseract --version`.
- [ ] Activate venv and confirm OCR libs import:  
      `source .venv/bin/activate && python - <<'PY'\nimport pdf2image, pytesseract; print('ocr libs ok')\nPY`
- [ ] Re-run tests after OCR binaries are present: `python -m pytest`.
- [ ] Install remaining runtime deps once `mcp` is available (fastapi, langchain, openai, uvicorn, etc.), or add conditional optional-deps flow.
- [ ] Add LLM-backed extraction path to `src/invoice_processor/core/extractor.py` (keep deterministic fallback; gate with a flag/env).
- [ ] Implement `_fetch_po_data` in `core/processor.py` to load POs from your datastore (e.g., SQLAlchemy models under `src/invoice_processor/db/`).
- [ ] Optionally migrate pydantic v1-style validators in `models.py` to `@field_validator` to remove deprecation warnings.
