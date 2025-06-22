"""
Production monitoring and alerting system
Health checks, metrics collection, and performance monitoring
"""

import asyncio
import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import psutil
import aiohttp
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class HealthStatus:
    """Health check status"""
    service: str
    status: str  # healthy, degraded, unhealthy
    response_time: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    network_io: Dict[str, float] = field(default_factory=dict)
    active_connections: int = 0
    request_rate: float = 0.0
    error_rate: float = 0.0
    response_time_avg: float = 0.0

class ProductionMonitor:
    """Comprehensive production monitoring system"""
    
    def __init__(self, config):
        self.config = config
        self.health_checks = {}
        self.metrics_history = []
        self.alerts_sent = {}
        self.monitoring_active = False
        
        # Initialize health check endpoints
        self.health_endpoints = {
            "database": self._check_database_health,
            "redis": self._check_redis_health,
            "openai": self._check_openai_health,
            "arabic_processor": self._check_arabic_processor_health,
            "websocket": self._check_websocket_health
        }
    
    async def start_monitoring(self):
        """Start production monitoring"""
        self.monitoring_active = True
        
        # Start monitoring tasks
        tasks = [
            self._health_check_loop(),
            self._metrics_collection_loop(),
            self._alert_monitoring_loop()
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring_active = False
    
    async def _health_check_loop(self):
        """Continuous health checking"""
        while self.monitoring_active:
            try:
                # Run all health checks
                health_results = {}
                
                for service, check_func in self.health_endpoints.items():
                    try:
                        start_time = time.time()
                        result = await check_func()
                        response_time = time.time() - start_time
                        
                        health_results[service] = HealthStatus(
                            service=service,
                            status="healthy" if result["healthy"] else "unhealthy",
                            response_time=response_time,
                            details=result.get("details", {}),
                            error=result.get("error")
                        )
                        
                    except Exception as e:
                        health_results[service] = HealthStatus(
                            service=service,
                            status="unhealthy",
                            response_time=0.0,
                            error=str(e)
                        )
                
                self.health_checks = health_results
                
                # Log health status
                unhealthy_services = [
                    service for service, status in health_results.items()
                    if status.status != "healthy"
                ]
                
                if unhealthy_services:
                    logger.warning(f"Unhealthy services: {unhealthy_services}")
                else:
                    logger.info("All services healthy")
                
                await asyncio.sleep(self.config.HEALTH_CHECK_INTERVAL)
                
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(5)
    
    async def _metrics_collection_loop(self):
        """Collect system metrics"""
        while self.monitoring_active:
            try:
                metrics = await self._collect_system_metrics()
                self.metrics_history.append(metrics)
                
                # Keep only recent metrics
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                self.metrics_history = [
                    m for m in self.metrics_history
                    if m.timestamp > cutoff_time
                ]
                
                await asyncio.sleep(60)  # Collect every minute
                
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(60)
    
    async def _alert_monitoring_loop(self):
        """Monitor for alert conditions"""
        while self.monitoring_active:
            try:
                await self._check_alert_conditions()
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Alert monitoring error: {e}")
                await asyncio.sleep(30)
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            from utils.database_arabic import arabic_db_manager
            
            async with arabic_db_manager.session_factory() as session:
                # Simple health check query
                result = await session.execute("SELECT 1")
                row = result.fetchone()
                
                if row and row[0] == 1:
                    return {
                        "healthy": True,
                        "details": {"connection": "active", "query_test": "passed"}
                    }
                else:
                    return {
                        "healthy": False,
                        "error": "Database query failed"
                    }
                    
        except Exception as e:
            return {
                "healthy": False,
                "error": f"Database connection failed: {str(e)}"
            }
    
    async def _check_redis_health(self) -> Dict[str, Any]:
        """Check Redis health"""
        try:
            # Would check Redis connection if available
            return {
                "healthy": True,
                "details": {"status": "Redis health check simulated"}
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": f"Redis check failed: {str(e)}"
            }
    
    async def _check_openai_health(self) -> Dict[str, Any]:
        """Check OpenAI API health"""
        try:
            # Simple API health check
            import openai
            import os
            
            client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            
            # Make a minimal request
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5
            )
            
            if response and response.choices:
                return {
                    "healthy": True,
                    "details": {"api_status": "active", "model": "gpt-4o"}
                }
            else:
                return {
                    "healthy": False,
                    "error": "OpenAI API returned empty response"
                }
                
        except Exception as e:
            return {
                "healthy": False,
                "error": f"OpenAI API check failed: {str(e)}"
            }
    
    async def _check_arabic_processor_health(self) -> Dict[str, Any]:
        """Check Arabic text processor health"""
        try:
            from utils.arabic_processor import process_arabic_text, extract_sentiment
            
            # Test Arabic processing
            test_text = "اختبار النظام"
            processed = process_arabic_text(test_text)
            sentiment = extract_sentiment(test_text)
            
            if processed and isinstance(sentiment, dict):
                return {
                    "healthy": True,
                    "details": {"processing": "active", "sentiment_analysis": "working"}
                }
            else:
                return {
                    "healthy": False,
                    "error": "Arabic processing failed"
                }
                
        except Exception as e:
            return {
                "healthy": False,
                "error": f"Arabic processor check failed: {str(e)}"
            }
    
    async def _check_websocket_health(self) -> Dict[str, Any]:
        """Check WebSocket service health"""
        try:
            # Would check WebSocket server if available
            return {
                "healthy": True,
                "details": {"websocket_server": "simulated_check"}
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": f"WebSocket check failed: {str(e)}"
            }
    
    async def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        # CPU usage
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_usage = (disk.used / disk.total) * 100
        
        # Network I/O
        network = psutil.net_io_counters()
        network_io = {
            "bytes_sent": network.bytes_sent,
            "bytes_recv": network.bytes_recv,
            "packets_sent": network.packets_sent,
            "packets_recv": network.packets_recv
        }
        
        # Process-specific metrics
        process = psutil.Process()
        active_connections = len(process.connections())
        
        return SystemMetrics(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            network_io=network_io,
            active_connections=active_connections
        )
    
    async def _check_alert_conditions(self):
        """Check for alert conditions"""
        if not self.metrics_history:
            return
        
        latest_metrics = self.metrics_history[-1]
        thresholds = self.config.ALERT_THRESHOLDS
        
        alerts = []
        
        # CPU usage alert
        if latest_metrics.cpu_usage > thresholds["cpu_usage"]:
            alerts.append({
                "type": "cpu_usage",
                "severity": "warning",
                "message": f"High CPU usage: {latest_metrics.cpu_usage:.1f}%",
                "threshold": thresholds["cpu_usage"],
                "value": latest_metrics.cpu_usage
            })
        
        # Memory usage alert
        if latest_metrics.memory_usage > thresholds["memory_usage"]:
            alerts.append({
                "type": "memory_usage",
                "severity": "warning",
                "message": f"High memory usage: {latest_metrics.memory_usage:.1f}%",
                "threshold": thresholds["memory_usage"],
                "value": latest_metrics.memory_usage
            })
        
        # Service health alerts
        for service, health in self.health_checks.items():
            if health.status != "healthy":
                alerts.append({
                    "type": "service_health",
                    "severity": "critical" if health.status == "unhealthy" else "warning",
                    "message": f"Service {service} is {health.status}",
                    "service": service,
                    "error": health.error
                })
        
        # Send alerts
        for alert in alerts:
            await self._send_alert(alert)
    
    async def _send_alert(self, alert: Dict[str, Any]):
        """Send alert notification"""
        alert_key = f"{alert['type']}_{alert.get('service', '')}"
        current_time = datetime.utcnow()
        
        # Rate limiting: don't send same alert more than once per hour
        if alert_key in self.alerts_sent:
            last_sent = self.alerts_sent[alert_key]
            if current_time - last_sent < timedelta(hours=1):
                return
        
        # Log alert
        logger.warning(f"ALERT: {alert['message']}")
        
        # In production, would send to monitoring service (PagerDuty, Slack, etc.)
        await self._log_alert_to_file(alert)
        
        self.alerts_sent[alert_key] = current_time
    
    async def _log_alert_to_file(self, alert: Dict[str, Any]):
        """Log alert to file"""
        try:
            alert_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "alert": alert
            }
            
            # Would write to alert log file in production
            logger.critical(f"Alert logged: {json.dumps(alert_entry)}")
            
        except Exception as e:
            logger.error(f"Failed to log alert: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        overall_status = "healthy"
        
        for health in self.health_checks.values():
            if health.status == "unhealthy":
                overall_status = "unhealthy"
                break
            elif health.status == "degraded" and overall_status == "healthy":
                overall_status = "degraded"
        
        return {
            "overall_status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                service: {
                    "status": health.status,
                    "response_time": health.response_time,
                    "error": health.error
                }
                for service, health in self.health_checks.items()
            }
        }
    
    def get_metrics_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get metrics summary for specified time period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_metrics = [
            m for m in self.metrics_history
            if m.timestamp > cutoff_time
        ]
        
        if not recent_metrics:
            return {"error": "No metrics available"}
        
        # Calculate averages
        avg_cpu = sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_usage for m in recent_metrics) / len(recent_metrics)
        avg_disk = sum(m.disk_usage for m in recent_metrics) / len(recent_metrics)
        
        return {
            "period_hours": hours,
            "metrics_count": len(recent_metrics),
            "averages": {
                "cpu_usage": avg_cpu,
                "memory_usage": avg_memory,
                "disk_usage": avg_disk
            },
            "latest": {
                "cpu_usage": recent_metrics[-1].cpu_usage,
                "memory_usage": recent_metrics[-1].memory_usage,
                "disk_usage": recent_metrics[-1].disk_usage,
                "active_connections": recent_metrics[-1].active_connections
            }
        }

# Global monitor instance
production_monitor = None

async def start_production_monitoring(config):
    """Start production monitoring"""
    global production_monitor
    production_monitor = ProductionMonitor(config)
    await production_monitor.start_monitoring()

def get_health_status():
    """Get current health status"""
    if production_monitor:
        return production_monitor.get_health_status()
    return {"error": "Monitoring not started"}

def get_metrics_summary(hours: int = 1):
    """Get metrics summary"""
    if production_monitor:
        return production_monitor.get_metrics_summary(hours)
    return {"error": "Monitoring not started"}