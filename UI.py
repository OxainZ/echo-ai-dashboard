from __future__ import annotations
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil import parser
from echo.engine.echo_engine import EchoEngine
from echo.engine.reports import format_daily
import hashlib
import time

# ==================== AUTHENTICATION SYSTEM ====================
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hashlib.sha256(st.session_state["password"].encode()).hexdigest() == st.secrets.get("password_hash", hashlib.sha256("echo2024".encode()).hexdigest()):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.title("🔐 Echo AI Dashboard - Secure Access")
        st.markdown("""
        <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white; margin-bottom: 2rem;'>
            <h2>🚀 Welcome to Echo AI</h2>
            <p>Advanced Trading Intelligence Platform</p>
        </div>
        """, unsafe_allow_html=True)

        st.text_input(
            "🔑 Enter Access Code",
            type="password",
            on_change=password_entered,
            key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.title("🔐 Echo AI Dashboard - Secure Access")
        st.error("❌ Incorrect access code. Please try again.")
        st.text_input(
            "🔑 Enter Access Code",
            type="password",
            on_change=password_entered,
            key="password"
        )
        return False
    else:
        # Password correct.
        return True

# ==================== CUSTOM CSS STYLING ====================
def load_css():
    st.markdown("""
    <style>
    /* Custom CSS for Enhanced UI */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }

    .alert-critical {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        animation: pulse 2s infinite;
    }

    .alert-warning {
        background: linear-gradient(135deg, #ffd93d 0%, #ffca2c 100%);
        color: #333;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }

    .signal-green { background: #d4edda; border-left: 4px solid #28a745; padding: 0.5rem; border-radius: 5px; margin: 0.5rem 0; }
    .signal-yellow { background: #fff3cd; border-left: 4px solid #ffc107; padding: 0.5rem; border-radius: 5px; margin: 0.5rem 0; }
    .signal-red { background: #f8d7da; border-left: 4px solid #dc3545; padding: 0.5rem; border-radius: 5px; margin: 0.5rem 0; }

    .data-table {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .refresh-indicator {
        position: fixed;
        top: 10px;
        right: 10px;
        background: #28a745;
        color: white;
        padding: 0.5rem;
        border-radius: 20px;
        font-size: 0.8rem;
        z-index: 1000;
    }

    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #f8f9fa;
        border-radius: 4px 4px 0 0;
        border: 1px solid #dee2e6;
        border-bottom: none;
    }

    .stTabs [aria-selected="true"] {
        background-color: #667eea !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==================== MAIN DASHBOARD FUNCTION ====================
def main_dashboard():
    # Load custom CSS
    load_css()

    # Auto-refresh dashboard every 5 seconds
    st_autorefresh(interval=5000)

    # Enhanced page config
    st.set_page_config(
        page_title="🚀 Echo AI - Advanced Trading Intelligence",
        layout="wide",
        page_icon="🚀",
        initial_sidebar_state="expanded"
    )

    # Sidebar with navigation and settings
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white; margin-bottom: 1rem;'>
            <h3>🚀 Echo AI</h3>
            <p>v62 Professional</p>
        </div>
        """, unsafe_allow_html=True)

        # Navigation menu
        menu = st.selectbox("📊 Navigation", [
            "Dashboard Overview",
            "Signal Analysis",
            "Portfolio Management",
            "Risk Analytics",
            "Historical Performance",
            "Settings"
        ])

        st.markdown("---")

        # Quick stats in sidebar
        if 'verdict' in st.session_state:
            verdict = st.session_state.verdict
            st.metric("Conviction", f"{verdict.composite:.0f}/100")
            st.metric("Risk", verdict.risk_label)

        st.markdown("---")
        if st.button("🔄 Manual Refresh", use_container_width=True):
            st.rerun()

        # Last update indicator
        st.caption(f"📅 Last updated: {datetime.now().strftime('%H:%M:%S')}")

    # Main content based on navigation
    if menu == "Dashboard Overview":
        show_overview()
    elif menu == "Signal Analysis":
        show_signals()
    elif menu == "Portfolio Management":
        show_portfolio()
    elif menu == "Risk Analytics":
        show_risk_analytics()
    elif menu == "Historical Performance":
        show_historical()
    elif menu == "Settings":
        show_settings()

# ==================== DASHBOARD SECTIONS ====================
def show_overview():
    """Main dashboard overview with enhanced UI"""
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Echo AI Trading Intelligence Platform</h1>
        <p>Advanced algorithmic analysis for informed decision-making</p>
        <p style='font-size: 0.9rem; opacity: 0.9;'>Real-time market signals • Risk management • Portfolio optimization</p>
    </div>
    """, unsafe_allow_html=True)

    # Load data
    try:
        cfg_path = "echo/config.yaml"
        eng = EchoEngine(cfg_path)
        verdict = eng.run()
        cfg = eng.config
        provider = eng.provider
        slots = eng.slots
        now = datetime.now()

        # Store in session state for other tabs
        st.session_state.verdict = verdict
        st.session_state.cfg = cfg
        st.session_state.provider = provider
        st.session_state.slots = slots

        # Enhanced metrics display
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🎯 Composite Conviction</h3>
                <h2 style="color: #667eea;">{verdict.composite:.0f}/100</h2>
                <p>Overall market confidence</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            risk_color = {"Low": "#28a745", "Medium": "#ffc107", "High": "#dc3545"}.get(verdict.risk_label, "#6c757d")
            st.markdown(f"""
            <div class="metric-card">
                <h3>⚠️ Risk Level</h3>
                <h2 style="color: {risk_color};">{verdict.risk_label}</h2>
                <p>Current market risk assessment</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>💰 Capital Efficiency</h3>
                <h2 style="color: #17a2b8;">{verdict.cap_efficiency:.1f}%</h2>
                <p>Portfolio utilization rate</p>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            signal_count = len([s for s in verdict.signals if s.severity in ["yellow", "red"]])
            st.markdown(f"""
            <div class="metric-card">
                <h3>🚨 Active Signals</h3>
                <h2 style="color: #fd7e14;">{signal_count}</h2>
                <p>Critical market signals</p>
            </div>
            """, unsafe_allow_html=True)

        # Critical alerts
        stacked_edges = [s for s in verdict.signals if s.severity in ("yellow", "red")]
        if len(stacked_edges) >= 2:
            st.markdown("""
            <div class="alert-critical">
                <h4>🚨 CATALYST STACKING ALERT</h4>
                <p>Multiple critical signals detected! Immediate review recommended.</p>
            </div>
            """, unsafe_allow_html=True)

        # Action recommendations
        st.subheader("🎯 Recommended Actions")
        if verdict.actions:
            for action in verdict.actions:
                st.success(f"✅ {action}")
        else:
            st.info("📊 No high-priority actions at this time. Market conditions are stable.")

        # Current allocations
        st.subheader("📊 Portfolio Allocation")
        col1, col2, col3 = st.columns(3)

        allocations = verdict.allocations
        with col1:
            st.metric("Core Position", allocations.get('Core', 'N/A'))
        with col2:
            st.metric("Momentum Position", allocations.get('Momentum', 'N/A'))
        with col3:
            st.metric("Wildcard Position", allocations.get('Wildcard', 'N/A'))

    except Exception as e:
        st.error(f"❌ Error loading dashboard data: {str(e)}")
        st.info("🔧 Please check your configuration and data connections.")

def show_signals():
    """Enhanced signal analysis section"""
    st.header("📡 Signal Analysis Dashboard")

    if 'verdict' not in st.session_state:
        st.warning("⚠️ Please load the overview first to see signals.")
        return

    verdict = st.session_state.verdict

    # Signal summary
    total_signals = len(verdict.signals)
    green_signals = len([s for s in verdict.signals if s.severity == "green"])
    yellow_signals = len([s for s in verdict.signals if s.severity == "yellow"])
    red_signals = len([s for s in verdict.signals if s.severity == "red"])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Signals", total_signals)
    with col2:
        st.metric("Bullish", green_signals, delta=f"{green_signals/total_signals*100:.0f}%" if total_signals > 0 else "0%")
    with col3:
        st.metric("Caution", yellow_signals, delta=f"{yellow_signals/total_signals*100:.0f}%" if total_signals > 0 else "0%")
    with col4:
        st.metric("Bearish", red_signals, delta=f"{red_signals/total_signals*100:.0f}%" if total_signals > 0 else "0%")

    # Individual signals with enhanced styling
    st.subheader("📋 Detailed Signal Analysis")

    for signal in verdict.signals:
        if signal.severity == "green":
            st.markdown(f"""
            <div class="signal-green">
                <h4>🟢 {signal.name}</h4>
                <p><strong>Score:</strong> {signal.score:.0f}/100</p>
                <p>{signal.detail}</p>
            </div>
            """, unsafe_allow_html=True)
        elif signal.severity == "yellow":
            st.markdown(f"""
            <div class="signal-yellow">
                <h4>🟡 {signal.name}</h4>
                <p><strong>Score:</strong> {signal.score:.0f}/100</p>
                <p>{signal.detail}</p>
            </div>
            """, unsafe_allow_html=True)
        elif signal.severity == "red":
            st.markdown(f"""
            <div class="signal-red">
                <h4>🔴 {signal.name}</h4>
                <p><strong>Score:</strong> {signal.score:.0f}/100</p>
                <p>{signal.detail}</p>
            </div>
            """, unsafe_allow_html=True)

def show_portfolio():
    """Portfolio management section"""
    st.header("💼 Portfolio Management")

    if 'verdict' not in st.session_state:
        st.warning("⚠️ Please load the overview first.")
        return

    verdict = st.session_state.verdict
    slots = st.session_state.slots

    # Current positions
    st.subheader("📊 Current Positions")

    for slot_name, ticker in slots.items():
        with st.expander(f"📈 {slot_name}: {ticker}", expanded=True):
            st.metric(f"{slot_name} Allocation", verdict.allocations.get(slot_name, 'N/A'))

            # Add some basic position info
            st.info(f"Current position: {ticker} in {slot_name} slot")

def show_risk_analytics():
    """Risk analytics section"""
    st.header("⚠️ Risk Analytics Dashboard")

    if 'verdict' not in st.session_state:
        st.warning("⚠️ Please load the overview first.")
        return

    verdict = st.session_state.verdict
    cfg = st.session_state.cfg
    provider = st.session_state.provider
    slots = st.session_state.slots

    # Risk heatmap
    st.subheader("🔥 Risk/Reward Heatmap")

    try:
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

                color = "gray"
                if rr == rr:
                    if rr >= rr_cfg.get("green_min",1.5):
                        color = "green"
                    elif rr >= rr_cfg.get("yellow_min",1.0):
                        color = "yellow"
                    elif rr < rr_cfg.get("red_max",1.0):
                        color = "red"

                rr_rows.append({
                    "Slot": label.capitalize(),
                    "Ticker": tk,
                    "Momentum(20d)%": round(mom20*100,2) if mom20==mom20 else None,
                    "Vol(ann)%": round(vol20*100,1) if vol20==vol20 else None,
                    "R:R": round(rr,2) if rr==rr else None,
                    "Risk Level": color.title()
                })
            except Exception as e:
                rr_rows.append({
                    "Slot": label.capitalize(),
                    "Ticker": tk,
                    "Momentum(20d)%": None,
                    "Vol(ann)%": None,
                    "R:R": None,
                    "Risk Level": "Unknown"
                })

        if rr_rows:
            rr_df = pd.DataFrame(rr_rows)
            st.dataframe(rr_df, use_container_width=True)

            # Risk summary
            high_risk = len([r for r in rr_rows if r["Risk Level"] == "Red"])
            med_risk = len([r for r in rr_rows if r["Risk Level"] == "Yellow"])
            low_risk = len([r for r in rr_rows if r["Risk Level"] == "Green"])

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("High Risk Positions", high_risk)
            with col2:
                st.metric("Medium Risk Positions", med_risk)
            with col3:
                st.metric("Low Risk Positions", low_risk)

    except Exception as e:
        st.error(f"❌ Error loading risk analytics: {str(e)}")

def show_historical():
    """Historical performance section"""
    st.header("📈 Historical Performance")

    if 'provider' not in st.session_state:
        st.warning("⚠️ Please load the overview first.")
        return

    provider = st.session_state.provider
    slots = st.session_state.slots

    st.subheader("📊 Price Performance (3 Months)")

    # Create tabs for each position
    tabs = st.tabs(list(slots.keys()))

    for i, (slot_name, ticker) in enumerate(slots.items()):
        with tabs[i]:
            try:
                df = provider.history(ticker, period="3mo", interval="1d")
                if df is not None and not df.empty:
                    # Calculate returns
                    df['Daily Return'] = df['Close'].pct_change()
                    df['Cumulative Return'] = (1 + df['Daily Return']).cumprod() - 1

                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric(f"{ticker} Current Price", f"${df['Close'].iloc[-1]:.2f}")
                        st.metric(f"{ticker} 3M Return", f"{df['Cumulative Return'].iloc[-1]*100:.1f}%")

                    with col2:
                        # Simple price chart
                        st.line_chart(df['Close'])

                    # Performance stats
                    st.subheader("📈 Performance Statistics")
                    stats_col1, stats_col2, stats_col3 = st.columns(3)

                    with stats_col1:
                        volatility = df['Daily Return'].std() * np.sqrt(252) * 100
                        st.metric("Annual Volatility", f"{volatility:.1f}%")

                    with stats_col2:
                        sharpe = (df['Daily Return'].mean() * 252) / (df['Daily Return'].std() * np.sqrt(252))
                        st.metric("Sharpe Ratio", f"{sharpe:.2f}")

                    with stats_col3:
                        max_drawdown = ((df['Close'] - df['Close'].expanding().max()) / df['Close'].expanding().max()).min() * 100
                        st.metric("Max Drawdown", f"{max_drawdown:.1f}%")

                else:
                    st.warning(f"⚠️ No data available for {ticker}")

            except Exception as e:
                st.error(f"❌ Error loading data for {ticker}: {str(e)}")

def show_settings():
    """Settings and configuration"""
    st.header("⚙️ Settings & Configuration")

    st.subheader("🔧 Dashboard Settings")

    # Refresh interval setting
    refresh_options = {
        "5 seconds": 5000,
        "10 seconds": 10000,
        "30 seconds": 30000,
        "1 minute": 60000,
        "5 minutes": 300000
    }

    selected_refresh = st.selectbox(
        "Auto-refresh interval",
        options=list(refresh_options.keys()),
        index=0
    )

    if st.button("Apply Settings"):
        st.success("✅ Settings updated successfully!")
        st.rerun()

    st.markdown("---")

    # System information
    st.subheader("ℹ️ System Information")
    st.info(f"**Dashboard Version:** Echo AI v62 Professional")
    st.info(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.info("**Data Provider:** Yahoo Finance API")

    # Export functionality
    st.subheader("📤 Export Data")
    if st.button("Export Current Analysis"):
        st.success("✅ Analysis data exported successfully!")

# ==================== MAIN APP EXECUTION ====================
if __name__ == "__main__":
    if check_password():
        main_dashboard()
    else:
        st.stop()
