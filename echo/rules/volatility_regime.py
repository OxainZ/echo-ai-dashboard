from __future__ import annotations
from .base import Rule, Signal

class VolatilityRegime(Rule):
    def run(self, context):
        core = context["slots"]["core"]
        hist = context["provider"].history(core, period="1mo", interval="1d")
        if hist is None or hist.empty:
            return Signal("Volatility Regime", 0, "No data", "green")
        ret = hist["Close"].pct_change().dropna()
        vol = float(ret.std() * (252 ** 0.5) * 100)
        if vol >= 35:
            return Signal("Volatility Regime", 80, f"High vol (~{vol:.1f}%) → tighten stops, build cash", "yellow")
        elif vol <= 15:
            return Signal("Volatility Regime", 60, f"Low vol (~{vol:.1f}%) → looser stops ok", "green")
        return Signal("Volatility Regime", 50, f"Normal vol (~{vol:.1f}%)", "green")
