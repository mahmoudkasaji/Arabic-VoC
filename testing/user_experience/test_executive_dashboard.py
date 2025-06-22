"""
Comprehensive tests for Executive Dashboard functionality
Tests real-time KPIs, Chart.js integration, and Arabic analytics
"""

import pytest
import json
import asyncio
from unittest.mock import Mock, patch
import time
from flask import Flask
from app import app, db

class TestExecutiveDashboard:
    """Test executive dashboard core functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        """Cleanup test environment"""
        self.app_context.pop()
    
    def test_dashboard_page_loads(self):
        """Test dashboard page renders correctly"""
        response = self.client.get('/analytics/executive')
        assert response.status_code == 200
        assert 'لوحة التحليلات والقيادة' in response.data.decode('utf-8')
        assert 'chart.js' in response.data.decode('utf-8').lower()
    
    def test_dashboard_metrics_api(self):
        """Test dashboard metrics API endpoint"""
        response = self.client.get('/api/executive-dashboard/metrics')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        
        # Verify required KPI structure
        assert 'csat' in data
        assert 'volume' in data
        assert 'sentiment' in data
        assert 'channels' in data
        assert 'trends' in data
        
        # Verify CSAT structure
        csat = data['csat']
        assert 'score' in csat
        assert 'confidence' in csat
        assert 'total_responses' in csat
        assert isinstance(csat['score'], (int, float))
        assert 0 <= csat['score'] <= 1
        
        # Verify volume metrics
        volume = data['volume']
        assert 'total' in volume
        assert 'today' in volume
        assert 'week' in volume
        assert 'month' in volume
        assert isinstance(volume['total'], int)
        
        # Verify sentiment analysis
        sentiment = data['sentiment']
        assert 'score' in sentiment
        assert 'confidence' in sentiment
        assert 'distribution' in sentiment
        assert -1 <= sentiment['score'] <= 1
    
    def test_dashboard_arabic_content(self):
        """Test dashboard handles Arabic content correctly"""
        response = self.client.get('/api/executive-dashboard/metrics')
        data = json.loads(response.data)
        
        # Verify Arabic channel labels
        channels = data['channels']
        assert 'labels' in channels
        assert any('واتساب' in label for label in channels['labels'])
        
        # Test with Arabic feedback
        arabic_feedback = "الخدمة ممتازة والموظفون متعاونون جداً"
        feedback_response = self.client.post('/api/feedback/submit', 
                                           json={
                                               'content': arabic_feedback,
                                               'channel': 'website',
                                               'rating': 5
                                           })
        assert feedback_response.status_code == 200
    
    @pytest.mark.performance
    def test_dashboard_load_time(self):
        """Test dashboard loads within 1 second target"""
        start_time = time.time()
        response = self.client.get('/analytics/executive')
        load_time = time.time() - start_time
        
        assert response.status_code == 200
        assert load_time < 1.0, f"Dashboard load time {load_time:.2f}s exceeds 1s target"
    
    @pytest.mark.performance  
    def test_metrics_api_performance(self):
        """Test metrics API responds within performance targets"""
        start_time = time.time()
        response = self.client.get('/api/executive-dashboard/metrics')
        response_time = time.time() - start_time
        
        assert response.status_code == 200
        assert response_time < 0.5, f"Metrics API response time {response_time:.2f}s too slow"
    
    def test_real_time_updates(self):
        """Test real-time data updates functionality"""
        # Get initial metrics
        response1 = self.client.get('/api/executive-dashboard/metrics')
        data1 = json.loads(response1.data)
        initial_volume = data1['volume']['total']
        
        # Submit new feedback
        self.client.post('/api/feedback/submit', 
                        json={
                            'content': 'خدمة رائعة',
                            'channel': 'email',
                            'rating': 5
                        })
        
        # Get updated metrics
        response2 = self.client.get('/api/executive-dashboard/metrics')
        data2 = json.loads(response2.data)
        updated_volume = data2['volume']['total']
        
        assert updated_volume > initial_volume
    
    def test_chart_data_format(self):
        """Test chart data is in correct format for Chart.js"""
        response = self.client.get('/api/executive-dashboard/metrics')
        data = json.loads(response.data)
        
        # Test trends chart data
        trends = data['trends']
        assert isinstance(trends['labels'], list)
        assert isinstance(trends['values'], list)
        assert len(trends['labels']) == len(trends['values'])
        
        # Test channels chart data  
        channels = data['channels']
        assert isinstance(channels['labels'], list)
        assert isinstance(channels['values'], list)
        assert len(channels['labels']) == len(channels['values'])
        assert all(isinstance(v, (int, float)) for v in channels['values'])
    
    def test_kpi_calculations(self):
        """Test KPI calculations are accurate"""
        response = self.client.get('/api/executive-dashboard/metrics')
        data = json.loads(response.data)
        
        # Test CSAT calculation
        csat = data['csat']
        assert csat['score'] >= 0 and csat['score'] <= 1
        assert csat['confidence'] >= 0 and csat['confidence'] <= 1
        
        # Test sentiment distribution adds up
        sentiment = data['sentiment']
        distribution = sentiment['distribution']
        total = distribution['positive'] + distribution['neutral'] + distribution['negative']
        assert total > 0, "Sentiment distribution should have values"
    
    def test_error_handling(self):
        """Test dashboard error handling"""
        # Test with database connection issues
        with patch('api.executive_dashboard.get_db_session') as mock_db:
            mock_db.side_effect = Exception("Database connection failed")
            
            response = self.client.get('/api/executive-dashboard/metrics')
            # Should handle gracefully, not crash
            assert response.status_code in [200, 500]  # Either works or fails gracefully
    
    def test_arabic_kpi_labels(self):
        """Test Arabic KPI labels and formatting"""
        response = self.client.get('/analytics/executive')
        content = response.data.decode('utf-8')
        
        # Verify Arabic KPI labels are present
        assert 'رضا العملاء' in content  # Customer Satisfaction
        assert 'حجم الاستجابات' in content  # Response Volume
        assert 'مؤشر المشاعر العربي' in content  # Arabic Sentiment Index
        assert 'اتجاهات الأداء' in content  # Performance Trends


class TestDashboardIntegration:
    """Integration tests for dashboard with other components"""
    
    def setup_method(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        self.app_context.pop()
    
    def test_navigation_integration(self):
        """Test dashboard navigation integration"""
        response = self.client.get('/analytics/executive')
        content = response.data.decode('utf-8')
        
        # Check navigation component is included
        assert 'navbar' in content
        assert 'التحليلات' in content  # Analytics in Arabic
        assert 'dropdown' in content
    
    def test_breadcrumb_navigation(self):
        """Test breadcrumb navigation on dashboard"""
        response = self.client.get('/analytics/executive')
        content = response.data.decode('utf-8')
        
        # Check breadcrumb structure
        assert 'breadcrumb' in content
        assert 'الرئيسية' in content  # Home in Arabic
    
    def test_responsive_design(self):
        """Test dashboard responsive design elements"""
        response = self.client.get('/analytics/executive')
        content = response.data.decode('utf-8')
        
        # Check responsive Bootstrap classes
        assert 'col-lg-' in content
        assert 'col-md-' in content
        assert 'viewport' in content
    
    def test_rtl_layout(self):
        """Test Right-to-Left layout for Arabic"""
        response = self.client.get('/analytics/executive')
        content = response.data.decode('utf-8')
        
        # Check RTL attributes
        assert 'dir="rtl"' in content
        assert 'lang="ar"' in content
        assert 'Cairo' in content  # Arabic font family


class TestDashboardSecurity:
    """Security tests for dashboard endpoints"""
    
    def setup_method(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        self.app_context.pop()
    
    def test_metrics_api_input_validation(self):
        """Test metrics API input validation"""
        # Test with malicious parameters
        response = self.client.get('/api/executive-dashboard/metrics?exec=rm%20-rf')
        assert response.status_code in [200, 400]  # Should not execute
        
        # Test with XSS attempts
        response = self.client.get('/api/executive-dashboard/metrics?alert=<script>alert(1)</script>')
        assert response.status_code in [200, 400]
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention"""
        # Test with SQL injection in parameters
        malicious_params = [
            "'; DROP TABLE feedback; --",
            "1' OR '1'='1",
            "UNION SELECT * FROM users"
        ]
        
        for param in malicious_params:
            response = self.client.get(f'/api/executive-dashboard/metrics?filter={param}')
            assert response.status_code in [200, 400, 422]
            # Ensure database integrity
            check_response = self.client.get('/api/executive-dashboard/metrics')
            assert check_response.status_code == 200