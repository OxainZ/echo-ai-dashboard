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

# Try to import with error handling
try:
    from echo.engine.echo_engine import EchoEngine
    from echo.engine.reports import format_daily
    IMPORT_SUCCESS = True
except ImportError as e:
    st.error(f"❌ Import Error: {e}")
    st.error("Please check that all echo modules are properly uploaded to Streamlit Cloud")
    IMPORT_SUCCESS = False
    EchoEngine = None
    format_daily = None

# ==================== SIMPLE DIAGNOSTIC MODE ====================
def diagnostic_mode():
    """Simple diagnostic version to test basic functionality"""
    st.title("🔧 Echo AI - Diagnostic Mode")

    st.success("✅ Streamlit is working!")
    st.info(f"📅 Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Test imports
    if IMPORT_SUCCESS:
        st.success("✅ Echo Engine imports successful")
    else:
        st.error("❌ Echo Engine import failed")
        return

    # Test basic data loading
    try:
        cfg_path = "echo/config.yaml"
        if os.path.exists(cfg_path):
            st.success("✅ Config file found")
            if EchoEngine is not None:
                eng = EchoEngine(cfg_path)
                verdict = eng.run()
                st.success("✅ Engine execution successful")

                # Show basic metrics
                col1, col2, col3 = st.columns(3)
                col1.metric("Conviction", f"{verdict.composite:.0f}/100")
                col2.metric("Risk", verdict.risk_label)
                col3.metric("Signals", len(verdict.signals))

                st.success("🎉 Full dashboard should work! Try redeploying with the main UI.py")
            else:
                st.error("❌ EchoEngine is not available")
        else:
            st.error(f"❌ Config file not found at {cfg_path}")
            st.info("Please ensure echo/config.yaml is uploaded to Streamlit Cloud")

    except Exception as e:
        st.error(f"❌ Engine execution failed: {str(e)}")
        st.info("This might be due to missing dependencies or configuration issues")

# ==================== MAIN APP ====================
def main():
    st.set_page_config(
        page_title="Echo AI - Diagnostic",
        layout="wide",
        page_icon="🔧"
    )

    # Auto-refresh every 30 seconds for diagnostic
    st_autorefresh(interval=30000)

    # Sidebar for navigation
    with st.sidebar:
        st.title("🔧 Diagnostic Tools")
        mode = st.selectbox("Mode", ["Diagnostic", "Full Dashboard"])

        if st.button("🔄 Refresh"):
            st.rerun()

    if mode == "Diagnostic":
        diagnostic_mode()
    else:
        st.info("Switch to Diagnostic mode first to test basic functionality")

if __name__ == "__main__":
    main()
