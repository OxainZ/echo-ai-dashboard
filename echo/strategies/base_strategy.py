"""
Base class for trading strategies.

Provides a common interface for implementing various trading strategies.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List
import pandas as pd


class OrderType(Enum):
    """Types of orders."""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class PositionType(Enum):
    """Types of positions."""
    LONG = "long"
    SHORT = "short"


@dataclass
class Position:
    """Represents an open position."""
    ticker: str
    position_type: PositionType
    entry_price: float
    quantity: float
    entry_time: datetime
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    @property
    def is_long(self) -> bool:
        return self.position_type == PositionType.LONG
    
    @property
    def is_short(self) -> bool:
        return self.position_type == PositionType.SHORT
    
    def unrealized_pnl(self, current_price: float) -> float:
        """Calculate unrealized profit/loss."""
        if self.is_long:
            return (current_price - self.entry_price) * self.quantity
        else:
            return (self.entry_price - current_price) * self.quantity
    
    def should_stop_loss(self, current_price: float) -> bool:
        """Check if stop loss should trigger."""
        if self.stop_loss is None:
            return False
        
        if self.is_long:
            return current_price <= self.stop_loss
        else:
            return current_price >= self.stop_loss
    
    def should_take_profit(self, current_price: float) -> bool:
        """Check if take profit should trigger."""
        if self.take_profit is None:
            return False
        
        if self.is_long:
            return current_price >= self.take_profit
        else:
            return current_price <= self.take_profit


@dataclass
class Trade:
    """Represents a completed trade."""
    ticker: str
    position_type: PositionType
    entry_price: float
    exit_price: float
    quantity: float
    entry_time: datetime
    exit_time: datetime
    pnl: float
    pnl_percent: float
    reason: str  # e.g., "take_profit", "stop_loss", "signal"


class BaseStrategy(ABC):
    """
    Abstract base class for trading strategies.
    
    Subclasses must implement:
    - generate_signals(): Generate buy/sell signals
    - calculate_position_size(): Determine position size
    """
    
    def __init__(self, name: str, initial_capital: float = 100000):
        self.name = name
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions: List[Position] = []
        self.trades: List[Trade] = []
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals from data.
        
        Args:
            data: DataFrame with OHLCV and any additional features
            
        Returns:
            Series with signals: 1 (buy), -1 (sell), 0 (hold)
        """
        pass
    
    @abstractmethod
    def calculate_position_size(self, ticker: str, signal: int, 
                                current_price: float, data: pd.DataFrame) -> float:
        """
        Calculate position size for a trade.
        
        Args:
            ticker: Stock ticker
            signal: Trading signal (1 or -1)
            current_price: Current price
            data: Market data
            
        Returns:
            Position size (number of shares)
        """
        pass
    
    def calculate_stop_loss(self, entry_price: float, position_type: PositionType) -> Optional[float]:
        """
        Calculate stop loss price.
        
        Args:
            entry_price: Entry price of position
            position_type: Long or short position
            
        Returns:
            Stop loss price or None
        """
        # Default: 2% stop loss
        if position_type == PositionType.LONG:
            return entry_price * 0.98
        else:
            return entry_price * 1.02
    
    def calculate_take_profit(self, entry_price: float, position_type: PositionType) -> Optional[float]:
        """
        Calculate take profit price.
        
        Args:
            entry_price: Entry price of position
            position_type: Long or short position
            
        Returns:
            Take profit price or None
        """
        # Default: 4% take profit (2:1 risk/reward)
        if position_type == PositionType.LONG:
            return entry_price * 1.04
        else:
            return entry_price * 0.96
    
    def open_position(self, ticker: str, position_type: PositionType,
                     entry_price: float, quantity: float, entry_time: datetime) -> Position:
        """Open a new position."""
        position = Position(
            ticker=ticker,
            position_type=position_type,
            entry_price=entry_price,
            quantity=quantity,
            entry_time=entry_time,
            stop_loss=self.calculate_stop_loss(entry_price, position_type),
            take_profit=self.calculate_take_profit(entry_price, position_type)
        )
        self.positions.append(position)
        return position
    
    def close_position(self, position: Position, exit_price: float, 
                      exit_time: datetime, reason: str = "signal") -> Trade:
        """Close an existing position."""
        pnl = position.unrealized_pnl(exit_price)
        pnl_percent = (pnl / (position.entry_price * position.quantity)) * 100
        
        trade = Trade(
            ticker=position.ticker,
            position_type=position.position_type,
            entry_price=position.entry_price,
            exit_price=exit_price,
            quantity=position.quantity,
            entry_time=position.entry_time,
            exit_time=exit_time,
            pnl=pnl,
            pnl_percent=pnl_percent,
            reason=reason
        )
        
        self.trades.append(trade)
        self.positions.remove(position)
        self.capital += pnl
        
        return trade
    
    def get_position(self, ticker: str) -> Optional[Position]:
        """Get open position for a ticker."""
        for position in self.positions:
            if position.ticker == ticker:
                return position
        return None
    
    def has_position(self, ticker: str) -> bool:
        """Check if there's an open position for a ticker."""
        return self.get_position(ticker) is not None
