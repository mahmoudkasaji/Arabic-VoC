"""
Performance tests for Arabic VoC platform
Testing caching, batching, and optimization
"""

import pytest
import asyncio
import time
from utils.performance import (
    LRUCache, ArabicTextCache, BatchProcessor, 
    optimize_arabic_processing, arabic_cache, performance_monitor
)

class TestLRUCache:
    """Test LRU cache implementation"""
    
    def test_cache_basic_operations(self):
        """Test basic cache operations"""
        cache = LRUCache(max_size=3)
        
        # Test put and get
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # Test cache miss
        assert cache.get("nonexistent") is None
        
        # Test cache stats
        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["size"] == 1
    
    def test_cache_eviction(self):
        """Test cache eviction when full"""
        cache = LRUCache(max_size=2)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")  # Should evict key1
        
        assert cache.get("key1") is None  # Evicted
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert cache.get_stats()["size"] == 2
    
    def test_cache_lru_ordering(self):
        """Test LRU ordering"""
        cache = LRUCache(max_size=2)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        
        # Access key1 to make it most recently used
        cache.get("key1")
        
        # Add key3, should evict key2 (least recently used)
        cache.put("key3", "value3")
        
        assert cache.get("key1") == "value1"  # Still there
        assert cache.get("key2") is None      # Evicted
        assert cache.get("key3") == "value3"  # New item
    
    def test_cache_update_existing(self):
        """Test updating existing cache entries"""
        cache = LRUCache(max_size=2)
        
        cache.put("key1", "value1")
        cache.put("key1", "updated_value1")  # Update
        
        assert cache.get("key1") == "updated_value1"
        assert cache.get_stats()["size"] == 1

class TestArabicTextCache:
    """Test Arabic-specific caching"""
    
    def setup_method(self):
        """Setup cache for each test"""
        self.cache = ArabicTextCache(max_size=10)
    
    def test_normalization_cache(self):
        """Test Arabic normalization caching"""
        text = "النص العربي"
        normalized = "النص العربي المعدل"
        
        # Should be cache miss initially
        assert self.cache.get_normalized(text) is None
        
        # Cache the result
        self.cache.cache_normalized(text, normalized)
        
        # Should be cache hit now
        assert self.cache.get_normalized(text) == normalized
    
    def test_sentiment_cache(self):
        """Test sentiment analysis caching"""
        text = "الخدمة ممتازة"
        sentiment = {"score": 0.8, "confidence": 0.9}
        
        assert self.cache.get_sentiment(text) is None
        self.cache.cache_sentiment(text, sentiment)
        assert self.cache.get_sentiment(text) == sentiment
    
    def test_cache_key_consistency(self):
        """Test cache key consistency for same text"""
        text = "النص العربي"
        
        # Cache normalization
        self.cache.cache_normalized(text, "normalized")
        
        # Same text should hit cache
        assert self.cache.get_normalized(text) == "normalized"
        
        # Different text should miss
        assert self.cache.get_normalized("نص مختلف") is None
    
    def test_cache_statistics(self):
        """Test cache statistics"""
        text = "اختبار"
        
        # Generate some cache activity
        self.cache.get_normalized(text)  # Miss
        self.cache.cache_normalized(text, "cached")
        self.cache.get_normalized(text)  # Hit
        
        stats = self.cache.get_all_stats()
        assert "normalization" in stats
        assert stats["normalization"]["hits"] >= 1
        assert stats["normalization"]["misses"] >= 1
    
    def test_cache_clear(self):
        """Test cache clearing"""
        self.cache.cache_normalized("text1", "result1")
        self.cache.cache_sentiment("text2", {"score": 0.5})
        
        # Verify cached
        assert self.cache.get_normalized("text1") == "result1"
        
        # Clear all caches
        self.cache.clear_all()
        
        # Should be empty
        assert self.cache.get_normalized("text1") is None
        assert self.cache.get_sentiment("text2") is None

class TestBatchProcessor:
    """Test batch processing functionality"""
    
    @pytest.mark.asyncio
    async def test_batch_processing_basic(self):
        """Test basic batch processing"""
        processor = BatchProcessor(batch_size=3, max_wait_time=0.1)
        results = []
        
        async def callback(result):
            results.append(result)
        
        # Add requests
        await processor.add_request("text1", "normalize", callback)
        await processor.add_request("text2", "normalize", callback)
        await processor.add_request("text3", "normalize", callback)
        
        # Wait for batch processing
        await asyncio.sleep(0.2)
        
        # Should have processed all requests
        assert len(results) == 3
    
    @pytest.mark.asyncio
    async def test_batch_time_trigger(self):
        """Test batch processing triggered by time"""
        processor = BatchProcessor(batch_size=10, max_wait_time=0.1)
        results = []
        
        async def callback(result):
            results.append(result)
        
        # Add just one request
        await processor.add_request("text1", "normalize", callback)
        
        # Wait for time-based trigger
        await asyncio.sleep(0.2)
        
        # Should have processed despite not reaching batch size
        assert len(results) == 1
    
    @pytest.mark.asyncio
    async def test_batch_operation_grouping(self):
        """Test operations are grouped by type"""
        processor = BatchProcessor(batch_size=5, max_wait_time=0.1)
        normalize_results = []
        sentiment_results = []
        
        async def normalize_callback(result):
            normalize_results.append(result)
        
        async def sentiment_callback(result):
            sentiment_results.append(result)
        
        # Add mixed operations
        await processor.add_request("text1", "normalize", normalize_callback)
        await processor.add_request("text2", "sentiment", sentiment_callback)
        await processor.add_request("text3", "normalize", normalize_callback)
        
        # Wait for processing
        await asyncio.sleep(0.2)
        
        # Should have processed both types
        assert len(normalize_results) == 2
        assert len(sentiment_results) == 1

class TestOptimizedProcessing:
    """Test optimized Arabic processing functions"""
    
    @pytest.mark.asyncio
    async def test_optimize_arabic_processing(self):
        """Test optimized processing with multiple operations"""
        text = "النص العربي للاختبار"
        operations = ["normalize", "sentiment"]
        
        results = await optimize_arabic_processing(text, operations)
        
        assert isinstance(results, dict)
        assert "normalize" in results
        assert "sentiment" in results
        assert results["normalize"] is not None
        assert results["sentiment"] is not None
    
    @pytest.mark.asyncio
    async def test_processing_with_cache_hits(self):
        """Test processing with cache hits"""
        text = "نص للاختبار"
        operations = ["normalize"]
        
        # First call - should cache results
        results1 = await optimize_arabic_processing(text, operations)
        
        # Second call - should hit cache
        start_time = time.time()
        results2 = await optimize_arabic_processing(text, operations)
        end_time = time.time()
        
        # Results should be same
        assert results1["normalize"] == results2["normalize"]
        
        # Second call should be faster (cache hit)
        assert (end_time - start_time) < 0.1
    
    @pytest.mark.asyncio
    async def test_processing_error_handling(self):
        """Test error handling in optimized processing"""
        # Use invalid operation to test error handling
        results = await optimize_arabic_processing("text", ["invalid_operation"])
        
        assert "invalid_operation" in results
        # Should handle error gracefully

class TestPerformanceMonitoring:
    """Test performance monitoring"""
    
    def test_performance_metrics_recording(self):
        """Test recording performance metrics"""
        monitor = performance_monitor
        initial_count = monitor.metrics["requests_processed"]
        
        # Record some metrics
        monitor.record_request(0.1, cache_hit=True)
        monitor.record_request(0.2, cache_hit=False)
        monitor.record_request(0.05, cache_hit=True, error=True)
        
        # Check metrics updated
        assert monitor.metrics["requests_processed"] == initial_count + 3
        assert monitor.metrics["cache_hits"] >= 2
        assert monitor.metrics["cache_misses"] >= 1
        assert monitor.metrics["errors"] >= 1
    
    def test_performance_metrics_calculation(self):
        """Test performance metrics calculations"""
        monitor = performance_monitor
        
        metrics = monitor.get_metrics()
        
        assert "requests_processed" in metrics
        assert "average_processing_time" in metrics
        assert "cache_hit_rate" in metrics
        assert "error_rate" in metrics
        assert "uptime_seconds" in metrics
        assert "requests_per_second" in metrics
        
        # Verify calculations
        if metrics["requests_processed"] > 0:
            assert 0 <= metrics["cache_hit_rate"] <= 1
            assert 0 <= metrics["error_rate"] <= 1
            assert metrics["uptime_seconds"] > 0

class TestPerformanceBenchmarks:
    """Performance benchmark tests"""
    
    def test_arabic_processing_performance(self):
        """Test Arabic processing performance benchmarks"""
        from utils.arabic_processor import ArabicTextProcessor
        
        processor = ArabicTextProcessor()
        text = "النص العربي الطويل للاختبار " * 100  # ~3000 characters
        
        # Test normalization performance
        start_time = time.time()
        normalized = processor.normalize_arabic(text)
        normalization_time = time.time() - start_time
        
        assert normalization_time < 1.0  # Should complete within 1 second
        assert isinstance(normalized, str)
        assert len(normalized) > 0
        
        # Test reshaping performance
        start_time = time.time()
        reshaped = processor.reshape_for_display(text)
        reshaping_time = time.time() - start_time
        
        assert reshaping_time < 1.0
        assert isinstance(reshaped, str)
    
    def test_cache_performance_benchmark(self):
        """Test cache performance under load"""
        cache = ArabicTextCache(max_size=100)
        
        # Generate test data
        test_texts = [f"النص العربي {i}" for i in range(200)]
        
        # Test cache performance
        start_time = time.time()
        
        # Cache some items
        for i, text in enumerate(test_texts[:50]):
            cache.cache_normalized(text, f"normalized_{i}")
        
        # Access cached items (should be fast)
        hit_count = 0
        for text in test_texts[:50]:
            if cache.get_normalized(text):
                hit_count += 1
        
        end_time = time.time()
        
        assert hit_count == 50  # All should be cache hits
        assert (end_time - start_time) < 0.5  # Should be fast
    
    @pytest.mark.asyncio
    async def test_concurrent_processing_performance(self):
        """Test performance under concurrent load"""
        text = "النص العربي للاختبار المتزامن"
        operations = ["normalize", "sentiment"]
        
        # Create multiple concurrent processing tasks
        tasks = []
        for i in range(10):
            task = optimize_arabic_processing(text, operations)
            tasks.append(task)
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # All tasks should complete
        assert len(results) == 10
        
        # Should complete within reasonable time
        assert (end_time - start_time) < 5.0
        
        # Results should be consistent
        first_result = results[0]
        for result in results[1:]:
            assert result["normalize"] == first_result["normalize"]
    
    def test_memory_usage_stability(self):
        """Test memory usage remains stable under load"""
        import sys
        
        cache = ArabicTextCache(max_size=50)
        
        # Get initial memory footprint
        initial_size = sys.getsizeof(cache.normalization_cache.cache)
        
        # Process many items
        for i in range(1000):
            text = f"النص العربي {i}"
            normalized = f"معدل {i}"
            cache.cache_normalized(text, normalized)
        
        # Check memory didn't grow excessively
        final_size = sys.getsizeof(cache.normalization_cache.cache)
        
        # Memory should be bounded by cache size
        assert final_size < initial_size * 100  # Reasonable upper bound
        
        # Cache should maintain max size
        stats = cache.get_all_stats()
        assert stats["normalization"]["size"] <= 50