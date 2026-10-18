"""Company and Sector schemas."""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class SectorBase(BaseModel):
    code: str = Field(..., max_length=20)
    name_en: str = Field(..., max_length=100)
    name_fr: str = Field(..., max_length=100)
    name_ar: str = Field(..., max_length=100)
    description_en: Optional[str] = None
    description_fr: Optional[str] = None
    description_ar: Optional[str] = None
    is_active: bool = True


class SectorResponse(SectorBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CompanyBase(BaseModel):
    ticker: str = Field(..., max_length=20)
    isin: Optional[str] = Field(None, max_length=12)
    name_en: str = Field(..., max_length=200)
    name_fr: str = Field(..., max_length=200)
    name_ar: str = Field(..., max_length=200)
    short_name_en: Optional[str] = Field(None, max_length=50)
    short_name_fr: Optional[str] = Field(None, max_length=50)
    short_name_ar: Optional[str] = Field(None, max_length=50)
    sector_id: Optional[int] = None
    description_en: Optional[str] = None
    description_fr: Optional[str] = None
    description_ar: Optional[str] = None
    website: Optional[str] = Field(None, max_length=500)
    founded_year: Optional[int] = None
    employees_count: Optional[int] = None
    slug_en: str = Field(..., max_length=200)
    slug_fr: str = Field(..., max_length=200)
    slug_ar: str = Field(..., max_length=200)


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    ticker: Optional[str] = Field(None, max_length=20)
    isin: Optional[str] = Field(None, max_length=12)
    name_en: Optional[str] = Field(None, max_length=200)
    name_fr: Optional[str] = Field(None, max_length=200)
    name_ar: Optional[str] = Field(None, max_length=200)
    short_name_en: Optional[str] = Field(None, max_length=50)
    short_name_fr: Optional[str] = Field(None, max_length=50)
    short_name_ar: Optional[str] = Field(None, max_length=50)
    sector_id: Optional[int] = None
    description_en: Optional[str] = None
    description_fr: Optional[str] = None
    description_ar: Optional[str] = None
    website: Optional[str] = Field(None, max_length=500)
    founded_year: Optional[int] = None
    employees_count: Optional[int] = None
    market_cap: Optional[Decimal] = None
    shares_outstanding: Optional[int] = None
    free_float_pct: Optional[Decimal] = None
    last_dividend: Optional[Decimal] = None
    last_dividend_date: Optional[date] = None
    dividend_yield: Optional[Decimal] = None
    is_active: Optional[bool] = None
    is_suspended: Optional[bool] = None
    slug_en: Optional[str] = Field(None, max_length=200)
    slug_fr: Optional[str] = Field(None, max_length=200)
    slug_ar: Optional[str] = Field(None, max_length=200)
    meta_title_en: Optional[str] = Field(None, max_length=200)
    meta_title_fr: Optional[str] = Field(None, max_length=200)
    meta_title_ar: Optional[str] = Field(None, max_length=200)
    meta_description_en: Optional[str] = Field(None, max_length=300)
    meta_description_fr: Optional[str] = Field(None, max_length=300)
    meta_description_ar: Optional[str] = Field(None, max_length=300)


class CompanyResponse(CompanyBase):
    id: int
    market_cap: Optional[Decimal] = None
    shares_outstanding: Optional[int] = None
    free_float_pct: Optional[Decimal] = None
    last_dividend: Optional[Decimal] = None
    last_dividend_date: Optional[date] = None
    dividend_yield: Optional[Decimal] = None
    is_active: bool
    is_suspended: bool
    listing_date: Optional[date] = None
    meta_title_en: Optional[str] = None
    meta_title_fr: Optional[str] = None
    meta_title_ar: Optional[str] = None
    meta_description_en: Optional[str] = None
    meta_description_fr: Optional[str] = None
    meta_description_ar: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_price_update: Optional[datetime] = None
    sector: Optional[SectorResponse] = None
    
    model_config = ConfigDict(from_attributes=True)


class CompanyListResponse(BaseModel):
    id: int
    ticker: str
    name_en: str
    name_fr: str
    name_ar: str
    short_name_en: Optional[str] = None
    short_name_fr: Optional[str] = None
    short_name_ar: Optional[str] = None
    sector_id: Optional[int] = None
    sector_name_en: Optional[str] = None
    sector_name_fr: Optional[str] = None
    sector_name_ar: Optional[str] = None
    is_active: bool
    is_suspended: bool
    last_price: Optional[Decimal] = None
    last_price_date: Optional[date] = None
    daily_change_pct: Optional[Decimal] = None
    market_cap: Optional[Decimal] = None
    slug_en: str
    slug_fr: str
    slug_ar: str
    
    model_config = ConfigDict(from_attributes=True)