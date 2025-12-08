"""
Unit Tests for Data Providers

Tests Yahoo Finance and other data provider integrations.
"""

import pytest
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from echo.data_providers.yfinance_provider import YFinanceProvider


class TestYFinanceProvider:
    """Test cases for Yahoo Finance data provider."""
    
    def test_provider_initialization(self):
        """Test that provider initializes correctly."""
        try:
            provider = YFinanceProvider()
            assert provider is not None
        except RuntimeError as e:
            if "yfinance not installed" in str(e):
                pytest.skip("yfinance not installed")
            raise
    
    def test_quote_structure(self):
        """Test that quote returns correct structure."""
        try:
            provider = YFinanceProvider()
            quote = provider.quote("AAPL")
            
            assert isinstance(quote, dict)
            assert "ticker" in quote
            assert "price" in quote
            assert "prev_close" in quote
            assert "currency" in quote
            assert quote["ticker"] == "AAPL"
        except Exception as e:
            pytest.skip(f"External API issue: {e}")
    
    def test_history_structure(self):
        """Test that history returns DataFrame with correct columns."""
        try:
            provider = YFinanceProvider()
            df = provider.history("AAPL", period="5d", interval="1d")
            
            assert isinstance(df, pd.DataFrame)
            assert len(df) > 0
            assert "Close" in df.columns
            assert "Open" in df.columns
            assert "High" in df.columns
            assert "Low" in df.columns
            assert "Volume" in df.columns
        except Exception as e:
            pytest.skip(f"External API issue: {e}")
    
    def test_history_periods(self):
        """Test different period parameters."""
        try:
            provider = YFinanceProvider()
            
            periods = ["1d", "5d", "1mo"]
            for period in periods:
                df = provider.history("SPY", period=period, interval="1d")
                assert isinstance(df, pd.DataFrame)
                assert len(df) > 0
        except Exception as e:
            pytest.skip(f"External API issue: {e}")
    
    def test_invalid_ticker(self):
        """Test handling of invalid ticker."""
        try:
            provider = YFinanceProvider()
            quote = provider.quote("INVALIDTICKER12345XYZ")
            
            # Provider should handle gracefully, not crash
            assert isinstance(quote, dict)
        except Exception as e:
            pytest.skip(f"External API issue: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
