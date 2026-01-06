"""FastAPI REST API for invoice processing."""

from invoice_processor.api.main import app, create_app

__all__ = ["app", "create_app"]
