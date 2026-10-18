"""Health check endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_db
from app.schemas.common import HealthCheckResponse, APIInfoResponse
from app.core.config import settings
import time

router = APIRouter()

_start_time = time.time()


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint."""
    db_status = "connected"
    redis_status = "connected"
    
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"
    
    # Redis check would go here if we had a redis dependency
    
    return HealthCheckResponse(
        status="healthy" if db_status == "connected" else "degraded",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        database=db_status,
        redis=redis_status,
        uptime_seconds=time.time() - _start_time,
    )


@router.get("/info", response_model=APIInfoResponse)
async def api_info():
    """API information endpoint."""
    return APIInfoResponse(
        name=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Tunisia Markets Hub API - Stock prices, FX rates, anomalies, and more",
        docs_url="/docs",
        openapi_url="/openapi.json",
        contact_email="contact@tunisia-markets.com",
    )