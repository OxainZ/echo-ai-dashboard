"""
Alpha Vantage Data Provider

Provides real-time and historical stock data from Alpha Vantage API.
"""

from __future__ import annotations
from typing import Dict, Optional
import pandas as pd
import requests
import os
from datetime import datetime, timedelta


class AlphaVantageProvider:
    """
    Data provider for Alpha Vantage API
    
    Requires ALPHA_VANTAGE_API_KEY environment variable.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('ALPHA_VANTAGE_API_KEY')
        if not self.api_key:
            raise ValueError(
                "Alpha Vantage API key not found. "
                "Set ALPHA_VANTAGE_API_KEY environment variable or pass api_key parameter."
            )
        self.base_url = "https://www.alphavantage.co/query"
    
    def quote(self, ticker: str) -> Dict:
        """
        Get real-time quote for a ticker
        
        Args:
            ticker: Stock symbol (e.g., 'AAPL')
            
        Returns:
            Dictionary with quote data
        """
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': ticker,
            'apikey': self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'Global Quote' not in data:
                return {
                    'ticker': ticker,
                    'price': None,
                    'prev_close': None,
                    'currency': 'USD',
                    'error': 'No data available'
                }
            
            quote = data['Global Quote']
            return {
                'ticker': ticker,
                'price': float(quote['05. price']) if quote.get('05. price') else 0.0,
                'prev_close': float(quote['08. previous close']) if quote.get('08. previous close') else 0.0,
                'change': float(quote['09. change']) if quote.get('09. change') else 0.0,
                'change_percent': quote.get('10. change percent', '0%').replace('%', ''),
                'volume': int(quote['06. volume']) if quote.get('06. volume') else 0,
                'currency': 'USD',
                'timestamp': quote.get('07. latest trading day', '')
            }
        except Exception as e:
            print(f"Error fetching quote for {ticker}: {e}")
            return {
                'ticker': ticker,
                'price': None,
                'prev_close': None,
                'currency': 'USD',
                'error': str(e)
            }
    
    def history(self, ticker: str, period: str = "3mo", interval: str = "1d") -> pd.DataFrame:
        """
        Get historical data for a ticker
        
        Args:
            ticker: Stock symbol
            period: Time period (e.g., '3mo', '1y', 'full')
            interval: Data interval ('1d', '1wk', '1mo')
            
        Returns:
            DataFrame with OHLCV data
        """
        # Map period to outputsize
        if period in ['1mo', '3mo']:
            outputsize = 'compact'  # Last 100 data points
        else:
            outputsize = 'full'  # Full history
        
        # Map interval to function
        if interval == '1d':
            function = 'TIME_SERIES_DAILY'
            time_key = 'Time Series (Daily)'
        elif interval == '1wk':
            function = 'TIME_SERIES_WEEKLY'
            time_key = 'Weekly Time Series'
        elif interval == '1mo':
            function = 'TIME_SERIES_MONTHLY'
            time_key = 'Monthly Time Series'
        else:
            function = 'TIME_SERIES_DAILY'
            time_key = 'Time Series (Daily)'
        
        params = {
            'function': function,
            'symbol': ticker,
            'outputsize': outputsize,
            'apikey': self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if time_key not in data:
                print(f"No data available for {ticker}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame.from_dict(data[time_key], orient='index')
            df.index = pd.to_datetime(df.index)
            df.index.name = 'Date'
            
            # Rename columns
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            
            # Convert to numeric
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Sort by date
            df = df.sort_index()
            
            return df
            
        except Exception as e:
            print(f"Error fetching history for {ticker}: {e}")
            return pd.DataFrame()
    
    def get_technical_indicator(self, ticker: str, indicator: str, 
                                time_period: int = 14, series_type: str = 'close') -> pd.DataFrame:
        """
        Get technical indicator from Alpha Vantage
        
        Args:
            ticker: Stock symbol
            indicator: Technical indicator (e.g., 'RSI', 'MACD', 'SMA')
            time_period: Period for indicator calculation
            series_type: Price series ('close', 'open', 'high', 'low')
            
        Returns:
            DataFrame with indicator values
        """
        indicator_map = {
            'RSI': 'RSI',
            'MACD': 'MACD',
            'SMA': 'SMA',
            'EMA': 'EMA',
            'BBANDS': 'BBANDS',
            'ADX': 'ADX'
        }
        
        function = indicator_map.get(indicator.upper(), 'SMA')
        
        params = {
            'function': function,
            'symbol': ticker,
            'interval': 'daily',
            'time_period': time_period,
            'series_type': series_type,
            'apikey': self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Find the technical indicator key
            tech_key = None
            for key in data.keys():
                if 'Technical' in key:
                    tech_key = key
                    break
            
            if not tech_key:
                return pd.DataFrame()
            
            df = pd.DataFrame.from_dict(data[tech_key], orient='index')
            df.index = pd.to_datetime(df.index)
            df.index.name = 'Date'
            
            # Convert to numeric
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df = df.sort_index()
            return df
            
        except Exception as e:
            print(f"Error fetching {indicator} for {ticker}: {e}")
            return pd.DataFrame()
    
    def get_company_overview(self, ticker: str) -> Dict:
        """
        Get company overview and fundamental data
        
        Args:
            ticker: Stock symbol
            
        Returns:
            Dictionary with company information
        """
        params = {
            'function': 'OVERVIEW',
            'symbol': ticker,
            'apikey': self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                'symbol': data.get('Symbol', ticker),
                'name': data.get('Name', ''),
                'sector': data.get('Sector', ''),
                'industry': data.get('Industry', ''),
                'market_cap': data.get('MarketCapitalization', ''),
                'pe_ratio': data.get('PERatio', ''),
                'dividend_yield': data.get('DividendYield', ''),
                '52_week_high': data.get('52WeekHigh', ''),
                '52_week_low': data.get('52WeekLow', '')
            }
        except Exception as e:
            print(f"Error fetching company overview for {ticker}: {e}")
            return {'symbol': ticker, 'error': str(e)}
