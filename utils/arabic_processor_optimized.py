
"""
Optimized Arabic Text Processor
Fast, efficient Arabic analysis with smart caching
"""

import time
import logging
from functools import lru_cache
from typing import Dict, Any, Optional
import asyncio

logger = logging.getLogger(__name__)

class OptimizedArabicProcessor:
    """
    High-performance Arabic text processor
    Uses caching and smart routing for better speed
    """
    
    def __init__(self):
        self.processing_stats = {
            "total_processed": 0,
            "cache_hits": 0,
            "avg_processing_time": 0
        }
    
    @lru_cache(maxsize=500)
    def analyze_text_cached(self, text: str) -> Dict[str, Any]:
        """
        Cached analysis for frequently seen text
        This makes repeat analysis instant
        """
        self.processing_stats["cache_hits"] += 1
        return self._perform_analysis(text)
    
    def _perform_analysis(self, text: str) -> Dict[str, Any]:
        """Core analysis logic"""
        start_time = time.time()
        
        try:
            # Quick text validation
            if not text or len(text.strip()) < 3:
                return {
                    "sentiment": 0.0,
                    "emotion": "محايد",
                    "category": "غير محدد",
                    "confidence": 0.5,
                    "processing_time": time.time() - start_time
                }
            
            # Smart routing based on text length
            if len(text) < 50:
                result = self._analyze_short_text(text)
            elif len(text) < 200:
                result = self._analyze_medium_text(text)
            else:
                result = self._analyze_long_text(text)
            
            # Add performance metrics
            processing_time = time.time() - start_time
            result["processing_time"] = processing_time
            
            # Update stats
            self.processing_stats["total_processed"] += 1
            self.processing_stats["avg_processing_time"] = (
                (self.processing_stats["avg_processing_time"] * 
                 (self.processing_stats["total_processed"] - 1) + processing_time) /
                self.processing_stats["total_processed"]
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return {
                "sentiment": 0.0,
                "emotion": "خطأ في التحليل",
                "category": "خطأ",
                "confidence": 0.0,
                "error": str(e),
                "processing_time": time.time() - start_time
            }
    
    def _analyze_short_text(self, text: str) -> Dict[str, Any]:
        """Fast analysis for short text (< 50 characters)"""
        
        # Quick keyword matching for common expressions
        positive_words = ["ممتاز", "رائع", "جيد", "شكرا", "أحسنتم"]
        negative_words = ["سيء", "رديء", "مشكلة", "خطأ", "لا أنصح"]
        
        text_lower = text.lower()
        
        positive_score = sum(1 for word in positive_words if word in text_lower)
        negative_score = sum(1 for word in negative_words if word in text_lower)
        
        if positive_score > negative_score:
            sentiment = 0.8
            emotion = "إيجابي"
        elif negative_score > positive_score:
            sentiment = -0.8
            emotion = "سلبي"
        else:
            sentiment = 0.0
            emotion = "محايد"
        
        return {
            "sentiment": sentiment,
            "emotion": emotion,
            "category": "تعليق سريع",
            "confidence": 0.9,
            "method": "keyword_matching"
        }
    
    def _analyze_medium_text(self, text: str) -> Dict[str, Any]:
        """Balanced analysis for medium text (50-200 characters)"""
        
        # Enhanced pattern matching
        service_keywords = ["خدمة", "دعم", "موظف", "عامل"]
        product_keywords = ["منتج", "سلعة", "جودة", "تصميم"]
        delivery_keywords = ["توصيل", "شحن", "تسليم", "وصول"]
        
        text_lower = text.lower()
        
        # Determine category
        if any(word in text_lower for word in service_keywords):
            category = "خدمة العملاء"
        elif any(word in text_lower for word in product_keywords):
            category = "جودة المنتج"
        elif any(word in text_lower for word in delivery_keywords):
            category = "التوصيل"
        else:
            category = "عام"
        
        # Sentiment analysis with more nuance
        sentiment_score = self._calculate_sentiment_score(text)
        
        if sentiment_score > 0.3:
            emotion = "راضي"
        elif sentiment_score < -0.3:
            emotion = "غير راضي"
        else:
            emotion = "محايد"
        
        return {
            "sentiment": sentiment_score,
            "emotion": emotion,
            "category": category,
            "confidence": 0.85,
            "method": "pattern_analysis"
        }
    
    def _analyze_long_text(self, text: str) -> Dict[str, Any]:
        """Comprehensive analysis for long text (> 200 characters)"""
        
        # For long text, we use more sophisticated analysis
        # but still keep it fast with smart shortcuts
        
        sentences = text.split('.')
        total_sentiment = 0
        sentence_count = len(sentences)
        
        categories = []
        emotions = []
        
        for sentence in sentences:
            if len(sentence.strip()) < 5:
                continue
                
            # Quick analysis per sentence
            sentence_result = self._analyze_medium_text(sentence)
            total_sentiment += sentence_result["sentiment"]
            categories.append(sentence_result["category"])
            emotions.append(sentence_result["emotion"])
        
        # Aggregate results
        avg_sentiment = total_sentiment / max(sentence_count, 1)
        
        # Most common category
        category = max(set(categories), key=categories.count) if categories else "عام"
        
        # Overall emotion
        if avg_sentiment > 0.4:
            emotion = "راضي جداً"
        elif avg_sentiment > 0.1:
            emotion = "راضي"
        elif avg_sentiment < -0.4:
            emotion = "غير راضي جداً"
        elif avg_sentiment < -0.1:
            emotion = "غير راضي"
        else:
            emotion = "محايد"
        
        return {
            "sentiment": avg_sentiment,
            "emotion": emotion,
            "category": category,
            "confidence": 0.8,
            "method": "comprehensive_analysis",
            "sentences_analyzed": sentence_count
        }
    
    def _calculate_sentiment_score(self, text: str) -> float:
        """Calculate sentiment score using optimized word lists"""
        
        positive_indicators = [
            "ممتاز", "رائع", "جيد", "مفيد", "سريع", "محترف", 
            "شكرا", "أنصح", "راضي", "مرتاح", "ودود"
        ]
        
        negative_indicators = [
            "سيء", "رديء", "بطيء", "مشكلة", "خطأ", "غاضب",
            "لا أنصح", "محبط", "صعب", "معقد", "غير مفيد"
        ]
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_indicators if word in text_lower)
        negative_count = sum(1 for word in negative_indicators if word in text_lower)
        
        # Normalize based on text length
        text_length = len(text.split())
        positive_ratio = positive_count / max(text_length * 0.1, 1)
        negative_ratio = negative_count / max(text_length * 0.1, 1)
        
        return min(1.0, max(-1.0, positive_ratio - negative_ratio))
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get processor performance statistics"""
        return {
            "total_processed": self.processing_stats["total_processed"],
            "cache_hits": self.processing_stats["cache_hits"],
            "cache_hit_rate": (
                self.processing_stats["cache_hits"] / 
                max(self.processing_stats["total_processed"], 1)
            ),
            "avg_processing_time": self.processing_stats["avg_processing_time"]
        }

# Global processor instance
processor = OptimizedArabicProcessor()

def analyze_arabic_feedback(text: str) -> Dict[str, Any]:
    """
    Main function for analyzing Arabic feedback
    This is what other parts of the system should use
    """
    return processor.analyze_text_cached(text)

def get_processor_stats() -> Dict[str, Any]:
    """Get performance statistics"""
    return processor.get_performance_stats()
