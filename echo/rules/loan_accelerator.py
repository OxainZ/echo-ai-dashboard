from __future__ import annotations
from .base import Rule, Signal
class LoanAccelerator(Rule):
    def run(self, context):
        cfg = context["config"].get("loan_accelerator", {})
        if not cfg.get("enabled", True):
            return Signal("Loan Accelerator", 0, "Disabled", "green")
        slots = context["slots"]
        whispers = context["config"].get("whispers", {})
        wild = slots["wildcard"]
        w = whispers.get(wild)
        ok, detail = False, "No qualifying catalyst"
        if w:
            gap = float(w.get("whisper_eps", 0)) - float(w.get("consensus_eps", 0))
            if gap > 0:
                ok, detail = True, f"{wild}: positive whisper gap {gap:+.02f}"
        if ok:
            cap = int(cfg.get('deploy_fraction',0.55)*cfg.get('loan_cap_usd',500))
            return Signal("Loan Accelerator", 80, f"ACTIVE: {detail} (deploy ≤ ${cap}, repay on first +10%)", "yellow")
        return Signal("Loan Accelerator", 20, "STANDBY: waiting for confirmed catalyst/options flow", "green")
