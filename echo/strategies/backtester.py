"""
Backtesting framework for trading strategies.

Provides tools to test strategies on historical data and evaluate performance.
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy, Trade, Position, PositionType


@dataclass
class BacktestResult:
    """Container for backtest results."""
    strategy_name: str
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_pct: float
    num_trades: int
    num_winning_trades: int
    num_losing_trades: int
    win_rate: float
    avg_win: float
    avg_loss: float
    avg_trade_return: float
    best_trade: float
    worst_trade: float
    max_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float
    profit_factor: float
    equity_curve: pd.Series
    trades: List[Trade]
    
    def to_dict(self) -> Dict:
        """Convert results to dictionary."""
        return {
            'strategy_name': self.strategy_name,
            'initial_capital': self.initial_capital,
            'final_capital': self.final_capital,
            'total_return': self.total_return,
            'total_return_pct': self.total_return_pct,
            'num_trades': self.num_trades,
            'num_winning_trades': self.num_winning_trades,
            'num_losing_trades': self.num_losing_trades,
            'win_rate': self.win_rate,
            'avg_win': self.avg_win,
            'avg_loss': self.avg_loss,
            'avg_trade_return': self.avg_trade_return,
            'best_trade': self.best_trade,
            'worst_trade': self.worst_trade,
            'max_drawdown': self.max_drawdown,
            'sharpe_ratio': self.sharpe_ratio,
            'sortino_ratio': self.sortino_ratio,
            'profit_factor': self.profit_factor
        }
    
    def summary(self) -> str:
        """Generate a text summary of results."""
        return f"""
Backtest Results for {self.strategy_name}
{'=' * 50}
Initial Capital: ${self.initial_capital:,.2f}
Final Capital: ${self.final_capital:,.2f}
Total Return: ${self.total_return:,.2f} ({self.total_return_pct:.2f}%)

Trade Statistics:
  Total Trades: {self.num_trades}
  Winning Trades: {self.num_winning_trades}
  Losing Trades: {self.num_losing_trades}
  Win Rate: {self.win_rate:.2f}%
  
Performance Metrics:
  Average Win: {self.avg_win:.2f}%
  Average Loss: {self.avg_loss:.2f}%
  Best Trade: {self.best_trade:.2f}%
  Worst Trade: {self.worst_trade:.2f}%
  Profit Factor: {self.profit_factor:.2f}
  
Risk Metrics:
  Max Drawdown: {self.max_drawdown:.2f}%
  Sharpe Ratio: {self.sharpe_ratio:.2f}
  Sortino Ratio: {self.sortino_ratio:.2f}
"""


class Backtester:
    """
    Backtest trading strategies on historical data.
    """
    
    def __init__(self, strategy: BaseStrategy, commission: float = 0.001):
        """
        Initialize backtester.
        
        Args:
            strategy: Trading strategy to test
            commission: Commission rate per trade (default 0.1%)
        """
        self.strategy = strategy
        self.commission = commission
        self.equity_curve: List[float] = []
    
    def run(self, data: pd.DataFrame, ticker: str = "STOCK") -> BacktestResult:
        """
        Run backtest on historical data.
        
        Args:
            data: DataFrame with OHLCV data (must have 'Close' column)
            ticker: Stock ticker symbol
            
        Returns:
            BacktestResult with performance metrics
        """
        # Reset strategy state
        self.strategy.capital = self.strategy.initial_capital
        self.strategy.positions = []
        self.strategy.trades = []
        self.equity_curve = [self.strategy.initial_capital]
        
        # Generate signals
        signals = self.strategy.generate_signals(data)
        
        # Iterate through each bar
        for idx in range(1, len(data)):
            current_time = data.index[idx]
            current_price = data['Close'].iloc[idx]
            current_signal = signals.iloc[idx]
            
            # Check existing positions for stop loss / take profit
            position = self.strategy.get_position(ticker)
            if position:
                if position.should_stop_loss(current_price):
                    self._execute_exit(position, current_price, current_time, "stop_loss")
                elif position.should_take_profit(current_price):
                    self._execute_exit(position, current_price, current_time, "take_profit")
            
            # Process signals
            if current_signal == 1 and not self.strategy.has_position(ticker):
                # Buy signal
                self._execute_entry(ticker, PositionType.LONG, current_price, 
                                  current_time, data.iloc[:idx+1])
            
            elif current_signal == -1:
                if position and position.is_long:
                    # Close long position
                    self._execute_exit(position, current_price, current_time, "signal")
                elif not position:
                    # Open short position
                    self._execute_entry(ticker, PositionType.SHORT, current_price,
                                      current_time, data.iloc[:idx+1])
            
            # Update equity curve
            current_equity = self._calculate_equity(current_price)
            self.equity_curve.append(current_equity)
        
        # Close any remaining positions
        if self.strategy.positions:
            final_price = data['Close'].iloc[-1]
            final_time = data.index[-1]
            for position in self.strategy.positions.copy():
                self._execute_exit(position, final_price, final_time, "end_of_data")
        
        # Calculate and return results
        return self._calculate_results(data.index)
    
    def _execute_entry(self, ticker: str, position_type: PositionType,
                      price: float, time: datetime, data: pd.DataFrame) -> None:
        """Execute a position entry."""
        # Calculate position size
        signal = 1 if position_type == PositionType.LONG else -1
        quantity = self.strategy.calculate_position_size(ticker, signal, price, data)
        
        if quantity <= 0:
            return
        
        # Calculate costs
        position_value = price * quantity
        commission_cost = position_value * self.commission
        
        # For long: pay cash + commission
        # For short: receive cash - commission
        if position_type == PositionType.LONG:
            total_cost = position_value + commission_cost
            if self.strategy.capital < total_cost:
                return  # Not enough capital
            self.strategy.capital -= total_cost
        else:  # SHORT
            # When shorting, we receive cash minus commission
            net_proceeds = position_value - commission_cost
            self.strategy.capital += net_proceeds
        
        # Open position
        self.strategy.open_position(ticker, position_type, price, quantity, time)
    
    def _execute_exit(self, position: Position, price: float, 
                     time: datetime, reason: str) -> None:
        """Execute a position exit."""
        # Calculate proceeds/cost
        position_value = price * position.quantity
        commission_cost = position_value * self.commission
        
        # For long: sell and receive cash - commission
        # For short: buy back and pay cash + commission
        if position.is_long:
            net_proceeds = position_value - commission_cost
            self.strategy.capital += net_proceeds
        else:  # SHORT
            total_cost = position_value + commission_cost
            self.strategy.capital -= total_cost
        
        # Close position
        self.strategy.close_position(position, price, time, reason)
    
    def _calculate_equity(self, current_price: float) -> float:
        """Calculate current portfolio equity."""
        equity = self.strategy.capital
        
        for position in self.strategy.positions:
            # For long: equity += current_value
            # For short: equity += cash_received - current_liability
            position_value = current_price * position.quantity
            equity += position_value
        
        return equity
    
    def _calculate_results(self, index: pd.DatetimeIndex) -> BacktestResult:
        """Calculate backtest performance metrics."""
        trades = self.strategy.trades
        equity_series = pd.Series(self.equity_curve, index=index[:len(self.equity_curve)])
        
        # Basic stats
        initial_capital = self.strategy.initial_capital
        final_capital = self.strategy.capital
        total_return = final_capital - initial_capital
        total_return_pct = (total_return / initial_capital) * 100
        
        # Trade stats
        num_trades = len(trades)
        winning_trades = [t for t in trades if t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl <= 0]
        num_winning = len(winning_trades)
        num_losing = len(losing_trades)
        win_rate = (num_winning / num_trades * 100) if num_trades > 0 else 0
        
        avg_win = np.mean([t.pnl_percent for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t.pnl_percent for t in losing_trades]) if losing_trades else 0
        avg_trade_return = np.mean([t.pnl_percent for t in trades]) if trades else 0
        
        best_trade = max([t.pnl_percent for t in trades]) if trades else 0
        worst_trade = min([t.pnl_percent for t in trades]) if trades else 0
        
        # Risk metrics
        returns = equity_series.pct_change().dropna()
        
        # Max drawdown
        running_max = equity_series.expanding().max()
        drawdown = (equity_series - running_max) / running_max
        max_drawdown = abs(drawdown.min()) * 100
        
        # Sharpe ratio
        if len(returns) > 1 and returns.std() > 0:
            sharpe_ratio = np.sqrt(252) * (returns.mean() / returns.std())
        else:
            sharpe_ratio = 0
        
        # Sortino ratio
        downside_returns = returns[returns < 0]
        if len(downside_returns) > 0 and downside_returns.std() > 0:
            sortino_ratio = np.sqrt(252) * (returns.mean() / downside_returns.std())
        else:
            sortino_ratio = 0
        
        # Profit factor
        total_wins = sum([t.pnl for t in winning_trades])
        total_losses = abs(sum([t.pnl for t in losing_trades]))
        profit_factor = (total_wins / total_losses) if total_losses > 0 else 0
        
        return BacktestResult(
            strategy_name=self.strategy.name,
            initial_capital=initial_capital,
            final_capital=final_capital,
            total_return=total_return,
            total_return_pct=total_return_pct,
            num_trades=num_trades,
            num_winning_trades=num_winning,
            num_losing_trades=num_losing,
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            avg_trade_return=avg_trade_return,
            best_trade=best_trade,
            worst_trade=worst_trade,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            profit_factor=profit_factor,
            equity_curve=equity_series,
            trades=trades
        )
