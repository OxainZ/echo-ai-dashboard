"""
LSTM Time-Series Forecasting Model

Implements an LSTM (Long Short-Term Memory) neural network for
predicting stock price movements based on historical patterns.

Features:
- Multi-layer LSTM architecture
- Dropout for regularization
- Configurable sequence length
- Support for multiple features (OHLCV data)
- Model saving/loading capabilities
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Tuple, Optional, Dict
import json
import os
from datetime import datetime

# Try to import ML libraries, but make them optional
try:
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    MinMaxScaler = None
    train_test_split = None

# Note: TensorFlow/Keras is optional for deployment but needed for training
# This allows the dashboard to work without heavy ML dependencies
KERAS_AVAILABLE = False
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
    KERAS_AVAILABLE = True
except ImportError:
    pass


class LSTMPredictor:
    """
    LSTM-based stock price prediction model
    
    Uses historical OHLCV data to predict future price movements.
    The model can be trained on historical data and used for inference
    on new data.
    
    Attributes:
        sequence_length (int): Number of time steps to use for prediction
        features (list): List of features to use (default: OHLCV)
        model: Trained Keras LSTM model
        scaler: MinMaxScaler for data normalization
    """
    
    def __init__(
        self,
        sequence_length: int = 60,
        features: list = None,
        lstm_units: int = 50,
        dropout_rate: float = 0.2
    ):
        """
        Initialize LSTM predictor
        
        Args:
            sequence_length: Number of past days to consider
            features: List of features to use (defaults to OHLCV)
            lstm_units: Number of LSTM units per layer
            dropout_rate: Dropout rate for regularization
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn is required. Install with: pip install scikit-learn")
        
        self.sequence_length = sequence_length
        self.features = features or ['Open', 'High', 'Low', 'Close', 'Volume']
        self.lstm_units = lstm_units
        self.dropout_rate = dropout_rate
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.is_trained = False
    
    def prepare_data(
        self,
        df: pd.DataFrame,
        target_column: str = 'Close'
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare time-series data for LSTM training
        
        Args:
            df: DataFrame with OHLCV data
            target_column: Column to predict (default: Close)
            
        Returns:
            Tuple of (X, y) arrays ready for training
        """
        # Extract features
        data = df[self.features].values
        
        # Normalize data
        scaled_data = self.scaler.fit_transform(data)
        
        # Create sequences
        X, y = [], []
        target_idx = self.features.index(target_column)
        
        for i in range(self.sequence_length, len(scaled_data)):
            X.append(scaled_data[i - self.sequence_length:i])
            y.append(scaled_data[i, target_idx])
        
        return np.array(X), np.array(y)
    
    def build_model(self, input_shape: Tuple) -> None:
        """
        Build LSTM model architecture
        
        Args:
            input_shape: Shape of input data (sequence_length, n_features)
        """
        if not KERAS_AVAILABLE:
            raise ImportError(
                "TensorFlow is required for model training. "
                "Install with: pip install tensorflow"
            )
        
        model = Sequential([
            # First LSTM layer with return sequences
            LSTM(
                units=self.lstm_units,
                return_sequences=True,
                input_shape=input_shape
            ),
            Dropout(self.dropout_rate),
            
            # Second LSTM layer
            LSTM(units=self.lstm_units, return_sequences=False),
            Dropout(self.dropout_rate),
            
            # Dense layers
            Dense(units=25),
            Dense(units=1)
        ])
        
        # Compile model
        model.compile(
            optimizer='adam',
            loss='mean_squared_error',
            metrics=['mae']
        )
        
        self.model = model
    
    def train(
        self,
        df: pd.DataFrame,
        epochs: int = 50,
        batch_size: int = 32,
        validation_split: float = 0.2,
        verbose: int = 1
    ) -> Dict:
        """
        Train the LSTM model
        
        Args:
            df: Historical price data
            epochs: Number of training epochs
            batch_size: Training batch size
            validation_split: Fraction of data for validation
            verbose: Verbosity level
            
        Returns:
            Dict with training history
        """
        # Prepare data
        X, y = self.prepare_data(df)
        
        # Build model if not already built
        if self.model is None:
            self.build_model(input_shape=(X.shape[1], X.shape[2]))
        
        # Early stopping callback
        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        # Train model
        history = self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            callbacks=[early_stop],
            verbose=verbose
        )
        
        self.is_trained = True
        
        return {
            'loss': history.history['loss'],
            'val_loss': history.history['val_loss'],
            'mae': history.history['mae'],
            'val_mae': history.history['val_mae']
        }
    
    def predict(
        self,
        df: pd.DataFrame,
        steps_ahead: int = 1
    ) -> np.ndarray:
        """
        Make predictions on new data
        
        Args:
            df: Recent historical data (at least sequence_length rows)
            steps_ahead: Number of steps to predict into future
            
        Returns:
            Array of predicted prices
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Prepare last sequence
        data = df[self.features].tail(self.sequence_length).values
        scaled_data = self.scaler.transform(data)
        
        predictions = []
        current_sequence = scaled_data.reshape(1, self.sequence_length, len(self.features))
        
        for _ in range(steps_ahead):
            # Predict next value
            pred_scaled = self.model.predict(current_sequence, verbose=0)
            
            # Create full feature vector for inverse transform
            # (use last known values for other features)
            full_pred = current_sequence[0, -1, :].copy()
            target_idx = self.features.index('Close')
            full_pred[target_idx] = pred_scaled[0, 0]
            
            # Inverse transform to get actual price
            pred_actual = self.scaler.inverse_transform(
                full_pred.reshape(1, -1)
            )[0, target_idx]
            predictions.append(pred_actual)
            
            # Update sequence for next prediction
            current_sequence = np.roll(current_sequence, -1, axis=1)
            current_sequence[0, -1, :] = full_pred
        
        return np.array(predictions)
    
    def save_model(self, path: str) -> None:
        """
        Save trained model to disk
        
        Args:
            path: Directory path to save model
        """
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        os.makedirs(path, exist_ok=True)
        
        # Save Keras model
        self.model.save(os.path.join(path, 'lstm_model.h5'))
        
        # Save scaler and metadata
        import pickle
        with open(os.path.join(path, 'scaler.pkl'), 'wb') as f:
            pickle.dump(self.scaler, f)
        
        metadata = {
            'sequence_length': self.sequence_length,
            'features': self.features,
            'lstm_units': self.lstm_units,
            'dropout_rate': self.dropout_rate,
            'trained_at': datetime.now().isoformat()
        }
        
        with open(os.path.join(path, 'metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
    
    @classmethod
    def load_model(cls, path: str) -> 'LSTMPredictor':
        """
        Load trained model from disk
        
        Args:
            path: Directory path containing saved model
            
        Returns:
            Loaded LSTMPredictor instance
        """
        if not KERAS_AVAILABLE:
            raise ImportError("TensorFlow required to load models")
        
        # Load metadata
        with open(os.path.join(path, 'metadata.json'), 'r') as f:
            metadata = json.load(f)
        
        # Create instance
        predictor = cls(
            sequence_length=metadata['sequence_length'],
            features=metadata['features'],
            lstm_units=metadata['lstm_units'],
            dropout_rate=metadata['dropout_rate']
        )
        
        # Load Keras model
        predictor.model = load_model(os.path.join(path, 'lstm_model.h5'))
        
        # Load scaler
        import pickle
        with open(os.path.join(path, 'scaler.pkl'), 'rb') as f:
            predictor.scaler = pickle.load(f)
        
        predictor.is_trained = True
        
        return predictor
    
    def evaluate(
        self,
        df: pd.DataFrame,
        test_size: float = 0.2
    ) -> Dict:
        """
        Evaluate model performance on test data
        
        Args:
            df: Historical data for evaluation
            test_size: Fraction of data to use for testing
            
        Returns:
            Dict with evaluation metrics
        """
        X, y = self.prepare_data(df)
        
        # Split data
        split_idx = int(len(X) * (1 - test_size))
        X_test, y_test = X[split_idx:], y[split_idx:]
        
        # Make predictions
        predictions = self.model.predict(X_test, verbose=0)
        
        # Calculate metrics
        mse = np.mean((predictions.flatten() - y_test) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(predictions.flatten() - y_test))
        
        # Calculate directional accuracy
        actual_direction = np.sign(np.diff(y_test))
        pred_direction = np.sign(np.diff(predictions.flatten()))
        directional_accuracy = np.mean(actual_direction == pred_direction)
        
        return {
            'mse': float(mse),
            'rmse': float(rmse),
            'mae': float(mae),
            'directional_accuracy': float(directional_accuracy)
        }


def create_lstm_signal(
    ticker: str,
    historical_data: pd.DataFrame,
    model_path: Optional[str] = None
) -> Dict:
    """
    Generate trading signal using LSTM predictions
    
    Args:
        ticker: Stock ticker symbol
        historical_data: Recent price history
        model_path: Path to pre-trained model (trains new if None)
        
    Returns:
        Dict with signal information
    """
    try:
        # Load or train model
        if model_path and os.path.exists(model_path):
            predictor = LSTMPredictor.load_model(model_path)
        else:
            # Train new model on available data
            predictor = LSTMPredictor(sequence_length=60)
            if len(historical_data) > 100:
                predictor.train(historical_data, epochs=20, verbose=0)
            else:
                return {
                    'error': 'Insufficient data for training',
                    'recommendation': 'neutral'
                }
        
        # Make prediction
        current_price = historical_data['Close'].iloc[-1]
        predictions = predictor.predict(historical_data, steps_ahead=5)
        predicted_price = predictions[-1]
        
        # Calculate expected return
        expected_return = (predicted_price - current_price) / current_price
        
        # Generate signal
        if expected_return > 0.02:  # 2% upside
            recommendation = 'bullish'
            confidence = min(0.95, 0.5 + abs(expected_return) * 2)
        elif expected_return < -0.02:  # 2% downside
            recommendation = 'bearish'
            confidence = min(0.95, 0.5 + abs(expected_return) * 2)
        else:
            recommendation = 'neutral'
            confidence = 0.5
        
        return {
            'ticker': ticker,
            'current_price': float(current_price),
            'predicted_price': float(predicted_price),
            'expected_return': float(expected_return),
            'recommendation': recommendation,
            'confidence': float(confidence),
            'model': 'LSTM'
        }
    
    except Exception as e:
        return {
            'error': str(e),
            'recommendation': 'neutral',
            'confidence': 0.0
        }
