"""
Simple Arabic Analyzer - Minimal implementation for compatibility
Provides basic Arabic text analysis functionality
"""

import logging
from typing import Dict, Any, Optional
from utils.arabic_processor import ArabicTextProcessor

logger = logging.getLogger(__name__)

class SimpleArabicAnalyzer:
    """Simple Arabic text analysis for basic sentiment and language detection"""
    
    def __init__(self):
        self.processor = ArabicTextProcessor()
        
        # Basic sentiment keywords (Arabic)
        self.positive_keywords = [
            "ممتاز", "رائع", "جيد", "مفيد", "سعيد", "راضي", "أحب", "أعجبني", "شكرا"
        ]
        
        self.negative_keywords = [
            "سيء", "فظيع", "محبط", "مشكلة", "خطأ", "غاضب", "لا أحب", "صعب", "بطيء"
        ]
    
    def analyze_feedback(self, text: str) -> Dict[str, Any]:
        """Basic feedback analysis"""
        if not text:
            return {
                'sentiment': 'neutral',
                'confidence': 0.0,
                'language': 'unknown',
                'keywords': []
            }
        
        # Detect language
        is_arabic = self.processor.is_arabic_text(text)
        language = 'ar' if is_arabic else 'en'
        
        # Basic sentiment analysis
        text_lower = text.lower()
        positive_count = sum(1 for word in self.positive_keywords if word in text_lower)
        negative_count = sum(1 for word in self.negative_keywords if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = 'positive'
            confidence = min(0.8, 0.5 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count:
            sentiment = 'negative'
            confidence = min(0.8, 0.5 + (negative_count - positive_count) * 0.1)
        else:
            sentiment = 'neutral'
            confidence = 0.5
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'language': language,
            'keywords': []
        }

def analyze_arabic_feedback(text: str) -> Dict[str, Any]:
    """Fallback function for backward compatibility"""
    analyzer = SimpleArabicAnalyzer()
    return analyzer.analyze_feedback(text)