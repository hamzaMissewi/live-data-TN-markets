import os
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Tunisia Markets Hub"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # API
    API_PREFIX: str = "/api/v1"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/tunisia_markets",
        validation_alias="DATABASE_URL"
    )
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="REDIS_URL"
    )
    REDIS_CACHE_TTL: int = 300  # 5 minutes
    
    # Celery
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/1",
        validation_alias="CELERY_BROKER_URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/2",
        validation_alias="CELERY_RESULT_BACKEND"
    )
    
    # External APIs
    BVMT_BASE_URL: str = "https://www.bvmt.com.tn"
    BCT_BASE_URL: str = "https://www.bct.gov.tn"
    EXCHANGERATE_API_URL: str = "https://api.exchangerate.host"
    ECB_RATES_URL: str = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
    
    # Scraping
    SCRAPER_TIMEOUT: int = 30
    SCRAPER_MAX_RETRIES: int = 3
    SCRAPER_USER_AGENT: str = "Mozilla/5.0 (compatible; TunisiaMarketsBot/1.0; +https://tunisia-markets.com/bot)"
    
    # Scheduling
    STOCK_INGESTION_CRON: str = "0 18 * * 1-5"  # Daily at 6 PM on weekdays
    FX_INGESTION_CRON: str = "0 * * * *"  # Hourly
    ANOMALY_DETECTION_CRON: str = "0 19 * * 1-5"  # Daily at 7 PM on weekdays
    
    # AdSense & Monetization
    ADSENSE_CLIENT_ID: Optional[str] = None
    ADSENSE_SLOT_CHART: Optional[str] = None
    ADSENSE_SLOT_SIDEBAR: Optional[str] = None
    ADSENSE_SLOT_IN_CONTENT: Optional[str] = None
    
    # Frontend URL (for CORS)
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    
    # Security
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production", validation_alias="SECRET_KEY")
    API_KEY_HEADER: str = "X-API-Key"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()