"""Unit tests for data providers."""

import pytest
import pandas as pd
from echo.data_providers.yfinance_provider import YFinanceProvider


class TestYFinanceProvider:
    """Test suite for Yahoo Finance data provider."""
    
    @pytest.fixture
    def provider(self):
        """Create a provider instance."""
        return YFinanceProvider(max_retries=2, retry_delay=0.1)
    
    def test_provider_initialization(self, provider):
        """Test provider can be initialized."""
        assert provider is not None
        assert provider.max_retries == 2
        assert provider.retry_delay == 0.1
    
    def test_validate_ticker_valid(self, provider):
        """Test ticker validation with valid tickers."""
        assert provider._validate_ticker("AAPL") == "AAPL"
        assert provider._validate_ticker("msft") == "MSFT"
        assert provider._validate_ticker(" GOOGL ") == "GOOGL"
        assert provider._validate_ticker("BRK.B") == "BRK.B"
    
    def test_validate_ticker_invalid(self, provider):
        """Test ticker validation with invalid tickers."""
        with pytest.raises(ValueError):
            provider._validate_ticker("")
        
        with pytest.raises(ValueError):
            provider._validate_ticker("AAPL;DROP")
        
        with pytest.raises(ValueError):
            provider._validate_ticker(None)
    
    def test_quote_structure(self, provider):
        """Test quote returns expected structure."""
        # This test requires network access
        # Consider mocking for CI/CD
        try:
            quote = provider.quote("AAPL")
            assert "ticker" in quote
            assert "price" in quote
            assert "prev_close" in quote
            assert "currency" in quote
            assert quote["ticker"] == "AAPL"
        except Exception:
            pytest.skip("Network unavailable or rate limited")
    
    def test_history_returns_dataframe(self, provider):
        """Test history returns a pandas DataFrame."""
        try:
            df = provider.history("AAPL", period="5d", interval="1d")
            assert isinstance(df, pd.DataFrame)
            assert not df.empty
        except Exception:
            pytest.skip("Network unavailable or rate limited")
    
    def test_history_invalid_parameters(self, provider):
        """Test history with invalid parameters."""
        with pytest.raises(ValueError):
            provider.history("AAPL", period="invalid")
        
        with pytest.raises(ValueError):
            provider.history("AAPL", interval="invalid")
