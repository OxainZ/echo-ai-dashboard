"""
Unit Tests for ML Models

Tests machine learning models and preprocessing utilities.
"""

import pytest
import sys
import os
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from echo.ml.base import BasePredictor, Prediction, ModelRegistry
from echo.ml.lstm_predictor import LSTMPredictor
from echo.ml.transformer_predictor import TransformerPredictor
from echo.ml.data_preprocessing import FinancialDataPreprocessor, FeatureEngineer


class TestPrediction:
    """Test Prediction dataclass."""
    
    def test_prediction_creation(self):
        """Test creating a prediction object."""
        from datetime import datetime
        
        pred = Prediction(
            timestamp=datetime.now(),
            ticker="AAPL",
            prediction_horizon="1d",
            predicted_price=150.0,
            confidence=0.85,
            direction="up",
            probability=0.75
        )
        
        assert pred.ticker == "AAPL"
        assert pred.predicted_price == 150.0
        assert pred.confidence == 0.85
        assert pred.direction == "up"


class TestLSTMPredictor:
    """Test LSTM predictor."""
    
    def test_lstm_initialization(self):
        """Test LSTM model initialization."""
        model = LSTMPredictor(sequence_length=60, hidden_units=128)
        
        assert model.model_name == "LSTM_Predictor"
        assert model.sequence_length == 60
        assert model.hidden_units == 128
        assert not model.is_trained
    
    def test_lstm_train(self):
        """Test LSTM training (stub)."""
        model = LSTMPredictor()
        
        # Create dummy data
        X = pd.DataFrame(np.random.rand(100, 5), columns=['f1', 'f2', 'f3', 'f4', 'f5'])
        y = pd.Series(np.random.rand(100))
        
        metrics = model.train(X, y, epochs=5)
        
        assert isinstance(metrics, dict)
        assert 'loss' in metrics
        assert model.is_trained
    
    def test_lstm_predict(self):
        """Test LSTM prediction."""
        model = LSTMPredictor()
        
        # Train first (stub training)
        X = pd.DataFrame(np.random.rand(100, 5))
        y = pd.Series(np.random.rand(100))
        model.train(X, y, epochs=5)
        
        # Make prediction
        prediction = model.predict("AAPL", horizon="1d")
        
        assert isinstance(prediction, Prediction)
        assert prediction.ticker == "AAPL"
        assert prediction.predicted_price > 0
        assert 0 <= prediction.confidence <= 1


class TestTransformerPredictor:
    """Test Transformer predictor."""
    
    def test_transformer_initialization(self):
        """Test Transformer initialization."""
        model = TransformerPredictor(d_model=128, num_heads=8, num_layers=4)
        
        assert model.model_name == "Transformer_Predictor"
        assert model.d_model == 128
        assert model.num_heads == 8
        assert model.num_layers == 4
    
    def test_transformer_train(self):
        """Test Transformer training (stub)."""
        model = TransformerPredictor()
        
        X = pd.DataFrame(np.random.rand(100, 5))
        y = pd.Series(np.random.rand(100))
        
        metrics = model.train(X, y, epochs=5)
        
        assert isinstance(metrics, dict)
        assert model.is_trained


class TestDataPreprocessing:
    """Test data preprocessing utilities."""
    
    def test_preprocessor_initialization(self):
        """Test preprocessor initialization."""
        preprocessor = FinancialDataPreprocessor(lookback_window=60)
        
        assert preprocessor.lookback_window == 60
    
    def test_add_technical_indicators(self):
        """Test adding technical indicators."""
        # Create dummy OHLCV data
        dates = pd.date_range('2023-01-01', periods=100)
        df = pd.DataFrame({
            'Open': np.random.uniform(100, 110, 100),
            'High': np.random.uniform(110, 120, 100),
            'Low': np.random.uniform(90, 100, 100),
            'Close': np.random.uniform(100, 110, 100),
            'Volume': np.random.uniform(1000000, 5000000, 100)
        }, index=dates)
        
        preprocessor = FinancialDataPreprocessor()
        df_with_indicators = preprocessor.add_technical_indicators(df)
        
        # Check that indicators were added
        assert 'SMA_5' in df_with_indicators.columns
        assert 'SMA_20' in df_with_indicators.columns
        assert 'RSI' in df_with_indicators.columns
        assert 'MACD' in df_with_indicators.columns
    
    def test_handle_missing_values(self):
        """Test handling missing values."""
        df = pd.DataFrame({
            'Close': [100, np.nan, 102, np.nan, 104],
            'Volume': [1000, 1100, np.nan, 1300, 1400]
        })
        
        preprocessor = FinancialDataPreprocessor()
        df_clean = preprocessor.handle_missing_values(df, method='ffill')
        
        # Check no NaN values remain
        assert not df_clean.isnull().any().any()
    
    def test_train_test_split(self):
        """Test train/test splitting."""
        df = pd.DataFrame({
            'Close': np.random.rand(100),
            'Volume': np.random.rand(100)
        })
        
        preprocessor = FinancialDataPreprocessor()
        train_df, test_df = preprocessor.split_train_test(df, test_size=0.2)
        
        assert len(train_df) == 80
        assert len(test_df) == 20
        assert len(train_df) + len(test_df) == len(df)


class TestFeatureEngineer:
    """Test feature engineering utilities."""
    
    def test_add_lagged_features(self):
        """Test adding lagged features."""
        df = pd.DataFrame({
            'Close': np.random.rand(50),
            'Volume': np.random.rand(50)
        })
        
        df_lagged = FeatureEngineer.add_lagged_features(df, ['Close'], [1, 2, 3])
        
        assert 'Close_lag_1' in df_lagged.columns
        assert 'Close_lag_2' in df_lagged.columns
        assert 'Close_lag_3' in df_lagged.columns
    
    def test_add_time_features(self):
        """Test adding time-based features."""
        dates = pd.date_range('2023-01-01', periods=100)
        df = pd.DataFrame({
            'Close': np.random.rand(100)
        }, index=dates)
        
        df_time = FeatureEngineer.add_time_features(df)
        
        assert 'day_of_week' in df_time.columns
        assert 'month' in df_time.columns
        assert 'quarter' in df_time.columns


class TestModelRegistry:
    """Test model registry."""
    
    def test_registry_operations(self):
        """Test registering and retrieving models."""
        registry = ModelRegistry()
        
        model1 = LSTMPredictor()
        model2 = TransformerPredictor()
        
        registry.register(model1)
        registry.register(model2)
        
        assert len(registry.list_models()) == 2
        assert registry.get("LSTM_Predictor") is model1
        assert registry.get("Transformer_Predictor") is model2
        
        registry.remove("LSTM_Predictor")
        assert len(registry.list_models()) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
