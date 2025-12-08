"""
Base Model Class for All AI Models

Provides common interface and memory persistence functionality.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
import json
import os
from datetime import datetime
import pickle


@dataclass
class ModelMemory:
    """
    Memory structure for model state and learning history
    """
    model_id: str
    created_at: str
    last_updated: str
    training_history: List[Dict[str, float]]
    performance_metrics: Dict[str, float]
    state_data: Dict[str, Any]
    version: str = "1.0"
    
    def save(self, path: str):
        """Save memory to disk"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(asdict(self), f, indent=2)
    
    @classmethod
    def load(cls, path: str) -> ModelMemory:
        """Load memory from disk"""
        with open(path, 'r') as f:
            data = json.load(f)
        return cls(**data)
    
    def update_metrics(self, new_metrics: Dict[str, float]):
        """Update performance metrics"""
        self.performance_metrics.update(new_metrics)
        self.last_updated = datetime.now().isoformat()
    
    def add_training_record(self, epoch: int, metrics: Dict[str, float]):
        """Add a training record to history"""
        record = {
            'epoch': epoch,
            'timestamp': datetime.now().isoformat(),
            **metrics
        }
        self.training_history.append(record)
        self.last_updated = datetime.now().isoformat()


class BaseModel(ABC):
    """
    Abstract base class for all AI models in the trading system.
    
    Provides common functionality:
    - Model persistence (save/load)
    - Memory management
    - Training interface
    - Prediction interface
    """
    
    def __init__(self, model_id: str, config: Optional[Dict] = None):
        self.model_id = model_id
        self.config = config or {}
        self.memory: Optional[ModelMemory] = None
        self.model = None
        self._initialize_memory()
    
    def _initialize_memory(self):
        """Initialize or load model memory"""
        memory_path = self._get_memory_path()
        if os.path.exists(memory_path):
            try:
                self.memory = ModelMemory.load(memory_path)
            except Exception as e:
                print(f"Failed to load memory from {memory_path}: {e}")
                self._create_new_memory()
        else:
            self._create_new_memory()
    
    def _create_new_memory(self):
        """Create new memory instance"""
        now = datetime.now().isoformat()
        self.memory = ModelMemory(
            model_id=self.model_id,
            created_at=now,
            last_updated=now,
            training_history=[],
            performance_metrics={},
            state_data={}
        )
    
    def _get_memory_path(self) -> str:
        """Get path for memory file"""
        memory_dir = self.config.get('memory_dir', './models/memory')
        os.makedirs(memory_dir, exist_ok=True)
        return os.path.join(memory_dir, f'{self.model_id}_memory.json')
    
    def _get_model_path(self) -> str:
        """Get path for model weights"""
        model_dir = self.config.get('model_dir', './models/weights')
        os.makedirs(model_dir, exist_ok=True)
        return os.path.join(model_dir, f'{self.model_id}.pkl')
    
    def save_memory(self):
        """Save model memory to disk"""
        if self.memory:
            self.memory.save(self._get_memory_path())
    
    def save_model(self):
        """Save model weights"""
        if self.model is not None:
            model_path = self._get_model_path()
            with open(model_path, 'wb') as f:
                pickle.dump(self.model, f)
            print(f"Model saved to {model_path}")
    
    def load_model(self):
        """Load model weights"""
        model_path = self._get_model_path()
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            print(f"Model loaded from {model_path}")
            return True
        return False
    
    @abstractmethod
    def train(self, X_train, y_train, X_val=None, y_val=None, epochs: int = 100):
        """
        Train the model
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features (optional)
            y_val: Validation labels (optional)
            epochs: Number of training epochs
        """
        pass
    
    @abstractmethod
    def predict(self, X) -> Any:
        """
        Make predictions
        
        Args:
            X: Input features
            
        Returns:
            Predictions
        """
        pass
    
    @abstractmethod
    def evaluate(self, X, y) -> Dict[str, float]:
        """
        Evaluate model performance
        
        Args:
            X: Test features
            y: Test labels
            
        Returns:
            Dictionary of evaluation metrics
        """
        pass
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of model performance"""
        if not self.memory:
            return {}
        
        return {
            'model_id': self.model_id,
            'created_at': self.memory.created_at,
            'last_updated': self.memory.last_updated,
            'total_training_epochs': len(self.memory.training_history),
            'current_metrics': self.memory.performance_metrics,
            'version': self.memory.version
        }
