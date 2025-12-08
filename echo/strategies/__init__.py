"""
Trading strategies and backtesting framework.

Provides base classes and utilities for implementing and testing trading strategies.
"""

from .base_strategy import BaseStrategy, Position, Trade
from .backtester import Backtester, BacktestResult
from .risk_manager import RiskManager, PositionSizer

__all__ = [
    'BaseStrategy',
    'Position',
    'Trade',
    'Backtester',
    'BacktestResult',
    'RiskManager',
    'PositionSizer'
]
