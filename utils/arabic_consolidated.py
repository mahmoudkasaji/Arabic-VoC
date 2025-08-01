"""
Consolidated Arabic Processing Utilities
Combines functionality from arabic_processor.py, arabic_utils.py, and simple_arabic_analyzer.py
"""

import re
import logging
from typing import Dict, Any, Optional
import arabic_reshaper
from bidi.algorithm import get_display

logger = logging.getLogger(__name__)

class ArabicTextProcessor:
    """Unified Arabic text processing - consolidates 3 separate modules"""
    
    def __init__(self):
        # Arabic character patterns
        self.arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+')
        self.diacritic_pattern = re.compile(r'[\u064B-\u0652\u0670\u0640]')
        
        # Common normalizations
        self.normalizations = {
            'ا': ['أ', 'إ', 'آ', 'ٱ'],
            'ه': ['ة'],
            'ي': ['ى', 'ئ'],
            'و': ['ؤ']
        }
    
    def is_arabic_text(self, text: str) -> bool:
        """Check if text contains Arabic characters"""
        if not text:
            return False
        return bool(self.arabic_pattern.search(text))
    
    def detect_language(self, text: str) -> str:
        """Simple language detection"""
        if not text:
            return "unknown"
        
        arabic_chars = len(self.arabic_pattern.findall(text))
        total_chars = len([c for c in text if c.isalpha()])
        
        if total_chars == 0:
            return "unknown"
        
        arabic_ratio = arabic_chars / total_chars
        return "ar" if arabic_ratio > 0.5 else "en" if arabic_ratio < 0.2 else "mixed"
    
    def normalize_text(self, text: str) -> str:
        """Normalize Arabic text for processing"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Apply normalizations
        for target, variants in self.normalizations.items():
            for variant in variants:
                text = text.replace(variant, target)
        
        # Remove diacritics and tatweel
        text = self.diacritic_pattern.sub('', text)
        text = text.replace('\u0640', '')  # tatweel
        
        return text
    
    def format_for_display(self, text: str) -> str:
        """Format Arabic text for RTL display"""
        if not text or not self.is_arabic_text(text):
            return text
        
        try:
            reshaped_text = arabic_reshaper.reshape(text)
            return get_display(reshaped_text)
        except Exception as e:
            logger.error(f"Error formatting Arabic text: {e}")
            return text
    
    def clean_for_analysis(self, text: str) -> str:
        """Clean text for AI analysis while preserving meaning"""
        if not text:
            return ""
        
        # Normalize but preserve structure
        text = self.normalize_text(text)
        
        # Remove excessive punctuation
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        text = re.sub(r'[.]{2,}', '.', text)
        
        return text.strip()

# Singleton instance for easy access
arabic_processor = ArabicTextProcessor()