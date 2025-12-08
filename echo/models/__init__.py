"""
AI Models Package for Echo Trading Dashboard

This package contains machine learning models for stock prediction and trading decisions:
- LSTM: Long Short-Term Memory networks for time series prediction
- Transformer: Attention-based models for pattern recognition
- RL Agent: Reinforcement Learning agents for trading strategy optimization
"""

from .base_model import BaseModel, ModelMemory

__all__ = ['BaseModel', 'ModelMemory']
