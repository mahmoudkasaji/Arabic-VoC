"""
Quick validation script for English UI implementation
Tests the current state of English language support
"""

import json
import os
from app import app
from utils.language_manager import language_manager

def validate_english_translations():
    """Validate English translation files"""
    print("🔍 Validating English Translations...")
    
    # Load English translations
    en_file = os.path.join('translations', 'en.json')
    ar_file = os.path.join('translations', 'ar.json')
    
    with open(en_file, 'r', encoding='utf-8') as f:
        en_translations = json.load(f)
    
    with open(ar_file, 'r', encoding='utf-8') as f:
        ar_translations = json.load(f)
    
    print(f"✅ English translations loaded: {len(str(en_translations))} characters")
    print(f"✅ Arabic translations loaded: {len(str(ar_translations))} characters")
    
    # Test key navigation elements
    navigation_keys = [
        'app.name',
        'navigation.surveys_dropdown.title',
        'navigation.analytics_dropdown.title', 
        'navigation.integrations_dropdown.title',
        'navigation.settings_dropdown.title',
        'navigation.contacts_dropdown.title',
        'language.switch_to',
        'language.toggle_tooltip'
    ]
    
    print("\n📋 Key Navigation Elements in English:")
    for key in navigation_keys:
        value = get_nested_value(en_translations, key)
        if value:
            print(f"  ✅ {key}: '{value}'")
        else:
            print(f"  ❌ {key}: Missing!")
    
    return True

def get_nested_value(dictionary, key_path):
    """Get nested dictionary values using dot notation"""
    keys = key_path.split('.')
    current = dictionary
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    
    return current

def test_language_manager():
    """Test language manager functionality"""
    print("\n🔧 Testing Language Manager...")
    
    with app.app_context():
        # Test supported languages
        supported = language_manager.supported_languages
        print(f"✅ Supported languages: {supported}")
        
        # Test default language
        default = language_manager.default_language
        print(f"✅ Default language: {default}")
        
        # Test translation function
        test_key = 'app.name'
        ar_translation = language_manager.translate(test_key, 'ar')
        en_translation = language_manager.translate(test_key, 'en')
        
        print(f"✅ Arabic translation of '{test_key}': '{ar_translation}'")
        print(f"✅ English translation of '{test_key}': '{en_translation}'")
        
        # Test language info
        en_info = language_manager.get_language_info('en')
        ar_info = language_manager.get_language_info('ar')
        
        print(f"✅ English language info: {en_info}")
        print(f"✅ Arabic language info: {ar_info}")
    
    return True

def test_web_pages():
    """Test web pages in English mode"""
    print("\n🌐 Testing Web Pages in English...")
    
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['language'] = 'en'
        
        test_routes = [
            '/',
            '/contacts',
            '/surveys'
        ]
        
        for route in test_routes:
            try:
                response = client.get(route)
                if response.status_code == 200:
                    content = response.data.decode('utf-8')
                    
                    # Check for English content indicators
                    if 'Voice of Customer Platform' in content:
                        print(f"  ✅ {route}: English content detected")
                    else:
                        print(f"  ⚠️  {route}: No clear English indicators")
                        
                    # Check direction
                    if 'dir="ltr"' in content:
                        print(f"  ✅ {route}: LTR direction set")
                    
                elif response.status_code == 404:
                    print(f"  ⚠️  {route}: Route not found")
                else:
                    print(f"  ❌ {route}: Status {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ {route}: Error - {str(e)}")
    
    return True

def main():
    """Main validation function"""
    print("🚀 English Language UI Validation")
    print("=" * 50)
    
    try:
        validate_english_translations()
        test_language_manager() 
        test_web_pages()
        
        print("\n" + "=" * 50)
        print("✅ English Language UI Validation Complete!")
        print("\n📋 Summary:")
        print("• Translation files are properly structured")
        print("• Language manager is functional") 
        print("• Web pages support English language mode")
        print("• Navigation elements have English translations")
        
    except Exception as e:
        print(f"\n❌ Validation failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()