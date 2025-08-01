"""
Language Management System for Voice of Customer Platform
Handles language detection, switching, and session management
"""

import json
import os
from flask import session, request, current_app
from typing import Dict, Any, Optional

class LanguageManager:
    """Centralized language management for the platform"""
    
    def __init__(self):
        self.translations = {}
        self.supported_languages = ['ar', 'en']
        self.default_language = 'ar'
        self.fallback_language = 'en'
        self._load_translations()
    
    def _load_translations(self):
        """Load translation files into memory"""
        translations_dir = os.path.join(os.path.dirname(__file__), '..', 'translations')
        
        for lang in self.supported_languages:
            translation_file = os.path.join(translations_dir, f'{lang}.json')
            try:
                if os.path.exists(translation_file):
                    with open(translation_file, 'r', encoding='utf-8') as f:
                        self.translations[lang] = json.load(f)
                else:
                    # Create empty translation structure if file doesn't exist
                    self.translations[lang] = {}
                    print(f"Warning: Translation file {translation_file} not found")
            except Exception as e:
                print(f"Error loading translation file {translation_file}: {e}")
                self.translations[lang] = {}
    
    def get_current_language(self) -> str:
        """Get current user's language preference - ENHANCED FIX"""
        try:
            from flask import session, g, has_request_context
            
            # Only proceed if we're in a request context
            if not has_request_context():
                return self.default_language
            
            # 1. Check URL parameter (highest priority) 
            if request and request.args.get('lang') in self.supported_languages:
                lang = request.args.get('lang')
                if lang:
                    self.set_language(lang)
                    return lang
            
            # 2. Use Flask's g object to cache language per request
            if hasattr(g, '_current_language') and g._current_language in self.supported_languages:
                return g._current_language
            
            # 3. Check session with error handling
            try:
                session_lang = session.get('language')
                if session_lang in self.supported_languages:
                    g._current_language = session_lang
                    return session_lang
            except Exception:
                pass
            
            # 4. Check browser Accept-Language header
            if request and request.headers.get('Accept-Language'):
                accept_lang = request.headers.get('Accept-Language')
                if accept_lang:
                    browser_langs = accept_lang.split(',')
                    for lang_header in browser_langs:
                        lang_code = lang_header.split(';')[0].strip()[:2].lower()
                        if lang_code in self.supported_languages:
                            self.set_language(lang_code)
                            g._current_language = lang_code
                            return lang_code
            
            # 5. Default language
            g._current_language = self.default_language
            return self.default_language
            
        except Exception as e:
            print(f"DEBUG: Language detection error: {e}")
            return self.default_language
    
    def set_language(self, language: str) -> bool:
        """Set user's language preference - FINAL FIX"""
        if language in self.supported_languages:
            try:
                from flask import session, g
                
                # Set in session
                session['language'] = language
                session.permanent = True
                session.modified = True
                
                # CRITICAL: Also cache in Flask's g object for immediate use
                g._current_language = language
                
                print(f"DEBUG: Language set to {language}, session and g object updated")
                return True
            except Exception as e:
                print(f"DEBUG: Error setting language: {e}")
                return False
        return False
    
    def get_direction(self, language: Optional[str] = None) -> str:
        """Get text direction for given language"""
        if not language:
            language = self.get_current_language()
        
        rtl_languages = ['ar', 'he', 'fa', 'ur']
        return 'rtl' if language in rtl_languages else 'ltr'
    
    def translate(self, key: str, language: Optional[str] = None, force_lang: Optional[str] = None, **kwargs) -> str:
        """Translate a key to specified language with variable substitution"""
        # Use force_lang if provided, otherwise use language parameter or current language
        target_lang = force_lang or language or self.get_current_language()
        
        # Get translation from nested key (e.g., "navigation.surveys.create")
        keys = key.split('.')
        translation = self.translations.get(target_lang, {})
        
        for k in keys:
            if isinstance(translation, dict) and k in translation:
                translation = translation[k]
            else:
                # Fallback to other language if key not found
                fallback_lang = self.fallback_language if target_lang != self.fallback_language else self.default_language
                fallback_translation = self.translations.get(fallback_lang, {})
                
                for k in keys:
                    if isinstance(fallback_translation, dict) and k in fallback_translation:
                        fallback_translation = fallback_translation[k]
                    else:
                        # Return key if no translation found
                        return f"[{key}]"
                
                translation = fallback_translation
                break
        
        # Handle variable substitution
        if isinstance(translation, str) and kwargs:
            try:
                return translation.format(**kwargs)
            except KeyError:
                return translation
        
        return str(translation) if translation else f"[{key}]"
    
    def get_language_info(self, language: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive language information"""
        if not language:
            language = self.get_current_language()
        
        language_info = {
            'ar': {
                'code': 'ar',
                'name': 'العربية',
                'english_name': 'Arabic',
                'direction': 'rtl',
                'font_family': "'Cairo', 'Amiri', sans-serif"
            },
            'en': {
                'code': 'en',
                'name': 'English',
                'english_name': 'English',
                'direction': 'ltr',
                'font_family': "'Inter', 'Roboto', sans-serif"
            }
        }
        
        return language_info.get(language, language_info['ar'])
    
    def get_opposite_language(self, language: Optional[str] = None) -> str:
        """Get the opposite language for toggle functionality"""
        if not language:
            language = self.get_current_language()
        
        return 'en' if language == 'ar' else 'ar'
    
    def get_toggle_url(self, current_url: Optional[str] = None) -> str:
        """Generate URL for language toggle"""
        if not current_url and request:
            current_url = request.url
        
        current_lang = self.get_current_language()
        target_lang = self.get_opposite_language(current_lang)
        
        # Simple implementation - add/update lang parameter
        if current_url:
            separator = '&' if '?' in current_url else '?'
            # Remove existing lang parameter if present
            if 'lang=' in current_url:
                import re
                current_url = re.sub(r'[?&]lang=[^&]*', '', current_url)
            return f"{current_url}{separator}lang={target_lang}"
        
        return f"?lang={target_lang}"

# Global instance
language_manager = LanguageManager()

# Helper functions for Flask templates
def get_current_language():
    """Template helper: Get current language"""
    return language_manager.get_current_language()

def get_direction():
    """Template helper: Get text direction"""
    return language_manager.get_direction()

def translate_key(key: str, **kwargs):
    """Template helper: Translate a key"""
    return language_manager.translate(key, **kwargs)

def get_language_toggle_url():
    """Template helper: Get language toggle URL"""
    return language_manager.get_toggle_url()

def get_language_info():
    """Template helper: Get current language info"""
    return language_manager.get_language_info()