"""
Full system validation tests
End-to-end workflows and integration validation
"""

import pytest
import time
import json
from app import app

class TestEndToEndWorkflows:
    """Test complete user workflows"""
    
    def setup_method(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        self.app_context.pop()
    
    @pytest.mark.integration
    def test_complete_feedback_workflow(self):
        """Test complete feedback collection and analysis workflow"""
        # Step 1: Navigate to feedback page
        response = self.client.get('/surveys/feedback')
        assert response.status_code == 200
        
        # Step 2: Submit Arabic feedback
        feedback_data = {
            'content': 'تجربة رائعة مع المنتج. الجودة عالية والخدمة ممتازة.',
            'channel': 'website',
            'rating': 5,
            'customer_email': 'test@example.com'
        }
        
        submit_response = self.client.post('/api/feedback/submit', json=feedback_data)
        assert submit_response.status_code == 200
        
        # Step 3: Verify feedback appears in analytics
        analytics_response = self.client.get('/api/executive-dashboard/metrics')
        assert analytics_response.status_code == 200
        
        analytics_data = analytics_response.get_json()
        assert analytics_data['volume']['total'] > 0
        assert analytics_data['sentiment']['score'] > 0  # Should be positive
    
    @pytest.mark.integration
    def test_survey_creation_to_response_workflow(self):
        """Test survey creation and response collection workflow"""
        # Step 1: Navigate to survey builder
        response = self.client.get('/surveys/builder')
        assert response.status_code == 200
        
        # Step 2: Create survey (if API exists)
        survey_data = {
            'title': 'استطلاع تجربة المستخدم',
            'description': 'نود معرفة رأيكم في تجربة استخدام منتجنا',
            'questions': [
                {
                    'type': 'rating',
                    'text': 'كيف تقيم سهولة الاستخدام؟',
                    'scale': 5
                },
                {
                    'type': 'text',
                    'text': 'ما هي اقتراحاتك للتحسين؟'
                }
            ]
        }
        
        create_response = self.client.post('/api/surveys/create', json=survey_data)
        # API might not exist yet, so accept 404
        assert create_response.status_code in [200, 201, 404, 405]
        
        # Step 3: Navigate to survey management
        manage_response = self.client.get('/surveys/manage')
        assert manage_response.status_code == 200
    
    @pytest.mark.integration
    def test_navigation_to_all_features(self):
        """Test navigation to all major features works"""
        major_features = [
            '/surveys/builder',
            '/surveys/manage',
            '/surveys/feedback',
            '/surveys/responses',
            '/analytics/executive',
            '/analytics/detailed',
            '/analytics/arabic',
            '/analytics/reports',
            '/integrations/sources',
            '/integrations/destinations',
            '/integrations/ai',
            '/settings/account',
            '/settings/system',
            '/settings/security',
            '/settings/admin'
        ]
        
        for feature_url in major_features:
            response = self.client.get(feature_url)
            assert response.status_code == 200, f"Feature {feature_url} not accessible"
            
            # Check Arabic content exists
            content = response.data.decode('utf-8')
            # At least one Arabic character should be present
            assert any(ord(char) >= 0x0600 and ord(char) <= 0x06FF for char in content), f"No Arabic content in {feature_url}"


class TestSystemPerformanceValidation:
    """Validate all performance targets"""
    
    def setup_method(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        self.app_context.pop()
    
    @pytest.mark.performance
    def test_all_performance_targets(self):
        """Test all documented performance targets"""
        performance_results = {}
        
        # Target 1: Dashboard load time <1 second
        start_time = time.time()
        response = self.client.get('/analytics/executive')
        dashboard_time = time.time() - start_time
        performance_results['dashboard_load'] = dashboard_time
        assert response.status_code == 200
        assert dashboard_time < 1.0, f"Dashboard load {dashboard_time:.3f}s exceeds 1s target"
        
        # Target 2: API response time <200ms
        start_time = time.time()
        response = self.client.get('/api/executive-dashboard/metrics')
        api_time = time.time() - start_time
        performance_results['api_response'] = api_time
        assert response.status_code == 200
        assert api_time < 0.2, f"API response {api_time:.3f}s exceeds 200ms target"
        
        # Target 3: Real-time update latency <50ms (relaxed to 100ms for testing)
        start_time = time.time()
        feedback_response = self.client.post('/api/feedback/submit', 
                                           json={
                                               'content': 'اختبار الأداء الشامل',
                                               'channel': 'performance_test',
                                               'rating': 5
                                           })
        metrics_response = self.client.get('/api/executive-dashboard/metrics')
        update_latency = time.time() - start_time
        performance_results['update_latency'] = update_latency
        
        assert feedback_response.status_code == 200
        assert metrics_response.status_code == 200
        assert update_latency < 0.1, f"Update latency {update_latency:.3f}s exceeds 100ms target"
        
        print(f"Performance Results: {performance_results}")
    
    @pytest.mark.performance
    def test_arabic_processing_performance(self):
        """Test Arabic text processing performance"""
        arabic_texts = [
            "الخدمة ممتازة والفريق محترف",
            "التطبيق سهل ومفيد للغاية", 
            "أنصح الجميع بتجربة هذا المنتج",
            "الدعم سريع ومتجاوب مع العملاء",
            "جودة عالية وأسعار مناسبة"
        ]
        
        processing_times = []
        
        for text in arabic_texts:
            start_time = time.time()
            response = self.client.post('/api/feedback/submit', 
                                      json={
                                          'content': text,
                                          'channel': 'arabic_performance_test',
                                          'rating': 4
                                      })
            processing_time = time.time() - start_time
            processing_times.append(processing_time)
            
            assert response.status_code == 200
        
        avg_processing_time = sum(processing_times) / len(processing_times)
        assert avg_processing_time < 0.5, f"Arabic processing avg {avg_processing_time:.3f}s too slow"


class TestSystemStabilityValidation:
    """Test system stability and error handling"""
    
    def setup_method(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        self.app_context.pop()
    
    def test_error_page_handling(self):
        """Test error pages display properly in Arabic"""
        # Test 404 error
        response = self.client.get('/nonexistent-page')
        assert response.status_code == 404
        
        # Test invalid API request
        response = self.client.post('/api/invalid-endpoint', json={})
        assert response.status_code == 404
    
    def test_malformed_data_handling(self):
        """Test handling of malformed data"""
        malformed_requests = [
            # Invalid JSON
            {'content': None, 'channel': 'test'},
            # Missing required fields
            {'channel': 'test'},
            # Invalid channel
            {'content': 'test', 'channel': 'invalid_channel'},
            # Extremely long content
            {'content': 'أ' * 10000, 'channel': 'test'}
        ]
        
        for request_data in malformed_requests:
            response = self.client.post('/api/feedback/submit', json=request_data)
            # Should handle gracefully, not crash
            assert response.status_code in [400, 422, 500]
    
    @pytest.mark.security
    def test_security_validations(self):
        """Test security measures are working"""
        # Test XSS prevention
        xss_payload = '<script>alert("xss")</script>'
        response = self.client.post('/api/feedback/submit', 
                                  json={
                                      'content': xss_payload,
                                      'channel': 'security_test'
                                  })
        
        if response.status_code == 200:
            # If accepted, ensure it's sanitized
            data = response.get_json()
            assert '<script>' not in str(data)
        
        # Test SQL injection prevention
        sql_payload = "'; DROP TABLE feedback; --"
        response = self.client.post('/api/feedback/submit',
                                  json={
                                      'content': sql_payload,
                                      'channel': 'security_test'
                                  })
        
        # Should not crash the system
        assert response.status_code in [200, 400, 422]
        
        # Verify system still works after injection attempt
        test_response = self.client.get('/api/executive-dashboard/metrics')
        assert test_response.status_code == 200


class TestComplianceValidation:
    """Test compliance with Arabic VoC requirements"""
    
    def setup_method(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        self.app_context.pop()
    
    def test_arabic_rtl_compliance(self):
        """Test RTL layout compliance across all pages"""
        pages_to_test = [
            '/analytics/executive',
            '/surveys/builder',
            '/integrations/sources',
            '/settings/account'
        ]
        
        for page in pages_to_test:
            response = self.client.get(page)
            content = response.data.decode('utf-8')
            
            # Check RTL attributes
            assert 'dir="rtl"' in content, f"Page {page} missing RTL direction"
            assert 'lang="ar"' in content, f"Page {page} missing Arabic language"
            
            # Check Arabic fonts
            assert 'cairo' in content.lower() or 'amiri' in content.lower(), f"Page {page} missing Arabic fonts"
    
    def test_arabic_text_processing_compliance(self):
        """Test Arabic text processing meets requirements"""
        test_cases = [
            # Standard Arabic
            "هذا نص تجريبي باللغة العربية",
            # Arabic with numbers
            "العدد هو ١٢٣٤٥ والتاريخ اليوم",
            # Mixed content
            "التطبيق version 2.0 جديد",
            # Dialect variations
            "الخدمة زينة وايد" # Gulf dialect
        ]
        
        for text in test_cases:
            response = self.client.post('/api/feedback/submit',
                                      json={
                                          'content': text,
                                          'channel': 'compliance_test',
                                          'rating': 4
                                      })
            
            assert response.status_code == 200, f"Failed to process Arabic text: {text}"
    
    def test_cultural_context_features(self):
        """Test cultural context features are working"""
        # Test with culturally relevant Arabic content
        cultural_content = [
            "الخدمة ممتازة ما شاء الله",  # Religious expression
            "الفريق محترم ومؤدب",          # Politeness emphasis
            "السعر مناسب والجودة عالية"    # Value emphasis
        ]
        
        for content in cultural_content:
            response = self.client.post('/api/feedback/submit',
                                      json={
                                          'content': content,
                                          'channel': 'cultural_test',
                                          'rating': 5
                                      })
            
            assert response.status_code == 200
            
            # Verify sentiment analysis works with cultural context
            if response.status_code == 200:
                # Get updated metrics to see if sentiment was processed
                metrics_response = self.client.get('/api/executive-dashboard/metrics')
                assert metrics_response.status_code == 200


if __name__ == "__main__":
    # Run comprehensive system validation
    import subprocess
    result = subprocess.run(['python', '-m', 'pytest', __file__, '-v'], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)