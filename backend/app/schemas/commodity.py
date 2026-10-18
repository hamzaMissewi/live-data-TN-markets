"""Commodity schemas."""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class CommodityBase(BaseModel):
    code: str = Field(..., max_length=20)
    name_en: str = Field(..., max_length=100)
    name_fr: str = Field(..., max_length=100)
    name_ar: str = Field(..., max_length=100)
    unit_en: str = Field(..., max_length=20)
    unit_fr: str = Field(..., max_length=20)
    unit_ar: str = Field(..., max_length=20)
    local_unit_en: Optional[str] = Field(None, max_length=20)
    local_unit_fr: Optional[str] = Field(None, max_length=20)
    local_unit_ar: Optional[str] = Field(None, max_length=20)
    local_unit_conversion: Optional[Decimal] = Field(None, gt=0)
    category: str = Field(..., max_length=50)
    decimals: int = Field(2, ge=0, le=8)
    is_active: bool = True
    display_order: int = 0
    primary_source: Optional[str] = Field(None, max_length=100)
    source_url: Optional[str] = Field(None, max_length=500)


class CommodityResponse(CommodityBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CommodityPriceResponse(BaseModel):
    id: int
    commodity_id: int
    date: date
    timestamp: Optional[datetime] = None
    price: Decimal
    local_price: Optional[Decimal] = None
    change_abs: Optional[Decimal] = None
    change_pct: Optional[Decimal] = None
    high: Optional[Decimal] = None
    low: Optional[Decimal] = None
    open_price: Optional[Decimal] = None
    close_price: Optional[Decimal] = None
    source: str
    source_timestamp: Optional[datetime] = None
    is_official: bool
    is_validated: bool
    created_at: datetime
    updated_at: datetime
    commodity: Optional[CommodityResponse] = None
    
    model_config = ConfigDict(from_attributes=True)


class CommodityHistoryResponse(BaseModel):
    commodity_id: int
    code: str
    name_en: str
    name_fr: str
    name_ar: str
    unit_en: str
    unit_fr: str
    unit_ar: str
    local_unit_en: Optional[str] = None
    local_unit_fr: Optional[str] = None
    local_unit_ar: Optional[str] = None
    data: List[CommodityPriceResponse]
    latest_price: Optional[CommodityPriceResponse] = None
    period: str
    total_records: int
    
    model_config = ConfigDict(from_attributes=True)


class CommodityChartDataPoint(BaseModel):
    time: int
    value: float
    local_value: Optional[float] = None


class CommodityChartDataResponse(BaseModel):
    commodity_code: str
    name: str
    unit: str
    local_unit: Optional[str] = None
    data: List[CommodityChartDataPoint]
    period: str
    latest_price: float
    latest_change_pct: Optional[float] = None