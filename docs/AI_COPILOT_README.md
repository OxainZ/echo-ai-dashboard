# Echo v62 — AI Copilot Context Pack

Use this file as the **system/project brief** for any coding copilot (GitHub Copilot Chat, Cursor, Continue, etc.).
Paste the short version (below) into your copilot's workspace instructions and keep this repository open so
the copilot can read the full docs.

## Short Project Brief (paste this into your copilot)
- Project: Echo v62 Local Runner (research-only trading decision support; no brokerage orders)
- Tech: Python 3.11+, Streamlit dashboard, pluggable data providers (default: yfinance), modular rules.
- Core tickers: Core=QQQ, Momentum=TSLA, Wildcard=AMZN (configurable in `echo/config.yaml`).
- Key features to preserve: Composite Conviction (0–100), risk label, "Do This" actions (no same-day round trips),
  Loan Accelerator gating, FOMC Tilt, Turn-of-Month, PEAD, Volatility Regime, VWAP/Execution guidance, Catalyst Countdown,
  Risk/Reward Heatmap, Sector Flow Scanner.
- Constraints: Do not remove existing features; only additive upgrades. No trading automation. Keep privacy-first.
- Quality bar: clean architecture, testable units, typed functions, small modules.
- Priority backlog is in `docs/TASKS_BACKLOG.md`.

## Repo Map
- `echo/engine` — orchestration + reporting
- `echo/rules` — modular signal rules (add new ones here)
- `echo/data_providers` — pluggable price/data sources
- `echo/app_streamlit.py` — dashboard UI
- `echo/main.py` — CLI report writer
- `echo/config.yaml` — user config
- `docs/` — specs, backlog, conventions
- `.vscode/` — recommended workspace settings/extensions

## Design Goals
- Keep Echo **local** and **modular**.
- Treat outputs as **research**. No order placement.
- Every new feature is toggled/configurable via `config.yaml`.
- Prefer pure-Python + minimal deps. Optional providers added cleanly.
