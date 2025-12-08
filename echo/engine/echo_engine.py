"""
Echo Engine - Core Trading Intelligence System

This module implements the Echo trading intelligence engine, which aggregates
multiple trading rules and market signals to generate actionable trading verdicts.

The engine evaluates market conditions through various rules (FOMC events, turn-of-month,
post-earnings drift, volatility regime, etc.) and produces composite signals with
risk assessments and recommended actions.
"""

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
    """
    Trading verdict output from the Echo Engine.
    
    Attributes:
        asof: Timestamp and timezone of the verdict generation
        composite: Composite conviction score (0-100) aggregated from all signals
        risk_label: Overall risk assessment (Low/Moderate/Elevated/High)
        cap_efficiency: Capital efficiency metric (0-100)
        signals: List of individual signals from each trading rule
        actions: List of recommended trading actions based on signals
        allocations: Current portfolio allocation across slots (Core/Momentum/Wildcard)
    """
    asof: str
    composite: float
    risk_label: str
    cap_efficiency: float
    signals: List[Signal]
    actions: List[str]
    allocations: Dict[str, str]

class EchoEngine:
    """
    Echo Trading Intelligence Engine.
    
    The Echo Engine is the core component that orchestrates multiple trading rules
    and market analysis strategies to produce comprehensive trading verdicts.
    
    The engine:
    1. Loads configuration from YAML file
    2. Initializes data providers for market data
    3. Instantiates trading rules (FOMC, TOM, PEAD, Volatility, etc.)
    4. Runs all rules to generate signals
    5. Aggregates signals into a composite verdict with risk assessment
    6. Generates actionable trading recommendations
    
    Attributes:
        config: Configuration dictionary loaded from YAML
        tz: Timezone for timestamp localization (default: America/Chicago)
        provider: Market data provider instance (e.g., YFinanceProvider)
        slots: Portfolio slot allocations (core, momentum, wildcard)
        rules: List of trading rule instances to evaluate
    
    Example:
        >>> engine = EchoEngine("echo/config.yaml")
        >>> verdict = engine.run()
        >>> print(f"Composite Score: {verdict.composite}")
        >>> print(f"Risk Level: {verdict.risk_label}")
        >>> for signal in verdict.signals:
        ...     print(f"{signal.name}: {signal.score}")
    """
    
    def __init__(self, config_path: str = "echo/config.yaml"):
        """
        Initialize the Echo Engine with configuration.
        
        Args:
            config_path: Path to YAML configuration file containing:
                - timezone: Market timezone
                - providers: Data provider configuration
                - slots: Portfolio allocation slots
                
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is malformed
        """
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
        """
        Build and initialize market data provider based on configuration.
        
        Args:
            cfg: Configuration dictionary containing provider settings
            
        Returns:
            Initialized data provider instance
            
        Raises:
            ValueError: If provider name is unknown or unsupported
        """
        name = cfg.get("providers",{}).get("price_data",{}).get("name","yfinance")
        if name == "yfinance":
            return YFinanceProvider()
        raise ValueError(f"Unknown provider: {name}")

    def run(self) -> Verdict:
        """
        Execute all trading rules and generate a comprehensive trading verdict.
        
        This is the main method that:
        1. Gets current timestamp in configured timezone
        2. Builds context with timestamp, config, provider, and slots
        3. Runs each trading rule to generate signals
        4. Aggregates signals into composite score
        5. Determines risk level based on signal severities
        6. Calculates capital efficiency metrics
        7. Generates actionable trading recommendations
        8. Returns complete verdict with all information
        
        Returns:
            Verdict: Complete trading verdict containing:
                - asof: Timestamp of verdict
                - composite: Aggregated conviction score (0-100)
                - risk_label: Risk assessment (Moderate/Elevated/High)
                - cap_efficiency: Capital efficiency metric
                - signals: Individual signals from all rules
                - actions: Recommended trading actions
                - allocations: Portfolio slot allocations
                
        Note:
            - Failed rules are logged but don't halt execution
            - Composite score is average of all successful signals
            - Risk label prioritizes highest severity (red > yellow > green)
            - Actions are generated based on specific signal thresholds
            
        Example:
            >>> engine = EchoEngine()
            >>> verdict = engine.run()
            >>> if verdict.risk_label == "High":
            ...     print("High risk detected, exercise caution")
            >>> for action in verdict.actions:
            ...     print(action)
        """
        now = now_tz(self.tz)
        context = {"now": now, "tz": self.tz, "config": self.config, "provider": self.provider, "slots": self.slots}
        signals: List[Signal] = []
        for r in self.rules:
            try:
                signals.append(r.run(context))
            except Exception as e:
                log.exception(f"Rule {r.__class__.__name__} failed: {e}")

        # Calculate composite conviction score (average of all signals)
        composite = sum(s.score for s in signals)/len(signals) if signals else 0.0
        
        # Determine risk level based on signal severities
        risk_label = "Moderate"
        for s in signals:
            if s.severity == "red": risk_label = "High"; break
            if s.severity == "yellow": risk_label = "Elevated"
            
        # Calculate capital efficiency (clamped between 10-100)
        cap_efficiency = min(100.0, max(10.0, composite))
        
        # Generate actionable recommendations based on signal thresholds
        actions: List[str] = []
        for s in signals:
            if s.name == "FOMC Tilt" and s.score >= 70:
                actions.append("Core: consider +5–10% add pre-FOMC (respect cash buffer & no same-day round trips).")
            if s.name.startswith("PEAD:") and s.score >= 60:
                actions.append(f"{s.name.split(':',1)[1]}: hold through drift window; trim systematically on strength.")
            if s.name == "Loan Accelerator" and s.score >= 70:
                actions.append("Loan: ACTIVE — deploy ≤ 55% of loan, repay with first +10% trim; cut at −6% per rule.")
                
        # Get current portfolio allocations
        allocations = {"Core": self.slots["core"], "Momentum": self.slots["momentum"], "Wildcard": self.slots["wildcard"]}
        
        return Verdict(asof=f"{fmt_ts(now)} {self.tz}", composite=composite, risk_label=risk_label,
                       cap_efficiency=cap_efficiency, signals=signals, actions=actions, allocations=allocations)
