"""Commodities API endpoints."""

from datetime import date, datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.models.commodity import Commodity, CommodityPrice
from app.schemas.commodity import (
    CommodityResponse,
    CommodityPriceResponse,
    CommodityHistoryResponse,
    CommodityChartDataResponse,
    CommodityChartDataPoint,
)
from app.schemas.common import PaginatedResponse, PaginationParams

router = APIRouter()


@router.get("/prices", response_model=list[dict])
async def list_commodity_prices(
    db: AsyncSession = Depends(get_db),
):
    """Get latest prices for all active commodities."""
    commodities_query = (
        select(Commodity)
        .where(Commodity.is_active == True)
        .order_by(Commodity.display_order)
    )
    commodities_result = await db.execute(commodities_query)
    commodities = commodities_result.scalars().all()

    items = []
    for commodity in commodities:
        latest_query = (
            select(CommodityPrice)
            .where(CommodityPrice.commodity_id == commodity.id)
            .order_by(desc(CommodityPrice.date), desc(CommodityPrice.timestamp))
            .limit(1)
        )
        latest_result = await db.execute(latest_query)
        latest = latest_result.scalar_one_or_none()

        if not latest:
            continue

        items.append(
            {
                "id": latest.id,
                "commodity_id": commodity.id,
                "date": latest.date.isoformat() if latest.date else None,
                "price": float(latest.price),
                "change": float(latest.change_abs) if latest.change_abs else 0,
                "change_percent": float(latest.change_pct) if latest.change_pct else 0,
                "code": commodity.code,
                "name": commodity.name_en,
                "unit": commodity.unit_en,
            }
        )

    return items


@router.get("", response_model=list[CommodityResponse])
async def list_commodities(
    active_only: bool = Query(True),
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List all commodities."""
    query = select(Commodity).order_by(Commodity.display_order)
    if active_only:
        query = query.where(Commodity.is_active == True)
    if category:
        query = query.where(Commodity.category == category)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/categories", response_model=list[str])
async def get_commodity_categories(
    db: AsyncSession = Depends(get_db),
):
    """Get all commodity categories."""
    query = select(Commodity.category).distinct().where(Commodity.is_active == True)
    result = await db.execute(query)
    return [row[0] for row in result.all()]


@router.get("/{commodity_code}/latest", response_model=CommodityPriceResponse)
async def get_latest_commodity_price(
    commodity_code: str,
    db: AsyncSession = Depends(get_db),
):
    """Get latest price for a commodity."""
    commodity_query = select(Commodity).where(Commodity.code == commodity_code.upper())
    commodity_result = await db.execute(commodity_query)
    commodity = commodity_result.scalar_one_or_none()

    if not commodity:
        raise HTTPException(status_code=404, detail="Commodity not found")

    latest_query = (
        select(CommodityPrice)
        .where(CommodityPrice.commodity_id == commodity.id)
        .order_by(desc(CommodityPrice.date), desc(CommodityPrice.timestamp))
        .limit(1)
    )
    latest_result = await db.execute(latest_query)
    latest_price = latest_result.scalar_one_or_none()

    if not latest_price:
        raise HTTPException(status_code=404, detail="No price data available")

    return CommodityPriceResponse.model_validate(latest_price)


@router.get("/{commodity_code}/history", response_model=CommodityHistoryResponse)
async def get_commodity_history(
    commodity_code: str,
    period: str = Query("1y", pattern="^(1m|3m|6m|1y|5y|all)$"),
    days: Optional[int] = Query(None, ge=1, le=1825),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Get price history for a commodity."""
    commodity_query = select(Commodity).where(Commodity.code == commodity_code.upper())
    commodity_result = await db.execute(commodity_query)
    commodity = commodity_result.scalar_one_or_none()

    if not commodity:
        raise HTTPException(status_code=404, detail="Commodity not found")

    today = date.today()
    if days is not None:
        start_date = today - timedelta(days=days)
    elif period == "1m":
        start_date = today.replace(day=1)
        if start_date.month == 1:
            start_date = start_date.replace(year=start_date.year - 1, month=12)
        else:
            start_date = start_date.replace(month=start_date.month - 1)
    elif period == "3m":
        start_date = (
            today.replace(month=today.month - 3)
            if today.month > 3
            else today.replace(year=today.year - 1, month=today.month + 9)
        )
    elif period == "6m":
        start_date = (
            today.replace(month=today.month - 6)
            if today.month > 6
            else today.replace(year=today.year - 1, month=today.month + 6)
        )
    elif period == "1y":
        start_date = today.replace(year=today.year - 1)
    elif period == "5y":
        start_date = today.replace(year=today.year - 5)
    else:
        start_date = date(1900, 1, 1)

    query = (
        select(CommodityPrice)
        .where(
            and_(
                CommodityPrice.commodity_id == commodity.id,
                CommodityPrice.date >= start_date,
            )
        )
        .order_by(desc(CommodityPrice.date))
    )

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    query = query.offset(pagination.offset).limit(pagination.limit)
    result = await db.execute(query)
    prices = result.scalars().all()

    latest_query = (
        select(CommodityPrice)
        .where(CommodityPrice.commodity_id == commodity.id)
        .order_by(desc(CommodityPrice.date))
        .limit(1)
    )
    latest_result = await db.execute(latest_query)
    latest_price = latest_result.scalar_one_or_none()

    return CommodityHistoryResponse(
        commodity_id=commodity.id,
        code=commodity.code,
        name_en=commodity.name_en,
        name_fr=commodity.name_fr,
        name_ar=commodity.name_ar,
        unit_en=commodity.unit_en,
        unit_fr=commodity.unit_fr,
        unit_ar=commodity.unit_ar,
        local_unit_en=commodity.local_unit_en,
        local_unit_fr=commodity.local_unit_fr,
        local_unit_ar=commodity.local_unit_ar,
        data=[CommodityPriceResponse.model_validate(p) for p in reversed(prices)],
        latest_price=CommodityPriceResponse.model_validate(latest_price)
        if latest_price
        else None,
        period=period,
        total_records=total,
    )


@router.get("/{commodity_code}/chart", response_model=CommodityChartDataResponse)
async def get_commodity_chart(
    commodity_code: str,
    period: str = Query("1y", pattern="^(1m|3m|6m|1y|5y|all)$"),
    limit: int = Query(500, ge=1, le=2000),
    db: AsyncSession = Depends(get_db),
):
    """Get commodity chart data for TradingView Lightweight Charts."""
    commodity_query = select(Commodity).where(Commodity.code == commodity_code.upper())
    commodity_result = await db.execute(commodity_query)
    commodity = commodity_result.scalar_one_or_none()

    if not commodity:
        raise HTTPException(status_code=404, detail="Commodity not found")

    today = date.today()
    if period == "1m":
        start_date = today.replace(day=1)
        if start_date.month == 1:
            start_date = start_date.replace(year=start_date.year - 1, month=12)
        else:
            start_date = start_date.replace(month=start_date.month - 1)
    elif period == "3m":
        start_date = (
            today.replace(month=today.month - 3)
            if today.month > 3
            else today.replace(year=today.year - 1, month=today.month + 9)
        )
    elif period == "6m":
        start_date = (
            today.replace(month=today.month - 6)
            if today.month > 6
            else today.replace(year=today.year - 1, month=today.month + 6)
        )
    elif period == "1y":
        start_date = today.replace(year=today.year - 1)
    elif period == "5y":
        start_date = today.replace(year=today.year - 5)
    else:
        start_date = date(1900, 1, 1)

    query = (
        select(CommodityPrice)
        .where(
            and_(
                CommodityPrice.commodity_id == commodity.id,
                CommodityPrice.date >= start_date,
            )
        )
        .order_by(CommodityPrice.date)
        .limit(limit)
    )
    result = await db.execute(query)
    prices = result.scalars().all()

    data = []
    for p in prices:
        data.append(
            CommodityChartDataPoint(
                time=int(p.date.strftime("%s")),
                value=float(p.price),
                local_value=float(p.local_price) if p.local_price else None,
            )
        )

    latest_price = data[-1].value if data else 0
    change_pct = None
    if len(data) >= 2:
        prev_value = data[-2].value
        if prev_value > 0:
            change_pct = ((latest_price - prev_value) / prev_value) * 100

    return CommodityChartDataResponse(
        commodity_code=commodity.code,
        name=commodity.name_en,
        unit=commodity.unit_en,
        local_unit=commodity.local_unit_en,
        data=data,
        period=period,
        latest_price=latest_price,
        latest_change_pct=change_pct,
    )
