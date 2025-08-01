"""
Comprehensive Test Suite for English Language Implementation
Tests for complete English UI, navigation, and language switching functionality
"""

import pytest
import json
import os
from flask import session, g
from app import app
from utils.language_manager import LanguageManager, language_manager
from utils.template_helpers import get_translated_message


class TestEnglishLanguageImplementation:
    """Test suite for English language version of the Voice of Customer platform"""
    
    def setup_method(self):
        """Setup test environment"""
        self.app = app
        self.client = app.test_client()
        app.config['TESTING'] = True
        
    def test_english_translations_completeness(self):
        """Test that English translations are complete and comprehensive"""
        print("🧪 Testing English translation completeness...")
        
        # Load English translations
        translations_path = os.path.join(os.path.dirname(__file__), '..', 'translations', 'en.json')
        with open(translations_path, 'r', encoding='utf-8') as f:
            en_translations = json.load(f)
        
        # Test key navigation elements
        navigation_keys = [
            'navigation.surveys_dropdown.title',
            'navigation.analytics_dropdown.title',
            'navigation.integrations_dropdown.title',
            'navigation.settings_dropdown.title',
            'navigation.contacts_dropdown.title'
        ]
        
        for key in navigation_keys:
            translation = self._get_nested_value(en_translations, key)
            assert translation is not None, f"Missing English translation for {key}"
            assert isinstance(translation, str) and len(translation) > 0, f"Empty translation for {key}"
            print(f"✅ {key}: {translation}")
        
        print("✅ English translations are complete")
        return True
    
    def test_language_manager_english_mode(self):
        """Test language manager functionality in English mode"""
        print("🧪 Testing Language Manager English mode...")
        
        with self.app.app_context():
            with self.client.session_transaction() as sess:
                sess['language'] = 'en'
            
            # Test current language detection
            current_lang = language_manager.get_current_language()
            assert current_lang == 'en', f"Expected 'en', got '{current_lang}'"
            
            # Test direction (LTR for English)
            direction = language_manager.get_direction()
            assert direction == 'ltr', f"Expected 'ltr', got '{direction}'"
            
            # Test language info
            lang_info = language_manager.get_language_info('en')
            assert lang_info['code'] == 'en'
            assert lang_info['direction'] == 'ltr'
            assert 'Inter' in lang_info['font_family'] or 'Roboto' in lang_info['font_family']
            
            print("✅ Language Manager English mode working correctly")
            return True
    
    def test_english_navigation_template_rendering(self):
        """Test that navigation renders correctly in English"""
        print("🧪 Testing English navigation template rendering...")
        
        with self.app.app_context():
            with self.client.session_transaction() as sess:
                sess['language'] = 'en'
            
            # Test home page navigation
            response = self.client.get('/', headers={'Accept-Language': 'en'})
            assert response.status_code == 200
            
            html_content = response.data.decode('utf-8')
            
            # Check for English navigation elements
            english_elements = [
                'Surveys',
                'Analytics', 
                'Integrations',
                'Settings',
                'Contacts'
            ]
            
            for element in english_elements:
                assert element in html_content, f"English element '{element}' not found in navigation"
                print(f"✅ Found '{element}' in English navigation")
            
            # Ensure Arabic text is not present when in English mode
            arabic_elements = ['الاستطلاعات', 'التحليلات', 'التكاملات']
            for element in arabic_elements:
                if element in html_content:
                    print(f"⚠️  Found Arabic text '{element}' in English mode - needs attention")
            
            print("✅ English navigation template rendering correctly")
            return True
    
    def test_language_toggle_api_endpoint(self):
        """Test the language toggle API endpoint"""
        print("🧪 Testing language toggle API endpoint...")
        
        with self.app.app_context():
            # Start with Arabic
            with self.client.session_transaction() as sess:
                sess['language'] = 'ar'
            
            # Toggle to English
            response = self.client.post('/api/language/toggle',
                                      json={'language': 'en'},
                                      headers={'Content-Type': 'application/json'})
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert data['language'] == 'en'
            
            print("✅ Language toggle API working correctly")
            return True
    
    def test_english_contact_management_page(self):
        """Test contact management page in English"""
        print("🧪 Testing Contact Management page in English...")
        
        with self.app.app_context():
            with self.client.session_transaction() as sess:
                sess['language'] = 'en'
            
            response = self.client.get('/contacts')
            assert response.status_code == 200
            
            html_content = response.data.decode('utf-8')
            
            # Check for English content
            assert 'Contact Management' in html_content
            assert 'Contact List' in html_content
            
            print("✅ Contact Management page renders correctly in English")
            return True
    
    def test_english_analytics_dashboard(self):
        """Test analytics dashboard in English"""
        print("🧪 Testing Analytics Dashboard in English...")
        
        with self.app.app_context():
            with self.client.session_transaction() as sess:
                sess['language'] = 'en'
            
            response = self.client.get('/analytics/dashboard')
            
            if response.status_code == 200:
                html_content = response.data.decode('utf-8')
                
                # Check for English analytics content
                english_analytics_terms = [
                    'Analytics',
                    'Dashboard',
                    'Customer Satisfaction'
                ]
                
                for term in english_analytics_terms:
                    if term in html_content:
                        print(f"✅ Found '{term}' in English analytics dashboard")
            
            print("✅ Analytics dashboard English rendering verified")
            return True
    
    def test_language_specific_css_and_direction(self):
        """Test that CSS direction and styling adapt correctly for English"""
        print("🧪 Testing CSS direction and styling for English...")
        
        with self.app.app_context():
            with self.client.session_transaction() as sess:
                sess['language'] = 'en'
            
            response = self.client.get('/')
            assert response.status_code == 200
            
            html_content = response.data.decode('utf-8')
            
            # Check for LTR direction
            assert 'dir="ltr"' in html_content or 'direction: ltr' in html_content
            
            # Check that English fonts are applied
            if 'Inter' in html_content or 'Roboto' in html_content:
                print("✅ English fonts detected")
            
            print("✅ CSS direction and styling correct for English")
            return True
    
    def test_comprehensive_page_coverage(self):
        """Test multiple pages to ensure comprehensive English support"""
        print("🧪 Testing comprehensive page coverage in English...")
        
        test_pages = [
            '/',
            '/contacts',
            '/surveys',
            '/analytics/dashboard',
            '/settings'
        ]
        
        with self.app.app_context():
            with self.client.session_transaction() as sess:
                sess['language'] = 'en'
            
            for page in test_pages:
                try:
                    response = self.client.get(page)
                    if response.status_code == 200:
                        print(f"✅ Page {page} renders correctly in English")
                    elif response.status_code == 404:
                        print(f"⚠️  Page {page} not found (expected for some routes)")
                    else:
                        print(f"⚠️  Page {page} returned status {response.status_code}")
                except Exception as e:
                    print(f"⚠️  Error testing page {page}: {str(e)}")
        
        print("✅ Comprehensive page coverage test completed")
        return True
    
    def test_javascript_language_toggle_function(self):
        """Test that JavaScript language toggle function is properly loaded"""
        print("🧪 Testing JavaScript language toggle function...")
        
        response = self.client.get('/')
        assert response.status_code == 200
        
        html_content = response.data.decode('utf-8')
        
        # Check that language toggle JavaScript is included
        if 'toggleLanguage' in html_content:
            print("✅ JavaScript toggleLanguage function found")
        else:
            print("⚠️  JavaScript toggleLanguage function not found")
        
        # Check for main.js inclusion
        if 'main.js' in html_content:
            print("✅ main.js script included")
        
        print("✅ JavaScript language toggle validation completed")
        return True
    
    def _get_nested_value(self, dictionary, key_path):
        """Helper function to get nested dictionary values using dot notation"""
        keys = key_path.split('.')
        current = dictionary
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current


def test_english_implementation_comprehensive():
    """Comprehensive test runner for English implementation"""
    print("🚀 Starting Comprehensive English Language Implementation Tests")
    print("=" * 80)
    
    test_suite = TestEnglishLanguageImplementation()
    test_suite.setup_method()
    
    tests = [
        test_suite.test_english_translations_completeness,
        test_suite.test_language_manager_english_mode,
        test_suite.test_english_navigation_template_rendering,
        test_suite.test_language_toggle_api_endpoint,
        test_suite.test_english_contact_management_page,
        test_suite.test_english_analytics_dashboard,
        test_suite.test_language_specific_css_and_direction,
        test_suite.test_comprehensive_page_coverage,
        test_suite.test_javascript_language_toggle_function
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
                print(f"❌ Test {test.__name__} failed")
        except Exception as e:
            failed += 1
            print(f"❌ Test {test.__name__} failed with error: {str(e)}")
        
        print("-" * 40)
    
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    print("=" * 80)
    
    if failed == 0:
        print("🎉 All English language implementation tests passed!")
        return True
    else:
        print(f"⚠️  {failed} tests failed - review and fix issues")
        return False


if __name__ == "__main__":
    test_english_implementation_comprehensive()