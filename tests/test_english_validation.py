#!/usr/bin/env python3
"""
Quick validation tests for English language support
Tests the actual implementation without Selenium
"""

import requests
import json
import re
from bs4 import BeautifulSoup

class TestEnglishValidation:
    """Validate English language support using HTTP requests"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        
    def test_language_toggle_presence(self):
        """Test that language toggle button exists on all pages"""
        pages = ['/', '/feedback', '/dashboard/realtime', '/surveys', '/login', '/register']
        results = {}
        
        for page in pages:
            try:
                response = requests.get(f"{self.base_url}{page}", timeout=5)
                if response.status_code == 200:
                    content = response.text
                    has_toggle = 'langToggle' in content and 'toggleLanguage' in content
                    has_i18n_script = '/static/js/i18n.js' in content
                    results[page] = {
                        'status': response.status_code,
                        'has_toggle': has_toggle,
                        'has_i18n_script': has_i18n_script,
                        'success': has_toggle and has_i18n_script
                    }
                else:
                    results[page] = {
                        'status': response.status_code,
                        'has_toggle': False,
                        'has_i18n_script': False,
                        'success': False
                    }
            except Exception as e:
                results[page] = {
                    'status': 'error',
                    'error': str(e),
                    'success': False
                }
        
        return results
    
    def test_i18n_attributes(self):
        """Test that data-i18n attributes are present"""
        pages = ['/', '/feedback', '/login']
        results = {}
        
        for page in pages:
            try:
                response = requests.get(f"{self.base_url}{page}", timeout=5)
                if response.status_code == 200:
                    content = response.text
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Count data-i18n elements
                    i18n_elements = soup.find_all(attrs={'data-i18n': True})
                    i18n_placeholder_elements = soup.find_all(attrs={'data-i18n-placeholder': True})
                    
                    results[page] = {
                        'status': response.status_code,
                        'i18n_elements': len(i18n_elements),
                        'i18n_placeholder_elements': len(i18n_placeholder_elements),
                        'total_translatable': len(i18n_elements) + len(i18n_placeholder_elements),
                        'success': len(i18n_elements) > 0
                    }
                    
                    # Sample some data-i18n keys
                    sample_keys = [elem.get('data-i18n') for elem in i18n_elements[:5]]
                    results[page]['sample_keys'] = sample_keys
                    
                else:
                    results[page] = {'status': response.status_code, 'success': False}
            except Exception as e:
                results[page] = {'status': 'error', 'error': str(e), 'success': False}
        
        return results
    
    def test_javascript_functionality(self):
        """Test that i18n.js is accessible and contains translations"""
        try:
            response = requests.get(f"{self.base_url}/static/js/i18n.js", timeout=5)
            if response.status_code == 200:
                content = response.text
                
                # Check for key components
                has_language_manager = 'LanguageManager' in content
                has_translations = 'translations' in content and 'ar:' in content and 'en:' in content
                has_toggle_function = 'toggleLanguage' in content
                has_update_function = 'updateAllTranslations' in content
                
                # Count translation keys
                ar_matches = re.findall(r'ar:\s*{', content)
                en_matches = re.findall(r'en:\s*{', content)
                
                return {
                    'status': response.status_code,
                    'has_language_manager': has_language_manager,
                    'has_translations': has_translations,
                    'has_toggle_function': has_toggle_function,
                    'has_update_function': has_update_function,
                    'ar_sections': len(ar_matches),
                    'en_sections': len(en_matches),
                    'success': all([has_language_manager, has_translations, has_toggle_function])
                }
            else:
                return {'status': response.status_code, 'success': False}
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'success': False}
    
    def test_content_structure(self):
        """Test that pages have proper bilingual structure"""
        test_page = '/'
        try:
            response = requests.get(f"{self.base_url}{test_page}", timeout=5)
            if response.status_code == 200:
                content = response.text
                soup = BeautifulSoup(content, 'html.parser')
                
                # Check HTML attributes
                html_tag = soup.find('html')
                has_lang_attr = html_tag and html_tag.get('lang') == 'ar'
                has_dir_attr = html_tag and html_tag.get('dir') == 'rtl'
                
                # Check for brand text element
                brand_element = soup.find(id='brandText')
                has_brand_element = brand_element is not None
                
                # Check for language toggle elements
                lang_toggle = soup.find(id='langToggle')
                lang_text = soup.find(id='langText')
                has_toggle_elements = lang_toggle is not None and lang_text is not None
                
                return {
                    'status': response.status_code,
                    'has_lang_attr': has_lang_attr,
                    'has_dir_attr': has_dir_attr,
                    'has_brand_element': has_brand_element,
                    'has_toggle_elements': has_toggle_elements,
                    'success': all([has_lang_attr, has_dir_attr, has_toggle_elements])
                }
            else:
                return {'status': response.status_code, 'success': False}
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'success': False}
    
    def run_all_tests(self):
        """Run all validation tests and return summary"""
        print("🔍 Running English Language Support Validation Tests...\n")
        
        # Test 1: Language toggle presence
        print("1. Testing language toggle presence...")
        toggle_results = self.test_language_toggle_presence()
        toggle_success = sum(1 for r in toggle_results.values() if r.get('success', False))
        print(f"   ✓ {toggle_success}/{len(toggle_results)} pages have working language toggle")
        
        # Test 2: i18n attributes
        print("\n2. Testing i18n attributes...")
        i18n_results = self.test_i18n_attributes()
        i18n_success = sum(1 for r in i18n_results.values() if r.get('success', False))
        total_translatable = sum(r.get('total_translatable', 0) for r in i18n_results.values())
        print(f"   ✓ {i18n_success}/{len(i18n_results)} pages have i18n attributes")
        print(f"   ✓ {total_translatable} total translatable elements found")
        
        # Test 3: JavaScript functionality
        print("\n3. Testing JavaScript i18n system...")
        js_results = self.test_javascript_functionality()
        js_success = js_results.get('success', False)
        print(f"   {'✓' if js_success else '✗'} i18n.js system functional")
        if js_success:
            print(f"   ✓ {js_results.get('ar_sections', 0)} Arabic translation sections")
            print(f"   ✓ {js_results.get('en_sections', 0)} English translation sections")
        
        # Test 4: Content structure
        print("\n4. Testing content structure...")
        structure_results = self.test_content_structure()
        structure_success = structure_results.get('success', False)
        print(f"   {'✓' if structure_success else '✗'} Proper HTML structure for bilingual support")
        
        # Summary
        print(f"\n📊 VALIDATION SUMMARY:")
        print(f"   Language Toggle: {toggle_success}/{len(toggle_results)} pages")
        print(f"   i18n Attributes: {total_translatable} elements")
        print(f"   JavaScript System: {'✓' if js_success else '✗'}")
        print(f"   Content Structure: {'✓' if structure_success else '✗'}")
        
        overall_success = (
            toggle_success > 0 and 
            i18n_success > 0 and 
            js_success and 
            structure_success
        )
        
        print(f"\n🎯 OVERALL STATUS: {'PASS ✓' if overall_success else 'NEEDS ATTENTION ⚠️'}")
        
        return {
            'toggle_results': toggle_results,
            'i18n_results': i18n_results,
            'js_results': js_results,
            'structure_results': structure_results,
            'overall_success': overall_success
        }

if __name__ == "__main__":
    validator = TestEnglishValidation()
    results = validator.run_all_tests()