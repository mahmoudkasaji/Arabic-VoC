"""
Consolidated Performance Management
Combines functionality from performance.py, performance_monitor.py, and dashboard_performance.py
"""

import asyncio
import time
import functools
import hashlib
import psutil
import logging
from typing import Dict, List, Optional, Any, Callable
from collections import OrderedDict
from datetime import datetime, timedelta
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Unified performance metrics structure"""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Response times
    api_response_time: float = 0.0
    websocket_latency: float = 0.0
    database_query_time: float = 0.0
    nlp_processing_time: float = 0.0
    
    # System metrics
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    memory_mb: float = 0.0
    
    # Dashboard metrics
    dashboard_load_time: float = 0.0
    chart_render_time: float = 0.0
    
    # Arabic-specific metrics
    arabic_text_processing_rate: float = 0.0
    rtl_render_performance: float = 0.0
    
    # Connection metrics
    active_connections: int = 0
    failed_connections: int = 0

class LRUCache:
    """Thread-safe LRU Cache for performance optimization"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache = OrderedDict()
        self.stats = {"hits": 0, "misses": 0}
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        if key in self.cache:
            self.cache.move_to_end(key)
            self.stats["hits"] += 1
            return self.cache[key]
        
        self.stats["misses"] += 1
        return None
    
    def put(self, key: str, value: Any) -> None:
        """Put item in cache"""
        if key in self.cache:
            self.cache[key] = value
            self.cache.move_to_end(key)
        else:
            if len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)
            self.cache[key] = value
    
    def clear(self) -> None:
        """Clear cache"""
        self.cache.clear()
        self.stats = {"hits": 0, "misses": 0}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total if total > 0 else 0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": hit_rate
        }

class ArabicTextCache:
    """Specialized cache for Arabic text processing results"""
    
    def __init__(self, max_size: int = 500):
        self.normalization_cache = LRUCache(max_size)
        self.sentiment_cache = LRUCache(max_size)
        self.reshaping_cache = LRUCache(max_size)
    
    def _hash_text(self, text: str) -> str:
        """Generate hash for text caching"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def get_normalized(self, text: str) -> Optional[str]:
        """Get cached normalized text"""
        return self.normalization_cache.get(self._hash_text(text))
    
    def cache_normalized(self, text: str, normalized: str) -> None:
        """Cache normalized text"""
        self.normalization_cache.put(self._hash_text(text), normalized)
    
    def get_sentiment(self, text: str) -> Optional[Dict[str, Any]]:
        """Get cached sentiment analysis"""
        return self.sentiment_cache.get(self._hash_text(text))
    
    def cache_sentiment(self, text: str, sentiment: Dict[str, Any]) -> None:
        """Cache sentiment analysis result"""
        self.sentiment_cache.put(self._hash_text(text), sentiment)

class PerformanceMonitor:
    """Unified performance monitoring and optimization"""
    
    def __init__(self):
        self.metrics_history: List[PerformanceMetrics] = []
        self.current_metrics = PerformanceMetrics()
        self.monitoring_active = False
        self.start_time = time.time()
        
        # Request tracking
        self.requests = []
        self.errors = []
        self.slow_requests = []
        
        # Alert thresholds
        self.alert_thresholds = {
            "api_response_time": 1.0,
            "websocket_latency": 0.1,
            "dashboard_load_time": 2.0,
            "memory_usage": 80.0,
            "cpu_usage": 85.0
        }
        
        # Performance targets
        self.performance_targets = {
            "dashboard_load_time": 1.0,
            "api_response_time": 0.5,
            "websocket_latency": 0.05,
            "arabic_processing_rate": 20.0
        }
    
    def track_request(self, endpoint: str, duration: float, status_code: int):
        """Track individual request performance"""
        request_data = {
            "timestamp": datetime.now(),
            "endpoint": endpoint,
            "duration": duration,
            "status_code": status_code
        }
        
        self.requests.append(request_data)
        
        if status_code >= 400:
            self.errors.append(request_data)
        
        if duration > 2.0:
            self.slow_requests.append(request_data)
        
        # Keep only recent records
        self._cleanup_old_records()
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system performance statistics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            stats = {
                "timestamp": datetime.now(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available / 1024 / 1024,
                "uptime_hours": (time.time() - self.start_time) / 3600
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {"error": str(e)}
    
    async def collect_metrics(self):
        """Collect comprehensive performance metrics"""
        metrics = PerformanceMetrics()
        
        # System metrics
        system_stats = self.get_system_stats()
        if "error" not in system_stats:
            metrics.cpu_usage = system_stats["cpu_percent"]
            metrics.memory_usage = system_stats["memory_percent"]
            metrics.memory_mb = system_stats["memory_available_mb"]
        
        # Request metrics
        if self.requests:
            recent_requests = [r for r in self.requests 
                             if (datetime.now() - r["timestamp"]).seconds < 300]
            if recent_requests:
                avg_response_time = sum(r["duration"] for r in recent_requests) / len(recent_requests)
                metrics.api_response_time = avg_response_time
        
        self.current_metrics = metrics
        self.metrics_history.append(metrics)
        
        # Keep only last 100 metrics
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-100:]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        if not self.requests:
            return {"message": "No performance data available"}
        
        # Calculate averages
        recent_requests = [r for r in self.requests 
                          if (datetime.now() - r["timestamp"]).seconds < 3600]
        
        if not recent_requests:
            return {"message": "No recent performance data"}
        
        avg_response_time = sum(r["duration"] for r in recent_requests) / len(recent_requests)
        error_rate = len([r for r in recent_requests if r["status_code"] >= 400]) / len(recent_requests)
        slow_request_rate = len([r for r in recent_requests if r["duration"] > 2.0]) / len(recent_requests)
        
        system_stats = self.get_system_stats()
        
        return {
            "summary": {
                "avg_response_time": avg_response_time,
                "error_rate": error_rate * 100,
                "slow_request_rate": slow_request_rate * 100,
                "total_requests_last_hour": len(recent_requests)
            },
            "system": system_stats,
            "alerts": self._check_alerts(),
            "cache_stats": self._get_cache_summary() if hasattr(self, 'text_cache') else {}
        }
    
    def _cleanup_old_records(self):
        """Clean up old performance records"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        self.requests = [r for r in self.requests if r["timestamp"] > cutoff_time]
        self.errors = [r for r in self.errors if r["timestamp"] > cutoff_time]
        self.slow_requests = [r for r in self.slow_requests if r["timestamp"] > cutoff_time]
    
    def _check_alerts(self) -> List[Dict[str, Any]]:
        """Check for performance alerts"""
        alerts = []
        
        if hasattr(self, 'current_metrics'):
            metrics = self.current_metrics
            
            if metrics.api_response_time > self.alert_thresholds["api_response_time"]:
                alerts.append({
                    "type": "slow_api",
                    "message": f"API response time ({metrics.api_response_time:.2f}s) exceeds threshold",
                    "severity": "warning"
                })
            
            if metrics.memory_usage > self.alert_thresholds["memory_usage"]:
                alerts.append({
                    "type": "high_memory",
                    "message": f"Memory usage ({metrics.memory_usage:.1f}%) exceeds threshold",
                    "severity": "critical"
                })
            
            if metrics.cpu_usage > self.alert_thresholds["cpu_usage"]:
                alerts.append({
                    "type": "high_cpu",
                    "message": f"CPU usage ({metrics.cpu_usage:.1f}%) exceeds threshold",
                    "severity": "warning"
                })
        
        return alerts
    
    def _get_cache_summary(self) -> Dict[str, Any]:
        """Get cache performance summary"""
        if hasattr(self, 'text_cache'):
            return {
                "normalization": self.text_cache.normalization_cache.get_stats(),
                "sentiment": self.text_cache.sentiment_cache.get_stats(),
                "reshaping": self.text_cache.reshaping_cache.get_stats()
            }
        return {}

def performance_timer(func):
    """Decorator to measure function execution time"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        
        logger.debug(f"{func.__name__} executed in {duration:.4f} seconds")
        return result
    return wrapper

def async_performance_timer(func):
    """Decorator to measure async function execution time"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start_time
        
        logger.debug(f"{func.__name__} executed in {duration:.4f} seconds")
        return result
    return wrapper

# Singleton instances
performance_monitor = PerformanceMonitor()
arabic_text_cache = ArabicTextCache()