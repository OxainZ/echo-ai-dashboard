"""Test configuration and fixtures"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


@pytest.fixture
def sample_price_data():
    """Generate sample OHLCV data for testing"""
    dates = pd.date_range(start='2024-01-01', end='2024-03-31', freq='D')
    np.random.seed(42)
    
    base_price = 100.0
    prices = []
    
    for i in range(len(dates)):
        # Generate realistic price movement
        change = np.random.normal(0, 0.02)
        price = base_price * (1 + change)
        prices.append(price)
        base_price = price
    
    df = pd.DataFrame({
        'Open': prices,
        'High': [p * 1.02 for p in prices],
        'Low': [p * 0.98 for p in prices],
        'Close': prices,
        'Volume': np.random.randint(1000000, 10000000, len(dates))
    }, index=dates)
    
    return df


@pytest.fixture
def sample_quote():
    """Generate sample quote data"""
    return {
        'ticker': 'AAPL',
        'price': 150.50,
        'prev_close': 149.00,
        'volume': 50000000,
        'currency': 'USD'
    }


@pytest.fixture
def sample_news_articles():
    """Generate sample news articles for sentiment testing"""
    return [
        {
            'title': 'Apple stock surges on strong earnings',
            'description': 'Tech giant beats expectations with record profits',
            'source': 'Financial Times',
            'publishedAt': '2024-01-15T10:00:00Z'
        },
        {
            'title': 'Market concerns grow over tech sector',
            'description': 'Analysts warn of potential downturn in technology stocks',
            'source': 'Reuters',
            'publishedAt': '2024-01-15T11:00:00Z'
        },
        {
            'title': 'Neutral outlook for Q2 earnings',
            'description': 'Mixed signals from corporate earnings reports',
            'source': 'Bloomberg',
            'publishedAt': '2024-01-15T12:00:00Z'
        }
    ]
