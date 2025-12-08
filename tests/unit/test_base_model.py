"""
Unit tests for BaseModel and ModelMemory classes
"""

import pytest
import os
import tempfile
import shutil
from datetime import datetime
from echo.models.base_model import BaseModel, ModelMemory


class MockModel(BaseModel):
    """Mock model for testing BaseModel"""
    
    def train(self, X_train, y_train, X_val=None, y_val=None, epochs=100):
        # Simple mock training
        self.model = "trained"
        metrics = {'loss': 0.1, 'accuracy': 0.9}
        self.memory.add_training_record(epochs, metrics)
        self.save_memory()
    
    def predict(self, X):
        if self.model is None:
            raise ValueError("Model not trained")
        return [1, 2, 3]
    
    def evaluate(self, X, y):
        metrics = {'accuracy': 0.85, 'loss': 0.15}
        self.memory.update_metrics(metrics)
        self.save_memory()
        return metrics


class TestModelMemory:
    """Test ModelMemory class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup after tests"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_memory_creation(self):
        """Test creating a new ModelMemory"""
        now = datetime.now().isoformat()
        memory = ModelMemory(
            model_id="test_model",
            created_at=now,
            last_updated=now,
            training_history=[],
            performance_metrics={},
            state_data={}
        )
        
        assert memory.model_id == "test_model"
        assert memory.version == "1.0"
        assert len(memory.training_history) == 0
    
    def test_memory_save_load(self):
        """Test saving and loading memory"""
        now = datetime.now().isoformat()
        memory = ModelMemory(
            model_id="test_model",
            created_at=now,
            last_updated=now,
            training_history=[],
            performance_metrics={'accuracy': 0.9},
            state_data={'epoch': 100}
        )
        
        # Save memory
        path = os.path.join(self.temp_dir, 'test_memory.json')
        memory.save(path)
        
        # Load memory
        loaded_memory = ModelMemory.load(path)
        
        assert loaded_memory.model_id == memory.model_id
        assert loaded_memory.performance_metrics == memory.performance_metrics
        assert loaded_memory.state_data == memory.state_data
    
    def test_update_metrics(self):
        """Test updating performance metrics"""
        now = datetime.now().isoformat()
        memory = ModelMemory(
            model_id="test_model",
            created_at=now,
            last_updated=now,
            training_history=[],
            performance_metrics={'accuracy': 0.8},
            state_data={}
        )
        
        # Update metrics
        memory.update_metrics({'accuracy': 0.9, 'loss': 0.1})
        
        assert memory.performance_metrics['accuracy'] == 0.9
        assert memory.performance_metrics['loss'] == 0.1
    
    def test_add_training_record(self):
        """Test adding training records"""
        now = datetime.now().isoformat()
        memory = ModelMemory(
            model_id="test_model",
            created_at=now,
            last_updated=now,
            training_history=[],
            performance_metrics={},
            state_data={}
        )
        
        # Add training record
        memory.add_training_record(1, {'loss': 0.5, 'accuracy': 0.7})
        memory.add_training_record(2, {'loss': 0.3, 'accuracy': 0.85})
        
        assert len(memory.training_history) == 2
        assert memory.training_history[0]['epoch'] == 1
        assert memory.training_history[1]['loss'] == 0.3


class TestBaseModel:
    """Test BaseModel class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            'model_dir': os.path.join(self.temp_dir, 'weights'),
            'memory_dir': os.path.join(self.temp_dir, 'memory')
        }
    
    def teardown_method(self):
        """Cleanup after tests"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_model_initialization(self):
        """Test model initialization"""
        model = MockModel("test_model", self.config)
        
        assert model.model_id == "test_model"
        assert model.memory is not None
        assert model.memory.model_id == "test_model"
    
    def test_model_train_and_predict(self):
        """Test training and prediction"""
        model = MockModel("test_model", self.config)
        
        # Train model
        X_train = [[1, 2], [3, 4]]
        y_train = [0, 1]
        model.train(X_train, y_train, epochs=10)
        
        assert model.model == "trained"
        assert len(model.memory.training_history) == 1
        
        # Make prediction
        predictions = model.predict([[5, 6]])
        assert predictions is not None
    
    def test_model_save_load(self):
        """Test saving and loading model"""
        model = MockModel("test_model", self.config)
        
        # Train and save
        model.train([[1, 2]], [0], epochs=5)
        model.save_model()
        
        # Create new model and load
        model2 = MockModel("test_model", self.config)
        loaded = model2.load_model()
        
        assert loaded is True
        assert model2.model == "trained"
    
    def test_model_evaluate(self):
        """Test model evaluation"""
        model = MockModel("test_model", self.config)
        model.train([[1, 2]], [0], epochs=5)
        
        # Evaluate
        metrics = model.evaluate([[3, 4]], [1])
        
        assert 'accuracy' in metrics
        assert 'loss' in metrics
        assert metrics['accuracy'] > 0
    
    def test_performance_summary(self):
        """Test getting performance summary"""
        model = MockModel("test_model", self.config)
        model.train([[1, 2]], [0], epochs=5)
        
        summary = model.get_performance_summary()
        
        assert 'model_id' in summary
        assert 'created_at' in summary
        assert 'total_training_epochs' in summary
        assert summary['model_id'] == "test_model"
        assert summary['total_training_epochs'] == 1
    
    def test_memory_persistence(self):
        """Test that memory persists across model instances"""
        # Create and train first model
        model1 = MockModel("persistent_model", self.config)
        model1.train([[1, 2]], [0], epochs=10)
        model1.save_memory()
        
        # Create second model with same ID
        model2 = MockModel("persistent_model", self.config)
        
        # Memory should be loaded automatically
        assert len(model2.memory.training_history) == 1
        assert model2.memory.training_history[0]['epoch'] == 10


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
