"""
Tests for Arabic text processing utilities
Focus on Arabic-specific edge cases and normalization
"""

import pytest
from utils.arabic_processor import ArabicTextProcessor, process_arabic_text, extract_sentiment

class TestArabicTextProcessor:
    """Test Arabic text processing functionality"""
    
    def setup_method(self):
        """Setup test instance"""
        self.processor = ArabicTextProcessor()
    
    def test_arabic_detection(self, arabic_feedback_samples):
        """Test Arabic text detection"""
        for text in arabic_feedback_samples:
            assert self.processor.is_arabic_text(text) == True
        
        # Test non-Arabic text
        assert self.processor.is_arabic_text("Hello World") == False
        assert self.processor.is_arabic_text("123456") == False
        assert self.processor.is_arabic_text("") == False
    
    def test_arabic_normalization(self, arabic_feedback_samples):
        """Test Arabic text normalization"""
        for text in arabic_feedback_samples:
            normalized = self.processor.normalize_arabic(text)
            assert isinstance(normalized, str)
            assert len(normalized) > 0
            # Normalized text should not contain problematic characters
            assert '\u200c' not in normalized  # Zero-width non-joiner
            assert '\u200d' not in normalized  # Zero-width joiner
    
    def test_reshaping_for_display(self, arabic_feedback_samples):
        """Test Arabic text reshaping for RTL display"""
        for text in arabic_feedback_samples:
            reshaped = self.processor.reshape_for_display(text)
            assert isinstance(reshaped, str)
            assert len(reshaped) >= len(text)  # Reshaping may add characters
    
    def test_edge_cases(self, arabic_edge_cases):
        """Test Arabic processing with edge cases"""
        for text in arabic_edge_cases:
            # Should not raise exceptions
            is_arabic = self.processor.is_arabic_text(text)
            assert isinstance(is_arabic, bool)
            
            if text.strip():  # Non-empty text
                normalized = self.processor.normalize_arabic(text)
                assert isinstance(normalized, str)
                
                reshaped = self.processor.reshape_for_display(text)
                assert isinstance(reshaped, str)
    
    def test_keyword_extraction(self, arabic_feedback_samples):
        """Test Arabic keyword extraction"""
        for text in arabic_feedback_samples:
            keywords = self.processor.extract_keywords(text)
            assert isinstance(keywords, list)
            # Keywords should be meaningful (more than 2 characters)
            for keyword in keywords:
                assert len(keyword) >= 2
    
    def test_emotion_detection(self, arabic_feedback_samples):
        """Test Arabic emotion word detection"""
        for text in arabic_feedback_samples:
            emotions = self.processor.detect_emotion_words(text)
            assert isinstance(emotions, dict)
            # Check for expected emotion categories
            expected_keys = ['positive', 'negative', 'neutral']
            for key in expected_keys:
                assert key in emotions
                assert isinstance(emotions[key], int)
                assert emotions[key] >= 0

class TestArabicProcessingFunctions:
    """Test standalone Arabic processing functions"""
    
    def test_process_arabic_text(self, arabic_feedback_samples):
        """Test main Arabic text processing function"""
        for text in arabic_feedback_samples:
            processed = process_arabic_text(text)
            assert isinstance(processed, str)
            assert len(processed) > 0
    
    def test_extract_sentiment(self, arabic_feedback_samples):
        """Test sentiment extraction from Arabic text"""
        for text in arabic_feedback_samples:
            sentiment = extract_sentiment(text)
            assert isinstance(sentiment, dict)
            assert 'score' in sentiment
            assert 'confidence' in sentiment
            assert isinstance(sentiment['score'], (int, float))
            assert isinstance(sentiment['confidence'], (int, float))
            assert -1 <= sentiment['score'] <= 1
            assert 0 <= sentiment['confidence'] <= 1
    
    def test_performance_large_text(self):
        """Test performance with large Arabic text"""
        large_text = "النص العربي الطويل جداً " * 1000
        
        # Should complete within reasonable time
        import time
        start_time = time.time()
        processed = process_arabic_text(large_text)
        end_time = time.time()
        
        assert isinstance(processed, str)
        assert (end_time - start_time) < 5.0  # Should complete within 5 seconds
    
    def test_memory_efficiency(self, arabic_feedback_samples):
        """Test memory efficiency with multiple texts"""
        import sys
        
        # Process multiple texts and check memory doesn't grow excessively
        initial_size = sys.getsizeof([])
        results = []
        
        for _ in range(100):
            for text in arabic_feedback_samples:
                result = process_arabic_text(text)
                results.append(result)
        
        final_size = sys.getsizeof(results)
        # Memory growth should be reasonable
        assert final_size < initial_size * 1000  # Not more than 1000x growth

class TestArabicSecurity:
    """Test security aspects of Arabic processing"""
    
    def test_malicious_input_handling(self, malicious_inputs):
        """Test handling of potentially malicious inputs"""
        processor = ArabicTextProcessor()
        
        for malicious_input in malicious_inputs:
            # Should not raise exceptions or cause security issues
            try:
                result = processor.normalize_arabic(malicious_input)
                assert isinstance(result, str)
                
                # Check that dangerous patterns are neutralized
                assert '<script>' not in result.lower()
                assert 'javascript:' not in result.lower()
                assert 'drop table' not in result.lower()
                
            except Exception as e:
                # If exception occurs, it should be a safe ValueError or similar
                assert isinstance(e, (ValueError, TypeError, UnicodeError))
    
    def test_input_length_limits(self):
        """Test input length limitations"""
        processor = ArabicTextProcessor()
        
        # Very long input should be handled gracefully
        very_long_text = "أ" * 100000  # 100k Arabic characters
        
        try:
            result = processor.normalize_arabic(very_long_text)
            # Should either process successfully or raise controlled exception
            assert isinstance(result, str) or result is None
        except Exception as e:
            # Should be a controlled exception, not system crash
            assert isinstance(e, (ValueError, MemoryError))
    
    def test_unicode_safety(self):
        """Test Unicode safety with Arabic text"""
        processor = ArabicTextProcessor()
        
        # Test various Unicode edge cases
        unicode_tests = [
            "\u0000Arabic\u0000",  # Null characters
            "\uFEFFArabic text\uFEFF",  # BOM characters
            "\u202Eاختبار\u202D",  # RTL/LTR override
            "اختبار\u061C",  # Arabic letter mark
        ]
        
        for test_text in unicode_tests:
            result = processor.normalize_arabic(test_text)
            # Should produce clean, safe output
            assert isinstance(result, str)
            assert '\u0000' not in result  # No null chars in output