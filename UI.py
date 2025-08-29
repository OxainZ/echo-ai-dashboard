from __future__ import annotations
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
from datetime import datetime, timedelta
from dateutil import parser
from echo.engine.echo_engine import EchoEngine
from echo.engine.reports import format_daily

# Auto-refresh dashboard every 5 seconds
st_autorefresh(interval=5000)

st.set_page_config(page_title="Echo v62 — Local Runner (PLUS)", layout="wide")
st.title("Echo v62 — Local Runner (PLUS)")
st.caption("Local, privacy-first dashboard. Research & decision support only — no trading automation.")

cfg_path = "echo/config.yaml"
eng = EchoEngine(cfg_path)
verdict = eng.run()
cfg = eng.config
provider = eng.provider
slots = eng.slots
now = datetime.now()

# Top metrics
col1, col2, col3 = st.columns(3)
col1.metric("Composite Conviction", f"{verdict.composite:.0f} / 100")
col2.metric("Risk Level", verdict.risk_label)
col3.metric("Capital Efficiency", f"{verdict.cap_efficiency:.1f}%")

# --- Catalyst Stacking Banner ---
stacked_edges = [s for s in verdict.signals if s.severity in ("yellow", "red")]
if len(stacked_edges) >= 2:
    st.warning("🚨 **Catalyst Stacking Alert:** Multiple edges aligned! Review signals and consider action.")

# --- Signals ---
st.subheader("Signals")
for s in verdict.signals:
    color = {"green":"🟢","yellow":"🟡","red":"🔴"}.get(s.severity,"🟢")
    st.markdown(f"{color} **{s.name}** — {s.score:.0f} <br>{s.detail}", unsafe_allow_html=True)

# --- Do This ---
st.subheader("Do This (Echo-aligned, no same-day round trips)")
if verdict.actions:
    for a in verdict.actions:
        st.markdown(f"- {a}")
else:
    st.info("No high-priority actions right now. Patience is a position.")

# --- Allocations ---
st.subheader("Current 3-slot allocations")
st.markdown(f"- Core: **{verdict.allocations['Core']}**")
st.markdown(f"- Momentum: **{verdict.allocations['Momentum']}**")
st.markdown(f"- Wildcard: **{verdict.allocations['Wildcard']}**")

st.divider()

# ===================== EXTRA PANELS =====================

# 1) Loan Heat Map
st.subheader("Loan Heat Map")
loan_cfg = cfg.get("loan_heat_map",{})
loan_sig = next((s for s in verdict.signals if s.name == "Loan Accelerator"), None)
if loan_sig is not None:
    score = getattr(loan_sig, 'score', 0)
    detail = getattr(loan_sig, 'detail', '')
    color_bands = loan_cfg.get("color_bands", {"active": "green", "watch": "yellow", "standby": "gray"})
    if score >= loan_cfg.get("active_min",70):
        st.success(f"ACTIVE — {detail} (Max deploy: ${cfg.get('loan_accelerator',{}).get('loan_cap_usd',500)})")
    elif loan_cfg.get("watch_min",30) <= score < loan_cfg.get("active_min",70):
        st.warning(f"WATCH — {detail}")
    else:
        st.info(detail)
    st.caption(f"Color bands: {color_bands}")
else:
    st.info("No loan signal available")

# 2) Catalyst Countdown
# cSpell:ignore fomc FOMC etfs
st.subheader("Catalyst Countdown")
cal = cfg.get("calendar", {})
countdown_rows = []
# HOW DO I D
for d in cal.get("fomc_dates", []):
    dd = parser.parse(d)
    days = (dd.date() - datetime.now().date()).days
    countdown_rows.append({"Event":"FOMC", "Date": dd.date().isoformat(), "Days": days})
# Earnings
for tk, ds in cal.get("earnings", {}).items():
    dd = parser.parse(ds)
    days = (dd.date() - datetime.now().date()).days
    countdown_rows.append({"Event": f"Earnings:{tk}", "Date": dd.date().isoformat(), "Days": days})
if countdown_rows:
    cdf = pd.DataFrame(countdown_rows).sort_values("Days")
    st.dataframe(cdf, use_container_width=True)
else:
    st.info("No catalysts listed in config.yaml")

# 3) Risk/Reward Heatmap (simple proxy: 20d momentum vs 20d volatility on slots)
st.subheader("Risk/Reward Heatmap")
import numpy as np
rr_cfg = cfg.get("rr_heatmap",{})
rr_rows = []
for label, tk in slots.items():
    try:
        df = provider.history(tk, period="3mo", interval="1d")
        if df is None or df.empty:
            continue
        ret = df["Close"].pct_change()
        mom20 = (df["Close"].iloc[-1] / df["Close"].iloc[-21] - 1.0) if len(df) > 21 else np.nan
        vol20 = ret.rolling(20).std().iloc[-1] * (252**0.5) if len(ret)>20 else np.nan
        rr = (mom20*100) / (vol20*100) if (vol20 and vol20!=0 and not np.isnan(vol20)) else np.nan
        # Color band logic
        color = "gray"
        if rr == rr:
            if rr >= rr_cfg.get("green_min",1.5):
                color = "green"
            elif rr >= rr_cfg.get("yellow_min",1.0):
                color = "yellow"
            elif rr < rr_cfg.get("red_max",1.0):
                color = "red"
        rr_rows.append({"Slot": label.capitalize(), "Ticker": tk, "Momentum(20d)%": round(mom20*100,2) if mom20==mom20 else None,
                        "Vol(ann%)": round(vol20*100,1) if vol20==vol20 else None, "R:R": round(rr,2) if rr==rr else None,
                        "Band": color,
                        "Suggested Stop": f"{rr_cfg.get('stop_pct',5)}%",
                        "Suggested Target": f"{rr_cfg.get('target_pct',10)}%"})
    except Exception as e:
        rr_rows.append({"Slot": label.capitalize(), "Ticker": tk, "Momentum(20d)%": None, "Vol(ann%)": None, "R:R": None, "Band": "gray", "Suggested Stop": None, "Suggested Target": None})
if rr_rows:
    rr_df = pd.DataFrame(rr_rows)
    st.dataframe(rr_df, use_container_width=True)
    st.caption(f"Thresholds: green ≥ {rr_cfg.get('green_min',1.5)}, yellow ≥ {rr_cfg.get('yellow_min',1.0)}, red < {rr_cfg.get('red_max',1.0)} | Stop: {rr_cfg.get('stop_pct',5)}%, Target: {rr_cfg.get('target_pct',10)}%")
else:
    st.info("No data available for R:R right now.")

# 4) Sector Flow Scanner (5d returns on sector ETFs from config)
st.subheader("Sector Flow Scanner (5d Change)")
flows = []
for name, etf in cfg.get("sector_etfs", {}).items():
    try:
        df = provider.history(etf, period="2mo", interval="1d")
        if df is None or df.empty or len(df)<6:
            continue
        c = df["Close"]
        chg5 = (c.iloc[-1]/c.iloc[-6]-1.0)*100
        flows.append({"Sector": name, "ETF": etf, "5d %": round(float(chg5),2)})
    except Exception:
        pass
if flows:
    flows_df = pd.DataFrame(flows).sort_values("5d %", ascending=False)
    st.dataframe(flows_df, use_container_width=True)
else:
    st.info("No sector flow data available.")
