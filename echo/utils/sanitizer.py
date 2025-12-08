"""
Data sanitization and validation utilities for Echo AI Dashboard
"""
from __future__ import annotations
from typing import Any, Dict, Optional
import pandas as pd
import numpy as np
from ..utils.logging import get_logger

log = get_logger("DataSanitizer")


class DataSanitizer:
    """Data sanitization and validation utilities"""
    
    @staticmethod
    def sanitize_ticker(ticker: str) -> str:
        """Sanitize and validate ticker symbol"""
        if not ticker:
            raise ValueError("Ticker cannot be empty")
        
        # Remove whitespace and convert to uppercase
        ticker = ticker.strip().upper()
        
        # Remove invalid characters
        ticker = ''.join(c for c in ticker if c.isalnum() or c in ['-', '.'])
        
        if not ticker:
            raise ValueError("Invalid ticker symbol")
        
        return ticker
    
    @staticmethod
    def sanitize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate price data DataFrame"""
        if df.empty:
            return df
        
        # Make a copy to avoid modifying original
        df = df.copy()
        
        # Remove duplicates
        df = df[~df.index.duplicated(keep='first')]
        
        # Handle missing values
        # Forward fill first, then backward fill any remaining
        df = df.ffill().bfill()
        
        # Remove infinite values
        df = df.replace([np.inf, -np.inf], np.nan)
        
        # Drop rows where all values are NaN
        df = df.dropna(how='all')
        
        # Ensure numeric columns are numeric
        numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Validate price data integrity
        if 'High' in df.columns and 'Low' in df.columns:
            # High should be >= Low
            invalid_rows = df['High'] < df['Low']
            if invalid_rows.any():
                log.warning(f"Found {invalid_rows.sum()} rows where High < Low, fixing...")
                df.loc[invalid_rows, 'High'] = df.loc[invalid_rows, 'Low']
        
        # Ensure Close is between High and Low
        if all(col in df.columns for col in ['High', 'Low', 'Close']):
            df.loc[df['Close'] > df['High'], 'Close'] = df.loc[df['Close'] > df['High'], 'High']
            df.loc[df['Close'] < df['Low'], 'Close'] = df.loc[df['Close'] < df['Low'], 'Low']
        
        # Remove negative prices
        for col in ['Open', 'High', 'Low', 'Close']:
            if col in df.columns:
                negative_rows = df[col] < 0
                if negative_rows.any():
                    log.warning(f"Found {negative_rows.sum()} negative values in {col}, removing...")
                    df = df[df[col] >= 0]
        
        # Ensure Volume is non-negative
        if 'Volume' in df.columns:
            df.loc[df['Volume'] < 0, 'Volume'] = 0
        
        return df
    
    @staticmethod
    def sanitize_quote(quote: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize quote data dictionary"""
        if not quote:
            return {}
        
        sanitized = {}
        
        # Ticker
        if 'ticker' in quote:
            try:
                sanitized['ticker'] = DataSanitizer.sanitize_ticker(quote['ticker'])
            except ValueError:
                log.warning(f"Invalid ticker in quote: {quote.get('ticker')}")
        
        # Numeric fields
        numeric_fields = ['price', 'prev_close', 'high', 'low', 'open', 'change']
        for field in numeric_fields:
            if field in quote:
                try:
                    value = float(quote[field]) if quote[field] is not None else None
                    if value is not None and (value < 0 or np.isnan(value) or np.isinf(value)):
                        log.warning(f"Invalid {field} in quote: {value}")
                        value = None
                    sanitized[field] = value
                except (ValueError, TypeError):
                    sanitized[field] = None
        
        # Volume (integer)
        if 'volume' in quote:
            try:
                volume = int(quote['volume']) if quote['volume'] is not None else 0
                sanitized['volume'] = max(0, volume)
            except (ValueError, TypeError):
                sanitized['volume'] = 0
        
        # String fields
        string_fields = ['currency', 'change_percent']
        for field in string_fields:
            if field in quote:
                sanitized[field] = str(quote[field]) if quote[field] is not None else ''
        
        return sanitized
    
    @staticmethod
    def validate_price_data(df: pd.DataFrame) -> bool:
        """Validate that DataFrame contains valid price data"""
        if df.empty:
            return False
        
        required_columns = ['Close']
        if not all(col in df.columns for col in required_columns):
            log.warning(f"Missing required columns. Required: {required_columns}, Got: {df.columns.tolist()}")
            return False
        
        # Check for sufficient data points
        if len(df) < 2:
            log.warning("Insufficient data points for analysis")
            return False
        
        return True
