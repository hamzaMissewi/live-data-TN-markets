"""Data ingestion Celery tasks for BVMT, FX, and commodities."""
import asyncio
from datetime import date, datetime, timedelta
from decimal import Decimal
import httpx
import pandas as pd
from sqlalchemy import select, insert
from celery import shared_task
from app.db.session import async_session_maker
from app.models.company import Company, Sector
from app.models.price import PriceDaily
from app.models.fx import FXPair, FXRate
from app.models.commodity import Commodity, CommodityPrice
from app.core.config import settings
from app.services.technical_analysis import compute_technical_indicators
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


@shared_task
def ingest_daily_prices():
    """Ingest daily BVMT stock prices."""
    asyncio.run(_ingest_daily_prices())


async def _ingest_daily_prices():
    """Async implementation of daily price ingestion."""
    logger.info("Starting daily price ingestion...")
    
    async with async_session_maker() as db:
        result = await db.execute(select(Company).where(Company.is_active == True))
        companies = result.scalars().all()
        
        if not companies:
            logger.warning("No active companies found")
            return
        
        async with httpx.AsyncClient(
            base_url=settings.BVMT_BASE_URL,
            timeout=settings.SCRAPER_TIMEOUT,
            headers={"User-Agent": settings.SCRAPER_USER_AGENT},
        ) as client:
            prices_to_insert = []
            
            for company in companies:
                try:
                    price_data = await fetch_company_prices(client, company.ticker, db)
                    if price_data:
                        prices_to_insert.extend(price_data)
                except Exception as e:
                    logger.error(f"Failed to fetch prices for {company.ticker}: {e}")
            
            if prices_to_insert:
                await db.execute(insert(PriceDaily), prices_to_insert)
                await db.commit()
                logger.info(f"Inserted {len(prices_to_insert)} daily prices")
            
            await update_technical_indicators(db)
            
            for company in companies:
                company.last_price_update = datetime.utcnow()
            await db.commit()
            
            logger.info("Daily price ingestion completed successfully")


async def fetch_company_prices(client, ticker: str, db) -> list:
    """Fetch prices for a single company."""
    today = date.today()
    
    comp_result = await db.execute(select(Company).where(Company.ticker == ticker.upper()))
    company = comp_result.scalar_one_or_none()
    if not company:
        return []
    
    # Check if we already have today's data
    result = await db.execute(
        select(PriceDaily).where(
            PriceDaily.company_id == company.id,
            PriceDaily.date == today,
        )
    )
    if result.scalar_one_or_none():
        return []
    
    # In production, this would fetch from BVMT
    return []
async def update_technical_indicators(db):
    """Update technical indicators for all prices."""
    logger.info("Updating technical indicators...")
    
    result = await db.execute(select(Company))
    companies = result.scalars().all()
    
    for company in companies:
        price_query = (
            select(PriceDaily)
            .where(PriceDaily.company_id == company.id)
            .order_by(PriceDaily.date)
        )
        price_result = await db.execute(price_query)
        prices = price_result.scalars().all()
        
        if len(prices) < 20:
            continue
        
        df = pd.DataFrame([{
            "date": p.date,
            "open": float(p.open_price),
            "high": float(p.high_price),
            "low": float(p.low_price),
            "close": float(p.close_price),
            "volume": p.volume,
        } for p in prices])
        
        indicators = compute_technical_indicators(df)
        
        for i, row in df.iterrows():
            price_id = prices[i].id
            ind = indicators.iloc[i]
            
            update_cols = {
                "sma_20": ind.get("sma_20"),
                "sma_50": ind.get("sma_50"),
                "sma_200": ind.get("sma_200"),
                "ema_12": ind.get("ema_12"),
                "ema_26": ind.get("ema_26"),
                "rsi_14": ind.get("rsi_14"),
                "macd": ind.get("macd"),
                "daily_return_pct": ind.get("daily_return_pct"),
            }
            update_cols = {k: (Decimal(str(v)) if pd.notna(v) else None) for k, v in update_cols.items()}
            
            for col, val in update_cols.items():
                setattr(prices[i], col, val)
        
        logger.info(f"Updated technical indicators for {company.ticker}")
    
    await db.commit()
    logger.info("Technical indicators updated successfully")
@shared_task
def ingest_fx_rates():
    """Ingest FX rates from external APIs."""
    asyncio.run(_ingest_fx_rates())


async def _ingest_fx_rates():
    """Async implementation of FX rate ingestion."""
    logger.info("Starting FX rate ingestion...")
    
    async with async_session_maker() as db:
        result = await db.execute(select(FXPair).where(FXPair.is_active == True))
        pairs = result.scalars().all()
        
        if not pairs:
            logger.warning("No active FX pairs found")
            return
        
        async with httpx.AsyncClient(timeout=settings.SCRAPER_TIMEOUT) as client:
            rates_to_insert = []
            
            for pair in pairs:
                try:
                    rate = await fetch_fx_rate(client, pair)
                    if rate:
                        rates_to_insert.append(rate)
                except Exception as e:
                    logger.error(f"Failed to fetch FX rate for {pair.symbol}: {e}")
            
            if rates_to_insert:
                await db.execute(insert(FXRate), rates_to_insert)
                await db.commit()
                logger.info(f"Inserted {len(rates_to_insert)} FX rates")
            
            logger.info("FX rate ingestion completed successfully")


async def fetch_fx_rate(client, pair: FXPair):
    """Fetch FX rate from exchangerate.host API."""
    url = f"{settings.EXCHANGERATE_API_URL}/latest?base={pair.base_currency}"
    
    try:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        
        rate = data["rates"].get(pair.quote_currency)
        if rate is None:
            logger.warning(f"Rate not found for {pair.symbol}")
            return None
        
        return FXRate(
            pair_id=pair.id,
            date=date.today(),
            timestamp=datetime.utcnow(),
            rate=Decimal(str(rate)),
            source="exchangerate.host",
            is_validated=True,
        )
    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching FX rate for {pair.symbol}: {e}")
        return None


@shared_task
def ingest_commodities():
    """Ingest commodity prices (gold, fuel, etc.)."""
    asyncio.run(_ingest_commodities())


async def _ingest_commodities():
    """Async implementation of commodity ingestion."""
    logger.info("Starting commodity price ingestion...")
    
    async with async_session_maker() as db:
        result = await db.execute(select(Commodity).where(Commodity.is_active == True))
        commodities = result.scalars().all()
        
        if not commodities:
            logger.warning("No active commodities found")
            return
        
        async with httpx.AsyncClient(timeout=settings.SCRAPER_TIMEOUT) as client:
            prices_to_insert = []
            
            for commodity in commodities:
                try:
                    price = await fetch_commodity_price(client, commodity)
                    if price:
                        prices_to_insert.append(price)
                except Exception as e:
                    logger.error(f"Failed to fetch price for {commodity.code}: {e}")
            
            if prices_to_insert:
                await db.execute(insert(CommodityPrice), prices_to_insert)
                await db.commit()
                logger.info(f"Inserted {len(prices_to_insert)} commodity prices")
            
            logger.info("Commodity price ingestion completed successfully")


async def fetch_commodity_price(client, commodity: Commodity):
    """Fetch commodity price based on its configuration."""
    if commodity.code == "GOLD":
        url = "https://api.metals.live/v1/spot/gold"
        try:
            response = await client.get(url)
            data = response.json()
            price = Decimal(str(data.get("price", 0)))
            return CommodityPrice(
                commodity_id=commodity.id,
                date=date.today(),
                timestamp=datetime.utcnow(),
                price=price,
                source=url,
                is_validated=True,
            )
        except Exception:
            return None
    
    return None


@shared_task
def seed_initial_data():
    """Seed initial reference data (sectors, companies, FX pairs, commodities)."""
    asyncio.run(_seed_initial_data())
async def _seed_initial_data():
    """Seed initial reference data."""
    from app.seed.data import SECTORS, COMPANIES, FX_PAIRS, COMMODITIES
    
    logger.info("Seeding initial data...")
    
    async with async_session_maker() as db:
        # Seed sectors
        for sector_data in SECTORS:
            sector = Sector(**sector_data)
            db.add(sector)
        await db.commit()
        logger.info(f"Seeded {len(SECTORS)} sectors")
        
        # Seed companies
        for company_data in COMPANIES:
            company = Company(**company_data)
            db.add(company)
        await db.commit()
        logger.info(f"Seeded {len(COMPANIES)} companies")
        
        # Seed FX pairs
        for pair_data in FX_PAIRS:
            pair = FXPair(**pair_data)
            db.add(pair)
        await db.commit()
        logger.info(f"Seeded {len(FX_PAIRS)} FX pairs")
        
        # Seed commodities
        for commodity_data in COMMODITIES:
            commodity = Commodity(**commodity_data)
            db.add(commodity)
        await db.commit()
        logger.info(f"Seeded {len(COMMODITIES)} commodities")
        
        logger.info("Initial data seeding completed")