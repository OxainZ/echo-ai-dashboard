"""Unit tests for feature engineering."""

import pytest
import pandas as pd
import numpy as np
from echo.ml.feature_engineering import FeatureEngineer


class TestFeatureEngineer:
    """Test suite for feature engineering utilities."""
    
    @pytest.fixture
    def sample_prices(self):
        """Create sample price data for testing."""
        np.random.seed(42)
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        prices = 100 + np.cumsum(np.random.randn(100))
        return pd.Series(prices, index=dates)
    
    @pytest.fixture
    def sample_ohlcv(self):
        """Create sample OHLCV data."""
        np.random.seed(42)
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        df = pd.DataFrame({
            'Open': 100 + np.cumsum(np.random.randn(100)),
            'High': 102 + np.cumsum(np.random.randn(100)),
            'Low': 98 + np.cumsum(np.random.randn(100)),
            'Close': 100 + np.cumsum(np.random.randn(100)),
            'Volume': np.random.randint(1000000, 10000000, 100)
        }, index=dates)
        return df
    
    def test_rsi_calculation(self, sample_prices):
        """Test RSI calculation."""
        engineer = FeatureEngineer()
        rsi = engineer.calculate_rsi(sample_prices, period=14)
        
        assert isinstance(rsi, pd.Series)
        assert len(rsi) == len(sample_prices)
        # RSI should be between 0 and 100
        assert rsi.dropna().min() >= 0
        assert rsi.dropna().max() <= 100
    
    def test_macd_calculation(self, sample_prices):
        """Test MACD calculation."""
        engineer = FeatureEngineer()
        macd_df = engineer.calculate_macd(sample_prices)
        
        assert isinstance(macd_df, pd.DataFrame)
        assert 'MACD' in macd_df.columns
        assert 'Signal' in macd_df.columns
        assert 'Histogram' in macd_df.columns
        assert len(macd_df) == len(sample_prices)
    
    def test_bollinger_bands_calculation(self, sample_prices):
        """Test Bollinger Bands calculation."""
        engineer = FeatureEngineer()
        bb_df = engineer.calculate_bollinger_bands(sample_prices, period=20)
        
        assert isinstance(bb_df, pd.DataFrame)
        assert 'BB_Upper' in bb_df.columns
        assert 'BB_Middle' in bb_df.columns
        assert 'BB_Lower' in bb_df.columns
        
        # Upper band should be > Middle > Lower band
        valid_data = bb_df.dropna()
        assert (valid_data['BB_Upper'] >= valid_data['BB_Middle']).all()
        assert (valid_data['BB_Middle'] >= valid_data['BB_Lower']).all()
    
    def test_moving_averages(self, sample_prices):
        """Test moving averages calculation."""
        engineer = FeatureEngineer()
        sma_df = engineer.calculate_moving_averages(sample_prices, periods=[5, 10, 20])
        
        assert isinstance(sma_df, pd.DataFrame)
        assert 'SMA_5' in sma_df.columns
        assert 'SMA_10' in sma_df.columns
        assert 'SMA_20' in sma_df.columns
    
    def test_returns_calculation(self, sample_prices):
        """Test returns calculation."""
        engineer = FeatureEngineer()
        returns = engineer.calculate_returns(sample_prices)
        
        assert isinstance(returns, pd.Series)
        assert len(returns) == len(sample_prices)
        # First value should be NaN
        assert pd.isna(returns.iloc[0])
    
    def test_engineer_features_comprehensive(self, sample_ohlcv):
        """Test comprehensive feature engineering."""
        engineer = FeatureEngineer()
        result = engineer.engineer_features(sample_ohlcv)
        
        # Check that result has more columns than input
        assert len(result.columns) > len(sample_ohlcv.columns)
        
        # Check for expected features
        expected_features = ['RSI', 'MACD', 'Signal', 'BB_Upper', 'Returns', 'Volatility']
        for feature in expected_features:
            assert feature in result.columns
