"""
Finnhub data provider (placeholder).

To use this provider:
1. Get an API key from https://finnhub.io/
2. Set the FINNHUB_API_KEY environment variable
3. Install finnhub: pip install finnhub-python
"""

from __future__ import annotations
from typing import Dict
import pandas as pd


class FinnhubProvider:
    """
    Finnhub data provider.
    
    Note: This is a placeholder implementation.
    Full implementation requires the finnhub-python package.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        raise NotImplementedError(
            "FinnhubProvider is not yet implemented. "
            "Install finnhub-python package and implement the methods."
        )
    
    def quote(self, ticker: str) -> Dict:
        """Get current quote for a ticker."""
        raise NotImplementedError("FinnhubProvider.quote not implemented")
    
    def history(self, ticker: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
        """Get historical data for a ticker."""
        raise NotImplementedError("FinnhubProvider.history not implemented")
