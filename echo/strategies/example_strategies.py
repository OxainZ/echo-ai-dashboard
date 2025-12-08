"""
Example trading strategies.

Demonstrates how to implement various trading strategies.
"""

from __future__ import annotations
import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy, PositionType
from .risk_manager import PositionSizer
from ..ml.feature_engineering import FeatureEngineer


class MomentumStrategy(BaseStrategy):
    """
    Simple momentum trading strategy.
    
    Buys when price is above moving average and momentum is positive.
    Sells when price falls below moving average.
    """
    
    def __init__(self, sma_period: int = 20, momentum_period: int = 10,
                 initial_capital: float = 100000, position_size_pct: float = 20):
        super().__init__("Momentum_Strategy", initial_capital)
        self.sma_period = sma_period
        self.momentum_period = momentum_period
        self.position_size_pct = position_size_pct
        self.engineer = FeatureEngineer()
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate buy/sell signals based on momentum.
        
        Args:
            data: DataFrame with 'Close' prices
            
        Returns:
            Series with signals (1: buy, -1: sell, 0: hold)
        """
        # Calculate indicators
        sma = data['Close'].rolling(window=self.sma_period).mean()
        momentum = self.engineer.calculate_momentum(data['Close'], self.momentum_period)
        
        # Generate signals
        signals = pd.Series(0, index=data.index)
        
        # Buy when price > SMA and momentum > 0
        buy_condition = (data['Close'] > sma) & (momentum > 0)
        signals[buy_condition] = 1
        
        # Sell when price < SMA
        sell_condition = data['Close'] < sma
        signals[sell_condition] = -1
        
        return signals
    
    def calculate_position_size(self, ticker: str, signal: int, 
                                current_price: float, data: pd.DataFrame) -> float:
        """Calculate position size as fixed percentage of capital."""
        return PositionSizer.fixed_percent(
            self.capital, 
            self.position_size_pct, 
            current_price
        )


class MeanReversionStrategy(BaseStrategy):
    """
    Mean reversion strategy using Bollinger Bands.
    
    Buys when price touches lower band (oversold).
    Sells when price touches upper band (overbought).
    """
    
    def __init__(self, bb_period: int = 20, bb_std: float = 2.0,
                 initial_capital: float = 100000, position_size_pct: float = 20):
        super().__init__("Mean_Reversion_Strategy", initial_capital)
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.position_size_pct = position_size_pct
        self.engineer = FeatureEngineer()
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate signals based on Bollinger Bands.
        
        Args:
            data: DataFrame with 'Close' prices
            
        Returns:
            Series with signals (1: buy, -1: sell, 0: hold)
        """
        # Calculate Bollinger Bands
        bb = self.engineer.calculate_bollinger_bands(
            data['Close'], 
            period=self.bb_period,
            num_std=self.bb_std
        )
        
        signals = pd.Series(0, index=data.index)
        
        # Buy when price touches lower band (oversold)
        buy_condition = data['Close'] <= bb['BB_Lower']
        signals[buy_condition] = 1
        
        # Sell when price touches upper band (overbought)
        sell_condition = data['Close'] >= bb['BB_Upper']
        signals[sell_condition] = -1
        
        return signals
    
    def calculate_position_size(self, ticker: str, signal: int, 
                                current_price: float, data: pd.DataFrame) -> float:
        """Calculate position size as fixed percentage of capital."""
        return PositionSizer.fixed_percent(
            self.capital,
            self.position_size_pct,
            current_price
        )


class RSIStrategy(BaseStrategy):
    """
    RSI-based strategy.
    
    Buys when RSI < 30 (oversold).
    Sells when RSI > 70 (overbought).
    """
    
    def __init__(self, rsi_period: int = 14, oversold: float = 30, overbought: float = 70,
                 initial_capital: float = 100000, position_size_pct: float = 20):
        super().__init__("RSI_Strategy", initial_capital)
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought
        self.position_size_pct = position_size_pct
        self.engineer = FeatureEngineer()
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate signals based on RSI.
        
        Args:
            data: DataFrame with 'Close' prices
            
        Returns:
            Series with signals (1: buy, -1: sell, 0: hold)
        """
        # Calculate RSI
        rsi = self.engineer.calculate_rsi(data['Close'], period=self.rsi_period)
        
        signals = pd.Series(0, index=data.index)
        
        # Buy when oversold
        signals[rsi < self.oversold] = 1
        
        # Sell when overbought
        signals[rsi > self.overbought] = -1
        
        return signals
    
    def calculate_position_size(self, ticker: str, signal: int, 
                                current_price: float, data: pd.DataFrame) -> float:
        """Calculate position size as fixed percentage of capital."""
        return PositionSizer.fixed_percent(
            self.capital,
            self.position_size_pct,
            current_price
        )


class MACDStrategy(BaseStrategy):
    """
    MACD crossover strategy.
    
    Buys when MACD crosses above signal line.
    Sells when MACD crosses below signal line.
    """
    
    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9,
                 initial_capital: float = 100000, position_size_pct: float = 20):
        super().__init__("MACD_Strategy", initial_capital)
        self.fast = fast
        self.slow = slow
        self.signal_period = signal
        self.position_size_pct = position_size_pct
        self.engineer = FeatureEngineer()
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate signals based on MACD crossovers.
        
        Args:
            data: DataFrame with 'Close' prices
            
        Returns:
            Series with signals (1: buy, -1: sell, 0: hold)
        """
        # Calculate MACD
        macd_df = self.engineer.calculate_macd(
            data['Close'],
            fast_period=self.fast,
            slow_period=self.slow,
            signal_period=self.signal_period
        )
        
        signals = pd.Series(0, index=data.index)
        
        # Previous values for crossover detection
        macd_prev = macd_df['MACD'].shift(1)
        signal_prev = macd_df['Signal'].shift(1)
        
        # Buy on bullish crossover (MACD crosses above signal)
        bullish_cross = (macd_df['MACD'] > macd_df['Signal']) & (macd_prev <= signal_prev)
        signals[bullish_cross] = 1
        
        # Sell on bearish crossover (MACD crosses below signal)
        bearish_cross = (macd_df['MACD'] < macd_df['Signal']) & (macd_prev >= signal_prev)
        signals[bearish_cross] = -1
        
        return signals
    
    def calculate_position_size(self, ticker: str, signal: int, 
                                current_price: float, data: pd.DataFrame) -> float:
        """Calculate position size as fixed percentage of capital."""
        return PositionSizer.fixed_percent(
            self.capital,
            self.position_size_pct,
            current_price
        )
