
"""
Performance Monitoring Utility
Tracks system performance and provides insights
"""

import time
import logging
import psutil
from typing import Dict, Any, List
from datetime import datetime, timedelta
from functools import wraps

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor system performance and generate insights"""
    
    def __init__(self):
        self.metrics = {
            "requests": [],
            "errors": [],
            "slow_requests": [],
            "system_stats": []
        }
        self.start_time = time.time()
    
    def track_request(self, endpoint: str, duration: float, status_code: int):
        """Track individual request performance"""
        request_data = {
            "timestamp": datetime.now(),
            "endpoint": endpoint,
            "duration": duration,
            "status_code": status_code
        }
        
        self.metrics["requests"].append(request_data)
        
        # Track errors
        if status_code >= 400:
            self.metrics["errors"].append(request_data)
        
        # Track slow requests (> 2 seconds)
        if duration > 2.0:
            self.metrics["slow_requests"].append(request_data)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system performance statistics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            stats = {
                "timestamp": datetime.now(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available / 1024 / 1024,
                "disk_percent": disk.percent,
                "uptime_hours": (time.time() - self.start_time) / 3600
            }
            
            self.metrics["system_stats"].append(stats)
            
            # Keep only last 100 records
            if len(self.metrics["system_stats"]) > 100:
                self.metrics["system_stats"] = self.metrics["system_stats"][-100:]
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {"error": str(e)}
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Generate performance summary for non-technical users"""
        
        try:
            # Calculate request statistics
            recent_requests = [r for r in self.metrics["requests"] 
                             if r["timestamp"] > datetime.now() - timedelta(hours=1)]
            
            if not recent_requests:
                return {
                    "status": "نظام جديد - لا توجد بيانات كافية",
                    "health": "جيد",
                    "recommendations": []
                }
            
            avg_response_time = sum(r["duration"] for r in recent_requests) / len(recent_requests)
            error_rate = len([r for r in recent_requests if r["status_code"] >= 400]) / len(recent_requests)
            slow_request_rate = len([r for r in recent_requests if r["duration"] > 2.0]) / len(recent_requests)
            
            # System health assessment
            latest_system = self.metrics["system_stats"][-1] if self.metrics["system_stats"] else {}
            cpu_usage = latest_system.get("cpu_percent", 0)
            memory_usage = latest_system.get("memory_percent", 0)
            
            # Determine overall health
            health_score = 100
            recommendations = []
            
            if avg_response_time > 3.0:
                health_score -= 20
                recommendations.append("سرعة الاستجابة بطيئة - يحتاج تحسين")
            
            if error_rate > 0.05:  # More than 5% errors
                health_score -= 25
                recommendations.append("معدل الأخطاء مرتفع - يحتاج متابعة")
            
            if cpu_usage > 80:
                health_score -= 15
                recommendations.append("استخدام المعالج مرتفع")
            
            if memory_usage > 85:
                health_score -= 15
                recommendations.append("استخدام الذاكرة مرتفع")
            
            # Health status in Arabic
            if health_score >= 90:
                health_status = "ممتاز 🟢"
            elif health_score >= 70:
                health_status = "جيد 🟡"
            elif health_score >= 50:
                health_status = "يحتاج تحسين 🟠"
            else:
                health_status = "يحتاج تدخل عاجل 🔴"
            
            return {
                "health_status": health_status,
                "health_score": health_score,
                "avg_response_time": f"{avg_response_time:.2f} ثانية",
                "requests_per_hour": len(recent_requests),
                "error_rate_percent": f"{error_rate * 100:.1f}%",
                "cpu_usage": f"{cpu_usage:.1f}%",
                "memory_usage": f"{memory_usage:.1f}%",
                "recommendations": recommendations,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"Error generating performance summary: {e}")
            return {
                "health_status": "خطأ في النظام 🔴",
                "error": str(e),
                "recommendations": ["اتصل بالدعم الفني"]
            }

# Global monitor instance
monitor = PerformanceMonitor()

def track_performance(func):
    """Decorator to track function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            monitor.track_request(func.__name__, duration, 200)
            return result
        except Exception as e:
            duration = time.time() - start_time
            monitor.track_request(func.__name__, duration, 500)
            raise e
    return wrapper

def get_performance_summary():
    """Get performance summary for dashboard"""
    return monitor.get_performance_summary()

def get_system_health():
    """Get current system health"""
    return monitor.get_system_stats()
