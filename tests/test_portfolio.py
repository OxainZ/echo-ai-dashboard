"""Tests for portfolio tracker"""
import pytest
from echo.portfolio.tracker import PortfolioTracker, Position


def test_portfolio_initialization():
    """Test portfolio tracker initialization"""
    tracker = PortfolioTracker(initial_cash=10000)
    assert tracker.cash == 10000
    assert len(tracker.positions) == 0
    assert len(tracker.transactions) == 0


def test_add_position():
    """Test adding a position to portfolio"""
    tracker = PortfolioTracker(initial_cash=10000)
    success = tracker.add_position("AAPL", shares=10, price=150.0)
    
    assert success is True
    assert "AAPL" in tracker.positions
    assert tracker.positions["AAPL"].shares == 10
    assert tracker.positions["AAPL"].avg_cost == 150.0
    assert tracker.cash == 10000 - (10 * 150.0)


def test_remove_position():
    """Test removing a position from portfolio"""
    tracker = PortfolioTracker(initial_cash=10000)
    tracker.add_position("AAPL", shares=10, price=150.0)
    
    success = tracker.remove_position("AAPL", shares=5, price=160.0)
    assert success is True
    assert tracker.positions["AAPL"].shares == 5
    assert tracker.cash == 10000 - 1500 + 800  # Initial - buy + sell


def test_position_pnl():
    """Test position P&L calculation"""
    position = Position("AAPL", shares=10, avg_cost=150.0)
    
    # Test unrealized P&L
    current_price = 160.0
    pnl = position.get_unrealized_pnl(current_price)
    assert pnl == 100.0  # (160 - 150) * 10
    
    # Test return percentage
    return_pct = position.get_return_pct(current_price)
    assert abs(return_pct - 6.67) < 0.1  # ~6.67%


def test_portfolio_metrics():
    """Test portfolio performance metrics"""
    tracker = PortfolioTracker(initial_cash=10000)
    tracker.add_position("AAPL", shares=10, price=150.0)
    tracker.add_position("TSLA", shares=5, price=200.0)
    
    current_prices = {"AAPL": 160.0, "TSLA": 220.0}
    metrics = tracker.get_performance_metrics(current_prices)
    
    assert 'total_value' in metrics
    assert 'total_return_pct' in metrics
    assert 'num_positions' in metrics
    assert metrics['num_positions'] == 2


def test_risk_metrics():
    """Test portfolio risk metrics"""
    tracker = PortfolioTracker(initial_cash=10000)
    tracker.add_position("AAPL", shares=10, price=150.0)
    
    current_prices = {"AAPL": 160.0}
    risk = tracker.get_risk_metrics(current_prices)
    
    assert 'risk_level' in risk
    assert 'max_concentration' in risk
    assert 'cash_buffer_pct' in risk
    assert risk['num_positions'] == 1


def test_allocation():
    """Test portfolio allocation calculation"""
    tracker = PortfolioTracker(initial_cash=10000)
    tracker.add_position("AAPL", shares=10, price=150.0)
    tracker.add_position("TSLA", shares=5, price=200.0)
    
    current_prices = {"AAPL": 160.0, "TSLA": 220.0}
    allocation = tracker.get_allocation(current_prices)
    
    assert 'AAPL' in allocation
    assert 'TSLA' in allocation
    assert 'CASH' in allocation
    
    # Total allocation should be 100%
    total = sum(allocation.values())
    assert abs(total - 100) < 0.1
