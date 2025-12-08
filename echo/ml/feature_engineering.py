"""
Feature engineering utilities for financial data.

Provides functions to calculate technical indicators and prepare features
for machine learning models.
"""

from __future__ import annotations
from typing import Optional
import pandas as pd
import numpy as np


class FeatureEngineer:
    """
    Feature engineering for financial time series data.
    
    Calculates technical indicators like RSI, MACD, Bollinger Bands,
    and other features useful for trading models.
    """
    
    @staticmethod
    def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI).
        
        Args:
            data: Price series (typically Close prices)
            period: RSI period (default 14)
            
        Returns:
            Series with RSI values
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_macd(data: pd.Series, 
                      fast_period: int = 12, 
                      slow_period: int = 26, 
                      signal_period: int = 9) -> pd.DataFrame:
        """
        Calculate Moving Average Convergence Divergence (MACD).
        
        Args:
            data: Price series (typically Close prices)
            fast_period: Fast EMA period
            slow_period: Slow EMA period
            signal_period: Signal line period
            
        Returns:
            DataFrame with MACD, Signal, and Histogram columns
        """
        ema_fast = data.ewm(span=fast_period, adjust=False).mean()
        ema_slow = data.ewm(span=slow_period, adjust=False).mean()
        
        macd = ema_fast - ema_slow
        signal = macd.ewm(span=signal_period, adjust=False).mean()
        histogram = macd - signal
        
        return pd.DataFrame({
            'MACD': macd,
            'Signal': signal,
            'Histogram': histogram
        })
    
    @staticmethod
    def calculate_bollinger_bands(data: pd.Series, 
                                 period: int = 20, 
                                 num_std: float = 2.0) -> pd.DataFrame:
        """
        Calculate Bollinger Bands.
        
        Args:
            data: Price series (typically Close prices)
            period: Moving average period
            num_std: Number of standard deviations for bands
            
        Returns:
            DataFrame with Upper, Middle, and Lower band columns
        """
        sma = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()
        
        upper_band = sma + (std * num_std)
        lower_band = sma - (std * num_std)
        
        return pd.DataFrame({
            'BB_Upper': upper_band,
            'BB_Middle': sma,
            'BB_Lower': lower_band
        })
    
    @staticmethod
    def calculate_moving_averages(data: pd.Series, 
                                 periods: list = [5, 10, 20, 50, 200]) -> pd.DataFrame:
        """
        Calculate multiple Simple Moving Averages (SMA).
        
        Args:
            data: Price series
            periods: List of periods for moving averages
            
        Returns:
            DataFrame with SMA columns
        """
        result = pd.DataFrame()
        for period in periods:
            result[f'SMA_{period}'] = data.rolling(window=period).mean()
        return result
    
    @staticmethod
    def calculate_momentum(data: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate price momentum.
        
        Args:
            data: Price series
            period: Lookback period
            
        Returns:
            Series with momentum values
        """
        return data.diff(period)
    
    @staticmethod
    def calculate_volatility(data: pd.Series, period: int = 20) -> pd.Series:
        """
        Calculate rolling volatility (standard deviation).
        
        Args:
            data: Returns series
            period: Rolling window period
            
        Returns:
            Series with volatility values
        """
        return data.rolling(window=period).std()
    
    @staticmethod
    def calculate_returns(data: pd.Series, period: int = 1) -> pd.Series:
        """
        Calculate returns over a specified period.
        
        Args:
            data: Price series
            period: Return period (1 for daily returns)
            
        Returns:
            Series with return values
        """
        return data.pct_change(periods=period)
    
    def engineer_features(self, df: pd.DataFrame, 
                         price_col: str = 'Close',
                         volume_col: str = 'Volume') -> pd.DataFrame:
        """
        Generate comprehensive feature set from OHLCV data.
        
        Args:
            df: DataFrame with OHLCV data
            price_col: Name of price column
            volume_col: Name of volume column
            
        Returns:
            DataFrame with engineered features
        """
        result = df.copy()
        
        # Technical indicators
        result['RSI'] = self.calculate_rsi(df[price_col])
        
        macd_df = self.calculate_macd(df[price_col])
        result = pd.concat([result, macd_df], axis=1)
        
        bb_df = self.calculate_bollinger_bands(df[price_col])
        result = pd.concat([result, bb_df], axis=1)
        
        sma_df = self.calculate_moving_averages(df[price_col])
        result = pd.concat([result, sma_df], axis=1)
        
        # Returns and momentum
        result['Returns'] = self.calculate_returns(df[price_col])
        result['Momentum'] = self.calculate_momentum(df[price_col])
        
        # Volatility
        result['Volatility'] = self.calculate_volatility(result['Returns'])
        
        # Volume features (if available)
        if volume_col in df.columns:
            result['Volume_SMA_20'] = df[volume_col].rolling(window=20).mean()
            result['Volume_Ratio'] = df[volume_col] / result['Volume_SMA_20']
        
        return result
