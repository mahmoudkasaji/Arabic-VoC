#!/usr/bin/env python3
"""
Comprehensive health check system for Arabic VoC Platform
Monitors all critical components and dependencies
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import aiohttp
import psycopg2
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class HealthCheckResult:
    """Health check result structure"""
    service: str
    status: str  # "healthy", "degraded", "unhealthy"
    response_time: float
    message: str
    timestamp: datetime
    details: Dict[str, Any] = None

class HealthChecker:
    """Comprehensive health monitoring system"""
    
    def __init__(self):
        self.base_url = os.getenv('APP_URL', 'http://localhost:5000')
        self.db_url = os.getenv('DATABASE_URL')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.checks = []
        
    async def check_web_server(self) -> HealthCheckResult:
        """Check web server responsiveness"""
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/health", timeout=10) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        return HealthCheckResult(
                            service="web_server",
                            status="healthy",
                            response_time=response_time,
                            message="Web server responding normally",
                            timestamp=datetime.now(),
                            details=data
                        )
                    else:
                        return HealthCheckResult(
                            service="web_server",
                            status="degraded",
                            response_time=response_time,
                            message=f"HTTP {response.status}",
                            timestamp=datetime.now()
                        )
        except Exception as e:
            return HealthCheckResult(
                service="web_server",
                status="unhealthy",
                response_time=time.time() - start_time,
                message=f"Connection failed: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def check_database(self) -> HealthCheckResult:
        """Check database connectivity and performance"""
        start_time = time.time()
        
        try:
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            
            # Test basic connectivity
            cursor.execute("SELECT 1")
            cursor.fetchone()
            
            # Test Arabic text handling
            cursor.execute("SELECT 'مرحبا بك' as arabic_test")
            result = cursor.fetchone()
            
            # Check database size and connections
            cursor.execute("""
                SELECT 
                    pg_size_pretty(pg_database_size(current_database())) as db_size,
                    count(*) as active_connections
                FROM pg_stat_activity 
                WHERE state = 'active'
            """)
            db_stats = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            response_time = time.time() - start_time
            
            return HealthCheckResult(
                service="database",
                status="healthy" if response_time < 1.0 else "degraded",
                response_time=response_time,
                message="Database responsive with Arabic support",
                timestamp=datetime.now(),
                details={
                    "arabic_test": result[0] if result else None,
                    "database_size": db_stats[0] if db_stats else None,
                    "active_connections": db_stats[1] if db_stats else None
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                service="database",
                status="unhealthy",
                response_time=time.time() - start_time,
                message=f"Database error: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def check_arabic_processing(self) -> HealthCheckResult:
        """Check Arabic text processing capabilities"""
        start_time = time.time()
        
        try:
            # Test Arabic text normalization
            from app.services.arabic_analysis import ArabicTextProcessor
            processor = ArabicTextProcessor()
            
            test_text = "الخدمة ممتازة جداً"
            normalized = processor.normalize_arabic(test_text)
            reshaped = processor.reshape_for_display(test_text)
            
            response_time = time.time() - start_time
            
            return HealthCheckResult(
                service="arabic_processing",
                status="healthy",
                response_time=response_time,
                message="Arabic processing working correctly",
                timestamp=datetime.now(),
                details={
                    "original": test_text,
                    "normalized": normalized,
                    "reshaped_length": len(reshaped)
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                service="arabic_processing",
                status="unhealthy",
                response_time=time.time() - start_time,
                message=f"Arabic processing error: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def check_ai_analysis(self) -> HealthCheckResult:
        """Check AI analysis system"""
        start_time = time.time()
        
        try:
            # Test basic OpenAI connectivity
            from app.services.arabic_analysis import analyze_arabic_feedback
            
            test_text = "الخدمة جيدة"
            result = analyze_arabic_feedback(test_text)
            
            response_time = time.time() - start_time
            
            # Validate result structure
            has_sentiment = 'sentiment' in result
            has_categorization = 'categorization' in result
            
            if has_sentiment and has_categorization:
                status = "healthy" if response_time < 5.0 else "degraded"
                message = "AI analysis functioning normally"
            else:
                status = "degraded"
                message = "AI analysis returning incomplete results"
            
            return HealthCheckResult(
                service="ai_analysis",
                status=status,
                response_time=response_time,
                message=message,
                timestamp=datetime.now(),
                details={
                    "has_sentiment": has_sentiment,
                    "has_categorization": has_categorization,
                    "result_keys": list(result.keys())
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                service="ai_analysis",
                status="unhealthy",
                response_time=time.time() - start_time,
                message=f"AI analysis error: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def check_agent_system(self) -> HealthCheckResult:
        """Check LangGraph agent orchestration"""
        start_time = time.time()
        
        try:
            from app.services.arabic_analysis import analyze_arabic_feedback_agents
            
            test_text = "الخدمة ممتازة"
            result = await analyze_arabic_feedback_agents(test_text)
            
            response_time = time.time() - start_time
            
            # Check if agent system responded correctly
            model_used = result.get('model_used', '')
            is_agent_result = 'langgraph' in model_used.lower()
            
            return HealthCheckResult(
                service="agent_system",
                status="healthy" if is_agent_result else "degraded",
                response_time=response_time,
                message="Agent system operational" if is_agent_result else "Fallback to legacy system",
                timestamp=datetime.now(),
                details={
                    "model_used": model_used,
                    "agent_system_active": is_agent_result,
                    "processing_stages": result.get('processing_stages')
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                service="agent_system",
                status="unhealthy",
                response_time=time.time() - start_time,
                message=f"Agent system error: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def check_memory_usage(self) -> HealthCheckResult:
        """Check system memory usage"""
        start_time = time.time()
        
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            memory_percent = memory.percent
            disk_percent = disk.percent
            
            # Determine status based on resource usage
            if memory_percent > 90 or disk_percent > 90:
                status = "unhealthy"
                message = "Critical resource usage"
            elif memory_percent > 80 or disk_percent > 80:
                status = "degraded"
                message = "High resource usage"
            else:
                status = "healthy"
                message = "Resource usage normal"
            
            return HealthCheckResult(
                service="system_resources",
                status=status,
                response_time=time.time() - start_time,
                message=message,
                timestamp=datetime.now(),
                details={
                    "memory_percent": memory_percent,
                    "memory_available_gb": round(memory.available / 1024**3, 2),
                    "disk_percent": disk_percent,
                    "disk_free_gb": round(disk.free / 1024**3, 2)
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                service="system_resources",
                status="unhealthy",
                response_time=time.time() - start_time,
                message=f"Resource check error: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks concurrently"""
        logger.info("Starting comprehensive health checks...")
        
        checks = [
            self.check_web_server(),
            self.check_database(),
            self.check_arabic_processing(),
            self.check_ai_analysis(),
            self.check_agent_system(),
            self.check_memory_usage()
        ]
        
        results = await asyncio.gather(*checks, return_exceptions=True)
        
        # Process results
        health_results = []
        overall_status = "healthy"
        
        for result in results:
            if isinstance(result, Exception):
                health_results.append(HealthCheckResult(
                    service="unknown",
                    status="unhealthy",
                    response_time=0.0,
                    message=f"Check failed: {str(result)}",
                    timestamp=datetime.now()
                ))
                overall_status = "unhealthy"
            else:
                health_results.append(result)
                if result.status == "unhealthy":
                    overall_status = "unhealthy"
                elif result.status == "degraded" and overall_status == "healthy":
                    overall_status = "degraded"
        
        # Compile summary
        summary = {
            "overall_status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "total_checks": len(health_results),
            "healthy_checks": sum(1 for r in health_results if r.status == "healthy"),
            "degraded_checks": sum(1 for r in health_results if r.status == "degraded"),
            "unhealthy_checks": sum(1 for r in health_results if r.status == "unhealthy"),
            "checks": [
                {
                    "service": r.service,
                    "status": r.status,
                    "response_time": round(r.response_time, 3),
                    "message": r.message,
                    "details": r.details
                }
                for r in health_results
            ]
        }
        
        logger.info(f"Health check completed: {overall_status}")
        return summary

def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Arabic VoC Platform Health Check')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    parser.add_argument('--service', help='Check specific service only')
    args = parser.parse_args()
    
    async def run_checks():
        checker = HealthChecker()
        
        if args.service:
            # Run specific service check
            method_name = f"check_{args.service}"
            if hasattr(checker, method_name):
                result = await getattr(checker, method_name)()
                if args.json:
                    print(json.dumps({
                        "service": result.service,
                        "status": result.status,
                        "response_time": result.response_time,
                        "message": result.message,
                        "details": result.details
                    }, indent=2))
                else:
                    print(f"{result.service}: {result.status} ({result.response_time:.3f}s) - {result.message}")
            else:
                print(f"Unknown service: {args.service}")
                return 1
        else:
            # Run all checks
            summary = await checker.run_all_checks()
            
            if args.json:
                print(json.dumps(summary, indent=2))
            else:
                print(f"Overall Status: {summary['overall_status'].upper()}")
                print(f"Checks: {summary['healthy_checks']}/{summary['total_checks']} healthy")
                print("\nDetailed Results:")
                for check in summary['checks']:
                    status_emoji = {"healthy": "✅", "degraded": "⚠️", "unhealthy": "❌"}.get(check['status'], "❓")
                    print(f"  {status_emoji} {check['service']}: {check['message']} ({check['response_time']}s)")
            
            # Exit code based on overall status
            return 0 if summary['overall_status'] == "healthy" else 1
    
    exit_code = asyncio.run(run_checks())
    exit(exit_code)

if __name__ == "__main__":
    main()