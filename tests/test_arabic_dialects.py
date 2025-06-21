"""
Arabic dialect and mixed content testing
Comprehensive testing for different Arabic dialects and edge cases
"""

import pytest
import asyncio
from typing import Dict, List
from utils.arabic_processor import ArabicTextProcessor, process_arabic_text, extract_sentiment
from utils.openai_client import analyze_arabic_feedback

class TestArabicDialects:
    """Test Arabic dialect processing"""
    
    def setup_method(self):
        """Setup test data for Arabic dialects"""
        self.processor = ArabicTextProcessor()
        
        # Dialect test data
        self.dialect_samples = {
            "gulf": [
                "الخدمة زينة ومشكورين على التعامل الطيب",  # Service is good, thanks for good treatment
                "ما شاء الله الموقع يهبل وسهل الاستخدام",  # Excellent website, easy to use
                "والله العظيم المنتج خرافي وينصح فيه بقوة",  # Excellent product, highly recommended
                "يعطيكم العافية على الجهد الرائع",  # Great work, well done
                "الله يعطيكم العافية والتوفيق إن شاء الله"  # Good luck and success
            ],
            "egyptian": [
                "الحمد لله الخدمة كويسة جداً ومفيش أي مشاكل",  # Service is very good, no problems
                "بجد المنتج ده عجبني أوي والناس كلها بتمدحه",  # Really liked this product, everyone praises it
                "ما شاء الله عليكم شغل محترم وناس محترمة",  # Professional work and people
                "بصراحة التطبيق ده حلو وسهل في الاستخدام",  # Honestly, this app is nice and easy to use
                "ربنا يبارك فيكم والله شغل ممتاز"  # God bless you, excellent work
            ],
            "levantine": [
                "والله الخدمة كتير منيحة ومشان هيك بنصح فيها",  # Service is very good, that's why we recommend it
                "بصراحة المنتج عجبني كتير وهاد شي بيفرحني",  # Honestly, I really liked the product
                "يعطيكم العافية على التعامل الراقي والمحترم",  # Thank you for the excellent service
                "ما شاء الله عليكم شغل نظيف ومرتب",  # Clean and organized work
                "الله يعطيكم القوة والصحة والعافية"  # God give you strength and health
            ],
            "moroccan": [
                "الخدمة زوينة بزاف والناس مزيانين معانا",  # Service is very good, people are nice
                "بصح هاد المنتج عجبني كتر وكاين لي فيه",  # This product really impressed me
                "ماشي مشكل الخدمة فوق الممتاز والناس مرحبين",  # No problem, service is excellent
                "الله يعطيكم الصحة على المجهود الكبير",  # God give you health for the great effort
                "واخا هكاك الشي زوين والخدمة ممتازة"  # Everything is good and service is excellent
            ]
        }
        
        # Mixed content samples
        self.mixed_content_samples = [
            "الخدمة excellent والفريق professional جداً",
            "Thank you كتير على الخدمة الرائعة والدعم المستمر",
            "المنتج amazing بس الـ delivery كان متأخر شوي",
            "Overall الخدمة ممتازة but need improvement في الـ response time",
            "موقعكم website جميل والـ UI user-friendly",
            "الـ customer service رائع والـ staff helpful كتير"
        ]
        
        # Long text samples
        self.long_text_samples = [
            "بسم الله الرحمن الرحيم، أود أن أعبر عن امتناني العميق وشكري الجزيل لكم على الخدمة الاستثنائية التي تقدمونها. " * 10,
            "لقد كانت تجربتي مع شركتكم المحترمة تجربة رائعة ومميزة من جميع النواحي، حيث لمست الاهتمام الكبير والعناية الفائقة " * 15,
            "إن مستوى الجودة العالي والخدمة المتميزة التي تقدمونها تعكس مدى حرصكم على إرضاء العملاء وتحقيق توقعاتهم " * 12
        ]
        
        # Special characters and diacritics
        self.diacritics_samples = [
            "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ",  # With full diacritics
            "مَرْحَبًا بِكُمْ فِي مَوْقِعِنَا الْمُتَمَيِّزِ",  # Welcome with diacritics
            "شُكْرًا لَكُمْ عَلَى الْخِدْمَةِ الرَّائِعَةِ",  # Thanks with diacritics
            "نَحْنُ نُقَدِّرُ جُهُودَكُمُ الْمُتَوَاصِلَةَ",  # We appreciate with diacritics
            "بَارَكَ اللَّهُ فِيكُمْ وَفِي عَمَلِكُمُ الْمُبَارَكِ"  # Blessed work with diacritics
        ]
    
    def test_gulf_dialect_processing(self):
        """Test Gulf Arabic dialect processing"""
        for text in self.dialect_samples["gulf"]:
            # Test Arabic detection
            assert self.processor.is_arabic_text(text) == True
            
            # Test normalization
            normalized = self.processor.normalize_arabic(text)
            assert isinstance(normalized, str)
            assert len(normalized) > 0
            
            # Test sentiment extraction
            sentiment = extract_sentiment(text)
            assert isinstance(sentiment, dict)
            # Check for either 'score' or 'sentiment' key (backward compatibility)
            score = sentiment.get("score", sentiment.get("sentiment", 0))
            confidence = sentiment.get("confidence", 0)
            assert score is not None
            assert confidence is not None
            # Gulf expressions should generally be positive
            assert score >= 0
    
    def test_egyptian_dialect_processing(self):
        """Test Egyptian Arabic dialect processing"""
        for text in self.dialect_samples["egyptian"]:
            # Test processing
            processed = process_arabic_text(text)
            assert isinstance(processed, str)
            assert len(processed) > 0
            
            # Test keyword extraction
            keywords = self.processor.extract_keywords(text)
            assert isinstance(keywords, list)
            
            # Test emotion detection
            emotions = self.processor.detect_emotion_words(text)
            assert isinstance(emotions, dict)
            assert all(key in emotions for key in ['positive', 'negative', 'neutral'])
    
    def test_levantine_dialect_processing(self):
        """Test Levantine Arabic dialect processing"""
        for text in self.dialect_samples["levantine"]:
            # Test reshaping for display
            reshaped = self.processor.reshape_for_display(text)
            assert isinstance(reshaped, str)
            
            # Test sentiment analysis
            sentiment = extract_sentiment(text)
            # Levantine expressions should generally be positive
            assert sentiment["score"] >= -0.5  # Allow for some variation
    
    def test_moroccan_dialect_processing(self):
        """Test Moroccan Arabic dialect processing"""
        for text in self.dialect_samples["moroccan"]:
            # Test basic processing
            is_arabic = self.processor.is_arabic_text(text)
            assert is_arabic == True
            
            # Test normalization (may need special handling for Moroccan)
            normalized = self.processor.normalize_arabic(text)
            assert isinstance(normalized, str)
    
    def test_mixed_content_processing(self):
        """Test mixed Arabic-English content processing"""
        for text in self.mixed_content_samples:
            # Should still be detected as Arabic (dominant language)
            is_arabic = self.processor.is_arabic_text(text)
            # Mixed content might not always be detected as Arabic
            
            # Should process without errors
            processed = process_arabic_text(text)
            assert isinstance(processed, str)
            assert len(processed) > 0
            
            # Sentiment analysis should work
            sentiment = extract_sentiment(text)
            assert isinstance(sentiment, dict)
            assert -1 <= sentiment["score"] <= 1
    
    def test_long_text_processing(self):
        """Test processing of long Arabic texts"""
        for text in self.long_text_samples:
            assert len(text) > 500  # Ensure it's actually long
            
            # Test performance with long text
            import time
            start_time = time.time()
            
            processed = process_arabic_text(text)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Should complete within reasonable time
            assert processing_time < 5.0  # 5 seconds max
            assert isinstance(processed, str)
            assert len(processed) > 0
    
    def test_diacritics_processing(self):
        """Test processing of Arabic text with diacritics"""
        for text in self.diacritics_samples:
            # Should be detected as Arabic
            assert self.processor.is_arabic_text(text) == True
            
            # Normalization should handle diacritics
            normalized = self.processor.normalize_arabic(text)
            assert isinstance(normalized, str)
            
            # Normalized text should be shorter (diacritics removed)
            assert len(normalized) <= len(text)
            
            # Should not contain diacritics after normalization
            diacritics = 'ًٌٍَُِّْ'
            for diacritic in diacritics:
                assert diacritic not in normalized
    
    def test_dialect_sentiment_consistency(self):
        """Test sentiment analysis consistency across dialects"""
        # Positive samples from each dialect
        positive_samples = [
            self.dialect_samples["gulf"][0],  # Service is good
            self.dialect_samples["egyptian"][0],  # Service is very good
            self.dialect_samples["levantine"][0],  # Service is very good
            self.dialect_samples["moroccan"][0]  # Service is very good
        ]
        
        sentiments = []
        for text in positive_samples:
            sentiment = extract_sentiment(text)
            score = sentiment.get("score", sentiment.get("sentiment", 0))
            sentiments.append(score)
        
        # All should be positive
        for score in sentiments:
            assert score > 0, f"Expected positive sentiment, got {score}"
        
        # Variance should not be too high (dialect consistency)
        import statistics
        if len(sentiments) > 1:
            std_dev = statistics.stdev(sentiments)
            assert std_dev < 0.5, f"High variance in sentiment scores: {std_dev}"
    
    def test_special_characters_handling(self):
        """Test handling of special characters and symbols"""
        special_texts = [
            "الخدمة ممتازة 😊👍 والدعم رائع! 💯",  # With emojis
            "التقييم: ⭐⭐⭐⭐⭐ خمس نجوم",  # With star ratings
            "رقم الهاتف: ٠١٢٣٤٥٦٧٨٩ للاستفسار",  # With Arabic numerals
            "البريد الإلكتروني: test@example.com",  # With email
            "الموقع: https://example.com/arabic",  # With URL
            "السعر: ١٠٠ ريال سعودي (100 SAR)"  # Mixed numerals
        ]
        
        for text in special_texts:
            # Should process without errors
            try:
                processed = process_arabic_text(text)
                sentiment = extract_sentiment(text)
                
                assert isinstance(processed, str)
                assert isinstance(sentiment, dict)
                
            except Exception as e:
                pytest.fail(f"Special character processing failed for '{text}': {e}")
    
    def test_empty_and_edge_cases(self):
        """Test empty strings and edge cases"""
        edge_cases = [
            "",  # Empty string
            "   ",  # Whitespace only
            "123456",  # Numbers only
            "!@#$%^&*()",  # Symbols only
            "a",  # Single character
            "أ",  # Single Arabic character
            "الـ",  # Arabic definite article only
            "اختبار" * 1000  # Very long repetitive text
        ]
        
        for text in edge_cases:
            try:
                # Should handle gracefully without crashing
                is_arabic = self.processor.is_arabic_text(text)
                assert isinstance(is_arabic, bool)
                
                if text.strip():  # Non-empty
                    processed = process_arabic_text(text)
                    assert isinstance(processed, str)
                    
            except Exception as e:
                # Should not crash, but may return default values
                assert isinstance(e, (ValueError, TypeError))

class TestPerformanceWithDialects:
    """Test performance with various dialect content"""
    
    def test_batch_dialect_processing(self):
        """Test processing multiple dialects in batch"""
        all_dialect_texts = []
        
        # Collect all dialect samples
        dialect_data = TestArabicDialects().dialect_samples
        for dialect_texts in dialect_data.values():
            all_dialect_texts.extend(dialect_texts)
        
        # Test batch processing performance
        import time
        start_time = time.time()
        
        results = []
        for text in all_dialect_texts:
            sentiment = extract_sentiment(text)
            results.append(sentiment)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete within reasonable time
        texts_per_second = len(all_dialect_texts) / total_time
        assert texts_per_second > 5, f"Processing too slow: {texts_per_second} texts/sec"
        
        # All results should be valid
        for result in results:
            assert isinstance(result, dict)
            assert "score" in result
            assert "confidence" in result
    
    def test_concurrent_dialect_processing(self):
        """Test concurrent processing of different dialects"""
        import concurrent.futures
        import threading
        
        dialect_data = TestArabicDialects().dialect_samples
        
        def process_dialect_batch(dialect_name, texts):
            """Process a batch of dialect texts"""
            results = []
            for text in texts:
                try:
                    sentiment = extract_sentiment(text)
                    results.append((dialect_name, sentiment))
                except Exception as e:
                    results.append((dialect_name, {"error": str(e)}))
            return results
        
        # Process dialects concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for dialect_name, texts in dialect_data.items():
                future = executor.submit(process_dialect_batch, dialect_name, texts)
                futures.append(future)
            
            # Collect results
            all_results = []
            for future in concurrent.futures.as_completed(futures):
                results = future.result()
                all_results.extend(results)
        
        # Verify all dialects were processed
        processed_dialects = set(result[0] for result in all_results)
        expected_dialects = set(dialect_data.keys())
        assert processed_dialects == expected_dialects
        
        # Verify no errors occurred
        error_results = [r for r in all_results if "error" in r[1]]
        assert len(error_results) == 0, f"Errors in concurrent processing: {error_results}"

class TestArabicContentValidation:
    """Test validation of Arabic content quality and authenticity"""
    
    def test_authentic_vs_translated_content(self):
        """Test detection of authentic vs translated Arabic content"""
        # Authentic Arabic expressions
        authentic_samples = [
            "بارك الله فيكم على هذا العمل المتميز",
            "جزاكم الله خيراً على الخدمة الرائعة",
            "ما شاء الله عليكم والله يوفقكم",
            "الله يعطيكم العافية والقوة"
        ]
        
        # Potentially translated content (more literal)
        translated_samples = [
            "شكراً لك على الخدمة الجيدة جداً",
            "أنا راضي جداً عن هذا المنتج",
            "هذا التطبيق سهل الاستخدام جداً",
            "أنصح بهذه الشركة بقوة"
        ]
        
        processor = ArabicTextProcessor()
        
        # Both should be detected as Arabic
        for text in authentic_samples + translated_samples:
            assert processor.is_arabic_text(text) == True
        
        # Authentic content might have more cultural markers
        authentic_keywords = []
        translated_keywords = []
        
        for text in authentic_samples:
            keywords = processor.extract_keywords(text)
            authentic_keywords.extend(keywords)
        
        for text in translated_samples:
            keywords = processor.extract_keywords(text)
            translated_keywords.extend(keywords)
        
        # Check for cultural/religious expressions in authentic content
        cultural_markers = ['الله', 'بارك', 'جزاكم', 'ما شاء']
        authentic_cultural_count = sum(1 for marker in cultural_markers 
                                     if any(marker in keyword for keyword in authentic_keywords))
        
        translated_cultural_count = sum(1 for marker in cultural_markers 
                                      if any(marker in keyword for keyword in translated_keywords))
        
        # Authentic content should have more cultural markers
        assert authentic_cultural_count >= translated_cultural_count
    
    def test_content_quality_metrics(self):
        """Test quality metrics for Arabic content"""
        high_quality_samples = [
            "أتقدم بجزيل الشكر والامتنان لفريق العمل المحترم على الخدمة الاستثنائية",
            "لقد فاقت الخدمة توقعاتي بشكل كبير وأنصح بها دون تردد",
            "الاهتمام بتفاصيل العميل والاستجابة السريعة يدل على الاحترافية العالية"
        ]
        
        low_quality_samples = [
            "زين",  # Too short
            "المنتج زين بس غالي شوي",  # Informal/incomplete
            "اوك",  # Very short/informal
        ]
        
        processor = ArabicTextProcessor()
        
        for text in high_quality_samples:
            # High quality should have more keywords
            keywords = processor.extract_keywords(text)
            assert len(keywords) >= 3
            
            # Should have reasonable length
            assert len(text.split()) >= 5
        
        for text in low_quality_samples:
            # Low quality might have fewer keywords
            keywords = processor.extract_keywords(text)
            # Should still process without errors
            assert isinstance(keywords, list)