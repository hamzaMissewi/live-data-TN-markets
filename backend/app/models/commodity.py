"""Commodity models for gold, fuel, etc."""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from sqlalchemy import (
    String, Text, Integer, DateTime, Date, Numeric, Boolean, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


class Commodity(Base):
    """Commodity configuration (gold, fuel, etc.)."""
    __tablename__ = "commodities"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    name_fr: Mapped[str] = mapped_column(String(100), nullable=False)
    name_ar: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Units
    unit_en: Mapped[str] = mapped_column(String(20), nullable=False)  # e.g., "ounce", "liter"
    unit_fr: Mapped[str] = mapped_column(String(20), nullable=False)
    unit_ar: Mapped[str] = mapped_column(String(20), nullable=False)
    local_unit_en: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # e.g., "gram"
    local_unit_fr: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    local_unit_ar: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    local_unit_conversion: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 6), nullable=True)
    
    # Category
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # precious_metal, energy, etc.
    
    # Configuration
    decimals: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Source
    primary_source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # Relationships
    prices: Mapped[list["CommodityPrice"]] = relationship(back_populates="commodity", lazy="dynamic")
    
    def __repr__(self) -> str:
        return f"<Commodity(code='{self.code}', name_en='{self.name_en}')>"


class CommodityPrice(Base):
    """Commodity price history - TimescaleDB hypertable."""
    __tablename__ = "commodity_prices"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    commodity_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("commodities.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Prices
    price: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    local_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    change_abs: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    change_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4), nullable=True)
    high: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    low: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    open_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    close_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    
    # Source
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    source_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Data quality
    is_official: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_validated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # Relationships
    commodity: Mapped["Commodity"] = relationship(back_populates="prices", lazy="selectin")
    
    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint("commodity_id", "date", "source", name="uq_commodity_prices_commodity_date_source"),
        Index("ix_commodity_prices_commodity_date_desc", "commodity_id", "date"),
        Index("ix_commodity_prices_date_category", "date", "commodity_id"),
    )
    
    def __repr__(self) -> str:
        return f"<CommodityPrice(commodity_id={self.commodity_id}, date={self.date}, price={self.price})>"