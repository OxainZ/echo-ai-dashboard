"""
Base Classes for Machine Learning Models

This module defines the abstract base classes and interfaces for
all ML models in the Echo AI system.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import numpy as np
import pandas as pd


@dataclass
class Prediction:
    """
    Prediction output from an ML model.
    
    Attributes:
        timestamp: When the prediction was made
        ticker: Stock ticker symbol
        prediction_horizon: How far ahead (e.g., "1d", "5d", "1mo")
        predicted_price: Predicted price value
        confidence: Confidence score (0-1)
        direction: Predicted direction ("up", "down", "neutral")
        probability: Probability of predicted direction (0-1)
        lower_bound: Lower confidence interval bound
        upper_bound: Upper confidence interval bound
        model_version: Version of the model used
        features_used: List of features used in prediction
    """
    timestamp: datetime
    ticker: str
    prediction_horizon: str
    predicted_price: float
    confidence: float
    direction: str
    probability: float
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    model_version: str = "1.0.0"
    features_used: Optional[List[str]] = None


class BasePredictor(ABC):
    """
    Abstract base class for all stock prediction models.
    
    All prediction models should inherit from this class and implement
    the required abstract methods.
    
    Attributes:
        model_name: Name of the model
        version: Model version
        is_trained: Whether the model has been trained
        hyperparameters: Model hyperparameters
    """
    
    def __init__(self, model_name: str, version: str = "1.0.0"):
        """
        Initialize the base predictor.
        
        Args:
            model_name: Name identifier for the model
            version: Version string for the model
        """
        self.model_name = model_name
        self.version = version
        self.is_trained = False
        self.hyperparameters: Dict = {}
        
    @abstractmethod
    def train(self, X: pd.DataFrame, y: pd.Series, **kwargs) -> Dict:
        """
        Train the model on provided data.
        
        Args:
            X: Feature matrix (DataFrame)
            y: Target variable (Series)
            **kwargs: Additional training parameters
            
        Returns:
            Dictionary with training metrics (loss, accuracy, etc.)
        """
        pass
    
    @abstractmethod
    def predict(self, ticker: str, horizon: str = "1d") -> Prediction:
        """
        Make a prediction for a given ticker.
        
        Args:
            ticker: Stock ticker symbol
            horizon: Prediction horizon (e.g., "1d", "5d", "1mo")
            
        Returns:
            Prediction object with predicted values and confidence
        """
        pass
    
    @abstractmethod
    def predict_batch(self, tickers: List[str], horizon: str = "1d") -> List[Prediction]:
        """
        Make predictions for multiple tickers at once.
        
        Args:
            tickers: List of stock ticker symbols
            horizon: Prediction horizon for all tickers
            
        Returns:
            List of Prediction objects
        """
        pass
    
    def validate(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict:
        """
        Validate model performance on test data.
        
        Args:
            X_test: Test feature matrix
            y_test: Test target variable
            
        Returns:
            Dictionary with validation metrics
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before validation")
        
        # Default implementation - override for specific metrics
        predictions = self.predict_batch([str(i) for i in range(len(X_test))])
        
        return {
            "mse": 0.0,
            "mae": 0.0,
            "r2_score": 0.0,
            "directional_accuracy": 0.0
        }
    
    def save_model(self, path: str) -> None:
        """
        Save model to disk.
        
        Args:
            path: File path to save the model
        """
        raise NotImplementedError("Save functionality not implemented")
    
    def load_model(self, path: str) -> None:
        """
        Load model from disk.
        
        Args:
            path: File path to load the model from
        """
        raise NotImplementedError("Load functionality not implemented")
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance scores.
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        raise NotImplementedError("Feature importance not implemented for this model")


class ModelRegistry:
    """
    Registry for managing multiple ML models.
    
    Allows registering, retrieving, and managing different prediction models.
    """
    
    def __init__(self):
        """Initialize the model registry."""
        self._models: Dict[str, BasePredictor] = {}
        
    def register(self, model: BasePredictor, name: Optional[str] = None) -> None:
        """
        Register a model in the registry.
        
        Args:
            model: Model instance to register
            name: Optional name override (defaults to model.model_name)
        """
        model_name = name or model.model_name
        self._models[model_name] = model
        
    def get(self, name: str) -> Optional[BasePredictor]:
        """
        Retrieve a model by name.
        
        Args:
            name: Name of the model to retrieve
            
        Returns:
            Model instance or None if not found
        """
        return self._models.get(name)
    
    def list_models(self) -> List[str]:
        """
        List all registered model names.
        
        Returns:
            List of model names
        """
        return list(self._models.keys())
    
    def remove(self, name: str) -> bool:
        """
        Remove a model from the registry.
        
        Args:
            name: Name of the model to remove
            
        Returns:
            True if removed, False if not found
        """
        if name in self._models:
            del self._models[name]
            return True
        return False
