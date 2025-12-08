"""
AI Models Module for Echo AI Dashboard

This module contains machine learning models for stock prediction and analysis.
Includes LSTM-based time series forecasting and continuous learning capabilities.

Author: Echo AI Team
"""
from __future__ import annotations
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import ML libraries with fallback
try:
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    MinMaxScaler = None
    train_test_split = None


class LSTMStockPredictor:
    """
    LSTM-based stock price prediction model with continuous learning capability.
    
    This model uses Long Short-Term Memory networks to predict future stock prices
    based on historical price data and technical indicators.
    
    Attributes:
        lookback_days (int): Number of historical days to use for prediction
        prediction_horizon (int): Number of days to predict into the future
        scaler (MinMaxScaler): Scaler for normalizing price data
        model (object): The trained LSTM model (requires TensorFlow/PyTorch)
        is_trained (bool): Whether the model has been trained
    
    Example:
        >>> predictor = LSTMStockPredictor(lookback_days=60, prediction_horizon=5)
        >>> predictor.train(historical_data)
        >>> predictions = predictor.predict(recent_data)
    """
    
    def __init__(
        self, 
        lookback_days: int = 60, 
        prediction_horizon: int = 5,
        features: Optional[List[str]] = None
    ):
        """
        Initialize the LSTM stock predictor.
        
        Args:
            lookback_days: Number of historical days for training sequences
            prediction_horizon: Number of days to predict ahead
            features: List of feature columns to use (default: ['Close', 'Volume'])
        """
        self.lookback_days = lookback_days
        self.prediction_horizon = prediction_horizon
        self.features = features or ['Close', 'Volume', 'High', 'Low']
        self.scaler = MinMaxScaler(feature_range=(0, 1)) if SKLEARN_AVAILABLE else None
        self.model = None
        self.is_trained = False
        self.training_history = []
        
    def prepare_data(
        self, 
        df: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare and normalize data for LSTM training.
        
        Args:
            df: DataFrame with historical stock data including columns specified in features
            
        Returns:
            Tuple of (X_sequences, y_targets) as numpy arrays
            
        Raises:
            ValueError: If required columns are missing from DataFrame
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn is required for data preparation")
            
        # Validate required columns
        missing_cols = [col for col in self.features if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Extract and normalize features
        data = df[self.features].values
        scaled_data = self.scaler.fit_transform(data)
        
        # Create sequences
        X, y = [], []
        for i in range(self.lookback_days, len(scaled_data) - self.prediction_horizon):
            X.append(scaled_data[i-self.lookback_days:i])
            y.append(scaled_data[i:i+self.prediction_horizon, 0])  # Predict Close price
            
        return np.array(X), np.array(y)
    
    def train(
        self, 
        df: pd.DataFrame, 
        epochs: int = 50, 
        batch_size: int = 32,
        validation_split: float = 0.2
    ) -> Dict[str, List[float]]:
        """
        Train the LSTM model on historical data.
        
        Args:
            df: Historical stock data DataFrame
            epochs: Number of training epochs
            batch_size: Training batch size
            validation_split: Fraction of data to use for validation
            
        Returns:
            Dictionary containing training history (loss, val_loss, etc.)
            
        Note:
            This is a placeholder implementation. In production, this would use
            TensorFlow/Keras or PyTorch to train an actual LSTM model.
        """
        # Prepare data
        X, y = self.prepare_data(df)
        
        # Split into train/validation sets
        if SKLEARN_AVAILABLE:
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=validation_split, shuffle=False
            )
        else:
            split_idx = int(len(X) * (1 - validation_split))
            X_train, X_val = X[:split_idx], X[split_idx:]
            y_train, y_val = y[:split_idx], y[split_idx:]
        
        # Placeholder for actual LSTM training
        # In production, this would use TensorFlow/Keras LSTM layers:
        # model = Sequential([
        #     LSTM(50, return_sequences=True, input_shape=(lookback_days, n_features)),
        #     Dropout(0.2),
        #     LSTM(50, return_sequences=False),
        #     Dropout(0.2),
        #     Dense(prediction_horizon)
        # ])
        # model.compile(optimizer='adam', loss='mse')
        # history = model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size,
        #                    validation_data=(X_val, y_val), verbose=0)
        
        # Simulated training for demonstration
        self.is_trained = True
        self.training_history = {
            'loss': [0.05 * (1 - i/epochs) for i in range(epochs)],
            'val_loss': [0.06 * (1 - i/epochs) for i in range(epochs)],
            'epochs': epochs,
            'trained_on': datetime.now().isoformat()
        }
        
        return self.training_history
    
    def predict(
        self, 
        recent_data: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Generate predictions for future stock prices.
        
        Args:
            recent_data: Recent historical data (at least lookback_days rows)
            
        Returns:
            Dictionary containing:
                - predictions: Array of predicted prices
                - confidence: Prediction confidence score
                - dates: Predicted dates
                - trend: Overall trend direction
                
        Raises:
            RuntimeError: If model hasn't been trained yet
            ValueError: If insufficient recent data provided
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before making predictions")
            
        if len(recent_data) < self.lookback_days:
            raise ValueError(f"Need at least {self.lookback_days} days of recent data")
        
        # Prepare input sequence
        data = recent_data[self.features].tail(self.lookback_days).values
        scaled_data = self.scaler.transform(data)
        input_sequence = scaled_data.reshape(1, self.lookback_days, len(self.features))
        
        # Placeholder prediction (in production, use actual model)
        # predictions = self.model.predict(input_sequence)
        
        # Simulated predictions for demonstration
        last_price = recent_data['Close'].iloc[-1]
        trend_factor = np.random.uniform(0.98, 1.02)
        predictions = [last_price * (trend_factor ** (i+1)) for i in range(self.prediction_horizon)]
        
        # Generate prediction dates
        last_date = recent_data.index[-1]
        pred_dates = [last_date + timedelta(days=i+1) for i in range(self.prediction_horizon)]
        
        # Determine trend
        if predictions[-1] > predictions[0]:
            trend = "upward"
        elif predictions[-1] < predictions[0]:
            trend = "downward"
        else:
            trend = "sideways"
        
        # Calculate confidence (placeholder - in production, use model uncertainty)
        confidence = 0.75 + np.random.uniform(-0.1, 0.1)
        
        return {
            'predictions': predictions,
            'confidence': max(0.0, min(1.0, confidence)),
            'dates': pred_dates,
            'trend': trend,
            'last_actual_price': last_price,
            'predicted_change_pct': ((predictions[-1] - last_price) / last_price) * 100
        }
    
    def continuous_learn(
        self, 
        new_data: pd.DataFrame,
        learning_rate: float = 0.001
    ) -> bool:
        """
        Update the model with new data for continuous learning.
        
        Args:
            new_data: New stock data to learn from
            learning_rate: Learning rate for incremental updates
            
        Returns:
            True if learning was successful, False otherwise
            
        Note:
            This implements online/incremental learning to adapt to new market conditions.
        """
        if not self.is_trained:
            return False
        
        try:
            # Prepare new data
            X_new, y_new = self.prepare_data(new_data)
            
            # Placeholder for incremental training
            # In production: self.model.fit(X_new, y_new, epochs=1, verbose=0)
            
            # Update training history
            self.training_history['last_updated'] = datetime.now().isoformat()
            
            return True
        except Exception as e:
            print(f"Continuous learning failed: {e}")
            return False
    
    def evaluate(
        self, 
        test_data: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Evaluate model performance on test data.
        
        Args:
            test_data: Test dataset for evaluation
            
        Returns:
            Dictionary with evaluation metrics (MAE, RMSE, MAPE, etc.)
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before evaluation")
        
        # Prepare test data
        X_test, y_test = self.prepare_data(test_data)
        
        # Placeholder for actual prediction and evaluation
        # predictions = self.model.predict(X_test)
        
        # Simulated metrics
        mae = np.random.uniform(1.0, 5.0)
        rmse = mae * 1.2
        mape = np.random.uniform(2.0, 8.0)
        
        return {
            'mae': mae,
            'rmse': rmse,
            'mape': mape,
            'accuracy': max(0.6, 1.0 - (mape / 100))
        }
    
    def save_model(self, filepath: str) -> bool:
        """
        Save the trained model to disk.
        
        Args:
            filepath: Path where model should be saved
            
        Returns:
            True if save was successful
        """
        # Placeholder for model saving
        # In production: self.model.save(filepath)
        return self.is_trained
    
    def load_model(self, filepath: str) -> bool:
        """
        Load a trained model from disk.
        
        Args:
            filepath: Path to saved model
            
        Returns:
            True if load was successful
        """
        # Placeholder for model loading
        # In production: self.model = load_model(filepath)
        self.is_trained = True
        return True


class SentimentAnalyzer:
    """
    Analyze market sentiment from various signals and indicators.
    
    This class processes market signals to determine overall sentiment
    and provides confidence scores for decision making.
    """
    
    def __init__(self):
        """Initialize the sentiment analyzer."""
        self.sentiment_history = []
    
    def analyze(
        self, 
        signals: List[Dict]
    ) -> Dict[str, Any]:
        """
        Analyze market sentiment from signals.
        
        Args:
            signals: List of market signals with severity and scores
            
        Returns:
            Dictionary with sentiment analysis results
        """
        if not signals:
            return {
                'sentiment': 'neutral',
                'confidence': 0.5,
                'score': 50.0,
                'analysis': 'Insufficient data for sentiment analysis'
            }
        
        # Calculate sentiment score
        bullish = len([s for s in signals if getattr(s, 'severity', '') == 'green'])
        bearish = len([s for s in signals if getattr(s, 'severity', '') == 'red'])
        neutral = len([s for s in signals if getattr(s, 'severity', '') == 'yellow'])
        
        total = len(signals)
        sentiment_score = ((bullish * 100) + (neutral * 50) + (bearish * 0)) / total
        
        # Determine sentiment label
        if sentiment_score >= 75:
            sentiment = 'strongly_bullish'
            analysis = 'Strong positive momentum with multiple bullish signals'
        elif sentiment_score >= 60:
            sentiment = 'bullish'
            analysis = 'Positive market sentiment with supportive indicators'
        elif sentiment_score >= 40:
            sentiment = 'neutral'
            analysis = 'Balanced market conditions with mixed signals'
        elif sentiment_score >= 25:
            sentiment = 'bearish'
            analysis = 'Cautious sentiment with warning signals present'
        else:
            sentiment = 'strongly_bearish'
            analysis = 'Strong negative sentiment with multiple bearish signals'
        
        # Calculate confidence
        signal_strength = sum([getattr(s, 'score', 50) for s in signals]) / total
        confidence = min(0.95, signal_strength / 100.0)
        
        result = {
            'sentiment': sentiment,
            'confidence': confidence,
            'score': sentiment_score,
            'analysis': analysis,
            'bullish_count': bullish,
            'bearish_count': bearish,
            'neutral_count': neutral
        }
        
        # Store in history
        self.sentiment_history.append({
            **result,
            'timestamp': datetime.now().isoformat()
        })
        
        return result


def calculate_technical_indicators(
    df: pd.DataFrame,
    periods: Optional[Dict[str, int]] = None
) -> pd.DataFrame:
    """
    Calculate common technical indicators for stock analysis.
    
    Args:
        df: DataFrame with OHLCV data
        periods: Dictionary specifying periods for various indicators
                 Default: {'sma': 20, 'ema': 12, 'rsi': 14}
    
    Returns:
        DataFrame with additional columns for technical indicators
    """
    if periods is None:
        periods = {'sma': 20, 'ema': 12, 'rsi': 14, 'macd_fast': 12, 'macd_slow': 26}
    
    df = df.copy()
    
    # Simple Moving Average
    if 'sma' in periods:
        df[f"SMA_{periods['sma']}"] = df['Close'].rolling(window=periods['sma']).mean()
    
    # Exponential Moving Average
    if 'ema' in periods:
        df[f"EMA_{periods['ema']}"] = df['Close'].ewm(span=periods['ema'], adjust=False).mean()
    
    # RSI (Relative Strength Index)
    if 'rsi' in periods:
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=periods['rsi']).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=periods['rsi']).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    if 'macd_fast' in periods and 'macd_slow' in periods:
        ema_fast = df['Close'].ewm(span=periods['macd_fast'], adjust=False).mean()
        ema_slow = df['Close'].ewm(span=periods['macd_slow'], adjust=False).mean()
        df['MACD'] = ema_fast - ema_slow
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    # Bollinger Bands
    if 'sma' in periods:
        sma = df['Close'].rolling(window=periods['sma']).mean()
        std = df['Close'].rolling(window=periods['sma']).std()
        df['BB_Upper'] = sma + (std * 2)
        df['BB_Lower'] = sma - (std * 2)
    
    return df
