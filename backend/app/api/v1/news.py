"""News API endpoints."""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, or_
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.models.news import NewsItem, NewsSource
from app.schemas.news import (
    NewsSourceResponse, NewsItemResponse, NewsListResponse
)
from app.schemas.common import PaginatedResponse, PaginationParams

router = APIRouter()


@router.get("/sources", response_model=list[NewsSourceResponse])
async def list_news_sources(
    active_only: bool = Query(True),
    language: Optional[str] = Query(None, pattern="^(en|fr|ar)$"),
    db: AsyncSession = Depends(get_db),
):
    """List all news sources."""
    query = select(NewsSource).order_by(NewsSource.name)
    if active_only:
        query = query.where(NewsSource.is_active == True)
    if language:
        query = query.where(NewsSource.language == language)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("", response_model=PaginatedResponse[NewsListResponse])
async def list_news(
    pagination: PaginationParams = Depends(),
    source_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    sentiment: Optional[str] = Query(None, pattern="^(positive|negative|neutral)$"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    search: Optional[str] = Query(None, max_length=200),
    db: AsyncSession = Depends(get_db),
):
    """List news items with filters and pagination."""
    query = (
        select(NewsItem)
        .options(selectinload(NewsItem.source))
        .where(NewsItem.is_published == True)
        .order_by(desc(NewsItem.published_at))
    )
    
    conditions = []
    if source_id:
        conditions.append(NewsItem.source_id == source_id)
    if category:
        conditions.append(NewsItem.category == category)
    if sentiment:
        conditions.append(NewsItem.sentiment == sentiment)
    if start_date:
        conditions.append(NewsItem.published_at >= start_date)
    if end_date:
        conditions.append(NewsItem.published_at <= end_date)
    if search:
        search_term = f"%{search}%"
        conditions.append(
            or_(
                NewsItem.title_fr.ilike(search_term),
                NewsItem.title_en.ilike(search_term),
                NewsItem.title_ar.ilike(search_term),
                NewsItem.summary_fr.ilike(search_term),
            )
        )
    
    if conditions:
        query = query.where(and_(*conditions))
    
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0
    
    query = query.offset(pagination.offset).limit(pagination.limit)
    result = await db.execute(query)
    news = result.scalars().all()
    
    items = [
        NewsListResponse(
            id=n.id,
            source_id=n.source_id,
            source_name=n.source.name if n.source else "",
            source=n.source.name if n.source else "",
            url=n.url,
            title_en=n.title_en,
            title_fr=n.title_fr,
            title_ar=n.title_ar,
            summary_en=n.summary_en,
            summary_fr=n.summary_fr,
            summary_ar=n.summary_ar,
            category=n.category,
            sentiment=n.sentiment,
            published_at=n.published_at,
            mentioned_tickers=n.mentioned_tickers,
        )
        for n in news
    ]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=(total + pagination.page_size - 1) // pagination.page_size,
        has_next=pagination.page * pagination.page_size < total,
        has_prev=pagination.page > 1,
    )
@router.get("/latest", response_model=list[NewsListResponse])
async def get_latest_news(
    limit: int = Query(10, ge=1, le=50),
    lang: str = Query("fr", pattern="^(en|fr|ar)$"),
    db: AsyncSession = Depends(get_db),
):
    """Get latest news items."""
    query = (
        select(NewsItem)
        .options(selectinload(NewsItem.source))
        .where(NewsItem.is_published == True)
        .order_by(desc(NewsItem.published_at))
        .limit(limit)
    )
    result = await db.execute(query)
    news = result.scalars().all()
    
    return [
        NewsListResponse(
            id=n.id,
            source_id=n.source_id,
            source_name=n.source.name if n.source else "",
            source=n.source.name if n.source else "",
            url=n.url,
            title_en=n.title_en,
            title_fr=n.title_fr,
            title_ar=n.title_ar,
            summary_en=n.summary_en,
            summary_fr=n.summary_fr,
            summary_ar=n.summary_ar,
            category=n.category,
            sentiment=n.sentiment,
            published_at=n.published_at,
            mentioned_tickers=n.mentioned_tickers,
        )
        for n in news
    ]


@router.get("/{news_id}", response_model=NewsItemResponse)
async def get_news_item(
    news_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific news item by ID."""
    query = (
        select(NewsItem)
        .options(selectinload(NewsItem.source))
        .where(NewsItem.id == news_id)
    )
    result = await db.execute(query)
    news = result.scalar_one_or_none()
    
    if not news:
        raise HTTPException(status_code=404, detail="News item not found")
    
    return news


@router.get("/company/{ticker}", response_model=PaginatedResponse[NewsListResponse])
async def get_company_news(
    ticker: str,
    pagination: PaginationParams = Depends(),
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    """Get news mentioning a specific company."""
    from app.models.company import Company
    from datetime import timedelta
    
    company_query = select(Company).where(Company.ticker == ticker.upper())
    company_result = await db.execute(company_query)
    company = company_result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    query = (
        select(NewsItem)
        .options(selectinload(NewsItem.source))
        .where(
            and_(
                NewsItem.is_published == True,
                NewsItem.published_at >= cutoff_date,
                NewsItem.mentioned_tickers.contains(ticker.upper())
            )
        )
        .order_by(desc(NewsItem.published_at))
    )
    
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0
    
    query = query.offset(pagination.offset).limit(pagination.limit)
    result = await db.execute(query)
    news = result.scalars().all()
    
    items = [
        NewsListResponse(
            id=n.id,
            source_id=n.source_id,
            source_name=n.source.name if n.source else "",
            source=n.source.name if n.source else "",
            url=n.url,
            title_en=n.title_en,
            title_fr=n.title_fr,
            title_ar=n.title_ar,
            summary_en=n.summary_en,
            summary_fr=n.summary_fr,
            summary_ar=n.summary_ar,
            category=n.category,
            sentiment=n.sentiment,
            published_at=n.published_at,
            mentioned_tickers=n.mentioned_tickers,
        )
        for n in news
    ]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=(total + pagination.page_size - 1) // pagination.page_size,
        has_next=pagination.page * pagination.page_size < total,
        has_prev=pagination.page > 1,
    )