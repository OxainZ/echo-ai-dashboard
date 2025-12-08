"""
Base Strategy Class

Defines the interface and common functionality for all trading strategies.
All strategies inherit from this base class to ensure consistent behavior.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
from datetime import datetime


@dataclass
class Trade:
    """
    Represents a single trade
    
    Attributes:
        timestamp: When trade was executed
        symbol: Stock ticker
        action: 'BUY' or 'SELL'
        quantity: Number of shares
        price: Execution price
        reason: Why trade was made
    """
    timestamp: datetime
    symbol: str
    action: str  # 'BUY' or 'SELL'
    quantity: int
    price: float
    reason: str = ""
    
    @property
    def value(self) -> float:
        """Total trade value"""
        return self.quantity * self.price


@dataclass
class Position:
    """
    Represents a current position
    
    Attributes:
        symbol: Stock ticker
        quantity: Number of shares held
        avg_price: Average entry price
        current_price: Current market price
    """
    symbol: str
    quantity: int
    avg_price: float
    current_price: float = 0.0
    
    @property
    def value(self) -> float:
        """Current position value"""
        return self.quantity * self.current_price
    
    @property
    def cost_basis(self) -> float:
        """Original cost"""
        return self.quantity * self.avg_price
    
    @property
    def pnl(self) -> float:
        """Profit/Loss"""
        return self.value - self.cost_basis
    
    @property
    def pnl_percent(self) -> float:
        """Profit/Loss percentage"""
        return (self.pnl / self.cost_basis) * 100 if self.cost_basis > 0 else 0.0


class RiskManager:
    """
    Handles risk management for trading strategies
    
    Features:
    - Position sizing
    - Stop loss management
    - Profit taking
    - Portfolio risk limits
    """
    
    def __init__(
        self,
        max_position_size: float = 0.25,
        stop_loss_pct: float = 0.05,
        take_profit_pct: float = 0.10,
        max_portfolio_risk: float = 0.20
    ):
        """
        Initialize risk manager
        
        Args:
            max_position_size: Max % of portfolio per position
            stop_loss_pct: Stop loss threshold (negative)
            take_profit_pct: Take profit threshold (positive)
            max_portfolio_risk: Max % of portfolio at risk
        """
        self.max_position_size = max_position_size
        self.stop_loss_pct = -abs(stop_loss_pct)
        self.take_profit_pct = abs(take_profit_pct)
        self.max_portfolio_risk = max_portfolio_risk
    
    def calculate_position_size(
        self,
        portfolio_value: float,
        price: float,
        volatility: Optional[float] = None
    ) -> int:
        """
        Calculate optimal position size
        
        Args:
            portfolio_value: Total portfolio value
            price: Stock price
            volatility: Optional volatility adjustment
            
        Returns:
            Number of shares to buy
        """
        # Base position size
        max_value = portfolio_value * self.max_position_size
        
        # Adjust for volatility if provided
        if volatility:
            # Reduce size for high volatility
            vol_adj = 1.0 / (1.0 + volatility)
            max_value *= vol_adj
        
        # Calculate shares (integer)
        shares = int(max_value / price)
        
        return max(1, shares)
    
    def check_stop_loss(self, position: Position) -> bool:
        """
        Check if stop loss should be triggered
        
        Args:
            position: Current position
            
        Returns:
            True if stop loss triggered
        """
        return position.pnl_percent <= self.stop_loss_pct * 100
    
    def check_take_profit(self, position: Position) -> bool:
        """
        Check if profit should be taken
        
        Args:
            position: Current position
            
        Returns:
            True if take profit triggered
        """
        return position.pnl_percent >= self.take_profit_pct * 100


class BaseStrategy(ABC):
    """
    Abstract base class for trading strategies
    
    All strategies must implement:
    - generate_signals: Analyze data and generate buy/sell signals
    - execute: Execute trades based on signals
    """
    
    def __init__(
        self,
        name: str,
        initial_capital: float = 100000.0,
        risk_manager: Optional[RiskManager] = None
    ):
        """
        Initialize strategy
        
        Args:
            name: Strategy name
            initial_capital: Starting capital
            risk_manager: Risk management configuration
        """
        self.name = name
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.risk_manager = risk_manager or RiskManager()
    
    @property
    def portfolio_value(self) -> float:
        """Total portfolio value"""
        positions_value = sum(pos.value for pos in self.positions.values())
        return self.cash + positions_value
    
    @property
    def total_return(self) -> float:
        """Total return percentage"""
        return ((self.portfolio_value - self.initial_capital) / self.initial_capital) * 100
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals from data
        
        Args:
            data: Historical price data
            
        Returns:
            DataFrame with signal column (1=buy, -1=sell, 0=hold)
        """
        pass
    
    def execute_trade(
        self,
        symbol: str,
        action: str,
        quantity: int,
        price: float,
        timestamp: datetime,
        reason: str = ""
    ) -> bool:
        """
        Execute a trade
        
        Args:
            symbol: Stock ticker
            action: 'BUY' or 'SELL'
            quantity: Number of shares
            price: Execution price
            timestamp: Trade timestamp
            reason: Reason for trade
            
        Returns:
            True if trade executed successfully
        """
        trade_value = quantity * price
        
        if action == 'BUY':
            if trade_value > self.cash:
                return False  # Insufficient funds
            
            # Update cash
            self.cash -= trade_value
            
            # Update position
            if symbol in self.positions:
                pos = self.positions[symbol]
                new_quantity = pos.quantity + quantity
                new_avg_price = ((pos.quantity * pos.avg_price) + trade_value) / new_quantity
                pos.quantity = new_quantity
                pos.avg_price = new_avg_price
            else:
                self.positions[symbol] = Position(symbol, quantity, price)
        
        elif action == 'SELL':
            if symbol not in self.positions or self.positions[symbol].quantity < quantity:
                return False  # Insufficient shares
            
            # Update cash
            self.cash += trade_value
            
            # Update position
            pos = self.positions[symbol]
            pos.quantity -= quantity
            
            # Remove position if fully closed
            if pos.quantity == 0:
                del self.positions[symbol]
        
        else:
            return False  # Invalid action
        
        # Record trade
        trade = Trade(timestamp, symbol, action, quantity, price, reason)
        self.trades.append(trade)
        
        return True
    
    def update_positions(self, current_prices: Dict[str, float]) -> None:
        """
        Update position values with current prices
        
        Args:
            current_prices: Dict mapping symbols to current prices
        """
        for symbol, position in self.positions.items():
            if symbol in current_prices:
                position.current_price = current_prices[symbol]
    
    def check_risk_management(self) -> List[Trade]:
        """
        Check and execute risk management rules
        
        Returns:
            List of risk management trades executed
        """
        risk_trades = []
        
        for symbol, position in list(self.positions.items()):
            # Check stop loss
            if self.risk_manager.check_stop_loss(position):
                if self.execute_trade(
                    symbol, 'SELL', position.quantity,
                    position.current_price, datetime.now(),
                    f"Stop loss triggered at {position.pnl_percent:.1f}%"
                ):
                    risk_trades.append(self.trades[-1])
            
            # Check take profit
            elif self.risk_manager.check_take_profit(position):
                if self.execute_trade(
                    symbol, 'SELL', position.quantity,
                    position.current_price, datetime.now(),
                    f"Take profit triggered at {position.pnl_percent:.1f}%"
                ):
                    risk_trades.append(self.trades[-1])
        
        return risk_trades
    
    def get_performance_metrics(self) -> Dict:
        """
        Calculate strategy performance metrics
        
        Returns:
            Dict with performance statistics
        """
        if not self.trades:
            return {}
        
        # Calculate returns
        returns = []
        for trade in self.trades:
            if trade.action == 'SELL':
                # Find corresponding buy
                symbol = trade.symbol
                if symbol in self.positions:
                    returns.append(
                        (trade.price - self.positions[symbol].avg_price) / 
                        self.positions[symbol].avg_price
                    )
        
        if not returns:
            return {
                'total_return': self.total_return,
                'num_trades': len(self.trades),
                'portfolio_value': self.portfolio_value
            }
        
        returns_arr = np.array(returns)
        
        # Calculate metrics
        win_rate = (returns_arr > 0).sum() / len(returns_arr) if len(returns_arr) > 0 else 0
        avg_win = returns_arr[returns_arr > 0].mean() if (returns_arr > 0).any() else 0
        avg_loss = returns_arr[returns_arr < 0].mean() if (returns_arr < 0).any() else 0
        
        return {
            'total_return': self.total_return,
            'num_trades': len(self.trades),
            'win_rate': win_rate * 100,
            'avg_win': avg_win * 100,
            'avg_loss': avg_loss * 100,
            'sharpe_ratio': (returns_arr.mean() / returns_arr.std() * np.sqrt(252)) if returns_arr.std() > 0 else 0,
            'portfolio_value': self.portfolio_value,
            'cash': self.cash
        }
