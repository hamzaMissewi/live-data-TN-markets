"""News scraping Celery tasks."""
import asyncio
import hashlib
from datetime import datetime
import httpx
from bs4 import BeautifulSoup
from sqlalchemy import select, insert, and_
from celery import shared_task
from app.db.session import async_session_maker
from app.models.news import NewsItem, NewsSource
from app.models.company import Company
from app.core.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


@shared_task
def scrape_news():
    """Scrape news from all active sources."""
    asyncio.run(_scrape_news())


async def _scrape_news():
    """Async implementation of news scraping."""
    logger.info("Starting news scraping...")
    
    async with async_session_maker() as db:
        result = await db.execute(select(NewsSource).where(NewsSource.is_active == True))
        sources = result.scalars().all()
        
        if not sources:
            logger.warning("No active news sources found")
            return
        
        async with httpx.AsyncClient(
            timeout=settings.SCRAPER_TIMEOUT,
            headers={"User-Agent": settings.SCRAPER_USER_AGENT},
        ) as client:
            news_to_insert = []
            
            for source in sources:
                try:
                    items = await scrape_single_source(client, source, db)
                    news_to_insert.extend(items)
                except Exception as e:
                    logger.error(f"Failed to scrape {source.name}: {e}")
            
            if news_to_insert:
                existing_hashes = set()
                result = await db.execute(select(NewsItem.url_hash))
                existing_hashes = {row[0] for row in result.all()}
                
                new_news = [
                    item for item in news_to_insert
                    if item["url_hash"] not in existing_hashes
                ]
                
                if new_news:
                    await db.execute(insert(NewsItem), new_news)
                    await db.commit()
                    logger.info(f"Inserted {len(new_news)} new news items")
            
            for source in sources:
                source.last_scraped_at = datetime.utcnow()
            await db.commit()
            
            logger.info("News scraping completed successfully")


async def scrape_single_source(client, source: NewsSource, db) -> list:
    """Scrape news from a single source."""
    items = []
    
    if source.rss_url:
        try:
            import xml.etree.ElementTree as ET
            response = await client.get(source.rss_url)
            response.raise_for_status()
            
            root = ET.fromstring(response.text)
            
            for item_elem in root.iter("item"):
                title_elem = item_elem.find("title")
                link_elem = item_elem.find("link")
                pub_date_elem = item_elem.find("pubDate")
                desc_elem = item_elem.find("description")
                
                if not (title_elem is not None and link_elem is not None):
                    continue
                
                title = title_elem.text or ""
                url = link_elem.text or ""
                
                from dateutil import parser as date_parser
                try:
                    pub_date = date_parser.parse(pub_date_elem.text) if pub_date_elem is not None else datetime.utcnow()
                except Exception:
                    pub_date = datetime.utcnow()
                
                summary = ""
                if desc_elem is not None:
                    soup = BeautifulSoup(desc_elem.text, "html.parser")
                    summary = soup.get_text()[:500]
                
                url_hash = hashlib.md5(url.encode()).hexdigest()
                
                mentioned_tickers = []
                company_result = await db.execute(select(Company.ticker))
                all_tickers = [row[0] for row in company_result.all()]
                for ticker in all_tickers:
                    if ticker in title or (summary and ticker in summary):
                        mentioned_tickers.append(ticker)
                
                news_item = {
                    "source_id": source.id,
                    "url": url,
                    "url_hash": url_hash,
                    "title_fr": title,
                    "summary_fr": summary,
                    "category": source.country,
                    "sentiment": "neutral",
                    "sentiment_score": 0.0,
                    "mentioned_tickers": ",".join(mentioned_tickers) if mentioned_tickers else None,
                    "published_at": pub_date,
                    "scraped_at": datetime.utcnow(),
                    "is_processed": False,
                    "is_published": True,
                }
                
                items.append(news_item)
        except Exception as e:
            logger.error(f"RSS scraping failed for {source.name}: {e}")
    
    return items
@shared_task
def correlate_news_with_anomalies():
    """Correlate news with anomalies for explanation flags."""
    asyncio.run(_correlate_news_with_anomalies())


async def _correlate_news_with_anomalies():
    """Correlate news with anomalies."""
    from app.models.anomaly import Anomaly
    from datetime import timedelta
    
    logger.info("Correlating news with anomalies...")
    
    async with async_session_maker() as db:
        today = datetime.utcnow().date()
        
        news_query = (
            select(NewsItem)
            .where(
                and_(
                    NewsItem.is_published == True,
                    NewsItem.mentioned_tickers.isnot(None),
                )
            )
            .order_by(NewsItem.published_at.desc())
            .limit(100)
        )
        news_result = await db.execute(news_query)
        news_items = news_result.scalars().all()
        
        for news in news_items:
            if news.mentioned_tickers:
                tickers = news.mentioned_tickers.split(",")
                for ticker in tickers:
                    ticker = ticker.strip()
                    
                    company_query = select(Company).where(Company.ticker == ticker.upper())
                    company_result = await db.execute(company_query)
                    company = company_result.scalar_one_or_none()
                    
                    if not company:
                        continue
                    
                    anomaly_query = (
                        select(Anomaly)
                        .where(
                            and_(
                                Anomaly.company_id == company.id,
                                Anomaly.date == today,
                                Anomaly.is_explained_by_news == False,
                            )
                        )
                    )
                    anomaly_result = await db.execute(anomaly_query)
                    anomalies = anomaly_result.scalars().all()
                    
                    for anomaly in anomalies:
                        anomaly.is_explained_by_news = True
                        anomaly.related_news_id = news.id
                        anomaly.news_explanation_en = f"Related news: {news.title_fr}"
                        anomaly.news_explanation_fr = f"Actualites connexes : {news.title_fr}"
                        anomaly.news_explanation_ar = f"أخبار ذات صلة: {news.title_fr}"
        
        await db.commit()
        logger.info(f"Correlated {len(news_items)} news items with anomalies")