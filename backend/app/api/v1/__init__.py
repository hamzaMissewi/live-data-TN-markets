"""API v1 routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.api.v1 import companies, prices, anomalies, fx, news, commodities, health
from app.db.session import get_db
from app.models.company import Sector
from app.schemas.company import SectorResponse

api_v1_router = APIRouter()


# Root-level sectors endpoint (frontend calls /api/v1/sectors)
@api_v1_router.get("/sectors", response_model=list[SectorResponse])
async def list_sectors_root(
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
):
    """List all market sectors (root-level endpoint)."""
    query = select(Sector)
    if active_only:
        query = query.where(Sector.is_active == True)
    query = query.order_by(Sector.code)
    result = await db.execute(query)
    return result.scalars().all()


# Root-level health endpoint (frontend calls /api/v1/health)
@api_v1_router.get("/health")
async def health_root(db: AsyncSession = Depends(get_db)):
    """Health check endpoint (v1 alias)."""
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
    }


api_v1_router.include_router(health.router, tags=["Health"])
api_v1_router.include_router(companies.router, prefix="/companies", tags=["Companies"])
api_v1_router.include_router(prices.router, prefix="/prices", tags=["Prices"])
api_v1_router.include_router(anomalies.router, prefix="/anomalies", tags=["Anomalies"])
api_v1_router.include_router(fx.router, prefix="/fx", tags=["FX Rates"])
api_v1_router.include_router(news.router, prefix="/news", tags=["News"])
api_v1_router.include_router(
    commodities.router, prefix="/commodities", tags=["Commodities"]
)
