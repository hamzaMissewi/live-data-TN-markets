"""Data validation service."""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Tuple
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def validate_price_data(
    open_price: Decimal,
    high_price: Decimal,
    low_price: Decimal,
    close_price: Decimal,
    volume: int,
    company_id: int,
    prev_close: Optional[Decimal] = None,
) -> Tuple[bool, Optional[str]]:
    """
    Validate price data for a single day.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    errors = []
    
    # Check for null/empty prices
    if close_price is None or close_price <= 0:
        errors.append("Close price must be positive")
    
    if open_price is None or open_price <= 0:
        errors.append("Open price must be positive")
    
    if high_price is None or high_price <= 0:
        errors.append("High price must be positive")
    
    if low_price is None or low_price <= 0:
        errors.append("Low price must be positive")
    
    # Validate OHLC relationships
    if high_price < low_price:
        errors.append("High price must be >= low price")
    
    if high_price < close_price:
        errors.append("High price must be >= close price")
    
    if high_price < open_price:
        errors.append("High price must be >= open price")
    
    if low_price > close_price:
        errors.append("Low price must be <= close price")
    
    if low_price > open_price:
        errors.append("Low price must be <= open price")
    
    # Validate volume
    if volume < 0:
        errors.append("Volume cannot be negative")
    
    # Check for extreme price jumps (>50% in a single day without reason)
    if prev_close is not None and prev_close > 0:
        change_pct = abs((close_price - prev_close) / prev_close) * 100
        if change_pct > 50:
            logger.warning(
                f"Extreme price movement for company {company_id}: "
                f"{prev_close} -> {close_price} ({change_pct:.2f}%)"
            )
            # This is a warning, not an error - flag it for review
    
    if errors:
        return False, "; ".join(errors)
    return True, None


def validate_fx_rate(
    rate: Decimal,
    base_currency: str,
    quote_currency: str,
    prev_rate: Optional[Decimal] = None,
) -> Tuple[bool, Optional[str]]:
    """Validate FX rate data."""
    errors = []
    
    if rate is None or rate <= 0:
        errors.append("Rate must be positive")
    
    if prev_rate is not None and prev_rate > 0:
        change_pct = abs((rate - prev_rate) / prev_rate) * 100
        if change_pct > 5:
            logger.warning(
                f"Large FX rate movement for {base_currency}/{quote_currency}: "
                f"{prev_rate} -> {rate} ({change_pct:.2f}%)"
            )
    
    if errors:
        return False, "; ".join(errors)
    return True, None


def validate_commodity_price(
    price: Decimal,
    commodity_code: str,
    prev_price: Optional[Decimal] = None,
) -> Tuple[bool, Optional[str]]:
    """Validate commodity price data."""
    errors = []
    
    if price is None or price <= 0:
        errors.append("Price must be positive")
    
    if prev_price is not None and prev_price > 0:
        change_pct = abs((price - prev_price) / prev_price) * 100
        if change_pct > 15:
            logger.warning(
                f"Large commodity price movement for {commodity_code}: "
                f"{prev_price} -> {price} ({change_pct:.2f}%)"
            )
    
    if errors:
        return False, "; ".join(errors)
    return True, None


def check_data_staleness(
    last_update: Optional[datetime],
    max_age_hours: int = 24,
) -> Tuple[bool, Optional[int]]:
    """
    Check if data is stale.
    
    Returns:
        Tuple of (is_stale, hours_since_update)
    """
    if last_update is None:
        return True, None
    
    hours_since = (datetime.utcnow() - last_update).total_seconds() / 3600
    is_stale = hours_since > max_age_hours
    
    return is_stale, int(hours_since)