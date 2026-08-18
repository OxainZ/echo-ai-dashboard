from __future__ import annotations
from .base import Rule, Signal
from dateutil import parser

# A config-fallback earnings date more than this many days in the past carries
# no usable PEAD information — report it as stale instead of silently scoring 0
# with "Outside PEAD window" (which looks identical to a quiet market).
_FALLBACK_STALE_AFTER_DAYS = 30


class PEAD(Rule):
    def __init__(self, slot_key: str):
        self.slot_key = slot_key

    @staticmethod
    def _live_date(context, ticker, today):
        """Pick the PEAD-relevant earnings date from live provider data:
        the most recent past date while inside the 30-day drift window,
        otherwise the next upcoming date. None when the provider has nothing
        (missing method, fetch error, or empty result) — caller falls back to
        the static config calendar."""
        getter = getattr(context.get("provider"), "earnings_dates", None)
        if getter is None:
            return None
        try:
            dates = getter(ticker)
        except Exception:
            return None
        if not dates:
            return None
        past = [d for d in dates if d <= today]
        future = [d for d in dates if d > today]
        if past and (today - past[-1]).days <= 30:
            return past[-1]
        if future:
            return future[0]
        return past[-1] if past else None

    def run(self, context):
        cfg = context["config"]
        ticker = context["slots"][self.slot_key]
        today = context["now"].date()

        d = self._live_date(context, ticker, today)
        source = "live"
        if d is None:
            dstr = cfg.get("calendar", {}).get("earnings", {}).get(ticker)
            if not dstr:
                return Signal(f"PEAD:{ticker}", 0,
                              f"No earnings date for {ticker} (live fetch empty, no config fallback)",
                              "green")
            d = parser.parse(dstr).date()
            source = "config fallback"
            if (today - d).days > _FALLBACK_STALE_AFTER_DAYS:
                # Staleness guard: we effectively have no earnings info — say so.
                return Signal(f"PEAD:{ticker}", 0,
                              f"Earnings date unavailable: live fetch empty and config "
                              f"fallback is stale ({d.isoformat()})",
                              "yellow")
        if today < d:
            whisper = cfg.get("whispers", {}).get(ticker, {})
            if whisper:
                gap = float(whisper.get("whisper_eps", 0)) - float(whisper.get("consensus_eps", 0))
                if gap > 0:
                    return Signal(f"PEAD:{ticker}", 60,
                                  f"Pre-earnings ({d.isoformat()}, {source}); positive whisper gap {gap:+.02f}",
                                  "yellow")
            return Signal(f"PEAD:{ticker}", 30,
                          f"Pre-earnings ({d.isoformat()}, {source}); no whisper data", "green")
        delta = (today - d).days
        if 1 <= delta <= 30:
            score = max(30.0, 75.0 - (delta - 1) * 1.5)
            return Signal(f"PEAD:{ticker}", score,
                          f"Post-earnings drift day {delta} ({source} date {d.isoformat()})", "green")
        return Signal(f"PEAD:{ticker}", 0,
                      f"Outside PEAD window ({source} date {d.isoformat()})", "green")
