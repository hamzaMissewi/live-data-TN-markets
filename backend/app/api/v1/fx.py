"""FX Rates API endpoints."""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.models.fx import FXPair, FXRate
from app.schemas.fx import (
    FXPairResponse,
    FXRateResponse,
    FXHistoryResponse,
    FXChartDataResponse,
    FXChartDataPoint,
    CurrencyConverterRequest,
    CurrencyConverterResponse,
)
from app.schemas.common import PaginatedResponse, PaginationParams

router = APIRouter()


@router.get("/rates", response_model=list[dict])
async def list_fx_rates(
    db: AsyncSession = Depends(get_db),
):
    """Get latest FX rates for all active pairs."""
    pairs_query = (
        select(FXPair).where(FXPair.is_active == True).order_by(FXPair.display_order)
    )
    pairs_result = await db.execute(pairs_query)
    pairs = pairs_result.scalars().all()

    items = []
    for pair in pairs:
        latest_query = (
            select(FXRate)
            .where(FXRate.pair_id == pair.id)
            .order_by(desc(FXRate.date), desc(FXRate.timestamp))
            .limit(1)
        )
        latest_result = await db.execute(latest_query)
        latest = latest_result.scalar_one_or_none()

        if not latest:
            continue

        items.append(
            {
                "id": latest.id,
                "pair_id": pair.id,
                "date": latest.date.isoformat() if latest.date else None,
                "rate": float(latest.rate),
                "base_currency": pair.base_currency,
                "quote_currency": pair.quote_currency,
                "symbol": pair.symbol,
                "change": float(latest.change_abs) if latest.change_abs else 0,
                "change_percent": float(latest.change_pct) if latest.change_pct else 0,
            }
        )

    return items


@router.get("/pairs", response_model=list[FXPairResponse])
async def list_fx_pairs(
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
):
    """List all currency pairs."""
    query = select(FXPair).order_by(FXPair.display_order)
    if active_only:
        query = query.where(FXPair.is_active == True)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/pairs/{pair_id}", response_model=FXPairResponse)
async def get_fx_pair(pair_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific currency pair."""
    pair = await db.get(FXPair, pair_id)
    if not pair:
        raise HTTPException(status_code=404, detail="Currency pair not found")
    return pair


@router.get("/{pair_symbol}/latest", response_model=FXRateResponse)
async def get_latest_fx_rate(
    pair_symbol: str,
    db: AsyncSession = Depends(get_db),
):
    """Get latest FX rate for a pair."""
    pair_query = select(FXPair).where(FXPair.symbol == pair_symbol.upper())
    pair_result = await db.execute(pair_query)
    pair = pair_result.scalar_one_or_none()

    if not pair:
        raise HTTPException(status_code=404, detail="Currency pair not found")

    latest_query = (
        select(FXRate)
        .where(FXRate.pair_id == pair.id)
        .order_by(desc(FXRate.date), desc(FXRate.timestamp))
        .limit(1)
    )
    latest_result = await db.execute(latest_query)
    latest_rate = latest_result.scalar_one_or_none()

    if not latest_rate:
        raise HTTPException(status_code=404, detail="No rate data available")

    return FXRateResponse.model_validate(latest_rate)


@router.get("/{pair_symbol}/history", response_model=FXHistoryResponse)
async def get_fx_history(
    pair_symbol: str,
    period: str = Query("1y", pattern="^(1m|3m|6m|1y|5y|all)$"),
    days: Optional[int] = Query(None, ge=1, le=1825),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Get FX rate history for a pair."""
    pair_query = select(FXPair).where(FXPair.symbol == pair_symbol.upper())
    pair_result = await db.execute(pair_query)
    pair = pair_result.scalar_one_or_none()

    if not pair:
        raise HTTPException(status_code=404, detail="Currency pair not found")

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
        select(FXRate)
        .where(and_(FXRate.pair_id == pair.id, FXRate.date >= start_date))
        .order_by(desc(FXRate.date))
    )

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    query = query.offset(pagination.offset).limit(pagination.limit)
    result = await db.execute(query)
    rates = result.scalars().all()

    latest_query = (
        select(FXRate)
        .where(FXRate.pair_id == pair.id)
        .order_by(desc(FXRate.date))
        .limit(1)
    )
    latest_result = await db.execute(latest_query)
    latest_rate = latest_result.scalar_one_or_none()

    return FXHistoryResponse(
        pair_id=pair.id,
        base_currency=pair.base_currency,
        quote_currency=pair.quote_currency,
        symbol=pair.symbol,
        name_en=pair.name_en,
        name_fr=pair.name_fr,
        name_ar=pair.name_ar,
        data=[FXRateResponse.model_validate(r) for r in reversed(rates)],
        latest_rate=FXRateResponse.model_validate(latest_rate) if latest_rate else None,
        period=period,
        total_records=total,
    )


@router.get("/{pair_symbol}/chart", response_model=FXChartDataResponse)
async def get_fx_chart(
    pair_symbol: str,
    period: str = Query("1y", pattern="^(1m|3m|6m|1y|5y|all)$"),
    limit: int = Query(500, ge=1, le=2000),
    db: AsyncSession = Depends(get_db),
):
    """Get FX chart data for TradingView Lightweight Charts."""
    pair_query = select(FXPair).where(FXPair.symbol == pair_symbol.upper())
    pair_result = await db.execute(pair_query)
    pair = pair_result.scalar_one_or_none()

    if not pair:
        raise HTTPException(status_code=404, detail="Currency pair not found")

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
        select(FXRate)
        .where(and_(FXRate.pair_id == pair.id, FXRate.date >= start_date))
        .order_by(FXRate.date)
        .limit(limit)
    )
    result = await db.execute(query)
    rates = result.scalars().all()

    data = []
    for r in rates:
        data.append(
            FXChartDataPoint(
                time=int(r.date.strftime("%s")),
                value=float(r.rate),
            )
        )

    latest_rate = data[-1].value if data else 0
    change_pct = None
    if len(data) >= 2:
        prev_value = data[-2].value
        if prev_value > 0:
            change_pct = ((latest_rate - prev_value) / prev_value) * 100

    return FXChartDataResponse(
        pair_symbol=pair.symbol,
        base_currency=pair.base_currency,
        quote_currency=pair.quote_currency,
        data=data,
        period=period,
        latest_rate=latest_rate,
        latest_change_pct=change_pct,
    )


@router.post("/convert", response_model=CurrencyConverterResponse)
async def convert_currency(
    request: CurrencyConverterRequest,
    db: AsyncSession = Depends(get_db),
):
    """Convert currency using latest or historical rate."""
    pair_query = select(FXPair).where(
        (FXPair.base_currency == request.from_currency.upper())
        & (FXPair.quote_currency == request.to_currency.upper())
    )
    pair_result = await db.execute(pair_query)
    pair = pair_result.scalar_one_or_none()

    if not pair:
        pair_query = select(FXPair).where(
            (FXPair.base_currency == request.to_currency.upper())
            & (FXPair.quote_currency == request.from_currency.upper())
        )
        pair_result = await db.execute(pair_query)
        pair = pair_result.scalar_one_or_none()
        if not pair:
            raise HTTPException(status_code=404, detail="Currency pair not found")
        inverse = True
    else:
        inverse = False

    if request.date:
        rate_query = (
            select(FXRate)
            .where(and_(FXRate.pair_id == pair.id, FXRate.date == request.date))
            .order_by(desc(FXRate.timestamp))
            .limit(1)
        )
    else:
        rate_query = (
            select(FXRate)
            .where(FXRate.pair_id == pair.id)
            .order_by(desc(FXRate.date), desc(FXRate.timestamp))
            .limit(1)
        )

    rate_result = await db.execute(rate_query)
    rate = rate_result.scalar_one_or_none()

    if not rate:
        raise HTTPException(status_code=404, detail="No rate data available")

    rate_value = float(rate.rate)
    if inverse:
        rate_value = 1 / rate_value

    converted = float(request.amount) * rate_value
    inverse_rate = 1 / rate_value

    return CurrencyConverterResponse(
        from_currency=request.from_currency.upper(),
        to_currency=request.to_currency.upper(),
        amount=request.amount,
        rate=Decimal(str(rate_value)),
        converted_amount=Decimal(str(converted)),
        rate_date=rate.date,
        rate_source=rate.source,
        inverse_rate=Decimal(str(inverse_rate)),
    )
