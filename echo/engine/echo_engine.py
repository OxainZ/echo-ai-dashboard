"""
Echo Engine - Core Trading Intelligence System

This module implements the main Echo Engine that orchestrates all trading rules,
processes market signals, and generates actionable trading recommendations.

The engine follows a modular architecture where:
1. Data providers fetch market data
2. Rules analyze data and generate signals
3. The engine aggregates signals into a verdict
4. The verdict drives portfolio allocations and actions
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
    Trading Verdict - The final output of the Echo Engine
    
    Attributes:
        asof (str): Timestamp when the verdict was generated
        composite (float): Composite conviction score (0-100)
        risk_label (str): Risk assessment (Low/Moderate/Elevated/High)
        cap_efficiency (float): Capital efficiency percentage
        signals (List[Signal]): All individual signals from rules
        actions (List[str]): Recommended actions to take
        allocations (Dict[str, str]): Portfolio slot allocations
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
    Main Echo Trading Intelligence Engine
    
    The engine orchestrates all trading rules and generates actionable verdicts
    by analyzing market conditions, portfolio positions, and risk factors.
    
    Architecture:
    - Loads configuration from YAML
    - Initializes data providers
    - Runs all registered trading rules
    - Aggregates signals into a composite verdict
    - Generates recommended actions
    
    Attributes:
        config (dict): Configuration loaded from YAML file
        tz (str): Timezone for trading operations
        provider (PriceProvider): Data provider for market data
        slots (dict): Portfolio allocation slots (core, momentum, wildcard)
        rules (List[Rule]): List of active trading rules
    """
    
    def __init__(self, config_path: str = "echo/config.yaml"):
        """
        Initialize the Echo Engine with configuration
        
        Args:
            config_path (str): Path to the YAML configuration file
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If configuration is invalid
        """
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        
        # Extract timezone configuration
        self.tz = self.config.get("timezone", "America/Chicago")
        
        # Initialize data provider
        self.provider = self._build_provider(self.config)
        
        # Load portfolio slots from config
        self.slots = {k: self.config["slots"][k] for k in ["core", "momentum", "wildcard"]}
        
        # Register all trading rules
        self.rules: List[Rule] = [
            FOMCTilt(),           # Federal Reserve meeting catalyst
            TurnOfMonth(),         # Turn-of-month effect
            PEAD("momentum"),      # Post-earnings drift for momentum slot
            PEAD("wildcard"),      # Post-earnings drift for wildcard slot
            VolatilityRegime(),    # Market volatility analysis
            ExecutionPrecision(),  # Trade execution timing
            LoanAccelerator(),     # Leveraged position management
        ]

    def _build_provider(self, cfg: dict):
        """
        Factory method to build the appropriate data provider
        
        Args:
            cfg (dict): Configuration dictionary
            
        Returns:
            PriceProvider: Initialized data provider instance
            
        Raises:
            ValueError: If provider name is not recognized
        """
        name = cfg.get("providers", {}).get("price_data", {}).get("name", "yfinance")
        if name == "yfinance":
            return YFinanceProvider()
        raise ValueError(f"Unknown provider: {name}")

    def run(self) -> Verdict:
        """
        Execute the Echo Engine analysis pipeline
        
        This is the main entry point that:
        1. Gathers current market context
        2. Runs all trading rules
        3. Aggregates signals into a composite score
        4. Assesses overall risk level
        5. Generates recommended actions
        6. Returns a complete trading verdict
        
        Returns:
            Verdict: Complete trading recommendation with signals and actions
            
        Note:
            Individual rule failures are logged but don't stop execution.
            The engine continues with available signals.
        """
        now = now_tz(self.tz)
        
        # Build execution context for rules
        context = {
            "now": now,
            "tz": self.tz,
            "config": self.config,
            "provider": self.provider,
            "slots": self.slots
        }
        
        # Execute all trading rules and collect signals
        signals: List[Signal] = []
        for r in self.rules:
            try:
                signals.append(r.run(context))
            except Exception as e:
                log.exception(f"Rule {r.__class__.__name__} failed: {e}")

        # Calculate composite conviction score (0-100)
        composite = sum(s.score for s in signals) / len(signals) if signals else 0.0
        
        # Assess overall risk level based on signal severities
        risk_label = "Moderate"
        for s in signals:
            if s.severity == "red":
                risk_label = "High"
                break
            if s.severity == "yellow":
                risk_label = "Elevated"
        
        # Calculate capital efficiency (bounded 10-100%)
        cap_efficiency = min(100.0, max(10.0, composite))
        
        # Generate actionable recommendations based on signals
        actions: List[str] = []
        for s in signals:
            # FOMC catalyst recommendations
            if s.name == "FOMC Tilt" and s.score >= 70:
                actions.append(
                    "Core: consider +5–10% add pre-FOMC (respect cash buffer & no same-day round trips)."
                )
            # Post-earnings drift recommendations
            if s.name.startswith("PEAD:") and s.score >= 60:
                slot_name = s.name.split(':', 1)[1]
                actions.append(
                    f"{slot_name}: hold through drift window; trim systematically on strength."
                )
            # Loan accelerator recommendations
            if s.name == "Loan Accelerator" and s.score >= 70:
                actions.append(
                    "Loan: ACTIVE — deploy ≤ 55% of loan, repay with first +10% trim; cut at −6% per rule."
                )
        
        # Map allocations with proper capitalization for display
        allocations = {
            "Core": self.slots["core"],
            "Momentum": self.slots["momentum"],
            "Wildcard": self.slots["wildcard"]
        }
        
        # Return complete verdict
        return Verdict(
            asof=f"{fmt_ts(now)} {self.tz}",
            composite=composite,
            risk_label=risk_label,
            cap_efficiency=cap_efficiency,
            signals=signals,
            actions=actions,
            allocations=allocations
        )
