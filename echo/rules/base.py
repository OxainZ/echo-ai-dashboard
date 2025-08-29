from dataclasses import dataclass
@dataclass
class Signal:
    name: str
    score: float     # 0..100
    detail: str
    severity: str = "green"  # green|yellow|red
class Rule:
    def run(self, context) -> Signal:
        raise NotImplementedError
