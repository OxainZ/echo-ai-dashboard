"""
Data caching utilities for Echo AI Dashboard
Implements memory and file-based caching with TTL support
"""
from __future__ import annotations
from typing import Any, Optional, Callable
from functools import wraps
import pickle
import time
import hashlib
from pathlib import Path
from ..utils.logging import get_logger
from ..utils.config import config

log = get_logger("DataCache")


class CacheManager:
    """Simple in-memory cache with TTL and optional file persistence"""
    
    def __init__(self, cache_dir: Optional[str] = None, default_ttl: int = 300):
        self.cache_dir = Path(cache_dir) if cache_dir else Path("data/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.memory_cache = {}
        self.default_ttl = default_ttl or config.cache_ttl_seconds
        self.enabled = True
    
    def _generate_key(self, func_name: str, *args, **kwargs) -> str:
        """Generate cache key from function name and arguments"""
        key_data = f"{func_name}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if not self.enabled:
            return None
        
        # Check memory cache first
        if key in self.memory_cache:
            data, expiry = self.memory_cache[key]
            if time.time() < expiry:
                log.debug(f"Cache hit (memory): {key}")
                return data
            else:
                del self.memory_cache[key]
        
        # Check file cache
        cache_file = self.cache_dir / f"{key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    data, expiry = pickle.load(f)
                if time.time() < expiry:
                    log.debug(f"Cache hit (file): {key}")
                    # Promote to memory cache
                    self.memory_cache[key] = (data, expiry)
                    return data
                else:
                    cache_file.unlink()
            except Exception as e:
                log.warning(f"Error reading cache file {key}: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL"""
        if not self.enabled:
            return
        
        ttl = ttl or self.default_ttl
        expiry = time.time() + ttl
        
        # Store in memory cache
        self.memory_cache[key] = (value, expiry)
        
        # Also persist to file cache for larger items
        try:
            cache_file = self.cache_dir / f"{key}.pkl"
            with open(cache_file, 'wb') as f:
                pickle.dump((value, expiry), f)
        except Exception as e:
            log.warning(f"Error writing cache file {key}: {e}")
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self.memory_cache.clear()
        for cache_file in self.cache_dir.glob("*.pkl"):
            try:
                cache_file.unlink()
            except Exception as e:
                log.warning(f"Error deleting cache file {cache_file}: {e}")
        log.info("Cache cleared")
    
    def invalidate(self, key: str) -> None:
        """Invalidate specific cache entry"""
        if key in self.memory_cache:
            del self.memory_cache[key]
        
        cache_file = self.cache_dir / f"{key}.pkl"
        if cache_file.exists():
            cache_file.unlink()


# Global cache manager instance
cache_manager = CacheManager()


def cached(ttl: Optional[int] = None):
    """
    Decorator to cache function results
    
    Usage:
        @cached(ttl=300)
        def expensive_function(arg1, arg2):
            # ... expensive computation
            return result
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_manager._generate_key(func.__name__, *args, **kwargs)
            
            # Try to get from cache
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator
