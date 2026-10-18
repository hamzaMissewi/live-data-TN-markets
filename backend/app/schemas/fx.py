"""FX rate schemas."""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class FXPairBase(BaseModel):
    base_currency: str = Field(..., min_length=3, max_length=3)
    quote_currency: str = Field(..., min_length=3, max_length=3)
    name_en: str = Field(..., max_length=50)
    name_fr: str = Field(..., max_length=50)
    name_ar: str = Field(..., max_length=50)
    symbol: str = Field(..., max_length=10)
    decimals: int = Field(4, ge=0, le=8)
    is_active: bool = True
    is_inverted: bool = False
    display_order: int = 0
    source_priority: int = 1


class FXPairResponse(FXPairBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class FXRateBase(BaseModel):
    pair_id: int
    date: date
    timestamp: Optional[datetime] = None
    rate: Decimal = Field(..., gt=0)
    bid: Optional[Decimal] = Field(None, gt=0)
    ask: Optional[Decimal] = Field(None, gt=0)
    high: Optional[Decimal] = Field(None, gt=0)
    low: Optional[Decimal] = Field(None, gt=0)
    open_rate: Optional[Decimal] = Field(None, gt=0)
    close_rate: Optional[Decimal] = Field(None, gt=0)
    change_abs: Optional[Decimal] = None
    change_pct: Optional[Decimal] = None
    source: str
    source_timestamp: Optional[datetime] = None
    is_official: bool = False
    is_validated: bool = False


class FXRateResponse(FXRateBase):
    id: int
    created_at: datetime
    updated_at: datetime
    pair: Optional[FXPairResponse] = None
    
    model_config = ConfigDict(from_attributes=True)


class FXHistoryResponse(BaseModel):
    pair_id: int
    base_currency: str
    quote_currency: str
    symbol: str
    name_en: str
    name_fr: str
    name_ar: str
    data: List[FXRateResponse]
    latest_rate: Optional[FXRateResponse] = None
    period: str
    total_records: int
    
    model_config = ConfigDict(from_attributes=True)


class CurrencyConverterRequest(BaseModel):
    from_currency: str = Field(..., min_length=3, max_length=3)
    to_currency: str = Field(..., min_length=3, max_length=3)
    amount: Decimal = Field(..., gt=0)
    date: Optional[date] = None  # If not provided, use latest rate


class CurrencyConverterResponse(BaseModel):
    from_currency: str
    to_currency: str
    amount: Decimal
    rate: Decimal
    converted_amount: Decimal
    rate_date: date
    rate_source: str
    inverse_rate: Decimal
    
    model_config = ConfigDict(from_attributes=True)


class FXChartDataPoint(BaseModel):
    time: int
    value: float


class FXChartDataResponse(BaseModel):
    pair_symbol: str
    base_currency: str
    quote_currency: str
    data: List[FXChartDataPoint]
    period: str
    latest_rate: float
    latest_change_pct: Optional[float] = None