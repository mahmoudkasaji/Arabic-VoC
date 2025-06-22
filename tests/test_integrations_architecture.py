"""
Tests for the Integrations Architecture (Data Sources, Destinations, AI Management)
Validates the data flow: Sources → Platform → AI Processing → Destinations
"""

import pytest
import json
from app import app, db
from unittest.mock import Mock, patch

class TestDataSourcesIntegration:
    """Test Data Sources catalog and functionality"""
    
    def setup_method(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        self.app_context.pop()
    
    def test_data_sources_page_loads(self):
        """Test data sources page renders correctly"""
        response = self.client.get('/integrations/sources')
        assert response.status_code == 200
        
        content = response.data.decode('utf-8')
        assert 'مصادر البيانات' in content  # Data Sources in Arabic
        assert 'موصلات API' in content      # API Connectors
        assert 'تكاملات القنوات' in content  # Channel Integrations
        assert 'أنظمة الأعمال' in content    # Business Systems
    
    def test_api_connectors_display(self):
        """Test API connectors section"""
        response = self.client.get('/integrations/sources')
        content = response.data.decode('utf-8')
        
        # Check API connector types
        assert 'REST API Endpoints' in content
        assert 'GraphQL Integrations' in content
        assert 'webhook' in content.lower()
    
    def test_channel_integrations_display(self):
        """Test channel integrations section"""
        response = self.client.get('/integrations/sources')
        content = response.data.decode('utf-8')
        
        # Check major channels
        assert 'WhatsApp Business' in content
        assert 'Twitter/X API' in content or 'Twitter' in content
        assert 'Gmail Integration' in content
        
        # Check status indicators
        assert 'نشط' in content      # Active
        assert 'غير نشط' in content  # Inactive
    
    def test_business_systems_display(self):
        """Test business systems integration section"""
        response = self.client.get('/integrations/sources')
        content = response.data.decode('utf-8')
        
        # Check major business systems
        assert 'Salesforce CRM' in content
        assert 'Zendesk Support' in content
        
        # Check integration status
        assert 'OAuth' in content or 'oauth' in content
    
    def test_connector_status_indicators(self):
        """Test connector status indicators functionality"""
        response = self.client.get('/integrations/sources')
        content = response.data.decode('utf-8')
        
        # Check status badge classes
        assert 'status-badge' in content
        assert 'status-active' in content or 'نشط' in content
        assert 'status-inactive' in content or 'غير نشط' in content


class TestDataDestinationsIntegration:
    """Test Data Destinations catalog and CX actions"""
    
    def setup_method(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        self.app_context.pop()
    
    def test_data_destinations_page_loads(self):
        """Test data destinations page renders correctly"""
        response = self.client.get('/integrations/destinations')
        assert response.status_code == 200
        
        content = response.data.decode('utf-8')
        assert 'وجهات البيانات' in content              # Data Destinations
        assert 'أنظمة إجراءات تجربة العملاء' in content  # CX Action Systems
        assert 'ذكاء الأعمال والتقارير' in content       # Business Intelligence
        assert 'التسويق والتواصل' in content          # Marketing & Communication
    
    def test_cx_action_systems_display(self):
        """Test CX action systems section"""
        response = self.client.get('/integrations/destinations')
        content = response.data.decode('utf-8')
        
        # Check CX action types
        assert 'Zendesk Auto-Ticketing' in content
        assert 'Customer Risk Alerts' in content
        
        # Check automation indicators
        assert 'إجراء/اليوم' in content or 'automation' in content.lower()
        assert 'trigger' in content.lower() or 'محفز' in content
    
    def test_business_intelligence_display(self):
        """Test business intelligence integrations"""
        response = self.client.get('/integrations/destinations')
        content = response.data.decode('utf-8')
        
        # Check BI platforms
        assert 'Power BI Export' in content
        assert 'BigQuery Warehouse' in content
        assert 'تقارير تلقائية' in content  # Automated Reports
    
    def test_trigger_system_display(self):
        """Test trigger system for automated actions"""
        response = self.client.get('/integrations/destinations')
        content = response.data.decode('utf-8')
        
        # Check trigger badges
        assert 'trigger-badge' in content
        assert 'مشكلة عاجلة' in content     # Urgent Issue
        assert 'تقييم سلبي' in content      # Negative Rating
        assert 'تقييم إيجابي' in content    # Positive Rating
    
    def test_marketing_automation_display(self):
        """Test marketing automation integrations"""
        response = self.client.get('/integrations/destinations')
        content = response.data.decode('utf-8')
        
        # Check marketing platforms
        assert 'MailChimp Campaigns' in content
        assert 'Twilio SMS Alerts' in content
        
        # Check campaign metrics
        assert 'حملات نشطة' in content or 'campaigns' in content.lower()


class TestAIManagementIntegration:
    """Test AI Management system for LLM configuration"""
    
    def setup_method(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        self.app_context.pop()
    
    def test_ai_management_page_loads(self):
        """Test AI management page renders correctly"""
        response = self.client.get('/integrations/ai')
        assert response.status_code == 200
        
        content = response.data.decode('utf-8')
        assert 'إدارة الذكاء الاصطناعي' in content      # AI Management
        assert 'نماذج اللغة الكبيرة' in content       # Large Language Models
        assert 'معالجة النصوص العربية' in content    # Arabic Text Processing
    
    def test_llm_configuration_display(self):
        """Test LLM configuration section"""
        response = self.client.get('/integrations/ai')
        content = response.data.decode('utf-8')
        
        # Check LLM providers
        assert 'OpenAI GPT-4' in content
        assert 'Azure OpenAI' in content
        
        # Check configuration parameters
        assert 'gpt-4o' in content
        assert 'درجة الحرارة' in content  # Temperature
        assert 'رموز' in content        # Tokens
    
    def test_performance_monitoring_display(self):
        """Test AI performance monitoring section"""
        response = self.client.get('/integrations/ai')
        content = response.data.decode('utf-8')
        
        # Check performance metrics
        assert 'الاستعلامات اليوم' in content     # Daily Queries
        assert 'وقت الاستجابة' in content       # Response Time  
        assert 'معدل الدقة' in content         # Accuracy Rate
        assert 'التكلفة الشهرية' in content     # Monthly Cost
    
    def test_arabic_processing_settings(self):
        """Test Arabic processing configuration"""
        response = self.client.get('/integrations/ai')
        content = response.data.decode('utf-8')
        
        # Check Arabic-specific settings
        assert 'كشف اللهجات العربية' in content    # Arabic Dialect Detection
        assert 'تطبيع النص العربي' in content     # Arabic Text Normalization  
        assert 'السياق الثقافي' in content       # Cultural Context
        assert 'مستوى الثقة' in content         # Confidence Level
    
    def test_model_status_indicators(self):
        """Test AI model status indicators"""
        response = self.client.get('/integrations/ai')
        content = response.data.decode('utf-8')
        
        # Check status indicators
        assert 'model-status' in content
        assert 'status-active' in content
        assert 'status-inactive' in content
        assert 'نشط' in content or 'غير نشط' in content


class TestIntegrationsDataFlow:
    """Test end-to-end data flow through integrations architecture"""
    
    def setup_method(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        self.app_context.pop()
    
    def test_data_flow_visualization(self):
        """Test data flow visualization across integration pages"""
        # Test that all three integration pages reference the data flow
        pages = [
            ('/integrations/sources', 'incoming'),
            ('/integrations/destinations', 'outgoing'),
            ('/integrations/ai', 'processing')
        ]
        
        for route, flow_type in pages:
            response = self.client.get(route)
            content = response.data.decode('utf-8')
            
            # Check data flow context is present
            assert 'data' in content.lower() or 'بيانات' in content
            assert 'integration' in content.lower() or 'تكامل' in content
    
    def test_integration_navigation_consistency(self):
        """Test navigation consistency across integration pages"""
        integration_routes = [
            '/integrations/sources',
            '/integrations/destinations', 
            '/integrations/ai'
        ]
        
        for route in integration_routes:
            response = self.client.get(route)
            content = response.data.decode('utf-8')
            
            # Check all integration navigation links are present
            assert 'مصادر البيانات' in content      # Data Sources
            assert 'وجهات البيانات' in content      # Data Destinations
            assert 'الذكاء الاصطناعي' in content    # AI Management
    
    def test_integration_redirect(self):
        """Test /integrations redirects to sources by default"""
        response = self.client.get('/integrations')
        
        # Should redirect to sources or load sources content
        assert response.status_code in [200, 301, 302]
        
        if response.status_code == 200:
            content = response.data.decode('utf-8')
            assert 'مصادر البيانات' in content
    
    @pytest.mark.integration
    def test_simulated_data_flow(self):
        """Test simulated data flow from source to destination"""
        # Step 1: Simulate data from source (feedback submission)
        feedback_response = self.client.post('/api/feedback/submit', 
                                           json={
                                               'content': 'الخدمة ممتازة جداً',
                                               'channel': 'whatsapp',
                                               'rating': 5
                                           })
        assert feedback_response.status_code == 200
        
        # Step 2: Verify AI processing (sentiment analysis)
        feedback_data = json.loads(feedback_response.data)
        assert 'sentiment_score' in feedback_data
        assert feedback_data['sentiment_score'] > 0  # Should be positive
        
        # Step 3: Verify data available for destinations (analytics)
        analytics_response = self.client.get('/api/executive-dashboard/metrics')
        assert analytics_response.status_code == 200
        
        analytics_data = json.loads(analytics_response.data)
        assert analytics_data['volume']['total'] > 0


class TestIntegrationsPerformance:
    """Performance tests for integrations system"""
    
    def setup_method(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        self.app_context.pop()
    
    @pytest.mark.performance
    def test_integrations_page_load_times(self):
        """Test integration pages load within performance targets"""
        import time
        
        integration_routes = [
            '/integrations/sources',
            '/integrations/destinations',
            '/integrations/ai'
        ]
        
        for route in integration_routes:
            start_time = time.time()
            response = self.client.get(route)
            load_time = time.time() - start_time
            
            assert response.status_code == 200
            assert load_time < 1.0, f"Route {route} load time {load_time:.2f}s exceeds 1s"
    
    @pytest.mark.performance
    def test_integration_component_rendering(self):
        """Test integration component rendering performance"""
        import time
        
        start_time = time.time()
        response = self.client.get('/integrations/sources')
        render_time = time.time() - start_time
        
        content = response.data.decode('utf-8')
        
        # Check that complex components loaded
        assert 'connector-card' in content
        assert 'status-badge' in content
        assert render_time < 0.8, f"Component rendering took {render_time:.2f}s"


class TestIntegrationsSecurity:
    """Security tests for integrations system"""
    
    def setup_method(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        self.app_context.pop()
    
    def test_integration_pages_xss_prevention(self):
        """Test XSS prevention on integration pages"""
        xss_payloads = [
            '<script>alert("xss")</script>',
            'javascript:alert(1)',
            '<img src=x onerror=alert(1)>'
        ]
        
        integration_routes = [
            '/integrations/sources',
            '/integrations/destinations',
            '/integrations/ai'
        ]
        
        for route in integration_routes:
            for payload in xss_payloads:
                response = self.client.get(f'{route}?config={payload}')
                content = response.data.decode('utf-8')
                
                # Ensure payload is not executed
                assert payload not in content
                assert '&lt;script&gt;' in content or payload not in content
    
    def test_integration_input_validation(self):
        """Test input validation for integration endpoints"""
        # Test with malicious configuration data
        malicious_configs = [
            {'exec': 'rm -rf /'},
            {'sql': "'; DROP TABLE users; --"},
            {'cmd': 'cat /etc/passwd'}
        ]
        
        for config in malicious_configs:
            response = self.client.post('/integrations/sources', json=config)
            # Should not execute malicious commands
            assert response.status_code in [400, 404, 405, 422]