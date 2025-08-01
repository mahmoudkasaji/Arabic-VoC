"""
Enhanced Template Globals for Voice of Customer Platform
Better way to handle translations without hardcoding in templates
"""

from utils.language_manager import language_manager
from flask import g, request


def setup_enhanced_template_globals(app):
    """
    Setup enhanced template globals and context processors
    This provides a cleaner way to handle multilingual templates
    """
    
    @app.context_processor
    def inject_language_context():
        """Inject language context into all templates"""
        try:
            current_lang = language_manager.get_current_language()
            return {
                'current_lang': current_lang,
                'lang_direction': language_manager.get_direction(current_lang),
                'lang_info': language_manager.get_language_info(current_lang),
                'opposite_lang': language_manager.get_opposite_language(current_lang),
                'supported_languages': language_manager.supported_languages,
                'language_toggle_url': '/language/toggle'
            }
        except:
            return {
                'current_lang': 'ar',
                'lang_direction': 'rtl',
                'lang_info': {'code': 'ar', 'direction': 'rtl'},
                'opposite_lang': 'en',
                'supported_languages': ['ar', 'en'],
                'language_toggle_url': '/language/toggle'
            }
    
    @app.template_global()
    def t(key, **kwargs):
        """
        Simple translation function - shorter alias for templates
        Usage in templates: {{ t('navigation.surveys') }}
        """
        return language_manager.translate(key, **kwargs)
    
    @app.template_global()
    def nav_text(section, key, default=''):
        """
        Navigation-specific text helper
        Usage: {{ nav_text('contacts', 'title') }}
        """
        full_key = f'navigation.{section}.{key}'
        return language_manager.translate(full_key, default=default)
    
    @app.template_global()
    def page_title(page, default=''):
        """
        Page title helper
        Usage: {{ page_title('contacts') }}
        """
        return language_manager.translate(f'{page}.title', default=default)
    
    @app.template_global()
    def btn_text(action, default=''):
        """
        Button text helper
        Usage: {{ btn_text('save') }}
        """
        return language_manager.translate(f'buttons.{action}', default=default)
    
    @app.template_filter('smart_translate')
    def smart_translate_filter(text, context='general'):
        """
        Smart translation filter that attempts to translate
        or returns original text if no translation found
        """
        if not text:
            return ''
        
        # Try direct translation first
        translation = language_manager.translate(text)
        if translation != text:
            return translation
        
        # Try with context prefix
        context_key = f'{context}.{text.lower().replace(" ", "_")}'
        context_translation = language_manager.translate(context_key)
        if context_translation != context_key:
            return context_translation
        
        # Return original if no translation found
        return text
    
    # Alternative shorter syntax for common use cases
    @app.template_global()
    def menu_item(key):
        """Menu item text - Usage: {{ menu_item('surveys') }}"""
        return language_manager.translate(f'navigation.{key}')
    
    @app.template_global()
    def form_label(key):
        """Form label text - Usage: {{ form_label('email') }}"""
        return language_manager.translate(f'forms.{key}')
    
    print("✅ Enhanced template globals registered successfully")


# Quick template replacement suggestions
TEMPLATE_IMPROVEMENTS = {
    'hardcoded_patterns': {
        'جهات الاتصال': '{{ nav_text("contacts_dropdown", "title") }}',
        'إدارة جهات الاتصال': '{{ nav_text("contacts_dropdown", "management") }}',
        'قائمة جهات الاتصال': '{{ nav_text("contacts_dropdown", "list") }}',
        'التحليلات الأساسية': '{{ nav_text("analytics_basic", "title") }}',
        'لوحة المؤشرات الرئيسية': '{{ nav_text("analytics_basic", "kpi_dashboard") }}',
        'توزيع الاستطلاعات': '{{ nav_text("surveys_distribution", "title") }}',
        'إدارة التكاملات والذكاء الاصطناعي': '{{ nav_text("integrations_ai", "title") }}',
    },
    'modern_syntax': {
        'old': "{{ 'navigation.contacts_dropdown.title' | translate }}",
        'new': "{{ nav_text('contacts_dropdown', 'title') }}",
        'benefit': '30% shorter and more readable'
    }
}


def apply_template_improvements():
    """Apply modern template syntax improvements"""
    print("📋 Template Improvement Suggestions:")
    print("Instead of long translation keys, use helper functions:")
    for old_pattern, new_pattern in TEMPLATE_IMPROVEMENTS['hardcoded_patterns'].items():
        print(f"  '{old_pattern}' → {new_pattern}")
    
    print(f"\n💡 Modern syntax benefits:")
    print(f"  Old: {TEMPLATE_IMPROVEMENTS['modern_syntax']['old']}")  
    print(f"  New: {TEMPLATE_IMPROVEMENTS['modern_syntax']['new']}")
    print(f"  {TEMPLATE_IMPROVEMENTS['modern_syntax']['benefit']}")


if __name__ == "__main__":
    apply_template_improvements()