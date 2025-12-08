"""
Multi-provider data source configuration and factory.

Supports multiple financial data providers with automatic fallback.
"""

from __future__ import annotations
from typing import Dict, Optional, Protocol
import pandas as pd
from enum import Enum
import os


class ProviderType(Enum):
    """Supported data providers."""
    YFINANCE = "yfinance"
    ALPHA_VANTAGE = "alphavantage"
    POLYGON = "polygon"
    FINNHUB = "finnhub"


class PriceProvider(Protocol):
    """Protocol defining the interface for price data providers."""
    
    def quote(self, ticker: str) -> Dict: ...
    def history(self, ticker: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame: ...


class ProviderFactory:
    """
    Factory for creating data provider instances.
    
    Supports multiple providers with automatic fallback.
    """
    
    @staticmethod
    def create_provider(provider_type: str = None) -> PriceProvider:
        """
        Create a data provider instance.
        
        Args:
            provider_type: Type of provider to create (default: from env var or yfinance)
            
        Returns:
            Provider instance
            
        Raises:
            ValueError: If provider type is unsupported
            RuntimeError: If provider cannot be initialized
        """
        # Get provider type from environment or use default
        if provider_type is None:
            provider_type = os.getenv('DEFAULT_DATA_PROVIDER', 'yfinance')
        
        provider_type = provider_type.lower()
        
        if provider_type == ProviderType.YFINANCE.value:
            from .yfinance_provider import YFinanceProvider
            return YFinanceProvider()
        
        elif provider_type == ProviderType.ALPHA_VANTAGE.value:
            from .alphavantage_provider import AlphaVantageProvider
            api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
            if not api_key:
                raise RuntimeError("ALPHA_VANTAGE_API_KEY environment variable not set")
            return AlphaVantageProvider(api_key)
        
        elif provider_type == ProviderType.POLYGON.value:
            from .polygon_provider import PolygonProvider
            api_key = os.getenv('POLYGON_API_KEY')
            if not api_key:
                raise RuntimeError("POLYGON_API_KEY environment variable not set")
            return PolygonProvider(api_key)
        
        elif provider_type == ProviderType.FINNHUB.value:
            from .finnhub_provider import FinnhubProvider
            api_key = os.getenv('FINNHUB_API_KEY')
            if not api_key:
                raise RuntimeError("FINNHUB_API_KEY environment variable not set")
            return FinnhubProvider(api_key)
        
        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")


class MultiProviderManager:
    """
    Manages multiple data providers with automatic fallback.
    
    Tries providers in order until one succeeds.
    """
    
    def __init__(self, providers: Optional[list] = None):
        """
        Initialize with a list of provider types.
        
        Args:
            providers: List of provider type strings (defaults to ['yfinance'])
        """
        if providers is None:
            providers = ['yfinance']
        
        self.providers = []
        for provider_type in providers:
            try:
                provider = ProviderFactory.create_provider(provider_type)
                self.providers.append((provider_type, provider))
            except Exception as e:
                print(f"Warning: Could not initialize provider {provider_type}: {e}")
        
        if not self.providers:
            raise RuntimeError("No data providers could be initialized")
    
    def quote(self, ticker: str) -> Dict:
        """
        Get quote with automatic fallback.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Quote dictionary
            
        Raises:
            RuntimeError: If all providers fail
        """
        last_error = None
        
        for provider_name, provider in self.providers:
            try:
                return provider.quote(ticker)
            except Exception as e:
                last_error = e
                print(f"Provider {provider_name} failed for {ticker}: {e}")
        
        raise RuntimeError(f"All providers failed to fetch quote for {ticker}: {last_error}")
    
    def history(self, ticker: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
        """
        Get historical data with automatic fallback.
        
        Args:
            ticker: Stock ticker symbol
            period: Data period
            interval: Data interval
            
        Returns:
            DataFrame with historical data
            
        Raises:
            RuntimeError: If all providers fail
        """
        last_error = None
        
        for provider_name, provider in self.providers:
            try:
                return provider.history(ticker, period, interval)
            except Exception as e:
                last_error = e
                print(f"Provider {provider_name} failed for {ticker}: {e}")
        
        raise RuntimeError(f"All providers failed to fetch history for {ticker}: {last_error}")
