"""
Phase 1 Testing: Language Infrastructure Validation
Tests for language management system, translation system, and template helpers
"""

import pytest
import json
import os
from flask import session
from utils.language_manager import LanguageManager, language_manager
from utils.template_helpers import get_translated_message, get_error_message, get_success_message

class TestLanguageManager:
    """Test LanguageManager core functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        self.lm = LanguageManager()
    
    def test_supported_languages(self):
        """Test supported languages configuration"""
        assert 'ar' in self.lm.supported_languages
        assert 'en' in self.lm.supported_languages
        assert self.lm.default_language == 'ar'
        assert self.lm.fallback_language == 'en'
    
    def test_translation_files_loaded(self):
        """Test translation files are loaded correctly"""
        assert 'ar' in self.lm.translations
        assert 'en' in self.lm.translations
        
        # Test key Arabic translations exist
        ar_translations = self.lm.translations['ar']
        assert 'app' in ar_translations
        assert 'navigation' in ar_translations
        assert 'buttons' in ar_translations
        
        # Test key English translations exist
        en_translations = self.lm.translations['en']
        assert 'app' in en_translations
        assert 'navigation' in en_translations
        assert 'buttons' in en_translations
    
    def test_direction_detection(self):
        """Test RTL/LTR direction detection"""
        assert self.lm.get_direction('ar') == 'rtl'
        assert self.lm.get_direction('en') == 'ltr'
        assert self.lm.get_direction('he') == 'rtl'  # Hebrew
        assert self.lm.get_direction('fr') == 'ltr'  # French (unsupported but should work)
    
    def test_language_info(self):
        """Test language info retrieval"""
        ar_info = self.lm.get_language_info('ar')
        assert ar_info['code'] == 'ar'
        assert ar_info['direction'] == 'rtl'
        assert 'Cairo' in ar_info['font_family']
        
        en_info = self.lm.get_language_info('en')
        assert en_info['code'] == 'en'
        assert en_info['direction'] == 'ltr'
        assert 'Inter' in en_info['font_family']
    
    def test_opposite_language(self):
        """Test opposite language detection"""
        assert self.lm.get_opposite_language('ar') == 'en'
        assert self.lm.get_opposite_language('en') == 'ar'
    
    def test_translation_basic(self):
        """Test basic translation functionality"""
        # Test simple key
        ar_app_name = self.lm.translate('app.name', 'ar')
        en_app_name = self.lm.translate('app.name', 'en')
        
        assert ar_app_name == 'منصة صوت العميل'
        assert en_app_name == 'Voice of Customer Platform'
        
        # Test nested key
        ar_create_btn = self.lm.translate('buttons.create', 'ar')
        en_create_btn = self.lm.translate('buttons.create', 'en')
        
        assert ar_create_btn == 'إنشاء'
        assert en_create_btn == 'Create'
    
    def test_translation_fallback(self):
        """Test translation fallback mechanism"""
        # Test missing key fallback
        missing_key = self.lm.translate('nonexistent.key', 'ar')
        assert missing_key == '[nonexistent.key]'
        
        # Test partial key fallback
        partial_key = self.lm.translate('app.nonexistent', 'ar')
        assert partial_key == '[app.nonexistent]'
    
    def test_translation_with_variables(self):
        """Test translation with variable substitution"""
        # Add test translation with variables
        self.lm.translations['en']['test'] = {'welcome': 'Welcome, {name}!'}
        self.lm.translations['ar']['test'] = {'welcome': 'مرحباً، {name}!'}
        
        en_welcome = self.lm.translate('test.welcome', 'en', name='Ahmed')
        ar_welcome = self.lm.translate('test.welcome', 'ar', name='Ahmed')
        
        assert en_welcome == 'Welcome, Ahmed!'
        assert ar_welcome == 'مرحباً، Ahmed!'

class TestTranslationFiles:
    """Test translation file integrity"""
    
    def test_translation_files_exist(self):
        """Test translation files exist and are readable"""
        translations_dir = os.path.join(os.path.dirname(__file__), '..', 'translations')
        
        ar_file = os.path.join(translations_dir, 'ar.json')
        en_file = os.path.join(translations_dir, 'en.json')
        
        assert os.path.exists(ar_file), "Arabic translation file missing"
        assert os.path.exists(en_file), "English translation file missing"
    
    def test_translation_files_valid_json(self):
        """Test translation files contain valid JSON"""
        translations_dir = os.path.join(os.path.dirname(__file__), '..', 'translations')
        
        # Test Arabic file
        with open(os.path.join(translations_dir, 'ar.json'), 'r', encoding='utf-8') as f:
            ar_data = json.load(f)
            assert isinstance(ar_data, dict)
            assert len(ar_data) > 0
        
        # Test English file
        with open(os.path.join(translations_dir, 'en.json'), 'r', encoding='utf-8') as f:
            en_data = json.load(f)
            assert isinstance(en_data, dict)
            assert len(en_data) > 0
    
    def test_translation_key_consistency(self):
        """Test that both translation files have consistent key structure"""
        translations_dir = os.path.join(os.path.dirname(__file__), '..', 'translations')
        
        with open(os.path.join(translations_dir, 'ar.json'), 'r', encoding='utf-8') as f:
            ar_data = json.load(f)
        
        with open(os.path.join(translations_dir, 'en.json'), 'r', encoding='utf-8') as f:
            en_data = json.load(f)
        
        # Test major sections exist in both
        major_sections = ['app', 'navigation', 'buttons', 'forms', 'messages']
        for section in major_sections:
            assert section in ar_data, f"Section '{section}' missing from Arabic translations"
            assert section in en_data, f"Section '{section}' missing from English translations"

class TestTemplateHelpers:
    """Test template helper functions"""
    
    def test_get_translated_message(self):
        """Test helper function for getting translated messages"""
        ar_message = get_translated_message('app.name', 'ar')
        en_message = get_translated_message('app.name', 'en')
        
        assert ar_message == 'منصة صوت العميل'
        assert en_message == 'Voice of Customer Platform'
    
    def test_get_error_message(self):
        """Test error message helper"""
        ar_error = get_error_message('general_error', 'ar')
        en_error = get_error_message('general_error', 'en')
        
        assert ar_error == 'حدث خطأ غير متوقع'
        assert en_error == 'An unexpected error occurred'
    
    def test_get_success_message(self):
        """Test success message helper"""
        ar_success = get_success_message('saved', 'ar')
        en_success = get_success_message('saved', 'en')
        
        assert ar_success == 'تم الحفظ بنجاح'
        assert en_success == 'Successfully saved'

if __name__ == '__main__':
    # Run basic validation
    print("🧪 Running Phase 1 Language Infrastructure Tests...")
    
    # Test 1: Language Manager Initialization
    try:
        lm = LanguageManager()
        print("✅ Language Manager initialized successfully")
    except Exception as e:
        print(f"❌ Language Manager initialization failed: {e}")
    
    # Test 2: Translation Loading
    try:
        assert 'ar' in lm.translations and 'en' in lm.translations
        print("✅ Translation files loaded successfully")
    except Exception as e:
        print(f"❌ Translation loading failed: {e}")
    
    # Test 3: Basic Translation
    try:
        ar_name = lm.translate('app.name', 'ar')
        en_name = lm.translate('app.name', 'en')
        assert ar_name and en_name
        print(f"✅ Basic translation works: '{ar_name}' / '{en_name}'")
    except Exception as e:
        print(f"❌ Basic translation failed: {e}")
    
    # Test 4: Direction Detection
    try:
        assert lm.get_direction('ar') == 'rtl'
        assert lm.get_direction('en') == 'ltr'
        print("✅ Direction detection works correctly")
    except Exception as e:
        print(f"❌ Direction detection failed: {e}")
    
    print("\n🎉 Phase 1 Infrastructure Testing Complete!")