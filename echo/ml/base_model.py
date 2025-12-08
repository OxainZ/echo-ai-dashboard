"""
Base class for all predictive models.

Provides a common interface for training, evaluation, and prediction.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional
import pandas as pd
import numpy as np


@dataclass
class ModelMetrics:
    """Container for model evaluation metrics."""
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    mae: Optional[float] = None  # Mean Absolute Error
    mse: Optional[float] = None  # Mean Squared Error
    rmse: Optional[float] = None  # Root Mean Squared Error
    r2_score: Optional[float] = None
    confidence_interval: Optional[tuple] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            k: v for k, v in self.__dict__.items()
            if v is not None
        }


class BasePredictor(ABC):
    """
    Abstract base class for all predictive models.
    
    Implements the common interface for training, evaluation,
    and prediction across different model types.
    """
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model: Optional[Any] = None
        self.is_trained: bool = False
        self.feature_columns: Optional[list] = None
        self.metrics: Optional[ModelMetrics] = None
    
    @abstractmethod
    def train(self, X: pd.DataFrame, y: pd.Series, **kwargs) -> ModelMetrics:
        """
        Train the model on the provided data.
        
        Args:
            X: Feature DataFrame
            y: Target Series
            **kwargs: Additional training parameters
            
        Returns:
            ModelMetrics with training performance
        """
        pass
    
    @abstractmethod
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Make predictions on new data.
        
        Args:
            X: Feature DataFrame
            
        Returns:
            Array of predictions
        """
        pass
    
    @abstractmethod
    def evaluate(self, X: pd.DataFrame, y: pd.Series) -> ModelMetrics:
        """
        Evaluate model performance on test data.
        
        Args:
            X: Feature DataFrame
            y: True target values
            
        Returns:
            ModelMetrics with evaluation results
        """
        pass
    
    def save_model(self, filepath: str) -> None:
        """
        Save model to disk.
        
        Args:
            filepath: Path to save the model
        """
        raise NotImplementedError("save_model must be implemented by subclass")
    
    @classmethod
    def load_model(cls, filepath: str) -> 'BasePredictor':
        """
        Load model from disk.
        
        Args:
            filepath: Path to the saved model
            
        Returns:
            Loaded model instance
        """
        raise NotImplementedError("load_model must be implemented by subclass")
    
    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """
        Get feature importance scores if available.
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        return None
    
    def explain_prediction(self, X: pd.DataFrame, instance_idx: int = 0) -> Dict[str, Any]:
        """
        Explain a specific prediction using SHAP or LIME.
        
        Args:
            X: Feature DataFrame
            instance_idx: Index of instance to explain
            
        Returns:
            Dictionary with explanation details
        """
        raise NotImplementedError("Explainability not implemented for this model")
