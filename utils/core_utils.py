"""
Core Utilities - Essential utilities only
Phase 2: Consolidates performance.py + security.py + auth.py (essential parts only)
"""

import time
import hashlib
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)

class SimplePerformanceMonitor:
    """Simplified performance monitoring"""
    
    def __init__(self):
        self.metrics = {}
    
    def start_timer(self, operation: str) -> str:
        """Start timing an operation"""
        timer_id = f"{operation}_{int(time.time() * 1000)}"
        self.metrics[timer_id] = {"start": time.time(), "operation": operation}
        return timer_id
    
    def end_timer(self, timer_id: str) -> float:
        """End timing and return duration"""
        if timer_id in self.metrics:
            duration = time.time() - self.metrics[timer_id]["start"]
            self.metrics[timer_id]["duration"] = duration
            return duration
        return 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get basic performance statistics"""
        completed_operations = [m for m in self.metrics.values() if "duration" in m]
        
        if not completed_operations:
            return {"operations": 0, "average_time": 0}
        
        avg_time = sum(op["duration"] for op in completed_operations) / len(completed_operations)
        
        return {
            "operations": len(completed_operations),
            "average_time": round(avg_time, 3),
            "last_updated": datetime.utcnow().isoformat()
        }

def performance_monitor(func):
    """Simple performance monitoring decorator"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"{func.__name__} completed in {duration:.3f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{func.__name__} failed after {duration:.3f}s: {e}")
            raise
    return wrapper

class SimpleSecurityUtils:
    """Essential security utilities"""
    
    @staticmethod
    def hash_text(text: str, salt: str = "") -> str:
        """Simple text hashing"""
        combined = f"{text}{salt}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    @staticmethod
    def validate_input(text: str, max_length: int = 1000) -> bool:
        """Basic input validation"""
        if not text or len(text.strip()) == 0:
            return False
        
        if len(text) > max_length:
            return False
        
        # Basic XSS prevention
        dangerous_patterns = ['<script', 'javascript:', 'onclick=', 'onerror=']
        text_lower = text.lower()
        
        return not any(pattern in text_lower for pattern in dangerous_patterns)
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        import re
        # Remove dangerous characters
        safe_name = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        # Limit length
        return safe_name[:100]
    
    @staticmethod
    def generate_simple_token() -> str:
        """Generate simple token for sessions"""
        import secrets
        return secrets.token_urlsafe(32)

class SimpleRateLimiter:
    """Basic rate limiting"""
    
    def __init__(self, max_requests: int = 100, time_window: int = 3600):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = {}
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed"""
        now = datetime.utcnow()
        
        # Clean old requests
        cutoff = now - timedelta(seconds=self.time_window)
        if identifier in self.requests:
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier] 
                if req_time > cutoff
            ]
        
        # Check current count
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        if len(self.requests[identifier]) >= self.max_requests:
            return False
        
        # Add current request
        self.requests[identifier].append(now)
        return True

def validate_api_key(api_key: str) -> bool:
    """Simple API key validation"""
    if not api_key or len(api_key) < 10:
        return False
    
    # Check against environment variable
    expected_key = os.getenv("OPENAI_API_KEY", "")
    return api_key == expected_key

def log_operation(operation: str, details: Dict[str, Any] = None):
    """Simple operation logging"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "operation": operation,
        "details": details or {}
    }
    logger.info(f"Operation: {operation} | Details: {details}")

# Health check utilities
def get_system_health() -> Dict[str, Any]:
    """Simple system health check"""
    import psutil
    
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "cpu_usage": cpu_percent,
            "memory_usage": memory.percent,
            "disk_usage": disk.percent,
            "available_memory_mb": round(memory.available / 1024 / 1024, 2)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

# Configuration utilities
def get_simple_config() -> Dict[str, Any]:
    """Get simplified configuration"""
    return {
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "database_configured": bool(os.getenv("DATABASE_URL")),
        "environment": os.getenv("FLASK_ENV", "production"),
        "debug_mode": os.getenv("FLASK_ENV") == "development"
    }

# Backward compatibility
performance_monitor_instance = SimplePerformanceMonitor()
security_utils = SimpleSecurityUtils()
rate_limiter = SimpleRateLimiter()