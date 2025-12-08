"""
Trading Decision Engine

Implements advanced trading logic with risk management, position sizing, and portfolio optimization.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import numpy as np
from datetime import datetime


class TradeAction(Enum):
    """Trading action types"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"


@dataclass
class TradeSignal:
    """
    Trading signal with decision and parameters
    """
    action: TradeAction
    ticker: str
    confidence: float  # 0.0 to 1.0
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    position_size: Optional[float] = None
    reasoning: str = ""
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class RiskManager:
    """
    Risk management for trading decisions
    
    Features:
    - Position sizing based on risk tolerance
    - Stop-loss calculation
    - Take-profit targets
    - Portfolio risk assessment
    """
    
    def __init__(self, config: Optional[Dict] = None):
        default_config = {
            'max_position_size': 0.2,  # Max 20% of portfolio per position
            'risk_per_trade': 0.02,     # Risk 2% per trade
            'stop_loss_pct': 0.05,      # 5% stop loss
            'take_profit_ratio': 2.0,   # 2:1 reward:risk ratio
            'max_portfolio_risk': 0.10, # Max 10% portfolio at risk
            'max_correlation': 0.7,     # Max correlation between positions
        }
        self.config = default_config
        if config:
            self.config.update(config)
    
    def calculate_position_size(self, portfolio_value: float, entry_price: float,
                                stop_loss_price: float) -> float:
        """
        Calculate position size based on risk parameters
        
        Args:
            portfolio_value: Total portfolio value
            entry_price: Entry price for the position
            stop_loss_price: Stop loss price
            
        Returns:
            Position size in shares
        """
        # Calculate risk per share
        risk_per_share = abs(entry_price - stop_loss_price)
        
        # Calculate dollar risk
        dollar_risk = portfolio_value * self.config['risk_per_trade']
        
        # Calculate position size
        position_size = dollar_risk / risk_per_share
        
        # Apply max position size constraint
        max_shares = (portfolio_value * self.config['max_position_size']) / entry_price
        position_size = min(position_size, max_shares)
        
        return max(0, position_size)
    
    def calculate_stop_loss(self, entry_price: float, is_long: bool = True) -> float:
        """
        Calculate stop loss price
        
        Args:
            entry_price: Entry price
            is_long: True for long position, False for short
            
        Returns:
            Stop loss price
        """
        stop_loss_pct = self.config['stop_loss_pct']
        
        if is_long:
            return entry_price * (1 - stop_loss_pct)
        else:
            return entry_price * (1 + stop_loss_pct)
    
    def calculate_take_profit(self, entry_price: float, stop_loss_price: float,
                             is_long: bool = True) -> float:
        """
        Calculate take profit price based on risk:reward ratio
        
        Args:
            entry_price: Entry price
            stop_loss_price: Stop loss price
            is_long: True for long position, False for short
            
        Returns:
            Take profit price
        """
        risk = abs(entry_price - stop_loss_price)
        reward = risk * self.config['take_profit_ratio']
        
        if is_long:
            return entry_price + reward
        else:
            return entry_price - reward
    
    def assess_portfolio_risk(self, positions: List[Dict]) -> Dict[str, float]:
        """
        Assess overall portfolio risk
        
        Args:
            positions: List of current positions
            
        Returns:
            Dictionary with risk metrics
        """
        if not positions:
            return {'total_risk': 0.0, 'risk_utilization': 0.0}
        
        total_value = sum(p.get('value', 0) for p in positions)
        total_risk = sum(
            p.get('value', 0) * self.config['stop_loss_pct']
            for p in positions
        )
        
        risk_pct = total_risk / total_value if total_value > 0 else 0
        risk_utilization = risk_pct / self.config['max_portfolio_risk']
        
        return {
            'total_risk': total_risk,
            'risk_percentage': risk_pct,
            'risk_utilization': risk_utilization,
            'max_risk_allowed': self.config['max_portfolio_risk']
        }
    
    def validate_trade(self, signal: TradeSignal, portfolio_value: float,
                      current_positions: List[Dict]) -> Tuple[bool, str]:
        """
        Validate if a trade should be executed based on risk parameters
        
        Args:
            signal: Trade signal
            portfolio_value: Current portfolio value
            current_positions: List of current positions
            
        Returns:
            (is_valid, reason)
        """
        # Check portfolio risk
        risk_assessment = self.assess_portfolio_risk(current_positions)
        if risk_assessment['risk_utilization'] >= 1.0:
            return False, "Portfolio risk limit reached"
        
        # Check position size
        if signal.position_size:
            position_value = signal.position_size * (signal.target_price or 0)
            if position_value > portfolio_value * self.config['max_position_size']:
                return False, "Position size exceeds maximum allowed"
        
        # Check confidence
        if signal.confidence < 0.5:
            return False, "Confidence too low"
        
        return True, "Trade validated"


class TradingDecisionEngine:
    """
    Main trading decision engine
    
    Combines AI predictions, technical analysis, and risk management
    to generate trading signals.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.risk_manager = RiskManager(config)
    
    def generate_signal(self, ticker: str, current_price: float,
                       ai_prediction: float, ai_confidence: float,
                       technical_score: float, portfolio_value: float) -> TradeSignal:
        """
        Generate trading signal based on multiple factors
        
        Args:
            ticker: Stock symbol
            current_price: Current market price
            ai_prediction: AI model's price prediction
            ai_confidence: AI model's confidence (0-1)
            technical_score: Technical analysis score (0-100)
            portfolio_value: Current portfolio value
            
        Returns:
            TradeSignal with decision and parameters
        """
        # Calculate expected return
        expected_return = (ai_prediction - current_price) / current_price
        
        # Normalize technical score to 0-1
        tech_confidence = technical_score / 100.0
        
        # Combine AI and technical confidence
        combined_confidence = (ai_confidence * 0.6) + (tech_confidence * 0.4)
        
        # Decision logic
        action = TradeAction.HOLD
        reasoning = "No clear signal"
        
        if expected_return > 0.03 and combined_confidence > 0.6:
            # Strong buy signal
            action = TradeAction.BUY
            reasoning = f"Expected return: {expected_return:.2%}, High confidence: {combined_confidence:.2f}"
        elif expected_return < -0.03 and combined_confidence > 0.6:
            # Strong sell signal
            action = TradeAction.SELL
            reasoning = f"Expected loss: {expected_return:.2%}, High confidence: {combined_confidence:.2f}"
        elif abs(expected_return) < 0.02:
            # Hold signal
            action = TradeAction.HOLD
            reasoning = f"Expected change minimal: {expected_return:.2%}"
        
        # Calculate stop loss and take profit
        stop_loss = self.risk_manager.calculate_stop_loss(current_price)
        take_profit = self.risk_manager.calculate_take_profit(current_price, stop_loss)
        
        # Calculate position size for buy signals
        position_size = None
        if action == TradeAction.BUY:
            position_size = self.risk_manager.calculate_position_size(
                portfolio_value, current_price, stop_loss
            )
        
        return TradeSignal(
            action=action,
            ticker=ticker,
            confidence=combined_confidence,
            target_price=take_profit if action == TradeAction.BUY else None,
            stop_loss=stop_loss if action == TradeAction.BUY else None,
            position_size=position_size,
            reasoning=reasoning
        )
    
    def check_exit_conditions(self, position: Dict) -> Optional[TradeSignal]:
        """
        Check if exit conditions are met for a position
        
        Args:
            position: Current position info
            
        Returns:
            Exit signal if conditions met, None otherwise
        """
        ticker = position.get('ticker')
        current_price = position.get('current_price', 0)
        entry_price = position.get('entry_price', 0)
        stop_loss = position.get('stop_loss', 0)
        take_profit = position.get('take_profit', 0)
        
        # Check stop loss
        if current_price <= stop_loss:
            return TradeSignal(
                action=TradeAction.STOP_LOSS,
                ticker=ticker,
                confidence=1.0,
                reasoning=f"Stop loss triggered at {current_price:.2f}"
            )
        
        # Check take profit
        if current_price >= take_profit:
            return TradeSignal(
                action=TradeAction.TAKE_PROFIT,
                ticker=ticker,
                confidence=1.0,
                reasoning=f"Take profit target reached at {current_price:.2f}"
            )
        
        return None
    
    def optimize_portfolio_allocation(self, signals: List[TradeSignal],
                                     portfolio_value: float) -> Dict[str, float]:
        """
        Optimize allocation across multiple signals
        
        Args:
            signals: List of trade signals
            portfolio_value: Total portfolio value
            
        Returns:
            Dictionary of ticker -> allocation percentage
        """
        # Filter to only BUY signals
        buy_signals = [s for s in signals if s.action == TradeAction.BUY]
        
        if not buy_signals:
            return {}
        
        # Weight by confidence
        total_confidence = sum(s.confidence for s in buy_signals)
        
        allocations = {}
        for signal in buy_signals:
            weight = signal.confidence / total_confidence
            # Apply max position size constraint
            allocation = min(weight, self.risk_manager.config['max_position_size'])
            allocations[signal.ticker] = allocation
        
        # Normalize to sum to 1.0 (or less)
        total_allocation = sum(allocations.values())
        if total_allocation > 1.0:
            allocations = {k: v/total_allocation for k, v in allocations.items()}
        
        return allocations
    
    def backtest_signal(self, signal: TradeSignal, historical_prices: np.ndarray) -> Dict:
        """
        Backtest a signal against historical data
        
        Args:
            signal: Trading signal
            historical_prices: Array of historical prices
            
        Returns:
            Dictionary with backtest results
        """
        if signal.action != TradeAction.BUY or len(historical_prices) == 0:
            return {'return': 0.0, 'success': False}
        
        entry_price = historical_prices[0]
        stop_loss = signal.stop_loss or entry_price * 0.95
        take_profit = signal.target_price or entry_price * 1.10
        
        # Simulate holding the position
        for price in historical_prices[1:]:
            if price <= stop_loss:
                return_pct = (price - entry_price) / entry_price
                return {'return': return_pct, 'success': False, 'exit': 'stop_loss'}
            elif price >= take_profit:
                return_pct = (price - entry_price) / entry_price
                return {'return': return_pct, 'success': True, 'exit': 'take_profit'}
        
        # Position still open
        final_return = (historical_prices[-1] - entry_price) / entry_price
        return {'return': final_return, 'success': final_return > 0, 'exit': 'ongoing'}
