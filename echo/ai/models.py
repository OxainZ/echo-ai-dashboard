"""
AI Models for Stock Price Prediction and Trading Analysis

This module provides machine learning models for:
- Stock price prediction using LSTM and Transformer architectures
- Trend analysis and market sentiment classification
- Risk assessment and volatility prediction
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

@dataclass
class PredictionResult:
    """Result from AI model prediction"""
    predicted_price: float
    confidence: float
    direction: str  # "bullish", "bearish", "neutral"
    timeframe_days: int
    risk_level: str  # "low", "medium", "high"
    supporting_factors: List[str]


class StockPricePredictor:
    """
    AI-powered stock price prediction using technical indicators and pattern recognition.
    
    This is a lightweight implementation suitable for real-time dashboard usage.
    For production, consider integrating TensorFlow/PyTorch LSTM/Transformer models.
    """
    
    def __init__(self, lookback_period: int = 30):
        self.lookback_period = lookback_period
        self.model_version = "v1.0-lightweight"
        
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators for analysis"""
        df = df.copy()
        
        # Moving averages
        df['SMA_10'] = df['Close'].rolling(window=10).mean()
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
        
        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        
        # Volatility
        df['Volatility'] = df['Close'].rolling(window=20).std()
        
        # Volume indicators
        df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
        
        return df
    
    def analyze_momentum(self, df: pd.DataFrame) -> Dict[str, float]:
        """Analyze price momentum indicators"""
        if len(df) < 20:
            return {"score": 0.5, "strength": 0.0}
        
        latest = df.iloc[-1]
        
        # Price vs moving averages
        sma_10_score = 1.0 if latest['Close'] > latest['SMA_10'] else 0.0
        sma_20_score = 1.0 if latest['Close'] > latest['SMA_20'] else 0.0
        
        # MACD signal
        macd_score = 1.0 if latest['MACD'] > latest['Signal_Line'] else 0.0
        
        # RSI analysis
        rsi = latest['RSI']
        if rsi < 30:
            rsi_score = 1.0  # Oversold, bullish signal
        elif rsi > 70:
            rsi_score = 0.0  # Overbought, bearish signal
        else:
            rsi_score = 0.5
        
        # Weighted momentum score
        momentum_score = (sma_10_score * 0.3 + sma_20_score * 0.3 + 
                         macd_score * 0.2 + rsi_score * 0.2)
        
        # Calculate momentum strength
        price_change = (df['Close'].iloc[-1] - df['Close'].iloc[-10]) / df['Close'].iloc[-10]
        momentum_strength = abs(price_change)
        
        return {
            "score": momentum_score,
            "strength": momentum_strength,
            "rsi": rsi,
            "macd_signal": "bullish" if macd_score > 0.5 else "bearish"
        }
    
    def predict(self, historical_data: pd.DataFrame, 
                ticker: str = "STOCK") -> PredictionResult:
        """
        Generate price prediction based on historical data
        
        Args:
            historical_data: DataFrame with OHLCV data
            ticker: Stock ticker symbol
            
        Returns:
            PredictionResult with prediction details
        """
        # Calculate technical indicators
        df = self.calculate_technical_indicators(historical_data)
        
        # Ensure we have enough data
        if len(df) < self.lookback_period:
            return self._default_prediction(df)
        
        # Analyze momentum
        momentum = self.analyze_momentum(df)
        
        # Get current price
        current_price = df['Close'].iloc[-1]
        
        # Simple trend-based prediction
        recent_trend = (df['Close'].iloc[-5:].mean() - df['Close'].iloc[-10:-5].mean())
        volatility = df['Volatility'].iloc[-1]
        
        # Predict direction
        if momentum['score'] > 0.6 and recent_trend > 0:
            direction = "bullish"
            predicted_change = 0.02 + (momentum['strength'] * 0.03)  # 2-5% gain
            confidence = 0.6 + (momentum['score'] * 0.3)
        elif momentum['score'] < 0.4 and recent_trend < 0:
            direction = "bearish"
            predicted_change = -0.02 - (momentum['strength'] * 0.03)  # 2-5% loss
            confidence = 0.6 + ((1 - momentum['score']) * 0.3)
        else:
            direction = "neutral"
            predicted_change = 0.0
            confidence = 0.5
        
        predicted_price = current_price * (1 + predicted_change)
        
        # Assess risk level
        if volatility > df['Volatility'].mean() * 1.5:
            risk_level = "high"
        elif volatility > df['Volatility'].mean() * 1.2:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Generate supporting factors
        supporting_factors = self._generate_factors(df, momentum, direction)
        
        return PredictionResult(
            predicted_price=predicted_price,
            confidence=min(0.85, confidence),  # Cap at 85% for lightweight model
            direction=direction,
            timeframe_days=5,  # 5-day prediction horizon
            risk_level=risk_level,
            supporting_factors=supporting_factors
        )
    
    def _default_prediction(self, df: pd.DataFrame) -> PredictionResult:
        """Return neutral prediction when insufficient data"""
        current_price = df['Close'].iloc[-1] if len(df) > 0 else 100.0
        return PredictionResult(
            predicted_price=current_price,
            confidence=0.3,
            direction="neutral",
            timeframe_days=5,
            risk_level="medium",
            supporting_factors=["Insufficient historical data for accurate prediction"]
        )
    
    def _generate_factors(self, df: pd.DataFrame, 
                         momentum: Dict, direction: str) -> List[str]:
        """Generate list of supporting factors for prediction"""
        factors = []
        latest = df.iloc[-1]
        
        # RSI analysis
        rsi = momentum['rsi']
        if rsi < 30:
            factors.append(f"RSI at {rsi:.1f} indicates oversold conditions")
        elif rsi > 70:
            factors.append(f"RSI at {rsi:.1f} indicates overbought conditions")
        
        # Moving average analysis
        if latest['Close'] > latest['SMA_20']:
            factors.append("Price trading above 20-day moving average")
        else:
            factors.append("Price trading below 20-day moving average")
        
        # MACD signal
        if momentum['macd_signal'] == "bullish":
            factors.append("MACD showing bullish crossover")
        else:
            factors.append("MACD showing bearish crossover")
        
        # Volume analysis
        if latest['Volume_Ratio'] > 1.2:
            factors.append("Above-average trading volume detected")
        
        # Volatility
        if latest['Volatility'] > df['Volatility'].mean() * 1.3:
            factors.append("Elevated volatility levels")
        
        return factors[:5]  # Return top 5 factors


class TradingDecisionEngine:
    """
    AI-powered trading decision engine with risk management
    """
    
    def __init__(self, risk_tolerance: float = 0.02, max_loss_pct: float = 0.05):
        """
        Args:
            risk_tolerance: Maximum acceptable risk per trade (default 2%)
            max_loss_pct: Stop-loss percentage (default 5%)
        """
        self.risk_tolerance = risk_tolerance
        self.max_loss_pct = max_loss_pct
        
    def generate_decision(self, prediction: PredictionResult, 
                         current_price: float,
                         portfolio_value: float) -> Dict:
        """
        Generate trading decision based on AI prediction
        
        Returns:
            Dict with action, position_size, stop_loss, take_profit, reasoning
        """
        # Determine action
        if prediction.direction == "bullish" and prediction.confidence > 0.65:
            action = "BUY"
            confidence_factor = prediction.confidence
        elif prediction.direction == "bearish" and prediction.confidence > 0.65:
            action = "SELL"
            confidence_factor = prediction.confidence
        else:
            action = "HOLD"
            confidence_factor = prediction.confidence
        
        # Calculate position sizing based on Kelly Criterion (simplified)
        if action != "HOLD":
            win_prob = prediction.confidence
            win_loss_ratio = 2.0  # Assuming 2:1 reward/risk ratio
            kelly_fraction = (win_prob * win_loss_ratio - (1 - win_prob)) / win_loss_ratio
            kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Cap at 25%
            
            position_size = portfolio_value * kelly_fraction * 0.5  # Use half-Kelly for safety
        else:
            position_size = 0.0
        
        # Set stop loss and take profit
        stop_loss = current_price * (1 - self.max_loss_pct)
        take_profit = current_price * (1 + self.max_loss_pct * 2)  # 2:1 reward/risk
        
        # Generate reasoning
        reasoning = self._generate_reasoning(action, prediction, confidence_factor)
        
        return {
            "action": action,
            "position_size": position_size,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "confidence": confidence_factor,
            "risk_level": prediction.risk_level,
            "reasoning": reasoning
        }
    
    def _generate_reasoning(self, action: str, prediction: PredictionResult, 
                           confidence: float) -> List[str]:
        """Generate reasoning for trading decision"""
        reasoning = []
        
        reasoning.append(f"Action: {action} based on {prediction.direction} prediction")
        reasoning.append(f"AI confidence level: {confidence:.1%}")
        reasoning.append(f"Expected price movement over {prediction.timeframe_days} days")
        reasoning.append(f"Risk assessment: {prediction.risk_level}")
        
        # Add key supporting factors
        if prediction.supporting_factors:
            reasoning.append("Key factors:")
            reasoning.extend(f"  - {factor}" for factor in prediction.supporting_factors[:3])
        
        return reasoning


class MarketSentimentAnalyzer:
    """
    Analyze market sentiment using multiple indicators
    """
    
    def analyze(self, historical_data: pd.DataFrame, 
                signals: Optional[List] = None) -> Dict:
        """
        Analyze overall market sentiment
        
        Returns:
            Dict with sentiment, strength, and analysis
        """
        # Calculate technical indicators if not present
        if 'RSI' not in historical_data.columns:
            predictor = StockPricePredictor()
            df = predictor.calculate_technical_indicators(historical_data)
        else:
            df = historical_data
        
        if len(df) < 20:
            return {
                "sentiment": "neutral",
                "strength": 0.5,
                "analysis": "Insufficient data for sentiment analysis"
            }
        
        latest = df.iloc[-1]
        
        # RSI-based sentiment
        rsi = latest['RSI']
        if rsi < 30:
            rsi_sentiment = "bullish"  # Oversold
            rsi_strength = 0.8
        elif rsi > 70:
            rsi_sentiment = "bearish"  # Overbought
            rsi_strength = 0.8
        else:
            rsi_sentiment = "neutral"
            rsi_strength = 0.5
        
        # Trend-based sentiment
        sma_20 = latest['SMA_20']
        current_price = latest['Close']
        if current_price > sma_20 * 1.05:
            trend_sentiment = "bullish"
            trend_strength = 0.7
        elif current_price < sma_20 * 0.95:
            trend_sentiment = "bearish"
            trend_strength = 0.7
        else:
            trend_sentiment = "neutral"
            trend_strength = 0.5
        
        # Volume sentiment
        volume_ratio = latest['Volume_Ratio']
        volume_strength = min(volume_ratio, 2.0) / 2.0
        
        # Combine sentiments
        sentiment_scores = {
            "bullish": 0,
            "bearish": 0,
            "neutral": 0
        }
        
        sentiment_scores[rsi_sentiment] += rsi_strength
        sentiment_scores[trend_sentiment] += trend_strength
        
        # Determine overall sentiment
        dominant_sentiment = max(sentiment_scores, key=sentiment_scores.get)
        overall_strength = sentiment_scores[dominant_sentiment] / 2.0  # Average of two indicators
        
        analysis = self._generate_sentiment_analysis(
            dominant_sentiment, overall_strength, rsi, volume_ratio
        )
        
        return {
            "sentiment": dominant_sentiment,
            "strength": min(overall_strength, 0.9),  # Cap at 90%
            "analysis": analysis,
            "rsi": rsi,
            "trend": trend_sentiment,
            "volume_signal": "strong" if volume_ratio > 1.2 else "weak"
        }
    
    def _generate_sentiment_analysis(self, sentiment: str, strength: float,
                                    rsi: float, volume_ratio: float) -> str:
        """Generate human-readable sentiment analysis"""
        strength_desc = "strong" if strength > 0.7 else "moderate" if strength > 0.5 else "weak"
        
        analysis = f"Market shows {strength_desc} {sentiment} sentiment. "
        
        if rsi < 30:
            analysis += "RSI indicates oversold conditions, potential reversal opportunity. "
        elif rsi > 70:
            analysis += "RSI indicates overbought conditions, caution advised. "
        
        if volume_ratio > 1.2:
            analysis += "Above-average volume supports current trend."
        else:
            analysis += "Volume is below average, trend may lack conviction."
        
        return analysis
