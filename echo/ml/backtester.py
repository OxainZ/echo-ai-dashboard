"""
Backtesting module for trading strategies
"""
from __future__ import annotations
from typing import Dict, List, Optional, Callable
import pandas as pd
import numpy as np
from datetime import datetime
from ..utils.logging import get_logger
from ..utils.config import config

log = get_logger("Backtester")


class Portfolio:
    """Track portfolio state during backtesting"""
    
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, Dict] = {}
        self.history: List[Dict] = []
        self.trades: List[Dict] = []
    
    def buy(self, ticker: str, price: float, shares: int, date: datetime) -> bool:
        """Execute buy order"""
        cost = price * shares
        if cost > self.cash:
            log.warning(f"Insufficient funds to buy {shares} shares of {ticker}")
            return False
        
        self.cash -= cost
        if ticker in self.positions:
            # Average cost
            old_shares = self.positions[ticker]['shares']
            old_cost = self.positions[ticker]['avg_price'] * old_shares
            new_shares = old_shares + shares
            self.positions[ticker] = {
                'shares': new_shares,
                'avg_price': (old_cost + cost) / new_shares
            }
        else:
            self.positions[ticker] = {
                'shares': shares,
                'avg_price': price
            }
        
        self.trades.append({
            'date': date,
            'action': 'BUY',
            'ticker': ticker,
            'price': price,
            'shares': shares,
            'value': cost
        })
        return True
    
    def sell(self, ticker: str, price: float, shares: int, date: datetime) -> bool:
        """Execute sell order"""
        if ticker not in self.positions or self.positions[ticker]['shares'] < shares:
            log.warning(f"Insufficient shares to sell {shares} of {ticker}")
            return False
        
        value = price * shares
        self.cash += value
        
        self.positions[ticker]['shares'] -= shares
        if self.positions[ticker]['shares'] == 0:
            del self.positions[ticker]
        
        self.trades.append({
            'date': date,
            'action': 'SELL',
            'ticker': ticker,
            'price': price,
            'shares': shares,
            'value': value
        })
        return True
    
    def get_value(self, prices: Dict[str, float]) -> float:
        """Calculate total portfolio value"""
        holdings_value = sum(
            pos['shares'] * prices.get(ticker, 0)
            for ticker, pos in self.positions.items()
        )
        return self.cash + holdings_value
    
    def record_state(self, date: datetime, prices: Dict[str, float]):
        """Record portfolio state at a point in time"""
        total_value = self.get_value(prices)
        self.history.append({
            'date': date,
            'cash': self.cash,
            'holdings_value': total_value - self.cash,
            'total_value': total_value,
            'return': (total_value - self.initial_capital) / self.initial_capital
        })


class Backtester:
    """Backtest trading strategies on historical data"""
    
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.enabled = config.enable_backtesting
    
    def run(self, strategy: Callable, data: Dict[str, pd.DataFrame], 
            start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict:
        """
        Run backtest for a trading strategy
        
        Args:
            strategy: Function that takes (portfolio, date, data) and returns trading decisions
            data: Dictionary of ticker -> DataFrame with OHLCV data
            start_date: Start date for backtest (YYYY-MM-DD)
            end_date: End date for backtest (YYYY-MM-DD)
            
        Returns:
            Dictionary with backtest results and performance metrics
        """
        if not self.enabled:
            log.warning("Backtesting is disabled")
            return {}
        
        try:
            portfolio = Portfolio(self.initial_capital)
            
            # Align dates across all tickers
            all_dates = self._get_common_dates(data)
            if start_date:
                all_dates = [d for d in all_dates if d >= pd.to_datetime(start_date)]
            if end_date:
                all_dates = [d for d in all_dates if d <= pd.to_datetime(end_date)]
            
            if not all_dates:
                log.error("No valid dates for backtesting")
                return {}
            
            # Run simulation
            for date in all_dates:
                # Get current prices
                prices = {ticker: df.loc[date, 'Close'] 
                         for ticker, df in data.items() if date in df.index}
                
                # Record portfolio state
                portfolio.record_state(date, prices)
                
                # Execute strategy
                try:
                    decisions = strategy(portfolio, date, data)
                    self._execute_decisions(portfolio, decisions, prices, date)
                except Exception as e:
                    log.warning(f"Strategy error on {date}: {e}")
            
            # Calculate performance metrics
            results = self._calculate_metrics(portfolio)
            results['trades'] = portfolio.trades
            results['portfolio_history'] = portfolio.history
            
            return results
            
        except Exception as e:
            log.exception(f"Error running backtest: {e}")
            return {}
    
    def _get_common_dates(self, data: Dict[str, pd.DataFrame]) -> List[datetime]:
        """Get dates that exist in all DataFrames"""
        if not data:
            return []
        
        date_sets = [set(df.index) for df in data.values()]
        common_dates = sorted(set.intersection(*date_sets))
        return common_dates
    
    def _execute_decisions(self, portfolio: Portfolio, decisions: List[Dict], 
                          prices: Dict[str, float], date: datetime):
        """Execute trading decisions"""
        for decision in decisions:
            action = decision.get('action', '').upper()
            ticker = decision.get('ticker')
            shares = decision.get('shares', 0)
            
            if not ticker or ticker not in prices:
                continue
            
            price = prices[ticker]
            
            if action == 'BUY':
                portfolio.buy(ticker, price, shares, date)
            elif action == 'SELL':
                portfolio.sell(ticker, price, shares, date)
    
    def _calculate_metrics(self, portfolio: Portfolio) -> Dict:
        """Calculate performance metrics"""
        if not portfolio.history:
            return {}
        
        history_df = pd.DataFrame(portfolio.history)
        
        # Returns
        total_return = history_df['return'].iloc[-1] if len(history_df) > 0 else 0
        
        # Volatility (annualized)
        returns = history_df['total_value'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252) if len(returns) > 1 else 0
        
        # Sharpe Ratio (assuming 0% risk-free rate)
        sharpe_ratio = (total_return / volatility) if volatility > 0 else 0
        
        # Maximum Drawdown
        cumulative = history_df['total_value']
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Win rate
        winning_trades = sum(1 for t in portfolio.trades 
                           if t['action'] == 'SELL' and self._is_winning_trade(t, portfolio.trades))
        total_closed_trades = sum(1 for t in portfolio.trades if t['action'] == 'SELL')
        win_rate = winning_trades / total_closed_trades if total_closed_trades > 0 else 0
        
        return {
            'initial_capital': portfolio.initial_capital,
            'final_value': history_df['total_value'].iloc[-1],
            'total_return': round(total_return * 100, 2),
            'volatility': round(volatility, 4),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'max_drawdown': round(max_drawdown * 100, 2),
            'total_trades': len(portfolio.trades),
            'win_rate': round(win_rate * 100, 2),
            'final_cash': round(portfolio.cash, 2),
            'open_positions': len(portfolio.positions),
        }
    
    def _is_winning_trade(self, sell_trade: Dict, all_trades: List[Dict]) -> bool:
        """Check if a sell trade was profitable"""
        ticker = sell_trade['ticker']
        sell_date = sell_trade['date']
        
        # Find corresponding buy trade(s)
        buy_trades = [t for t in all_trades 
                     if t['action'] == 'BUY' 
                     and t['ticker'] == ticker 
                     and t['date'] <= sell_date]
        
        if not buy_trades:
            return False
        
        # Use most recent buy for simplicity
        buy_price = buy_trades[-1]['price']
        sell_price = sell_trade['price']
        
        return sell_price > buy_price


def simple_moving_average_strategy(short_window: int = 20, long_window: int = 50):
    """
    Simple Moving Average Crossover Strategy
    Buy when short MA crosses above long MA, sell when it crosses below
    """
    def strategy(portfolio: Portfolio, date: datetime, data: Dict[str, pd.DataFrame]) -> List[Dict]:
        decisions = []
        
        for ticker, df in data.items():
            if date not in df.index:
                continue
            
            # Calculate moving averages
            df_subset = df.loc[:date]
            if len(df_subset) < long_window:
                continue
            
            short_ma = df_subset['Close'].rolling(short_window).mean().iloc[-1]
            long_ma = df_subset['Close'].rolling(long_window).mean().iloc[-1]
            
            # Previous values
            if len(df_subset) > 1:
                short_ma_prev = df_subset['Close'].rolling(short_window).mean().iloc[-2]
                long_ma_prev = df_subset['Close'].rolling(long_window).mean().iloc[-2]
                
                # Buy signal: short MA crosses above long MA
                if short_ma > long_ma and short_ma_prev <= long_ma_prev:
                    shares = int(portfolio.cash * 0.3 / df.loc[date, 'Close'])  # Invest 30% of cash
                    if shares > 0:
                        decisions.append({'action': 'BUY', 'ticker': ticker, 'shares': shares})
                
                # Sell signal: short MA crosses below long MA
                elif short_ma < long_ma and short_ma_prev >= long_ma_prev:
                    if ticker in portfolio.positions:
                        shares = portfolio.positions[ticker]['shares']
                        decisions.append({'action': 'SELL', 'ticker': ticker, 'shares': shares})
        
        return decisions
    
    return strategy
