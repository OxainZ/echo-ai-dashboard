"""
Quandl data provider for Echo AI Dashboard
Provides historical financial data
"""
from __future__ import annotations
from typing import Dict, Optional
import pandas as pd
import requests
from .base import PriceProvider
from ..utils.config import config
from ..utils.logging import get_logger

log = get_logger("QuandlProvider")


class QuandlProvider(PriceProvider):
    """Quandl (Nasdaq Data Link) API data provider"""
    
    BASE_URL = "https://data.nasdaq.com/api/v3"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.quandl_api_key
        if not self.api_key:
            log.warning("Quandl API key not configured. Some features may be limited.")
    
    def quote(self, ticker: str) -> Dict:
        """
        Get latest quote for a ticker
        Note: Quandl is primarily for historical data, real-time quotes are limited
        """
        if not self.api_key:
            log.error("Quandl API key not configured")
            return self._get_fallback_quote(ticker)
        
        try:
            # Get most recent data point
            url = f"{self.BASE_URL}/datasets/WIKI/{ticker}.json"
            params = {'api_key': self.api_key, 'rows': 1}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'dataset' not in data or not data['dataset'].get('data'):
                log.warning(f"No quote data for {ticker}, using fallback")
                return self._get_fallback_quote(ticker)
            
            latest = data['dataset']['data'][0]
            column_names = data['dataset']['column_names']
            
            # Map columns to values
            data_dict = dict(zip(column_names, latest))
            
            return {
                'ticker': ticker,
                'price': float(data_dict.get('Close', 0)),
                'prev_close': float(data_dict.get('Open', 0)),
                'volume': int(data_dict.get('Volume', 0)),
                'high': float(data_dict.get('High', 0)),
                'low': float(data_dict.get('Low', 0)),
                'currency': 'USD',
            }
        except Exception as e:
            log.exception(f"Error fetching quote for {ticker}: {e}")
            return self._get_fallback_quote(ticker)
    
    def history(self, ticker: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
        """Get historical price data from Quandl"""
        if not self.api_key:
            log.error("Quandl API key not configured")
            return pd.DataFrame()
        
        try:
            # Calculate start date based on period
            from datetime import datetime, timedelta
            end_date = datetime.now()
            
            if period == '1mo':
                start_date = end_date - timedelta(days=30)
            elif period == '3mo':
                start_date = end_date - timedelta(days=90)
            elif period == '1y':
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=30)
            
            url = f"{self.BASE_URL}/datasets/WIKI/{ticker}.json"
            params = {
                'api_key': self.api_key,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'dataset' not in data or not data['dataset'].get('data'):
                log.warning(f"No historical data for {ticker}")
                return pd.DataFrame()
            
            column_names = data['dataset']['column_names']
            rows = data['dataset']['data']
            
            # Create DataFrame
            df = pd.DataFrame(rows, columns=column_names)
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
            df = df.sort_index()
            
            # Keep relevant columns
            df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
            df = df.astype(float)
            
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
