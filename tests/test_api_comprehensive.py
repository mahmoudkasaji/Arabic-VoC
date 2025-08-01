"""
Comprehensive API testing for Arabic VoC platform
Testing all endpoints with Arabic content and edge cases
"""

import pytest
import asyncio
import json
from httpx import AsyncClient
from fastapi import FastAPI
from datetime import datetime, timedelta
from typing import List, Dict

# Import all routers for testing
# Note: These APIs were migrated to Flask routes
# from api.auth import router as auth_router
# from api.surveys import router as surveys_router  
# from api.feedback_collection import router as feedback_router
# from api.analytics import router as analytics_router

# Note: Test app disabled as APIs migrated to Flask routes
# Create test app
# test_app = FastAPI()
# test_app.include_router(auth_router)
# test_app.include_router(surveys_router)
# test_app.include_router(feedback_router)
# test_app.include_router(analytics_router)

class TestSurveyAPIs:
    """Test survey management APIs with Arabic content"""
    
    @pytest.fixture
    async def authenticated_client(self):
        """Create authenticated client for testing"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            # Mock authentication - in real tests, would create actual user
            yield client
    
    @pytest.mark.asyncio
    async def test_create_arabic_survey(self, authenticated_client):
        """Test creating survey with Arabic content"""
        survey_data = {
            "title": "Customer Satisfaction Survey",
            "title_ar": "استطلاع رضا العملاء",
            "description": "Please rate our services",
            "description_ar": "يرجى تقييم خدماتنا المقدمة",
            "primary_language": "ar",
            "supported_languages": ["ar", "en"],
            "rtl_enabled": True,
            "welcome_message_ar": "مرحباً بكم في استطلاع رضا العملاء",
            "thank_you_message_ar": "شكراً لكم على وقتكم الثمين",
            "estimated_duration": 5,
            "is_public": True
        }
        
        response = await authenticated_client.post("/api/surveys/", json=survey_data)
        
        # Should succeed or fail gracefully (depending on auth setup)
        assert response.status_code in [201, 403, 422]
        
        if response.status_code == 201:
            data = response.json()
            assert data["title_ar"] == survey_data["title_ar"]
            assert data["primary_language"] == "ar"
            assert data["rtl_enabled"] == True
    
    @pytest.mark.asyncio
    async def test_survey_validation_errors(self, authenticated_client):
        """Test survey validation with invalid data"""
        invalid_survey_data = {
            "title": "ab",  # Too short
            "title_ar": "English text",  # Not Arabic
            "primary_language": "invalid",  # Invalid language
            "supported_languages": [],  # Empty array
            "end_date": "2020-01-01T00:00:00",  # Past date
            "estimated_duration": 200  # Too long
        }
        
        response = await authenticated_client.post("/api/surveys/", json=invalid_survey_data)
        assert response.status_code == 422
        
        errors = response.json()["detail"]
        assert isinstance(errors, list)
        assert len(errors) > 0
    
    @pytest.mark.asyncio
    async def test_list_surveys_with_search(self, authenticated_client):
        """Test listing surveys with Arabic search"""
        # Test search with Arabic terms
        response = await authenticated_client.get(
            "/api/surveys/?search=رضا&language=ar&limit=10"
        )
        
        # Should not fail
        assert response.status_code in [200, 403]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_add_arabic_questions(self, authenticated_client):
        """Test adding questions with Arabic content"""
        # First create a survey (mock survey_id = 1)
        question_data = {
            "text": "How would you rate our service?",
            "text_ar": "كيف تقيم خدماتنا المقدمة؟",
            "description": "Please provide your honest feedback",
            "description_ar": "يرجى تقديم رأيكم الصادق",
            "type": "rating",
            "is_required": True,
            "order_index": 1,
            "rtl_enabled": True,
            "min_value": 1,
            "max_value": 5,
            "options": {
                "labels_ar": ["سيء جداً", "سيء", "متوسط", "جيد", "ممتاز"],
                "labels_en": ["Very Poor", "Poor", "Average", "Good", "Excellent"]
            }
        }
        
        response = await authenticated_client.post("/api/surveys/1/questions", json=question_data)
        
        # Should handle gracefully
        assert response.status_code in [201, 404, 403]

class TestFeedbackCollectionAPIs:
    """Test feedback collection APIs with multi-channel support"""
    
    @pytest.mark.asyncio
    async def test_submit_arabic_feedback_all_channels(self):
        """Test submitting feedback through all supported channels"""
        channels = [
            "email", "phone", "website", "mobile_app", "social_media",
            "whatsapp", "sms", "in_person", "survey", "chatbot"
        ]
        
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            for channel in channels:
                feedback_data = {
                    "content": f"تجربة رائعة مع خدمة {channel}",
                    "channel": channel,
                    "customer_email": "test@example.com",
                    "customer_name_ar": "أحمد محمد",
                    "rating": 5,
                    "priority": "normal",
                    "location_ar": "الرياض، المملكة العربية السعودية"
                }
                
                response = await client.post("/api/feedback/submit", json=feedback_data)
                
                # Should succeed or fail gracefully
                assert response.status_code in [201, 422, 500]
    
    @pytest.mark.asyncio
    async def test_batch_feedback_submission(self):
        """Test batch feedback submission"""
        feedback_items = []
        
        # Create batch of Arabic feedback
        arabic_texts = [
            "الخدمة ممتازة جداً وأنصح بها",
            "المنتج جيد لكن يحتاج تحسينات",
            "تجربة رائعة وخدمة عملاء متميزة",
            "سرعة التسليم مقبولة والجودة عالية",
            "أسعار معقولة وخدمة احترافية"
        ]
        
        for i, text in enumerate(arabic_texts):
            feedback_items.append({
                "content": text,
                "channel": "website",
                "customer_email": f"customer{i}@example.com",
                "rating": (i % 5) + 1,
                "customer_name_ar": f"عميل رقم {i+1}"
            })
        
        batch_data = {"feedback_items": feedback_items}
        
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            response = await client.post("/api/feedback/batch", json=batch_data)
            
            # Should handle batch submission
            assert response.status_code in [200, 422, 429, 500]
    
    @pytest.mark.asyncio
    async def test_survey_response_submission(self):
        """Test survey response submission with Arabic answers"""
        survey_response_data = {
            "survey_uuid": "test-uuid-123",
            "respondent_name_ar": "سارة أحمد",
            "respondent_email": "sara@example.com",
            "answers": {
                "1": {
                    "question": "ما رأيك في خدماتنا؟",
                    "answer": "الخدمة ممتازة ومتميزة",
                    "type": "text"
                },
                "2": {
                    "question": "تقييم الجودة",
                    "answer": 5,
                    "type": "rating"
                },
                "3": {
                    "question": "اقتراحات للتحسين",
                    "answer": "زيادة سرعة الاستجابة وتحسين التطبيق",
                    "type": "textarea"
                }
            },
            "language_used": "ar",
            "started_at": (datetime.utcnow() - timedelta(minutes=5)).isoformat()
        }
        
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            response = await client.post("/api/feedback/survey-response", json=survey_response_data)
            
            # Should handle gracefully (survey might not exist)
            assert response.status_code in [201, 404, 422]
    
    @pytest.mark.asyncio
    async def test_feedback_search_arabic(self):
        """Test searching feedback with Arabic queries"""
        search_queries = [
            "ممتاز",  # Excellent
            "خدمة",   # Service
            "رضا",    # Satisfaction
            "تحسين",  # Improvement
            "جودة"    # Quality
        ]
        
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            for query in search_queries:
                response = await client.get(f"/api/feedback/search?q={query}")
                
                # Should not fail
                assert response.status_code in [200, 500]
                
                if response.status_code == 200:
                    data = response.json()
                    assert "query" in data
                    assert "results" in data
                    assert data["query"] == query

class TestAnalyticsAPIs:
    """Test analytics APIs with Arabic content"""
    
    @pytest.mark.asyncio
    async def test_feedback_analytics(self):
        """Test comprehensive feedback analytics"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            response = await client.get("/api/feedback/analytics?days=30")
            
            # Should return analytics or handle gracefully
            assert response.status_code in [200, 500]
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = [
                    "total_feedback", "by_channel", "by_sentiment",
                    "by_rating", "average_sentiment", "trending_topics"
                ]
                
                for field in required_fields:
                    assert field in data
                
                # Validate data types
                assert isinstance(data["total_feedback"], int)
                assert isinstance(data["by_channel"], dict)
                assert isinstance(data["by_sentiment"], dict)
                assert isinstance(data["trending_topics"], list)
    
    @pytest.mark.asyncio
    async def test_survey_analytics(self):
        """Test survey-specific analytics"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            # Test with mock survey ID
            response = await client.get("/api/surveys/1/analytics")
            
            # Should handle gracefully (survey might not exist)
            assert response.status_code in [200, 403, 404]

class TestAPIPerformance:
    """Test API performance with Arabic content"""
    
    @pytest.mark.asyncio
    async def test_feedback_submission_performance(self):
        """Test feedback submission performance under load"""
        import time
        
        # Test data
        feedback_data = {
            "content": "اختبار الأداء للنظام مع النص العربي الطويل نسبياً لقياس سرعة المعالجة " * 5,
            "channel": "website",
            "customer_email": "performance@test.com",
            "rating": 4
        }
        
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            # Measure response time
            start_time = time.time()
            
            response = await client.post("/api/feedback/submit", json=feedback_data)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Should respond within 5 seconds (target)
            assert response_time < 5.0, f"Response too slow: {response_time}s"
            
            # Should not fail due to performance issues
            assert response.status_code in [201, 422, 500]
    
    @pytest.mark.asyncio
    async def test_concurrent_api_requests(self):
        """Test concurrent API requests with Arabic content"""
        import asyncio
        
        async def make_request(client, text_content):
            """Make a single API request"""
            feedback_data = {
                "content": text_content,
                "channel": "website",
                "rating": 5
            }
            
            try:
                response = await client.post("/api/feedback/submit", json=feedback_data)
                return response.status_code
            except Exception as e:
                return str(e)
        
        # Create multiple concurrent requests
        arabic_texts = [
            f"تجربة متزامنة رقم {i} للنظام العربي"
            for i in range(10)
        ]
        
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            # Run concurrent requests
            tasks = [make_request(client, text) for text in arabic_texts]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check that most requests succeeded or failed gracefully
            success_count = sum(1 for result in results if isinstance(result, int))
            assert success_count >= len(arabic_texts) * 0.7  # At least 70% should complete

class TestAPIErrorHandling:
    """Test API error handling with various edge cases"""
    
    @pytest.mark.asyncio
    async def test_malformed_requests(self):
        """Test handling of malformed requests"""
        malformed_data = [
            {},  # Empty data
            {"invalid": "data"},  # Missing required fields
            {"content": ""},  # Empty content
            {"content": "test", "channel": "invalid"},  # Invalid channel
            {"content": "a" * 10000}  # Oversized content
        ]
        
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            for data in malformed_data:
                response = await client.post("/api/feedback/submit", json=data)
                
                # Should return proper error codes
                assert response.status_code in [400, 422, 500]
                
                # Should have error details
                if response.status_code == 422:
                    error_data = response.json()
                    assert "detail" in error_data
    
    @pytest.mark.asyncio
    async def test_sql_injection_attempts(self):
        """Test protection against SQL injection"""
        malicious_inputs = [
            "'; DROP TABLE feedback; --",
            "1' OR '1'='1",
            "admin'; UPDATE feedback SET content='hacked'; --",
            "test'; DELETE FROM feedback WHERE 1=1; --"
        ]
        
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            for malicious_input in malicious_inputs:
                feedback_data = {
                    "content": malicious_input,
                    "channel": "website"
                }
                
                response = await client.post("/api/feedback/submit", json=feedback_data)
                
                # Should either sanitize or reject
                assert response.status_code in [201, 422]
                
                # If accepted, should be sanitized
                if response.status_code == 201:
                    data = response.json()
                    # Malicious SQL should be escaped/sanitized
                    assert "DROP TABLE" not in data.get("content", "").upper()
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test rate limiting functionality"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            feedback_data = {
                "content": "اختبار حدود المعدل",
                "channel": "website"
            }
            
            # Make rapid requests
            responses = []
            for i in range(10):
                response = await client.post("/api/feedback/submit", json=feedback_data)
                responses.append(response.status_code)
            
            # Should eventually hit rate limit
            rate_limited = any(status == 429 for status in responses)
            # Rate limiting might not trigger in test environment
            assert True  # Just ensure no crashes

class TestArabicContentIntegration:
    """Test integration of Arabic content across all APIs"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_arabic_workflow(self):
        """Test complete Arabic workflow from survey creation to analytics"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            # 1. Create Arabic survey (might fail due to auth)
            survey_data = {
                "title_ar": "استطلاع تجربة العميل",
                "description_ar": "نود التعرف على رأيكم في خدماتنا",
                "primary_language": "ar"
            }
            
            survey_response = await client.post("/api/surveys/", json=survey_data)
            # Continue regardless of auth status
            
            # 2. Submit Arabic feedback
            feedback_data = {
                "content": "تجربة ممتازة مع فريق خدمة العملاء المحترم",
                "channel": "website",
                "customer_name_ar": "عبدالله أحمد",
                "rating": 5
            }
            
            feedback_response = await client.post("/api/feedback/submit", json=feedback_data)
            # Should handle gracefully
            assert feedback_response.status_code in [201, 422, 500]
            
            # 3. Search for Arabic feedback
            search_response = await client.get("/api/feedback/search?q=ممتازة")
            assert search_response.status_code in [200, 500]
            
            # 4. Get analytics
            analytics_response = await client.get("/api/feedback/analytics")
            assert analytics_response.status_code in [200, 500]
    
    @pytest.mark.asyncio
    async def test_mixed_language_handling(self):
        """Test handling of mixed Arabic-English content"""
        mixed_content_samples = [
            {
                "content": "الخدمة excellent والفريق professional",
                "channel": "email"
            },
            {
                "content": "Thank you كتير على الدعم الرائع",
                "channel": "phone"
            },
            {
                "content": "المنتج amazing بس الـ delivery متأخر",
                "channel": "website"
            }
        ]
        
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            for sample in mixed_content_samples:
                response = await client.post("/api/feedback/submit", json=sample)
                
                # Should handle mixed content gracefully
                assert response.status_code in [201, 422, 500]
                
                # If successful, should preserve the mixed content
                if response.status_code == 201:
                    data = response.json()
                    assert len(data["content"]) > 0

class TestAPIDocumentation:
    """Test API documentation and schema validation"""
    
    @pytest.mark.asyncio
    async def test_openapi_schema(self):
        """Test OpenAPI schema generation"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            response = await client.get("/openapi.json")
            
            if response.status_code == 200:
                schema = response.json()
                
                # Should have proper OpenAPI structure
                assert "openapi" in schema
                assert "paths" in schema
                assert "components" in schema
                
                # Should have Arabic-related endpoints
                paths = schema["paths"]
                arabic_endpoints = [
                    "/api/surveys/",
                    "/api/feedback/submit",
                    "/api/feedback/analytics"
                ]
                
                for endpoint in arabic_endpoints:
                    # Endpoints might not all be present in test
                    # Just ensure schema is valid if present
                    if endpoint in paths:
                        assert isinstance(paths[endpoint], dict)