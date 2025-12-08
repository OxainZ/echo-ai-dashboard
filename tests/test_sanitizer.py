"""Tests for data sanitization"""
import pytest
import pandas as pd
import numpy as np
from echo.utils.sanitizer import DataSanitizer


def test_sanitize_ticker():
    """Test ticker sanitization"""
    assert DataSanitizer.sanitize_ticker("  aapl  ") == "AAPL"
    assert DataSanitizer.sanitize_ticker("tsla") == "TSLA"
    assert DataSanitizer.sanitize_ticker("BRK.B") == "BRK.B"
    
    with pytest.raises(ValueError):
        DataSanitizer.sanitize_ticker("")
    
    with pytest.raises(ValueError):
        DataSanitizer.sanitize_ticker("   ")


def test_sanitize_dataframe(sample_price_data):
    """Test DataFrame sanitization"""
    df = sample_price_data.copy()
    
    # Add some issues
    df.loc[df.index[0], 'Close'] = np.nan
    df.loc[df.index[5], 'High'] = df.loc[df.index[5], 'Low'] - 1  # Invalid: High < Low
    
    sanitized = DataSanitizer.sanitize_dataframe(df)
    
    # Check no NaN values
    assert not sanitized['Close'].isna().any()
    
    # Check High >= Low
    assert (sanitized['High'] >= sanitized['Low']).all()


def test_sanitize_quote():
    """Test quote sanitization"""
    quote = {
        'ticker': ' aapl ',
        'price': '150.50',
        'prev_close': 149.00,
        'volume': '50000000'
    }
    
    sanitized = DataSanitizer.sanitize_quote(quote)
    
    assert sanitized['ticker'] == 'AAPL'
    assert isinstance(sanitized['price'], float)
    assert isinstance(sanitized['volume'], int)


def test_validate_price_data(sample_price_data):
    """Test price data validation"""
    assert DataSanitizer.validate_price_data(sample_price_data) is True
    
    # Test with insufficient data
    small_df = sample_price_data.head(1)
    assert DataSanitizer.validate_price_data(small_df) is False
    
    # Test with missing columns
    invalid_df = sample_price_data.drop(columns=['Close'])
    assert DataSanitizer.validate_price_data(invalid_df) is False
