"""
Environment configuration management for Echo AI Dashboard
Handles loading and validation of environment variables
"""
from __future__ import annotations
import os
from typing import Optional
from pathlib import Path


class Config:
    """Centralized configuration management"""
    
    def __init__(self):
        self.load_env()
    
    def load_env(self):
        """Load environment variables from .env file if it exists"""
        env_path = Path(__file__).parent.parent.parent / '.env'
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        if key and not key in os.environ:
                            os.environ[key] = value
    
    @staticmethod
    def get(key: str, default: Optional[str] = None) -> Optional[str]:
        """Get configuration value from environment"""
        return os.environ.get(key, default)
    
    @staticmethod
    def get_int(key: str, default: int = 0) -> int:
        """Get integer configuration value"""
        try:
            return int(os.environ.get(key, default))
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def get_bool(key: str, default: bool = False) -> bool:
        """Get boolean configuration value"""
        value = os.environ.get(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    @staticmethod
    def get_float(key: str, default: float = 0.0) -> float:
        """Get float configuration value"""
        try:
            return float(os.environ.get(key, default))
        except (ValueError, TypeError):
            return default
    
    # Application Settings
    @property
    def app_env(self) -> str:
        return self.get('APP_ENV', 'development')
    
    @property
    def debug(self) -> bool:
        return self.get_bool('DEBUG', False)
    
    @property
    def log_level(self) -> str:
        return self.get('LOG_LEVEL', 'INFO')
    
    # Security
    @property
    def password_hash(self) -> Optional[str]:
        return self.get('PASSWORD_HASH')
    
    # Data Provider API Keys
    @property
    def alpha_vantage_api_key(self) -> Optional[str]:
        return self.get('ALPHA_VANTAGE_API_KEY')
    
    @property
    def quandl_api_key(self) -> Optional[str]:
        return self.get('QUANDL_API_KEY')
    
    @property
    def news_api_key(self) -> Optional[str]:
        return self.get('NEWS_API_KEY')
    
    @property
    def finbert_model_path(self) -> str:
        return self.get('FINBERT_MODEL_PATH', 'ProsusAI/finbert')
    
    # Cache Configuration
    @property
    def cache_ttl_seconds(self) -> int:
        return self.get_int('CACHE_TTL_SECONDS', 300)
    
    @property
    def redis_host(self) -> str:
        return self.get('REDIS_HOST', 'localhost')
    
    @property
    def redis_port(self) -> int:
        return self.get_int('REDIS_PORT', 6379)
    
    # Trading Configuration
    @property
    def default_timezone(self) -> str:
        return self.get('DEFAULT_TIMEZONE', 'America/Chicago')
    
    @property
    def enable_backtesting(self) -> bool:
        return self.get_bool('ENABLE_BACKTESTING', True)
    
    @property
    def enable_ml_predictions(self) -> bool:
        return self.get_bool('ENABLE_ML_PREDICTIONS', True)
    
    @property
    def enable_sentiment_analysis(self) -> bool:
        return self.get_bool('ENABLE_SENTIMENT_ANALYSIS', True)


# Global config instance
config = Config()
