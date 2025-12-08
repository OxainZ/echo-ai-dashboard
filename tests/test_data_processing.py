"""
Unit tests for data processing utilities

Tests data cleaning, feature engineering, and validation.
"""
import pytest
import pandas as pd
import numpy as np

from echo.utils.data_processing import DataCleaner, FeatureEngine, prepare_ml_dataset


def create_sample_ohlcv() -> pd.DataFrame:
    """Create sample OHLCV data for testing"""
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.randn(100) * 2)
    
    df = pd.DataFrame({
        'Open': close + np.random.randn(100) * 0.5,
        'High': close + np.abs(np.random.randn(100)) * 1.5,
        'Low': close - np.abs(np.random.randn(100)) * 1.5,
        'Close': close,
        'Volume': np.random.randint(1000000, 10000000, 100)
    }, index=dates)
    
    # Ensure OHLC validity
    df['High'] = df[['Open', 'High', 'Close']].max(axis=1)
    df['Low'] = df[['Open', 'Low', 'Close']].min(axis=1)
    
    return df


def test_handle_missing_values_ffill():
    """Test forward fill for missing values"""
    df = create_sample_ohlcv()
    df.loc[df.index[10:15], 'Close'] = np.nan
    
    df_clean = DataCleaner.handle_missing_values(df, method='ffill')
    
    assert not df_clean['Close'].isna().any()


def test_handle_missing_values_drop():
    """Test dropping rows with missing values"""
    df = create_sample_ohlcv()
    df.loc[df.index[10], 'Close'] = np.nan
    
    df_clean = DataCleaner.handle_missing_values(df, method='drop')
    
    assert len(df_clean) == len(df) - 1
    assert not df_clean.isna().any().any()


def test_detect_outliers_iqr():
    """Test outlier detection with IQR method"""
    series = pd.Series([1, 2, 3, 4, 5, 100])  # 100 is outlier
    outliers = DataCleaner.detect_outliers(series, method='iqr')
    
    assert outliers.iloc[-1] == True
    assert outliers.iloc[:-1].sum() == 0


def test_validate_ohlcv_valid():
    """Test OHLCV validation with valid data"""
    df = create_sample_ohlcv()
    
    results = DataCleaner.validate_ohlcv(df)
    
    assert results['is_valid'] == True
    assert results['has_required_columns'] == True
    assert results['high_gte_low'] == True


def test_validate_ohlcv_invalid():
    """Test OHLCV validation with invalid data"""
    df = create_sample_ohlcv()
    df.loc[df.index[0], 'High'] = df.loc[df.index[0], 'Low'] - 1  # Invalid
    
    results = DataCleaner.validate_ohlcv(df)
    
    assert results['is_valid'] == False
    assert results['high_gte_low'] == False


def test_add_moving_averages():
    """Test moving average calculation"""
    df = create_sample_ohlcv()
    
    df_feat = FeatureEngine.add_moving_averages(df, windows=[5, 10])
    
    assert 'SMA_5' in df_feat.columns
    assert 'SMA_10' in df_feat.columns
    assert 'EMA_5' in df_feat.columns
    assert 'EMA_10' in df_feat.columns


def test_add_momentum_indicators():
    """Test momentum indicator calculation"""
    df = create_sample_ohlcv()
    
    df_feat = FeatureEngine.add_momentum_indicators(df)
    
    assert 'ROC_10' in df_feat.columns
    assert 'RSI' in df_feat.columns
    assert 'MACD' in df_feat.columns


def test_add_volatility_indicators():
    """Test volatility indicator calculation"""
    df = create_sample_ohlcv()
    
    df_feat = FeatureEngine.add_volatility_indicators(df)
    
    assert 'BB_Upper' in df_feat.columns
    assert 'BB_Lower' in df_feat.columns
    assert 'ATR' in df_feat.columns
    assert 'Volatility_20' in df_feat.columns


def test_add_volume_indicators():
    """Test volume indicator calculation"""
    df = create_sample_ohlcv()
    
    df_feat = FeatureEngine.add_volume_indicators(df)
    
    assert 'Volume_MA_20' in df_feat.columns
    assert 'Volume_Ratio' in df_feat.columns
    assert 'OBV' in df_feat.columns


def test_create_all_features():
    """Test comprehensive feature creation"""
    df = create_sample_ohlcv()
    
    df_feat = FeatureEngine.create_all_features(df)
    
    # Should have all features
    assert 'SMA_20' in df_feat.columns
    assert 'RSI' in df_feat.columns
    assert 'BB_Upper' in df_feat.columns
    assert 'OBV' in df_feat.columns
    
    # Should have dropped NaN rows
    assert not df_feat.isna().any().any()


def test_prepare_ml_dataset():
    """Test ML dataset preparation"""
    df = create_sample_ohlcv()
    
    df_ml = prepare_ml_dataset(df, clean_data=True, add_features=True)
    
    # Should have features
    assert len(df_ml.columns) > len(df.columns)
    
    # Should be clean
    assert not df_ml.isna().any().any()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
