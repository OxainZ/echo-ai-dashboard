"""
Basic Echo AI Dashboard Application

This module provides a simplified version of the Echo AI dashboard without authentication.
Intended for development, testing, and demonstration purposes.

Features:
- Real-time market analysis
- Signal monitoring
- Portfolio tracking
- Auto-refresh functionality

Note: This version has no authentication. For production use, see UI.py
"""
from __future__ import annotations
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil import parser
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ==================== BASIC DASHBOARD (NO AUTHENTICATION) ====================
def main():
    """
    Main function for the basic Echo AI dashboard.
    
    Displays a simplified dashboard with:
    - Market signals
    - Portfolio allocations
    - Recommended actions
    
    Auto-refreshes every 30 seconds for real-time updates.
    """
    # Basic page config
    st.set_page_config(
        page_title="Echo AI Dashboard",
        layout="wide",
        page_icon="🚀"
    )

    # Auto-refresh every 30 seconds
    st_autorefresh(interval=30000)

    # Header
    st.markdown("""
    <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white; margin-bottom: 2rem;'>
        <h1>🚀 Echo AI Trading Intelligence</h1>
        <p>Real-time market analysis and signals</p>
        <p style='font-size: 0.9rem; opacity: 0.9;'>No authentication required - Basic deployment test</p>
    </div>
    """, unsafe_allow_html=True)

    # Try to load the Echo Engine
    try:
        from echo.engine.echo_engine import EchoEngine

        # Load configuration
        cfg_path = "echo/config.yaml"
        if os.path.exists(cfg_path):
            # Initialize Echo Engine with configuration
            eng = EchoEngine(cfg_path)
            verdict = eng.run()
            cfg = eng.config
            provider = eng.provider
            slots = eng.slots

            # Success message
            st.success("✅ Echo Engine loaded successfully!")

            # Main metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Composite Conviction", f"{verdict.composite:.0f}/100")

            with col2:
                st.metric("Risk Level", verdict.risk_label)

            with col3:
                st.metric("Capital Efficiency", f"{verdict.cap_efficiency:.1f}%")

            with col4:
                st.metric("Active Signals", len([s for s in verdict.signals if s.severity in ["yellow", "red"]]))

            # Signals section
            st.subheader("📡 Market Signals")
            for signal in verdict.signals[:5]:  # Show first 5 signals
                color = {"green":"🟢","yellow":"🟡","red":"🔴"}.get(signal.severity,"🟢")
                st.markdown(f"{color} **{signal.name}** — {signal.score:.0f}")

            # Actions
            st.subheader("🎯 Recommended Actions")
            if verdict.actions:
                for action in verdict.actions[:3]:  # Show first 3 actions
                    st.info(f"📋 {action}")
            else:
                st.info("✅ No urgent actions required")

            # Portfolio allocation
            st.subheader("📊 Portfolio Allocation")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Core", verdict.allocations.get('Core', 'N/A'))
            with col2:
                st.metric("Momentum", verdict.allocations.get('Momentum', 'N/A'))
            with col3:
                st.metric("Wildcard", verdict.allocations.get('Wildcard', 'N/A'))

        else:
            st.error("❌ Configuration file not found")
            st.info("Please ensure echo/config.yaml is uploaded")

    except ImportError as e:
        st.error(f"❌ Import Error: {e}")
        st.info("🔧 Trying basic mode...")

        # Fallback basic dashboard
        st.warning("⚠️ Running in basic mode - some features may be limited")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Status", "Basic Mode")
        with col2:
            st.metric("Time", datetime.now().strftime("%H:%M:%S"))
        with col3:
            st.metric("Version", "Echo AI v62")

        st.info("📊 This is a simplified version to test deployment")
        st.success("✅ Streamlit Cloud connection working!")

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.info("🔧 Please check the logs for more details")

    # Footer
    st.markdown("---")
    st.caption(f"📅 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 🚀 Echo AI Dashboard")

if __name__ == "__main__":
    main()
