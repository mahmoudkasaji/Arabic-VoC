"""
Load testing and performance validation for Arabic VoC platform
Testing concurrent requests, throughput, and response times
"""

import pytest
import asyncio
import time
import random
from httpx import AsyncClient
from fastapi import FastAPI
from typing import List, Dict
from utils.arabic_processor import process_arabic_text, extract_sentiment
from utils.openai_client import analyze_arabic_feedback

# Create test app for load testing
test_app = FastAPI()

class TestLoadPerformance:
    """Load testing with Arabic content"""
    
    def setup_method(self):
        """Setup test data for load testing"""
        self.arabic_feedback_samples = [
            "الخدمة ممتازة جداً وأنصح بها بشدة",
            "المنتج سيء ولا أنصح بشرائه",
            "التطبيق جيد لكن يحتاج تحسينات",
            "فريق الدعم سريع ومفيد جداً",
            "التسليم متأخر والجودة متوسطة",
            "أحب هذا المتجر وأتسوق منه دائماً",
            "الموقع الإلكتروني لا يعمل بشكل صحيح",
            "منتج رائع بسعر معقول جداً",
            "خدمة عملاء ممتازة ومتجاوبة",
            "تجربة تسوق رائعة وسريعة"
        ]
        
        self.large_arabic_texts = [
            "تجربة استثنائية مع فريق العمل المحترم الذي قدم لنا خدمة متميزة " * 20,
            "أود أن أعبر عن امتناني العميق لجميع العاملين في هذه الشركة الرائدة " * 25,
            "لقد كانت التجربة مع منتجكم أفضل مما توقعت بكثير وأنصح الجميع " * 30
        ]
    
    def test_arabic_processing_throughput(self):
        """Test throughput of Arabic text processing"""
        start_time = time.time()
        processed_count = 0
        
        # Process texts for 10 seconds
        while time.time() - start_time < 10:
            text = random.choice(self.arabic_feedback_samples)
            
            try:
                processed = process_arabic_text(text)
                sentiment = extract_sentiment(text)
                
                assert isinstance(processed, str)
                assert isinstance(sentiment, dict)
                processed_count += 1
                
            except Exception as e:
                pytest.fail(f"Processing failed: {e}")
        
        end_time = time.time()
        duration = end_time - start_time
        throughput = processed_count / duration
        
        # Should process at least 10 texts per second
        assert throughput >= 10, f"Low throughput: {throughput:.2f} texts/sec"
        print(f"Arabic processing throughput: {throughput:.2f} texts/sec")
    
    def test_large_text_processing_performance(self):
        """Test performance with large Arabic texts"""
        for large_text in self.large_arabic_texts:
            start_time = time.time()
            
            # Process large text
            processed = process_arabic_text(large_text)
            sentiment = extract_sentiment(large_text)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Should complete within 5 seconds (target requirement)
            assert processing_time < 5.0, f"Large text processing too slow: {processing_time}s"
            
            # Should return valid results
            assert isinstance(processed, str)
            assert len(processed) > 0
            assert isinstance(sentiment, dict)
            
            text_length = len(large_text)
            chars_per_second = text_length / processing_time
            print(f"Large text ({text_length} chars) processed at {chars_per_second:.0f} chars/sec")
    
    @pytest.mark.asyncio
    async def test_concurrent_processing(self):
        """Test concurrent Arabic text processing"""
        async def process_text_async(text: str, delay: float = 0):
            """Process text with optional delay"""
            if delay:
                await asyncio.sleep(delay)
            
            start_time = time.time()
            processed = process_arabic_text(text)
            sentiment = extract_sentiment(text)
            end_time = time.time()
            
            return {
                'processed': processed,
                'sentiment': sentiment,
                'processing_time': end_time - start_time,
                'text_length': len(text)
            }
        
        # Create concurrent tasks
        tasks = []
        for i in range(20):  # 20 concurrent processes
            text = random.choice(self.arabic_feedback_samples)
            delay = random.uniform(0, 0.1)  # Small random delay
            task = process_text_async(text, delay)
            tasks.append(task)
        
        # Execute concurrently
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        total_time = end_time - start_time
        
        # Check results
        successful_results = [r for r in results if isinstance(r, dict)]
        failed_results = [r for r in results if isinstance(r, Exception)]
        
        # Should have high success rate
        success_rate = len(successful_results) / len(results)
        assert success_rate >= 0.9, f"Low success rate: {success_rate:.2%}"
        
        # Should complete in reasonable time
        assert total_time < 10.0, f"Concurrent processing too slow: {total_time}s"
        
        # Calculate average processing time
        processing_times = [r['processing_time'] for r in successful_results]
        avg_processing_time = sum(processing_times) / len(processing_times)
        
        print(f"Concurrent processing: {len(successful_results)}/{len(results)} successful")
        print(f"Average processing time: {avg_processing_time:.3f}s")
        print(f"Total concurrent time: {total_time:.3f}s")
    
    def test_memory_usage_stability(self):
        """Test memory usage stability under load"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Process many texts
        for i in range(1000):
            text = random.choice(self.arabic_feedback_samples)
            
            processed = process_arabic_text(text)
            sentiment = extract_sentiment(text)
            
            # Verify results
            assert isinstance(processed, str)
            assert isinstance(sentiment, dict)
            
            # Check memory every 100 iterations
            if i % 100 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_growth = current_memory - initial_memory
                
                # Memory growth should be reasonable (< 100MB for 1000 texts)
                assert memory_growth < 100, f"Excessive memory growth: {memory_growth:.1f}MB"
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        total_growth = final_memory - initial_memory
        
        print(f"Memory usage: {initial_memory:.1f}MB -> {final_memory:.1f}MB (+{total_growth:.1f}MB)")
        assert total_growth < 50, f"Memory leak detected: {total_growth:.1f}MB growth"

class TestAPILoadTesting:
    """API load testing simulation"""
    
    @pytest.mark.asyncio
    async def test_simulated_api_load(self):
        """Simulate API load testing"""
        # This would test actual API endpoints if available
        # For now, test the underlying functions
        
        feedback_data_samples = [
            {
                "content": "الخدمة ممتازة والفريق محترف",
                "channel": "website",
                "rating": 5
            },
            {
                "content": "المنتج جيد لكن السعر مرتفع",
                "channel": "mobile_app", 
                "rating": 3
            },
            {
                "content": "تجربة سيئة مع خدمة العملاء",
                "channel": "phone",
                "rating": 1
            }
        ]
        
        async def simulate_feedback_submission(data):
            """Simulate feedback submission processing"""
            start_time = time.time()
            
            # Simulate validation
            content = data["content"]
            if not content or len(content) > 5000:
                raise ValueError("Invalid content")
            
            # Simulate processing
            processed = process_arabic_text(content)
            sentiment = extract_sentiment(content)
            
            # Simulate response
            end_time = time.time()
            
            return {
                "id": random.randint(1, 10000),
                "content": processed,
                "sentiment_score": sentiment.get("score", sentiment.get("sentiment", 0)),
                "confidence_score": sentiment.get("confidence", 0),
                "processing_time": end_time - start_time,
                "status": "processed"
            }
        
        # Simulate concurrent API requests
        tasks = []
        for i in range(50):  # 50 concurrent requests
            data = random.choice(feedback_data_samples)
            task = simulate_feedback_submission(data)
            tasks.append(task)
        
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        total_time = end_time - start_time
        
        # Analyze results
        successful = [r for r in results if isinstance(r, dict)]
        failed = [r for r in results if isinstance(r, Exception)]
        
        success_rate = len(successful) / len(results)
        requests_per_second = len(results) / total_time
        
        # Performance assertions
        assert success_rate >= 0.95, f"Low API success rate: {success_rate:.2%}"
        assert requests_per_second >= 10, f"Low API throughput: {requests_per_second:.1f} req/s"
        
        # Response time analysis
        processing_times = [r["processing_time"] for r in successful]
        avg_response_time = sum(processing_times) / len(processing_times)
        max_response_time = max(processing_times)
        
        assert avg_response_time < 1.0, f"High average response time: {avg_response_time:.3f}s"
        assert max_response_time < 5.0, f"High max response time: {max_response_time:.3f}s"
        
        print(f"API Load Test Results:")
        print(f"  Success rate: {success_rate:.2%}")
        print(f"  Throughput: {requests_per_second:.1f} requests/sec")
        print(f"  Avg response time: {avg_response_time:.3f}s")
        print(f"  Max response time: {max_response_time:.3f}s")

class TestBenchmarkComparison:
    """Benchmark Arabic processing against performance targets"""
    
    def test_sentiment_analysis_benchmark(self):
        """Benchmark sentiment analysis against 5-second target"""
        test_texts = [
            "نص قصير للاختبار",  # Short text
            "نص متوسط الطول يحتوي على تفاصيل أكثر للمراجعة والتحليل",  # Medium text
            "نص طويل جداً يحتوي على محتوى مفصل وشامل " * 50,  # Long text
        ]
        
        results = []
        
        for text in test_texts:
            text_length = len(text)
            
            # Test multiple iterations for consistency
            times = []
            for _ in range(5):
                start_time = time.time()
                
                # Core processing
                processed = process_arabic_text(text)
                sentiment = extract_sentiment(text)
                
                # Optional: Test OpenAI if available
                try:
                    ai_result = analyze_arabic_feedback(text[:500])  # Limit for API
                except:
                    ai_result = None
                
                end_time = time.time()
                times.append(end_time - start_time)
            
            avg_time = sum(times) / len(times)
            max_time = max(times)
            
            results.append({
                'text_length': text_length,
                'avg_time': avg_time,
                'max_time': max_time,
                'meets_target': max_time < 5.0
            })
            
            # Assert performance target
            assert max_time < 5.0, f"Text ({text_length} chars) processing too slow: {max_time:.2f}s"
        
        # Print benchmark results
        print("\nSentiment Analysis Benchmark:")
        print("Text Length | Avg Time | Max Time | Target Met")
        print("-" * 50)
        for result in results:
            status = "✓" if result['meets_target'] else "✗"
            print(f"{result['text_length']:10d} | {result['avg_time']:7.3f}s | {result['max_time']:7.3f}s | {status}")
    
    def test_throughput_benchmark(self):
        """Benchmark processing throughput"""
        sample_texts = [
            "تجربة ممتازة",
            "خدمة جيدة جداً", 
            "منتج رائع وسعر معقول",
            "فريق محترف ومتعاون",
            "تطبيق سهل الاستخدام"
        ]
        
        # Test sustained throughput for 30 seconds
        start_time = time.time()
        processed_count = 0
        
        while time.time() - start_time < 30:
            text = random.choice(sample_texts)
            
            # Process text
            processed = process_arabic_text(text)
            sentiment = extract_sentiment(text)
            
            # Validate results
            assert isinstance(processed, str)
            assert isinstance(sentiment, dict)
            
            processed_count += 1
        
        end_time = time.time()
        duration = end_time - start_time
        throughput = processed_count / duration
        
        print(f"\nThroughput Benchmark:")
        print(f"  Processed: {processed_count} texts")
        print(f"  Duration: {duration:.1f} seconds")
        print(f"  Throughput: {throughput:.1f} texts/second")
        
        # Should process at least 20 texts per second
        assert throughput >= 20, f"Low throughput: {throughput:.1f} texts/sec (target: 20+)"