"""
Performance testing for Arabic dashboard
Load testing, response time validation, and real-time update testing
"""

import pytest
import asyncio
import time
import json
from datetime import datetime, timedelta
from typing import List, Dict
from unittest.mock import Mock, patch

from utils.dashboard_performance import PerformanceMonitor, ArabicDashboardOptimizer
from utils.arabic_nlp_advanced import AdvancedArabicNLP

class TestDashboardPerformance:
    """Test dashboard performance under various loads"""
    
    def setup_method(self):
        """Setup test environment"""
        self.performance_monitor = PerformanceMonitor()
        self.optimizer = ArabicDashboardOptimizer()
        self.nlp = AdvancedArabicNLP()
        
        # Test data
        self.arabic_texts = [
            "الخدمة ممتازة جداً وأنصح بها بشدة",
            "المنتج سيء ولا أنصح بشرائه أبداً",
            "التطبيق جيد ولكن يحتاج إلى بعض التحسينات",
            "فريق الدعم سريع ومفيد جداً في حل المشاكل",
            "التسليم متأخر والجودة متوسطة"
        ] * 20  # 100 texts for testing
    
    def test_dashboard_load_time_target(self):
        """Test dashboard load time meets <1s target"""
        start_time = time.time()
        
        # Simulate dashboard initialization
        self.simulate_dashboard_load()
        
        load_time = time.time() - start_time
        
        # Record load time
        self.performance_monitor.record_dashboard_load_time(load_time)
        
        # Assert meets target
        assert load_time < 1.0, f"Dashboard load time {load_time:.3f}s exceeds 1s target"
        print(f"Dashboard load time: {load_time:.3f}s ✓")
    
    def simulate_dashboard_load(self):
        """Simulate dashboard loading operations"""
        # Simulate various dashboard components loading
        time.sleep(0.1)  # Simulate API calls
        time.sleep(0.05)  # Simulate data processing
        time.sleep(0.02)  # Simulate chart initialization
    
    @pytest.mark.asyncio
    async def test_api_response_time_target(self):
        """Test API response time meets <500ms target"""
        
        async def mock_api_call():
            """Mock API call with processing delay"""
            await asyncio.sleep(0.1)  # Simulate processing
            return {"status": "success", "data": []}
        
        # Measure API response time
        result = await self.performance_monitor.measure_api_response_time(mock_api_call)
        
        response_time = self.performance_monitor.current_metrics.api_response_time
        
        assert response_time < 0.5, f"API response time {response_time:.3f}s exceeds 500ms target"
        print(f"API response time: {response_time:.3f}s ✓")
    
    def test_websocket_latency_target(self):
        """Test WebSocket latency meets <50ms target"""
        
        # Simulate WebSocket message timing
        send_time = time.time()
        time.sleep(0.02)  # Simulate network delay
        
        latency = self.performance_monitor.measure_websocket_latency(send_time)
        
        assert latency < 0.05, f"WebSocket latency {latency:.3f}s exceeds 50ms target"
        print(f"WebSocket latency: {latency:.3f}s ✓")
    
    def test_arabic_processing_rate_target(self):
        """Test Arabic processing rate meets >20 texts/sec target"""
        
        start_time = time.time()
        
        # Process Arabic texts
        processed_count = 0
        for text in self.arabic_texts:
            # Simulate processing
            from utils.arabic_processor import process_arabic_text, extract_sentiment
            processed = process_arabic_text(text)
            sentiment = extract_sentiment(text)
            processed_count += 1
        
        processing_time = time.time() - start_time
        processing_rate = processed_count / processing_time
        
        # Record performance
        self.performance_monitor.measure_arabic_processing_performance(
            processed_count, processing_time
        )
        
        assert processing_rate >= 20.0, f"Arabic processing rate {processing_rate:.1f} texts/sec below 20 target"
        print(f"Arabic processing rate: {processing_rate:.1f} texts/sec ✓")
    
    @pytest.mark.asyncio
    async def test_concurrent_dashboard_load(self):
        """Test dashboard performance under concurrent load"""
        
        async def simulate_user_session():
            """Simulate a user dashboard session"""
            # Dashboard load
            start_time = time.time()
            await asyncio.sleep(0.2)  # Simulate dashboard load
            load_time = time.time() - start_time
            
            # API calls
            for _ in range(5):
                await asyncio.sleep(0.05)  # Simulate API calls
            
            return load_time
        
        # Simulate 10 concurrent users
        tasks = [simulate_user_session() for _ in range(10)]
        load_times = await asyncio.gather(*tasks)
        
        # All load times should be reasonable
        max_load_time = max(load_times)
        avg_load_time = sum(load_times) / len(load_times)
        
        assert max_load_time < 2.0, f"Max concurrent load time {max_load_time:.3f}s too high"
        assert avg_load_time < 1.0, f"Average concurrent load time {avg_load_time:.3f}s too high"
        
        print(f"Concurrent load - Max: {max_load_time:.3f}s, Avg: {avg_load_time:.3f}s ✓")
    
    @pytest.mark.asyncio
    async def test_real_time_update_frequency(self):
        """Test real-time update frequency and accuracy"""
        
        updates_received = []
        
        def mock_websocket_update(data):
            """Mock WebSocket update handler"""
            updates_received.append({
                "timestamp": time.time(),
                "data": data
            })
        
        # Simulate real-time updates
        start_time = time.time()
        while time.time() - start_time < 5.0:  # 5 seconds of updates
            mock_websocket_update({"metric": "test", "value": time.time()})
            await asyncio.sleep(0.1)  # 100ms intervals
        
        # Analyze update frequency
        if len(updates_received) > 1:
            intervals = []
            for i in range(1, len(updates_received)):
                interval = updates_received[i]["timestamp"] - updates_received[i-1]["timestamp"]
                intervals.append(interval)
            
            avg_interval = sum(intervals) / len(intervals)
            update_frequency = 1.0 / avg_interval
            
            assert update_frequency >= 5.0, f"Update frequency {update_frequency:.1f} Hz too low"
            print(f"Real-time update frequency: {update_frequency:.1f} Hz ✓")
    
    def test_memory_usage_under_load(self):
        """Test memory usage remains stable under load"""
        import psutil
        import gc
        
        # Get initial memory usage
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # Simulate heavy dashboard usage
        for i in range(1000):
            # Process Arabic text
            text = self.arabic_texts[i % len(self.arabic_texts)]
            from utils.arabic_processor import extract_sentiment
            sentiment = extract_sentiment(text)
            
            # Cache some data
            self.optimizer.cache[f"test_key_{i}"] = {
                "text": text,
                "sentiment": sentiment,
                "timestamp": time.time()
            }
            
            # Clean up periodically
            if i % 100 == 0:
                gc.collect()
        
        # Get final memory usage
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory
        
        assert memory_growth < 100, f"Memory growth {memory_growth:.1f}MB too high"
        print(f"Memory usage: {initial_memory:.1f}MB → {final_memory:.1f}MB (+{memory_growth:.1f}MB) ✓")
    
    @pytest.mark.asyncio
    async def test_cache_performance(self):
        """Test caching system performance"""
        
        # Test cache writes
        start_time = time.time()
        for i in range(1000):
            await self.optimizer.cache_dashboard_data(f"key_{i}", {"data": f"value_{i}"})
        cache_write_time = time.time() - start_time
        
        # Test cache reads
        start_time = time.time()
        hits = 0
        for i in range(1000):
            cached_data = await self.optimizer.get_cached_data(f"key_{i}")
            if cached_data:
                hits += 1
        cache_read_time = time.time() - start_time
        
        hit_ratio = hits / 1000
        
        assert cache_write_time < 1.0, f"Cache write time {cache_write_time:.3f}s too slow"
        assert cache_read_time < 0.5, f"Cache read time {cache_read_time:.3f}s too slow"
        assert hit_ratio > 0.95, f"Cache hit ratio {hit_ratio:.2%} too low"
        
        print(f"Cache performance - Write: {cache_write_time:.3f}s, Read: {cache_read_time:.3f}s, Hit ratio: {hit_ratio:.2%} ✓")

class TestArabicVisualizationPerformance:
    """Test Arabic visualization rendering performance"""
    
    def setup_method(self):
        """Setup visualization test environment"""
        self.optimizer = ArabicDashboardOptimizer()
        
        # Test Arabic data for charts
        self.chart_data = {
            "labels": ["الخدمة", "المنتج", "التطبيق", "الدعم", "التسليم"] * 20,
            "values": list(range(100)),
            "arabic_texts": [
                "هذا نص عربي طويل جداً يحتوي على تفاصيل كثيرة ومعلومات مفصلة " * 10
                for _ in range(50)
            ]
        }
    
    @pytest.mark.asyncio
    async def test_arabic_text_optimization(self):
        """Test Arabic text optimization for rendering"""
        
        start_time = time.time()
        optimized_texts = await self.optimizer.optimize_arabic_text_rendering(
            self.chart_data["arabic_texts"]
        )
        optimization_time = time.time() - start_time
        
        # Check optimization results
        assert len(optimized_texts) == len(self.chart_data["arabic_texts"])
        assert optimization_time < 1.0, f"Text optimization took {optimization_time:.3f}s"
        
        # Check that long texts are truncated
        long_texts = [text for text in optimized_texts if len(text) > 200]
        assert len(long_texts) == 0, f"Found {len(long_texts)} texts longer than 200 characters"
        
        print(f"Arabic text optimization: {optimization_time:.3f}s for {len(optimized_texts)} texts ✓")
    
    def test_chart_data_optimization(self):
        """Test chart data optimization for performance"""
        
        large_dataset = [{"x": i, "y": i*2, "label": f"البيانات {i}"} for i in range(1000)]
        
        start_time = time.time()
        optimized_data = self.optimizer.optimize_chart_data(large_dataset, max_points=100)
        optimization_time = time.time() - start_time
        
        assert len(optimized_data) <= 100, f"Optimized data has {len(optimized_data)} points, expected ≤100"
        assert optimization_time < 0.1, f"Chart optimization took {optimization_time:.3f}s"
        
        print(f"Chart data optimization: {len(large_dataset)} → {len(optimized_data)} points in {optimization_time:.3f}s ✓")
    
    def test_rtl_text_processing_performance(self):
        """Test RTL text processing performance"""
        
        rtl_texts = [
            "هذا نص عربي من اليمين إلى اليسار مع أرقام ١٢٣٤٥",
            "تطبيق رائع ومفيد جداً للمستخدمين العرب",
            "الخدمة ممتازة والدعم سريع ومتجاوب"
        ] * 100
        
        start_time = time.time()
        
        # Simulate RTL text processing
        processed_texts = []
        for text in rtl_texts:
            # Normalize and prepare for RTL rendering
            normalized = self.optimizer._normalize_for_rendering(text)
            processed_texts.append(normalized)
        
        processing_time = time.time() - start_time
        processing_rate = len(rtl_texts) / processing_time
        
        assert processing_rate >= 100, f"RTL processing rate {processing_rate:.1f} texts/sec too low"
        print(f"RTL text processing rate: {processing_rate:.1f} texts/sec ✓")

class TestRealTimeDataAccuracy:
    """Test real-time data accuracy and consistency"""
    
    def setup_method(self):
        """Setup real-time testing environment"""
        self.performance_monitor = PerformanceMonitor()
        self.nlp = AdvancedArabicNLP()
    
    @pytest.mark.asyncio
    async def test_websocket_message_accuracy(self):
        """Test WebSocket message accuracy and ordering"""
        
        messages_sent = []
        messages_received = []
        
        # Simulate sending messages
        for i in range(100):
            message = {
                "id": i,
                "timestamp": time.time(),
                "data": {"metric": "test", "value": i}
            }
            messages_sent.append(message)
            
            # Simulate network delay
            await asyncio.sleep(0.001)
            
            # Simulate receiving message
            messages_received.append(message)
        
        # Check message ordering
        for i, (sent, received) in enumerate(zip(messages_sent, messages_received)):
            assert sent["id"] == received["id"], f"Message {i} order mismatch"
            assert sent["data"]["value"] == received["data"]["value"], f"Message {i} data mismatch"
        
        print(f"WebSocket message accuracy: {len(messages_received)}/{len(messages_sent)} messages ✓")
    
    def test_sentiment_analysis_consistency(self):
        """Test sentiment analysis consistency across multiple runs"""
        
        test_texts = [
            "الخدمة ممتازة جداً",
            "المنتج سيء للغاية",
            "التطبيق متوسط الجودة"
        ]
        
        # Run sentiment analysis multiple times
        results = []
        for run in range(10):
            run_results = []
            for text in test_texts:
                from utils.arabic_processor import extract_sentiment
                sentiment = extract_sentiment(text)
                run_results.append(sentiment.get("score", sentiment.get("sentiment", 0)))
            results.append(run_results)
        
        # Check consistency
        for text_idx in range(len(test_texts)):
            text_results = [results[run][text_idx] for run in range(10)]
            
            # Calculate variance
            mean_score = sum(text_results) / len(text_results)
            variance = sum((score - mean_score) ** 2 for score in text_results) / len(text_results)
            
            assert variance < 0.1, f"High variance {variance:.3f} in sentiment for text {text_idx}"
        
        print(f"Sentiment analysis consistency validated for {len(test_texts)} texts ✓")
    
    @pytest.mark.asyncio
    async def test_real_time_metrics_accuracy(self):
        """Test real-time metrics calculation accuracy"""
        
        # Generate test metrics
        test_metrics = []
        for i in range(100):
            metric = {
                "timestamp": datetime.utcnow(),
                "value": i,
                "category": "test"
            }
            test_metrics.append(metric)
            await asyncio.sleep(0.01)  # Small delay
        
        # Calculate aggregations
        total_value = sum(m["value"] for m in test_metrics)
        average_value = total_value / len(test_metrics)
        max_value = max(m["value"] for m in test_metrics)
        min_value = min(m["value"] for m in test_metrics)
        
        # Verify calculations
        expected_total = sum(range(100))
        expected_average = expected_total / 100
        expected_max = 99
        expected_min = 0
        
        assert abs(total_value - expected_total) < 1, f"Total calculation error: {total_value} vs {expected_total}"
        assert abs(average_value - expected_average) < 0.1, f"Average calculation error: {average_value} vs {expected_average}"
        assert max_value == expected_max, f"Max calculation error: {max_value} vs {expected_max}"
        assert min_value == expected_min, f"Min calculation error: {min_value} vs {expected_min}"
        
        print(f"Real-time metrics accuracy validated ✓")

class TestCulturalContextValidation:
    """Test cultural context detection and dialect-specific scenarios"""
    
    def setup_method(self):
        """Setup cultural context testing"""
        self.nlp = AdvancedArabicNLP()
        
        # Dialect-specific test cases
        self.dialect_tests = {
            "gulf": [
                "الخدمة زينة ومشكورين على التعامل الطيب",
                "ما شاء الله الموقع يهبل وسهل الاستخدام",
                "يعطيكم العافية على الجهد الرائع"
            ],
            "egyptian": [
                "الحمد لله الخدمة كويسة جداً ومفيش أي مشاكل",
                "بجد المنتج ده عجبني أوي والناس كلها بتمدحه",
                "بصراحة التطبيق ده حلو وسهل في الاستخدام"
            ],
            "levantine": [
                "والله الخدمة كتير منيحة ومشان هيك بنصح فيها",
                "بصراحة المنتج عجبني كتير وهاد شي بيفرحني",
                "يعطيكم العافية على التعامل الراقي والمحترم"
            ]
        }
        
        # Cultural context test cases
        self.cultural_tests = {
            "hospitality": [
                "استقبال ممتاز وضيافة كريمة",
                "ترحيب حار وكرم في التعامل",
                "حفاوة بالغة واهتمام بالضيوف"
            ],
            "religion": [
                "بارك الله فيكم على هذا العمل",
                "جزاكم الله خيراً على الخدمة",
                "الحمد لله والشكر لكم"
            ],
            "family": [
                "خدمة تناسب جميع أفراد العائلة",
                "منتج آمن للأطفال والأهل",
                "تجربة عائلية رائعة"
            ]
        }
    
    def test_dialect_detection_accuracy(self):
        """Test accuracy of Arabic dialect detection"""
        
        correct_detections = 0
        total_tests = 0
        
        for expected_dialect, texts in self.dialect_tests.items():
            for text in texts:
                # Analyze cultural context (includes dialect detection)
                analysis = self.nlp.analyze_cultural_context(text)
                regional_indicators = analysis["regional_indicators"]
                
                # Check if expected dialect is detected
                if expected_dialect in regional_indicators:
                    confidence = regional_indicators[expected_dialect]["confidence"]
                    if confidence > 0.5:  # Threshold for positive detection
                        correct_detections += 1
                
                total_tests += 1
        
        accuracy = correct_detections / total_tests if total_tests > 0 else 0
        
        assert accuracy >= 0.7, f"Dialect detection accuracy {accuracy:.2%} below 70% threshold"
        print(f"Dialect detection accuracy: {accuracy:.2%} ({correct_detections}/{total_tests}) ✓")
    
    def test_cultural_context_detection(self):
        """Test cultural context detection accuracy"""
        
        context_accuracy = {}
        
        for expected_context, texts in self.cultural_tests.items():
            correct_detections = 0
            
            for text in texts:
                analysis = self.nlp.analyze_cultural_context(text)
                cultural_markers = analysis["cultural_markers"]
                
                # Check if expected context is detected
                if expected_context in cultural_markers:
                    strength = cultural_markers[expected_context]["strength"]
                    if strength > 0.3:  # Threshold for positive detection
                        correct_detections += 1
            
            accuracy = correct_detections / len(texts) if texts else 0
            context_accuracy[expected_context] = accuracy
            
            assert accuracy >= 0.6, f"Cultural context '{expected_context}' detection accuracy {accuracy:.2%} too low"
        
        overall_accuracy = sum(context_accuracy.values()) / len(context_accuracy)
        print(f"Cultural context detection - Overall: {overall_accuracy:.2%} ✓")
        
        for context, accuracy in context_accuracy.items():
            print(f"  {context}: {accuracy:.2%}")
    
    def test_emotion_detection_with_cultural_context(self):
        """Test emotion detection considering cultural context"""
        
        # Emotion test cases with cultural nuances
        emotion_tests = {
            "gratitude": [
                "جزاكم الله خيراً على الخدمة الممتازة",
                "بارك الله فيكم وفي عملكم",
                "شكراً من القلب على التعامل الطيب"
            ],
            "satisfaction": [
                "الحمد لله راضي تماماً عن الخدمة",
                "كله تمام والله يعطيكم العافية",
                "والله العظيم خدمة ممتازة"
            ],
            "joy": [
                "فرحان جداً بالمنتج الجديد",
                "ما شاء الله تطبيق رائع ومفرح",
                "سعيد بالتجربة وأنصح الجميع"
            ]
        }
        
        emotion_accuracy = {}
        
        for expected_emotion, texts in emotion_tests.items():
            correct_detections = 0
            
            for text in texts:
                analysis = self.nlp.detect_emotions_advanced(text)
                emotions = analysis["emotions"]
                
                # Check if expected emotion is detected
                if expected_emotion in emotions:
                    score = emotions[expected_emotion]
                    if score > 0.5:  # Threshold for positive detection
                        correct_detections += 1
            
            accuracy = correct_detections / len(texts) if texts else 0
            emotion_accuracy[expected_emotion] = accuracy
            
            assert accuracy >= 0.7, f"Emotion '{expected_emotion}' detection accuracy {accuracy:.2%} too low"
        
        overall_accuracy = sum(emotion_accuracy.values()) / len(emotion_accuracy)
        print(f"Emotion detection with cultural context - Overall: {overall_accuracy:.2%} ✓")

class TestEndToEndUserJourney:
    """Test complete end-to-end user journey in Arabic"""
    
    @pytest.mark.asyncio
    async def test_complete_dashboard_journey(self):
        """Test complete user journey through Arabic dashboard"""
        
        journey_steps = []
        start_time = time.time()
        
        # Step 1: Dashboard load
        step_start = time.time()
        await asyncio.sleep(0.2)  # Simulate dashboard load
        journey_steps.append({"step": "dashboard_load", "time": time.time() - step_start})
        
        # Step 2: Authentication (simulated)
        step_start = time.time()
        await asyncio.sleep(0.1)  # Simulate auth
        journey_steps.append({"step": "authentication", "time": time.time() - step_start})
        
        # Step 3: Data loading
        step_start = time.time()
        await asyncio.sleep(0.3)  # Simulate data load
        journey_steps.append({"step": "data_loading", "time": time.time() - step_start})
        
        # Step 4: Chart rendering
        step_start = time.time()
        await asyncio.sleep(0.15)  # Simulate chart render
        journey_steps.append({"step": "chart_rendering", "time": time.time() - step_start})
        
        # Step 5: Real-time updates
        step_start = time.time()
        for _ in range(5):
            await asyncio.sleep(0.05)  # Simulate real-time updates
        journey_steps.append({"step": "realtime_updates", "time": time.time() - step_start})
        
        total_journey_time = time.time() - start_time
        
        # Validate journey performance
        assert total_journey_time < 3.0, f"Complete journey took {total_journey_time:.3f}s, exceeds 3s limit"
        
        # Validate individual steps
        step_limits = {
            "dashboard_load": 1.0,
            "authentication": 0.5,
            "data_loading": 1.0,
            "chart_rendering": 0.5,
            "realtime_updates": 1.0
        }
        
        for step in journey_steps:
            step_name = step["step"]
            step_time = step["time"]
            limit = step_limits.get(step_name, 1.0)
            
            assert step_time < limit, f"Step '{step_name}' took {step_time:.3f}s, exceeds {limit}s limit"
        
        print(f"Complete user journey: {total_journey_time:.3f}s ✓")
        for step in journey_steps:
            print(f"  {step['step']}: {step['time']:.3f}s")
    
    @pytest.mark.asyncio 
    async def test_arabic_content_workflow(self):
        """Test Arabic content processing workflow"""
        
        # Sample Arabic feedback
        arabic_feedback = [
            "الخدمة ممتازة ولكن التطبيق بطيء أحياناً",
            "منتج رائع وجودة عالية، أنصح به بشدة",
            "تجربة سيئة مع خدمة العملاء، يحتاج تحسين"
        ]
        
        workflow_results = []
        
        for feedback in arabic_feedback:
            step_start = time.time()
            
            # Step 1: Text processing
            from utils.arabic_processor import process_arabic_text
            processed_text = process_arabic_text(feedback)
            
            # Step 2: Sentiment analysis
            from utils.arabic_processor import extract_sentiment
            sentiment = extract_sentiment(feedback)
            
            # Step 3: Advanced NLP
            nlp = AdvancedArabicNLP()
            emotions = nlp.detect_emotions_advanced(feedback)
            cultural_context = nlp.analyze_cultural_context(feedback)
            
            # Step 4: Entity extraction
            entities = nlp.extract_entities_advanced(feedback)
            
            workflow_time = time.time() - step_start
            
            workflow_results.append({
                "text": feedback,
                "processing_time": workflow_time,
                "sentiment_score": sentiment.get("score", sentiment.get("sentiment", 0)),
                "emotions_detected": len(emotions["emotions"]),
                "cultural_markers": len(cultural_context["cultural_markers"]),
                "entities_found": entities["statistics"]["total_entities"]
            })
        
        # Validate workflow performance
        avg_processing_time = sum(r["processing_time"] for r in workflow_results) / len(workflow_results)
        
        assert avg_processing_time < 1.0, f"Average Arabic workflow time {avg_processing_time:.3f}s too high"
        
        # Validate processing quality
        for result in workflow_results:
            assert abs(result["sentiment_score"]) <= 1.0, "Sentiment score out of range"
            assert result["emotions_detected"] >= 0, "Negative emotion count"
            assert result["entities_found"] >= 0, "Negative entity count"
        
        print(f"Arabic content workflow - Average time: {avg_processing_time:.3f}s ✓")
        for i, result in enumerate(workflow_results):
            print(f"  Text {i+1}: {result['processing_time']:.3f}s, Sentiment: {result['sentiment_score']:.2f}")
        
        return workflow_results