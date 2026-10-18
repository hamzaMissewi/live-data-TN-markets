"""Anomaly detection models."""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from enum import Enum as PyEnum
from sqlalchemy import (
    String, Text, Integer, DateTime, Date, Numeric, Boolean, ForeignKey, Index, Enum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


class AnomalyType(str, PyEnum):
    """Types of anomalies detected."""
    VOLUME_SPIKE = "volume_spike"
    PRICE_GAP = "price_gap"
    VOLATILITY_SPIKE = "volatility_spike"
    RSI_EXTREME = "rsi_extreme"
    MOVING_AVERAGE_CROSS = "ma_cross"
    BOLLINGER_BREAKOUT = "bollinger_breakout"
    UNUSUAL_TURNOVER = "unusual_turnover"
    PRICE_VOLUME_DIVERGENCE = "price_volume_divergence"
    GAP_UP = "gap_up"
    GAP_DOWN = "gap_down"


class Anomaly(Base):
    """Detected market anomalies."""
    __tablename__ = "anomalies"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    anomaly_type: Mapped[AnomalyType] = mapped_column(
        Enum(AnomalyType, native_enum=False), nullable=False, index=True
    )
    
    # Detection metrics
    z_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4), nullable=True)
    value: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 4), nullable=True)
    expected_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 4), nullable=True)
    threshold: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4), nullable=True)
    
    # Context
    description_en: Mapped[str] = mapped_column(Text, nullable=False)
    description_fr: Mapped[str] = mapped_column(Text, nullable=False)
    description_ar: Mapped[str] = mapped_column(Text, nullable=False)
    
    # News correlation
    is_explained_by_news: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    related_news_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("news_items.id", ondelete="SET NULL"), nullable=True
    )
    news_explanation_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    news_explanation_fr: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    news_explanation_ar: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Severity
    severity: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)  # low, medium, high, critical
    confidence: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 3), nullable=True)  # 0-1
    
    # Status
    is_reviewed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_false_positive: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reviewed_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # Relationships
    company: Mapped["Company"] = relationship(back_populates="anomalies", lazy="selectin")
    related_news: Mapped[Optional["NewsItem"]] = relationship(lazy="selectin")
    
    # Indexes
    __table_args__ = (
        Index("ix_anomalies_company_date_desc", "company_id", "date"),
        Index("ix_anomalies_type_date", "anomaly_type", "date"),
        Index("ix_anomalies_severity_date", "severity", "date"),
        Index("ix_anomalies_unreviewed", "is_reviewed", "date"),
    )
    
    def __repr__(self) -> str:
        return f"<Anomaly(company_id={self.company_id}, type={self.anomaly_type}, date={self.date}, severity={self.severity})>"