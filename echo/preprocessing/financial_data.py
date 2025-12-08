"""
Data Preprocessing Module

Provides data cleaning, normalization, and feature engineering for financial data.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class FinancialDataPreprocessor:
    """
    Preprocessing pipeline for financial time series data
    
    Features:
    - Data cleaning and validation
    - Missing value handling
    - Feature engineering (technical indicators)
    - Data normalization
    - Train/test splitting with temporal awareness
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.feature_columns = []
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean financial data
        
        Args:
            df: Raw dataframe with OHLCV data
            
        Returns:
            Cleaned dataframe
        """
        df = df.copy()
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Sort by date
        if df.index.name == 'Date' or 'Date' in df.columns:
            df = df.sort_index() if df.index.name == 'Date' else df.sort_values('Date')
        
        # Handle missing values
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        # Forward fill first, then backward fill
        df[numeric_cols] = df[numeric_cols].ffill().bfill()
        
        # Drop rows with remaining NaN values
        df = df.dropna()
        
        # Remove invalid values (negative prices, zero volume)
        if 'Close' in df.columns:
            df = df[df['Close'] > 0]
        if 'Volume' in df.columns:
            df = df[df['Volume'] >= 0]
        
        return df
    
    def add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add technical indicators as features
        
        Args:
            df: Dataframe with OHLCV data
            
        Returns:
            Dataframe with additional technical indicators
        """
        df = df.copy()
        
        # Price-based indicators
        df['Returns'] = df['Close'].pct_change()
        df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))
        
        # Moving Averages
        df['SMA_5'] = df['Close'].rolling(window=5).mean()
        df['SMA_10'] = df['Close'].rolling(window=10).mean()
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        # Exponential Moving Averages
        df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
        
        # MACD (Moving Average Convergence Divergence)
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
        
        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        df['BB_Width'] = df['BB_Upper'] - df['BB_Lower']
        df['BB_Position'] = (df['Close'] - df['BB_Lower']) / df['BB_Width']
        
        # RSI (Relative Strength Index)
        df['RSI'] = self._calculate_rsi(df['Close'], period=14)
        
        # Stochastic Oscillator
        df['Stochastic_K'], df['Stochastic_D'] = self._calculate_stochastic(df)
        
        # Average True Range (ATR) - Volatility
        df['ATR'] = self._calculate_atr(df, period=14)
        
        # On-Balance Volume (OBV)
        if 'Volume' in df.columns:
            df['OBV'] = self._calculate_obv(df)
            
            # Volume indicators
            df['Volume_SMA_20'] = df['Volume'].rolling(window=20).mean()
            df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA_20']
        
        # Price momentum
        df['Momentum_5'] = df['Close'] - df['Close'].shift(5)
        df['Momentum_10'] = df['Close'] - df['Close'].shift(10)
        
        # Rate of Change
        df['ROC_5'] = ((df['Close'] - df['Close'].shift(5)) / df['Close'].shift(5)) * 100
        df['ROC_10'] = ((df['Close'] - df['Close'].shift(10)) / df['Close'].shift(10)) * 100
        
        # High-Low spread
        if 'High' in df.columns and 'Low' in df.columns:
            df['HL_Spread'] = df['High'] - df['Low']
            df['HL_Spread_Pct'] = (df['HL_Spread'] / df['Close']) * 100
        
        # Drop NaN values created by indicators
        df = df.dropna()
        
        return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_stochastic(self, df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
        """Calculate Stochastic Oscillator"""
        low_min = df['Low'].rolling(window=k_period).min()
        high_max = df['High'].rolling(window=k_period).max()
        
        stochastic_k = 100 * (df['Close'] - low_min) / (high_max - low_min)
        stochastic_d = stochastic_k.rolling(window=d_period).mean()
        
        return stochastic_k, stochastic_d
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        
        return atr
    
    def _calculate_obv(self, df: pd.DataFrame) -> pd.Series:
        """Calculate On-Balance Volume"""
        obv = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()
        return obv
    
    def prepare_features(self, df: pd.DataFrame, target_col: str = 'Close') -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare features and target for model training
        
        Args:
            df: Dataframe with all indicators
            target_col: Column to use as target
            
        Returns:
            X: Feature dataframe
            y: Target series
        """
        # Define feature columns (exclude target and date columns)
        exclude_cols = [target_col, 'Date', 'Open', 'High', 'Low', 'Volume', 'Dividends', 'Stock Splits']
        self.feature_columns = [col for col in df.columns if col not in exclude_cols and col in df.columns]
        
        X = df[self.feature_columns].copy()
        y = df[target_col].copy()
        
        return X, y
    
    def normalize_features(self, X: pd.DataFrame, scaler=None) -> Tuple[np.ndarray, any]:
        """
        Normalize features using Min-Max scaling
        
        Args:
            X: Feature dataframe
            scaler: Pre-fitted scaler (optional)
            
        Returns:
            Normalized features, fitted scaler
        """
        from sklearn.preprocessing import MinMaxScaler
        
        if scaler is None:
            scaler = MinMaxScaler()
            X_scaled = scaler.fit_transform(X)
        else:
            X_scaled = scaler.transform(X)
        
        return X_scaled, scaler
    
    def temporal_train_test_split(self, df: pd.DataFrame, test_size: float = 0.2) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Split data into train and test sets maintaining temporal order
        
        Args:
            df: Dataframe to split
            test_size: Proportion of data for testing
            
        Returns:
            train_df, test_df
        """
        split_idx = int(len(df) * (1 - test_size))
        train_df = df.iloc[:split_idx].copy()
        test_df = df.iloc[split_idx:].copy()
        
        return train_df, test_df
    
    def process_pipeline(self, df: pd.DataFrame, add_indicators: bool = True) -> pd.DataFrame:
        """
        Run complete preprocessing pipeline
        
        Args:
            df: Raw dataframe
            add_indicators: Whether to add technical indicators
            
        Returns:
            Processed dataframe
        """
        # Clean data
        df = self.clean_data(df)
        
        # Add technical indicators
        if add_indicators:
            df = self.add_technical_indicators(df)
        
        return df
    
    def get_feature_importance_data(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Categorize features for importance analysis
        
        Returns:
            Dictionary of feature categories
        """
        categories = {
            'price_based': ['Returns', 'Log_Returns', 'Momentum_5', 'Momentum_10'],
            'moving_averages': ['SMA_5', 'SMA_10', 'SMA_20', 'SMA_50', 'EMA_12', 'EMA_26'],
            'momentum_indicators': ['RSI', 'MACD', 'MACD_Signal', 'MACD_Hist', 'Stochastic_K', 'Stochastic_D'],
            'volatility_indicators': ['BB_Width', 'BB_Position', 'ATR', 'HL_Spread', 'HL_Spread_Pct'],
            'volume_indicators': ['OBV', 'Volume_Ratio'],
            'rate_of_change': ['ROC_5', 'ROC_10']
        }
        
        # Filter to only include columns that exist in df
        available_categories = {}
        for cat, features in categories.items():
            available_features = [f for f in features if f in df.columns]
            if available_features:
                available_categories[cat] = available_features
        
        return available_categories
