"""
Quandl Data Provider

Provides financial and economic data from Quandl/NASDAQ Data Link.
"""

from __future__ import annotations
from typing import Dict, Optional
import pandas as pd
import requests
import os


class QuandlProvider:
    """
    Data provider for Quandl/NASDAQ Data Link API
    
    Requires QUANDL_API_KEY environment variable.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('QUANDL_API_KEY')
        if not self.api_key:
            raise ValueError(
                "Quandl API key not found. "
                "Set QUANDL_API_KEY environment variable or pass api_key parameter."
            )
        self.base_url = "https://data.nasdaq.com/api/v3"
    
    def quote(self, ticker: str, database: str = "WIKI") -> Dict:
        """
        Get latest quote for a ticker
        
        Args:
            ticker: Stock symbol (e.g., 'AAPL')
            database: Quandl database (default: 'WIKI' for Wiki EOD Stock Prices)
            
        Returns:
            Dictionary with quote data
        """
        dataset_code = f"{database}/{ticker}"
        url = f"{self.base_url}/datasets/{dataset_code}/data.json"
        
        params = {
            'api_key': self.api_key,
            'limit': 1,
            'order': 'desc'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'dataset_data' not in data or not data['dataset_data']['data']:
                return {
                    'ticker': ticker,
                    'price': None,
                    'prev_close': None,
                    'currency': 'USD',
                    'error': 'No data available'
                }
            
            columns = data['dataset_data']['column_names']
            values = data['dataset_data']['data'][0]
            
            # Create dict from columns and values
            quote_dict = dict(zip(columns, values))
            
            return {
                'ticker': ticker,
                'price': quote_dict.get('Close', None),
                'prev_close': quote_dict.get('Adj. Close', None),
                'open': quote_dict.get('Open', None),
                'high': quote_dict.get('High', None),
                'low': quote_dict.get('Low', None),
                'volume': quote_dict.get('Volume', None),
                'currency': 'USD',
                'date': quote_dict.get('Date', '')
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
    
    def history(self, ticker: str, database: str = "WIKI", 
                start_date: Optional[str] = None, 
                end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Get historical data for a ticker
        
        Args:
            ticker: Stock symbol
            database: Quandl database (e.g., 'WIKI', 'EOD')
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            
        Returns:
            DataFrame with OHLCV data
        """
        dataset_code = f"{database}/{ticker}"
        url = f"{self.base_url}/datasets/{dataset_code}/data.json"
        
        params = {
            'api_key': self.api_key,
            'order': 'asc'
        }
        
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'dataset_data' not in data:
                print(f"No data available for {ticker}")
                return pd.DataFrame()
            
            columns = data['dataset_data']['column_names']
            values = data['dataset_data']['data']
            
            # Create DataFrame
            df = pd.DataFrame(values, columns=columns)
            
            # Set date as index
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)
            
            # Ensure numeric types
            numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj. Close']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            return df
            
        except Exception as e:
            print(f"Error fetching history for {ticker}: {e}")
            return pd.DataFrame()
    
    def get_dataset(self, database_code: str, dataset_code: str) -> pd.DataFrame:
        """
        Get arbitrary Quandl dataset
        
        Args:
            database_code: Database code (e.g., 'FRED')
            dataset_code: Dataset code (e.g., 'GDP')
            
        Returns:
            DataFrame with dataset
        """
        dataset = f"{database_code}/{dataset_code}"
        url = f"{self.base_url}/datasets/{dataset}/data.json"
        
        params = {
            'api_key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'dataset_data' not in data:
                return pd.DataFrame()
            
            columns = data['dataset_data']['column_names']
            values = data['dataset_data']['data']
            
            df = pd.DataFrame(values, columns=columns)
            
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)
            
            return df
            
        except Exception as e:
            print(f"Error fetching dataset {dataset}: {e}")
            return pd.DataFrame()
    
    def get_economic_indicator(self, indicator: str) -> pd.DataFrame:
        """
        Get economic indicator from FRED database
        
        Args:
            indicator: Indicator code (e.g., 'GDP', 'UNRATE', 'DGS10')
            
        Returns:
            DataFrame with indicator data
        """
        return self.get_dataset('FRED', indicator)
    
    def search_datasets(self, query: str, per_page: int = 10) -> pd.DataFrame:
        """
        Search for datasets
        
        Args:
            query: Search query
            per_page: Number of results per page
            
        Returns:
            DataFrame with search results
        """
        url = f"{self.base_url}/datasets.json"
        
        params = {
            'api_key': self.api_key,
            'query': query,
            'per_page': per_page
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'datasets' not in data:
                return pd.DataFrame()
            
            datasets = data['datasets']
            
            results = []
            for ds in datasets:
                results.append({
                    'database_code': ds.get('database_code', ''),
                    'dataset_code': ds.get('dataset_code', ''),
                    'name': ds.get('name', ''),
                    'description': ds.get('description', '')[:100],  # Truncate
                    'frequency': ds.get('frequency', ''),
                    'newest_available_date': ds.get('newest_available_date', ''),
                    'oldest_available_date': ds.get('oldest_available_date', '')
                })
            
            return pd.DataFrame(results)
            
        except Exception as e:
            print(f"Error searching datasets: {e}")
            return pd.DataFrame()
