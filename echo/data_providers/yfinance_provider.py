"""
Yahoo Finance Data Provider

This module implements the Yahoo Finance data provider for fetching real-time
and historical market data using the yfinance library.

The provider supports:
- Real-time price quotes
- Historical OHLCV data
- Multiple time periods and intervals
- Currency information
"""

from __future__ import annotations
from typing import Dict
import pandas as pd

try:
    import yfinance as yf
except Exception:
    yf = None

class YFinanceProvider:
    """
    Yahoo Finance data provider for market data.
    
    This provider wraps the yfinance library to fetch real-time quotes
    and historical price data for stocks, ETFs, and other securities.
    
    Features:
        - Real-time price quotes with previous close
        - Historical OHLCV data (Open, High, Low, Close, Volume)
        - Flexible time periods (1d, 5d, 1mo, 3mo, 6mo, 1y, etc.)
        - Multiple intervals (1m, 2m, 5m, 15m, 30m, 60m, 1d, 1wk, 1mo)
        - Currency information for international securities
    
    Note:
        Requires yfinance library to be installed: pip install yfinance
        
    Example:
        >>> provider = YFinanceProvider()
        >>> quote = provider.quote("AAPL")
        >>> print(f"Price: ${quote['price']}")
        >>> history = provider.history("AAPL", period="1mo")
        >>> print(history.tail())
    """
    
    def __init__(self):
        """
        Initialize the Yahoo Finance provider.
        
        Raises:
            RuntimeError: If yfinance library is not installed
        """
        if yf is None:
            raise RuntimeError("yfinance not installed. Run `pip install yfinance`.")
            
    def quote(self, ticker: str) -> Dict:
        """
        Fetch real-time quote for a given ticker.
        
        Args:
            ticker: Stock ticker symbol (e.g., "AAPL", "MSFT", "SPY")
            
        Returns:
            Dictionary containing:
                - ticker: The ticker symbol
                - price: Current/last price (float or None)
                - prev_close: Previous closing price (float or None)
                - currency: Currency code (e.g., "USD", "EUR")
                
        Example:
            >>> provider = YFinanceProvider()
            >>> quote = provider.quote("AAPL")
            >>> print(f"Current: ${quote['price']}, Prev: ${quote['prev_close']}")
            
        Note:
            - Returns None for price if market is closed or data unavailable
            - Currency defaults to "USD" if not available
        """
        t = yf.Ticker(ticker)
        info = t.fast_info
        return {
            "ticker": ticker,
            "price": float(info.last_price) if info.last_price is not None else None,
            "prev_close": float(info.previous_close) if info.previous_close is not None else None,
            "currency": info.currency or "USD",
        }
        
    def history(self, ticker: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
        """
        Fetch historical OHLCV data for a given ticker.
        
        Args:
            ticker: Stock ticker symbol (e.g., "AAPL", "MSFT", "SPY")
            period: Time period for historical data
                Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
            interval: Data interval/granularity
                Valid intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
                
        Returns:
            pandas DataFrame with columns:
                - Date (index): Trading date/datetime
                - Open: Opening price
                - High: High price
                - Low: Low price
                - Close: Closing price (not adjusted)
                - Volume: Trading volume
                - Dividends: Dividend amount (if any)
                - Stock Splits: Split ratio (if any)
                
        Example:
            >>> provider = YFinanceProvider()
            >>> # Get 3 months of daily data
            >>> df = provider.history("AAPL", period="3mo", interval="1d")
            >>> print(f"Average Close: ${df['Close'].mean():.2f}")
            >>> 
            >>> # Get 1 day of 5-minute data
            >>> df_intraday = provider.history("SPY", period="1d", interval="5m")
            
        Note:
            - auto_adjust=False returns unadjusted prices
            - Some period/interval combinations may not be valid
            - Intraday intervals (< 1d) limited to last 60 days of data
        """
        t = yf.Ticker(ticker)
        df = t.history(period=period, interval=interval, auto_adjust=False)
        return df
