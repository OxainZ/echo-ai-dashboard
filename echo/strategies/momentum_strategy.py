"""
Momentum Trading Strategy

Implements a momentum-based trading strategy that identifies and trades
stocks showing strong directional movement. The strategy buys assets
with positive momentum and sells those with negative momentum.

Key Features:
- Rate of Change (ROC) momentum indicator
- Moving average crossover signals
- Relative Strength Index (RSI) filtering
- Dynamic position sizing based on momentum strength
"""
from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Dict
from .base_strategy import BaseStrategy, RiskManager


class MomentumStrategy(BaseStrategy):
    """
    Momentum-based trading strategy
    
    Buys stocks when momentum indicators show strength and sells
    when momentum weakens or reverses.
    
    Signals:
    - BUY: ROC > threshold AND price > MA AND RSI < overbought
    - SELL: ROC < -threshold OR price < MA OR RSI > overbought
    """
    
    def __init__(
        self,
        name: str = "Momentum Strategy",
        initial_capital: float = 100000.0,
        lookback_period: int = 20,
        roc_threshold: float = 2.0,
        ma_period: int = 50,
        rsi_period: int = 14,
        rsi_overbought: float = 70,
        rsi_oversold: float = 30,
        risk_manager: RiskManager = None
    ):
        """
        Initialize momentum strategy
        
        Args:
            name: Strategy name
            initial_capital: Starting capital
            lookback_period: Period for momentum calculation
            roc_threshold: Minimum ROC% for signal
            ma_period: Moving average period
            rsi_period: RSI calculation period
            rsi_overbought: RSI overbought threshold
            rsi_oversold: RSI oversold threshold
            risk_manager: Risk management configuration
        """
        super().__init__(name, initial_capital, risk_manager)
        self.lookback_period = lookback_period
        self.roc_threshold = roc_threshold
        self.ma_period = ma_period
        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold
    
    def calculate_roc(self, prices: pd.Series, period: int) -> pd.Series:
        """
        Calculate Rate of Change
        
        Args:
            prices: Price series
            period: Lookback period
            
        Returns:
            ROC series
        """
        return ((prices - prices.shift(period)) / prices.shift(period)) * 100
    
    def calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """
        Calculate Relative Strength Index
        
        Args:
            prices: Price series
            period: RSI period
            
        Returns:
            RSI series
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate momentum-based trading signals
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with 'signal' column (1=buy, -1=sell, 0=hold)
        """
        df = data.copy()
        
        # Calculate indicators
        df['ROC'] = self.calculate_roc(df['Close'], self.lookback_period)
        df['MA'] = df['Close'].rolling(window=self.ma_period).mean()
        df['RSI'] = self.calculate_rsi(df['Close'], self.rsi_period)
        
        # Initialize signal column
        df['signal'] = 0
        
        # Generate buy signals
        buy_condition = (
            (df['ROC'] > self.roc_threshold) &
            (df['Close'] > df['MA']) &
            (df['RSI'] < self.rsi_overbought) &
            (df['RSI'] > self.rsi_oversold)
        )
        df.loc[buy_condition, 'signal'] = 1
        
        # Generate sell signals
        sell_condition = (
            (df['ROC'] < -self.roc_threshold) |
            (df['Close'] < df['MA']) |
            (df['RSI'] > self.rsi_overbought)
        )
        df.loc[sell_condition, 'signal'] = -1
        
        # Add momentum strength for position sizing
        df['momentum_strength'] = df['ROC'].abs() / 10.0  # Normalize
        
        return df
    
    def backtest(self, data: pd.DataFrame, symbol: str) -> Dict:
        """
        Backtest strategy on historical data
        
        Args:
            data: Historical OHLCV data
            symbol: Stock ticker
            
        Returns:
            Dict with backtest results
        """
        # Generate signals
        df = self.generate_signals(data)
        
        # Execute trades based on signals
        position_open = False
        
        for i in range(self.ma_period, len(df)):
            row = df.iloc[i]
            timestamp = df.index[i]
            price = row['Close']
            signal = row['signal']
            
            # Update position prices
            self.update_positions({symbol: price})
            
            # Check risk management
            self.check_risk_management()
            
            # Execute signals
            if signal == 1 and not position_open:
                # Buy signal
                quantity = self.risk_manager.calculate_position_size(
                    self.portfolio_value,
                    price,
                    volatility=row.get('momentum_strength', 0.5)
                )
                
                if self.execute_trade(
                    symbol, 'BUY', quantity, price, timestamp,
                    f"Momentum buy: ROC={row['ROC']:.2f}%"
                ):
                    position_open = True
            
            elif signal == -1 and position_open:
                # Sell signal
                if symbol in self.positions:
                    quantity = self.positions[symbol].quantity
                    if self.execute_trade(
                        symbol, 'SELL', quantity, price, timestamp,
                        f"Momentum sell: ROC={row['ROC']:.2f}%"
                    ):
                        position_open = False
        
        # Close any remaining positions
        if symbol in self.positions:
            final_price = df['Close'].iloc[-1]
            quantity = self.positions[symbol].quantity
            self.execute_trade(
                symbol, 'SELL', quantity, final_price,
                df.index[-1], "End of backtest"
            )
        
        # Get performance metrics
        metrics = self.get_performance_metrics()
        
        return {
            'strategy': self.name,
            'symbol': symbol,
            'start_date': df.index[0],
            'end_date': df.index[-1],
            'metrics': metrics,
            'final_value': self.portfolio_value,
            'trades': self.trades
        }
