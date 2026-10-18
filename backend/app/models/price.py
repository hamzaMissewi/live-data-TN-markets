"""Price models for daily and intraday data."""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from sqlalchemy import (
    String, Integer, DateTime, Date, Numeric, ForeignKey, Index, UniqueConstraint, text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


class PriceDaily(Base):
    """Daily OHLCV price data for stocks - TimescaleDB hypertable."""
    __tablename__ = "prices_daily"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    
    # OHLCV
    open_price: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    high_price: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    low_price: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    close_price: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    adjusted_close: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    volume: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    turnover: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2), nullable=True)
    
    # Technical indicators (precomputed)
    sma_20: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    sma_50: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    sma_200: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    ema_12: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    ema_26: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    rsi_14: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    macd: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    macd_signal: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    macd_histogram: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    bollinger_upper: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    bollinger_middle: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    bollinger_lower: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    
    # Returns
    daily_return: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4), nullable=True)
    daily_return_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4), nullable=True)
    
    # Data quality
    source: Mapped[str] = mapped_column(String(50), default="bvmt", nullable=False)
    is_validated: Mapped[bool] = mapped_column(default=False, nullable=False)
    validation_notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # Relationships
    company: Mapped["Company"] = relationship(back_populates="prices_daily", lazy="selectin")
    
    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint("company_id", "date", name="uq_prices_daily_company_date"),
        Index("ix_prices_daily_company_date_desc", "company_id", "date"),
        Index("ix_prices_daily_date_volume", "date", "volume"),
    )
    
    def __repr__(self) -> str:
        return f"<PriceDaily(company_id={self.company_id}, date={self.date}, close={self.close_price})>"


class PriceIntraday(Base):
    """Intraday price data (optional, for higher frequency)."""
    __tablename__ = "prices_intraday"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    
    # OHLC
    open_price: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    high_price: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    low_price: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    close_price: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    volume: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Data quality
    source: Mapped[str] = mapped_column(String(50), default="bvmt", nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    company: Mapped["Company"] = relationship(lazy="selectin")
    
    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint("company_id", "timestamp", name="uq_prices_intraday_company_timestamp"),
        Index("ix_prices_intraday_company_timestamp_desc", "company_id", "timestamp"),
    )
    
    def __repr__(self) -> str:
        return f"<PriceIntraday(company_id={self.company_id}, ts={self.timestamp}, close={self.close_price})>"