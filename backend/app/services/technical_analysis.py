"""Technical analysis service using pandas."""
import pandas as pd
import numpy as np
from typing import Optional


def compute_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute technical indicators for a DataFrame of OHLCV data.
    
    Args:
        df: DataFrame with columns ['open', 'high', 'low', 'close', 'volume']
    
    Returns:
        DataFrame with technical indicators added
    """
    if len(df) < 2:
        # Not enough data
        for col in ["sma_20", "sma_50", "sma_200", "ema_12", "ema_26",
                     "rsi_14", "macd", "macd_signal", "macd_histogram",
                     "bollinger_upper", "bollinger_middle", "bollinger_lower",
                     "daily_return", "daily_return_pct"]:
            df[col] = np.nan
        return df
    
    close = df["close"]
    high = df["high"]
    low = df["low"]
    volume = df["volume"]
    
    # Moving Averages
    df["sma_20"] = close.rolling(window=20, min_periods=1).mean()
    df["sma_50"] = close.rolling(window=50, min_periods=1).mean()
    df["sma_200"] = close.rolling(window=200, min_periods=1).mean()
    
    # EMAs (alpha = 2/(n+1))
    df["ema_12"] = close.ewm(span=12, adjust=False).mean()
    df["ema_26"] = close.ewm(span=26, adjust=False).mean()
    
    # MACD
    df["macd"] = df["ema_12"] - df["ema_26"]
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_histogram"] = df["macd"] - df["macd_signal"]
    
    # Bollinger Bands
    bb_std = close.rolling(window=20, min_periods=1).std()
    df["bollinger_middle"] = close.rolling(window=20, min_periods=1).mean()
    df["bollinger_upper"] = df["bollinger_middle"] + (2 * bb_std)
    df["bollinger_lower"] = df["bollinger_middle"] - (2 * bb_std)
    
    # RSI
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
    rs = gain / loss.replace(0, np.nan)
    df["rsi_14"] = 100 - (100 / (1 + rs))
    df["rsi_14"] = df["rsi_14"].fillna(50)  # Neutral for initial values
    
    # Daily returns
    df["daily_return"] = close.diff()
    df["daily_return_pct"] = close.pct_change() * 100
    
    # Volume analysis
    df["vol_ma_20"] = volume.rolling(window=20, min_periods=1).mean()
    df["vol_z_score"] = (volume - df["vol_ma_20"]) / volume.rolling(window=20, min_periods=1).std().replace(0, np.nan)
    
    return df


def compute_sector_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Compute sector-level performance metrics."""
    return df


def compute_market_breadth(df: pd.DataFrame) -> dict:
    """Compute market breadth indicators."""
    if len(df) == 0:
        return {}
    
    advancing = len(df[df["daily_return_pct"] > 0])
    declining = len(df[df["daily_return_pct"] < 0])
    unchanged = len(df[df["daily_return_pct"] == 0])
    
    return {
        "advancing": advancing,
        "declining": declining,
        "unchanged": unchanged,
        "advance_decline_ratio": advancing / declining if declining > 0 else float("inf"),
    }


def format_price(value: Optional[float], currency: str = "TND") -> str:
    """Format a price value with currency symbol and proper decimals."""
    if value is None:
        return "N/A"
    
    if currency == "TND":
        return f"{value:,.2f} TND"
    return f"{value:,.2f} {currency}"


def format_change(value: Optional[float]) -> str:
    """Format a change value with sign."""
    if value is None:
        return "N/A"
    
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f}%"