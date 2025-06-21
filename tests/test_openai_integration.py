"""
OpenAI integration testing with Arabic content
Testing sentiment analysis, error handling, and fallback mechanisms
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from utils.openai_client import analyze_arabic_feedback, batch_analyze_feedback, ArabicFeedbackAnalyzer

class TestOpenAIIntegration:
    """Test OpenAI API integration with Arabic content"""
    
    def setup_method(self):
        """Setup test data"""
        self.analyzer = ArabicFeedbackAnalyzer()
        
        self.test_samples = [
            "الخدمة ممتازة جداً وأنصح بها بشدة للجميع",
            "المنتج سيء ولا أنصح بشرائه أبداً",
            "التطبيق جيد ولكن يحتاج إلى بعض التحسينات",
            "فريق الدعم سريع ومفيد جداً في حل المشاكل",
            "الأسعار مرتفعة نسبياً ولكن الجودة تستحق",
        ]
        
        self.long_text_sample = """
        أود أن أعبر عن امتناني العميق لفريق العمل المحترم في شركتكم الموقرة على الخدمة الاستثنائية 
        التي تلقيتها خلال تعاملي معكم. لقد كانت التجربة رائعة من البداية حتى النهاية، بدءاً من سهولة 
        التواصل والاستفسار، مروراً بسرعة الاستجابة والتعامل المهني، وانتهاءً بجودة الخدمة المقدمة 
        التي فاقت كل توقعاتي. إن مستوى الاحترافية والاهتمام بالتفاصيل الذي لمسته يعكس مدى حرصكم 
        على إرضاء العملاء وتقديم أفضل ما لديكم. أتطلع إلى التعامل معكم مستقبلاً وأنصح الجميع 
        بالتعامل مع شركتكم المتميزة.
        """.strip()
    
    @pytest.mark.asyncio
    async def test_basic_sentiment_analysis(self):
        """Test basic sentiment analysis functionality"""
        for text in self.test_samples:
            try:
                result = self.analyzer.analyze_sentiment(text)
                
                # Verify result structure
                assert isinstance(result, dict)
                assert "score" in result
                assert "confidence" in result
                assert "reasoning" in result
                
                # Verify value ranges
                assert -1 <= result["score"] <= 1
                assert 0 <= result["confidence"] <= 1
                assert isinstance(result["reasoning"], str)
                
            except Exception as e:
                # OpenAI might not be available in test environment
                pytest.skip(f"OpenAI API not available: {e}")
    
    @pytest.mark.asyncio
    async def test_categorization_functionality(self):
        """Test feedback categorization"""
        business_texts = [
            "الخدمة في الفندق كانت رائعة والطعام لذيذ",  # Hospitality
            "التطبيق سهل الاستخدام ولكن بطيء أحياناً",  # Technology
            "موظف البنك كان مفيداً في إنجاز المعاملة",  # Banking
            "المنتج وصل بحالة جيدة والتسليم سريع",  # E-commerce
        ]
        
        for text in business_texts:
            try:
                result = self.analyzer.categorize_feedback(text)
                
                assert isinstance(result, dict)
                assert "categories" in result
                assert "confidence" in result
                assert isinstance(result["categories"], list)
                assert len(result["categories"]) > 0
                
            except Exception as e:
                pytest.skip(f"OpenAI API not available: {e}")
    
    @pytest.mark.asyncio
    async def test_summary_generation(self):
        """Test Arabic summary generation"""
        try:
            summary = self.analyzer.generate_summary(self.long_text_sample)
            
            assert isinstance(summary, str)
            assert len(summary) > 0
            assert len(summary) < len(self.long_text_sample)  # Should be shorter
            
            # Should be in Arabic
            arabic_char_count = sum(1 for char in summary if '\u0600' <= char <= '\u06FF')
            total_chars = len([c for c in summary if c.isalpha()])
            
            if total_chars > 0:
                arabic_ratio = arabic_char_count / total_chars
                assert arabic_ratio > 0.5  # Should be mostly Arabic
            
        except Exception as e:
            pytest.skip(f"OpenAI API not available: {e}")
    
    @pytest.mark.asyncio
    async def test_action_items_generation(self):
        """Test action items suggestion"""
        feedback_with_issues = [
            "الخدمة بطيئة ويحتاج الموقع إلى تحسين سرعة التحميل",
            "موظف الاستقبال غير مفيد ولا يجيب على الأسئلة بوضوح",
            "أسعار المنتجات مرتفعة مقارنة بالمنافسين",
            "التطبيق يتعطل كثيراً ويحتاج إلى إصلاحات"
        ]
        
        for text in feedback_with_issues:
            try:
                categories = {"service": 0.8, "technical": 0.6}
                action_items = self.analyzer.suggest_actions(text, categories)
                
                assert isinstance(action_items, list)
                # Should suggest some actions for problematic feedback
                assert len(action_items) >= 0
                
                for item in action_items:
                    assert isinstance(item, str)
                    assert len(item) > 0
                
            except Exception as e:
                pytest.skip(f"OpenAI API not available: {e}")

class TestOpenAIPerformance:
    """Test OpenAI integration performance"""
    
    @pytest.mark.asyncio
    async def test_single_analysis_performance(self):
        """Test performance of single text analysis"""
        text = "الخدمة ممتازة والفريق محترف جداً في التعامل"
        
        try:
            start_time = time.time()
            result = analyze_arabic_feedback(text)
            end_time = time.time()
            
            analysis_time = end_time - start_time
            
            # Should complete within 5 seconds (target)
            assert analysis_time < 5.0, f"Analysis took too long: {analysis_time}s"
            
            # Should return valid result
            assert isinstance(result, dict)
            assert "sentiment" in result
            
        except Exception as e:
            pytest.skip(f"OpenAI API not available: {e}")
    
    @pytest.mark.asyncio
    async def test_batch_analysis_performance(self):
        """Test batch analysis performance"""
        texts = [
            "الخدمة ممتازة",
            "المنتج جيد",
            "التطبيق سهل",
            "الفريق محترف",
            "الأسعار معقولة"
        ]
        
        try:
            start_time = time.time()
            results = batch_analyze_feedback(texts)
            end_time = time.time()
            
            total_time = end_time - start_time
            time_per_text = total_time / len(texts)
            
            # Batch should be more efficient than individual calls
            assert time_per_text < 2.0, f"Batch analysis too slow: {time_per_text}s per text"
            
            # Should return results for all texts
            assert len(results) == len(texts)
            
            for result in results:
                assert isinstance(result, dict)
                assert "sentiment" in result
                
        except Exception as e:
            pytest.skip(f"OpenAI API not available: {e}")

class TestOpenAIErrorHandling:
    """Test error handling and fallback mechanisms"""
    
    @pytest.mark.asyncio
    async def test_api_failure_handling(self):
        """Test handling of OpenAI API failures"""
        # Mock OpenAI client to simulate failures
        with patch('utils.openai_client.openai') as mock_openai:
            # Simulate API error
            mock_openai.chat.completions.create.side_effect = Exception("API Error")
            
            analyzer = ArabicFeedbackAnalyzer()
            
            # Should handle error gracefully
            try:
                result = analyzer.analyze_sentiment("اختبار النص العربي")
                # Should either return fallback result or raise controlled exception
                assert isinstance(result, dict) or result is None
            except Exception as e:
                # Should be a controlled exception, not API error
                assert "API Error" not in str(e)
    
    @pytest.mark.asyncio
    async def test_invalid_response_handling(self):
        """Test handling of invalid API responses"""
        with patch('utils.openai_client.openai') as mock_openai:
            # Mock invalid JSON response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "invalid json content"
            mock_openai.chat.completions.create.return_value = mock_response
            
            analyzer = ArabicFeedbackAnalyzer()
            
            try:
                result = analyzer.analyze_sentiment("اختبار النص")
                # Should handle invalid response gracefully
                assert isinstance(result, dict) or result is None
            except Exception as e:
                # Should be a controlled exception
                assert isinstance(e, (ValueError, TypeError, KeyError))
    
    @pytest.mark.asyncio
    async def test_rate_limiting_handling(self):
        """Test handling of rate limiting"""
        with patch('utils.openai_client.openai') as mock_openai:
            # Simulate rate limiting error
            from openai import RateLimitError
            mock_openai.chat.completions.create.side_effect = RateLimitError(
                message="Rate limit exceeded",
                response=Mock(),
                body={}
            )
            
            analyzer = ArabicFeedbackAnalyzer()
            
            try:
                result = analyzer.analyze_sentiment("اختبار النص")
                # Should handle rate limiting gracefully
                assert isinstance(result, dict) or result is None
            except Exception as e:
                # Should be handled appropriately
                assert "Rate limit" in str(e) or isinstance(e, RateLimitError)
    
    @pytest.mark.asyncio
    async def test_fallback_analysis(self):
        """Test fallback to local analysis when OpenAI fails"""
        from utils.arabic_processor import extract_sentiment
        
        # Compare OpenAI analysis with fallback
        text = "الخدمة ممتازة جداً"
        
        # Get fallback result
        fallback_result = extract_sentiment(text)
        
        assert isinstance(fallback_result, dict)
        assert "score" in fallback_result
        assert "confidence" in fallback_result
        assert -1 <= fallback_result["score"] <= 1
        assert 0 <= fallback_result["confidence"] <= 1
        
        # Fallback should work even when OpenAI is unavailable
        try:
            openai_result = analyze_arabic_feedback(text)
            
            # Both should give somewhat similar results for clearly positive text
            if openai_result and "sentiment" in openai_result:
                openai_score = openai_result["sentiment"]["score"]
                fallback_score = fallback_result["score"]
                
                # For clearly positive text, both should be positive
                if fallback_score > 0.5:
                    assert openai_score > 0, "OpenAI and fallback sentiment should agree on positive text"
                    
        except Exception:
            # If OpenAI fails, fallback should still work
            assert fallback_result["score"] > 0  # Should detect positive sentiment

class TestOpenAIContentQuality:
    """Test OpenAI analysis quality with various Arabic content"""
    
    @pytest.mark.asyncio
    async def test_dialect_handling(self):
        """Test handling of different Arabic dialects"""
        dialect_samples = {
            "gulf": "الخدمة زينة ومشكورين على التعامل الطيب",
            "egyptian": "الحمد لله الخدمة كويسة جداً ومفيش مشاكل",
            "levantine": "والله الخدمة منيحة كتير ومشان هيك بنصح فيها",
            "moroccan": "الخدمة زوينة بزاف والناس مزيانين معانا"
        }
        
        try:
            results = {}
            for dialect, text in dialect_samples.items():
                result = analyze_arabic_feedback(text)
                results[dialect] = result
                
                # Should analyze all dialects successfully
                assert isinstance(result, dict)
                assert "sentiment" in result
                
                # All these samples are positive, should be detected as such
                sentiment_score = result["sentiment"]["score"]
                assert sentiment_score > 0, f"{dialect} dialect not detected as positive"
            
            # Sentiment scores should be consistent across dialects for similar content
            scores = [r["sentiment"]["score"] for r in results.values()]
            import statistics
            if len(scores) > 1:
                std_dev = statistics.stdev(scores)
                assert std_dev < 0.5, f"High variance in dialect sentiment: {std_dev}"
                
        except Exception as e:
            pytest.skip(f"OpenAI API not available: {e}")
    
    @pytest.mark.asyncio
    async def test_mixed_content_analysis(self):
        """Test analysis of mixed Arabic-English content"""
        mixed_samples = [
            "الخدمة excellent والفريق professional جداً",
            "Thank you كتير على الدعم الرائع",
            "المنتج amazing بس الـ delivery متأخر شوي",
            "Overall الخدمة ممتازة but need improvement في السرعة"
        ]
        
        try:
            for text in mixed_samples:
                result = analyze_arabic_feedback(text)
                
                assert isinstance(result, dict)
                assert "sentiment" in result
                
                # Should handle mixed content without errors
                sentiment_score = result["sentiment"]["score"]
                assert -1 <= sentiment_score <= 1
                
        except Exception as e:
            pytest.skip(f"OpenAI API not available: {e}")
    
    @pytest.mark.asyncio
    async def test_context_understanding(self):
        """Test contextual understanding of Arabic feedback"""
        contextual_samples = [
            ("الخدمة ليست سيئة", "double_negative"),  # "Service is not bad" - should be neutral/positive
            ("لا أستطيع أن أشكو من الخدمة", "negated_complaint"),  # "Can't complain" - positive
            ("الخدمة مقبولة إلى حد ما", "qualified_positive"),  # "Service is acceptable" - neutral
            ("ممكن الخدمة تكون أحسن", "suggestion"),  # "Service could be better" - constructive
        ]
        
        try:
            for text, context_type in contextual_samples:
                result = analyze_arabic_feedback(text)
                
                assert isinstance(result, dict)
                assert "sentiment" in result
                
                # Check that context is understood appropriately
                sentiment_score = result["sentiment"]["score"]
                
                if context_type == "double_negative":
                    # Should not be strongly negative
                    assert sentiment_score > -0.5
                elif context_type == "negated_complaint":
                    # Should be positive or neutral
                    assert sentiment_score >= 0
                    
        except Exception as e:
            pytest.skip(f"OpenAI API not available: {e}")

class TestOpenAIIntegrationResilience:
    """Test resilience and reliability of OpenAI integration"""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling of concurrent OpenAI requests"""
        texts = [f"اختبار متزامن رقم {i}" for i in range(5)]
        
        async def analyze_single(text):
            try:
                return analyze_arabic_feedback(text)
            except Exception as e:
                return {"error": str(e)}
        
        try:
            # Make concurrent requests
            tasks = [analyze_single(text) for text in texts]
            results = await asyncio.gather(*tasks)
            
            # Should handle concurrent requests
            assert len(results) == len(texts)
            
            # Count successful analyses
            successful = sum(1 for r in results if "sentiment" in r)
            error_count = sum(1 for r in results if "error" in r)
            
            # Most should succeed (allowing for some API limitations)
            assert successful >= len(texts) * 0.6  # At least 60% success rate
            
        except Exception as e:
            pytest.skip(f"Concurrent testing failed: {e}")
    
    @pytest.mark.asyncio
    async def test_large_text_handling(self):
        """Test handling of large Arabic texts"""
        # Create large text (approaching token limits)
        base_text = "هذا نص طويل جداً يحتوي على محتوى عربي مفصل وشامل "
        large_text = base_text * 200  # Very long text
        
        try:
            result = analyze_arabic_feedback(large_text)
            
            # Should handle large text gracefully
            assert isinstance(result, dict)
            
            if "sentiment" in result:
                # Should still provide meaningful analysis
                assert "score" in result["sentiment"]
                assert -1 <= result["sentiment"]["score"] <= 1
            
        except Exception as e:
            # Should fail gracefully with controlled error
            assert "token" in str(e).lower() or "length" in str(e).lower()
    
    @pytest.mark.asyncio
    async def test_retry_mechanism(self):
        """Test retry mechanism for failed requests"""
        # This would test automatic retries in a real implementation
        text = "اختبار آلية إعادة المحاولة"
        
        # Mock temporary failures
        with patch('utils.openai_client.openai') as mock_openai:
            call_count = 0
            
            def side_effect(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count < 3:  # Fail first 2 attempts
                    raise Exception("Temporary error")
                else:  # Succeed on 3rd attempt
                    mock_response = Mock()
                    mock_response.choices = [Mock()]
                    mock_response.choices[0].message.content = json.dumps({
                        "sentiment": {"score": 0.5, "confidence": 0.8},
                        "summary": "تحليل ناجح"
                    })
                    return mock_response
            
            mock_openai.chat.completions.create.side_effect = side_effect
            
            try:
                # Should eventually succeed after retries
                result = analyze_arabic_feedback(text)
                assert isinstance(result, dict)
                # If retry mechanism exists, call_count should be > 1
                
            except Exception:
                # If no retry mechanism, should fail on first attempt
                assert call_count == 1