"""
Base Classes for Trading Rules and Signals

This module defines the core abstractions for the Echo trading system:
- Signal: Represents a trading signal with score and severity
- Rule: Base class for all trading rule implementations

All trading rules must inherit from Rule and implement the run() method
to analyze market conditions and return a Signal.
"""
from dataclasses import dataclass

@dataclass
class Signal:
    """
    Trading Signal - Output of a trading rule analysis
    
    Represents a specific market insight or trading opportunity identified
    by a rule. Signals are aggregated by the engine to form a verdict.
    
    Attributes:
        name (str): Human-readable name of the signal
        score (float): Conviction score from 0 (bearish) to 100 (bullish)
        detail (str): Detailed explanation of the signal
        severity (str): Risk level - "green" (low), "yellow" (medium), "red" (high)
    """
    name: str
    score: float     # 0..100
    detail: str
    severity: str = "green"  # green|yellow|red

class Rule:
    """
    Base class for all trading rules
    
    A rule analyzes specific market conditions, patterns, or catalysts
    to generate trading signals. Each rule operates independently and
    returns a single Signal with its assessment.
    
    Subclasses must implement:
        run(context) -> Signal: Analyze market and return signal
        
    The context dictionary provides:
        - now: Current timestamp
        - tz: Timezone
        - config: Configuration dictionary
        - provider: Data provider for market data
        - slots: Portfolio allocation slots
    """
    
    def run(self, context) -> Signal:
        """
        Execute rule analysis and generate signal
        
        Args:
            context (dict): Execution context with market data and config
            
        Returns:
            Signal: Trading signal with score and recommendation
            
        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        raise NotImplementedError
