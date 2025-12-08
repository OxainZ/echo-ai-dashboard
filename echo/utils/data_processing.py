"""
Data Processing Utilities

Provides utilities for cleaning, normalizing, and engineering features
from raw market data. These utilities ensure data quality and prepare
datasets for ML model training and inference.

Key Features:
- Missing value handling
- Outlier detection and treatment
- Technical indicator calculation
- Feature scaling and normalization
- Data validation
"""
from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta


class DataCleaner:
    """
    Handles data cleaning and preprocessing for market data
    
    Provides methods to:
    - Fill missing values
    - Remove or cap outliers
    - Validate data quality
    - Interpolate gaps
    """
    
    @staticmethod
    def handle_missing_values(
        df: pd.DataFrame,
        method: str = 'ffill',
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Handle missing values in time-series data
        
        Args:
            df: DataFrame with potential missing values
            method: Method to use - 'ffill', 'bfill', 'interpolate', 'drop'
            limit: Maximum number of consecutive NaNs to fill
            
        Returns:
            DataFrame with missing values handled
        """
        df_clean = df.copy()
        
        if method == 'ffill':
            # Forward fill - use last known value
            df_clean = df_clean.ffill(limit=limit)
        elif method == 'bfill':
            # Backward fill - use next known value
            df_clean = df_clean.bfill(limit=limit)
        elif method == 'interpolate':
            # Linear interpolation
            df_clean = df_clean.interpolate(method='linear', limit=limit)
        elif method == 'drop':
            # Drop rows with any missing values
            df_clean = df_clean.dropna()
        else:
            raise ValueError(f"Unknown method: {method}")
        
        return df_clean
    
    @staticmethod
    def detect_outliers(
        series: pd.Series,
        method: str = 'iqr',
        threshold: float = 3.0
    ) -> pd.Series:
        """
        Detect outliers in a data series
        
        Args:
            series: Data series to check
            method: Detection method - 'iqr' or 'zscore'
            threshold: Threshold for outlier detection
            
        Returns:
            Boolean series indicating outliers
        """
        if method == 'iqr':
            # Interquartile range method
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            return (series < lower_bound) | (series > upper_bound)
        
        elif method == 'zscore':
            # Z-score method
            z_scores = np.abs((series - series.mean()) / series.std())
            return z_scores > threshold
        
        else:
            raise ValueError(f"Unknown method: {method}")
    
    @staticmethod
    def remove_outliers(
        df: pd.DataFrame,
        columns: List[str],
        method: str = 'iqr',
        action: str = 'cap'
    ) -> pd.DataFrame:
        """
        Remove or cap outliers in specified columns
        
        Args:
            df: DataFrame to process
            columns: List of columns to check for outliers
            method: Outlier detection method
            action: 'cap' to limit outliers or 'remove' to drop rows
            
        Returns:
            DataFrame with outliers handled
        """
        df_clean = df.copy()
        
        for col in columns:
            if col not in df_clean.columns:
                continue
            
            outliers = DataCleaner.detect_outliers(df_clean[col], method=method)
            
            if action == 'cap':
                # Cap outliers at threshold values
                Q1 = df_clean[col].quantile(0.25)
                Q3 = df_clean[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 3 * IQR
                upper_bound = Q3 + 3 * IQR
                
                df_clean.loc[df_clean[col] < lower_bound, col] = lower_bound
                df_clean.loc[df_clean[col] > upper_bound, col] = upper_bound
            
            elif action == 'remove':
                # Remove rows with outliers
                df_clean = df_clean[~outliers]
        
        return df_clean
    
    @staticmethod
    def validate_ohlcv(df: pd.DataFrame) -> Dict[str, bool]:
        """
        Validate OHLCV data quality
        
        Args:
            df: DataFrame with OHLCV columns
            
        Returns:
            Dict with validation results
        """
        results = {}
        
        # Check required columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        results['has_required_columns'] = all(
            col in df.columns for col in required_cols
        )
        
        if not results['has_required_columns']:
            return results
        
        # Check High >= Low
        results['high_gte_low'] = (df['High'] >= df['Low']).all()
        
        # Check High >= Open, Close
        results['high_valid'] = (
            (df['High'] >= df['Open']).all() and
            (df['High'] >= df['Close']).all()
        )
        
        # Check Low <= Open, Close
        results['low_valid'] = (
            (df['Low'] <= df['Open']).all() and
            (df['Low'] <= df['Close']).all()
        )
        
        # Check for negative values
        results['no_negative_prices'] = (df[['Open', 'High', 'Low', 'Close']] >= 0).all().all()
        results['no_negative_volume'] = (df['Volume'] >= 0).all()
        
        # Check for missing values
        results['no_missing_values'] = not df[required_cols].isnull().any().any()
        
        # Overall validation
        results['is_valid'] = all([
            results['has_required_columns'],
            results['high_gte_low'],
            results['high_valid'],
            results['low_valid'],
            results['no_negative_prices'],
            results['no_negative_volume']
        ])
        
        return results


class FeatureEngine:
    """
    Creates technical indicators and features for ML models
    
    Calculates:
    - Moving averages
    - Momentum indicators
    - Volatility measures
    - Volume indicators
    """
    
    @staticmethod
    def add_moving_averages(
        df: pd.DataFrame,
        windows: List[int] = None
    ) -> pd.DataFrame:
        """
        Add simple and exponential moving averages
        
        Args:
            df: DataFrame with Close prices
            windows: List of window sizes (default: [5, 10, 20, 50])
            
        Returns:
            DataFrame with MA columns added
        """
        if windows is None:
            windows = [5, 10, 20, 50]
        
        df_feat = df.copy()
        
        for window in windows:
            # Simple moving average
            df_feat[f'SMA_{window}'] = df_feat['Close'].rolling(window=window).mean()
            
            # Exponential moving average
            df_feat[f'EMA_{window}'] = df_feat['Close'].ewm(span=window, adjust=False).mean()
        
        return df_feat
    
    @staticmethod
    def add_momentum_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add momentum-based technical indicators
        
        Args:
            df: DataFrame with OHLC data
            
        Returns:
            DataFrame with momentum indicators added
        """
        df_feat = df.copy()
        
        # Rate of Change (ROC)
        df_feat['ROC_10'] = df_feat['Close'].pct_change(periods=10) * 100
        
        # Relative Strength Index (RSI)
        delta = df_feat['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df_feat['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema_12 = df_feat['Close'].ewm(span=12, adjust=False).mean()
        ema_26 = df_feat['Close'].ewm(span=26, adjust=False).mean()
        df_feat['MACD'] = ema_12 - ema_26
        df_feat['MACD_Signal'] = df_feat['MACD'].ewm(span=9, adjust=False).mean()
        df_feat['MACD_Hist'] = df_feat['MACD'] - df_feat['MACD_Signal']
        
        return df_feat
    
    @staticmethod
    def add_volatility_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add volatility-based indicators
        
        Args:
            df: DataFrame with OHLC data
            
        Returns:
            DataFrame with volatility indicators added
        """
        df_feat = df.copy()
        
        # Bollinger Bands
        sma_20 = df_feat['Close'].rolling(window=20).mean()
        std_20 = df_feat['Close'].rolling(window=20).std()
        df_feat['BB_Upper'] = sma_20 + (2 * std_20)
        df_feat['BB_Middle'] = sma_20
        df_feat['BB_Lower'] = sma_20 - (2 * std_20)
        df_feat['BB_Width'] = (df_feat['BB_Upper'] - df_feat['BB_Lower']) / df_feat['BB_Middle']
        
        # Average True Range (ATR)
        high_low = df_feat['High'] - df_feat['Low']
        high_close = np.abs(df_feat['High'] - df_feat['Close'].shift())
        low_close = np.abs(df_feat['Low'] - df_feat['Close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df_feat['ATR'] = tr.rolling(window=14).mean()
        
        # Historical Volatility
        df_feat['Volatility_20'] = df_feat['Close'].pct_change().rolling(window=20).std() * np.sqrt(252)
        
        return df_feat
    
    @staticmethod
    def add_volume_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add volume-based indicators
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with volume indicators added
        """
        df_feat = df.copy()
        
        # Volume moving average
        df_feat['Volume_MA_20'] = df_feat['Volume'].rolling(window=20).mean()
        df_feat['Volume_Ratio'] = df_feat['Volume'] / df_feat['Volume_MA_20']
        
        # On-Balance Volume (OBV)
        obv = [0]
        for i in range(1, len(df_feat)):
            if df_feat['Close'].iloc[i] > df_feat['Close'].iloc[i - 1]:
                obv.append(obv[-1] + df_feat['Volume'].iloc[i])
            elif df_feat['Close'].iloc[i] < df_feat['Close'].iloc[i - 1]:
                obv.append(obv[-1] - df_feat['Volume'].iloc[i])
            else:
                obv.append(obv[-1])
        df_feat['OBV'] = obv
        
        # Volume Price Trend (VPT)
        df_feat['VPT'] = (df_feat['Volume'] * df_feat['Close'].pct_change()).cumsum()
        
        return df_feat
    
    @staticmethod
    def create_all_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Create comprehensive feature set
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with all features added
        """
        df_feat = df.copy()
        
        # Add all feature types
        df_feat = FeatureEngine.add_moving_averages(df_feat)
        df_feat = FeatureEngine.add_momentum_indicators(df_feat)
        df_feat = FeatureEngine.add_volatility_indicators(df_feat)
        df_feat = FeatureEngine.add_volume_indicators(df_feat)
        
        # Drop NaN rows created by indicators
        df_feat = df_feat.dropna()
        
        return df_feat


def prepare_ml_dataset(
    df: pd.DataFrame,
    clean_data: bool = True,
    add_features: bool = True
) -> pd.DataFrame:
    """
    Prepare dataset for machine learning
    
    Args:
        df: Raw OHLCV DataFrame
        clean_data: Whether to clean data
        add_features: Whether to add technical features
        
    Returns:
        Cleaned and feature-engineered DataFrame
    """
    # Clean data
    if clean_data:
        df = DataCleaner.handle_missing_values(df, method='ffill')
        df = DataCleaner.remove_outliers(
            df,
            columns=['Open', 'High', 'Low', 'Close', 'Volume'],
            action='cap'
        )
    
    # Add features
    if add_features:
        df = FeatureEngine.create_all_features(df)
    
    return df
