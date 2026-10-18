"""Companies API endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.models.company import Company, Sector
from app.schemas.company import (
    CompanyResponse, CompanyListResponse, SectorResponse,
    CompanyCreate, CompanyUpdate
)
from app.schemas.common import PaginatedResponse, PaginationParams

router = APIRouter()


@router.get("/sectors", response_model=list[SectorResponse])
async def list_sectors(
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
):
    """List all market sectors."""
    query = select(Sector)
    if active_only:
        query = query.where(Sector.is_active == True)
    query = query.order_by(Sector.code)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/sectors/{sector_id}", response_model=SectorResponse)
async def get_sector(sector_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific sector by ID."""
    sector = await db.get(Sector, sector_id)
    if not sector:
        raise HTTPException(status_code=404, detail="Sector not found")
    return sector
@router.get("", response_model=PaginatedResponse[CompanyListResponse])
async def list_companies(
    pagination: PaginationParams = Depends(),
    sector_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(True),
    search: Optional[str] = Query(None, max_length=100),
    sort_by: str = Query("ticker", pattern="^(ticker|name_en|market_cap|last_price_date)$"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
):
    """List companies with pagination and filters."""
    query = select(Company).options(selectinload(Company.sector))
    
    # Filters
    conditions = []
    if sector_id is not None:
        conditions.append(Company.sector_id == sector_id)
    if is_active is not None:
        conditions.append(Company.is_active == is_active)
    if search:
        search_term = f"%{search}%"
        conditions.append(
            or_(
                Company.ticker.ilike(search_term),
                Company.name_en.ilike(search_term),
                Company.name_fr.ilike(search_term),
                Company.name_ar.ilike(search_term),
            )
        )
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0
# Sorting
    sort_column = getattr(Company, sort_by, Company.ticker)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # Pagination
    query = query.offset(pagination.offset).limit(pagination.limit)
    
    result = await db.execute(query)
    companies = result.scalars().all()
    
    # Transform to list response with latest price
    items = []
    for company in companies:
        # Get latest price
        latest_price_query = (
            select(PriceDaily.close_price, PriceDaily.date, PriceDaily.daily_return_pct)
            .where(PriceDaily.company_id == company.id)
            .order_by(PriceDaily.date.desc())
            .limit(1)
        )
        latest_price_result = await db.execute(latest_price_query)
        latest_price_data = latest_price_result.first()
        
        items.append(CompanyListResponse(
            id=company.id,
            ticker=company.ticker,
            name_en=company.name_en,
            name_fr=company.name_fr,
            name_ar=company.name_ar,
            short_name_en=company.short_name_en,
            short_name_fr=company.short_name_fr,
            short_name_ar=company.short_name_ar,
            sector_id=company.sector_id,
            sector_name_en=company.sector.name_en if company.sector else None,
            sector_name_fr=company.sector.name_fr if company.sector else None,
            sector_name_ar=company.sector.name_ar if company.sector else None,
            is_active=company.is_active,
            is_suspended=company.is_suspended,
            last_price=latest_price_data[0] if latest_price_data else None,
            last_price_date=latest_price_data[1] if latest_price_data else None,
            daily_change_pct=latest_price_data[2] if latest_price_data else None,
            market_cap=company.market_cap,
            slug_en=company.slug_en,
            slug_fr=company.slug_fr,
            slug_ar=company.slug_ar,
        ))
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=(total + pagination.page_size - 1) // pagination.page_size,
        has_next=pagination.page * pagination.page_size < total,
        has_prev=pagination.page > 1,
    )
@router.get("/{ticker}", response_model=CompanyResponse)
async def get_company(
    ticker: str,
    lang: str = Query("en", pattern="^(en|fr|ar)$"),
    db: AsyncSession = Depends(get_db),
):
    """Get company details by ticker."""
    query = (
        select(Company)
        .options(selectinload(Company.sector))
        .where(Company.ticker == ticker.upper())
    )
    result = await db.execute(query)
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    return company


@router.get("/slug/{slug}", response_model=CompanyResponse)
async def get_company_by_slug(
    slug: str,
    lang: str = Query("en", pattern="^(en|fr|ar)$"),
    db: AsyncSession = Depends(get_db),
):
    """Get company details by slug (SEO-friendly URL)."""
    slug_column = getattr(Company, f"slug_{lang}", Company.slug_en)
    query = (
        select(Company)
        .options(selectinload(Company.sector))
        .where(slug_column == slug)
    )
    result = await db.execute(query)
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    return company


@router.post("", response_model=CompanyResponse, status_code=201)
async def create_company(
    company_data: CompanyCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new company (admin only)."""
    existing = await db.execute(
        select(Company).where(Company.ticker == company_data.ticker.upper())
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Ticker already exists")
    
    company = Company(**company_data.model_dump())
    company.ticker = company.ticker.upper()
    if company.isin:
        company.isin = company.isin.upper()
    
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company


@router.patch("/{ticker}", response_model=CompanyResponse)
async def update_company(
    ticker: str,
    company_data: CompanyUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update company details (admin only)."""
    query = select(Company).where(Company.ticker == ticker.upper())
    result = await db.execute(query)
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    update_data = company_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)
    
    await db.commit()
    await db.refresh(company)
    return company