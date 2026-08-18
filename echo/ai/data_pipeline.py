"""
Data Pipeline for Real-time Stock Data

Handles:
- Real-time data fetching from multiple sources
- Data preprocessing and normalization
- Feature engineering for AI models
- Data caching and management
"""

from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from ..data_providers.yfinance_provider import YFinanceProvider
import warnings
warnings.filterwarnings('ignore')


class DataPipeline:
    """
    Real-time data pipeline for stock market data
    
    Fetches, preprocesses, and prepares data for AI models
    """
    
    def __init__(self, provider: Optional[YFinanceProvider] = None):
        """
        Args:
            provider: Data provider instance (defaults to YFinanceProvider)
        """
        self.provider = provider or YFinanceProvider()
        self.cache = {}
        
    def fetch_realtime_data(self, ticker: str, period: str = "3mo", 
                           interval: str = "1d") -> pd.DataFrame:
        """
        Fetch real-time stock data
        
        Args:
            ticker: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            DataFrame with OHLCV data
        """
        cache_key = f"{ticker}_{period}_{interval}"
        
        # Check cache (with 5-minute expiry for real-time data)
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < timedelta(minutes=5):
                return cached_data.copy()
        
        # Fetch fresh data
        df = self.provider.history(ticker, period=period, interval=interval)
        
        if df.empty:
            raise ValueError(f"No data available for {ticker}")
        
        # Cache the data
        self.cache[cache_key] = (df.copy(), datetime.now())
        
        return df
    
    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess raw stock data
        
        Args:
            df: Raw DataFrame with OHLCV data
            
        Returns:
            Preprocessed DataFrame with additional features
        """
        df = df.copy()
        
        # Handle missing values
        df = df.ffill().bfill()
        
        # Ensure proper column names
        if 'Close' not in df.columns and 'close' in df.columns:
            df.rename(columns=str.lower, inplace=True)
            df.rename(columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            }, inplace=True)
        
        # Calculate returns
        df['Returns'] = df['Close'].pct_change()
        df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))
        
        # Calculate price ranges
        df['Daily_Range'] = df['High'] - df['Low']
        prev_close = df['Close'].shift(1)
        df['True_Range'] = pd.concat([
            df['High'] - df['Low'],
            (df['High'] - prev_close).abs(),
            (df['Low'] - prev_close).abs()
        ], axis=1).max(axis=1)
        
        # Normalize volume (z-score). Where the 20-day window has zero
        # variance, 0/0 made every row NaN and the later dropna() silently
        # emptied the whole frame — a constant-volume stretch broke the entire
        # prediction path with an IndexError. Zero variance means volume is at
        # its window mean, so the z-score is 0.
        volume_mean = df['Volume'].rolling(window=20).mean()
        volume_std = df['Volume'].rolling(window=20).std()
        df['Volume_Normalized'] = (df['Volume'] - volume_mean) / volume_std
        df.loc[volume_std == 0, 'Volume_Normalized'] = 0.0

        return df
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Engineer features for ML models
        
        Args:
            df: Preprocessed DataFrame
            
        Returns:
            DataFrame with engineered features
        """
        df = df.copy()
        
        # Momentum features
        df['Momentum_5'] = df['Close'] / df['Close'].shift(5) - 1
        df['Momentum_10'] = df['Close'] / df['Close'].shift(10) - 1
        df['Momentum_20'] = df['Close'] / df['Close'].shift(20) - 1
        
        # Volatility features
        df['Volatility_10'] = df['Returns'].rolling(window=10).std()
        df['Volatility_20'] = df['Returns'].rolling(window=20).std()
        
        # Price position features
        df['Price_to_MA5'] = df['Close'] / df['Close'].rolling(window=5).mean()
        df['Price_to_MA20'] = df['Close'] / df['Close'].rolling(window=20).mean()
        
        # Volume features
        df['Volume_MA5'] = df['Volume'].rolling(window=5).mean()
        df['Volume_MA20'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_MA20']
        
        # Trend strength
        df['Trend_Strength'] = df['Close'].rolling(window=20).apply(
            lambda x: np.polyfit(range(len(x)), x, 1)[0]
        )
        
        return df
    
    def prepare_for_prediction(self, ticker: str, period: str = "3mo") -> pd.DataFrame:
        """
        Fetch and prepare data for AI prediction
        
        Args:
            ticker: Stock ticker symbol
            period: Time period for historical data
            
        Returns:
            Fully preprocessed DataFrame ready for prediction
        """
        # Fetch data
        df = self.fetch_realtime_data(ticker, period=period)
        
        # Preprocess
        df = self.preprocess_data(df)
        
        # Engineer features
        df = self.engineer_features(df)
        
        # Drop NaN values from feature engineering
        df = df.dropna()

        if df.empty:
            # Fail loudly with a message the UI can display — an empty frame
            # here previously surfaced as a bare IndexError downstream.
            raise ValueError(
                f"Not enough clean history for {ticker} to compute features "
                f"(rolling windows need ~20+ trading days beyond warm-up)"
            )

        return df
    
    def get_current_price(self, ticker: str) -> Dict:
        """
        Get current price and basic info
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dict with current price information
        """
        quote = self.provider.quote(ticker)
        return quote
    
    def get_multiple_tickers(self, tickers: List[str], period: str = "3mo") -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple tickers
        
        Args:
            tickers: List of ticker symbols
            period: Time period for historical data
            
        Returns:
            Dict mapping ticker to preprocessed DataFrame
        """
        results = {}
        
        for ticker in tickers:
            try:
                df = self.prepare_for_prediction(ticker, period=period)
                results[ticker] = df
            except Exception as e:
                print(f"Error fetching data for {ticker}: {e}")
                results[ticker] = None
        
        return results
    
    def clear_cache(self):
        """Clear the data cache"""
        self.cache.clear()


class DataValidator:
    """
    Validate data quality and integrity
    """
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> Dict[str, bool]:
        """
        Validate DataFrame quality
        
        Returns:
            Dict with validation results
        """
        validations = {
            "has_data": len(df) > 0,
            "has_required_columns": all(col in df.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume']),
            "no_nulls": not df[['Open', 'High', 'Low', 'Close', 'Volume']].isnull().any().any(),
            "positive_prices": (df[['Open', 'High', 'Low', 'Close']] > 0).all().all(),
            "valid_ranges": (df['High'] >= df['Low']).all(),
            "sufficient_data": len(df) >= 20,
        }
        
        validations["is_valid"] = all(validations.values())
        
        return validations
    
    @staticmethod
    def get_data_quality_score(df: pd.DataFrame) -> float:
        """
        Calculate data quality score (0-1)
        
        Returns:
            Quality score between 0 and 1
        """
        validations = DataValidator.validate_dataframe(df)
        
        # Remove is_valid from scoring
        score_items = {k: v for k, v in validations.items() if k != "is_valid"}
        
        score = sum(score_items.values()) / len(score_items)
        
        return score


class MarketDataAggregator:
    """
    Aggregate market data from multiple sources
    """
    
    def __init__(self, pipeline: Optional[DataPipeline] = None):
        self.pipeline = pipeline or DataPipeline()
    
    def get_market_overview(self, tickers: Optional[List[str]] = None) -> Dict:
        """
        Get overview of market conditions
        
        Args:
            tickers: List of tickers to analyze (defaults to major indices)
            
        Returns:
            Dict with market overview metrics
        """
        if tickers is None:
            tickers = ["SPY", "QQQ", "DIA"]  # Major market indices
        
        overview = {
            "timestamp": datetime.now().isoformat(),
            "markets": {}
        }
        
        for ticker in tickers:
            try:
                quote = self.pipeline.get_current_price(ticker)
                df = self.pipeline.fetch_realtime_data(ticker, period="1mo")
                
                if len(df) > 1:
                    current = df['Close'].iloc[-1]
                    prev = df['Close'].iloc[-2]
                    change = (current - prev) / prev * 100
                    
                    overview["markets"][ticker] = {
                        "price": quote.get("price") or current,
                        "change_pct": change,
                        "volume": df['Volume'].iloc[-1],
                        "trend": "up" if change > 0 else "down"
                    }
            except Exception as e:
                print(f"Error fetching overview for {ticker}: {e}")
                overview["markets"][ticker] = {"error": str(e)}
        
        return overview
    
    def detect_market_regime(self, ticker: str = "SPY") -> Dict:
        """
        Detect current market regime (bullish, bearish, volatile, etc.)
        
        Args:
            ticker: Ticker to analyze (default: SPY for overall market)
            
        Returns:
            Dict with regime classification
        """
        df = self.pipeline.fetch_realtime_data(ticker, period="6mo")
        df = self.pipeline.preprocess_data(df)
        
        # Calculate metrics
        returns_20d = df['Returns'].tail(20)
        volatility = returns_20d.std() * np.sqrt(252)  # Annualized
        avg_return = returns_20d.mean() * 252  # Annualized
        
        # Determine regime
        if volatility > 0.25:
            regime = "high_volatility"
        elif volatility < 0.12:
            regime = "low_volatility"
        else:
            regime = "normal_volatility"
        
        if avg_return > 0.15:
            trend = "strong_bullish"
        elif avg_return > 0.05:
            trend = "bullish"
        elif avg_return < -0.15:
            trend = "strong_bearish"
        elif avg_return < -0.05:
            trend = "bearish"
        else:
            trend = "neutral"
        
        return {
            "regime": regime,
            "trend": trend,
            "volatility": volatility,
            "annualized_return": avg_return,
            "analysis": f"Market is in {regime} regime with {trend} trend"
        }
