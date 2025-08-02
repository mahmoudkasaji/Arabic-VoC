"""
Template Helper Functions for Internationalization
Jinja2 filters and functions for language support
"""

from flask import request, url_for
from .language_manager import language_manager

def register_template_helpers(app):
    """Register all template helper functions with Flask app"""
    
    @app.template_filter('translate')
    def translate_filter(key, **kwargs):
        """Jinja2 filter for translating keys - FIXED VERSION
        Usage: {{ 'navigation.surveys' | translate }}
        Usage with variables: {{ 'messages.welcome' | translate(name=user.name) }}
        """
        try:
            # Debug: Force reload translations
            language_manager._load_translations()
            
            # Get current language directly
            current_lang = language_manager.get_current_language()
            
            # Direct translation without hybrid wrapper
            result = language_manager.translate(key, **kwargs)
            
            # Fallback if translation failed
            if result == f"[{key}]" or result is None:
                # Try with explicit language
                result = language_manager.translate(key, force_lang=current_lang, **kwargs)
            
            return result
        except Exception as e:
            print(f"Translation filter error for key '{key}': {e}")
            import traceback
            traceback.print_exc()
            return f"[{key}]"
    
    @app.template_global()
    def get_lang():
        """Template global: Get current language code"""
        return language_manager.get_current_language()
    
    @app.template_global()
    def get_dir():
        """Template global: Get text direction (rtl/ltr)"""
        return language_manager.get_direction()
    
    @app.template_global()
    def get_language_info():
        """Template global: Get comprehensive language info"""
        return language_manager.get_language_info()
    
    @app.template_global()
    def get_opposite_lang():
        """Template global: Get opposite language for toggle"""
        return language_manager.get_opposite_language()
    
    @app.template_global()
    def get_language_toggle_url():
        """Template global: Get URL for language toggle"""
        return language_manager.get_toggle_url()
    
    @app.template_global()
    def get_localized_url(endpoint, **values):
        """Template global: Get URL with current language parameter"""
        current_lang = language_manager.get_current_language()
        if current_lang != language_manager.default_language:
            values['lang'] = current_lang
        return url_for(endpoint, **values)
    
    @app.template_filter('lang_class')
    def language_class_filter(base_class=''):
        """Template filter: Add language-specific CSS classes
        Usage: {{ 'text-center' | lang_class }}
        """
        current_lang = language_manager.get_current_language()
        direction = language_manager.get_direction()
        
        classes = [base_class] if base_class else []
        classes.extend([f'lang-{current_lang}', f'dir-{direction}'])
        
        return ' '.join(filter(None, classes))
    
    @app.template_filter('font_family')
    def font_family_filter():
        """Template filter: Get appropriate font family for current language"""
        lang_info = language_manager.get_language_info()
        return lang_info.get('font_family', "'Inter', sans-serif")
    
    @app.template_global()
    def translate_choices(choices_dict):
        """Template global: Translate a dictionary of choices
        Usage: {{ translate_choices({'option1': 'translation.key1', 'option2': 'translation.key2'}) }}
        """
        return {
            key: language_manager.translate(value) 
            for key, value in choices_dict.items()
        }
    
    @app.context_processor
    def inject_language_context():
        """Inject language context into all templates"""
        return {
            'current_language': language_manager.get_current_language(),
            'text_direction': language_manager.get_direction(),
            'language_info': language_manager.get_language_info(),
            'opposite_language': language_manager.get_opposite_language(),
            'toggle_url': language_manager.get_toggle_url(),
            'supported_languages': language_manager.supported_languages
        }
    
    # Alternative simpler translate function for debugging
    @app.template_global()
    def translate(key, **kwargs):
        """Template global function for translation (alternative to filter)"""
        return language_manager.translate(key, **kwargs)

# Utility functions for use in Python code
def get_translated_message(key, language=None, **kwargs):
    """Get translated message for use in Python code (API responses, etc.)"""
    return language_manager.translate(key, language=language, **kwargs)

def get_error_message(error_type, language=None, **kwargs):
    """Get translated error message"""
    return get_translated_message(f'messages.errors.{error_type}', language=language, **kwargs)

def get_success_message(success_type, language=None, **kwargs):
    """Get translated success message"""
    return get_translated_message(f'messages.success.{success_type}', language=language, **kwargs)

# Language-aware URL helpers
def url_for_language(endpoint, language=None, **values):
    """Generate URL with specific language parameter"""
    if language and language != language_manager.default_language:
        values['lang'] = language
    return url_for(endpoint, **values)

def redirect_with_language(endpoint, language=None, **values):
    """Redirect to endpoint with language parameter"""
    from flask import redirect
    return redirect(url_for_language(endpoint, language=language, **values))