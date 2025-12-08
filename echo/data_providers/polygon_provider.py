"""
Polygon.io data provider (placeholder).

To use this provider:
1. Get an API key from https://polygon.io/
2. Set the POLYGON_API_KEY environment variable
3. Install polygon: pip install polygon-api-client
"""

from __future__ import annotations
from typing import Dict
import pandas as pd


class PolygonProvider:
    """
    Polygon.io data provider.
    
    Note: This is a placeholder implementation.
    Full implementation requires the polygon-api-client package.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        raise NotImplementedError(
            "PolygonProvider is not yet implemented. "
            "Install polygon-api-client package and implement the methods."
        )
    
    def quote(self, ticker: str) -> Dict:
        """Get current quote for a ticker."""
        raise NotImplementedError("PolygonProvider.quote not implemented")
    
    def history(self, ticker: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
        """Get historical data for a ticker."""
        raise NotImplementedError("PolygonProvider.history not implemented")
