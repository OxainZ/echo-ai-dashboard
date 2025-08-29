from __future__ import annotations
from .base import Rule, Signal
from dateutil import parser

class PEAD(Rule):
    def __init__(self, slot_key: str):
        self.slot_key = slot_key
    def run(self, context):
        cfg = context["config"]
        earnings = cfg.get("calendar", {}).get("earnings", {})
        ticker = context["slots"][self.slot_key]
        dstr = earnings.get(ticker)
        if not dstr:
            return Signal(f"PEAD:{ticker}", 0, f"No earnings date set for {ticker}", "green")
        d = parser.parse(dstr).date()
        today = context["now"].date()
        if today < d:
            whisper = cfg.get("whispers", {}).get(ticker, {})
            if whisper:
                gap = float(whisper.get("whisper_eps", 0)) - float(whisper.get("consensus_eps", 0))
                if gap > 0:
                    return Signal(f"PEAD:{ticker}", 60, f"Pre-earnings; positive whisper gap {gap:+.02f}", "yellow")
            return Signal(f"PEAD:{ticker}", 30, "Pre-earnings; no whisper data", "green")
        delta = (today - d).days
        if 1 <= delta <= 30:
            score = max(30.0, 75.0 - (delta-1)*1.5)
            return Signal(f"PEAD:{ticker}", score, f"Post-earnings drift day {delta}", "green")
        return Signal(f"PEAD:{ticker}", 0, "Outside PEAD window", "green")
