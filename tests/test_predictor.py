"""Tests for ML predictor module"""
import pytest
import pandas as pd
from echo.ml.predictor import StockPredictor, TradingSignalGenerator


def test_stock_predictor_initialization():
    """Test StockPredictor initialization"""
    predictor = StockPredictor()
    assert predictor.model_type == "lstm"
    assert predictor.enabled is not None


def test_simple_prediction(sample_price_data):
    """Test simple prediction with sample data"""
    predictor = StockPredictor(model_type="simple")
    result = predictor.predict("TEST", sample_price_data, days_ahead=5)
    
    assert 'ticker' in result
    assert result['ticker'] == 'TEST'
    assert 'predictions' in result
    assert len(result['predictions']) == 5
    assert 'confidence' in result
    assert 0 <= result['confidence'] <= 1
    assert 'trend' in result
    assert result['trend'] in ['bullish', 'bearish', 'neutral']


def test_prediction_structure(sample_price_data):
    """Test prediction output structure"""
    predictor = StockPredictor()
    result = predictor.predict("AAPL", sample_price_data, days_ahead=3)
    
    for pred in result['predictions']:
        assert 'day' in pred
        assert 'date' in pred
        assert 'predicted_price' in pred
        assert 'lower_bound' in pred
        assert 'upper_bound' in pred
        assert pred['lower_bound'] <= pred['predicted_price'] <= pred['upper_bound']


def test_trading_signal_generation(sample_price_data, sample_quote):
    """Test trading signal generation"""
    generator = TradingSignalGenerator()
    signal = generator.generate_signal("AAPL", sample_price_data, sample_quote)
    
    assert 'ticker' in signal
    assert 'signal' in signal
    assert signal['signal'] in ['BUY', 'SELL', 'HOLD']
    assert 'confidence' in signal
    assert 0 <= signal['confidence'] <= 1
    assert 'reasoning' in signal
    assert isinstance(signal['reasoning'], list)


def test_insufficient_data():
    """Test predictor with insufficient data"""
    predictor = StockPredictor()
    empty_df = pd.DataFrame()
    result = predictor.predict("TEST", empty_df, days_ahead=5)
    
    assert 'predictions' in result
    assert result['model_type'] == 'fallback'
    assert result['confidence'] < 0.5
