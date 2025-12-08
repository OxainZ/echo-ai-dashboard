"""
Unit tests for FinancialDataPreprocessor
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from echo.preprocessing.financial_data import FinancialDataPreprocessor


class TestFinancialDataPreprocessor:
    """Test FinancialDataPreprocessor class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.preprocessor = FinancialDataPreprocessor()
        
        # Create sample data
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        
        self.sample_data = pd.DataFrame({
            'Date': dates,
            'Open': 100 + np.random.randn(len(dates)).cumsum(),
            'High': 105 + np.random.randn(len(dates)).cumsum(),
            'Low': 95 + np.random.randn(len(dates)).cumsum(),
            'Close': 100 + np.random.randn(len(dates)).cumsum(),
            'Volume': np.random.randint(1000000, 10000000, len(dates))
        })
        self.sample_data.set_index('Date', inplace=True)
    
    def test_clean_data_removes_duplicates(self):
        """Test that clean_data removes duplicate rows"""
        # Add duplicates
        df_with_dupes = pd.concat([self.sample_data, self.sample_data.iloc[:5]])
        
        cleaned = self.preprocessor.clean_data(df_with_dupes)
        
        assert len(cleaned) < len(df_with_dupes)
        assert cleaned.index.is_unique
    
    def test_clean_data_handles_missing_values(self):
        """Test that clean_data handles missing values"""
        df_with_nan = self.sample_data.copy()
        df_with_nan.iloc[10:15, :] = np.nan
        
        cleaned = self.preprocessor.clean_data(df_with_nan)
        
        # Should have fewer rows (NaN rows removed or filled)
        assert not cleaned.isnull().any().any()
    
    def test_clean_data_removes_invalid_prices(self):
        """Test that clean_data removes invalid prices"""
        df_invalid = self.sample_data.copy()
        df_invalid.iloc[5, df_invalid.columns.get_loc('Close')] = -10
        df_invalid.iloc[10, df_invalid.columns.get_loc('Close')] = 0
        
        cleaned = self.preprocessor.clean_data(df_invalid)
        
        assert (cleaned['Close'] > 0).all()
    
    def test_add_technical_indicators_creates_features(self):
        """Test that technical indicators are added"""
        df_with_indicators = self.preprocessor.add_technical_indicators(self.sample_data)
        
        # Check for key indicators
        expected_indicators = [
            'SMA_5', 'SMA_20', 'EMA_12', 'RSI', 'MACD', 
            'BB_Upper', 'BB_Lower', 'ATR'
        ]
        
        for indicator in expected_indicators:
            assert indicator in df_with_indicators.columns
    
    def test_rsi_calculation(self):
        """Test RSI calculation"""
        df_with_indicators = self.preprocessor.add_technical_indicators(self.sample_data)
        
        # RSI should be between 0 and 100
        rsi_values = df_with_indicators['RSI'].dropna()
        assert (rsi_values >= 0).all()
        assert (rsi_values <= 100).all()
    
    def test_macd_calculation(self):
        """Test MACD calculation"""
        df_with_indicators = self.preprocessor.add_technical_indicators(self.sample_data)
        
        # MACD components should exist
        assert 'MACD' in df_with_indicators.columns
        assert 'MACD_Signal' in df_with_indicators.columns
        assert 'MACD_Hist' in df_with_indicators.columns
        
        # MACD_Hist should equal MACD - MACD_Signal
        macd_diff = df_with_indicators['MACD'] - df_with_indicators['MACD_Signal']
        macd_hist = df_with_indicators['MACD_Hist']
        
        # Allow small floating point differences
        assert np.allclose(macd_diff.dropna(), macd_hist.dropna(), rtol=1e-5)
    
    def test_bollinger_bands_calculation(self):
        """Test Bollinger Bands calculation"""
        df_with_indicators = self.preprocessor.add_technical_indicators(self.sample_data)
        
        # Upper band should be above lower band
        valid_data = df_with_indicators[['BB_Upper', 'BB_Lower']].dropna()
        assert (valid_data['BB_Upper'] > valid_data['BB_Lower']).all()
    
    def test_prepare_features(self):
        """Test feature preparation"""
        df_with_indicators = self.preprocessor.add_technical_indicators(self.sample_data)
        X, y = self.preprocessor.prepare_features(df_with_indicators, target_col='Close')
        
        # Check that target is not in features
        assert 'Close' not in X.columns
        
        # Check that we have features
        assert len(X.columns) > 0
        
        # Check that lengths match
        assert len(X) == len(y)
    
    def test_normalize_features(self):
        """Test feature normalization"""
        df_with_indicators = self.preprocessor.add_technical_indicators(self.sample_data)
        X, _ = self.preprocessor.prepare_features(df_with_indicators)
        
        X_scaled, scaler = self.preprocessor.normalize_features(X)
        
        # Check that values are between 0 and 1
        assert X_scaled.min() >= 0
        assert X_scaled.max() <= 1
        
        # Check shape is preserved
        assert X_scaled.shape == X.shape
    
    def test_temporal_train_test_split(self):
        """Test temporal train/test split"""
        train_df, test_df = self.preprocessor.temporal_train_test_split(
            self.sample_data, test_size=0.2
        )
        
        # Check sizes
        total_len = len(self.sample_data)
        assert len(train_df) == int(total_len * 0.8)
        assert len(test_df) == total_len - len(train_df)
        
        # Check temporal order (train should come before test)
        assert train_df.index.max() < test_df.index.min()
    
    def test_process_pipeline(self):
        """Test complete processing pipeline"""
        processed = self.preprocessor.process_pipeline(
            self.sample_data, add_indicators=True
        )
        
        # Should have technical indicators
        assert 'RSI' in processed.columns
        assert 'MACD' in processed.columns
        
        # Should be clean (no NaN, valid prices)
        assert not processed.isnull().any().any()
        assert (processed['Close'] > 0).all()
    
    def test_get_feature_importance_data(self):
        """Test feature categorization"""
        df_with_indicators = self.preprocessor.add_technical_indicators(self.sample_data)
        categories = self.preprocessor.get_feature_importance_data(df_with_indicators)
        
        # Should have various categories
        assert 'price_based' in categories
        assert 'moving_averages' in categories
        assert 'momentum_indicators' in categories
        
        # Each category should have features
        for cat, features in categories.items():
            assert len(features) > 0
            # All features should exist in dataframe
            for feature in features:
                assert feature in df_with_indicators.columns


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
