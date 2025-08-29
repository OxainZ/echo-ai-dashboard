from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict
import yaml
from ..utils.dates import now_tz, fmt_ts
from ..utils.logging import get_logger
from ..data_providers.yfinance_provider import YFinanceProvider
from ..rules.base import Rule, Signal
from ..rules.fomc_tilt import FOMCTilt
from ..rules.tom_window import TurnOfMonth
from ..rules.pead import PEAD
from ..rules.volatility_regime import VolatilityRegime
from ..rules.execution_precision import ExecutionPrecision
from ..rules.loan_accelerator import LoanAccelerator

log = get_logger("EchoEngine")

@dataclass
class Verdict:
    asof: str
    composite: float
    risk_label: str
    cap_efficiency: float
    signals: List[Signal]
    actions: List[str]
    allocations: Dict[str, str]

class EchoEngine:
    def __init__(self, config_path: str = "echo/config.yaml"):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        self.tz = self.config.get("timezone","America/Chicago")
        self.provider = self._build_provider(self.config)
        self.slots = {k:self.config["slots"][k] for k in ["core","momentum","wildcard"]}
        self.rules: List[Rule] = [
            FOMCTilt(),
            TurnOfMonth(),
            PEAD("momentum"),
            PEAD("wildcard"),
            VolatilityRegime(),
            ExecutionPrecision(),
            LoanAccelerator(),
        ]

    def _build_provider(self, cfg):
        name = cfg.get("providers",{}).get("price_data",{}).get("name","yfinance")
        if name == "yfinance":
            return YFinanceProvider()
        raise ValueError(f"Unknown provider: {name}")

    def run(self) -> Verdict:
        now = now_tz(self.tz)
        context = {"now": now, "tz": self.tz, "config": self.config, "provider": self.provider, "slots": self.slots}
        signals: List[Signal] = []
        for r in self.rules:
            try:
                signals.append(r.run(context))
            except Exception as e:
                log.exception(f"Rule {r.__class__.__name__} failed: {e}")

        composite = sum(s.score for s in signals)/len(signals) if signals else 0.0
        risk_label = "Moderate"
        for s in signals:
            if s.severity == "red": risk_label = "High"; break
            if s.severity == "yellow": risk_label = "Elevated"
        cap_efficiency = min(100.0, max(10.0, composite))
        actions: List[str] = []
        for s in signals:
            if s.name == "FOMC Tilt" and s.score >= 70:
                actions.append("Core: consider +5–10% add pre-FOMC (respect cash buffer & no same-day round trips).")
            if s.name.startswith("PEAD:") and s.score >= 60:
                actions.append(f"{s.name.split(':',1)[1]}: hold through drift window; trim systematically on strength.")
            if s.name == "Loan Accelerator" and s.score >= 70:
                actions.append("Loan: ACTIVE — deploy ≤ 55% of loan, repay with first +10% trim; cut at −6% per rule.")
        allocations = {"Core": self.slots["core"], "Momentum": self.slots["momentum"], "Wildcard": self.slots["wildcard"]}
        return Verdict(asof=f"{fmt_ts(now)} {self.tz}", composite=composite, risk_label=risk_label,
                       cap_efficiency=cap_efficiency, signals=signals, actions=actions, allocations=allocations)
