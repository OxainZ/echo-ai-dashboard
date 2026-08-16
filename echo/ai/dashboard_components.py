"""
Enhanced AI Dashboard Components

Provides Streamlit UI components for displaying AI predictions,
trading recommendations, and market analysis
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Optional
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class AIDashboardUI:
    """
    UI components for AI-powered trading dashboard
    """
    
    @staticmethod
    def display_prediction_card(prediction, ticker: str, current_price: float):
        """
        Display AI prediction in a card format
        
        Args:
            prediction: PredictionResult object
            ticker: Stock ticker
            current_price: Current stock price
        """
        # Determine colors based on direction
        direction_colors = {
            "bullish": "#28a745",
            "bearish": "#dc3545",
            "neutral": "#ffc107"
        }
        
        direction_icons = {
            "bullish": "📈",
            "bearish": "📉",
            "neutral": "➡️"
        }
        
        color = direction_colors.get(prediction.direction, "#6c757d")
        icon = direction_icons.get(prediction.direction, "❓")
        
        predicted_change = ((prediction.predicted_price - current_price) / current_price) * 100
        
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, {color}15 0%, {color}05 100%); 
                    border-left: 4px solid {color}; 
                    border-radius: 10px; 
                    padding: 1.5rem; 
                    margin: 1rem 0;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <h3 style='margin: 0 0 1rem 0; color: {color};'>{icon} {ticker} AI Prediction</h3>
            <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;'>
                <div>
                    <p style='margin: 0; font-size: 0.9rem; opacity: 0.8;'>Current Price</p>
                    <h4 style='margin: 0.2rem 0;'>${current_price:.2f}</h4>
                </div>
                <div>
                    <p style='margin: 0; font-size: 0.9rem; opacity: 0.8;'>Predicted Price</p>
                    <h4 style='margin: 0.2rem 0; color: {color};'>${prediction.predicted_price:.2f}</h4>
                </div>
                <div>
                    <p style='margin: 0; font-size: 0.9rem; opacity: 0.8;'>Expected Change</p>
                    <h4 style='margin: 0.2rem 0; color: {color};'>{predicted_change:+.2f}%</h4>
                </div>
                <div>
                    <p style='margin: 0; font-size: 0.9rem; opacity: 0.8;'>AI Confidence</p>
                    <h4 style='margin: 0.2rem 0;'>{prediction.confidence:.1%}</h4>
                </div>
            </div>
            <div style='margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(0,0,0,0.1);'>
                <p style='margin: 0; font-size: 0.85rem;'><strong>Timeframe:</strong> {prediction.timeframe_days} days</p>
                <p style='margin: 0.3rem 0; font-size: 0.85rem;'><strong>Risk Level:</strong> {prediction.risk_level.title()}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display supporting factors
        if prediction.supporting_factors:
            with st.expander("📊 View AI Analysis Factors"):
                for factor in prediction.supporting_factors:
                    st.markdown(f"✓ {factor}")
    
    @staticmethod
    def display_trading_decision(decision: Dict, ticker: str):
        """
        Display AI trading decision
        
        Args:
            decision: Decision dict from TradingDecisionEngine
            ticker: Stock ticker
        """
        action_colors = {
            "BUY": "#28a745",
            "SELL": "#dc3545",
            "HOLD": "#ffc107"
        }
        
        action_icons = {
            "BUY": "🟢",
            "SELL": "🔴",
            "HOLD": "🟡"
        }
        
        color = action_colors.get(decision["action"], "#6c757d")
        icon = action_icons.get(decision["action"], "⚪")
        
        st.markdown(f"""
        <div style='background: {color}; 
                    color: white; 
                    border-radius: 10px; 
                    padding: 1.5rem; 
                    margin: 1rem 0;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <h2 style='margin: 0 0 1rem 0;'>{icon} {decision["action"]} {ticker}</h2>
            <div style='background: rgba(255,255,255,0.1); 
                        border-radius: 8px; 
                        padding: 1rem;'>
                <p style='margin: 0.5rem 0;'><strong>Confidence:</strong> {decision["confidence"]:.1%}</p>
                <p style='margin: 0.5rem 0;'><strong>Risk Level:</strong> {decision["risk_level"].title()}</p>
                {f"<p style='margin: 0.5rem 0;'><strong>Position Size:</strong> ${decision['position_size']:.2f}</p>" if decision["position_size"] > 0 else ""}
                {f"<p style='margin: 0.5rem 0;'><strong>Stop Loss:</strong> ${decision['stop_loss']:.2f}</p>" if decision["action"] != "HOLD" else ""}
                {f"<p style='margin: 0.5rem 0;'><strong>Take Profit:</strong> ${decision['take_profit']:.2f}</p>" if decision["action"] != "HOLD" else ""}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display reasoning
        with st.expander("🤔 View AI Reasoning"):
            for reason in decision["reasoning"]:
                st.write(reason)
    
    @staticmethod
    def display_sentiment_gauge(sentiment: Dict):
        """
        Display market sentiment gauge
        
        Args:
            sentiment: Sentiment analysis dict
        """
        sentiment_colors = {
            "bullish": "#28a745",
            "bearish": "#dc3545",
            "neutral": "#ffc107"
        }
        
        color = sentiment_colors.get(sentiment["sentiment"], "#6c757d")

        # Directional gauge: 0 = strongly bearish, 50 = neutral, 100 = strongly
        # bullish, matching the red/yellow/green bands. (Previously the gauge
        # plotted raw strength, so a STRONG BEARISH reading rendered at 80 —
        # deep inside the green band.)
        strength = float(sentiment.get("strength", 0.5))
        label = str(sentiment.get("sentiment", "neutral"))
        if "bullish" in label:
            gauge_value = 50 + strength * 50
        elif "bearish" in label:
            gauge_value = 50 - strength * 50
        else:
            gauge_value = 50.0

        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=gauge_value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"Market Sentiment: {label.title()} (0 = bearish, 100 = bullish)"},
            delta={'reference': 50},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 33], 'color': "#f8d7da"},
                    {'range': [33, 66], 'color': "#fff3cd"},
                    {'range': [66, 100], 'color': "#d4edda"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': gauge_value
                }
            }
        ))
        
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)
        
        st.info(f"📊 {sentiment['analysis']}")
    
    @staticmethod
    def display_technical_chart(df: pd.DataFrame, ticker: str, 
                                prediction=None):
        """
        Display technical analysis chart with AI prediction
        
        Args:
            df: DataFrame with OHLCV and technical indicators
            ticker: Stock ticker
            prediction: Optional PredictionResult to overlay
        """
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.6, 0.2, 0.2],
            subplot_titles=(f'{ticker} Price & Indicators', 'Volume', 'RSI')
        )
        
        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Price'
            ),
            row=1, col=1
        )
        
        # Add moving averages if available
        if 'SMA_20' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['SMA_20'],
                    name='SMA 20',
                    line=dict(color='orange', width=1)
                ),
                row=1, col=1
            )
        
        if 'BB_Upper' in df.columns and 'BB_Lower' in df.columns:
            # Bollinger Bands
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['BB_Upper'],
                    name='BB Upper',
                    line=dict(color='gray', width=1, dash='dash'),
                    showlegend=False
                ),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['BB_Lower'],
                    name='BB Lower',
                    line=dict(color='gray', width=1, dash='dash'),
                    fill='tonexty',
                    showlegend=False
                ),
                row=1, col=1
            )
        
        # Add prediction marker if available
        if prediction:
            last_date = df.index[-1]
            fig.add_trace(
                go.Scatter(
                    x=[last_date],
                    y=[prediction.predicted_price],
                    mode='markers',
                    name='AI Prediction',
                    marker=dict(
                        size=15,
                        color='purple',
                        symbol='star',
                        line=dict(color='white', width=2)
                    )
                ),
                row=1, col=1
            )
        
        # Volume
        colors = ['red' if df['Close'].iloc[i] < df['Open'].iloc[i] 
                 else 'green' for i in range(len(df))]
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['Volume'],
                name='Volume',
                marker_color=colors
            ),
            row=2, col=1
        )
        
        # RSI if available
        if 'RSI' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['RSI'],
                    name='RSI',
                    line=dict(color='blue', width=2)
                ),
                row=3, col=1
            )
            
            # Add RSI reference lines
            fig.add_hline(y=70, line_dash="dash", line_color="red", 
                         opacity=0.5, row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", 
                         opacity=0.5, row=3, col=1)
        
        # Update layout
        fig.update_layout(
            height=800,
            xaxis_rangeslider_visible=False,
            showlegend=True,
            hovermode='x unified'
        )
        
        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        fig.update_yaxes(title_text="RSI", row=3, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def display_risk_metrics(decision: Dict):
        """
        Display risk metrics and management info
        
        Args:
            decision: Trading decision dict
        """
        st.subheader("⚠️ Risk Management")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            risk_color = {
                "low": "#28a745",
                "medium": "#ffc107",
                "high": "#dc3545"
            }.get(decision["risk_level"], "#6c757d")
            
            st.markdown(f"""
            <div style='text-align: center; padding: 1rem; background: {risk_color}20; 
                        border-radius: 10px; border: 2px solid {risk_color};'>
                <h4 style='margin: 0; color: {risk_color};'>Risk Level</h4>
                <h2 style='margin: 0.5rem 0; color: {risk_color};'>{decision["risk_level"].upper()}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if decision["action"] != "HOLD" and decision["position_size"] > 0:
                st.metric("Position Size", f"${decision['position_size']:.2f}")
            else:
                st.metric("Position Size", "N/A")
        
        with col3:
            st.metric("Confidence", f"{decision['confidence']:.1%}")
        
        # Risk parameters
        if decision["action"] != "HOLD":
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🛑 Stop Loss**")
                st.write(f"${decision['stop_loss']:.2f}")
                
            with col2:
                st.markdown("**🎯 Take Profit**")
                st.write(f"${decision['take_profit']:.2f}")
    
    @staticmethod
    def display_disclaimer():
        """Display important investment disclaimers"""
        with st.expander("⚠️ IMPORTANT: Investment Disclaimer", expanded=False):
            st.warning("""
            **INVESTMENT DISCLAIMER**
            
            This AI-powered trading dashboard is for **informational and educational purposes only**. 
            It does NOT constitute financial advice, investment advice, or any other type of professional advice.
            
            **Key Points:**
            - ❌ AI predictions are NOT guaranteed and may be incorrect
            - ❌ Past performance does NOT indicate future results  
            - ❌ Trading involves substantial risk of loss
            - ❌ You may lose all invested capital
            - ✅ Always do your own research before investing
            - ✅ Consult a licensed financial advisor for personalized advice
            
            **By using this dashboard, you acknowledge these risks and accept full responsibility 
            for your trading decisions.**
            """)
            
            st.info("""
            **DATA DISCLAIMER**
            
            All market data is sourced from publicly available APIs. Data is provided "as is" 
            without warranties. Real-time data may have delays.
            """)
            
            st.info("""
            **AI MODEL DISCLAIMER**
            
            AI models are based on historical patterns and technical analysis. They are NOT 
            guaranteed to predict future market movements and should be ONE of many factors 
            in your decision-making process.
            """)
    
    @staticmethod
    def display_model_info():
        """Display AI model information"""
        with st.expander("🤖 AI Model Information"):
            st.markdown("""
            **Model Architecture:**
            - Technical Indicator Analysis
            - Momentum & Trend Detection
            - Pattern Recognition
            - Risk Assessment Algorithms
            
            **Features Used:**
            - Price action and trends
            - Volume analysis
            - RSI, MACD, Bollinger Bands
            - Moving averages
            - Volatility metrics
            
            **Prediction Methodology:**
            - Multi-factor analysis
            - Confidence scoring
            - Risk-adjusted recommendations
            - Real-time data processing
            
            **Model Version:** v1.0-lightweight  
            **Last Updated:** 2024
            
            *Note: This is a lightweight implementation. For production use, 
            consider implementing deep learning models (LSTM/Transformer).*
            """)
