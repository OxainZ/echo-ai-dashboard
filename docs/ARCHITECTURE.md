# Architecture — Echo v62 Local Runner

## High-Level
- `EchoEngine` builds a `context` (time, config, provider, slots), runs all `Rule`s, collects `Signal`s,
  computes Composite Conviction, Risk Label, and "Do This" suggestions.
- Streamlit dashboard visualizes signals + panels; CLI writes a markdown daily report.

## Data Flow
- Provider (`PriceProvider`) → quotes/history → rules compute signals → engine fuses → report/UI.

## Extension Points
- Add a rule: create `echo/rules/my_rule.py` with `Rule.run(context) -> Signal` and register in `EchoEngine.rules`.
- Add a provider: implement `quote()` and `history()` in a new class and switch `providers.price_data.name` in `config.yaml`.
- Add a panel: edit `app_streamlit.py`; read config + provider, render dataframe/metrics.

## Signals Fused Today
- FOMC Tilt, Turn-of-Month, PEAD (Momentum/Wildcard), Volatility Regime, Execution Precision, Loan Accelerator.

## Roadmap Hooks (placeholders to add next)
- Catalyst Stacking Alert (2+ edges align)
- Loan Heat Map color bands from config thresholds
- R:R thresholds + targets/stops display
- Sector Flow cross-check with slot momentum
