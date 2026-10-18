"""Anomaly detection Celery tasks."""
import asyncio
from datetime import date, datetime, timedelta
from decimal import Decimal
import numpy as np
import pandas as pd
from sqlalchemy import select, and_, insert
from celery import shared_task
from app.db.session import async_session_maker
from app.models.company import Company
from app.models.price import PriceDaily
from app.models.anomaly import Anomaly, AnomalyType
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

VOLUME_ZSCORE_THRESHOLD = 3.0
PRICE_ZSCORE_THRESHOLD = 2.5
RSI_OVERSOLD = 30.0
RSI_OVERBOUGHT = 70.0


@shared_task
def detect_anomalies(company_id: int = None, days: int = 30):
    """Detect market anomalies for all companies or a specific company."""
    asyncio.run(_detect_anomalies_task(company_id, days))


async def _detect_anomalies_task(company_id: int = None, days: int = 30):
    """Async implementation of anomaly detection."""
    logger.info("Starting anomaly detection...")
    
    async with async_session_maker() as db:
        query = select(Company).where(Company.is_active == True)
        if company_id:
            query = query.where(Company.id == company_id)
        
        result = await db.execute(query)
        companies = result.scalars().all()
        
        if not companies:
            logger.warning("No active companies found")
            return
        
        anomalies_to_insert = []
        cutoff_date = date.today() - timedelta(days=days)
        
        for company in companies:
            try:
                price_query = (
                    select(PriceDaily)
                    .where(
                        and_(
                            PriceDaily.company_id == company.id,
                            PriceDaily.date >= cutoff_date
                        )
                    )
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
                    "rsi_14": float(p.rsi_14) if p.rsi_14 else None,
                } for p in prices])
                
                anomalies_to_insert.extend(detect_volume_spikes(df, company, prices))
                anomalies_to_insert.extend(detect_price_gaps(df, company, prices))
                anomalies_to_insert.extend(detect_rsi_extremes(df, company, prices))
                anomalies_to_insert.extend(detect_bollinger_breakouts(df, company, prices))
                anomalies_to_insert.extend(detect_ma_crosses(df, company, prices))
                
            except Exception as e:
                logger.error(f"Anomaly detection failed for {company.ticker}: {e}")
        
        if anomalies_to_insert:
            existing_query = select(Anomaly.company_id, Anomaly.date, Anomaly.anomaly_type)
            existing_result = await db.execute(existing_query)
            existing = {(row.company_id, row.date, row.anomaly_type) for row in existing_result.all()}
            
            new_anomalies = [
                a for a in anomalies_to_insert
                if (a["company_id"], a["date"], a["anomaly_type"]) not in existing
            ]
            
            if new_anomalies:
                await db.execute(insert(Anomaly), new_anomalies)
                await db.commit()
                logger.info(f"Inserted {len(new_anomalies)} new anomalies")
        
        logger.info("Anomaly detection completed successfully")
def detect_volume_spikes(df, company, prices):
    """Detect volume spikes using z-score."""
    anomalies = []
    if len(df) < 10:
        return anomalies
    
    volumes = df["volume"].values
    mean_vol = np.mean(volumes[:-1])
    std_vol = np.std(volumes[:-1])
    
    if std_vol > 0:
        z_score = (volumes[-1] - mean_vol) / std_vol
        if z_score >= VOLUME_ZSCORE_THRESHOLD:
            anomalies.append(_create_anomaly(
                company=company,
                price_date=prices[-1].date,
                anomaly_type=AnomalyType.VOLUME_SPIKE,
                z_score=z_score,
                severity="high" if z_score > 4.0 else "medium",
                description_en=f"Unusual trading volume: {z_score:.2f} standard deviations above normal",
                description_fr=f"Volume d'échange inhabituel : {z_score:.2f} écarts-types au-dessus de la normale",
                description_ar=f"حجم تداول غير عادي: {z_score:.2f} انحراف معياري فوق الطبيعي",
            ))
    return anomalies


def detect_price_gaps(df, company, prices):
    """Detect price gaps between consecutive days."""
    anomalies = []
    if len(df) < 2:
        return anomalies
    
    prev_close = df["close"].iloc[-2]
    open_price = df["open"].iloc[-1]
    gap_pct = ((open_price - prev_close) / prev_close) * 100
    
    if abs(gap_pct) >= 5.0:
        anomaly_type = AnomalyType.GAP_UP if gap_pct > 0 else AnomalyType.GAP_DOWN
        anomalies.append(_create_anomaly(
            company=company,
            price_date=prices[-1].date,
            anomaly_type=anomaly_type,
            value=gap_pct,
            severity="high" if abs(gap_pct) > 10.0 else "medium",
            description_en=f"Price gap of {gap_pct:.2f}% vs previous close",
            description_fr=f"Écart de prix de {gap_pct:.2f}% par rapport à la clôture précédente",
            description_ar=f"فجوة سعرية بنسبة {gap_pct:.2f}% مقارنة بإغلاق اليوم السابق",
        ))
    return anomalies


def detect_rsi_extremes(df, company, prices):
    """Detect RSI extreme values."""
    anomalies = []
    if len(df) < 15 or df["rsi_14"].isna().all():
        return anomalies
    
    rsi = df["rsi_14"].iloc[-1]
    if pd.notna(rsi):
        if rsi >= RSI_OVERBOUGHT:
            anomalies.append(_create_anomaly(
                company=company,
                price_date=prices[-1].date,
                anomaly_type=AnomalyType.RSI_EXTREME,
                value=rsi,
                severity="medium" if rsi < 85 else "high",
                description_en=f"RSI extreme (overbought): {rsi:.2f}",
                description_fr=f"RSI extrême (surachaté) : {rsi:.2f}",
                description_ar=f"مؤشر RSI متطرف (متشرى): {rsi:.2f}",
            ))
        elif rsi <= RSI_OVERSOLD:
            anomalies.append(_create_anomaly(
                company=company,
                price_date=prices[-1].date,
                anomaly_type=AnomalyType.RSI_EXTREME,
                value=rsi,
                severity="medium" if rsi > 15 else "high",
                description_en=f"RSI extreme (oversold): {rsi:.2f}",
                description_fr=f"RSI extrême (survendu) : {rsi:.2f}",
                description_ar=f"مؤشر RSI متطرف (مبيع زائد): {rsi:.2f}",
            ))
    return anomalies
def detect_bollinger_breakouts(df, company, prices):
    """Detect Bollinger Band breakouts."""
    anomalies = []
    if len(df) < 20:
        return anomalies
    
    close = df["close"]
    sma_20 = close.rolling(window=20).mean()
    bb_std = close.rolling(window=20).std()
    bb_upper = sma_20 + 2 * bb_std
    bb_lower = sma_20 - 2 * bb_std
    
    current_close = close.iloc[-1]
    prev_upper = bb_upper.iloc[-2] if len(bb_upper) > 1 else None
    prev_lower = bb_lower.iloc[-2] if len(bb_lower) > 1 else None
    
    if prev_upper is not None and prev_upper > 0:
        ratio = (current_close - prev_upper) / prev_upper
        if ratio > 0.05:
            anomalies.append(_create_anomaly(
                company=company,
                price_date=prices[-1].date,
                anomaly_type=AnomalyType.BOLLINGER_BREAKOUT,
                value=ratio * 100,
                severity="medium",
                description_en=f"Price above upper Bollinger Band by {ratio*100:.2f}%",
                description_fr=f"Prix au-dessus de la borne supérieure de Bollinger de {ratio*100:.2f}%",
                description_ar=f"السعر أعلى من حد بولينجر العلوي بمقدار {ratio*100:.2f}%",
            ))
    
    if prev_lower is not None and prev_lower > 0:
        ratio = (prev_lower - current_close) / prev_lower
        if ratio > 0.05:
            anomalies.append(_create_anomaly(
                company=company,
                price_date=prices[-1].date,
                anomaly_type=AnomalyType.BOLLINGER_BREAKOUT,
                value=-ratio * 100,
                severity="medium",
                description_en=f"Price below lower Bollinger Band by {ratio*100:.2f}%",
                description_fr=f"Prix en dessous de la borne inférieure de Bollinger de {ratio*100:.2f}%",
                description_ar=f"السعر أقل من حد بولينجر السفلي بمقدار {ratio*100:.2f}%",
            ))
    return anomalies


def detect_ma_crosses(df, company, prices):
    """Detect moving average crosses."""
    anomalies = []
    if len(df) < 21:
        return anomalies
    
    close = df["close"]
    sma_20 = close.rolling(window=20).mean()
    sma_50 = close.rolling(window=50).mean()
    
    if len(sma_20) > 1 and len(sma_50) > 1:
        if sma_20.iloc[-2] < sma_50.iloc[-2] and sma_20.iloc[-1] > sma_50.iloc[-1]:
            anomalies.append(_create_anomaly(
                company=company,
                price_date=prices[-1].date,
                anomaly_type=AnomalyType.MOVING_AVERAGE_CROSS,
                value=float(sma_20.iloc[-1]),
                severity="high",
                description_en="Golden cross: 20-day MA crossed above 50-day MA",
                description_fr="Croisement haussier : MA(20) au-dessus de MA(50)",
                description_ar="تقاطع ذهبي: المتوسط المتحرك 20 أعلى من 50",
            ))
        elif sma_20.iloc[-2] > sma_50.iloc[-2] and sma_20.iloc[-1] < sma_50.iloc[-1]:
            anomalies.append(_create_anomaly(
                company=company,
                price_date=prices[-1].date,
                anomaly_type=AnomalyType.MOVING_AVERAGE_CROSS,
                value=float(sma_20.iloc[-1]),
                severity="high",
                description_en="Death cross: 20-day MA crossed below 50-day MA",
                description_fr="Croisement baissier : MA(20) en dessous de MA(50)",
                description_ar="تقاطع أسود: المتوسط المتحرك 20 تحت 50",
            ))
    return anomalies


def _create_anomaly(**kwargs):
    """Helper to create anomaly dict."""
    return {
        "company_id": kwargs["company"].id,
        "date": kwargs["price_date"],
        "anomaly_type": kwargs["anomaly_type"].value,
        "z_score": kwargs.get("z_score"),
        "value": kwargs.get("value"),
        "expected_value": kwargs.get("expected_value"),
        "threshold": kwargs.get("threshold"),
        "description_en": kwargs["description_en"],
        "description_fr": kwargs["description_fr"],
        "description_ar": kwargs["description_ar"],
        "is_explained_by_news": False,
        "severity": kwargs.get("severity", "medium"),
        "confidence": min(kwargs.get("z_score", 0) / 5.0, 1.0) if "z_score" in kwargs else 0.8,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }