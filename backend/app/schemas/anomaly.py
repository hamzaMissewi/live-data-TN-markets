"""Anomaly schemas."""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class AnomalyType(str, Enum):
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


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnomalyBase(BaseModel):
    company_id: int
    date: date
    anomaly_type: AnomalyType
    z_score: Optional[Decimal] = None
    value: Optional[Decimal] = None
    expected_value: Optional[Decimal] = None
    threshold: Optional[Decimal] = None
    description_en: str
    description_fr: str
    description_ar: str
    is_explained_by_news: bool = False
    related_news_id: Optional[int] = None
    news_explanation_en: Optional[str] = None
    news_explanation_fr: Optional[str] = None
    news_explanation_ar: Optional[str] = None
    severity: Severity = Severity.MEDIUM
    confidence: Optional[Decimal] = Field(None, ge=0, le=1)


class AnomalyResponse(AnomalyBase):
    id: int
    is_reviewed: bool
    is_false_positive: bool
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    company_ticker: Optional[str] = None
    company_name_en: Optional[str] = None
    company_name_fr: Optional[str] = None
    company_name_ar: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class AnomalyListResponse(BaseModel):
    id: int
    company_id: int
    company_ticker: str
    company_name_en: str
    company_name_fr: str
    company_name_ar: str
    date: date
    anomaly_type: AnomalyType
    severity: Severity
    z_score: Optional[Decimal] = None
    description_en: str
    description_fr: str
    description_ar: str
    is_explained_by_news: bool
    is_reviewed: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AnomalyStatsResponse(BaseModel):
    total_anomalies: int
    by_type: dict[str, int]
    by_severity: dict[str, int]
    by_company: dict[str, int]
    recent_count: int  # last 7 days
    unexplained_count: int