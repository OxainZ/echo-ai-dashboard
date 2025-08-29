from __future__ import annotations
from .base import Rule, Signal
from datetime import timedelta

class TurnOfMonth(Rule):
    def run(self, context):
        cfg = context["config"]
        if not cfg.get("injections", {}).get("tom_preference", True):
            return Signal("Turn-of-Month", 0, "ToM preference disabled", "green")
        today = context["now"].date()
        first = today.replace(day=1)
        last = (first.replace(month=first.month % 12 + 1, day=1) - timedelta(days=1))
        score, severity, detail = 0.0, "green", "Outside ToM window"
        if (last - today).days in (0,1,2) or (today - first).days in (0,1,2):
            score, severity, detail = 65.0, "green", "Turn-of-Month window: prefer injection T-2 → T+2"
        return Signal("Turn-of-Month", score, detail, severity)
