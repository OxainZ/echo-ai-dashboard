"""
Machine Learning prediction models for Echo AI Dashboard
Implements LSTM and Transformer-based stock price prediction
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from ..utils.logging import get_logger
from ..utils.config import config

log = get_logger("MLPredictor")


class StockPredictor:
    """
    Base class for stock price prediction models
    Note: This is a framework - actual ML models would require training data and frameworks
    """
    
    def __init__(self, model_type: str = "lstm"):
        self.model_type = model_type
        self.model = None
        self.is_trained = False
        self.enabled = config.enable_ml_predictions
    
    def predict(self, ticker: str, historical_data: pd.DataFrame, days_ahead: int = 5) -> Dict:
        """
        Generate price predictions for future days
        
        Args:
            ticker: Stock ticker symbol
            historical_data: Historical price DataFrame with OHLCV data
            days_ahead: Number of days to predict
            
        Returns:
            Dictionary with predictions and confidence scores
        """
        if not self.enabled:
            return self._get_fallback_prediction(ticker, historical_data, days_ahead)
        
        try:
            if historical_data.empty or len(historical_data) < 30:
                log.warning(f"Insufficient data for {ticker}, using simple prediction")
                return self._simple_prediction(ticker, historical_data, days_ahead)
            
            # Use appropriate model
            if self.model_type == "lstm":
                return self._lstm_prediction(ticker, historical_data, days_ahead)
            elif self.model_type == "transformer":
                return self._transformer_prediction(ticker, historical_data, days_ahead)
            else:
                return self._simple_prediction(ticker, historical_data, days_ahead)
                
        except Exception as e:
            log.exception(f"Error predicting for {ticker}: {e}")
            return self._get_fallback_prediction(ticker, historical_data, days_ahead)
    
    def _simple_prediction(self, ticker: str, data: pd.DataFrame, days: int) -> Dict:
        """
        Simple statistical prediction using moving averages and trends
        This is a lightweight approach that doesn't require training
        """
        if data.empty:
            return self._get_fallback_prediction(ticker, data, days)
        
        # Calculate recent trend
        close_prices = data['Close'].values
        last_price = close_prices[-1]
        
        # Calculate moving averages
        ma_7 = np.mean(close_prices[-7:]) if len(close_prices) >= 7 else last_price
        ma_30 = np.mean(close_prices[-30:]) if len(close_prices) >= 30 else last_price
        
        # Calculate momentum
        returns = np.diff(close_prices) / close_prices[:-1]
        avg_return = np.mean(returns[-10:]) if len(returns) >= 10 else 0
        volatility = np.std(returns[-30:]) if len(returns) >= 30 else 0.02
        
        # Trend direction
        trend = "bullish" if ma_7 > ma_30 else "bearish"
        trend_strength = abs(ma_7 - ma_30) / ma_30 if ma_30 > 0 else 0
        
        # Generate predictions
        predictions = []
        last_predicted = last_price
        
        for i in range(1, days + 1):
            # Add trend-based movement with some randomness
            expected_return = avg_return * (1 + trend_strength)
            predicted_price = last_predicted * (1 + expected_return)
            
            # Add noise based on volatility
            noise = np.random.normal(0, volatility * last_predicted)
            predicted_price += noise * 0.3  # Reduced noise for smoother predictions
            
            predictions.append({
                'day': i,
                'date': (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d'),
                'predicted_price': round(predicted_price, 2),
                'lower_bound': round(predicted_price * (1 - volatility * 1.5), 2),
                'upper_bound': round(predicted_price * (1 + volatility * 1.5), 2),
            })
            
            last_predicted = predicted_price
        
        # Calculate confidence based on data quality and volatility
        confidence = min(0.85, max(0.45, 1 - volatility * 5))
        
        return {
            'ticker': ticker,
            'predictions': predictions,
            'confidence': round(confidence, 2),
            'trend': trend,
            'trend_strength': round(trend_strength, 3),
            'model_type': 'simple_statistical',
            'last_price': round(last_price, 2),
            'volatility': round(volatility, 3),
        }
    
    def _lstm_prediction(self, ticker: str, data: pd.DataFrame, days: int) -> Dict:
        """
        LSTM-based prediction (placeholder for actual implementation)
        Would require TensorFlow/PyTorch and trained models
        """
        log.info("LSTM prediction not yet implemented, using simple prediction")
        return self._simple_prediction(ticker, data, days)
    
    def _transformer_prediction(self, ticker: str, data: pd.DataFrame, days: int) -> Dict:
        """
        Transformer-based prediction (placeholder for actual implementation)
        Would require TensorFlow/PyTorch and trained models
        """
        log.info("Transformer prediction not yet implemented, using simple prediction")
        return self._simple_prediction(ticker, data, days)
    
    def _get_fallback_prediction(self, ticker: str, data: pd.DataFrame, days: int) -> Dict:
        """Fallback prediction when data is insufficient"""
        last_price = data['Close'].iloc[-1] if not data.empty else 100.0
        
        predictions = []
        for i in range(1, days + 1):
            predictions.append({
                'day': i,
                'date': (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d'),
                'predicted_price': round(last_price, 2),
                'lower_bound': round(last_price * 0.95, 2),
                'upper_bound': round(last_price * 1.05, 2),
            })
        
        return {
            'ticker': ticker,
            'predictions': predictions,
            'confidence': 0.3,
            'trend': 'neutral',
            'trend_strength': 0.0,
            'model_type': 'fallback',
            'last_price': round(last_price, 2),
            'volatility': 0.02,
        }


class TradingSignalGenerator:
    """Generate trading signals (Buy/Sell/Hold) based on predictions and analysis"""
    
    def __init__(self):
        self.predictor = StockPredictor()
    
    def generate_signal(self, ticker: str, historical_data: pd.DataFrame, 
                       current_quote: Dict) -> Dict:
        """
        Generate trading signal with recommendation
        
        Returns:
            Dictionary with signal, confidence, and reasoning
        """
        try:
            # Get predictions
            prediction = self.predictor.predict(ticker, historical_data, days_ahead=5)
            
            current_price = current_quote.get('price', historical_data['Close'].iloc[-1])
            predicted_price_5d = prediction['predictions'][-1]['predicted_price']
            
            # Calculate expected return
            expected_return = (predicted_price_5d - current_price) / current_price
            
            # Determine signal
            if expected_return > 0.02:  # 2% upside
                signal = "BUY"
                strength = min(1.0, expected_return * 20)
            elif expected_return < -0.02:  # 2% downside
                signal = "SELL"
                strength = min(1.0, abs(expected_return) * 20)
            else:
                signal = "HOLD"
                strength = 0.5
            
            # Generate reasoning
            reasoning = self._generate_reasoning(
                signal, expected_return, prediction['trend'], 
                prediction['volatility'], prediction['confidence']
            )
            
            return {
                'ticker': ticker,
                'signal': signal,
                'strength': round(strength, 2),
                'confidence': prediction['confidence'],
                'expected_return_5d': round(expected_return * 100, 2),
                'current_price': round(current_price, 2),
                'predicted_price_5d': predicted_price_5d,
                'reasoning': reasoning,
                'trend': prediction['trend'],
                'volatility': prediction['volatility'],
            }
            
        except Exception as e:
            log.exception(f"Error generating signal for {ticker}: {e}")
            return {
                'ticker': ticker,
                'signal': 'HOLD',
                'strength': 0.5,
                'confidence': 0.3,
                'reasoning': 'Insufficient data for recommendation',
            }
    
    def _generate_reasoning(self, signal: str, expected_return: float, 
                           trend: str, volatility: float, confidence: float) -> List[str]:
        """Generate human-readable reasoning for the signal"""
        reasoning = []
        
        if signal == "BUY":
            reasoning.append(f"Expected {expected_return*100:.1f}% upside over 5 days")
            if trend == "bullish":
                reasoning.append("Stock is in bullish trend")
            if volatility < 0.02:
                reasoning.append("Low volatility indicates stability")
        elif signal == "SELL":
            reasoning.append(f"Expected {abs(expected_return)*100:.1f}% downside over 5 days")
            if trend == "bearish":
                reasoning.append("Stock is in bearish trend")
            if volatility > 0.03:
                reasoning.append("High volatility increases risk")
        else:  # HOLD
            reasoning.append("Price expected to remain stable")
            reasoning.append("Wait for clearer trend signals")
        
        if confidence < 0.5:
            reasoning.append("⚠️ Low confidence - proceed with caution")
        
        return reasoning
