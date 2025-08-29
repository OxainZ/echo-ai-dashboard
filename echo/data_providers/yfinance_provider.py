from __future__ import annotations
from typing import Dict
import pandas as pd

try:
    import yfinance as yf
except Exception:
    yf = None

class YFinanceProvider:
    def __init__(self):
        if yf is None:
            raise RuntimeError("yfinance not installed. Run `pip install yfinance`.")
    def quote(self, ticker: str) -> Dict:
        t = yf.Ticker(ticker)
        info = t.fast_info
        return {
            "ticker": ticker,
            "price": float(info.last_price) if info.last_price is not None else None,
            "prev_close": float(info.previous_close) if info.previous_close is not None else None,
            "currency": info.currency or "USD",
        }
    def history(self, ticker: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
        t = yf.Ticker(ticker)
        df = t.history(period=period, interval=interval, auto_adjust=False)
        return df
