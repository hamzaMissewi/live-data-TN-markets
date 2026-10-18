"""Company and Sector models."""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import (
    String, Text, Integer, DateTime, Date, Numeric, Boolean, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


class Sector(Base):
    """Market sector classification."""
    __tablename__ = "sectors"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    name_fr: Mapped[str] = mapped_column(String(100), nullable=False)
    name_ar: Mapped[str] = mapped_column(String(100), nullable=False)
    description_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_fr: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_ar: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # Relationships
    companies: Mapped[list["Company"]] = relationship(back_populates="sector", lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<Sector(code='{self.code}', name_en='{self.name_en}')>"


class Company(Base):
    """Listed company on BVMT."""
    __tablename__ = "companies"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    isin: Mapped[Optional[str]] = mapped_column(String(12), unique=True, nullable=True, index=True)
    name_en: Mapped[str] = mapped_column(String(200), nullable=False)
    name_fr: Mapped[str] = mapped_column(String(200), nullable=False)
    name_ar: Mapped[str] = mapped_column(String(200), nullable=False)
    short_name_en: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    short_name_fr: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    short_name_ar: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Sector
    sector_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("sectors.id", ondelete="SET NULL"), nullable=True, index=True
    )
    
    # Company details
    description_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_fr: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_ar: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    founded_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    employees_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Market data
    market_cap: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2), nullable=True)
    shares_outstanding: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    free_float_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    
    # Dividends
    last_dividend: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    last_dividend_date: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)
    dividend_yield: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_suspended: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    listing_date: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)
    
    # SEO
    slug_en: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    slug_fr: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    slug_ar: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    meta_title_en: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    meta_title_fr: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    meta_title_ar: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    meta_description_en: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    meta_description_fr: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    meta_description_ar: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    last_price_update: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    sector: Mapped[Optional["Sector"]] = relationship(back_populates="companies", lazy="selectin")
    prices_daily: Mapped[list["PriceDaily"]] = relationship(back_populates="company", lazy="dynamic")
    anomalies: Mapped[list["Anomaly"]] = relationship(back_populates="company", lazy="dynamic")
    
    # Indexes
    __table_args__ = (
        Index("ix_companies_sector_active", "sector_id", "is_active"),
        Index("ix_companies_ticker_active", "ticker", "is_active"),
    )
    
    def __repr__(self) -> str:
        return f"<Company(ticker='{self.ticker}', name_en='{self.name_en}')>"