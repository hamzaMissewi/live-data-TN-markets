"""News models."""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String, Text, Integer, DateTime, Boolean, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


class NewsSource(Base):
    """News source configuration."""
    __tablename__ = "news_sources"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    name_fr: Mapped[str] = mapped_column(String(100), nullable=False)
    name_ar: Mapped[str] = mapped_column(String(100), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    rss_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="fr", nullable=False)
    country: Mapped[str] = mapped_column(String(2), default="TN", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    credibility_score: Mapped[int] = mapped_column(Integer, default=50, nullable=False)  # 0-100
    
    # Scraping config
    scrape_selector: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    date_format: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    last_scraped_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    news_items: Mapped[list["NewsItem"]] = relationship(back_populates="source", lazy="dynamic")
    
    def __repr__(self) -> str:
        return f"<NewsSource(name='{self.name}')>"


class NewsItem(Base):
    """News articles related to market."""
    __tablename__ = "news_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("news_sources.id", ondelete="CASCADE"), nullable=False, index=True
    )
    external_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, index=True)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    url_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    
    # Content
    title_en: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    title_fr: Mapped[str] = mapped_column(String(500), nullable=False)
    title_ar: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    summary_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    summary_fr: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    summary_ar: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_fr: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_ar: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Classification
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    sentiment: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # positive, negative, neutral
    sentiment_score: Mapped[Optional[float]] = mapped_column(nullable=True)
    
    # Related entities
    mentioned_tickers: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    mentioned_sectors: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    
    # Dates
    published_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    scraped_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Status
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # Relationships
    source: Mapped["NewsSource"] = relationship(back_populates="news_items", lazy="selectin")
    
    # Indexes
    __table_args__ = (
        Index("ix_news_items_published_desc", "published_at"),
        Index("ix_news_items_category_published", "category", "published_at"),
        Index("ix_news_items_sentiment_published", "sentiment", "published_at"),
    )
    
    def __repr__(self) -> str:
        return f"<NewsItem(title_fr='{self.title_fr[:50]}...', published={self.published_at})>"