"""
Risk management utilities for trading strategies.

Provides position sizing, risk controls, and portfolio management.
"""

from __future__ import annotations
from typing import Optional
import pandas as pd
import numpy as np


class PositionSizer:
    """
    Calculate position sizes based on risk management rules.
    """
    
    @staticmethod
    def fixed_dollar(capital: float, amount: float, price: float) -> float:
        """
        Fixed dollar amount position sizing.
        
        Args:
            capital: Total capital
            amount: Dollar amount to invest
            price: Current price
            
        Returns:
            Number of shares
        """
        return min(amount, capital) / price
    
    @staticmethod
    def fixed_percent(capital: float, percent: float, price: float) -> float:
        """
        Fixed percentage of capital position sizing.
        
        Args:
            capital: Total capital
            percent: Percentage of capital (0-100)
            price: Current price
            
        Returns:
            Number of shares
        """
        amount = capital * (percent / 100)
        return amount / price
    
    @staticmethod
    def kelly_criterion(win_rate: float, avg_win: float, avg_loss: float, 
                       capital: float, price: float, fraction: float = 0.5) -> float:
        """
        Kelly Criterion position sizing.
        
        Args:
            win_rate: Historical win rate (0-1)
            avg_win: Average winning return (%)
            avg_loss: Average losing return (%)
            capital: Total capital
            price: Current price
            fraction: Kelly fraction (default 0.5 for half-Kelly)
            
        Returns:
            Number of shares
        """
        if avg_loss == 0:
            return 0
        
        win_loss_ratio = avg_win / abs(avg_loss)
        kelly_percent = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
        kelly_percent = max(0, kelly_percent) * fraction * 100
        
        return PositionSizer.fixed_percent(capital, kelly_percent, price)
    
    @staticmethod
    def risk_based(capital: float, risk_percent: float, entry_price: float,
                  stop_loss: float) -> float:
        """
        Risk-based position sizing (fixed risk per trade).
        
        Args:
            capital: Total capital
            risk_percent: Percentage of capital to risk (0-100)
            entry_price: Entry price
            stop_loss: Stop loss price
            
        Returns:
            Number of shares
        """
        risk_amount = capital * (risk_percent / 100)
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk == 0:
            return 0
        
        return risk_amount / price_risk
    
    @staticmethod
    def volatility_based(capital: float, target_volatility: float, 
                        price: float, returns: pd.Series) -> float:
        """
        Volatility-based position sizing.
        
        Args:
            capital: Total capital
            target_volatility: Target portfolio volatility (annualized %)
            price: Current price
            returns: Historical returns series
            
        Returns:
            Number of shares
        """
        if len(returns) < 2:
            return 0
        
        # Calculate annualized volatility
        returns_std = returns.std()
        annual_vol = returns_std * np.sqrt(252)
        
        if annual_vol == 0:
            return 0
        
        # Scale position to achieve target volatility
        position_fraction = (target_volatility / 100) / annual_vol
        position_value = capital * position_fraction
        
        return position_value / price


class RiskManager:
    """
    Manage overall portfolio risk and implement risk controls.
    """
    
    def __init__(self, max_position_size: float = 0.2,
                 max_portfolio_risk: float = 0.02,
                 max_correlated_exposure: float = 0.4):
        """
        Initialize risk manager.
        
        Args:
            max_position_size: Maximum position as fraction of capital (default 20%)
            max_portfolio_risk: Maximum portfolio risk per trade (default 2%)
            max_correlated_exposure: Maximum exposure to correlated assets (default 40%)
        """
        self.max_position_size = max_position_size
        self.max_portfolio_risk = max_portfolio_risk
        self.max_correlated_exposure = max_correlated_exposure
    
    def check_position_size(self, position_value: float, capital: float) -> bool:
        """
        Check if position size is within limits.
        
        Args:
            position_value: Dollar value of position
            capital: Total capital
            
        Returns:
            True if position size is acceptable
        """
        position_fraction = position_value / capital
        return position_fraction <= self.max_position_size
    
    def check_portfolio_risk(self, risk_amount: float, capital: float) -> bool:
        """
        Check if trade risk is within limits.
        
        Args:
            risk_amount: Dollar amount at risk
            capital: Total capital
            
        Returns:
            True if risk is acceptable
        """
        risk_fraction = risk_amount / capital
        return risk_fraction <= self.max_portfolio_risk
    
    def calculate_max_drawdown(self, equity_curve: pd.Series) -> float:
        """
        Calculate maximum drawdown from equity curve.
        
        Args:
            equity_curve: Series of portfolio values over time
            
        Returns:
            Maximum drawdown as percentage
        """
        running_max = equity_curve.expanding().max()
        drawdown = (equity_curve - running_max) / running_max
        return abs(drawdown.min()) * 100
    
    def calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sharpe ratio.
        
        Args:
            returns: Series of returns
            risk_free_rate: Annual risk-free rate (default 2%)
            
        Returns:
            Sharpe ratio
        """
        if len(returns) < 2:
            return 0
        
        excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
        
        if excess_returns.std() == 0:
            return 0
        
        return np.sqrt(252) * (excess_returns.mean() / excess_returns.std())
    
    def calculate_sortino_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sortino ratio (like Sharpe but using downside deviation).
        
        Args:
            returns: Series of returns
            risk_free_rate: Annual risk-free rate (default 2%)
            
        Returns:
            Sortino ratio
        """
        if len(returns) < 2:
            return 0
        
        excess_returns = returns - (risk_free_rate / 252)
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0
        
        return np.sqrt(252) * (excess_returns.mean() / downside_returns.std())
    
    def check_diversification(self, positions: dict, correlations: pd.DataFrame) -> bool:
        """
        Check if portfolio is adequately diversified.
        
        Args:
            positions: Dict of ticker -> position weight
            correlations: Correlation matrix of returns
            
        Returns:
            True if diversification is adequate
        """
        # Calculate effective number of positions (Herfindahl index)
        weights = np.array(list(positions.values()))
        herfindahl = np.sum(weights ** 2)
        effective_positions = 1 / herfindahl
        
        # Should have at least 3 effective positions
        return effective_positions >= 3
