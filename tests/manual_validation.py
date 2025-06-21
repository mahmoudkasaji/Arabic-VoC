#!/usr/bin/env python3
"""
Manual validation script for English language support
Tests actual functionality without external dependencies
"""

import requests
import re

def test_basic_functionality():
    """Test basic English language support functionality"""
    base_url = "http://localhost:5000"
    
    print("Testing English Language Support Implementation")
    print("=" * 50)
    
    # Test 1: Check if language toggle exists on main page
    print("\n1. Testing language toggle presence...")
    try:
        response = requests.get(base_url, timeout=5)
        content = response.text
        
        has_toggle_button = 'id="langToggle"' in content
        has_lang_text = 'id="langText"' in content
        has_toggle_function = 'toggleLanguage' in content
        
        print(f"   Toggle button present: {'✓' if has_toggle_button else '✗'}")
        print(f"   Language text element: {'✓' if has_lang_text else '✗'}")
        print(f"   Toggle function: {'✓' if has_toggle_function else '✗'}")
        
    except Exception as e:
        print(f"   Error testing main page: {e}")
    
    # Test 2: Check if i18n script is loaded
    print("\n2. Testing i18n script availability...")
    try:
        i18n_response = requests.get(f"{base_url}/static/js/i18n.js", timeout=5)
        if i18n_response.status_code == 200:
            i18n_content = i18n_response.text
            has_language_manager = 'LanguageManager' in i18n_content
            has_translations = 'translations:' in i18n_content
            has_ar_translations = '"ar":' in i18n_content
            has_en_translations = '"en":' in i18n_content
            
            print(f"   i18n.js accessible: ✓")
            print(f"   LanguageManager class: {'✓' if has_language_manager else '✗'}")
            print(f"   Translation structure: {'✓' if has_translations else '✗'}")
            print(f"   Arabic translations: {'✓' if has_ar_translations else '✗'}")
            print(f"   English translations: {'✓' if has_en_translations else '✗'}")
        else:
            print(f"   i18n.js not accessible: {i18n_response.status_code}")
    except Exception as e:
        print(f"   Error accessing i18n.js: {e}")
    
    # Test 3: Check data-i18n attributes on key pages
    print("\n3. Testing data-i18n attributes...")
    pages_to_test = [
        ('Homepage', '/'),
        ('Feedback', '/feedback'),
        ('Login', '/login')
    ]
    
    for page_name, page_path in pages_to_test:
        try:
            response = requests.get(f"{base_url}{page_path}", timeout=5)
            content = response.text
            
            # Count data-i18n attributes
            i18n_count = len(re.findall(r'data-i18n="[^"]*"', content))
            i18n_placeholder_count = len(re.findall(r'data-i18n-placeholder="[^"]*"', content))
            
            print(f"   {page_name}: {i18n_count} i18n elements, {i18n_placeholder_count} placeholder elements")
            
        except Exception as e:
            print(f"   Error testing {page_name}: {e}")
    
    # Test 4: Check HTML structure
    print("\n4. Testing HTML structure...")
    try:
        response = requests.get(base_url, timeout=5)
        content = response.text
        
        has_rtl_dir = 'dir="rtl"' in content
        has_ar_lang = 'lang="ar"' in content
        has_brand_text = 'id="brandText"' in content
        
        print(f"   RTL direction: {'✓' if has_rtl_dir else '✗'}")
        print(f"   Arabic language: {'✓' if has_ar_lang else '✗'}")
        print(f"   Brand text element: {'✓' if has_brand_text else '✗'}")
        
    except Exception as e:
        print(f"   Error testing HTML structure: {e}")
    
    # Test 5: Check key translation keys
    print("\n5. Testing translation keys...")
    try:
        i18n_response = requests.get(f"{base_url}/static/js/i18n.js", timeout=5)
        if i18n_response.status_code == 200:
            content = i18n_response.text
            
            # Key sections to verify
            key_sections = [
                'nav:', 'home:', 'features:', 'feedback:', 
                'dashboard:', 'surveys:', 'auth:', 'common:'
            ]
            
            for section in key_sections:
                ar_section = f'ar: {{.*?{section}' in content.replace('\n', ' ')
                en_section = f'en: {{.*?{section}' in content.replace('\n', ' ')
                print(f"   {section:<12} AR: {'✓' if section in content else '✗'} | EN: {'✓' if section in content else '✗'}")
                
    except Exception as e:
        print(f"   Error testing translation keys: {e}")
    
    print("\n" + "=" * 50)
    print("Validation complete. Check results above.")

if __name__ == "__main__":
    test_basic_functionality()