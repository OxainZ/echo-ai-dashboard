"""
Data Preprocessing for Machine Learning

This module provides utilities for preprocessing financial data
before feeding it to ML models.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class FinancialDataPreprocessor:
    """
    Preprocessor for financial time series data.
    
    Handles:
    - Missing value imputation
    - Feature engineering (technical indicators)
    - Normalization and scaling
    - Train/test splitting with temporal ordering
    - Lag feature creation
    """
    
    def __init__(self, lookback_window: int = 60, forecast_horizon: int = 1):
        """
        Initialize the preprocessor.
        
        Args:
            lookback_window: Number of historical days to use as features
            forecast_horizon: Number of days ahead to predict
        """
        self.lookback_window = lookback_window
        self.forecast_horizon = forecast_horizon
        self.feature_stats: Dict = {}
        
    def add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add technical indicators to the dataframe.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with additional technical indicator columns
        """
        df = df.copy()
        
        # Simple Moving Averages
        df['SMA_5'] = df['Close'].rolling(window=5).mean()
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        # Exponential Moving Averages
        df['EMA_12'] = df['Close'].ewm(span=12).mean()
        df['EMA_26'] = df['Close'].ewm(span=26).mean()
        
        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        
        # RSI (Relative Strength Index)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        
        # Volume indicators
        df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
        
        # Price momentum
        df['Returns'] = df['Close'].pct_change()
        df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))
        
        # Volatility
        df['Volatility'] = df['Returns'].rolling(window=20).std()
        
        return df
    
    def create_sequences(self, data: np.ndarray, target: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create sequences for time series prediction.
        
        Args:
            data: Input feature array
            target: Target variable array
            
        Returns:
            Tuple of (X, y) where X is sequences and y is targets
        """
        X, y = [], []
        
        for i in range(len(data) - self.lookback_window - self.forecast_horizon + 1):
            X.append(data[i:(i + self.lookback_window)])
            y.append(target[i + self.lookback_window + self.forecast_horizon - 1])
            
        return np.array(X), np.array(y)
    
    def normalize_features(self, df: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """
        Normalize features using min-max scaling.
        
        Args:
            df: DataFrame to normalize
            fit: Whether to fit the scaler (True for training data)
            
        Returns:
            Normalized DataFrame
        """
        df = df.copy()
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if fit:
            # Store statistics for inverse transform
            self.feature_stats = {}
            for col in numeric_cols:
                self.feature_stats[col] = {
                    'min': df[col].min(),
                    'max': df[col].max()
                }
        
        # Normalize
        for col in numeric_cols:
            if col in self.feature_stats:
                min_val = self.feature_stats[col]['min']
                max_val = self.feature_stats[col]['max']
                if max_val != min_val:
                    df[col] = (df[col] - min_val) / (max_val - min_val)
                    
        return df
    
    def handle_missing_values(self, df: pd.DataFrame, method: str = 'ffill') -> pd.DataFrame:
        """
        Handle missing values in the dataset.
        
        Args:
            df: DataFrame with potential missing values
            method: Method to use ('ffill', 'bfill', 'interpolate')
            
        Returns:
            DataFrame with missing values handled
        """
        df = df.copy()
        
        if method == 'ffill':
            df = df.fillna(method='ffill')
        elif method == 'bfill':
            df = df.fillna(method='bfill')
        elif method == 'interpolate':
            df = df.interpolate(method='linear')
        else:
            raise ValueError(f"Unknown method: {method}")
            
        # Fill any remaining NaN with 0
        df = df.fillna(0)
        
        return df
    
    def split_train_test(self, df: pd.DataFrame, test_size: float = 0.2) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Split data into train and test sets preserving temporal order.
        
        Args:
            df: DataFrame to split
            test_size: Proportion of data to use for testing
            
        Returns:
            Tuple of (train_df, test_df)
        """
        split_idx = int(len(df) * (1 - test_size))
        
        train_df = df.iloc[:split_idx].copy()
        test_df = df.iloc[split_idx:].copy()
        
        return train_df, test_df
    
    def preprocess_for_training(self, df: pd.DataFrame, target_col: str = 'Close') -> Dict:
        """
        Complete preprocessing pipeline for training.
        
        Args:
            df: Raw OHLCV DataFrame
            target_col: Column to predict
            
        Returns:
            Dictionary with preprocessed data and metadata
        """
        # Add technical indicators
        df_features = self.add_technical_indicators(df)
        
        # Handle missing values
        df_features = self.handle_missing_values(df_features)
        
        # Split train/test
        train_df, test_df = self.split_train_test(df_features)
        
        # Normalize features
        train_norm = self.normalize_features(train_df, fit=True)
        test_norm = self.normalize_features(test_df, fit=False)
        
        return {
            'train_data': train_norm,
            'test_data': test_norm,
            'feature_names': train_norm.columns.tolist(),
            'target_col': target_col,
            'train_size': len(train_norm),
            'test_size': len(test_norm)
        }


class FeatureEngineer:
    """
    Advanced feature engineering for financial data.
    """
    
    @staticmethod
    def add_lagged_features(df: pd.DataFrame, columns: List[str], lags: List[int]) -> pd.DataFrame:
        """
        Add lagged versions of specified columns.
        
        Args:
            df: Input DataFrame
            columns: Columns to create lags for
            lags: List of lag periods
            
        Returns:
            DataFrame with lagged features
        """
        df = df.copy()
        
        for col in columns:
            for lag in lags:
                df[f'{col}_lag_{lag}'] = df[col].shift(lag)
                
        return df
    
    @staticmethod
    def add_rolling_statistics(df: pd.DataFrame, column: str, windows: List[int]) -> pd.DataFrame:
        """
        Add rolling statistics (mean, std, min, max) for a column.
        
        Args:
            df: Input DataFrame
            column: Column to compute statistics for
            windows: List of window sizes
            
        Returns:
            DataFrame with rolling statistics
        """
        df = df.copy()
        
        for window in windows:
            df[f'{column}_rolling_mean_{window}'] = df[column].rolling(window).mean()
            df[f'{column}_rolling_std_{window}'] = df[column].rolling(window).std()
            df[f'{column}_rolling_min_{window}'] = df[column].rolling(window).min()
            df[f'{column}_rolling_max_{window}'] = df[column].rolling(window).max()
            
        return df
    
    @staticmethod
    def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add time-based features (day of week, month, quarter, etc.).
        
        Args:
            df: DataFrame with DatetimeIndex
            
        Returns:
            DataFrame with time features
        """
        df = df.copy()
        
        if isinstance(df.index, pd.DatetimeIndex):
            df['day_of_week'] = df.index.dayofweek
            df['day_of_month'] = df.index.day
            df['month'] = df.index.month
            df['quarter'] = df.index.quarter
            df['is_month_start'] = df.index.is_month_start.astype(int)
            df['is_month_end'] = df.index.is_month_end.astype(int)
            
        return df
