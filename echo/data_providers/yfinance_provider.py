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

    def earnings_dates(self, ticker: str) -> list:
        """Known earnings dates (past + upcoming) for `ticker`, sorted ascending,
        as `datetime.date` objects.

        Tries `Ticker.get_earnings_dates()` (past + future) first, then falls
        back to `Ticker.calendar` (upcoming only; dict in yfinance>=0.2, DataFrame
        in older releases). Returns [] when nothing is available — callers then
        fall back to the static config calendar.
        """
        t = yf.Ticker(ticker)
        dates = set()
        try:
            df = t.get_earnings_dates(limit=8)
            if df is not None and len(df):
                dates.update(pd.Timestamp(idx).date() for idx in df.index)
        except Exception:
            pass
        if not dates:
            try:
                cal = t.calendar
                if isinstance(cal, dict):
                    raw = cal.get("Earnings Date") or []
                elif cal is not None and "Earnings Date" in getattr(cal, "index", []):
                    raw = list(cal.loc["Earnings Date"])
                else:
                    raw = []
                dates.update(pd.Timestamp(d).date() for d in raw if d is not None)
            except Exception:
                pass
        return sorted(dates)
