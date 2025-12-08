"""
AI Module for Echo Trading Dashboard

Provides machine learning models and tools for:
- Stock price prediction
- Trading decision-making
- Market sentiment analysis
- Risk assessment
- Data pipeline and preprocessing
- Dashboard UI components
"""

from .models import (
    StockPricePredictor,
    TradingDecisionEngine,
    MarketSentimentAnalyzer,
    PredictionResult
)

from .data_pipeline import (
    DataPipeline,
    DataValidator,
    MarketDataAggregator
)

from .config import (
    get_config,
    get_disclaimer,
    AI_MODEL_CONFIG,
    RISK_MANAGEMENT,
    DISCLAIMERS
)

from .dashboard_components import AIDashboardUI

__all__ = [
    'StockPricePredictor',
    'TradingDecisionEngine',
    'MarketSentimentAnalyzer',
    'PredictionResult',
    'DataPipeline',
    'DataValidator',
    'MarketDataAggregator',
    'AIDashboardUI',
    'get_config',
    'get_disclaimer',
    'AI_MODEL_CONFIG',
    'RISK_MANAGEMENT',
    'DISCLAIMERS'
]
