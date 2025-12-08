"""
Portfolio tracking module for Echo AI Dashboard
Track investments, performance, and risk metrics over time
"""
from __future__ import annotations
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from ..utils.logging import get_logger

log = get_logger("PortfolioTracker")


class Position:
    """Represents a single position in the portfolio"""
    
    def __init__(self, ticker: str, shares: float, avg_cost: float, 
                 purchase_date: Optional[datetime] = None):
        self.ticker = ticker
        self.shares = shares
        self.avg_cost = avg_cost
        self.purchase_date = purchase_date or datetime.now()
        self.history: List[Dict] = []
    
    def get_cost_basis(self) -> float:
        """Get total cost basis"""
        return self.shares * self.avg_cost
    
    def get_market_value(self, current_price: float) -> float:
        """Get current market value"""
        return self.shares * current_price
    
    def get_unrealized_pnl(self, current_price: float) -> float:
        """Get unrealized profit/loss"""
        return self.get_market_value(current_price) - self.get_cost_basis()
    
    def get_return_pct(self, current_price: float) -> float:
        """Get return percentage"""
        if self.avg_cost == 0:
            return 0.0
        return ((current_price - self.avg_cost) / self.avg_cost) * 100
    
    def add_shares(self, shares: float, price: float):
        """Add shares to position (average cost)"""
        total_cost = self.get_cost_basis() + (shares * price)
        self.shares += shares
        self.avg_cost = total_cost / self.shares if self.shares > 0 else 0
    
    def remove_shares(self, shares: float) -> bool:
        """Remove shares from position"""
        if shares > self.shares:
            return False
        self.shares -= shares
        return True


class PortfolioTracker:
    """Track and analyze portfolio performance over time"""
    
    def __init__(self, initial_cash: float = 0.0):
        self.positions: Dict[str, Position] = {}
        self.cash = initial_cash
        self.transactions: List[Dict] = []
        self.snapshots: List[Dict] = []
        self.created_at = datetime.now()
    
    def add_position(self, ticker: str, shares: float, price: float, 
                     date: Optional[datetime] = None) -> bool:
        """Add or update a position"""
        try:
            date = date or datetime.now()
            cost = shares * price
            
            if ticker in self.positions:
                self.positions[ticker].add_shares(shares, price)
            else:
                self.positions[ticker] = Position(ticker, shares, price, date)
            
            self.cash -= cost
            
            self.transactions.append({
                'date': date,
                'type': 'BUY',
                'ticker': ticker,
                'shares': shares,
                'price': price,
                'amount': cost
            })
            
            log.info(f"Added position: {shares} shares of {ticker} at ${price}")
            return True
            
        except Exception as e:
            log.exception(f"Error adding position: {e}")
            return False
    
    def remove_position(self, ticker: str, shares: float, price: float,
                       date: Optional[datetime] = None) -> bool:
        """Remove shares from a position"""
        try:
            if ticker not in self.positions:
                log.warning(f"Position {ticker} not found")
                return False
            
            date = date or datetime.now()
            position = self.positions[ticker]
            
            if not position.remove_shares(shares):
                log.warning(f"Insufficient shares to sell for {ticker}")
                return False
            
            value = shares * price
            self.cash += value
            
            # Calculate realized P&L
            cost_basis = shares * position.avg_cost
            realized_pnl = value - cost_basis
            
            self.transactions.append({
                'date': date,
                'type': 'SELL',
                'ticker': ticker,
                'shares': shares,
                'price': price,
                'amount': value,
                'realized_pnl': realized_pnl
            })
            
            # Remove position if no shares left
            if position.shares <= 0:
                del self.positions[ticker]
            
            log.info(f"Removed position: {shares} shares of {ticker} at ${price}, P&L: ${realized_pnl:.2f}")
            return True
            
        except Exception as e:
            log.exception(f"Error removing position: {e}")
            return False
    
    def get_total_value(self, current_prices: Dict[str, float]) -> float:
        """Get total portfolio value"""
        holdings_value = sum(
            pos.get_market_value(current_prices.get(ticker, pos.avg_cost))
            for ticker, pos in self.positions.items()
        )
        return self.cash + holdings_value
    
    def get_holdings_value(self, current_prices: Dict[str, float]) -> float:
        """Get total value of holdings (excluding cash)"""
        return sum(
            pos.get_market_value(current_prices.get(ticker, pos.avg_cost))
            for ticker, pos in self.positions.items()
        )
    
    def get_allocation(self, current_prices: Dict[str, float]) -> Dict[str, float]:
        """Get allocation percentages for each position"""
        total_value = self.get_total_value(current_prices)
        if total_value == 0:
            return {}
        
        allocation = {}
        for ticker, pos in self.positions.items():
            value = pos.get_market_value(current_prices.get(ticker, pos.avg_cost))
            allocation[ticker] = (value / total_value) * 100
        
        allocation['CASH'] = (self.cash / total_value) * 100
        return allocation
    
    def take_snapshot(self, current_prices: Dict[str, float], date: Optional[datetime] = None):
        """Record portfolio state at a point in time"""
        date = date or datetime.now()
        
        total_value = self.get_total_value(current_prices)
        holdings_value = self.get_holdings_value(current_prices)
        
        snapshot = {
            'date': date,
            'total_value': total_value,
            'cash': self.cash,
            'holdings_value': holdings_value,
            'num_positions': len(self.positions),
            'positions': {
                ticker: {
                    'shares': pos.shares,
                    'avg_cost': pos.avg_cost,
                    'current_price': current_prices.get(ticker, pos.avg_cost),
                    'market_value': pos.get_market_value(current_prices.get(ticker, pos.avg_cost)),
                    'unrealized_pnl': pos.get_unrealized_pnl(current_prices.get(ticker, pos.avg_cost)),
                    'return_pct': pos.get_return_pct(current_prices.get(ticker, pos.avg_cost))
                }
                for ticker, pos in self.positions.items()
            }
        }
        
        self.snapshots.append(snapshot)
        return snapshot
    
    def get_performance_metrics(self, current_prices: Dict[str, float]) -> Dict:
        """Calculate portfolio performance metrics"""
        try:
            total_value = self.get_total_value(current_prices)
            
            # Calculate returns
            total_invested = sum(t['amount'] for t in self.transactions if t['type'] == 'BUY')
            total_return = ((total_value - total_invested) / total_invested * 100) if total_invested > 0 else 0
            
            # Calculate realized P&L
            realized_pnl = sum(t.get('realized_pnl', 0) for t in self.transactions if t['type'] == 'SELL')
            
            # Calculate unrealized P&L
            unrealized_pnl = sum(
                pos.get_unrealized_pnl(current_prices.get(ticker, pos.avg_cost))
                for ticker, pos in self.positions.items()
            )
            
            # Time-based metrics
            days_active = (datetime.now() - self.created_at).days or 1
            
            # Volatility (if we have snapshots)
            volatility = 0.0
            if len(self.snapshots) > 1:
                values = [s['total_value'] for s in self.snapshots]
                returns = np.diff(values) / values[:-1]
                volatility = np.std(returns) * np.sqrt(252) if len(returns) > 0 else 0
            
            # Sharpe ratio (simplified, assuming 0% risk-free rate)
            sharpe = (total_return / 100 / volatility) if volatility > 0 else 0
            
            # Diversification score (0-100)
            diversification = min(100, len(self.positions) * 20)
            
            return {
                'total_value': round(total_value, 2),
                'cash': round(self.cash, 2),
                'holdings_value': round(self.get_holdings_value(current_prices), 2),
                'total_invested': round(total_invested, 2),
                'total_return_pct': round(total_return, 2),
                'realized_pnl': round(realized_pnl, 2),
                'unrealized_pnl': round(unrealized_pnl, 2),
                'total_pnl': round(realized_pnl + unrealized_pnl, 2),
                'num_positions': len(self.positions),
                'num_transactions': len(self.transactions),
                'days_active': days_active,
                'volatility': round(volatility, 4),
                'sharpe_ratio': round(sharpe, 2),
                'diversification_score': diversification,
            }
            
        except Exception as e:
            log.exception(f"Error calculating performance metrics: {e}")
            return {}
    
    def get_risk_metrics(self, current_prices: Dict[str, float]) -> Dict:
        """Calculate risk metrics for the portfolio"""
        try:
            total_value = self.get_total_value(current_prices)
            if total_value == 0:
                return {}
            
            allocation = self.get_allocation(current_prices)
            
            # Concentration risk (% in largest position)
            position_allocations = {k: v for k, v in allocation.items() if k != 'CASH'}
            max_concentration = max(position_allocations.values()) if position_allocations else 0
            
            # Cash buffer
            cash_pct = allocation.get('CASH', 0)
            
            # Exposure (% invested)
            exposure = 100 - cash_pct
            
            # Risk level based on concentration and diversification
            if max_concentration > 50:
                risk_level = "High"
            elif max_concentration > 30 or len(self.positions) < 3:
                risk_level = "Moderate"
            else:
                risk_level = "Low"
            
            return {
                'risk_level': risk_level,
                'max_concentration': round(max_concentration, 2),
                'cash_buffer_pct': round(cash_pct, 2),
                'exposure_pct': round(exposure, 2),
                'num_positions': len(self.positions),
                'diversification_score': min(100, len(self.positions) * 20),
            }
            
        except Exception as e:
            log.exception(f"Error calculating risk metrics: {e}")
            return {}
