"""
Yahoo Finance Data Provider

Implements the PriceProvider protocol using the yfinance library
to fetch real-time market data and historical price information.

This provider handles:
- Real-time quote data
- Historical OHLCV data
- Automatic error handling
- Data format standardization
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
    Yahoo Finance data provider implementation
    
    Provides market data access through the yfinance library.
    Implements the PriceProvider protocol for compatibility with
    the Echo Engine.
    
    Raises:
        RuntimeError: If yfinance library is not installed
    """
    
    def __init__(self):
        """Initialize the Yahoo Finance provider"""
        if yf is None:
            raise RuntimeError("yfinance not installed. Run `pip install yfinance`.")
    
    def quote(self, ticker: str) -> Dict:
        """
        Get real-time quote data for a ticker
        
        Args:
            ticker (str): Stock ticker symbol (e.g., 'AAPL', 'TSLA')
            
        Returns:
            Dict: Quote data with keys:
                - ticker: Stock symbol
                - price: Current price (or None if unavailable)
                - prev_close: Previous close price
                - currency: Trading currency (default: USD)
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
        Get historical price data for a ticker
        
        Args:
            ticker (str): Stock ticker symbol
            period (str): Time period (e.g., '1d', '5d', '1mo', '3mo', '1y')
            interval (str): Data interval (e.g., '1m', '5m', '1h', '1d')
            
        Returns:
            pd.DataFrame: Historical OHLCV data with columns:
                - Open, High, Low, Close: Price data
                - Volume: Trading volume
                - Dividends, Stock Splits: Corporate actions
                
        Note:
            Uses auto_adjust=False to preserve raw price data.
            Adjustments can be applied separately if needed.
        """
        t = yf.Ticker(ticker)
        df = t.history(period=period, interval=interval, auto_adjust=False)
        return df
