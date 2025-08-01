"""
API endpoints for Replit user preferences management
"""

from flask import jsonify, request
from flask_login import current_user, login_required
from app import app, db
from models.replit_user_preferences import ReplitUserPreferences


@app.route('/api/user/preferences', methods=['POST'])
@login_required
def update_preferences():
    """Update user preferences"""
    try:
        data = request.get_json()
        
        # Get or create user preferences
        preferences = ReplitUserPreferences.get_or_create(current_user.id)
        
        # Update preferences
        if 'language_preference' in data:
            preferences.language_preference = data['language_preference']
        if 'timezone' in data:
            preferences.timezone = data['timezone']
        if 'theme' in data:
            preferences.theme = data['theme']
        if 'dashboard_layout' in data:
            preferences.dashboard_layout = data['dashboard_layout']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Preferences updated successfully'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/admin/toggle-admin-status', methods=['POST'])
@login_required
def toggle_admin_status():
    """Toggle admin status for a user (admin only)"""
    try:
        # Check if current user is admin
        current_prefs = ReplitUserPreferences.get_or_create(current_user.id)
        if not current_prefs.is_admin:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        data = request.get_json()
        user_id = data.get('user_id')
        is_admin = data.get('is_admin', False)
        
        # Get target user preferences
        target_prefs = ReplitUserPreferences.get_or_create(user_id)
        target_prefs.is_admin = is_admin
        
        if is_admin and target_prefs.admin_level == 'user':
            target_prefs.admin_level = 'admin'
        elif not is_admin:
            target_prefs.admin_level = 'user'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Admin status updated successfully'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/admin/change-role', methods=['POST'])
@login_required
def change_user_role():
    """Change user role (admin only)"""
    try:
        # Check if current user is admin
        current_prefs = ReplitUserPreferences.get_or_create(current_user.id)
        if not current_prefs.is_admin:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        data = request.get_json()
        user_id = data.get('user_id')
        new_role = data.get('role')
        
        if new_role not in ['user', 'analyst', 'admin', 'super_admin']:
            return jsonify({'success': False, 'message': 'Invalid role'}), 400
        
        # Get target user preferences
        target_prefs = ReplitUserPreferences.get_or_create(user_id)
        target_prefs.admin_level = new_role
        target_prefs.is_admin = new_role in ['admin', 'super_admin']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Role updated successfully'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500