"""Application settings and configuration."""

from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path


class Settings(BaseSettings):
    """
    Application configuration loaded from environment or .env file.
    
    All settings default to development-friendly values.
    Override via environment variables or .env file.
    """

    # Application metadata
    app_name: str = "DECEPTRA"
    app_version: str = "1.0.0"
    debug: bool = True

    # Base path for templates and static files
    base_path: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent)

    # Database
    database_url: str = Field(default_factory=lambda: f"sqlite:///{Path(__file__).parent.parent.parent.as_posix()}/deceptra.db")
    
    # Request logging
    max_body_log_size: int = 10000  # bytes; requests larger than this are truncated
    log_headers_sanitize: bool = True  # Redact Authorization, Cookie, X-API-Key
    log_level: str = "INFO"

    # Request timeout
    request_timeout_ms: int = 30000

    # CORS
    cors_origins: list = ["*"]

    # AI Settings
    llm_api_key: str = "local-key-fallback"
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model_name: str = "gpt-3.5-turbo"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
