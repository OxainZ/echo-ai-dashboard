from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict
from .echo_engine import Verdict

@dataclass
class Report:
    title: str
    asof: str
    sources: List[str]
    bullets: List[str]
    actions: List[str]
    allocations: Dict[str,str]

def format_daily(verdict: Verdict) -> str:
    lines = []
    lines.append(f"As of {verdict.asof}")
    lines.append("")
    lines.append("## Echo One-Glance")
    lines.append(f"- Composite Conviction: **{verdict.composite:.0f}/100**")
    lines.append(f"- Risk Level: **{verdict.risk_label}**")
    lines.append(f"- Capital Efficiency: **{verdict.cap_efficiency:.1f}%**")
    lines.append("")
    lines.append("## Signals")
    for s in verdict.signals:
        color = {"green":"🟢","yellow":"🟡","red":"🔴"}.get(s.severity,"🟢")
        lines.append(f"- {color} **{s.name}**: {s.score:.0f} — {s.detail}")
    lines.append("")
    lines.append("## Do This (Echo-aligned, no same-day round trips)")
    for a in verdict.actions:
        lines.append(f"- {a}")
    lines.append("")
    lines.append("## Current 3-slot allocations")
    for k,v in verdict.allocations.items():
        lines.append(f"- {k}: {v}")
    return "\n".join(lines)
