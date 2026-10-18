"""Price API endpoints."""

from datetime import date, datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.models.company import Company
from app.models.price import PriceDaily
from app.schemas.price import (
    PriceDailyResponse,
    PriceHistoryResponse,
    ChartDataResponse,
    ChartDataPoint,
)
from app.schemas.common import PaginatedResponse, PaginationParams

router = APIRouter()


@router.get("/{ticker}/history", response_model=PriceHistoryResponse)
async def get_price_history(
    ticker: str,
    period: str = Query("1y", pattern="^(1m|3m|6m|1y|5y|all)$"),
    days: Optional[int] = Query(None, ge=1, le=1825),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Get price history for a company."""
    company_query = select(Company).where(Company.ticker == ticker.upper())
    company_result = await db.execute(company_query)
    company = company_result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    if days is not None:
        start_date = date.today() - timedelta(days=days)
    else:
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
        select(PriceDaily)
        .where(and_(PriceDaily.company_id == company.id, PriceDaily.date >= start_date))
        .order_by(desc(PriceDaily.date))
    )

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    query = query.offset(pagination.offset).limit(pagination.limit)
    result = await db.execute(query)
    prices = result.scalars().all()

    latest_query = (
        select(PriceDaily)
        .where(PriceDaily.company_id == company.id)
        .order_by(desc(PriceDaily.date))
        .limit(1)
    )
    latest_result = await db.execute(latest_query)
    latest_price = latest_result.scalar_one_or_none()

    return PriceHistoryResponse(
        company_id=company.id,
        ticker=company.ticker,
        name_en=company.name_en,
        name_fr=company.name_fr,
        name_ar=company.name_ar,
        data=[PriceDailyResponse.model_validate(p) for p in reversed(prices)],
        latest_price=PriceDailyResponse.model_validate(latest_price)
        if latest_price
        else None,
        period=period,
        total_records=total,
    )


@router.get("/{ticker}/chart", response_model=ChartDataResponse)
async def get_chart_data(
    ticker: str,
    period: str = Query("1y", pattern="^(1m|3m|6m|1y|5y|all)$"),
    limit: int = Query(500, ge=1, le=2000),
    db: AsyncSession = Depends(get_db),
):
    """Get chart data optimized for TradingView Lightweight Charts."""
    company_query = select(Company).where(Company.ticker == ticker.upper())
    company_result = await db.execute(company_query)
    company = company_result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

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
        select(PriceDaily)
        .where(and_(PriceDaily.company_id == company.id, PriceDaily.date >= start_date))
        .order_by(PriceDaily.date)
        .limit(limit)
    )
    result = await db.execute(query)
    prices = result.scalars().all()

    data = []
    for p in prices:
        data.append(
            ChartDataPoint(
                time=int(p.date.strftime("%s")),
                open=float(p.open_price),
                high=float(p.high_price),
                low=float(p.low_price),
                close=float(p.close_price),
                volume=p.volume,
            )
        )

    return ChartDataResponse(
        ticker=company.ticker,
        name=company.name_en,
        currency="TND",
        data=data,
        period=period,
    )


@router.get("/{ticker}/latest", response_model=PriceDailyResponse)
async def get_latest_price(
    ticker: str,
    db: AsyncSession = Depends(get_db),
):
    """Get latest price for a company."""
    company_query = select(Company).where(Company.ticker == ticker.upper())
    company_result = await db.execute(company_query)
    company = company_result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    latest_query = (
        select(PriceDaily)
        .where(PriceDaily.company_id == company.id)
        .order_by(desc(PriceDaily.date))
        .limit(1)
    )
    latest_result = await db.execute(latest_query)
    latest_price = latest_result.scalar_one_or_none()

    if not latest_price:
        raise HTTPException(status_code=404, detail="No price data available")

    return PriceDailyResponse.model_validate(latest_price)


@router.get("/latest", response_model=list[dict])
async def get_latest_prices(
    db: AsyncSession = Depends(get_db),
):
    """Get latest prices for all active companies (market overview)."""
    query = (
        select(Company)
        .options(selectinload(Company.sector))
        .where(Company.is_active == True)
    )
    result = await db.execute(query)
    companies = result.scalars().all()

    items = []
    for company in companies:
        latest_price_query = (
            select(PriceDaily)
            .where(PriceDaily.company_id == company.id)
            .order_by(PriceDaily.date.desc())
            .limit(1)
        )
        latest_result = await db.execute(latest_price_query)
        latest = latest_result.scalar_one_or_none()

        if not latest:
            continue

        prev_price_query = (
            select(PriceDaily.close_price)
            .where(PriceDaily.company_id == company.id)
            .where(PriceDaily.date < latest.date)
            .order_by(PriceDaily.date.desc())
            .limit(1)
        )
        prev_result = await db.execute(prev_price_query)
        prev_close = prev_result.scalar_one_or_none()

        change = float(latest.close_price) - (
            float(prev_close) if prev_close else float(latest.close_price)
        )
        change_pct = (
            (change / float(prev_close) * 100)
            if prev_close and float(prev_close) > 0
            else 0
        )

        items.append(
            {
                "symbol": company.ticker,
                "name": company.name_en,
                "price": float(latest.close_price),
                "change": round(change, 4),
                "change_percent": round(change_pct, 2),
                "volume": latest.volume,
                "open": float(latest.open_price),
                "high": float(latest.high_price),
                "low": float(latest.low_price),
                "close": float(latest.close_price),
                "previous_close": float(prev_close)
                if prev_close
                else float(latest.close_price),
                "market_cap": float(company.market_cap) if company.market_cap else None,
                "sector": company.sector.name_en if company.sector else "",
                "currency": "TND",
            }
        )

    return items


@router.get("/market/summary")
async def get_market_summary(
    db: AsyncSession = Depends(get_db),
):
    """Get market summary with top gainers, losers, volume leaders."""
    latest_date_query = select(func.max(PriceDaily.date))
    latest_date_result = await db.execute(latest_date_query)
    latest_date = latest_date_result.scalar()

    if not latest_date:
        return {"error": "No price data available"}

    subquery = (
        select(
            PriceDaily.company_id,
            PriceDaily.close_price,
            PriceDaily.daily_return_pct,
            PriceDaily.volume,
            PriceDaily.turnover,
        )
        .where(PriceDaily.date == latest_date)
        .subquery()
    )

    query = (
        select(
            Company.ticker,
            Company.name_en,
            Company.name_fr,
            Company.name_ar,
            Company.sector_id,
            subquery.c.close_price,
            subquery.c.daily_return_pct,
            subquery.c.volume,
            subquery.c.turnover,
        )
        .join(subquery, Company.id == subquery.c.company_id)
        .where(Company.is_active == True)
        .order_by(subquery.c.daily_return_pct.desc())
    )

    result = await db.execute(query)
    all_stocks = result.all()

    gainers = [
        {
            "ticker": s.ticker,
            "name_en": s.name_en,
            "name_fr": s.name_fr,
            "name_ar": s.name_ar,
            "price": float(s.close_price) if s.close_price else 0,
            "change_pct": float(s.daily_return_pct) if s.daily_return_pct else 0,
            "volume": s.volume,
            "turnover": float(s.turnover) if s.turnover else 0,
        }
        for s in all_stocks[:10]
    ]

    losers = [
        {
            "ticker": s.ticker,
            "name_en": s.name_en,
            "name_fr": s.name_fr,
            "name_ar": s.name_ar,
            "price": float(s.close_price) if s.close_price else 0,
            "change_pct": float(s.daily_return_pct) if s.daily_return_pct else 0,
            "volume": s.volume,
            "turnover": float(s.turnover) if s.turnover else 0,
        }
        for s in all_stocks[-10:][::-1]
    ]

    volume_leaders = sorted(all_stocks, key=lambda x: x.volume or 0, reverse=True)[:10]
    volume_data = [
        {
            "ticker": s.ticker,
            "name_en": s.name_en,
            "name_fr": s.name_fr,
            "name_ar": s.name_ar,
            "price": float(s.close_price) if s.close_price else 0,
            "change_pct": float(s.daily_return_pct) if s.daily_return_pct else 0,
            "volume": s.volume,
            "turnover": float(s.turnover) if s.turnover else 0,
        }
        for s in volume_leaders
    ]

    prices = [float(s.close_price) for s in all_stocks if s.close_price]
    tunindex_value = sum(prices) / len(prices) * 100 if prices else 0

    return {
        "date": latest_date.isoformat(),
        "tunindex": round(tunindex_value, 2),
        "total_stocks": len(all_stocks),
        "advancing": len(
            [s for s in all_stocks if s.daily_return_pct and s.daily_return_pct > 0]
        ),
        "declining": len(
            [s for s in all_stocks if s.daily_return_pct and s.daily_return_pct < 0]
        ),
        "unchanged": len(
            [s for s in all_stocks if s.daily_return_pct and s.daily_return_pct == 0]
        ),
        "total_volume": sum(s.volume or 0 for s in all_stocks),
        "total_turnover": sum(float(s.turnover or 0) for s in all_stocks),
        "top_gainers": gainers,
        "top_losers": losers,
        "volume_leaders": volume_data,
    }
