"""Configuration management for invoice processor."""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    # OpenAI Configuration
    openai_api_key: str = Field(..., description="OpenAI API key")

    # Database Configuration
    database_url: str = Field(
        default="sqlite:///./invoices.db", description="Database connection URL"
    )

    # Storage Configuration
    storage_path: Path = Field(default=Path("./data/invoices"), description="Invoice storage path")

    # QuickBooks Integration
    quickbooks_client_id: Optional[str] = Field(default=None, description="QuickBooks client ID")
    quickbooks_client_secret: Optional[str] = Field(
        default=None, description="QuickBooks client secret"
    )
    quickbooks_redirect_uri: Optional[str] = Field(
        default="http://localhost:8000/callback/quickbooks", description="OAuth redirect URI"
    )
    quickbooks_environment: str = Field(default="sandbox", description="QuickBooks environment")

    # Xero Integration
    xero_client_id: Optional[str] = Field(default=None, description="Xero client ID")
    xero_client_secret: Optional[str] = Field(default=None, description="Xero client secret")
    xero_redirect_uri: Optional[str] = Field(
        default="http://localhost:8000/callback/xero", description="OAuth redirect URI"
    )

    # Redis Configuration
    redis_url: Optional[str] = Field(
        default="redis://localhost:6379/0", description="Redis connection URL"
    )

    # API Server Configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_workers: int = Field(default=4, description="Number of API workers")
    api_secret_key: str = Field(default="change-me-in-production", description="JWT secret key")

    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format (json or text)")

    # Processing Configuration
    max_file_size_mb: int = Field(default=10, description="Maximum file size in MB")
    ocr_language: str = Field(default="eng", description="Tesseract OCR language")
    confidence_threshold: float = Field(default=0.7, description="Minimum confidence threshold")

    # Security
    token_encryption_key: str = Field(
        default="change-me-32-byte-encryption-key", description="Encryption key for tokens"
    )

    # Development
    debug: bool = Field(default=False, description="Debug mode")
    testing: bool = Field(default=False, description="Testing mode")

    @field_validator("storage_path")
    @classmethod
    def create_storage_path(cls, v: Path) -> Path:
        """Ensure storage path exists."""
        v.mkdir(parents=True, exist_ok=True)
        return v

    @field_validator("token_encryption_key")
    @classmethod
    def validate_encryption_key(cls, v: str) -> str:
        """Validate encryption key length."""
        if len(v) < 32:
            raise ValueError("Encryption key must be at least 32 characters")
        return v


def get_settings() -> Settings:
    """Get application settings singleton."""
    return Settings()
