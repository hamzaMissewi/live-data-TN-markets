"""Anomaly API endpoints."""

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, or_
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.models.company import Company
from app.models.anomaly import Anomaly, AnomalyType
from app.schemas.anomaly import (
    AnomalyResponse,
    AnomalyListResponse,
    AnomalyStatsResponse,
    AnomalyType as AnomalyTypeSchema,
    Severity,
)
from app.schemas.common import PaginatedResponse, PaginationParams

router = APIRouter()


@router.get("", response_model=dict)
async def list_anomalies(
    pagination: PaginationParams = Depends(),
    company_id: Optional[int] = Query(None),
    anomaly_type: Optional[AnomalyTypeSchema] = Query(None),
    severity: Optional[Severity] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    is_reviewed: Optional[bool] = Query(None),
    is_explained: Optional[bool] = Query(None),
    days: Optional[int] = Query(None, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    """List anomalies with filters and pagination."""
    from datetime import timedelta

    query = (
        select(Anomaly)
        .options(selectinload(Anomaly.company))
        .order_by(desc(Anomaly.date), desc(Anomaly.created_at))
    )

    conditions = []
    if company_id:
        conditions.append(Anomaly.company_id == company_id)
    if anomaly_type:
        conditions.append(Anomaly.anomaly_type == anomaly_type)
    if severity:
        conditions.append(Anomaly.severity == severity)
    if start_date:
        conditions.append(Anomaly.date >= start_date)
    if end_date:
        conditions.append(Anomaly.date <= end_date)
    if days is not None:
        cutoff = date.today() - timedelta(days=days)
        conditions.append(Anomaly.date >= cutoff)
    if is_reviewed is not None:
        conditions.append(Anomaly.is_reviewed == is_reviewed)
    if is_explained is not None:
        conditions.append(Anomaly.is_explained_by_news == is_explained)

    if conditions:
        query = query.where(and_(*conditions))

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    query = query.offset(pagination.offset).limit(pagination.limit)
    result = await db.execute(query)
    anomalies = result.scalars().all()

    items = [
        AnomalyListResponse(
            id=a.id,
            company_id=a.company_id,
            company_ticker=a.company.ticker if a.company else "",
            company_name_en=a.company.name_en if a.company else "",
            company_name_fr=a.company.name_fr if a.company else "",
            company_name_ar=a.company.name_ar if a.company else "",
            date=a.date,
            anomaly_type=a.anomaly_type,
            severity=a.severity,
            z_score=a.z_score,
            description_en=a.description_en,
            description_fr=a.description_fr,
            description_ar=a.description_ar,
            is_explained_by_news=a.is_explained_by_news,
            is_reviewed=a.is_reviewed,
            created_at=a.created_at,
        )
        for a in anomalies
    ]

    total_pages = (total + pagination.page_size - 1) // pagination.page_size

    return {
        "data": items,
        "meta": {
            "page": pagination.page,
            "per_page": pagination.page_size,
            "total_pages": total_pages,
            "total": total,
        },
    }


@router.get("/stats", response_model=AnomalyStatsResponse)
async def get_anomaly_stats(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    """Get anomaly statistics."""
    from datetime import timedelta

    cutoff_date = date.today() - timedelta(days=days)

    total_query = select(func.count(Anomaly.id)).where(Anomaly.date >= cutoff_date)
    total = await db.scalar(total_query) or 0

    type_query = (
        select(Anomaly.anomaly_type, func.count(Anomaly.id))
        .where(Anomaly.date >= cutoff_date)
        .group_by(Anomaly.anomaly_type)
    )
    type_result = await db.execute(type_query)
    by_type = {str(k): v for k, v in type_result.all()}

    severity_query = (
        select(Anomaly.severity, func.count(Anomaly.id))
        .where(Anomaly.date >= cutoff_date)
        .group_by(Anomaly.severity)
    )
    severity_result = await db.execute(severity_query)
    by_severity = {str(k): v for k, v in severity_result.all()}
    company_query = (
        select(Company.ticker, func.count(Anomaly.id))
        .join(Anomaly, Company.id == Anomaly.company_id)
        .where(Anomaly.date >= cutoff_date)
        .group_by(Company.ticker)
        .order_by(func.count(Anomaly.id).desc())
        .limit(10)
    )
    company_result = await db.execute(company_query)
    by_company = {k: v for k, v in company_result.all()}

    recent_cutoff = date.today() - timedelta(days=7)
    recent_query = select(func.count(Anomaly.id)).where(Anomaly.date >= recent_cutoff)
    recent_count = await db.scalar(recent_query) or 0

    unexplained_query = select(func.count(Anomaly.id)).where(
        and_(Anomaly.date >= cutoff_date, Anomaly.is_explained_by_news == False)
    )
    unexplained_count = await db.scalar(unexplained_query) or 0

    return AnomalyStatsResponse(
        total_anomalies=total,
        by_type=by_type,
        by_severity=by_severity,
        by_company=by_company,
        recent_count=recent_count,
        unexplained_count=unexplained_count,
    )


@router.get("/latest", response_model=list[AnomalyListResponse])
async def get_latest_anomalies(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get latest anomalies across all companies."""
    query = (
        select(Anomaly)
        .options(selectinload(Anomaly.company))
        .order_by(desc(Anomaly.date), desc(Anomaly.created_at))
        .limit(limit)
    )
    result = await db.execute(query)
    anomalies = result.scalars().all()

    return [
        AnomalyListResponse(
            id=a.id,
            company_id=a.company_id,
            company_ticker=a.company.ticker if a.company else "",
            company_name_en=a.company.name_en if a.company else "",
            company_name_fr=a.company.name_fr if a.company else "",
            company_name_ar=a.company.name_ar if a.company else "",
            date=a.date,
            anomaly_type=a.anomaly_type,
            severity=a.severity,
            z_score=a.z_score,
            description_en=a.description_en,
            description_fr=a.description_fr,
            description_ar=a.description_ar,
            is_explained_by_news=a.is_explained_by_news,
            is_reviewed=a.is_reviewed,
            created_at=a.created_at,
        )
        for a in anomalies
    ]


@router.get("/company/{ticker}", response_model=PaginatedResponse[AnomalyListResponse])
async def get_company_anomalies(
    ticker: str,
    pagination: PaginationParams = Depends(),
    anomaly_type: Optional[AnomalyTypeSchema] = Query(None),
    severity: Optional[Severity] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get anomalies for a specific company."""
    company_query = select(Company).where(Company.ticker == ticker.upper())
    company_result = await db.execute(company_query)
    company = company_result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    query = (
        select(Anomaly)
        .options(selectinload(Anomaly.company))
        .where(Anomaly.company_id == company.id)
        .order_by(desc(Anomaly.date), desc(Anomaly.created_at))
    )

    conditions = []
    if anomaly_type:
        conditions.append(Anomaly.anomaly_type == anomaly_type)
    if severity:
        conditions.append(Anomaly.severity == severity)
    if start_date:
        conditions.append(Anomaly.date >= start_date)
    if end_date:
        conditions.append(Anomaly.date <= end_date)

    if conditions:
        query = query.where(and_(*conditions))

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    query = query.offset(pagination.offset).limit(pagination.limit)
    result = await db.execute(query)
    anomalies = result.scalars().all()

    items = [
        AnomalyListResponse(
            id=a.id,
            company_id=a.company_id,
            company_ticker=a.company.ticker if a.company else "",
            company_name_en=a.company.name_en if a.company else "",
            company_name_fr=a.company.name_fr if a.company else "",
            company_name_ar=a.company.name_ar if a.company else "",
            date=a.date,
            anomaly_type=a.anomaly_type,
            severity=a.severity,
            z_score=a.z_score,
            description_en=a.description_en,
            description_fr=a.description_fr,
            description_ar=a.description_ar,
            is_explained_by_news=a.is_explained_by_news,
            is_reviewed=a.is_reviewed,
            created_at=a.created_at,
        )
        for a in anomalies
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


@router.get("/types", response_model=list[AnomalyTypeSchema])
async def get_anomaly_types():
    """Get list of all anomaly types."""
    return list(AnomalyTypeSchema)
