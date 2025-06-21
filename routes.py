
from flask import session, render_template, redirect, url_for, request, jsonify
from main import app, db
from replit_auth import require_login, make_replit_blueprint, replit
from flask_login import current_user
import json

app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/')
def index():
    """Main page - show different content based on auth status"""
    if current_user.is_authenticated:
        # Logged in users see the main dashboard
        return render_template('index.html', user=current_user)
    else:
        # Logged out users see landing page
        return render_template('landing.html')

@app.route('/feedback')
def feedback_page():
    """Feedback page - accessible to all users"""
    return render_template('feedback.html', user=current_user if current_user.is_authenticated else None)

@app.route('/dashboard/realtime')
@require_login
def dashboard():
    """Protected dashboard - requires login"""
    return render_template('dashboard_realtime.html', user=current_user)

@app.route('/surveys')
@require_login  
def surveys():
    """Protected surveys page - requires login"""
    return render_template('surveys.html', user=current_user)

@app.route('/analytics')
@require_login
def analytics():
    """Protected analytics page - requires login"""
    return render_template('analytics.html', user=current_user)

# API endpoints for feedback (no auth required)
@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit feedback - no authentication required"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Basic validation
        content = data.get('content', '').strip()
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        # For now, just return success (you can add database storage later)
        feedback_data = {
            'content': content,
            'rating': data.get('rating'),
            'name': data.get('name', 'Anonymous'),
            'timestamp': 'now'
        }
        
        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully',
            'data': feedback_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API endpoint for user info (authenticated)
@app.route('/api/user', methods=['GET'])
@require_login
def get_user_info():
    """Get current user information"""
    if current_user.is_authenticated:
        user_data = {
            'id': current_user.id,
            'email': current_user.email,
            'first_name': current_user.first_name,
            'last_name': current_user.last_name,
            'profile_image_url': current_user.profile_image_url
        }
        return jsonify(user_data)
    else:
        return jsonify({'error': 'Not authenticated'}), 401

# Legacy routes for compatibility - redirect to Replit auth
@app.route('/login')
def login_redirect():
    """Redirect to Replit auth login"""
    return redirect(url_for('replit_auth.login'))

@app.route('/register') 
def register_redirect():
    """Redirect to Replit auth (no separate registration needed)"""
    return redirect(url_for('replit_auth.login'))

# Health check
@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Arabic VoC Platform is running with Replit Auth'})
