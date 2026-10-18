"""Celery application for background tasks."""
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

app = Celery(
    "tunisia-markets",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.ingestion",
        "app.workers.anomaly_detection",
        "app.workers.news_scraping",
    ],
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_routes={
        "app.workers.ingestion.ingest_daily_prices": {"queue": "ingestion"},
        "app.workers.ingestion.ingest_fx_rates": {"queue": "ingestion"},
        "app.workers.anomaly_detection.detect_anomalies": {"queue": "analytics"},
        "app.workers.news_scraping.scrape_news": {"queue": "news"},
    },
)

# Celery Beat schedule
app.conf.beat_schedule = {
    "ingest-daily-prices": {
        "task": "app.workers.ingestion.ingest_daily_prices",
        "schedule": crontab(hour=18, minute=0, day_of_week="1-5"),
    },
    "ingest-fx-rates": {
        "task": "app.workers.ingestion.ingest_fx_rates",
        "schedule": crontab(minute=0),
    },
    "detect-anomalies": {
        "task": "app.workers.anomaly_detection.detect_anomalies",
        "schedule": crontab(hour=19, minute=0, day_of_week="1-5"),
    },
    "scrape-news": {
        "task": "app.workers.news_scraping.scrape_news",
        "schedule": crontab(minute="*/30"),
    },
    "ingest-commodities": {
        "task": "app.workers.ingestion.ingest_commodities",
        "schedule": crontab(hour=18, minute=30, day_of_week="1-5"),
    },
}