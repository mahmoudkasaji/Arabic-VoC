"""
API endpoint tests for Arabic VoC platform
Focus on Arabic feedback submission and analytics
"""

import pytest
import json
from httpx import AsyncClient

class TestFeedbackAPI:
    """Test feedback collection API endpoints"""
    
    @pytest.mark.asyncio
    async def test_submit_arabic_feedback(self, async_client: AsyncClient, arabic_feedback_samples):
        """Test Arabic feedback submission"""
        for feedback_text in arabic_feedback_samples[:3]:  # Test first 3 samples
            payload = {
                "content": feedback_text,
                "channel": "website",
                "rating": 4
            }
            
            response = await async_client.post("/api/feedback/submit", json=payload)
            assert response.status_code == 200
            
            data = response.json()
            assert "id" in data
            assert data["content"] == feedback_text
            assert data["channel"] == "website"
            assert "sentiment_score" in data
    
    @pytest.mark.asyncio
    async def test_feedback_validation(self, async_client: AsyncClient):
        """Test feedback input validation"""
        # Test missing content
        response = await async_client.post("/api/feedback/submit", json={
            "channel": "website"
        })
        assert response.status_code == 422
        
        # Test invalid channel
        response = await async_client.post("/api/feedback/submit", json={
            "content": "اختبار",
            "channel": "invalid_channel"
        })
        assert response.status_code == 422
        
        # Test content too long
        response = await async_client.post("/api/feedback/submit", json={
            "content": "أ" * 6000,  # Exceeds 5000 char limit
            "channel": "website"
        })
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_list_feedback(self, async_client: AsyncClient):
        """Test feedback listing endpoint"""
        response = await async_client.get("/api/feedback/list")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        # Test with filters
        response = await async_client.get("/api/feedback/list?channel=website&limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) <= 5
    
    @pytest.mark.asyncio
    async def test_feedback_security(self, async_client: AsyncClient, malicious_inputs):
        """Test security with malicious inputs"""
        for malicious_input in malicious_inputs[:5]:  # Test first 5
            payload = {
                "content": malicious_input,
                "channel": "website"
            }
            
            response = await async_client.post("/api/feedback/submit", json=payload)
            
            # Should either reject (422) or sanitize (200)
            assert response.status_code in [200, 422]
            
            if response.status_code == 200:
                data = response.json()
                # Verify dangerous content is sanitized
                assert "<script>" not in data["content"].lower()
                assert "javascript:" not in data["content"].lower()

class TestAnalyticsAPI:
    """Test analytics API endpoints"""
    
    @pytest.mark.asyncio
    async def test_dashboard_metrics(self, async_client: AsyncClient):
        """Test dashboard metrics endpoint"""
        response = await async_client.get("/api/analytics/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        required_fields = [
            "total_feedback", "processed_feedback", "pending_feedback",
            "average_sentiment", "sentiment_distribution", "channel_metrics"
        ]
        
        for field in required_fields:
            assert field in data
    
    @pytest.mark.asyncio
    async def test_sentiment_metrics(self, async_client: AsyncClient):
        """Test sentiment analysis metrics"""
        response = await async_client.get("/api/analytics/sentiment")
        assert response.status_code == 200
        
        data = response.json()
        assert "average_sentiment" in data
        assert "positive_count" in data
        assert "negative_count" in data
        assert "neutral_count" in data
        assert "confidence_score" in data
    
    @pytest.mark.asyncio
    async def test_trend_analysis(self, async_client: AsyncClient):
        """Test trend analysis endpoint"""
        response = await async_client.get("/api/analytics/trends")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        if data:  # If we have trend data
            trend = data[0]
            assert "date" in trend
            assert "feedback_count" in trend
            assert "average_sentiment" in trend

class TestHealthAndStatus:
    """Test health check and status endpoints"""
    
    @pytest.mark.asyncio
    async def test_health_check(self, async_client: AsyncClient):
        """Test health check endpoint"""
        response = await async_client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "message" in data
    
    @pytest.mark.asyncio
    async def test_api_performance(self, async_client: AsyncClient):
        """Test API response times"""
        import time
        
        endpoints = ["/health", "/api/feedback/list", "/api/analytics/dashboard"]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = await async_client.get(endpoint)
            end_time = time.time()
            
            assert response.status_code == 200
            assert (end_time - start_time) < 2.0  # Should respond within 2 seconds

class TestArabicSpecificAPI:
    """Test Arabic-specific API functionality"""
    
    @pytest.mark.asyncio
    async def test_arabic_content_processing(self, async_client: AsyncClient):
        """Test that Arabic content is properly processed"""
        arabic_text = "الخدمة ممتازة جداً وأنصح بها بشدة"
        
        payload = {
            "content": arabic_text,
            "channel": "website",
            "rating": 5
        }
        
        response = await async_client.post("/api/feedback/submit", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify Arabic content is preserved
        assert data["content"] == arabic_text
        
        # Verify sentiment analysis worked
        assert "sentiment_score" in data
        assert data["sentiment_score"] > 0  # Should be positive for this text
        
        # Verify confidence score
        assert "confidence_score" in data
        assert 0 <= data["confidence_score"] <= 1
    
    @pytest.mark.asyncio
    async def test_mixed_language_handling(self, async_client: AsyncClient):
        """Test handling of mixed Arabic/English content"""
        mixed_text = "الخدمة excellent والدعم very good"
        
        payload = {
            "content": mixed_text,
            "channel": "website"
        }
        
        response = await async_client.post("/api/feedback/submit", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["content"] == mixed_text
        assert "sentiment_score" in data
    
    @pytest.mark.asyncio
    async def test_arabic_character_encoding(self, async_client: AsyncClient):
        """Test proper Arabic character encoding in API responses"""
        arabic_text = "اختبار الترميز العربي ٠١٢٣٤٥٦٧٨٩"
        
        payload = {
            "content": arabic_text,
            "channel": "website"
        }
        
        response = await async_client.post("/api/feedback/submit", json=payload)
        assert response.status_code == 200
        
        # Verify response is properly UTF-8 encoded
        response_text = response.text
        assert arabic_text in response_text
        
        # Verify JSON parsing preserves Arabic characters
        data = response.json()
        assert data["content"] == arabic_text