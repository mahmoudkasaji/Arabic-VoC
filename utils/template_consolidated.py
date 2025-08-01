"""
Consolidated Template Utilities
Combines functionality from template_helpers.py and template_filters.py
"""

from flask import session, request
from typing import Dict, Any, Optional, Union
import json
import logging

logger = logging.getLogger(__name__)

class TemplateManager:
    """Unified template management with Arabic and bilingual support"""
    
    def __init__(self):
        # Translation dictionaries
        self.translations = {
            'ar': {
                'feedback_submitted': 'تم إرسال التعليق بنجاح',
                'general_error': 'حدث خطأ، يرجى المحاولة مرة أخرى',
                'success': 'نجح',
                'error': 'خطأ',
                'save': 'حفظ',
                'cancel': 'إلغاء',
                'delete': 'حذف',
                'edit': 'تحرير',
                'create': 'إنشاء',
                'update': 'تحديث'
            },
            'en': {
                'feedback_submitted': 'Feedback submitted successfully',
                'general_error': 'An error occurred, please try again',
                'success': 'Success',
                'error': 'Error',
                'save': 'Save',
                'cancel': 'Cancel',
                'delete': 'Delete',
                'edit': 'Edit',
                'create': 'Create',
                'update': 'Update'
            }
        }
    
    def get_current_language(self) -> str:
        """Get current language from session or default"""
        return session.get('language', 'ar')
    
    def set_language(self, lang: str) -> None:
        """Set current language in session"""
        if lang in ['ar', en']:
            session['language'] = lang
    
    def get_message(self, key: str, lang: Optional[str] = None) -> str:
        """Get translated message"""
        if lang is None:
            lang = self.get_current_language()
        
        return self.translations.get(lang, {}).get(key, key)
    
    def get_success_message(self, key: str) -> str:
        """Get success message in current language"""
        return self.get_message(key)
    
    def get_error_message(self, key: str) -> str:
        """Get error message in current language"""
        return self.get_message(key)
    
    def format_currency(self, amount: float, currency: str = 'SAR') -> str:
        """Format currency for Arabic/English display"""
        lang = self.get_current_language()
        
        if lang == 'ar':
            return f"{amount:,.2f} {currency}"
        else:
            return f"{currency} {amount:,.2f}"
    
    def format_date(self, date, format_type: str = 'short') -> str:
        """Format date for current language"""
        if not date:
            return ""
        
        lang = self.get_current_language()
        
        if format_type == 'short':
            if lang == 'ar':
                return date.strftime('%d/%m/%Y')
            else:
                return date.strftime('%m/%d/%Y')
        else:
            if lang == 'ar':
                return date.strftime('%d %B %Y')
            else:
                return date.strftime('%B %d, %Y')
    
    def get_text_direction(self) -> str:
        """Get text direction for current language"""
        return 'rtl' if self.get_current_language() == 'ar' else 'ltr'
    
    def get_text_align(self) -> str:
        """Get text alignment for current language"""
        return 'text-end' if self.get_current_language() == 'ar' else 'text-start'

# Template filters for Jinja2
def register_filters(app):
    """Register template filters with Flask app"""
    template_manager = TemplateManager()
    
    @app.template_filter('translate')
    def translate_filter(key, lang=None):
        return template_manager.get_message(key, lang)
    
    @app.template_filter('currency')
    def currency_filter(amount, currency='SAR'):
        return template_manager.format_currency(amount, currency)
    
    @app.template_filter('arabic_date')
    def arabic_date_filter(date, format_type='short'):
        return template_manager.format_date(date, format_type)

# Template context processors
def register_context_processors(app):
    """Register template context processors"""
    template_manager = TemplateManager()
    
    @app.context_processor
    def inject_language_helpers():
        return {
            'current_language': template_manager.get_current_language(),
            'text_direction': template_manager.get_text_direction(),
            'text_align': template_manager.get_text_align(),
            'get_message': template_manager.get_message
        }

# Singleton instance
template_manager = TemplateManager()