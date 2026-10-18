"""FX rate models."""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from sqlalchemy import (
    String, Integer, DateTime, Date, Numeric, Boolean, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


class FXPair(Base):
    """Currency pair configuration."""
    __tablename__ = "fx_pairs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    base_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    quote_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    
    # Display
    name_en: Mapped[str] = mapped_column(String(50), nullable=False)
    name_fr: Mapped[str] = mapped_column(String(50), nullable=False)
    name_ar: Mapped[str] = mapped_column(String(50), nullable=False)
    symbol: Mapped[str] = mapped_column(String(10), nullable=False)  # e.g., "EUR/TND"
    
    # Configuration
    decimals: Mapped[int] = mapped_column(Integer, default=4, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_inverted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Source priority (lower = higher priority)
    source_priority: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # Relationships
    rates: Mapped[list["FXRate"]] = relationship(back_populates="pair", lazy="dynamic")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("base_currency", "quote_currency", name="uq_fx_pairs_currencies"),
        Index("ix_fx_pairs_active_order", "is_active", "display_order"),
    )
    
    @property
    def pair_code(self) -> str:
        return f"{self.base_currency}{self.quote_currency}"
    
    def __repr__(self) -> str:
        return f"<FXPair({self.symbol})>"


class FXRate(Base):
    """Foreign exchange rates - TimescaleDB hypertable."""
    __tablename__ = "fx_rates"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pair_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("fx_pairs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    
    # Rates
    rate: Mapped[Decimal] = mapped_column(Numeric(12, 6), nullable=False)
    bid: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 6), nullable=True)
    ask: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 6), nullable=True)
    high: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 6), nullable=True)
    low: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 6), nullable=True)
    open_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 6), nullable=True)
    close_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 6), nullable=True)
    
    # Change
    change_abs: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 6), nullable=True)
    change_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4), nullable=True)
    
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
    pair: Mapped["FXPair"] = relationship(back_populates="rates", lazy="selectin")
    
    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint("pair_id", "date", "source", name="uq_fx_rates_pair_date_source"),
        Index("ix_fx_rates_pair_date_desc", "pair_id", "date"),
        Index("ix_fx_rates_date_source", "date", "source"),
    )
    
    def __repr__(self) -> str:
        return f"<FXRate(pair_id={self.pair_id}, date={self.date}, rate={self.rate}, source={self.source})>"