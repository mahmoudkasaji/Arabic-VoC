"""
Dashboard performance optimization and monitoring utilities
Real-time metrics collection and performance tracking
"""

import asyncio
import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import psutil
import os

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
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
    data_update_frequency: float = 0.0
    
    # Arabic-specific metrics
    arabic_text_processing_rate: float = 0.0
    rtl_render_performance: float = 0.0
    font_load_time: float = 0.0
    
    # Connection metrics
    active_websocket_connections: int = 0
    failed_connections: int = 0
    reconnection_attempts: int = 0

class PerformanceMonitor:
    """Real-time performance monitoring for Arabic dashboard"""
    
    def __init__(self):
        self.metrics_history: List[PerformanceMetrics] = []
        self.current_metrics = PerformanceMetrics()
        self.monitoring_active = False
        self.alert_thresholds = {
            "api_response_time": 1.0,  # 1 second
            "websocket_latency": 0.1,  # 100ms
            "dashboard_load_time": 2.0,  # 2 seconds
            "memory_usage": 80.0,  # 80%
            "cpu_usage": 85.0  # 85%
        }
        self.performance_targets = {
            "dashboard_load_time": 1.0,  # Target: <1s
            "api_response_time": 0.5,   # Target: <500ms
            "websocket_latency": 0.05,  # Target: <50ms
            "arabic_processing_rate": 20.0  # Target: >20 texts/sec
        }
    
    async def start_monitoring(self, interval: float = 5.0):
        """Start continuous performance monitoring"""
        self.monitoring_active = True
        
        while self.monitoring_active:
            try:
                await self.collect_metrics()
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(interval)
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
    
    async def collect_metrics(self):
        """Collect current performance metrics"""
        metrics = PerformanceMetrics()
        
        # System metrics
        metrics.cpu_usage = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()
        metrics.memory_usage = memory_info.percent
        metrics.memory_mb = memory_info.used / 1024 / 1024
        
        # Store metrics
        self.current_metrics = metrics
        self.metrics_history.append(metrics)
        
        # Keep only last 1000 measurements
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
        
        # Check for alerts
        await self.check_performance_alerts(metrics)
    
    async def measure_api_response_time(self, func, *args, **kwargs):
        """Measure API response time"""
        start_time = time.time()
        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            end_time = time.time()
            
            response_time = end_time - start_time
            self.current_metrics.api_response_time = response_time
            
            return result
        except Exception as e:
            end_time = time.time()
            self.current_metrics.api_response_time = end_time - start_time
            raise e
    
    def measure_websocket_latency(self, start_timestamp: float):
        """Measure WebSocket message latency"""
        latency = time.time() - start_timestamp
        self.current_metrics.websocket_latency = latency
        return latency
    
    async def measure_database_query_time(self, query_func, *args, **kwargs):
        """Measure database query execution time"""
        start_time = time.time()
        try:
            result = await query_func(*args, **kwargs)
            end_time = time.time()
            
            query_time = end_time - start_time
            self.current_metrics.database_query_time = query_time
            
            return result
        except Exception as e:
            end_time = time.time()
            self.current_metrics.database_query_time = end_time - start_time
            raise e
    
    def measure_arabic_processing_performance(self, text_count: int, processing_time: float):
        """Measure Arabic text processing performance"""
        if processing_time > 0:
            processing_rate = text_count / processing_time
            self.current_metrics.arabic_text_processing_rate = processing_rate
    
    def record_dashboard_load_time(self, load_time: float):
        """Record dashboard load time"""
        self.current_metrics.dashboard_load_time = load_time
    
    def record_chart_render_time(self, render_time: float):
        """Record chart rendering time"""
        self.current_metrics.chart_render_time = render_time
    
    def record_websocket_connection(self, connected: bool, failed: bool = False):
        """Record WebSocket connection events"""
        if connected:
            self.current_metrics.active_websocket_connections += 1
        else:
            self.current_metrics.active_websocket_connections = max(0, self.current_metrics.active_websocket_connections - 1)
        
        if failed:
            self.current_metrics.failed_connections += 1
    
    async def check_performance_alerts(self, metrics: PerformanceMetrics):
        """Check for performance threshold violations"""
        alerts = []
        
        for metric_name, threshold in self.alert_thresholds.items():
            current_value = getattr(metrics, metric_name, 0)
            
            if current_value > threshold:
                alerts.append({
                    "metric": metric_name,
                    "current_value": current_value,
                    "threshold": threshold,
                    "severity": "warning" if current_value < threshold * 1.2 else "critical"
                })
        
        if alerts:
            await self.handle_performance_alerts(alerts)
    
    async def handle_performance_alerts(self, alerts: List[Dict]):
        """Handle performance alerts"""
        for alert in alerts:
            logger.warning(
                f"Performance alert: {alert['metric']} = {alert['current_value']:.3f} "
                f"(threshold: {alert['threshold']}) - {alert['severity']}"
            )
    
    def get_performance_summary(self, time_window: timedelta = timedelta(minutes=15)) -> Dict[str, Any]:
        """Get performance summary for specified time window"""
        cutoff_time = datetime.utcnow() - time_window
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        
        if not recent_metrics:
            return {"error": "No metrics available for the specified time window"}
        
        summary = {
            "time_window_minutes": time_window.total_seconds() / 60,
            "metrics_count": len(recent_metrics),
            "averages": {},
            "maximums": {},
            "targets_met": {},
            "performance_score": 0.0
        }
        
        # Calculate averages and maximums
        metrics_to_analyze = [
            "api_response_time", "websocket_latency", "database_query_time",
            "dashboard_load_time", "cpu_usage", "memory_usage",
            "arabic_text_processing_rate"
        ]
        
        for metric_name in metrics_to_analyze:
            values = [getattr(m, metric_name) for m in recent_metrics if getattr(m, metric_name) > 0]
            
            if values:
                summary["averages"][metric_name] = sum(values) / len(values)
                summary["maximums"][metric_name] = max(values)
                
                # Check if targets are met
                if metric_name in self.performance_targets:
                    target = self.performance_targets[metric_name]
                    avg_value = summary["averages"][metric_name]
                    
                    if metric_name == "arabic_text_processing_rate":
                        summary["targets_met"][metric_name] = avg_value >= target
                    else:
                        summary["targets_met"][metric_name] = avg_value <= target
        
        # Calculate overall performance score (0-100)
        targets_met = list(summary["targets_met"].values())
        summary["performance_score"] = (sum(targets_met) / len(targets_met) * 100) if targets_met else 0
        
        return summary
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get current real-time metrics"""
        return {
            "timestamp": self.current_metrics.timestamp.isoformat(),
            "api_response_time": self.current_metrics.api_response_time,
            "websocket_latency": self.current_metrics.websocket_latency,
            "database_query_time": self.current_metrics.database_query_time,
            "dashboard_load_time": self.current_metrics.dashboard_load_time,
            "cpu_usage": self.current_metrics.cpu_usage,
            "memory_usage": self.current_metrics.memory_usage,
            "memory_mb": self.current_metrics.memory_mb,
            "arabic_processing_rate": self.current_metrics.arabic_text_processing_rate,
            "active_connections": self.current_metrics.active_websocket_connections,
            "performance_targets": self.performance_targets,
            "targets_status": {
                metric: "✓" if (
                    getattr(self.current_metrics, metric) <= target if metric != "arabic_text_processing_rate"
                    else getattr(self.current_metrics, metric) >= target
                ) else "✗"
                for metric, target in self.performance_targets.items()
            }
        }

class ArabicDashboardOptimizer:
    """Optimization utilities for Arabic dashboard performance"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = {}
        self.optimization_settings = {
            "cache_duration": 300,  # 5 minutes
            "max_cache_size": 1000,
            "batch_size": 50,
            "compression_enabled": True
        }
    
    async def optimize_arabic_text_rendering(self, texts: List[str]) -> List[str]:
        """Optimize Arabic text for faster rendering"""
        optimized_texts = []
        
        for text in texts:
            # Normalize Arabic text for consistent rendering
            optimized_text = self._normalize_for_rendering(text)
            
            # Truncate very long texts for dashboard display
            if len(optimized_text) > 200:
                optimized_text = optimized_text[:197] + "..."
            
            optimized_texts.append(optimized_text)
        
        return optimized_texts
    
    def _normalize_for_rendering(self, text: str) -> str:
        """Normalize Arabic text for optimal rendering performance"""
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Normalize common Arabic character variations
        text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        text = text.replace('ة', 'ه').replace('ى', 'ي')
        
        return text
    
    async def cache_dashboard_data(self, key: str, data: Any, ttl: int = None):
        """Cache dashboard data with TTL"""
        ttl = ttl or self.optimization_settings["cache_duration"]
        
        self.cache[key] = data
        self.cache_ttl[key] = time.time() + ttl
        
        # Clean expired cache entries
        await self._cleanup_cache()
    
    async def get_cached_data(self, key: str) -> Optional[Any]:
        """Get cached dashboard data"""
        if key in self.cache:
            if time.time() < self.cache_ttl.get(key, 0):
                return self.cache[key]
            else:
                # Remove expired entry
                del self.cache[key]
                if key in self.cache_ttl:
                    del self.cache_ttl[key]
        
        return None
    
    async def _cleanup_cache(self):
        """Clean up expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, expiry_time in self.cache_ttl.items()
            if current_time >= expiry_time
        ]
        
        for key in expired_keys:
            if key in self.cache:
                del self.cache[key]
            del self.cache_ttl[key]
        
        # Limit cache size
        if len(self.cache) > self.optimization_settings["max_cache_size"]:
            # Remove oldest entries
            sorted_items = sorted(self.cache_ttl.items(), key=lambda x: x[1])
            items_to_remove = len(self.cache) - self.optimization_settings["max_cache_size"]
            
            for key, _ in sorted_items[:items_to_remove]:
                if key in self.cache:
                    del self.cache[key]
                del self.cache_ttl[key]
    
    async def batch_process_arabic_data(self, data_items: List[Any], processor_func) -> List[Any]:
        """Process Arabic data in optimized batches"""
        batch_size = self.optimization_settings["batch_size"]
        results = []
        
        for i in range(0, len(data_items), batch_size):
            batch = data_items[i:i + batch_size]
            
            try:
                if asyncio.iscoroutinefunction(processor_func):
                    batch_results = await processor_func(batch)
                else:
                    batch_results = processor_func(batch)
                
                results.extend(batch_results)
                
                # Small delay to prevent overwhelming the system
                if i + batch_size < len(data_items):
                    await asyncio.sleep(0.01)
                    
            except Exception as e:
                logger.error(f"Error processing batch {i//batch_size + 1}: {e}")
                # Continue with next batch
                continue
        
        return results
    
    def optimize_chart_data(self, data: List[Dict], max_points: int = 100) -> List[Dict]:
        """Optimize chart data for better rendering performance"""
        if len(data) <= max_points:
            return data
        
        # Sample data points evenly
        step = len(data) // max_points
        optimized_data = []
        
        for i in range(0, len(data), step):
            if len(optimized_data) < max_points:
                optimized_data.append(data[i])
        
        return optimized_data
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics"""
        current_time = time.time()
        active_cache_entries = sum(
            1 for expiry_time in self.cache_ttl.values()
            if current_time < expiry_time
        )
        
        return {
            "cache_size": len(self.cache),
            "active_cache_entries": active_cache_entries,
            "cache_hit_ratio": getattr(self, '_cache_hits', 0) / max(getattr(self, '_cache_requests', 1), 1),
            "optimization_settings": self.optimization_settings,
            "memory_usage_kb": sum(
                len(str(data).encode('utf-8')) for data in self.cache.values()
            ) / 1024
        }

# Global instances
performance_monitor = PerformanceMonitor()
dashboard_optimizer = ArabicDashboardOptimizer()

async def start_performance_monitoring():
    """Start the global performance monitoring"""
    await performance_monitor.start_monitoring()

def get_performance_metrics():
    """Get current performance metrics"""
    return performance_monitor.get_real_time_metrics()

def get_performance_summary(minutes: int = 15):
    """Get performance summary for the last N minutes"""
    return performance_monitor.get_performance_summary(timedelta(minutes=minutes))