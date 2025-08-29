from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Position:
    ticker: str
    shares: float = 0.0
    cost_basis: float = 0.0

@dataclass
class Portfolio:
    slots: Dict[str, Position] = field(default_factory=dict)
    cash_usd: float = 0.0
    @classmethod
    def from_config(cls, slots_cfg: Dict[str, str]):
        return cls(slots={k: Position(ticker=v) for k,v in slots_cfg.items()})
