Create a new app in streamlit cloud, select UI.py as Main file path.# Tasks Backlog (Prioritized — additive only)

## P0 — UX/Signals
- [ ] Catalyst Stacking Banner (lights up when ≥2 edges confirm)
- [ ] Loan Heat Map thresholds from config (color bands + deploy size suggestions)
- [ ] R:R Heatmap thresholds → green/yellow/red bands + suggested stop/target

## P1 — Data/Providers
- [ ] Optional premium provider scaffolds (Polygon, Finnhub) with env-key read
- [ ] Retry/backoff on provider errors

## P2 — Dashboard
- [ ] Compact Mode (One-Glance + Do This only)
- [ ] Sector Flow → link out to components (e.g., SOXX top holdings)
- [ ] Export buttons: CSV/PNG of current panels

## P3 — Engine
- [ ] Weighting model for Composite Conviction by rule importance
- [ ] Config flags to enable/disable specific rules
- [ ] Simple backtest harness for PEAD/ToM/FOMC heuristics (offline)

## P4 — QA
- [ ] Unit tests for rules (toy data) and engine fusion math
- [ ] CI-friendly lint/format (ruff/black) — optional

## Done
- [x] PLUS panels (Loan Heat Map, Catalyst Countdown, R:R Heatmap, Sector Flow)
