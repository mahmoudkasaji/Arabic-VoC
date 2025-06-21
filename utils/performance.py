"""
Performance optimization utilities for Arabic VoC platform
Caching, batching, and optimization for Arabic text processing
"""

import asyncio
import time
import functools
import hashlib
from typing import Dict, List, Optional, Any, Callable
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)

class LRUCache:
    """Thread-safe LRU Cache implementation"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache = OrderedDict()
        self.stats = {"hits": 0, "misses": 0}
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        if key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self.stats["hits"] += 1
            return self.cache[key]
        
        self.stats["misses"] += 1
        return None
    
    def put(self, key: str, value: Any) -> None:
        """Put item in cache"""
        if key in self.cache:
            # Update existing
            self.cache[key] = value
            self.cache.move_to_end(key)
        else:
            # Add new
            if len(self.cache) >= self.max_size:
                # Remove least recently used
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
        self.keyword_cache = LRUCache(max_size)
    
    def _hash_text(self, text: str) -> str:
        """Create hash key for text"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def get_normalized(self, text: str) -> Optional[str]:
        """Get cached normalized text"""
        key = self._hash_text(text)
        return self.normalization_cache.get(key)
    
    def cache_normalized(self, text: str, normalized: str) -> None:
        """Cache normalized text"""
        key = self._hash_text(text)
        self.normalization_cache.put(key, normalized)
    
    def get_sentiment(self, text: str) -> Optional[Dict[str, Any]]:
        """Get cached sentiment analysis"""
        key = self._hash_text(text)
        return self.sentiment_cache.get(key)
    
    def cache_sentiment(self, text: str, sentiment: Dict[str, Any]) -> None:
        """Cache sentiment analysis"""
        key = self._hash_text(text)
        self.sentiment_cache.put(key, sentiment)
    
    def get_reshaped(self, text: str) -> Optional[str]:
        """Get cached reshaped text"""
        key = self._hash_text(text)
        return self.reshaping_cache.get(key)
    
    def cache_reshaped(self, text: str, reshaped: str) -> None:
        """Cache reshaped text"""
        key = self._hash_text(text)
        self.reshaping_cache.put(key, reshaped)
    
    def get_keywords(self, text: str) -> Optional[List[str]]:
        """Get cached keywords"""
        key = self._hash_text(text)
        return self.keyword_cache.get(key)
    
    def cache_keywords(self, text: str, keywords: List[str]) -> None:
        """Cache keywords"""
        key = self._hash_text(text)
        self.keyword_cache.put(key, keywords)
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all caches"""
        return {
            "normalization": self.normalization_cache.get_stats(),
            "sentiment": self.sentiment_cache.get_stats(),
            "reshaping": self.reshaping_cache.get_stats(),
            "keywords": self.keyword_cache.get_stats()
        }
    
    def clear_all(self) -> None:
        """Clear all caches"""
        self.normalization_cache.clear()
        self.sentiment_cache.clear()
        self.reshaping_cache.clear()
        self.keyword_cache.clear()

class BatchProcessor:
    """Batch processor for efficient Arabic text processing"""
    
    def __init__(self, batch_size: int = 10, max_wait_time: float = 1.0):
        self.batch_size = batch_size
        self.max_wait_time = max_wait_time
        self.pending_requests = []
        self.processing = False
    
    async def add_request(self, text: str, operation: str, callback: Callable) -> None:
        """Add request to batch processing queue"""
        request = {
            "text": text,
            "operation": operation,
            "callback": callback,
            "timestamp": time.time()
        }
        
        self.pending_requests.append(request)
        
        # Trigger processing if batch is full or max wait time exceeded
        if (len(self.pending_requests) >= self.batch_size or 
            self._should_process_batch()):
            await self._process_batch()
    
    def _should_process_batch(self) -> bool:
        """Check if batch should be processed based on time"""
        if not self.pending_requests:
            return False
        
        oldest_request = min(self.pending_requests, key=lambda x: x["timestamp"])
        return (time.time() - oldest_request["timestamp"]) >= self.max_wait_time
    
    async def _process_batch(self) -> None:
        """Process current batch of requests"""
        if self.processing or not self.pending_requests:
            return
        
        self.processing = True
        current_batch = self.pending_requests.copy()
        self.pending_requests.clear()
        
        try:
            # Group by operation type
            operations = {}
            for request in current_batch:
                op_type = request["operation"]
                if op_type not in operations:
                    operations[op_type] = []
                operations[op_type].append(request)
            
            # Process each operation type in batch
            for op_type, requests in operations.items():
                await self._process_operation_batch(op_type, requests)
        
        except Exception as e:
            logger.error(f"Batch processing error: {e}")
        
        finally:
            self.processing = False
    
    async def _process_operation_batch(self, operation: str, requests: List[Dict]) -> None:
        """Process batch of requests for specific operation"""
        if operation == "normalize":
            await self._batch_normalize(requests)
        elif operation == "sentiment":
            await self._batch_sentiment_analysis(requests)
        elif operation == "reshape":
            await self._batch_reshape(requests)
        elif operation == "keywords":
            await self._batch_extract_keywords(requests)
    
    async def _batch_normalize(self, requests: List[Dict]) -> None:
        """Batch normalize Arabic texts"""
        from utils.arabic_processor import ArabicTextProcessor
        processor = ArabicTextProcessor()
        
        for request in requests:
            try:
                result = processor.normalize_arabic(request["text"])
                await request["callback"](result)
            except Exception as e:
                logger.error(f"Normalization error: {e}")
                await request["callback"](None)
    
    async def _batch_sentiment_analysis(self, requests: List[Dict]) -> None:
        """Batch sentiment analysis"""
        from utils.openai_client import analyze_arabic_feedback
        
        # Group texts for batch processing
        texts = [req["text"] for req in requests]
        
        try:
            results = await asyncio.get_event_loop().run_in_executor(
                None, self._batch_analyze_texts, texts
            )
            
            for request, result in zip(requests, results):
                await request["callback"](result)
                
        except Exception as e:
            logger.error(f"Batch sentiment analysis error: {e}")
            for request in requests:
                await request["callback"](None)
    
    def _batch_analyze_texts(self, texts: List[str]) -> List[Dict]:
        """Synchronous batch text analysis"""
        from utils.openai_client import batch_analyze_feedback
        return batch_analyze_feedback(texts)
    
    async def _batch_reshape(self, requests: List[Dict]) -> None:
        """Batch reshape Arabic texts"""
        from utils.arabic_processor import ArabicTextProcessor
        processor = ArabicTextProcessor()
        
        for request in requests:
            try:
                result = processor.reshape_for_display(request["text"])
                await request["callback"](result)
            except Exception as e:
                logger.error(f"Reshaping error: {e}")
                await request["callback"](None)
    
    async def _batch_extract_keywords(self, requests: List[Dict]) -> None:
        """Batch extract keywords"""
        from utils.arabic_processor import ArabicTextProcessor
        processor = ArabicTextProcessor()
        
        for request in requests:
            try:
                result = processor.extract_keywords(request["text"])
                await request["callback"](result)
            except Exception as e:
                logger.error(f"Keyword extraction error: {e}")
                await request["callback"](None)

class PerformanceMonitor:
    """Monitor and track performance metrics"""
    
    def __init__(self):
        self.metrics = {
            "requests_processed": 0,
            "total_processing_time": 0,
            "average_processing_time": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": 0
        }
        self.start_time = time.time()
    
    def record_request(self, processing_time: float, cache_hit: bool = False, error: bool = False):
        """Record performance metrics for a request"""
        self.metrics["requests_processed"] += 1
        self.metrics["total_processing_time"] += processing_time
        self.metrics["average_processing_time"] = (
            self.metrics["total_processing_time"] / self.metrics["requests_processed"]
        )
        
        if cache_hit:
            self.metrics["cache_hits"] += 1
        else:
            self.metrics["cache_misses"] += 1
        
        if error:
            self.metrics["errors"] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        uptime = time.time() - self.start_time
        total_requests = self.metrics["cache_hits"] + self.metrics["cache_misses"]
        cache_hit_rate = self.metrics["cache_hits"] / total_requests if total_requests > 0 else 0
        
        return {
            **self.metrics,
            "uptime_seconds": uptime,
            "requests_per_second": self.metrics["requests_processed"] / uptime if uptime > 0 else 0,
            "cache_hit_rate": cache_hit_rate,
            "error_rate": self.metrics["errors"] / self.metrics["requests_processed"] if self.metrics["requests_processed"] > 0 else 0
        }

# Global instances
arabic_cache = ArabicTextCache(max_size=1000)
batch_processor = BatchProcessor(batch_size=10, max_wait_time=1.0)
performance_monitor = PerformanceMonitor()

def timed_cache(cache_key_func: Callable = None, ttl_seconds: int = 3600):
    """Decorator for timed caching with Arabic text support"""
    def decorator(func):
        cache = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if cache_key_func:
                key = cache_key_func(*args, **kwargs)
            else:
                key = str(args) + str(sorted(kwargs.items()))
            
            # Check cache
            if key in cache:
                value, timestamp = cache[key]
                if time.time() - timestamp < ttl_seconds:
                    return value
                else:
                    del cache[key]
            
            # Execute function and cache result
            start_time = time.time()
            result = func(*args, **kwargs)
            processing_time = time.time() - start_time
            
            cache[key] = (result, time.time())
            performance_monitor.record_request(processing_time, cache_hit=False)
            
            return result
        
        return wrapper
    return decorator

async def optimize_arabic_processing(text: str, operations: List[str]) -> Dict[str, Any]:
    """Optimized Arabic text processing with caching and batching"""
    results = {}
    
    for operation in operations:
        start_time = time.time()
        cache_hit = False
        
        try:
            if operation == "normalize":
                cached = arabic_cache.get_normalized(text)
                if cached:
                    results[operation] = cached
                    cache_hit = True
                else:
                    from utils.arabic_processor import ArabicTextProcessor
                    processor = ArabicTextProcessor()
                    result = processor.normalize_arabic(text)
                    arabic_cache.cache_normalized(text, result)
                    results[operation] = result
            
            elif operation == "sentiment":
                cached = arabic_cache.get_sentiment(text)
                if cached:
                    results[operation] = cached
                    cache_hit = True
                else:
                    from utils.openai_client import analyze_arabic_feedback
                    result = analyze_arabic_feedback(text)
                    arabic_cache.cache_sentiment(text, result)
                    results[operation] = result
            
            elif operation == "reshape":
                cached = arabic_cache.get_reshaped(text)
                if cached:
                    results[operation] = cached
                    cache_hit = True
                else:
                    from utils.arabic_processor import ArabicTextProcessor
                    processor = ArabicTextProcessor()
                    result = processor.reshape_for_display(text)
                    arabic_cache.cache_reshaped(text, result)
                    results[operation] = result
            
            elif operation == "keywords":
                cached = arabic_cache.get_keywords(text)
                if cached:
                    results[operation] = cached
                    cache_hit = True
                else:
                    from utils.arabic_processor import ArabicTextProcessor
                    processor = ArabicTextProcessor()
                    result = processor.extract_keywords(text)
                    arabic_cache.cache_keywords(text, result)
                    results[operation] = result
        
        except Exception as e:
            logger.error(f"Error in {operation}: {e}")
            results[operation] = None
            performance_monitor.record_request(time.time() - start_time, cache_hit, error=True)
            continue
        
        processing_time = time.time() - start_time
        performance_monitor.record_request(processing_time, cache_hit)
    
    return results