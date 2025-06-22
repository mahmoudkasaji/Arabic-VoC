"""
Comprehensive tests for 4-tier navigation system
Tests navigation structure, breadcrumbs, and routing
"""

import pytest
from flask import Flask
from app import app

class TestNavigationStructure:
    """Test 4-tier navigation architecture"""
    
    def setup_method(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        self.app_context.pop()
    
    def test_primary_navigation_routes(self):
        """Test all primary navigation routes work"""
        primary_routes = [
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
        
        for route in primary_routes:
            response = self.client.get(route)
            assert response.status_code == 200, f"Route {route} failed with {response.status_code}"
    
    def test_navigation_component_inclusion(self):
        """Test navigation component is included on all pages"""
        test_routes = [
            '/analytics/executive',
            '/surveys/builder',
            '/integrations/sources',
            '/settings/account'
        ]
        
        for route in test_routes:
            response = self.client.get(route)
            content = response.data.decode('utf-8')
            
            # Check navigation component elements
            assert 'navbar' in content
            assert 'dropdown' in content
            assert 'الاستطلاعات' in content  # Surveys
            assert 'التحليلات' in content   # Analytics
            assert 'التكاملات' in content   # Integrations
            assert 'الإعدادات' in content   # Settings
    
    def test_breadcrumb_system(self):
        """Test breadcrumb navigation system"""
        breadcrumb_tests = [
            ('/surveys/builder', ['الاستطلاعات', 'منشئ الاستطلاعات']),
            ('/analytics/executive', ['التحليلات', 'لوحة القيادة']),
            ('/integrations/sources', ['التكاملات', 'مصادر البيانات']),
            ('/settings/account', ['الإعدادات', 'إدارة الحساب'])
        ]
        
        for route, expected_breadcrumbs in breadcrumb_tests:
            response = self.client.get(route)
            content = response.data.decode('utf-8')
            
            # Check breadcrumb structure exists
            assert 'breadcrumb' in content
            assert 'الرئيسية' in content  # Home
            
            # Check expected breadcrumb items
            for breadcrumb in expected_breadcrumbs:
                assert breadcrumb in content
    
    def test_dropdown_menu_structure(self):
        """Test dropdown menu structure and content"""
        response = self.client.get('/analytics/executive')
        content = response.data.decode('utf-8')
        
        # Test Surveys dropdown
        assert 'منشئ الاستطلاعات' in content
        assert 'إدارة الاستطلاعات' in content
        assert 'جمع التعليقات' in content
        assert 'إدارة الردود' in content
        
        # Test Analytics dropdown
        assert 'لوحة القيادة' in content
        assert 'التحليلات التفصيلية' in content
        assert 'الرؤى العربية' in content
        assert 'التقارير والتصدير' in content
        
        # Test Integrations dropdown
        assert 'مصادر البيانات' in content
        assert 'وجهات البيانات' in content
        assert 'إدارة الذكاء الاصطناعي' in content
    
    def test_backward_compatibility(self):
        """Test backward compatibility with old routes"""
        compatibility_routes = [
            ('/executive-dashboard', '/analytics/executive'),
            ('/survey-builder', '/surveys/builder'),
            ('/feedback', '/surveys/feedback'),
            ('/integrations', '/integrations/sources')
        ]
        
        for old_route, new_route in compatibility_routes:
            # Test old route still works (redirect or direct access)
            response = self.client.get(old_route)
            assert response.status_code in [200, 301, 302]
    
    def test_navigation_accessibility(self):
        """Test navigation accessibility features"""
        response = self.client.get('/analytics/executive')
        content = response.data.decode('utf-8')
        
        # Check ARIA attributes
        assert 'role="button"' in content
        assert 'aria-label' in content or 'aria-expanded' in content
        
        # Check keyboard navigation support
        assert 'data-bs-toggle' in content
        assert 'dropdown' in content


class TestRoutingSystem:
    """Test Flask routing system integrity"""
    
    def setup_method(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        self.app_context.pop()
    
    def test_route_uniqueness(self):
        """Test all routes are unique and properly mapped"""
        from app import app as flask_app
        
        routes = []
        for rule in flask_app.url_map.iter_rules():
            if rule.endpoint != 'static':
                routes.append(str(rule))
        
        # Check for duplicate routes
        assert len(routes) == len(set(routes)), "Duplicate routes found"
    
    def test_route_methods(self):
        """Test routes accept correct HTTP methods"""
        # GET routes should accept GET
        get_routes = [
            '/analytics/executive',
            '/surveys/builder',
            '/integrations/sources'
        ]
        
        for route in get_routes:
            response = self.client.get(route)
            assert response.status_code == 200
            
            # POST should not be allowed on display routes
            response = self.client.post(route)
            assert response.status_code == 405  # Method not allowed
    
    def test_route_parameters(self):
        """Test routes handle parameters correctly"""
        # Test routes with potential parameters
        param_tests = [
            '/analytics/executive?filter=today',
            '/surveys/manage?status=active',
            '/integrations/sources?category=api'
        ]
        
        for route in param_tests:
            response = self.client.get(route)
            assert response.status_code == 200
    
    def test_invalid_routes(self):
        """Test handling of invalid routes"""
        invalid_routes = [
            '/nonexistent',
            '/surveys/invalid',
            '/analytics/fake',
            '/integrations/missing'
        ]
        
        for route in invalid_routes:
            response = self.client.get(route)
            assert response.status_code == 404


class TestMobileNavigation:
    """Test navigation on mobile devices"""
    
    def setup_method(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        self.app_context.pop()
    
    def test_mobile_navbar_toggle(self):
        """Test mobile navbar toggle functionality"""
        response = self.client.get('/analytics/executive')
        content = response.data.decode('utf-8')
        
        # Check mobile toggle button
        assert 'navbar-toggler' in content
        assert 'data-bs-toggle="collapse"' in content
        assert 'data-bs-target="#mainNavigation"' in content
    
    def test_responsive_navigation(self):
        """Test responsive navigation elements"""
        response = self.client.get('/analytics/executive')
        content = response.data.decode('utf-8')
        
        # Check responsive classes
        assert 'navbar-expand-lg' in content
        assert 'collapse navbar-collapse' in content
        
        # Check viewport meta tag
        assert 'viewport' in content
        assert 'width=device-width' in content
    
    def test_mobile_breadcrumbs(self):
        """Test breadcrumb display on mobile"""
        response = self.client.get('/surveys/builder')
        content = response.data.decode('utf-8')
        
        # Breadcrumbs should be present and responsive
        assert 'breadcrumb' in content
        assert 'container-fluid' in content or 'container' in content


class TestNavigationPerformance:
    """Performance tests for navigation system"""
    
    def setup_method(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        self.app_context.pop()
    
    @pytest.mark.performance
    def test_navigation_load_time(self):
        """Test navigation component load time"""
        import time
        
        start_time = time.time()
        response = self.client.get('/analytics/executive')
        load_time = time.time() - start_time
        
        assert response.status_code == 200
        assert load_time < 0.5, f"Navigation load time {load_time:.2f}s too slow"
    
    @pytest.mark.performance
    def test_route_switching_speed(self):
        """Test speed of switching between routes"""
        import time
        
        routes = [
            '/analytics/executive',
            '/surveys/builder', 
            '/integrations/sources',
            '/settings/account'
        ]
        
        total_time = 0
        for route in routes:
            start_time = time.time()
            response = self.client.get(route)
            route_time = time.time() - start_time
            total_time += route_time
            
            assert response.status_code == 200
            assert route_time < 0.3, f"Route {route} took {route_time:.2f}s"
        
        avg_time = total_time / len(routes)
        assert avg_time < 0.2, f"Average route time {avg_time:.2f}s too slow"