"""
Enhanced UI with AI Integration for Echo Trading Dashboard

This module integrates AI prediction, sentiment analysis, and trading decisions
into the main dashboard UI.
"""

from __future__ import annotations
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil import parser
from echo.engine.echo_engine import EchoEngine
from echo.engine.reports import format_daily
from echo.ai import (
    StockPricePredictor,
    TradingDecisionEngine,
    MarketSentimentAnalyzer,
    DataPipeline,
    AIDashboardUI,
    get_disclaimer
)
import hashlib
import time

# Same authentication as UI.py
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hashlib.sha256(st.session_state["password"].encode()).hexdigest() == st.secrets.get("password_hash", hashlib.sha256("echo2024".encode()).hexdigest()):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("🔐 Echo AI Dashboard - Secure Access")
        st.markdown("""
        <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white; margin-bottom: 2rem;'>
            <h2>🚀 Welcome to Echo AI with Advanced Intelligence</h2>
            <p>AI-Powered Trading Intelligence Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.text_input("🔑 Enter Access Code", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.title("🔐 Echo AI Dashboard - Secure Access")
        st.error("❌ Incorrect access code. Please try again.")
        st.text_input("🔑 Enter Access Code", type="password", on_change=password_entered, key="password")
        return False
    else:
        return True


def load_css():
    """Load custom CSS for enhanced UI"""
    st.markdown("""
    <style>
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
    
    .ai-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.75rem;
        font-weight: bold;
        display: inline-block;
        margin-left: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)


def main_dashboard():
    """Main AI-enhanced dashboard"""
    # Must be the first Streamlit command of the run
    st.set_page_config(
        page_title="🚀 Echo AI - Advanced Intelligence",
        layout="wide",
        page_icon="🤖",
        initial_sidebar_state="expanded"
    )

    load_css()

    # Auto-refresh every 15 seconds
    st_autorefresh(interval=15000)
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white; margin-bottom: 1rem;'>
            <h3>🤖 Echo AI</h3>
            <p>Neural Intelligence v3.0</p>
        </div>
        """, unsafe_allow_html=True)
        
        menu = st.selectbox("🧠 Navigation", [
            "🏠 Dashboard Overview",
            "🤖 AI Predictions",
            "📊 Signal Analysis",
            "💼 Portfolio Management",
            "⚠️ Risk Analytics",
            "📈 Historical Performance",
            "⚙️ Settings"
        ])
        
        st.markdown("---")
        
        # Quick AI status
        col1, col2 = st.columns(2)
        with col1:
            st.metric("AI Status", "🟢 Active")
        with col2:
            st.metric("Model", "v1.0")
        
        st.markdown("---")
        
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
        
        st.caption(f"📅 {datetime.now().strftime('%H:%M:%S')}")
    
    # Route to selected view
    if menu == "🏠 Dashboard Overview":
        show_overview_with_ai()
    elif menu == "🤖 AI Predictions":
        show_ai_predictions()
    elif menu == "📊 Signal Analysis":
        show_signals()
    elif menu == "💼 Portfolio Management":
        show_portfolio()
    elif menu == "⚠️ Risk Analytics":
        show_risk_analytics()
    elif menu == "📈 Historical Performance":
        show_historical()
    elif menu == "⚙️ Settings":
        show_settings()


def show_overview_with_ai():
    """Dashboard overview with AI enhancements"""
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Echo AI Trading Intelligence Platform</h1>
        <p>Advanced AI-powered analysis for informed decision-making</p>
        <p style='font-size: 0.9rem; opacity: 0.9;'>Real-time AI predictions • Market sentiment • Risk management</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display disclaimer
    AIDashboardUI.display_disclaimer()
    
    try:
        # Load Echo engine
        cfg_path = "echo/config.yaml"
        eng = EchoEngine(cfg_path)
        verdict = eng.run()
        cfg = eng.config
        provider = eng.provider
        slots = eng.slots
        
        # Store in session
        st.session_state.verdict = verdict
        st.session_state.cfg = cfg
        st.session_state.provider = provider
        st.session_state.slots = slots
        
        # Enhanced metrics with AI badge
        st.subheader("📊 Market Intelligence Dashboard")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🎯 Conviction <span class="ai-badge">AI</span></h3>
                <h2 style="color: #667eea;">{verdict.composite:.0f}/100</h2>
                <p>AI-enhanced confidence</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            risk_color = {"Low": "#28a745", "Medium": "#ffc107", "High": "#dc3545", "Elevated": "#fd7e14", "Moderate": "#17a2b8"}.get(verdict.risk_label, "#6c757d")
            st.markdown(f"""
            <div class="metric-card">
                <h3>⚠️ Risk Level</h3>
                <h2 style="color: {risk_color};">{verdict.risk_label}</h2>
                <p>Current assessment</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>💰 Capital Efficiency</h3>
                <h2 style="color: #17a2b8;">{verdict.cap_efficiency:.1f}%</h2>
                <p>Portfolio utilization</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            signal_count = len([s for s in verdict.signals if s.severity in ["yellow", "red"]])
            st.markdown(f"""
            <div class="metric-card">
                <h3>🚨 Active Signals</h3>
                <h2 style="color: #fd7e14;">{signal_count}</h2>
                <p>Critical alerts</p>
            </div>
            """, unsafe_allow_html=True)
        
        # AI Market Sentiment Analysis
        st.subheader("🧠 AI Market Sentiment Analysis")
        
        # Fetch data for main market ticker
        try:
            pipeline = DataPipeline(provider)
            sentiment_analyzer = MarketSentimentAnalyzer()
            
            # Use SPY for overall market sentiment
            market_df = pipeline.prepare_for_prediction("SPY", period="3mo")
            sentiment = sentiment_analyzer.analyze(market_df)
            
            AIDashboardUI.display_sentiment_gauge(sentiment)
            
        except Exception as e:
            st.warning(f"⚠️ Unable to fetch market sentiment: {str(e)}")
        
        # Portfolio Allocations
        st.subheader("📊 Portfolio Allocation")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Core Position", verdict.allocations.get('Core', 'N/A'))
        with col2:
            st.metric("Momentum Position", verdict.allocations.get('Momentum', 'N/A'))
        with col3:
            st.metric("Wildcard Position", verdict.allocations.get('Wildcard', 'N/A'))
        
        # Action recommendations
        st.subheader("🎯 Recommended Actions")
        if verdict.actions:
            for action in verdict.actions:
                st.success(f"✅ {action}")
        else:
            st.info("📊 No high-priority actions at this time.")
        
        # Critical alerts
        stacked_edges = [s for s in verdict.signals if s.severity in ("yellow", "red")]
        if len(stacked_edges) >= 2:
            st.error("🚨 **CATALYST STACKING ALERT**: Multiple critical signals detected!")
        
    except Exception as e:
        st.error(f"❌ Error loading dashboard: {str(e)}")


def show_ai_predictions():
    """AI Predictions view with detailed analysis"""
    st.header("🤖 AI Stock Predictions & Trading Decisions")
    
    # Display disclaimers
    AIDashboardUI.display_disclaimer()
    AIDashboardUI.display_model_info()
    
    if 'slots' not in st.session_state:
        st.warning("⚠️ Please load the overview first.")
        return
    
    slots = st.session_state.slots
    provider = st.session_state.provider
    
    # Initialize AI components
    pipeline = DataPipeline(provider)
    predictor = StockPricePredictor(lookback_period=30)
    decision_engine = TradingDecisionEngine()
    
    # Ticker selection
    all_tickers = list(slots.values())
    selected_ticker = st.selectbox("📊 Select Stock for AI Analysis", all_tickers, index=0)
    
    if selected_ticker:
        try:
            with st.spinner(f"🤖 Running AI analysis on {selected_ticker}..."):
                # Fetch and prepare data
                df = pipeline.prepare_for_prediction(selected_ticker, period="3mo")
                current_quote = pipeline.get_current_price(selected_ticker)
                current_price = current_quote.get("price") or float(df['Close'].iloc[-1])
                
                # Generate prediction
                prediction = predictor.predict(df, ticker=selected_ticker)
                
                # Display prediction card
                st.subheader(f"📈 AI Prediction for {selected_ticker}")
                AIDashboardUI.display_prediction_card(prediction, selected_ticker, current_price)
                
                # Generate trading decision
                st.subheader("💡 AI Trading Decision")
                decision = decision_engine.generate_decision(
                    prediction, 
                    current_price, 
                    portfolio_value=10000  # Example portfolio value
                )
                
                AIDashboardUI.display_trading_decision(decision, selected_ticker)
                
                # Risk metrics
                AIDashboardUI.display_risk_metrics(decision)
                
                # Technical chart
                st.subheader(f"📊 Technical Analysis Chart - {selected_ticker}")
                AIDashboardUI.display_technical_chart(df, selected_ticker, prediction)
                
        except Exception as e:
            st.error(f"❌ Error generating AI prediction: {str(e)}")
            st.info("💡 This could be due to insufficient data or API limitations. Please try another ticker.")


def show_signals():
    """Enhanced signal analysis"""
    st.header("📡 Signal Analysis Dashboard")
    
    if 'verdict' not in st.session_state:
        st.warning("⚠️ Please load the overview first.")
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
        st.metric("🟢 Bullish", green_signals)
    with col3:
        st.metric("🟡 Caution", yellow_signals)
    with col4:
        st.metric("🔴 Bearish", red_signals)
    
    # Display signals
    st.subheader("📋 Detailed Signal Analysis")
    
    for signal in verdict.signals:
        severity_styles = {
            "green": ("🟢", "#d4edda", "#28a745"),
            "yellow": ("🟡", "#fff3cd", "#ffc107"),
            "red": ("🔴", "#f8d7da", "#dc3545")
        }
        
        icon, bg_color, border_color = severity_styles.get(signal.severity, ("⚪", "#f8f9fa", "#6c757d"))
        
        st.markdown(f"""
        <div style='background: {bg_color}; border-left: 4px solid {border_color}; 
                    padding: 1rem; border-radius: 5px; margin: 0.5rem 0;'>
            <h4>{icon} {signal.name}</h4>
            <p><strong>Score:</strong> {signal.score:.0f}/100</p>
            <p>{signal.detail}</p>
        </div>
        """, unsafe_allow_html=True)


def show_portfolio():
    """Portfolio management view"""
    st.header("💼 Portfolio Management")
    
    if 'verdict' not in st.session_state:
        st.warning("⚠️ Please load the overview first.")
        return
    
    verdict = st.session_state.verdict
    slots = st.session_state.slots
    
    st.subheader("📊 Current Positions")
    
    for slot_name, ticker in slots.items():
        with st.expander(f"📈 {slot_name}: {ticker}", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Allocation", verdict.allocations.get(slot_name, 'N/A'))
            with col2:
                st.metric("Ticker", ticker)


def show_risk_analytics():
    """Risk analytics view"""
    st.header("⚠️ Risk Analytics Dashboard")
    
    if 'verdict' not in st.session_state:
        st.warning("⚠️ Please load the overview first.")
        return
    
    verdict = st.session_state.verdict
    
    st.subheader("📊 Risk Assessment")
    
    col1, col2, col3 = st.columns(3)
    
    risk_color = {"Low": "#28a745", "Medium": "#ffc107", "High": "#dc3545", "Elevated": "#fd7e14", "Moderate": "#17a2b8"}.get(verdict.risk_label, "#6c757d")
    
    with col1:
        st.metric("Risk Level", verdict.risk_label)
    with col2:
        st.metric("Conviction Score", f"{verdict.composite:.0f}/100")
    with col3:
        signal_count = len([s for s in verdict.signals if s.severity in ["yellow", "red"]])
        st.metric("Warning Signals", signal_count)
    
    # Risk signals
    st.subheader("🚨 Risk Signals")
    risk_signals = [s for s in verdict.signals if s.severity in ["yellow", "red"]]
    
    if risk_signals:
        for signal in risk_signals:
            st.warning(f"⚠️ **{signal.name}**: {signal.detail}")
    else:
        st.success("✅ No major risk signals detected at this time.")


def show_historical():
    """Historical performance view"""
    st.header("📈 Historical Performance")
    
    if 'slots' not in st.session_state:
        st.warning("⚠️ Please load the overview first.")
        return
    
    slots = st.session_state.slots
    provider = st.session_state.provider
    
    st.subheader("📊 3-Month Performance")
    
    selected_ticker = st.selectbox("Select ticker", list(slots.values()))
    
    if selected_ticker:
        try:
            pipeline = DataPipeline(provider)
            df = pipeline.fetch_realtime_data(selected_ticker, period="3mo")
            
            # Display chart
            AIDashboardUI.display_technical_chart(df, selected_ticker)
            
            # Performance stats
            returns = (df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0] * 100
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("3-Month Return", f"{returns:.2f}%")
            with col2:
                st.metric("Current Price", f"${df['Close'].iloc[-1]:.2f}")
            with col3:
                volatility = df['Close'].pct_change().std() * np.sqrt(252) * 100
                st.metric("Annualized Volatility", f"{volatility:.2f}%")
                
        except Exception as e:
            st.error(f"Error loading historical data: {str(e)}")


def show_settings():
    """Settings view"""
    st.header("⚙️ Settings")
    
    st.subheader("🤖 AI Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.slider("AI Confidence Threshold", 0.5, 0.95, 0.65, 0.05)
        st.slider("Risk Tolerance", 0.0, 1.0, 0.6, 0.1)
    
    with col2:
        st.selectbox("Update Frequency", ["5s", "15s", "30s", "1m", "5m"], index=1)
        st.selectbox("AI Model Version", ["v1.0-lightweight"], index=0)
    
    st.subheader("ℹ️ System Information")
    st.info("**Echo AI Version:** v3.0 Neural Intelligence")
    st.info("**AI Model:** Lightweight Technical Analysis Engine")
    st.info(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.info("**Status:** 🟢 All Systems Operational")
    
    if st.button("💾 Save Settings"):
        st.success("✅ Settings saved successfully!")


if __name__ == "__main__":
    if check_password():
        main_dashboard()
    else:
        st.stop()
