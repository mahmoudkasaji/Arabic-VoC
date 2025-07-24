#!/usr/bin/env python3
"""
Phase 2: Navigation Infrastructure Testing
Tests for dynamic language support in navigation templates
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.language_manager import language_manager
from flask import Flask
from jinja2 import Environment, FileSystemLoader
import tempfile

def test_navigation_template_rendering():
    """Test that navigation templates render correctly with translation filters"""
    print("🧪 Testing Phase 2 Navigation Infrastructure...")
    
    # Set up Jinja2 environment with translation filter
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    
    # Add translation filter to environment
    def translate_filter(key, lang='ar'):
        return language_manager.translate(key, lang)
    
    def get_lang_helper():
        return language_manager.current_language
    
    def get_dir_helper():
        return language_manager.get_direction()
        
    env.filters['translate'] = translate_filter
    env.globals['get_lang'] = get_lang_helper
    env.globals['get_dir'] = get_dir_helper
    
    try:
        # Test navigation template rendering
        nav_template = env.get_template('components/unified_navigation.html')
        
        # Test Arabic rendering
        language_manager.set_language('ar')
        arabic_html = nav_template.render()
        
        # Check for translation placeholders (should be gone)
        if '{{ ' in arabic_html and ' | translate }}' in arabic_html:
            print("❌ Found untranslated template placeholders in Arabic")
            return False
        
        # Check for Arabic content
        if 'الاستطلاعات' not in arabic_html or 'التحليلات' not in arabic_html:
            print("❌ Arabic translations not found in navigation")
            return False
            
        print("✅ Arabic navigation rendering successful")
        
        # Test English rendering
        language_manager.set_language('en')
        english_html = nav_template.render()
        
        # Check for translation placeholders (should be gone)
        if '{{ ' in english_html and ' | translate }}' in english_html:
            print("❌ Found untranslated template placeholders in English")
            return False
            
        # Check for English content
        if 'Surveys' not in english_html or 'Analytics' not in english_html:
            print("❌ English translations not found in navigation")
            return False
            
        print("✅ English navigation rendering successful")
        
        # Test language toggle button presence
        if 'toggleLanguage()' not in arabic_html:
            print("❌ Language toggle button not found")
            return False
            
        print("✅ Language toggle button integrated")
        
        return True
        
    except Exception as e:
        print(f"❌ Template rendering failed: {e}")
        return False

def test_html_direction_attributes():
    """Test that HTML attributes change correctly"""
    print("🧪 Testing HTML direction attributes...")
    
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    
    def get_lang_helper():
        return language_manager.current_language
    
    def get_dir_helper():
        return language_manager.get_direction()
        
    env.globals['get_lang'] = get_lang_helper
    env.globals['get_dir'] = get_dir_helper
    
    try:
        # Test homepage template
        homepage_template = env.get_template('index_simple.html')
        
        # Test Arabic
        language_manager.set_language('ar')
        arabic_html = homepage_template.render()
        
        if 'lang="ar"' not in arabic_html or 'dir="rtl"' not in arabic_html:
            print("❌ Arabic HTML attributes not set correctly")
            return False
        
        print("✅ Arabic HTML attributes correct (lang='ar' dir='rtl')")
        
        # Test English
        language_manager.set_language('en')
        english_html = homepage_template.render()
        
        if 'lang="en"' not in english_html or 'dir="ltr"' not in english_html:
            print("❌ English HTML attributes not set correctly")
            return False
        
        print("✅ English HTML attributes correct (lang='en' dir='ltr')")
        
        return True
        
    except Exception as e:
        print(f"❌ HTML attribute testing failed: {e}")
        return False

def test_translation_completeness():
    """Test that all required navigation translations exist"""
    print("🧪 Testing translation completeness...")
    
    required_keys = [
        'app.name',
        'navigation.surveys_dropdown.title',
        'navigation.analytics_dropdown.title', 
        'navigation.integrations_dropdown.title',
        'navigation.settings_dropdown.title',
        'language.switch_to',
        'language.toggle_tooltip'
    ]
    
    for key in required_keys:
        # Test Arabic
        arabic_text = language_manager.translate(key, 'ar')
        if not arabic_text or arabic_text == key:
            print(f"❌ Missing Arabic translation for: {key}")
            return False
        
        # Test English  
        english_text = language_manager.translate(key, 'en')
        if not english_text or english_text == key:
            print(f"❌ Missing English translation for: {key}")
            return False
    
    print("✅ All required navigation translations present")
    return True

if __name__ == "__main__":
    print("🧪 Running Phase 2 Navigation Infrastructure Tests...")
    
    tests = [
        test_translation_completeness,
        test_html_direction_attributes,
        test_navigation_template_rendering
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    if passed == len(tests):
        print("🎉 Phase 2 Navigation Infrastructure Testing Complete!")
        print(f"✅ All {passed}/{len(tests)} tests passed")
    else:
        print(f"❌ {len(tests) - passed}/{len(tests)} tests failed")
        print("Phase 2 requires fixes before proceeding to Phase 3")