"""
LSTM Model for Stock Price Time Series Prediction

This module implements an LSTM-based neural network for predicting stock prices
using historical price data and technical indicators.
"""

from __future__ import annotations
from typing import Dict, Any, Optional, Tuple
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings

from ..base_model import BaseModel

# Try to import deep learning libraries
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False
    warnings.warn("TensorFlow not available. LSTM model will use simple baseline prediction.")


class LSTMPredictor(BaseModel):
    """
    LSTM-based stock price predictor with memory and continuous learning.
    
    Features:
    - Multi-step ahead prediction
    - Attention to recent patterns
    - Continuous learning with incremental updates
    - Automatic feature scaling
    """
    
    def __init__(self, model_id: str = "lstm_stock_predictor", config: Optional[Dict] = None):
        default_config = {
            'sequence_length': 60,  # Look back 60 days
            'forecast_horizon': 5,   # Predict 5 days ahead
            'lstm_units': [128, 64, 32],
            'dropout_rate': 0.2,
            'learning_rate': 0.001,
            'batch_size': 32,
            'model_dir': './models/weights',
            'memory_dir': './models/memory'
        }
        if config:
            default_config.update(config)
        
        super().__init__(model_id, default_config)
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.has_tensorflow = HAS_TENSORFLOW
        
        if not HAS_TENSORFLOW:
            print("Warning: TensorFlow not available. Using simple baseline model.")
    
    def _build_model(self, n_features: int):
        """Build LSTM model architecture"""
        if not self.has_tensorflow:
            # Simple baseline model (moving average)
            return None
        
        model = Sequential()
        
        # First LSTM layer
        model.add(LSTM(
            units=self.config['lstm_units'][0],
            return_sequences=True,
            input_shape=(self.config['sequence_length'], n_features)
        ))
        model.add(Dropout(self.config['dropout_rate']))
        
        # Additional LSTM layers
        for units in self.config['lstm_units'][1:]:
            model.add(LSTM(units=units, return_sequences=True))
            model.add(Dropout(self.config['dropout_rate']))
        
        # Final LSTM layer
        model.add(LSTM(units=self.config['lstm_units'][-1], return_sequences=False))
        model.add(Dropout(self.config['dropout_rate']))
        
        # Output layer
        model.add(Dense(units=self.config['forecast_horizon']))
        
        # Compile model
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=self.config['learning_rate']),
            loss='mean_squared_error',
            metrics=['mae']
        )
        
        return model
    
    def _create_sequences(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create sequences for LSTM training
        
        Args:
            data: Time series data (scaled)
            
        Returns:
            X: Input sequences
            y: Target values
        """
        X, y = [], []
        seq_len = self.config['sequence_length']
        forecast_horizon = self.config['forecast_horizon']
        
        for i in range(len(data) - seq_len - forecast_horizon + 1):
            X.append(data[i:i + seq_len])
            y.append(data[i + seq_len:i + seq_len + forecast_horizon, 0])  # Predict close price
        
        return np.array(X), np.array(y)
    
    def _baseline_predict(self, X: np.ndarray) -> np.ndarray:
        """Simple baseline prediction (moving average) when TensorFlow not available"""
        predictions = []
        for seq in X:
            # Use last 5 values to predict next 5
            last_values = seq[-5:, 0]
            pred = np.array([last_values.mean()] * self.config['forecast_horizon'])
            predictions.append(pred)
        return np.array(predictions)
    
    def train(self, X_train, y_train, X_val=None, y_val=None, epochs: int = 100):
        """
        Train the LSTM model
        
        Args:
            X_train: Training features (raw time series data)
            y_train: Training labels (not used, we predict future from X)
            X_val: Validation features
            y_val: Validation labels (not used)
            epochs: Number of training epochs
        """
        print(f"Training LSTM model with {len(X_train)} samples...")
        
        # Scale the data
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        # Create sequences
        X_seq, y_seq = self._create_sequences(X_train_scaled)
        
        if len(X_seq) == 0:
            print("Error: Not enough data to create sequences")
            return
        
        print(f"Created {len(X_seq)} sequences")
        
        if not self.has_tensorflow:
            # For baseline, we don't need to train
            self.model = "baseline"
            metrics = {'loss': 0.0, 'mae': 0.0}
        else:
            # Build model if not exists
            if self.model is None:
                self.model = self._build_model(X_seq.shape[2])
            
            # Prepare validation data if provided
            if X_val is not None:
                X_val_scaled = self.scaler.transform(X_val)
                X_val_seq, y_val_seq = self._create_sequences(X_val_scaled)
                validation_data = (X_val_seq, y_val_seq)
            else:
                validation_data = None
            
            # Callbacks
            early_stopping = EarlyStopping(
                monitor='val_loss' if validation_data else 'loss',
                patience=10,
                restore_best_weights=True
            )
            
            # Train model
            history = self.model.fit(
                X_seq, y_seq,
                epochs=epochs,
                batch_size=self.config['batch_size'],
                validation_data=validation_data,
                callbacks=[early_stopping],
                verbose=1
            )
            
            # Update memory with training history
            final_epoch = len(history.history['loss'])
            metrics = {
                'loss': float(history.history['loss'][-1]),
                'mae': float(history.history['mae'][-1])
            }
            if validation_data:
                metrics['val_loss'] = float(history.history['val_loss'][-1])
                metrics['val_mae'] = float(history.history['val_mae'][-1])
        
        # Update memory
        self.memory.add_training_record(epochs, metrics)
        self.save_memory()
        self.save_model()
        
        print(f"Training complete. Final metrics: {metrics}")
    
    def predict(self, X) -> np.ndarray:
        """
        Make predictions
        
        Args:
            X: Input features (recent historical data)
            
        Returns:
            Predicted future values
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Scale input
        X_scaled = self.scaler.transform(X)
        
        # Create sequences
        X_seq, _ = self._create_sequences(X_scaled)
        
        if len(X_seq) == 0:
            raise ValueError("Input data too short to create sequences")
        
        # Predict
        if not self.has_tensorflow:
            predictions = self._baseline_predict(X_seq)
        else:
            predictions = self.model.predict(X_seq, verbose=0)
        
        # Inverse transform predictions (approximate)
        # Note: This is simplified; proper inverse transform would need full feature set
        predictions_reshaped = np.zeros((predictions.shape[0], predictions.shape[1], X_scaled.shape[1]))
        predictions_reshaped[:, :, 0] = predictions
        
        predictions_original = []
        for pred in predictions_reshaped:
            pred_inv = self.scaler.inverse_transform(pred)
            predictions_original.append(pred_inv[:, 0])
        
        return np.array(predictions_original)
    
    def evaluate(self, X, y=None) -> Dict[str, float]:
        """
        Evaluate model performance
        
        Args:
            X: Test features
            y: Not used (we predict future from X)
            
        Returns:
            Dictionary of evaluation metrics
        """
        # Make predictions
        predictions = self.predict(X)
        
        # For evaluation, compare last prediction with actual last value
        # This is simplified; in practice, you'd have actual future values
        X_scaled = self.scaler.transform(X)
        actual_last = X_scaled[-self.config['forecast_horizon']:, 0]
        
        if len(predictions) > 0:
            pred_last = predictions[-1][:len(actual_last)]
            
            mse = mean_squared_error(actual_last, pred_last)
            mae = mean_absolute_error(actual_last, pred_last)
            rmse = np.sqrt(mse)
            
            metrics = {
                'mse': float(mse),
                'mae': float(mae),
                'rmse': float(rmse)
            }
        else:
            metrics = {'mse': 0.0, 'mae': 0.0, 'rmse': 0.0}
        
        # Update memory
        self.memory.update_metrics(metrics)
        self.save_memory()
        
        return metrics
    
    def predict_next_days(self, recent_data: np.ndarray, n_days: int = 5) -> np.ndarray:
        """
        Predict next N days
        
        Args:
            recent_data: Recent historical data (at least sequence_length days)
            n_days: Number of days to predict
            
        Returns:
            Predicted prices for next n_days
        """
        if len(recent_data) < self.config['sequence_length']:
            raise ValueError(f"Need at least {self.config['sequence_length']} days of data")
        
        # Use last sequence_length days
        input_data = recent_data[-self.config['sequence_length']:]
        
        # Make prediction
        prediction = self.predict(input_data.reshape(1, -1, input_data.shape[1]))
        
        return prediction[0][:n_days]
