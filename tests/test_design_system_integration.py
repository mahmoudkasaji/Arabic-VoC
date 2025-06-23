"""
Design System Integration Tests
Validates unified design system implementation across all pages
"""

import pytest
import requests
from bs4 import BeautifulSoup


class TestDesignSystemIntegration:
    """Test design system consistency and functionality"""
    
    def setup_method(self):
        self.base_url = "http://localhost:5000"
        self.pages = [
            ('/', 'Homepage'),
            ('/settings/system', 'Settings'),
            ('/feedback', 'Feedback Form'),
            ('/analytics/executive', 'Executive Dashboard')
        ]
    
    def test_design_system_css_loading(self):
        """Test that design system CSS loads correctly"""
        response = requests.get(f"{self.base_url}/static/css/design-system.css", timeout=10)
        assert response.status_code == 200, "Design system CSS should be accessible"
        
        css_content = response.text
        
        # Check for essential CSS custom properties
        required_properties = [
            '--primary-500',
            '--space-4',
            '--radius-xl',
            '--shadow-base',
            '--font-family-primary'
        ]
        
        for prop in required_properties:
            assert prop in css_content, f"CSS custom property {prop} should be defined"
    
    def test_component_classes_defined(self):
        """Test that all component classes are defined in CSS"""
        response = requests.get(f"{self.base_url}/static/css/design-system.css", timeout=10)
        css_content = response.text
        
        required_classes = [
            '.card-custom',
            '.btn-primary-custom',
            '.form-control-custom',
            '.container-custom',
            '.arabic-title',
            '.navbar-custom'
        ]
        
        for css_class in required_classes:
            assert css_class in css_content, f"Component class {css_class} should be defined"
    
    def test_html_structure_consistency(self):
        """Test that all pages have consistent HTML structure"""
        for path, name in self.pages:
            response = requests.get(f"{self.base_url}{path}", timeout=15)
            assert response.status_code == 200, f"{name} should load successfully"
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check basic HTML structure
            html_tag = soup.find('html')
            assert html_tag is not None, f"{name} should have HTML tag"
            assert html_tag.get('lang') == 'ar', f"{name} should have Arabic language"
            assert html_tag.get('dir') == 'rtl', f"{name} should have RTL direction"
    
    def test_shared_components_inclusion(self):
        """Test that shared components are included"""
        for path, name in self.pages:
            response = requests.get(f"{self.base_url}{path}", timeout=15)
            content = response.text
            
            # Check for shared component inclusions
            shared_components = [
                'components/head.html',
                'components/scripts.html'
            ]
            
            for component in shared_components:
                # Should be included via template inheritance
                assert 'design-system.css' in content, f"{name} should load design system CSS"
                assert 'bootstrap' in content.lower(), f"{name} should load Bootstrap"
    
    def test_design_system_component_usage(self):
        """Test that pages use design system components"""
        component_expectations = {
            '/settings/system': ['card-custom', 'btn-primary-custom', 'form-control-custom'],
            '/': ['btn-primary-custom', 'arabic-title'],
            '/feedback': ['card-custom', 'form-control-custom'],
            '/analytics/executive': ['card-custom']
        }
        
        for path, expected_components in component_expectations.items():
            response = requests.get(f"{self.base_url}{path}", timeout=15)
            content = response.text
            
            # Check for at least some expected components
            found_components = [comp for comp in expected_components if comp in content]
            assert len(found_components) > 0, f"Page {path} should use design system components"
    
    def test_color_system_usage(self):
        """Test that pages use design system color variables"""
        for path, name in self.pages:
            response = requests.get(f"{self.base_url}{path}", timeout=15)
            content = response.text
            
            # Should use design system CSS or color indicators
            color_indicators = [
                'design-system.css',
                'primary-custom',
                'text-primary',
                'Cairo',
                'arabic-title'
            ]
            
            has_color_system = any(indicator in content for indicator in color_indicators)
            assert has_color_system, f"{name} should use design system colors"
    
    def test_typography_consistency(self):
        """Test typography consistency across pages"""
        for path, name in self.pages:
            response = requests.get(f"{self.base_url}{path}", timeout=15)
            content = response.text
            
            # Check for consistent typography
            typography_indicators = [
                'Cairo',
                'Amiri',
                'arabic-title'
            ]
            
            has_typography = any(indicator in content for indicator in typography_indicators)
            assert has_typography, f"{name} should use consistent Arabic typography"
    
    def test_responsive_design_implementation(self):
        """Test that responsive design is implemented"""
        css_response = requests.get(f"{self.base_url}/static/css/design-system.css", timeout=10)
        css_content = css_response.text
        
        # Check for responsive breakpoints
        responsive_indicators = [
            '@media (max-width: 768px)',
            '@media (max-width: 576px)',
            'container-custom'
        ]
        
        found_responsive = [indicator for indicator in responsive_indicators if indicator in css_content]
        assert len(found_responsive) >= 2, f"Responsive design should include media queries and containers"
    
    def test_arabic_rtl_support(self):
        """Test Arabic RTL support across all pages"""
        for path, name in self.pages:
            response = requests.get(f"{self.base_url}{path}", timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check RTL direction
            html_tag = soup.find('html')
            assert html_tag.get('dir') == 'rtl', f"{name} should have RTL direction"
            
            # Check for Arabic content
            content = response.text
            arabic_indicators = [
                'منصة صوت العميل',
                'إعدادات',
                'تعليق',
                'التحليلات'
            ]
            
            has_arabic = any(indicator in content for indicator in arabic_indicators)
            assert has_arabic, f"{name} should contain Arabic text"
    
    def test_interactive_elements_consistency(self):
        """Test that interactive elements use consistent styling"""
        for path, name in self.pages:
            response = requests.get(f"{self.base_url}{path}", timeout=15)
            content = response.text
            
            # Check for design system button classes or interactive elements
            interactive_indicators = [
                'btn-primary-custom',
                'btn-outline-custom',
                'card-interactive',
                'nav-link',
                'form-control'
            ]
            
            has_interactive = any(indicator in content for indicator in interactive_indicators)
            assert has_interactive, f"{name} should use consistent interactive styling"


class TestDesignSystemPerformance:
    """Test design system performance impact"""
    
    def setup_method(self):
        self.base_url = "http://localhost:5000"
    
    def test_css_file_size_reasonable(self):
        """Test that design system CSS file size is reasonable"""
        response = requests.get(f"{self.base_url}/static/css/design-system.css", timeout=10)
        css_size = len(response.text)
        
        # CSS should be comprehensive but not excessive (under 100KB)
        assert css_size < 100000, f"CSS file size ({css_size} bytes) should be reasonable"
        assert css_size > 5000, f"CSS file size ({css_size} bytes) should be substantial"
    
    def test_page_load_time_acceptable(self):
        """Test that pages load within acceptable time"""
        import time
        
        pages = ['/', '/settings/system', '/feedback']
        
        for page in pages:
            start_time = time.time()
            response = requests.get(f"{self.base_url}{page}", timeout=10)
            load_time = time.time() - start_time
            
            assert response.status_code == 200, f"Page {page} should load successfully"
            assert load_time < 3.0, f"Page {page} should load within 3 seconds (took {load_time:.2f}s)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])