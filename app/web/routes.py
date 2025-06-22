"""
Web routes for Arabic VoC Platform
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.models.feedback import Feedback, FeedbackStatus
from app.main import db

bp = Blueprint('web', __name__)

@bp.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@bp.route('/feedback')
def feedback_page():
    """Feedback submission page"""
    return render_template('feedback.html')

@bp.route('/analytics')
def analytics_page():
    """Analytics dashboard"""
    return render_template('executive_dashboard.html')

@bp.route('/surveys')
def surveys_page():
    """Survey management page"""
    return render_template('surveys.html')

@bp.route('/survey-builder')
def survey_builder():
    """Survey builder interface"""
    return render_template('survey_builder.html')

@bp.route('/integrations')
def integrations_page():
    """Integrations management"""
    return redirect(url_for('web.integrations_sources'))

@bp.route('/integrations/sources')
def integrations_sources():
    """Data sources page"""
    return render_template('integrations_sources.html')

@bp.route('/integrations/destinations') 
def integrations_destinations():
    """Data destinations page"""
    return render_template('integrations_destinations.html')

@bp.route('/integrations/ai')
def integrations_ai():
    """AI management page"""
    return render_template('integrations_ai.html')

@bp.route('/settings')
def settings_page():
    """Settings overview"""
    return redirect(url_for('web.settings_account'))

@bp.route('/settings/account')
def settings_account():
    """Account settings"""
    return render_template('settings_account.html')

@bp.route('/settings/system')
def settings_system():
    """System settings"""
    return render_template('settings_system.html')

@bp.route('/settings/security')
def settings_security():
    """Security settings"""
    return render_template('settings_security.html')

@bp.route('/login')
def login():
    """Login page"""
    return render_template('login.html')

@bp.route('/register')
def register():
    """Registration page"""
    return render_template('register.html')