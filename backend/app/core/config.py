from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "ACME Salary Management System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql://postgres@127.0.0.1:5432/acme_salary"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Security
    SECRET_KEY: str = "acme-super-secret-development-key-change-in-production-12345"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    # Initial Admin Bootstrap
    ADMIN_EMAIL: str = "hr.manager@acme.corp"
    ADMIN_INITIAL_PASSWORD: str = "AcmeHR2026!SecurePass"
    ADMIN_NAME: str = "HR Operations Manager"

    # Supported Currencies (ISO 4217)
    SUPPORTED_CURRENCIES: List[str] = [
        "USD",
        "EUR",
        "GBP",
        "CAD",
        "INR",
        "AUD",
        "SGD",
        "JPY",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
