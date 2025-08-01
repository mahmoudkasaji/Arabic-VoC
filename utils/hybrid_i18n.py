"""
Hybrid Internationalization System
Combines Flask-Babel backend with JavaScript frontend for instant language switching
"""

from flask import Flask, request, session, g, jsonify
import json
import os

class HybridI18N:
    def __init__(self, app=None):
        self.app = None
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the hybrid i18n system with Flask app"""
        self.app = app
        
        # Configure supported languages
        app.config.setdefault('LANGUAGES', {
            'ar': 'العربية',
            'en': 'English'
        })
        app.config.setdefault('BABEL_DEFAULT_LOCALE', 'ar')
        app.config.setdefault('BABEL_DEFAULT_TIMEZONE', 'UTC')
        
        # Enhanced i18n without Flask-Babel dependency
        # Uses existing translation system but adds API layer
        
        # Register context processor
        app.context_processor(self.inject_i18n_vars)
        
        # Register API routes for frontend
        self.register_api_routes()
    
    def get_locale(self):
        """Determine user's preferred language"""
        # 1. Check session (highest priority)
        if 'language' in session and session['language'] in self.app.config['LANGUAGES']:
            return session['language']
        
        # 2. Check URL parameter
        if request and request.args.get('lang') in self.app.config['LANGUAGES']:
            return request.args.get('lang')
            
        # 3. Check browser preferences
        if request:
            return request.accept_languages.best_match(
                self.app.config['LANGUAGES'].keys()
            ) or self.app.config['BABEL_DEFAULT_LOCALE']
        
        return self.app.config['BABEL_DEFAULT_LOCALE']
    
    def inject_i18n_vars(self):
        """Inject i18n variables into all templates"""
        current_lang = self.get_locale()
        return {
            'LANGUAGES': self.app.config['LANGUAGES'],
            'CURRENT_LANGUAGE': current_lang,
            'LANGUAGE_DIRECTION': 'rtl' if current_lang == 'ar' else 'ltr',
            'get_locale': lambda: current_lang,
            'get_direction': lambda: 'rtl' if current_lang == 'ar' else 'ltr'
        }
    
    def register_api_routes(self):
        """Register API routes for frontend integration"""
        
        @self.app.route('/api/i18n/switch/<language>', methods=['POST'])
        def switch_language_api(language):
            """API endpoint for language switching"""
            if language in self.app.config['LANGUAGES']:
                session['language'] = language
                session.permanent = True
                return jsonify({
                    'success': True,
                    'language': language,
                    'direction': 'rtl' if language == 'ar' else 'ltr',
                    'translations': self.get_frontend_translations(language)
                })
            return jsonify({'success': False, 'error': 'Unsupported language'}), 400
        
        @self.app.route('/api/i18n/translations/<language>')
        def get_translations_api(language):
            """Get translations for frontend JavaScript"""
            if language in self.app.config['LANGUAGES']:
                return jsonify({
                    'language': language,
                    'translations': self.get_frontend_translations(language)
                })
            return jsonify({'error': 'Unsupported language'}), 400
        
        @self.app.route('/api/i18n/status')
        def get_i18n_status():
            """Get current i18n status"""
            current_lang = self.get_locale()
            return jsonify({
                'current_language': current_lang,
                'direction': 'rtl' if current_lang == 'ar' else 'ltr',
                'available_languages': self.app.config['LANGUAGES'],
                'translations': self.get_frontend_translations(current_lang)
            })
    
    def get_frontend_translations(self, language):
        """Get translations formatted for frontend JavaScript"""
        # Load translations from our existing JSON files
        translation_file = f'translations/{language}.json'
        if os.path.exists(translation_file):
            with open(translation_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def set_language(self, language):
        """Set user's language preference"""
        if language in self.app.config['LANGUAGES']:
            session['language'] = language
            session.permanent = True
            return True
        return False

# Global instance
hybrid_i18n = HybridI18N()