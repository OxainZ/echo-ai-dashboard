"""
Alpha Vantage data provider (placeholder).

To use this provider:
1. Get an API key from https://www.alphavantage.co/
2. Set the ALPHA_VANTAGE_API_KEY environment variable
3. Install alpha_vantage: pip install alpha_vantage
"""

from __future__ import annotations
from typing import Dict
import pandas as pd


class AlphaVantageProvider:
    """
    Alpha Vantage data provider.
    
    Note: This is a placeholder implementation.
    Full implementation requires the alpha_vantage package.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        # try:
        #     from alpha_vantage.timeseries import TimeSeries
        #     self.ts = TimeSeries(key=api_key, output_format='pandas')
        # except ImportError:
        #     raise RuntimeError("alpha_vantage package not installed. Run: pip install alpha_vantage")
        raise NotImplementedError(
            "AlphaVantageProvider is not yet implemented. "
            "Install alpha_vantage package and implement the methods."
        )
    
    def quote(self, ticker: str) -> Dict:
        """Get current quote for a ticker."""
        raise NotImplementedError("AlphaVantageProvider.quote not implemented")
    
    def history(self, ticker: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
        """Get historical data for a ticker."""
        raise NotImplementedError("AlphaVantageProvider.history not implemented")
