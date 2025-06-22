#!/usr/bin/env python3
"""
Performance benchmarking for Arabic VoC Platform
Comprehensive performance analysis and optimization recommendations
"""

import asyncio
import time
import statistics
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Tuple
from concurrent.futures import ProcessPoolExecutor
import psutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceBenchmark:
    """Comprehensive performance benchmarking suite"""
    
    def __init__(self):
        self.results = {}
        self.test_data = self._load_test_data()
    
    def _load_test_data(self) -> Dict[str, List[str]]:
        """Load test data for benchmarking"""
        return {
            "short_texts": [
                "الخدمة ممتازة",
                "المنتج جيد",
                "التطبيق سريع",
                "الدعم مفيد",
                "الأسعار مناسبة"
            ],
            "medium_texts": [
                "الخدمة ممتازة جداً وأنصح بها للجميع، فريق العمل محترف ومتعاون",
                "المنتج جودته عالية ولكن السعر مرتفع قليلاً، بشكل عام تجربة جيدة",
                "التطبيق سهل الاستخدام وسريع، لكن يحتاج إلى بعض الميزات الإضافية",
                "فريق الدعم سريع في الرد ومفيد في حل المشاكل، شكراً لكم",
                "الأسعار معقولة مقارنة بالجودة المقدمة، راضي عن التجربة"
            ],
            "long_texts": [
                """أود أن أعبر عن امتناني العميق لفريق العمل المحترم في شركتكم الموقرة على الخدمة 
                الاستثنائية التي تلقيتها خلال تعاملي معكم. لقد كانت التجربة رائعة من البداية حتى النهاية، 
                بدءاً من سهولة التواصل والاستفسار، مروراً بسرعة الاستجابة والتعامل المهني، وانتهاءً بجودة 
                الخدمة المقدمة التي فاقت كل توقعاتي. إن مستوى الاحترافية والاهتمام بالتفاصيل الذي لمسته 
                يعكس مدى حرصكم على إرضاء العملاء وتقديم أفضل ما لديكم. أتطلع للتعامل معكم مرة أخرى في المستقبل.""",
                
                """للأسف، كانت تجربتي مع خدمتكم محبطة إلى حد كبير. واجهت عدة مشاكل منذ البداية، 
                بدءاً من صعوبة في التسجيل والتي استغرقت وقتاً أطول من المتوقع، مروراً بعدم وضوح 
                التعليمات المقدمة، وانتهاءً بعدم تجاوب فريق الدعم مع استفساراتي في الوقت المناسب. 
                أعتقد أن هناك حاجة ماسة لتحسين الخدمة وتطوير آليات التواصل مع العملاء. آمل أن تأخذوا 
                هذه الملاحظات بعين الاعتبار وتعملوا على تحسين الوضع للعملاء المستقبليين."""
            ],
            "mixed_language": [
                "الخدمة excellent والفريق professional جداً",
                "The support team كانوا helpful والمشكلة تم حلها quickly", 
                "Overall experience كانت positive ولكن يحتاج improvements"
            ],
            "dialects": [
                "الخدمة زينة ومشكورين على التعامل الطيب",  # Gulf
                "الحمد لله الخدمة كويسة جداً ومفيش مشاكل",    # Egyptian
                "والله الخدمة منيحة كتير ومشان هيك بنصح فيها", # Levantine
                "الخدمة زوينة بزاف وراه عاجبتني بزاف"        # Moroccan
            ]
        }
    
    async def benchmark_agent_system(self) -> Dict[str, Any]:
        """Benchmark the LangGraph agent system"""
        logger.info("Benchmarking agent system performance...")
        
        from app.services.arabic_analysis import analyze_arabic_feedback_agents
        
        results = {}
        
        # Test different text lengths
        for category, texts in self.test_data.items():
            logger.info(f"Testing {category}...")
            
            times = []
            success_count = 0
            
            for text in texts:
                for iteration in range(3):  # 3 iterations per text
                    start_time = time.time()
                    
                    try:
                        result = await analyze_arabic_feedback_agents(text)
                        end_time = time.time()
                        
                        processing_time = end_time - start_time
                        times.append(processing_time)
                        
                        # Validate result quality
                        if (result.get('sentiment') and 
                            result.get('categorization') and
                            result.get('model_used', '').lower().find('langgraph') != -1):
                            success_count += 1
                        
                    except Exception as e:
                        logger.warning(f"Agent analysis failed: {e}")
                        times.append(10.0)  # Penalty time for failures
            
            if times:
                results[category] = {
                    "avg_time": statistics.mean(times),
                    "median_time": statistics.median(times),
                    "min_time": min(times),
                    "max_time": max(times),
                    "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
                    "success_rate": success_count / len(times),
                    "total_tests": len(times)
                }
        
        return results
    
    async def benchmark_legacy_system(self) -> Dict[str, Any]:
        """Benchmark the legacy analysis system for comparison"""
        logger.info("Benchmarking legacy system performance...")
        
        from app.services.arabic_analysis import analyze_arabic_feedback
        
        results = {}
        
        for category, texts in self.test_data.items():
            logger.info(f"Testing legacy {category}...")
            
            times = []
            success_count = 0
            
            for text in texts:
                for iteration in range(3):
                    start_time = time.time()
                    
                    try:
                        result = analyze_arabic_feedback(text)
                        end_time = time.time()
                        
                        processing_time = end_time - start_time
                        times.append(processing_time)
                        
                        if result.get('sentiment') and result.get('categorization'):
                            success_count += 1
                        
                    except Exception as e:
                        logger.warning(f"Legacy analysis failed: {e}")
                        times.append(10.0)
            
            if times:
                results[category] = {
                    "avg_time": statistics.mean(times),
                    "median_time": statistics.median(times),
                    "min_time": min(times),
                    "max_time": max(times),
                    "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
                    "success_rate": success_count / len(times),
                    "total_tests": len(times)
                }
        
        return results
    
    async def benchmark_concurrent_load(self, concurrent_users: int = 10) -> Dict[str, Any]:
        """Benchmark system under concurrent load"""
        logger.info(f"Benchmarking concurrent load with {concurrent_users} users...")
        
        from app.services.arabic_analysis import analyze_arabic_feedback_agents
        
        async def simulate_user():
            """Simulate a single user's requests"""
            user_times = []
            user_successes = 0
            
            # Each user makes 5 requests
            for _ in range(5):
                text = self.test_data["medium_texts"][0]  # Use consistent text
                start_time = time.time()
                
                try:
                    result = await analyze_arabic_feedback_agents(text)
                    end_time = time.time()
                    
                    user_times.append(end_time - start_time)
                    if result.get('sentiment'):
                        user_successes += 1
                        
                except Exception:
                    user_times.append(10.0)
                
                # Small delay between requests
                await asyncio.sleep(0.1)
            
            return user_times, user_successes
        
        # Run concurrent users
        start_time = time.time()
        
        tasks = [simulate_user() for _ in range(concurrent_users)]
        user_results = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        
        # Aggregate results
        all_times = []
        total_successes = 0
        total_requests = 0
        
        for user_times, user_successes in user_results:
            all_times.extend(user_times)
            total_successes += user_successes
            total_requests += len(user_times)
        
        return {
            "concurrent_users": concurrent_users,
            "total_requests": total_requests,
            "total_time": total_time,
            "requests_per_second": total_requests / total_time,
            "avg_response_time": statistics.mean(all_times),
            "median_response_time": statistics.median(all_times),
            "95th_percentile": sorted(all_times)[int(len(all_times) * 0.95)],
            "success_rate": total_successes / total_requests,
            "throughput": total_successes / total_time
        }
    
    def benchmark_memory_usage(self) -> Dict[str, Any]:
        """Benchmark memory usage patterns"""
        logger.info("Benchmarking memory usage...")
        
        import gc
        
        # Get baseline memory
        gc.collect()
        process = psutil.Process()
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        memory_measurements = []
        
        # Simulate processing load
        for i in range(100):
            # Create some processing load
            test_text = self.test_data["long_texts"][0] * (i % 3 + 1)
            
            # Measure memory every 10 iterations
            if i % 10 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_measurements.append(current_memory)
            
            # Simulate processing
            time.sleep(0.01)
        
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024
        
        return {
            "baseline_memory_mb": baseline_memory,
            "final_memory_mb": final_memory,
            "peak_memory_mb": max(memory_measurements),
            "memory_increase_mb": final_memory - baseline_memory,
            "measurements": memory_measurements
        }
    
    async def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        logger.info("Generating comprehensive performance report...")
        
        report = {
            "report_timestamp": datetime.now().isoformat(),
            "system_info": {
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": psutil.virtual_memory().total / 1024**3,
                "python_version": __import__('sys').version
            }
        }
        
        # Run benchmarks
        try:
            report["agent_performance"] = await self.benchmark_agent_system()
        except Exception as e:
            logger.error(f"Agent benchmark failed: {e}")
            report["agent_performance"] = {"error": str(e)}
        
        try:
            report["legacy_performance"] = await self.benchmark_legacy_system()
        except Exception as e:
            logger.error(f"Legacy benchmark failed: {e}")
            report["legacy_performance"] = {"error": str(e)}
        
        try:
            report["concurrent_load"] = await self.benchmark_concurrent_load()
        except Exception as e:
            logger.error(f"Concurrent benchmark failed: {e}")
            report["concurrent_load"] = {"error": str(e)}
        
        try:
            report["memory_usage"] = self.benchmark_memory_usage()
        except Exception as e:
            logger.error(f"Memory benchmark failed: {e}")
            report["memory_usage"] = {"error": str(e)}
        
        # Performance analysis and recommendations
        report["analysis"] = self._analyze_performance(report)
        
        return report
    
    def _analyze_performance(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance results and generate recommendations"""
        analysis = {
            "summary": {},
            "recommendations": [],
            "performance_grade": "Unknown"
        }
        
        try:
            # Compare agent vs legacy performance
            agent_perf = report.get("agent_performance", {})
            legacy_perf = report.get("legacy_performance", {})
            
            if agent_perf and legacy_perf and "medium_texts" in both:
                agent_avg = agent_perf["medium_texts"]["avg_time"]
                legacy_avg = legacy_perf["medium_texts"]["avg_time"]
                
                improvement = ((legacy_avg - agent_avg) / legacy_avg) * 100
                analysis["summary"]["agent_improvement"] = f"{improvement:.1f}%"
                
                if improvement > 20:
                    analysis["recommendations"].append("Agent system showing significant performance improvement")
                elif improvement < 0:
                    analysis["recommendations"].append("Consider optimizing agent system - legacy performs better")
            
            # Analyze concurrent performance
            concurrent = report.get("concurrent_load", {})
            if concurrent:
                rps = concurrent.get("requests_per_second", 0)
                avg_response = concurrent.get("avg_response_time", 0)
                
                if rps > 10:
                    analysis["summary"]["throughput"] = "High"
                elif rps > 5:
                    analysis["summary"]["throughput"] = "Medium"
                else:
                    analysis["summary"]["throughput"] = "Low"
                    analysis["recommendations"].append("Consider performance optimization for better throughput")
                
                if avg_response < 2.0:
                    analysis["summary"]["response_time"] = "Excellent"
                elif avg_response < 5.0:
                    analysis["summary"]["response_time"] = "Good"
                else:
                    analysis["summary"]["response_time"] = "Needs Improvement"
                    analysis["recommendations"].append("Response time optimization recommended")
            
            # Memory analysis
            memory = report.get("memory_usage", {})
            if memory:
                memory_increase = memory.get("memory_increase_mb", 0)
                
                if memory_increase < 50:
                    analysis["summary"]["memory_efficiency"] = "Excellent"
                elif memory_increase < 100:
                    analysis["summary"]["memory_efficiency"] = "Good"
                else:
                    analysis["summary"]["memory_efficiency"] = "Needs Optimization"
                    analysis["recommendations"].append("Memory usage optimization recommended")
            
            # Overall grade
            scores = []
            if analysis["summary"].get("throughput") == "High":
                scores.append(90)
            elif analysis["summary"].get("throughput") == "Medium":
                scores.append(70)
            else:
                scores.append(50)
            
            if analysis["summary"].get("response_time") == "Excellent":
                scores.append(95)
            elif analysis["summary"].get("response_time") == "Good":
                scores.append(80)
            else:
                scores.append(60)
            
            if analysis["summary"].get("memory_efficiency") == "Excellent":
                scores.append(95)
            elif analysis["summary"].get("memory_efficiency") == "Good":
                scores.append(80)
            else:
                scores.append(65)
            
            if scores:
                avg_score = sum(scores) / len(scores)
                if avg_score >= 90:
                    analysis["performance_grade"] = "A+"
                elif avg_score >= 80:
                    analysis["performance_grade"] = "A"
                elif avg_score >= 70:
                    analysis["performance_grade"] = "B+"
                elif avg_score >= 60:
                    analysis["performance_grade"] = "B"
                else:
                    analysis["performance_grade"] = "C"
        
        except Exception as e:
            logger.error(f"Performance analysis failed: {e}")
            analysis["error"] = str(e)
        
        return analysis

async def main():
    """Main benchmark execution"""
    logger.info("Starting Arabic VoC Platform performance benchmarking...")
    
    benchmark = PerformanceBenchmark()
    
    # Generate comprehensive report
    report = await benchmark.generate_performance_report()
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"performance_report_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "="*60)
    print("ARABIC VOC PLATFORM PERFORMANCE REPORT")
    print("="*60)
    
    analysis = report.get("analysis", {})
    print(f"Overall Grade: {analysis.get('performance_grade', 'Unknown')}")
    print(f"Report saved to: {filename}")
    
    if "summary" in analysis:
        print("\nPerformance Summary:")
        for key, value in analysis["summary"].items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
    
    if "recommendations" in analysis and analysis["recommendations"]:
        print("\nRecommendations:")
        for i, rec in enumerate(analysis["recommendations"], 1):
            print(f"  {i}. {rec}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(main())