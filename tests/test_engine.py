"""
Unit tests for Echo Engine core functionality

Tests the main engine, signal generation, and verdict creation.
"""
import pytest

from echo.engine.echo_engine import EchoEngine, Verdict
from echo.rules.base import Signal, Rule


class MockRule(Rule):
    """Mock rule for testing"""
    
    def __init__(self, score: float = 50.0, severity: str = "green"):
        self.score = score
        self.severity = severity
    
    def run(self, context) -> Signal:
        return Signal(
            name="Mock Signal",
            score=self.score,
            detail="Test signal",
            severity=self.severity
        )


def test_signal_creation():
    """Test Signal dataclass creation"""
    signal = Signal(
        name="Test Signal",
        score=75.0,
        detail="Test detail",
        severity="green"
    )
    
    assert signal.name == "Test Signal"
    assert signal.score == 75.0
    assert signal.detail == "Test detail"
    assert signal.severity == "green"


def test_signal_default_severity():
    """Test Signal default severity"""
    signal = Signal(
        name="Test",
        score=50.0,
        detail="Detail"
    )
    
    assert signal.severity == "green"


def test_verdict_creation():
    """Test Verdict creation"""
    signals = [
        Signal("Signal 1", 60.0, "Detail 1", "green"),
        Signal("Signal 2", 80.0, "Detail 2", "yellow")
    ]
    
    verdict = Verdict(
        asof="2024-01-01",
        composite=70.0,
        risk_label="Moderate",
        cap_efficiency=85.0,
        signals=signals,
        actions=["Action 1"],
        allocations={"Core": "QQQ"}
    )
    
    assert verdict.composite == 70.0
    assert verdict.risk_label == "Moderate"
    assert len(verdict.signals) == 2
    assert len(verdict.actions) == 1


def test_rule_must_implement_run():
    """Test that Rule.run() must be implemented"""
    rule = Rule()
    
    with pytest.raises(NotImplementedError):
        rule.run({})


def test_mock_rule():
    """Test MockRule implementation"""
    rule = MockRule(score=75.0, severity="yellow")
    signal = rule.run({})
    
    assert signal.score == 75.0
    assert signal.severity == "yellow"
    assert signal.name == "Mock Signal"


# Note: Full engine tests require config file
# These would be integration tests
def test_engine_initialization_without_config():
    """Test that engine requires valid config"""
    with pytest.raises(FileNotFoundError):
        engine = EchoEngine("nonexistent_config.yaml")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
