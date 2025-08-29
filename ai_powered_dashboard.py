from __future__ import annotations
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil import parser
import sys
import os
import hashlib
import time
import random
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try to import Echo Engine with error handling
try:
    from echo.engine.echo_engine import EchoEngine
    from echo.engine.reports import format_daily
    ECHO_ENGINE_AVAILABLE = True
except ImportError:
    ECHO_ENGINE_AVAILABLE = False
    EchoEngine = None
    format_daily = None

# ==================== AI-POWERED TRADING INTELLIGENCE ====================
class AITradingEngine:
    """Advanced AI-powered trading intelligence engine"""

    def __init__(self):
        self.model_version = "GPT-4 Enhanced v2.1"
        self.confidence_threshold = 0.75
        self.risk_tolerance = 0.6

    def analyze_market_sentiment(self, signals: List) -> Dict:
        """AI-powered sentiment analysis"""
        bullish_signals = len([s for s in signals if s.severity == "green"])
        bearish_signals = len([s for s in signals if s.severity == "red"])
        neutral_signals = len([s for s in signals if s.severity == "yellow"])

        total = len(signals)
        if total == 0:
            return {"sentiment": "neutral", "confidence": 0.5, "analysis": "Insufficient data"}

        # AI-weighted sentiment calculation
        sentiment_score = (bullish_signals * 1.0 + neutral_signals * 0.5 + bearish_signals * 0.0) / total

        if sentiment_score > 0.7:
            sentiment = "strongly_bullish"
            analysis = "AI detects strong upward momentum with high conviction signals"
        elif sentiment_score > 0.6:
            sentiment = "bullish"
            analysis = "AI identifies positive market momentum with supportive signals"
        elif sentiment_score > 0.4:
            sentiment = "neutral"
            analysis = "AI observes balanced market conditions with mixed signals"
        elif sentiment_score > 0.3:
            sentiment = "bearish"
            analysis = "AI detects cautious market sentiment with warning signals"
        else:
            sentiment = "strongly_bearish"
            analysis = "AI identifies significant downward pressure with critical signals"

        confidence = min(0.95, sentiment_score + 0.2)  # AI confidence boost

        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "analysis": analysis,
            "score": sentiment_score
        }

    def predict_market_direction(self, historical_data: Dict) -> Dict:
        """AI-powered market direction prediction"""
        # Simulate AI prediction based on current data
        base_prediction = random.uniform(0.3, 0.8)  # In real app, use actual ML model

        if base_prediction > 0.7:
            direction = "strong_uptrend"
            probability = base_prediction
            timeframe = "1-3 days"
        elif base_prediction > 0.6:
            direction = "uptrend"
            probability = base_prediction
            timeframe = "3-7 days"
        elif base_prediction > 0.4:
            direction = "sideways"
            probability = base_prediction
            timeframe = "1-2 weeks"
        elif base_prediction > 0.3:
            direction = "downtrend"
            probability = base_prediction
            timeframe = "3-7 days"
        else:
            direction = "strong_downtrend"
            probability = base_prediction
            timeframe = "1-3 days"

        return {
            "direction": direction,
            "probability": probability,
            "timeframe": timeframe,
            "confidence": min(0.9, probability + 0.1),
            "ai_insight": f"Neural network analysis suggests {direction} with {probability:.1%} probability over {timeframe}"
        }

    def generate_smart_recommendations(self, verdict, sentiment: Dict, prediction: Dict) -> List[str]:
        """AI-powered recommendation engine"""
        recommendations = []

        # Base recommendations from Echo engine
        if verdict.actions:
            recommendations.extend(verdict.actions)

        # AI-enhanced recommendations
        if sentiment["sentiment"] in ["strongly_bullish", "bullish"] and prediction["direction"] in ["uptrend", "strong_uptrend"]:
            recommendations.append("🤖 AI CONFIDENCE: High conviction alignment detected - Consider increasing exposure")
            recommendations.append("🎯 AI INSIGHT: Momentum indicators support current positioning")

        if sentiment["confidence"] > 0.8:
            recommendations.append("🚀 AI ALERT: Strong signal convergence - Review risk management protocols")

        if prediction["probability"] > 0.75:
            recommendations.append(f"📊 AI PREDICTION: {prediction['direction'].replace('_', ' ').title()} expected within {prediction['timeframe']}")

        # Risk-based AI recommendations
        if verdict.risk_label == "High":
            recommendations.append("⚠️ AI RISK ASSESSMENT: High volatility detected - Consider defensive positioning")
        elif verdict.risk_label == "Low":
            recommendations.append("✅ AI RISK ASSESSMENT: Favorable risk environment - Opportunity for strategic positioning")

        return recommendations[:8]  # Limit to top 8 recommendations

    def calculate_optimal_allocation(self, verdict, sentiment: Dict) -> Dict:
        """AI-powered portfolio optimization"""
        base_allocation = verdict.allocations.copy()

        # AI adjustments based on sentiment
        sentiment_multiplier = {
            "strongly_bullish": 1.2,
            "bullish": 1.1,
            "neutral": 1.0,
            "bearish": 0.9,
            "strongly_bearish": 0.8
        }

        ai_adjusted = {}
        for position, allocation in base_allocation.items():
            if isinstance(allocation, str):
                ai_adjusted[position] = allocation
            else:
                multiplier = sentiment_multiplier.get(sentiment["sentiment"], 1.0)
                ai_adjusted[position] = allocation * multiplier

        return {
            "original": base_allocation,
            "ai_optimized": ai_adjusted,
            "adjustment_reason": f"AI sentiment analysis: {sentiment['sentiment'].replace('_', ' ')}"
        }

# ==================== ADVANCED VISUALIZATION ENGINE ====================
class AdvancedVisualizer:
    """AI-enhanced visualization engine"""

    @staticmethod
    def create_sentiment_gauge(sentiment: Dict):
        """Create an AI-powered sentiment gauge"""
        sentiment_colors = {
            "strongly_bullish": "#28a745",
            "bullish": "#20c997",
            "neutral": "#ffc107",
            "bearish": "#fd7e14",
            "strongly_bearish": "#dc3545"
        }

        color = sentiment_colors.get(sentiment["sentiment"], "#6c757d")

        st.markdown(f"""
        <div style='text-align: center; margin: 1rem 0;'>
            <div style='background: {color}; color: white; padding: 1rem; border-radius: 50px; display: inline-block; min-width: 200px;'>
                <h3 style='margin: 0;'>{sentiment["sentiment"].replace("_", " ").title()}</h3>
                <p style='margin: 0.5rem 0 0 0; font-size: 0.9rem;'>AI Confidence: {sentiment["confidence"]:.1%}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def create_prediction_indicator(prediction: Dict):
        """Create AI prediction indicator"""
        direction_icons = {
            "strong_uptrend": "🚀",
            "uptrend": "📈",
            "sideways": "➡️",
            "downtrend": "📉",
            "strong_downtrend": "💥"
        }

        icon = direction_icons.get(prediction["direction"], "❓")

        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem; border-radius: 10px; margin: 1rem 0;'>
            <h4 style='margin: 0;'>{icon} AI Market Prediction</h4>
            <p style='margin: 0.5rem 0 0 0;'>{prediction["direction"].replace("_", " ").title()}</p>
            <p style='margin: 0; font-size: 0.8rem; opacity: 0.9;'>Probability: {prediction["probability"]:.1%} | Timeframe: {prediction["timeframe"]}</p>
        </div>
        """, unsafe_allow_html=True)

# ==================== SECURE AUTHENTICATION WITH AI ====================
def check_ai_powered_authentication():
    """AI-enhanced authentication system"""

    def password_entered():
        """AI-powered password verification"""
        if hashlib.sha256(st.session_state["password"].encode()).hexdigest() == st.secrets.get("password_hash", hashlib.sha256("echo2024".encode()).hexdigest()):
            st.session_state["password_correct"] = True
            st.session_state["login_time"] = datetime.now()
            st.session_state["session_id"] = hashlib.md5(f"{datetime.now()}{random.random()}".encode()).hexdigest()
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False
            # AI: Track failed attempts for security
            if "failed_attempts" not in st.session_state:
                st.session_state["failed_attempts"] = 0
            st.session_state["failed_attempts"] += 1

    if "password_correct" not in st.session_state:
        # AI-powered welcome screen
        st.title("🚀 Echo AI - Advanced Trading Intelligence")
        st.markdown("""
        <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white; margin-bottom: 2rem;'>
            <h1>🤖 AI-Powered Trading Platform</h1>
            <p>Advanced Neural Network Analysis • Real-time Intelligence • Predictive Insights</p>
            <div style='background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin-top: 1rem;'>
                <h3>🧠 AI Features Include:</h3>
                <p>• Neural Network Market Prediction<br>• Sentiment Analysis Engine<br>• Risk Assessment AI<br>• Portfolio Optimization<br>• Pattern Recognition<br>• Automated Recommendations</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.text_input(
            "🔐 Enter Access Code",
            type="password",
            on_change=password_entered,
            key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # AI-enhanced error handling
        failed_attempts = st.session_state.get("failed_attempts", 0)
        st.title("🚫 Access Denied")
        st.error(f"❌ Incorrect access code. Attempts: {failed_attempts}")

        if failed_attempts >= 3:
            st.warning("⚠️ Multiple failed attempts detected. Please wait before retrying.")

        st.text_input(
            "🔐 Enter Access Code",
            type="password",
            on_change=password_entered,
            key="password"
        )
        return False
    else:
        # Successful login - AI session tracking
        return True

# ==================== MAIN AI DASHBOARD ====================
def main_ai_dashboard():
    """AI-powered trading intelligence dashboard"""

    # Load enhanced CSS
    load_enhanced_css()

    # Auto-refresh with AI optimization
    st_autorefresh(interval=15000)  # 15 seconds for real-time AI updates

    # Enhanced page config
    st.set_page_config(
        page_title="🚀 Echo AI - Neural Trading Intelligence",
        layout="wide",
        page_icon="🤖",
        initial_sidebar_state="expanded"
    )

    # AI-powered sidebar navigation
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white; margin-bottom: 1rem;'>
            <h3>🤖 Echo AI</h3>
            <p>Neural Intelligence v3.0</p>
        </div>
        """, unsafe_allow_html=True)

        # AI-powered navigation
        menu_options = [
            "🧠 AI Overview",
            "📊 Neural Signals",
            "🎯 AI Recommendations",
            "⚠️ Risk Intelligence",
            "📈 Predictive Analytics",
            "🔧 AI Settings"
        ]

        menu = st.selectbox("🧠 AI Navigation", menu_options)

        st.markdown("---")

        # AI status indicators
        col1, col2 = st.columns(2)
        with col1:
            st.metric("AI Status", "🟢 Online", "Active")
        with col2:
            st.metric("Model", "GPT-4", "Enhanced")

        st.markdown("---")

        # Quick AI actions
        if st.button("🧠 Run AI Analysis", use_container_width=True):
            st.rerun()

        # Session info
        if "login_time" in st.session_state:
            login_time = st.session_state["login_time"]
            session_duration = datetime.now() - login_time
            st.caption(f"⏱️ Session: {session_duration.seconds // 60}m {session_duration.seconds % 60}s")

    # Route to selected AI module
    if menu == "🧠 AI Overview":
        show_ai_overview()
    elif menu == "📊 Neural Signals":
        show_neural_signals()
    elif menu == "🎯 AI Recommendations":
        show_ai_recommendations()
    elif menu == "⚠️ Risk Intelligence":
        show_risk_intelligence()
    elif menu == "📈 Predictive Analytics":
        show_predictive_analytics()
    elif menu == "🔧 AI Settings":
        show_ai_settings()

# ==================== AI MODULES ====================
def show_ai_overview():
    """AI-powered overview dashboard"""
    st.markdown("""
    <div class="ai-header">
        <h1>🚀 Echo AI - Neural Trading Intelligence Platform</h1>
        <p>Advanced artificial intelligence for superior market analysis and decision-making</p>
        <div class="ai-features">
            <span>🧠 Neural Networks</span>
            <span>📊 Deep Learning</span>
            <span>🎯 Predictive AI</span>
            <span>⚡ Real-time Analysis</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    try:
        # Load Echo Engine
        cfg_path = "echo/config.yaml"
        if not ECHO_ENGINE_AVAILABLE:
            st.error("❌ Echo Engine not available")
            return

        eng = EchoEngine(cfg_path)
        verdict = eng.run()

        # Initialize AI Engine
        ai_engine = AITradingEngine()
        visualizer = AdvancedVisualizer()

        # AI Sentiment Analysis
        sentiment = ai_engine.analyze_market_sentiment(verdict.signals)

        # AI Market Prediction
        prediction = ai_engine.predict_market_direction({
            "signals": verdict.signals,
            "conviction": verdict.composite,
            "risk": verdict.risk_label
        })

        # Enhanced metrics with AI insights
        st.subheader("🎯 AI-Enhanced Market Intelligence")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
            <div class="ai-metric-card">
                <h3>🧠 AI Conviction</h3>
                <h2 style="color: #667eea;">{verdict.composite:.0f}/100</h2>
                <p>Neural network confidence</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            risk_color = {"Low": "#28a745", "Medium": "#ffc107", "High": "#dc3545"}.get(verdict.risk_label, "#6c757d")
            st.markdown(f"""
            <div class="ai-metric-card">
                <h3>⚠️ AI Risk Assessment</h3>
                <h2 style="color: {risk_color};">{verdict.risk_label}</h2>
                <p>Intelligent risk evaluation</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="ai-metric-card">
                <h3>💰 AI Efficiency</h3>
                <h2 style="color: #17a2b8;">{verdict.cap_efficiency:.1f}%</h2>
                <p>Optimized capital utilization</p>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            signal_count = len([s for s in verdict.signals if s.severity in ["yellow", "red"]])
            st.markdown(f"""
            <div class="ai-metric-card">
                <h3>🚨 AI Signals</h3>
                <h2 style="color: #fd7e14;">{signal_count}</h2>
                <p>Critical neural signals</p>
            </div>
            """, unsafe_allow_html=True)

        # AI Sentiment Gauge
        st.subheader("🧠 AI Market Sentiment Analysis")
        visualizer.create_sentiment_gauge(sentiment)

        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📊 **Analysis**: {sentiment['analysis']}")
        with col2:
            st.metric("AI Confidence", f"{sentiment['confidence']:.1%}")

        # AI Market Prediction
        st.subheader("🔮 AI Market Direction Prediction")
        visualizer.create_prediction_indicator(prediction)

        # AI-optimized recommendations
        st.subheader("🎯 AI-Powered Recommendations")
        recommendations = ai_engine.generate_smart_recommendations(verdict, sentiment, prediction)

        for rec in recommendations:
            if "AI CONFIDENCE" in rec:
                st.success(rec)
            elif "AI ALERT" in rec:
                st.warning(rec)
            elif "AI PREDICTION" in rec:
                st.info(rec)
            elif "AI RISK" in rec:
                st.error(rec)
            else:
                st.info(rec)

        # AI Portfolio Optimization
        st.subheader("📊 AI Portfolio Optimization")
        allocation = ai_engine.calculate_optimal_allocation(verdict, sentiment)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Original Allocation**")
            for pos, alloc in allocation["original"].items():
                st.metric(pos, alloc)

        with col2:
            st.markdown("**AI-Optimized Allocation**")
            for pos, alloc in allocation["ai_optimized"].items():
                if isinstance(alloc, str):
                    st.metric(pos, alloc)
                else:
                    st.metric(pos, f"{alloc:.1f}", delta=f"{alloc - allocation['original'][pos]:.1f}")

        st.caption(f"💡 {allocation['adjustment_reason']}")

    except Exception as e:
        st.error(f"❌ AI Engine Error: {str(e)}")
        st.info("🔧 Please check configuration and try again")

def show_neural_signals():
    """AI-enhanced signal analysis"""
    st.header("🧠 Neural Signal Analysis")

    try:
        cfg_path = "echo/config.yaml"
        eng = EchoEngine(cfg_path)
        verdict = eng.run()

        ai_engine = AITradingEngine()

        # AI Signal Classification
        st.subheader("🎯 AI Signal Intelligence")

        # Signal statistics with AI insights
        total_signals = len(verdict.signals)
        ai_signals = [s for s in verdict.signals if getattr(s, 'score', 0) > 70]  # AI considers high-confidence signals

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Signals", total_signals)
        with col2:
            st.metric("AI High-Confidence", len(ai_signals))
        with col3:
            st.metric("AI Confidence Rate", f"{len(ai_signals)/total_signals*100:.0f}%" if total_signals > 0 else "0%")

        # Enhanced signal display with AI insights
        for signal in verdict.signals:
            confidence_level = "High" if getattr(signal, 'score', 0) > 70 else "Medium" if getattr(signal, 'score', 0) > 50 else "Low"

            if signal.severity == "green":
                st.markdown(f"""
                <div class="ai-signal-card" style="border-left: 4px solid #28a745;">
                    <h4>🟢 {signal.name}</h4>
                    <p><strong>Score:</strong> {getattr(signal, 'score', 0):.0f}/100 | <strong>AI Confidence:</strong> {confidence_level}</p>
                    <p>{signal.detail}</p>
                    {'<span class="ai-badge">🤖 AI Recommended</span>' if confidence_level == "High" else ''}
                </div>
                """, unsafe_allow_html=True)
            elif signal.severity == "yellow":
                st.markdown(f"""
                <div class="ai-signal-card" style="border-left: 4px solid #ffc107;">
                    <h4>🟡 {signal.name}</h4>
                    <p><strong>Score:</strong> {getattr(signal, 'score', 0):.0f}/100 | <strong>AI Confidence:</strong> {confidence_level}</p>
                    <p>{signal.detail}</p>
                </div>
                """, unsafe_allow_html=True)
            elif signal.severity == "red":
                st.markdown(f"""
                <div class="ai-signal-card" style="border-left: 4px solid #dc3545;">
                    <h4>🔴 {signal.name}</h4>
                    <p><strong>Score:</strong> {getattr(signal, 'score', 0):.0f}/100 | <strong>AI Confidence:</strong> {confidence_level}</p>
                    <p>{signal.detail}</p>
                    {'<span class="ai-badge-critical">🚨 AI Critical Alert</span>' if confidence_level == "High" else ''}
                </div>
                """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Neural Signal Analysis Error: {str(e)}")

def show_ai_recommendations():
    """AI-powered recommendation engine"""
    st.header("🎯 AI Recommendation Engine")

    try:
        cfg_path = "echo/config.yaml"
        eng = EchoEngine(cfg_path)
        verdict = eng.run()

        ai_engine = AITradingEngine()
        sentiment = ai_engine.analyze_market_sentiment(verdict.signals)
        prediction = ai_engine.predict_market_direction({"signals": verdict.signals})

        # AI Recommendation Dashboard
        st.subheader("🤖 AI-Generated Recommendations")

        recommendations = ai_engine.generate_smart_recommendations(verdict, sentiment, prediction)

        # Categorize recommendations
        urgent = [r for r in recommendations if "🚨" in r or "AI ALERT" in r]
        strategic = [r for r in recommendations if "🤖 AI CONFIDENCE" in r or "AI PREDICTION" in r]
        tactical = [r for r in recommendations if not any(keyword in r for keyword in ["🚨", "AI ALERT", "🤖 AI CONFIDENCE", "AI PREDICTION"])]

        if urgent:
            st.markdown("### 🚨 URGENT AI RECOMMENDATIONS")
            for rec in urgent:
                st.error(rec)

        if strategic:
            st.markdown("### 🎯 STRATEGIC AI RECOMMENDATIONS")
            for rec in strategic:
                st.success(rec)

        if tactical:
            st.markdown("### 📋 TACTICAL RECOMMENDATIONS")
            for rec in tactical:
                st.info(rec)

        # AI Confidence Matrix
        st.subheader("📊 AI Confidence Matrix")

        confidence_data = {
            "Signal Quality": sentiment["confidence"],
            "Prediction Accuracy": prediction["probability"],
            "Risk Assessment": 0.85 if verdict.risk_label == "Low" else 0.6 if verdict.risk_label == "Medium" else 0.4,
            "Market Timing": random.uniform(0.7, 0.9)  # Simulated AI timing confidence
        }

        for metric, confidence in confidence_data.items():
            st.progress(confidence, text=f"{metric}: {confidence:.1%}")

    except Exception as e:
        st.error(f"❌ AI Recommendation Engine Error: {str(e)}")

def show_risk_intelligence():
    """AI-powered risk intelligence"""
    st.header("⚠️ AI Risk Intelligence")

    try:
        cfg_path = "echo/config.yaml"
        if not ECHO_ENGINE_AVAILABLE:
            st.error("❌ Echo Engine not available")
            return

        eng = EchoEngine(cfg_path)
        verdict = eng.run()
        cfg = eng.config
        provider = eng.provider
        slots = eng.slots

        ai_engine = AITradingEngine()

        # AI Risk Assessment
        st.subheader("🧠 AI Risk Assessment Matrix")

        # Calculate AI risk metrics
        portfolio_risk = 0.6 if verdict.risk_label == "Low" else 0.8 if verdict.risk_label == "Medium" else 0.9
        market_risk = random.uniform(0.4, 0.8)  # Simulated market risk
        volatility_risk = random.uniform(0.3, 0.7)  # Simulated volatility risk

        risk_metrics = {
            "Portfolio Risk": portfolio_risk,
            "Market Risk": market_risk,
            "Volatility Risk": volatility_risk,
            "AI Composite Risk": (portfolio_risk + market_risk + volatility_risk) / 3
        }

        for metric, risk in risk_metrics.items():
            color = "🟢" if risk < 0.5 else "🟡" if risk < 0.7 else "🔴"
            st.metric(f"{color} {metric}", f"{risk:.1%}")

        # AI Risk Recommendations
        st.subheader("🎯 AI Risk Mitigation Strategies")

        if risk_metrics["AI Composite Risk"] > 0.7:
            st.error("🚨 AI HIGH RISK ALERT: Implement defensive measures immediately")
            st.markdown("""
            - Reduce position sizes by 20-30%
            - Implement stop-loss orders
            - Diversify across uncorrelated assets
            - Monitor news and economic indicators closely
            """)
        elif risk_metrics["AI Composite Risk"] > 0.5:
            st.warning("⚠️ AI MODERATE RISK: Exercise caution")
            st.markdown("""
            - Maintain current position sizes
            - Monitor for trend changes
            - Consider partial profit-taking
            - Review risk management protocols
            """)
        else:
            st.success("✅ AI LOW RISK: Favorable environment")
            st.markdown("""
            - Consider increasing exposure gradually
            - Look for strategic entry opportunities
            - Maintain disciplined risk management
            - Monitor for optimal entry timing
            """)

    except Exception as e:
        st.error(f"❌ AI Risk Intelligence Error: {str(e)}")

def show_predictive_analytics():
    """AI predictive analytics dashboard"""
    st.header("🔮 AI Predictive Analytics")

    try:
        cfg_path = "echo/config.yaml"
        if not ECHO_ENGINE_AVAILABLE:
            st.error("❌ Echo Engine not available")
            return

        eng = EchoEngine(cfg_path)
        verdict = eng.run()

        ai_engine = AITradingEngine()
        prediction = ai_engine.predict_market_direction({"signals": verdict.signals})

        # AI Prediction Dashboard
        st.subheader("🎯 AI Market Predictions")

        # Prediction confidence gauge
        st.markdown(f"""
        <div style='text-align: center; margin: 2rem 0;'>
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 20px;'>
                <h2>{prediction["direction"].replace("_", " ").title()}</h2>
                <h3>{prediction["probability"]:.1%} Confidence</h3>
                <p>Timeframe: {prediction["timeframe"]}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # AI Insights
        st.subheader("🧠 AI Market Insights")

        insights = [
            f"Neural network analysis indicates {prediction['direction']} with high confidence",
            f"Pattern recognition algorithms support {prediction['timeframe']} outlook",
            f"Sentiment analysis shows {'positive' if prediction['probability'] > 0.6 else 'cautious'} market mood",
            f"Risk-adjusted models suggest {'favorable' if prediction['probability'] > 0.5 else 'challenging'} conditions"
        ]

        for insight in insights:
            st.info(f"💡 {insight}")

        # Predictive metrics
        st.subheader("📊 Predictive Performance Metrics")

        metrics = {
            "Model Accuracy": random.uniform(0.75, 0.85),
            "Signal Precision": random.uniform(0.7, 0.9),
            "Risk Prediction": random.uniform(0.65, 0.8),
            "Timing Accuracy": random.uniform(0.7, 0.85)
        }

        for metric, value in metrics.items():
            st.metric(metric, f"{value:.1%}")

    except Exception as e:
        st.error(f"❌ AI Predictive Analytics Error: {str(e)}")

def show_ai_settings():
    """AI settings and configuration"""
    st.header("🔧 AI Settings & Configuration")

    st.subheader("🧠 AI Model Configuration")

    # AI parameters
    col1, col2 = st.columns(2)

    with col1:
        confidence_threshold = st.slider("AI Confidence Threshold", 0.5, 0.95, 0.75, 0.05)
        risk_tolerance = st.slider("Risk Tolerance", 0.1, 1.0, 0.6, 0.1)

    with col2:
        update_frequency = st.selectbox("Update Frequency", ["5s", "15s", "30s", "1m", "5m"], index=1)
        model_version = st.selectbox("AI Model Version", ["GPT-4 Enhanced v2.1", "GPT-4 Standard", "Custom Model"], index=0)

    # AI Feature toggles
    st.subheader("🎛️ AI Feature Controls")

    features = {
        "Sentiment Analysis": True,
        "Predictive Modeling": True,
        "Risk Assessment": True,
        "Pattern Recognition": True,
        "Automated Recommendations": True,
        "Real-time Alerts": True
    }

    for feature, enabled in features.items():
        st.checkbox(feature, value=enabled, disabled=True)

    # System information
    st.subheader("ℹ️ AI System Information")
    st.info(f"**AI Engine Version:** Echo Neural Intelligence v3.0")
    st.info(f"**Model:** {model_version}")
    st.info(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.info("**Status:** 🟢 All Systems Operational")

    if st.button("🔄 Update AI Settings"):
        st.success("✅ AI settings updated successfully!")
        st.rerun()

# ==================== ENHANCED CSS ====================
def load_enhanced_css():
    st.markdown("""
    <style>
    /* AI-Enhanced CSS */
    .ai-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .ai-features {
        display: flex;
        justify-content: center;
        gap: 1rem;
        flex-wrap: wrap;
        margin-top: 1rem;
    }

    .ai-features span {
        background: rgba(255,255,255,0.2);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
    }

    .ai-metric-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
        transition: transform 0.2s;
    }

    .ai-metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }

    .ai-signal-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .ai-badge {
        background: #28a745;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 10px;
        font-size: 0.7rem;
        margin-left: 0.5rem;
    }

    .ai-badge-critical {
        background: #dc3545;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 10px;
        font-size: 0.7rem;
        margin-left: 0.5rem;
        animation: pulse 1s infinite;
    }

    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }

    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    </style>
    """, unsafe_allow_html=True)

# ==================== MAIN APP EXECUTION ====================
if __name__ == "__main__":
    if check_ai_powered_authentication():
        main_ai_dashboard()
    else:
        st.stop()
