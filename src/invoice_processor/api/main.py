"""FastAPI application for invoice processing service."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from invoice_processor.api.routes import router
from invoice_processor.config import get_settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    logger.info("Invoice Processor API starting up")
    yield
    logger.info("Invoice Processor API shutting down")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Invoice Processor API",
        description="AI-powered invoice processing with OCR extraction",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Configure CORS - allow internal network access
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:3001",
            "http://192.168.0.*",
            "https://demo-api.aiqso.io",
            "https://aiqso.io",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routes
    app.include_router(router, prefix="/api")

    @app.get("/")
    async def root() -> dict:
        """Root endpoint with service information."""
        return {
            "service": "Invoice Processor API",
            "version": "0.1.0",
            "docs": "/docs",
            "health": "/api/health",
        }

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "invoice_processor.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
