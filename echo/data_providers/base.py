"""
Price Provider Protocol

Defines the interface that all market data providers must implement
to be compatible with the Echo Engine.

This protocol ensures:
- Consistent data access patterns
- Easy provider swapping (yfinance, Alpha Vantage, etc.)
- Type safety through Protocol typing
"""
from typing import Protocol, Dict
import pandas as pd

class PriceProvider(Protocol):
    """
    Protocol for market data providers
    
    All data providers must implement these methods to provide
    real-time quotes and historical price data.
    
    Methods:
        quote: Fetch real-time quote for a ticker
        history: Fetch historical OHLCV data
    """
    
    def quote(self, ticker: str) -> Dict:
        """
        Get real-time quote data
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            Dict: Quote data with ticker, price, prev_close, currency
        """
        ...
    
    def history(self, ticker: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
        """
        Get historical price data
        
        Args:
            ticker (str): Stock ticker symbol
            period (str): Time period for data
            interval (str): Data interval granularity
            
        Returns:
            pd.DataFrame: Historical OHLCV data
        """
        ...
