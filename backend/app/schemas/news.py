"""News schemas."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class NewsSourceBase(BaseModel):
    name: str = Field(..., max_length=100)
    name_en: str = Field(..., max_length=100)
    name_fr: str = Field(..., max_length=100)
    name_ar: str = Field(..., max_length=100)
    url: str = Field(..., max_length=500)
    logo_url: Optional[str] = Field(None, max_length=500)
    rss_url: Optional[str] = Field(None, max_length=500)
    language: str = Field("fr", max_length=10)
    country: str = Field("TN", max_length=2)
    is_active: bool = True
    credibility_score: int = Field(50, ge=0, le=100)
    scrape_selector: Optional[str] = Field(None, max_length=200)
    date_format: Optional[str] = Field(None, max_length=50)


class NewsSourceResponse(NewsSourceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    last_scraped_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class NewsItemBase(BaseModel):
    source_id: int
    external_id: Optional[str] = Field(None, max_length=200)
    url: str = Field(..., max_length=1000)
    title_en: Optional[str] = Field(None, max_length=500)
    title_fr: str = Field(..., max_length=500)
    title_ar: Optional[str] = Field(None, max_length=500)
    summary_en: Optional[str] = None
    summary_fr: Optional[str] = None
    summary_ar: Optional[str] = None
    content_en: Optional[str] = None
    content_fr: Optional[str] = None
    content_ar: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    tags: Optional[str] = None  # JSON array
    sentiment: Optional[str] = Field(None, max_length=20)
    sentiment_score: Optional[float] = None
    mentioned_tickers: Optional[str] = None  # JSON array
    mentioned_sectors: Optional[str] = None  # JSON array
    published_at: datetime


class NewsItemResponse(NewsItemBase):
    id: int
    url_hash: str
    is_processed: bool
    is_published: bool
    scraped_at: datetime
    created_at: datetime
    updated_at: datetime
    source: Optional[NewsSourceResponse] = None
    
    model_config = ConfigDict(from_attributes=True)


class NewsListResponse(BaseModel):
    id: int
    source_id: int
    source_name: str
    source: str
    url: str
    title_en: Optional[str] = None
    title_fr: str
    title_ar: Optional[str] = None
    summary_en: Optional[str] = None
    summary_fr: Optional[str] = None
    summary_ar: Optional[str] = None
    category: Optional[str] = None
    sentiment: Optional[str] = None
    published_at: datetime
    mentioned_tickers: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class NewsWithAnomalyResponse(NewsItemResponse):
    related_anomalies_count: int = 0