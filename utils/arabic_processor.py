"""
Arabic text processing utilities
Handles Arabic text reshaping, normalization, and RTL support
"""

import re
import logging
from typing import Dict, Any, Optional
import arabic_reshaper
from bidi.algorithm import get_display

logger = logging.getLogger(__name__)

class ArabicTextProcessor:
    """Arabic text processing and normalization"""
    
    def __init__(self):
        # Configure Arabic reshaper for proper display
        self.reshaper_config = {
            'delete_harakat': False,  # Keep diacritics for better AI processing
            'support_zwj': True,      # Support zero-width joiner
            'support_zwnj': True,     # Support zero-width non-joiner
        }
        
        # Common Arabic text patterns
        self.arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+')
        self.diacritic_pattern = re.compile(r'[\u064B-\u0652\u0670\u0640]')
        
    def is_arabic_text(self, text: str) -> bool:
        """Check if text contains Arabic characters"""
        if not text:
            return False
        return bool(self.arabic_pattern.search(text))
    
    def normalize_arabic(self, text: str) -> str:
        """Normalize Arabic text for better processing"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Normalize Arabic characters
        text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        text = text.replace('ة', 'ه')
        text = text.replace('ى', 'ي')
        
        # Remove tatweel (elongation character)
        text = text.replace('\u0640', '')
        
        return text
    
    def reshape_for_display(self, text: str) -> str:
        """Reshape Arabic text for proper RTL display"""
        if not text or not self.is_arabic_text(text):
            return text
        
        try:
            # Reshape Arabic text
            reshaped_text = arabic_reshaper.reshape(text, **self.reshaper_config)
            
            # Apply bidirectional algorithm
            display_text = get_display(reshaped_text)
            
            return display_text
            
        except Exception as e:
            logger.error(f"Error reshaping Arabic text: {str(e)}")
            return text
    
    def clean_for_analysis(self, text: str) -> str:
        """Clean Arabic text for AI analysis (preserve meaning)"""
        if not text:
            return ""
        
        # Remove excessive punctuation but keep sentence structure
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        text = re.sub(r'[.]{3,}', '...', text)
        
        # Remove excessive emoji repetition
        text = re.sub(r'([\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF])\1{2,}', r'\1', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        return text
    
    def extract_keywords(self, text: str, min_length: int = 3) -> list:
        """Extract Arabic keywords from text"""
        if not text or not self.is_arabic_text(text):
            return []
        
        # Split into words and filter
        words = text.split()
        keywords = []
        
        # Common Arabic stop words (simplified list)
        stop_words = {
            'في', 'من', 'إلى', 'على', 'عن', 'مع', 'إن', 'أن', 'كان', 'كانت',
            'هذا', 'هذه', 'ذلك', 'تلك', 'التي', 'الذي', 'التي', 'الذين',
            'ما', 'لا', 'لم', 'لن', 'قد', 'قال', 'قالت', 'يقول', 'تقول',
            'كل', 'بعض', 'جميع', 'كيف', 'متى', 'أين', 'لماذا', 'ماذا'
        }
        
        for word in words:
            # Remove punctuation
            clean_word = re.sub(r'[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]', '', word)
            
            # Filter by length and stop words
            if (len(clean_word) >= min_length and 
                clean_word not in stop_words and 
                self.is_arabic_text(clean_word)):
                keywords.append(clean_word)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)
        
        return unique_keywords[:10]  # Return top 10 keywords
    
    def detect_emotion_words(self, text: str) -> Dict[str, int]:
        """Detect emotion-related words in Arabic text"""
        if not text:
            return {}
        
        # Arabic emotion word patterns
        emotion_patterns = {
            'positive': [
                'ممتاز', 'رائع', 'جميل', 'سعيد', 'مبهر', 'مذهل', 'أحب', 'أعجب',
                'شكرا', 'مشكور', 'بارك', 'نعم', 'موافق', 'ناجح', 'فرح', 'سرور'
            ],
            'negative': [
                'سيء', 'فظيع', 'مريع', 'غاضب', 'زعلان', 'حزين', 'أكره', 'لا أحب',
                'مشكلة', 'خطأ', 'فشل', 'لا', 'رفض', 'غير راضي', 'إحباط', 'قلق'
            ],
            'neutral': [
                'عادي', 'طبيعي', 'مقبول', 'لا بأس', 'ربما', 'أعتقد', 'يبدو', 'ممكن'
            ]
        }
        
        emotion_counts = {}
        text_lower = text.lower()
        
        for emotion, words in emotion_patterns.items():
            count = 0
            for word in words:
                count += text_lower.count(word)
            if count > 0:
                emotion_counts[emotion] = count
        
        return emotion_counts

# Global processor instance
arabic_processor = ArabicTextProcessor()

async def process_arabic_text(text: str) -> str:
    """Process Arabic text for analysis and display"""
    try:
        # Normalize the text
        normalized = arabic_processor.normalize_arabic(text)
        
        # Clean for analysis
        cleaned = arabic_processor.clean_for_analysis(normalized)
        
        logger.debug(f"Processed Arabic text: {len(text)} -> {len(cleaned)} characters")
        
        return cleaned
        
    except Exception as e:
        logger.error(f"Error processing Arabic text: {str(e)}")
        return text

async def extract_sentiment(text: str) -> Dict[str, Any]:
    """Extract sentiment indicators from Arabic text"""
    try:
        # Get emotion word counts
        emotions = arabic_processor.detect_emotion_words(text)
        
        # Calculate basic sentiment score
        positive_score = emotions.get('positive', 0)
        negative_score = emotions.get('negative', 0)
        neutral_score = emotions.get('neutral', 0)
        
        total_emotional_words = positive_score + negative_score + neutral_score
        
        if total_emotional_words == 0:
            sentiment_score = 0.0
            confidence = 0.1
        else:
            sentiment_score = (positive_score - negative_score) / total_emotional_words
            confidence = min(1.0, total_emotional_words / 10.0)
        
        return {
            "sentiment": sentiment_score,
            "confidence": confidence,
            "emotions": emotions,
            "keywords": arabic_processor.extract_keywords(text)
        }
        
    except Exception as e:
        logger.error(f"Error extracting sentiment: {str(e)}")
        return {
            "sentiment": 0.0,
            "confidence": 0.0,
            "emotions": {},
            "keywords": []
        }

def format_for_display(text: str) -> str:
    """Format Arabic text for web display"""
    try:
        return arabic_processor.reshape_for_display(text)
    except Exception as e:
        logger.error(f"Error formatting text for display: {str(e)}")
        return text
