"""
Alpha Vantage data provider for Echo AI Dashboard
Provides real-time and historical stock data
"""
from __future__ import annotations
from typing import Dict, Optional
import pandas as pd
import requests
from .base import PriceProvider
from ..utils.config import config
from ..utils.logging import get_logger

log = get_logger("AlphaVantageProvider")


class AlphaVantageProvider(PriceProvider):
    """Alpha Vantage API data provider"""
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.alpha_vantage_api_key
        if not self.api_key:
            log.warning("Alpha Vantage API key not configured. Some features may be limited.")
    
    def quote(self, ticker: str) -> Dict:
        """Get real-time quote for a ticker"""
        if not self.api_key:
            log.error("Alpha Vantage API key not configured")
            return self._get_fallback_quote(ticker)
        
        try:
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': ticker,
                'apikey': self.api_key
            }
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'Global Quote' not in data:
                log.warning(f"No quote data for {ticker}, using fallback")
                return self._get_fallback_quote(ticker)
            
            quote_data = data['Global Quote']
            return {
                'ticker': ticker,
                'price': float(quote_data.get('05. price', 0)),
                'prev_close': float(quote_data.get('08. previous close', 0)),
                'volume': int(quote_data.get('06. volume', 0)),
                'change': float(quote_data.get('09. change', 0)),
                'change_percent': quote_data.get('10. change percent', '0%').rstrip('%'),
                'currency': 'USD',
            }
        except Exception as e:
            log.exception(f"Error fetching quote for {ticker}: {e}")
            return self._get_fallback_quote(ticker)
    
    def history(self, ticker: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
        """Get historical price data"""
        if not self.api_key:
            log.error("Alpha Vantage API key not configured")
            return pd.DataFrame()
        
        try:
            # Map period to Alpha Vantage outputsize
            outputsize = 'compact' if period in ['1mo', '3mo'] else 'full'
            
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': ticker,
                'outputsize': outputsize,
                'apikey': self.api_key
            }
            
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'Time Series (Daily)' not in data:
                log.warning(f"No historical data for {ticker}")
                return pd.DataFrame()
            
            time_series = data['Time Series (Daily)']
            
            # Convert to DataFrame
            df = pd.DataFrame.from_dict(time_series, orient='index')
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            
            # Rename columns to match yfinance format
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            df = df.astype(float)
            
            # Filter by period
            if period == '1mo':
                df = df.last('30D')
            elif period == '3mo':
                df = df.last('90D')
            elif period == '1y':
                df = df.last('365D')
            
            return df
            
        except Exception as e:
            log.exception(f"Error fetching history for {ticker}: {e}")
            return pd.DataFrame()
    
    def _get_fallback_quote(self, ticker: str) -> Dict:
        """Fallback quote when API is unavailable"""
        return {
            'ticker': ticker,
            'price': None,
            'prev_close': None,
            'currency': 'USD',
        }
