"""
Unit Tests for Echo AI Dashboard Core Modules
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from echo.ai_models import (
    LSTMStockPredictor, 
    SentimentAnalyzer,
    calculate_technical_indicators
)


@pytest.fixture
def sample_stock_data():
    """Generate sample stock data for testing - shared fixture."""
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    np.random.seed(42)
    
    data = pd.DataFrame({
        'Open': 100 + np.random.randn(len(dates)).cumsum(),
        'High': 102 + np.random.randn(len(dates)).cumsum(),
        'Low': 98 + np.random.randn(len(dates)).cumsum(),
        'Close': 100 + np.random.randn(len(dates)).cumsum(),
        'Volume': np.random.randint(1000000, 5000000, len(dates))
    }, index=dates)
    
    return data


class TestLSTMStockPredictor:
    """Test suite for LSTM stock predictor."""
    
    @pytest.fixture
    def predictor(self):
        """Create a predictor instance."""
        return LSTMStockPredictor(lookback_days=60, prediction_horizon=5)
    
    def test_initialization(self, predictor):
        """Test predictor initialization."""
        assert predictor.lookback_days == 60
        assert predictor.prediction_horizon == 5
        assert not predictor.is_trained
        assert 'Close' in predictor.features
    
    def test_train(self, predictor, sample_stock_data):
        """Test model training."""
        history = predictor.train(sample_stock_data, epochs=10, batch_size=32)
        
        assert predictor.is_trained
        assert 'loss' in history


class TestSentimentAnalyzer:
    """Test suite for sentiment analyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance."""
        return SentimentAnalyzer()
    
    def test_initialization(self, analyzer):
        """Test analyzer initialization."""
        assert analyzer.sentiment_history == []


class TestTechnicalIndicators:
    """Test suite for technical indicators."""
    
    def test_calculate_indicators_default(self, sample_stock_data):
        """Test calculating indicators with default periods."""
        result = calculate_technical_indicators(sample_stock_data)
        
        assert 'SMA_20' in result.columns
        assert 'RSI' in result.columns


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
