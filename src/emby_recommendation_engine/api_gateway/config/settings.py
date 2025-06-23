from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # Service URLs
    user_service_url: str = "http://user-service:8001"
    content_service_url: str = "http://content-service:8002"
    recommendation_service_url: str = "http://recommendation-service:8003"
    external_data_service_url: str = "http://external-data-service:8004"

    # External dependencies
    redis_url: str = "redis://redis:6379"
    kafka_bootstrap_servers: str = "kafka:9092"

    # Security
    secret_key: str = "your-secret-key-here"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get settings singleton"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
