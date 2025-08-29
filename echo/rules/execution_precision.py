from __future__ import annotations
from .base import Rule, Signal
class ExecutionPrecision(Rule):
    def run(self, context):
        return Signal("Execution Precision", 55, "Use marketable limits; stage near VWAP; only add if vol ≥1.5× avg.", "green")
