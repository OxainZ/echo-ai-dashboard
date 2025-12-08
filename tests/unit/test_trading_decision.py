"""
Unit tests for Trading Decision Engine
"""

import pytest
import numpy as np
from echo.engine.trading_decision import (
    TradeAction, TradeSignal, RiskManager, TradingDecisionEngine
)


class TestTradeSignal:
    """Test TradeSignal class"""
    
    def test_signal_creation(self):
        """Test creating a trade signal"""
        signal = TradeSignal(
            action=TradeAction.BUY,
            ticker="AAPL",
            confidence=0.85,
            target_price=150.0,
            stop_loss=140.0,
            position_size=10
        )
        
        assert signal.action == TradeAction.BUY
        assert signal.ticker == "AAPL"
        assert signal.confidence == 0.85
        assert signal.timestamp != ""
    
    def test_signal_with_reasoning(self):
        """Test signal with reasoning"""
        signal = TradeSignal(
            action=TradeAction.SELL,
            ticker="TSLA",
            confidence=0.7,
            reasoning="Technical indicators suggest overbought"
        )
        
        assert signal.reasoning == "Technical indicators suggest overbought"


class TestRiskManager:
    """Test RiskManager class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.risk_manager = RiskManager({
            'max_position_size': 0.2,
            'risk_per_trade': 0.02,
            'stop_loss_pct': 0.05,
            'take_profit_ratio': 2.0
        })
    
    def test_calculate_position_size(self):
        """Test position size calculation"""
        portfolio_value = 10000
        entry_price = 100
        stop_loss_price = 95
        
        position_size = self.risk_manager.calculate_position_size(
            portfolio_value, entry_price, stop_loss_price
        )
        
        # Position size should be positive
        assert position_size > 0
        
        # Position should not exceed max position size
        max_shares = (portfolio_value * 0.2) / entry_price
        assert position_size <= max_shares
    
    def test_calculate_stop_loss_long(self):
        """Test stop loss calculation for long position"""
        entry_price = 100
        stop_loss = self.risk_manager.calculate_stop_loss(entry_price, is_long=True)
        
        # Stop loss should be below entry price
        assert stop_loss < entry_price
        
        # Should be approximately 5% below
        expected = entry_price * 0.95
        assert abs(stop_loss - expected) < 0.01
    
    def test_calculate_stop_loss_short(self):
        """Test stop loss calculation for short position"""
        entry_price = 100
        stop_loss = self.risk_manager.calculate_stop_loss(entry_price, is_long=False)
        
        # Stop loss should be above entry price for short
        assert stop_loss > entry_price
        
        # Should be approximately 5% above
        expected = entry_price * 1.05
        assert abs(stop_loss - expected) < 0.01
    
    def test_calculate_take_profit(self):
        """Test take profit calculation"""
        entry_price = 100
        stop_loss_price = 95
        
        take_profit = self.risk_manager.calculate_take_profit(
            entry_price, stop_loss_price, is_long=True
        )
        
        # Take profit should be above entry
        assert take_profit > entry_price
        
        # Reward should be 2x risk
        risk = entry_price - stop_loss_price
        reward = take_profit - entry_price
        assert abs(reward / risk - 2.0) < 0.01
    
    def test_assess_portfolio_risk_empty(self):
        """Test risk assessment with no positions"""
        risk = self.risk_manager.assess_portfolio_risk([])
        
        assert risk['total_risk'] == 0.0
        assert risk['risk_utilization'] == 0.0
    
    def test_assess_portfolio_risk_with_positions(self):
        """Test risk assessment with positions"""
        positions = [
            {'ticker': 'AAPL', 'value': 1000},
            {'ticker': 'GOOGL', 'value': 1500}
        ]
        
        risk = self.risk_manager.assess_portfolio_risk(positions)
        
        assert risk['total_risk'] > 0
        assert 'risk_percentage' in risk
        assert 'risk_utilization' in risk
    
    def test_validate_trade_success(self):
        """Test trade validation success"""
        signal = TradeSignal(
            action=TradeAction.BUY,
            ticker="AAPL",
            confidence=0.8,
            target_price=150.0,
            stop_loss=140.0,
            position_size=10
        )
        
        is_valid, reason = self.risk_manager.validate_trade(
            signal, 10000, []
        )
        
        assert is_valid is True
    
    def test_validate_trade_low_confidence(self):
        """Test trade validation with low confidence"""
        signal = TradeSignal(
            action=TradeAction.BUY,
            ticker="AAPL",
            confidence=0.3,
            target_price=150.0
        )
        
        is_valid, reason = self.risk_manager.validate_trade(
            signal, 10000, []
        )
        
        assert is_valid is False
        assert "confidence" in reason.lower()


class TestTradingDecisionEngine:
    """Test TradingDecisionEngine class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.engine = TradingDecisionEngine()
    
    def test_generate_buy_signal(self):
        """Test generating buy signal"""
        signal = self.engine.generate_signal(
            ticker="AAPL",
            current_price=100.0,
            ai_prediction=110.0,  # 10% expected return
            ai_confidence=0.8,
            technical_score=75,
            portfolio_value=10000
        )
        
        assert signal.action == TradeAction.BUY
        assert signal.ticker == "AAPL"
        assert signal.confidence > 0
        assert signal.stop_loss is not None
        assert signal.target_price is not None
    
    def test_generate_sell_signal(self):
        """Test generating sell signal"""
        signal = self.engine.generate_signal(
            ticker="TSLA",
            current_price=200.0,
            ai_prediction=180.0,  # -10% expected return
            ai_confidence=0.8,
            technical_score=20,
            portfolio_value=10000
        )
        
        assert signal.action == TradeAction.SELL
        assert signal.ticker == "TSLA"
    
    def test_generate_hold_signal(self):
        """Test generating hold signal"""
        signal = self.engine.generate_signal(
            ticker="GOOGL",
            current_price=100.0,
            ai_prediction=101.0,  # Only 1% expected return
            ai_confidence=0.5,
            technical_score=50,
            portfolio_value=10000
        )
        
        assert signal.action == TradeAction.HOLD
    
    def test_check_exit_stop_loss(self):
        """Test stop loss exit condition"""
        position = {
            'ticker': 'AAPL',
            'entry_price': 100,
            'current_price': 94,  # Below stop loss
            'stop_loss': 95,
            'take_profit': 110
        }
        
        exit_signal = self.engine.check_exit_conditions(position)
        
        assert exit_signal is not None
        assert exit_signal.action == TradeAction.STOP_LOSS
    
    def test_check_exit_take_profit(self):
        """Test take profit exit condition"""
        position = {
            'ticker': 'AAPL',
            'entry_price': 100,
            'current_price': 111,  # Above take profit
            'stop_loss': 95,
            'take_profit': 110
        }
        
        exit_signal = self.engine.check_exit_conditions(position)
        
        assert exit_signal is not None
        assert exit_signal.action == TradeAction.TAKE_PROFIT
    
    def test_check_exit_no_action(self):
        """Test no exit when conditions not met"""
        position = {
            'ticker': 'AAPL',
            'entry_price': 100,
            'current_price': 105,  # Between stop and target
            'stop_loss': 95,
            'take_profit': 110
        }
        
        exit_signal = self.engine.check_exit_conditions(position)
        
        assert exit_signal is None
    
    def test_optimize_portfolio_allocation(self):
        """Test portfolio optimization"""
        signals = [
            TradeSignal(TradeAction.BUY, "AAPL", 0.8),
            TradeSignal(TradeAction.BUY, "GOOGL", 0.6),
            TradeSignal(TradeAction.BUY, "MSFT", 0.7)
        ]
        
        allocations = self.engine.optimize_portfolio_allocation(signals, 10000)
        
        # Should have allocations for all buy signals
        assert len(allocations) == 3
        
        # Total allocation should not exceed 1.0
        assert sum(allocations.values()) <= 1.0
        
        # Higher confidence should get more allocation
        assert allocations["AAPL"] >= allocations["GOOGL"]
    
    def test_optimize_portfolio_no_buy_signals(self):
        """Test optimization with no buy signals"""
        signals = [
            TradeSignal(TradeAction.SELL, "AAPL", 0.8),
            TradeSignal(TradeAction.HOLD, "GOOGL", 0.6)
        ]
        
        allocations = self.engine.optimize_portfolio_allocation(signals, 10000)
        
        assert len(allocations) == 0
    
    def test_backtest_signal_success(self):
        """Test backtesting successful trade"""
        signal = TradeSignal(
            action=TradeAction.BUY,
            ticker="AAPL",
            confidence=0.8,
            target_price=110.0,
            stop_loss=95.0
        )
        
        # Simulate price reaching target
        historical_prices = np.array([100, 102, 105, 108, 110, 112])
        
        result = self.engine.backtest_signal(signal, historical_prices)
        
        assert result['success'] is True
        assert result['exit'] == 'take_profit'
        assert result['return'] > 0
    
    def test_backtest_signal_stop_loss(self):
        """Test backtesting failed trade"""
        signal = TradeSignal(
            action=TradeAction.BUY,
            ticker="AAPL",
            confidence=0.8,
            target_price=110.0,
            stop_loss=95.0
        )
        
        # Simulate price hitting stop loss
        historical_prices = np.array([100, 98, 96, 94, 92])
        
        result = self.engine.backtest_signal(signal, historical_prices)
        
        assert result['success'] is False
        assert result['exit'] == 'stop_loss'
        assert result['return'] < 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
