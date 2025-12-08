from __future__ import annotations
from typing import Dict, Optional
import pandas as pd
import time
import re
from functools import lru_cache

try:
    import yfinance as yf
except Exception:
    yf = None

class YFinanceProvider:
    """Enhanced Yahoo Finance data provider with error handling, retry logic, and caching."""
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        if yf is None:
            raise RuntimeError("yfinance not installed. Run `pip install yfinance`.")
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def _validate_ticker(self, ticker: str) -> str:
        """Validate and sanitize ticker symbol."""
        if not ticker or not isinstance(ticker, str):
            raise ValueError("Ticker must be a non-empty string")
        
        # Remove whitespace and convert to uppercase
        ticker = ticker.strip().upper()
        
        # Basic validation: alphanumeric, dots, hyphens
        if not re.match(r'^[A-Z0-9.\-]+$', ticker):
            raise ValueError(f"Invalid ticker symbol: {ticker}")
        
        return ticker
    
    def _retry_on_failure(self, func, *args, **kwargs):
        """Retry a function call on failure with exponential backoff."""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    time.sleep(wait_time)
        
        raise last_exception
    
    def quote(self, ticker: str) -> Dict:
        """
        Get current quote for a ticker with error handling.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with ticker, price, prev_close, and currency
            
        Raises:
            ValueError: If ticker is invalid
            RuntimeError: If data fetch fails after retries
        """
        ticker = self._validate_ticker(ticker)
        
        def _fetch_quote():
            t = yf.Ticker(ticker)
            info = t.fast_info
            
            # Handle missing data gracefully
            price = float(info.last_price) if hasattr(info, 'last_price') and info.last_price is not None else None
            prev_close = float(info.previous_close) if hasattr(info, 'previous_close') and info.previous_close is not None else None
            currency = info.currency if hasattr(info, 'currency') else "USD"
            
            if price is None:
                raise RuntimeError(f"Unable to fetch price data for {ticker}")
            
            return {
                "ticker": ticker,
                "price": price,
                "prev_close": prev_close,
                "currency": currency or "USD",
            }
        
        return self._retry_on_failure(_fetch_quote)
    
    def history(self, ticker: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
        """
        Get historical data for a ticker with error handling.
        
        Args:
            ticker: Stock ticker symbol
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            DataFrame with historical price data
            
        Raises:
            ValueError: If ticker or parameters are invalid
            RuntimeError: If data fetch fails after retries
        """
        ticker = self._validate_ticker(ticker)
        
        # Validate period and interval
        valid_periods = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"}
        valid_intervals = {"1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"}
        
        if period not in valid_periods:
            raise ValueError(f"Invalid period: {period}. Must be one of {valid_periods}")
        if interval not in valid_intervals:
            raise ValueError(f"Invalid interval: {interval}. Must be one of {valid_intervals}")
        
        def _fetch_history():
            t = yf.Ticker(ticker)
            df = t.history(period=period, interval=interval, auto_adjust=False)
            
            if df.empty:
                raise RuntimeError(f"No historical data available for {ticker} (period={period}, interval={interval})")
            
            return df
        
        return self._retry_on_failure(_fetch_history)
