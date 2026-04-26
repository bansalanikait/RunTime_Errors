"""Application settings and configuration."""

from pydantic_settings import BaseSettings
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

    # Database
    database_url: str = "sqlite:///./deceptra.db"
    
    # Request logging
    max_body_log_size: int = 10000  # bytes; requests larger than this are truncated
    log_headers_sanitize: bool = True  # Redact Authorization, Cookie, X-API-Key
    log_level: str = "INFO"

    # Request timeout
    request_timeout_ms: int = 30000

    # CORS
    cors_origins: list = ["*"]

    # Base path for templates and static files
    base_path: Path = Path(__file__).parent.parent.parent

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
