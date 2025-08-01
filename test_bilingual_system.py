"""
Comprehensive Bilingual System Test
Test script to verify all translation components are working
"""

from app import app
import requests
import json

def test_translation_system():
    """Test the core translation system"""
    print("🧪 TESTING BILINGUAL SYSTEM")
    print("=" * 50)
    
    with app.app_context():
        from utils.language_manager import language_manager
        from flask import g
        
        # Test 1: Translation loading
        print("1. TRANSLATION LOADING:")
        ar_count = len(language_manager.translations.get('ar', {}))
        en_count = len(language_manager.translations.get('en', {}))
        print(f"   Arabic translations: {ar_count}")
        print(f"   English translations: {en_count}")
        
        # Test 2: Core translation function
        print("\n2. CORE TRANSLATION FUNCTION:")
        test_keys = ['app.name', 'navigation.surveys_dropdown.title', 'language.switch_to']
        for key in test_keys:
            ar_val = language_manager.translate(key, force_lang='ar')
            en_val = language_manager.translate(key, force_lang='en')
            print(f"   {key}:")
            print(f"     AR: '{ar_val}'")
            print(f"     EN: '{en_val}'")
        
        # Test 3: Template filter registration
        print("\n3. TEMPLATE FILTER REGISTRATION:")
        if 'translate' in app.jinja_env.filters:
            print("   ✓ translate filter registered")
            
            # Test the filter directly
            filter_func = app.jinja_env.filters['translate']
            test_result = filter_func('app.name')
            print(f"   ✓ Filter test result: '{test_result}'")
        else:
            print("   ✗ translate filter NOT registered")
        
        # Test 4: Template globals
        print("\n4. TEMPLATE GLOBALS:")
        globals_to_check = ['get_lang', 'get_dir', 'get_language_info']
        for global_name in globals_to_check:
            if global_name in app.jinja_env.globals:
                print(f"   ✓ {global_name} registered")
            else:
                print(f"   ✗ {global_name} NOT registered")

def test_live_pages():
    """Test actual page rendering"""
    print("\n5. LIVE PAGE TESTING:")
    
    base_url = "http://localhost:5000"
    
    # Test Arabic version
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            content = response.text
            if "منصة صوت العميل" in content:
                print("   ✓ Arabic content found")
            elif "Voice of Customer Platform" in content:
                print("   ! English content found instead of Arabic")
            else:
                print("   ✗ No expected content found")
        else:
            print(f"   ✗ HTTP {response.status_code}")
    except Exception as e:
        print(f"   ✗ Request failed: {e}")
    
    # Test language switching
    try:
        response = requests.get(f"{base_url}/language/toggle", allow_redirects=True, timeout=5)
        if response.status_code == 200:
            print("   ✓ Language toggle works")
        else:
            print(f"   ✗ Language toggle failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Language toggle failed: {e}")

def main():
    """Run all tests"""
    test_translation_system()
    test_live_pages()
    
    print("\n" + "=" * 50)
    print("🎯 RECOMMENDED FIXES:")
    print("1. Ensure template helpers are registered early in app initialization")
    print("2. Add explicit error handling for translation system")
    print("3. Test translation filter directly in templates")
    print("4. Verify language detection works in request context")

if __name__ == "__main__":
    main()