"""
Application Configuration
Centralized settings management using Pydantic
"""

from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Stock Prediction System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:stockpred123@localhost:5432/stock_predictions"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # API Keys
    POLYGON_API_KEY: Optional[str] = None
    ALPACA_API_KEY: Optional[str] = None
    ALPACA_SECRET_KEY: Optional[str] = None
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    
    # Email Alerts
    SENDGRID_API_KEY: Optional[str] = None
    EMAIL_FROM: str = "noreply@stockpredictions.com"
    EMAIL_TO: str = ""
    
    # SMS Alerts
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_FROM_NUMBER: Optional[str] = None
    TWILIO_TO_NUMBER: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    API_KEY: str = "dev-api-key-12345"
    
    # ML Models
    MODEL_PATH: str = "./ml_models/trained_models"
    RETRAIN_INTERVAL_DAYS: int = 7
    
    # Data Fetching
    DATA_UPDATE_INTERVAL_MINUTES: int = 15
    STOCK_UNIVERSE: str = "SP500"  # SP500, RUSSELL1000, ALL
    
    # Performance
    MAX_WORKERS: int = 4
    BATCH_SIZE: int = 50
    CACHE_TTL_SECONDS: int = 300
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    # Prediction Settings
    MIN_CONFIDENCE_THRESHOLD: float = 0.55
    MAX_PREDICTIONS_PER_DAY: int = 50

    # Stock Universe Lists
    SP500_TICKERS_URL: str = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    RUSSELL1000_TICKERS_URL: str = "https://en.wikipedia.org/wiki/Russell_1000_Index"

    # Gmail SMTP for Email Alerts
    ALERT_EMAIL: Optional[str] = None
    ALERT_PASSWORD: Optional[str] = None
    RECIPIENT_EMAIL: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    """
    return Settings()


# Create global settings instance
settings = get_settings()
