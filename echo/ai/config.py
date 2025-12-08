"""
AI Configuration for Echo Trading Dashboard

Contains configuration for AI models, risk management, and trading parameters
"""

# AI Model Configuration
AI_MODEL_CONFIG = {
    "predictor": {
        "lookback_period": 30,
        "model_version": "v1.0-lightweight",
        "confidence_threshold": 0.65,
        "prediction_horizon_days": 5
    },
    "sentiment_analyzer": {
        "min_data_points": 20,
        "sentiment_threshold": 0.6
    },
    "decision_engine": {
        "risk_tolerance": 0.02,  # 2% max risk per trade
        "max_loss_pct": 0.05,  # 5% stop-loss
        "max_position_size": 0.25,  # 25% max position size
        "kelly_fraction": 0.5  # Use half-Kelly for safety
    }
}

# Risk Management Configuration
RISK_MANAGEMENT = {
    "position_sizing": {
        "method": "kelly",  # kelly, fixed, volatility_adjusted
        "max_portfolio_risk": 0.10,  # 10% max portfolio risk
        "max_single_position": 0.25,  # 25% max single position
    },
    "stop_loss": {
        "default_pct": 0.05,  # 5% stop-loss
        "trailing_stop": True,
        "atr_multiplier": 2.0  # For ATR-based stops
    },
    "take_profit": {
        "default_pct": 0.10,  # 10% take-profit
        "reward_risk_ratio": 2.0  # 2:1 reward/risk
    },
    "risk_limits": {
        "max_daily_loss": 0.03,  # 3% max daily loss
        "max_drawdown": 0.15,  # 15% max drawdown
        "max_open_positions": 5
    }
}

# Data Pipeline Configuration
DATA_PIPELINE = {
    "cache_duration_minutes": 5,
    "default_period": "3mo",
    "default_interval": "1d",
    "required_data_points": 20,
    "data_sources": ["yfinance"],  # Can add more sources
}

# Trading Strategy Configuration
TRADING_STRATEGY = {
    "entry_rules": {
        "min_confidence": 0.65,
        "require_multiple_confirmations": True,
        "check_market_regime": True
    },
    "exit_rules": {
        "use_trailing_stop": True,
        "partial_profit_taking": True,
        "time_based_exit": False
    },
    "filters": {
        "min_volume": 100000,  # Minimum daily volume
        "min_price": 5.0,  # Minimum stock price
        "max_volatility": 0.50  # Maximum annualized volatility
    }
}

# Dashboard Configuration
DASHBOARD_CONFIG = {
    "auto_refresh_seconds": 15,
    "max_predictions_display": 5,
    "show_technical_indicators": True,
    "show_ai_explanations": True,
    "enable_alerts": True,
    "alert_thresholds": {
        "high_confidence": 0.80,
        "high_risk": 0.75,
        "significant_movement": 0.05  # 5% price movement
    }
}

# Ethical and Legal Disclaimers
DISCLAIMERS = {
    "investment_disclaimer": """
    IMPORTANT INVESTMENT DISCLAIMER:
    
    This AI-powered trading dashboard is for informational and educational purposes only.
    It does NOT constitute financial advice, investment advice, trading advice, or any 
    other type of professional advice.
    
    Key Points:
    - AI predictions are not guaranteed and may be incorrect
    - Past performance does not indicate future results
    - Trading involves substantial risk of loss
    - You may lose all invested capital
    - Always do your own research before making investment decisions
    - Consult with a licensed financial advisor for personalized advice
    
    By using this dashboard, you acknowledge that you understand these risks and 
    accept full responsibility for your trading decisions.
    """,
    
    "data_disclaimer": """
    DATA SOURCING DISCLAIMER:
    
    All market data is sourced from publicly available APIs and data providers.
    - Data is provided "as is" without warranties
    - Data accuracy is dependent on third-party sources
    - Real-time data may have delays
    - Historical data may contain errors or gaps
    
    We make no representations about the accuracy, reliability, or completeness of data.
    """,
    
    "ai_disclaimer": """
    AI MODEL DISCLAIMER:
    
    The AI models used in this dashboard are:
    - Based on historical patterns and technical analysis
    - Not guaranteed to predict future market movements
    - Subject to model limitations and biases
    - Continuously learning but not infallible
    
    AI predictions should be one of many factors in your decision-making process,
    not the sole basis for trading decisions.
    """,
    
    "risk_disclaimer": """
    RISK WARNING:
    
    Trading stocks and other securities involves significant risk, including:
    - Loss of principal investment
    - Market volatility and unpredictability
    - Liquidity risks
    - Execution risks
    - Regulatory and geopolitical risks
    
    Only invest what you can afford to lose. Consider your financial situation,
    investment objectives, and risk tolerance before trading.
    """
}

# Compliance and Ethics
COMPLIANCE = {
    "data_usage": "ethical",  # Ensure data is sourced ethically
    "privacy": "user_data_not_stored",  # No personal data storage
    "transparency": "open_about_limitations",  # Be transparent about AI limitations
    "responsible_ai": True,  # Follow responsible AI principles
    "regulatory_compliance": "educational_tool",  # Position as educational tool
}

# Feature Flags
FEATURE_FLAGS = {
    "enable_ai_predictions": True,
    "enable_sentiment_analysis": True,
    "enable_risk_assessment": True,
    "enable_auto_trading": False,  # Disabled for safety
    "enable_paper_trading": False,  # Could be enabled for simulation
    "enable_backtesting": False,  # Could be enabled for strategy testing
    "enable_advanced_models": False,  # Reserved for LSTM/Transformer models
}

# Model Performance Tracking
PERFORMANCE_TRACKING = {
    "track_predictions": True,
    "track_accuracy": True,
    "min_tracking_samples": 10,
    "performance_window_days": 30
}

# Logging and Monitoring
LOGGING_CONFIG = {
    "log_predictions": True,
    "log_decisions": True,
    "log_errors": True,
    "log_level": "INFO",
    "log_to_file": False
}

def get_config(section: str = None):
    """
    Get configuration settings
    
    Args:
        section: Specific section to retrieve (None for all)
        
    Returns:
        Configuration dict
    """
    all_config = {
        "ai_model": AI_MODEL_CONFIG,
        "risk_management": RISK_MANAGEMENT,
        "data_pipeline": DATA_PIPELINE,
        "trading_strategy": TRADING_STRATEGY,
        "dashboard": DASHBOARD_CONFIG,
        "disclaimers": DISCLAIMERS,
        "compliance": COMPLIANCE,
        "features": FEATURE_FLAGS,
        "performance": PERFORMANCE_TRACKING,
        "logging": LOGGING_CONFIG
    }
    
    if section:
        return all_config.get(section, {})
    return all_config


def get_disclaimer(disclaimer_type: str = "investment") -> str:
    """
    Get specific disclaimer text
    
    Args:
        disclaimer_type: Type of disclaimer (investment, data, ai, risk)
        
    Returns:
        Disclaimer text
    """
    key = f"{disclaimer_type}_disclaimer"
    return DISCLAIMERS.get(key, "")
