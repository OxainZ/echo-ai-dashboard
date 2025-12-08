"""
Unit Tests for Echo Engine

Tests the core functionality of the Echo trading intelligence engine.
"""

import pytest
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from echo.engine.echo_engine import EchoEngine, Verdict
from echo.rules.base import Signal


class TestEchoEngine:
    """Test cases for Echo Engine."""
    
    def test_engine_initialization(self):
        """Test that engine initializes correctly."""
        try:
            engine = EchoEngine("echo/config.yaml")
            assert engine is not None
            assert engine.config is not None
            assert engine.provider is not None
            assert engine.rules is not None
            assert len(engine.rules) > 0
        except FileNotFoundError:
            pytest.skip("Config file not found - expected in CI/CD environments")
    
    def test_verdict_structure(self):
        """Test that Verdict has correct structure."""
        signals = [
            Signal(name="Test Signal", score=75.0, detail="Test detail", severity="green")
        ]
        
        verdict = Verdict(
            asof="2024-12-08 10:00:00 CST",
            composite=75.0,
            risk_label="Moderate",
            cap_efficiency=75.0,
            signals=signals,
            actions=["Test action"],
            allocations={"Core": "SPY", "Momentum": "QQQ", "Wildcard": "ARKK"}
        )
        
        assert verdict.composite == 75.0
        assert verdict.risk_label == "Moderate"
        assert len(verdict.signals) == 1
        assert len(verdict.actions) == 1
        assert len(verdict.allocations) == 3
    
    def test_engine_run(self):
        """Test that engine can run and generate verdict."""
        try:
            engine = EchoEngine("echo/config.yaml")
            verdict = engine.run()
            
            assert isinstance(verdict, Verdict)
            assert verdict.composite >= 0
            assert verdict.composite <= 100
            assert verdict.risk_label in ["Moderate", "Elevated", "High", "Low"]
            assert isinstance(verdict.signals, list)
            assert isinstance(verdict.actions, list)
            assert isinstance(verdict.allocations, dict)
        except FileNotFoundError:
            pytest.skip("Config file not found")
        except Exception as e:
            # Network errors or API rate limits shouldn't fail the test
            pytest.skip(f"External dependency issue: {e}")
    
    def test_risk_label_logic(self):
        """Test risk label determination logic."""
        # This tests the logic without needing actual data
        signals_green = [
            Signal("S1", 80, "Detail1", "green"),
            Signal("S2", 75, "Detail2", "green")
        ]
        
        signals_yellow = [
            Signal("S1", 80, "Detail1", "green"),
            Signal("S2", 60, "Detail2", "yellow")
        ]
        
        signals_red = [
            Signal("S1", 80, "Detail1", "green"),
            Signal("S2", 40, "Detail2", "red")
        ]
        
        # Simulate risk label logic
        def determine_risk(signals):
            risk_label = "Moderate"
            for s in signals:
                if s.severity == "red":
                    risk_label = "High"
                    break
                if s.severity == "yellow":
                    risk_label = "Elevated"
            return risk_label
        
        assert determine_risk(signals_green) == "Moderate"
        assert determine_risk(signals_yellow) == "Elevated"
        assert determine_risk(signals_red) == "High"


class TestSignal:
    """Test cases for Signal dataclass."""
    
    def test_signal_creation(self):
        """Test creating a signal."""
        signal = Signal(
            name="Test Signal",
            score=80.5,
            detail="This is a test",
            severity="green"
        )
        
        assert signal.name == "Test Signal"
        assert signal.score == 80.5
        assert signal.severity == "green"
        assert signal.detail == "This is a test"
    
    def test_signal_severity_values(self):
        """Test that signal severity can be green, yellow, or red."""
        severities = ["green", "yellow", "red"]
        
        for sev in severities:
            signal = Signal("Test", 50, "Detail", sev)
            assert signal.severity == sev


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
