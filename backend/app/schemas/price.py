"""Price schemas."""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class PriceDailyBase(BaseModel):
    company_id: int
    date: date
    open_price: Decimal = Field(..., ge=0)
    high_price: Decimal = Field(..., ge=0)
    low_price: Decimal = Field(..., ge=0)
    close_price: Decimal = Field(..., ge=0)
    adjusted_close: Optional[Decimal] = Field(None, ge=0)
    volume: int = Field(..., ge=0)
    turnover: Optional[Decimal] = Field(None, ge=0)


class TechnicalIndicators(BaseModel):
    sma_20: Optional[Decimal] = None
    sma_50: Optional[Decimal] = None
    sma_200: Optional[Decimal] = None
    ema_12: Optional[Decimal] = None
    ema_26: Optional[Decimal] = None
    rsi_14: Optional[Decimal] = None
    macd: Optional[Decimal] = None
    macd_signal: Optional[Decimal] = None
    macd_histogram: Optional[Decimal] = None
    bollinger_upper: Optional[Decimal] = None
    bollinger_middle: Optional[Decimal] = None
    bollinger_lower: Optional[Decimal] = None


class PriceDailyResponse(PriceDailyBase):
    id: int
    daily_return: Optional[Decimal] = None
    daily_return_pct: Optional[Decimal] = None
    technical: Optional[TechnicalIndicators] = None
    source: str
    is_validated: bool
    validation_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PriceIntradayResponse(BaseModel):
    id: int
    company_id: int
    timestamp: datetime
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    volume: int
    source: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PriceHistoryResponse(BaseModel):
    company_id: int
    ticker: str
    name_en: str
    name_fr: str
    name_ar: str
    data: List[PriceDailyResponse]
    latest_price: Optional[PriceDailyResponse] = None
    period: str  # e.g., "1m", "3m", "6m", "1y", "5y", "all"
    total_records: int
    
    model_config = ConfigDict(from_attributes=True)


class ChartDataPoint(BaseModel):
    """Lightweight chart data point for TradingView Lightweight Charts."""
    time: int  # Unix timestamp
    open: float
    high: float
    low: float
    close: float
    volume: Optional[int] = None


class ChartDataResponse(BaseModel):
    """Response format for TradingView Lightweight Charts."""
    ticker: str
    name: str
    currency: str = "TND"
    data: List[ChartDataPoint]
    period: str