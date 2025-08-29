from __future__ import annotations
from .base import Rule, Signal
from datetime import timedelta
from dateutil import parser

class FOMCTilt(Rule):
    def run(self, context):
        today = context["now"].date()
        fomc_dates = [parser.parse(d).date() for d in context["config"].get("calendar", {}).get("fomc_dates", [])]
        score, severity, detail = 0.0, "green", "No FOMC tilt"
        for d in fomc_dates:
            if today == d - timedelta(days=1):
                score, severity, detail = 80.0, "yellow", "Pre-FOMC day: consider +5–10% Core tilt"
                break
        return Signal("FOMC Tilt", score, detail, severity)
