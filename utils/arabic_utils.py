"""
Arabic Utilities - Consolidated Arabic processing
Phase 2: Simplified Arabic processing utilities
"""

import re
import logging
from typing import Optional, Dict, Any
import arabic_reshaper
from bidi.algorithm import get_display

logger = logging.getLogger(__name__)

class ArabicProcessor:
    """Unified Arabic text processing - simplified from 4 modules into 1"""
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """Basic Arabic text normalization"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Basic Arabic normalization (simplified from advanced NLP)
        text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        text = text.replace('ة', 'ه')  # Taa marbuta normalization
        text = text.replace('ي', 'ى')  # Yaa normalization
        
        # Remove diacritics (simplified)
        diacritics = '\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652\u0653\u0654\u0655\u0656\u0657\u0658\u0659\u065A\u065B\u065C\u065D\u065E\u065F'
        text = ''.join(c for c in text if c not in diacritics)
        
        return text.strip()
    
    @staticmethod
    def detect_language(text: str) -> str:
        """Simple language detection"""
        if not text:
            return "unknown"
        
        # Count Arabic characters
        arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
        latin_chars = sum(1 for c in text if c.isalpha() and not ('\u0600' <= c <= '\u06FF'))
        
        total_chars = arabic_chars + latin_chars
        if total_chars == 0:
            return "unknown"
        
        arabic_ratio = arabic_chars / total_chars
        
        if arabic_ratio > 0.7:
            return "ar"
        elif arabic_ratio < 0.3:
            return "en"
        else:
            return "mixed"
    
    @staticmethod
    def format_rtl(text: str) -> str:
        """Format Arabic text for RTL display"""
        if not text:
            return ""
        
        try:
            # Reshape Arabic text for proper display
            reshaped_text = arabic_reshaper.reshape(text)
            # Apply bidirectional algorithm
            display_text = get_display(reshaped_text)
            return display_text
        except Exception as e:
            logger.error(f"RTL formatting failed: {e}")
            return text
    
    @staticmethod
    def is_arabic(text: str) -> bool:
        """Check if text is primarily Arabic"""
        if not text:
            return False
        
        arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
        return arabic_chars > len(text) * 0.3
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean text for analysis (simplified from advanced processing)"""
        if not text:
            return ""
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove extra punctuation (but keep Arabic punctuation)
        text = re.sub(r'[^\w\s\u0600-\u06FF\u0660-\u0669.,!?؟]', ' ', text)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    @staticmethod
    def extract_keywords(text: str, max_keywords: int = 5) -> list:
        """Simple keyword extraction (replaces complex NLP)"""
        if not text:
            return []
        
        # Clean and normalize
        clean_text = ArabicProcessor.normalize_text(text)
        
        # Simple word splitting and filtering
        words = clean_text.split()
        
        # Filter short words and common Arabic stop words
        stop_words = {'في', 'من', 'إلى', 'على', 'عن', 'مع', 'هذا', 'هذه', 'ذلك', 'التي', 'اللي', 'كان', 'كانت'}
        
        keywords = [word for word in words 
                   if len(word) > 2 and word not in stop_words]
        
        # Return most frequent words (simple frequency-based extraction)
        from collections import Counter
        word_counts = Counter(keywords)
        
        return [word for word, count in word_counts.most_common(max_keywords)]
    
    @staticmethod
    def get_text_stats(text: str) -> Dict[str, Any]:
        """Get basic text statistics"""
        if not text:
            return {"word_count": 0, "char_count": 0, "language": "unknown"}
        
        return {
            "word_count": len(text.split()),
            "char_count": len(text),
            "language": ArabicProcessor.detect_language(text),
            "is_arabic": ArabicProcessor.is_arabic(text),
            "keywords": ArabicProcessor.extract_keywords(text, 3)
        }

# Backward compatibility functions
def normalize_arabic_text(text: str) -> str:
    """Backward compatibility"""
    return ArabicProcessor.normalize_text(text)

def detect_arabic_language(text: str) -> str:
    """Backward compatibility"""
    return ArabicProcessor.detect_language(text)

def format_arabic_rtl(text: str) -> str:
    """Backward compatibility"""
    return ArabicProcessor.format_rtl(text)