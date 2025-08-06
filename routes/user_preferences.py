"""
User Preferences Routes
Handles user preference management and settings
"""

from flask import jsonify, request
from flask_login import current_user
from app import app, db
from replit_auth import require_login
from models.replit_user_preferences import ReplitUserPreferences
import logging

logger = logging.getLogger(__name__)


@app.route('/user/preferences', methods=['GET'])
@require_login
def get_user_preferences():
    """Get user preferences as JSON"""
    try:
        preferences = ReplitUserPreferences.get_or_create(current_user.id)
        return jsonify({
            'success': True,
            'preferences': {
                'language': preferences.language,
                'theme': preferences.theme,
                'dashboard_layout': preferences.dashboard_layout,
                'notifications_enabled': preferences.notifications_enabled,
                'email_notifications': preferences.email_notifications,
                'sms_notifications': preferences.sms_notifications
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting user preferences: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/user/preferences', methods=['POST'])
@require_login
def update_user_preferences():
    """Update user preferences"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        preferences = ReplitUserPreferences.get_or_create(current_user.id)
        
        # Update preferences with provided data
        if 'language' in data:
            preferences.language = data['language']
        if 'theme' in data:
            preferences.theme = data['theme']
        if 'dashboard_layout' in data:
            preferences.dashboard_layout = data['dashboard_layout']
        if 'notifications_enabled' in data:
            preferences.notifications_enabled = data['notifications_enabled']
        if 'email_notifications' in data:
            preferences.email_notifications = data['email_notifications']
        if 'sms_notifications' in data:
            preferences.sms_notifications = data['sms_notifications']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Preferences updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating user preferences: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500