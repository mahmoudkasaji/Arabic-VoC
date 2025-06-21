from flask import session, render_template, redirect, url_for
from app import app, db
from replit_auth import require_login, make_replit_blueprint
from flask_login import current_user

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

# Legacy routes for compatibility
@app.route('/login')
def login_redirect():
    """Redirect to Replit auth login"""
    return redirect(url_for('replit_auth.login'))

@app.route('/register') 
def register_redirect():
    """Redirect to Replit auth (no separate registration needed)"""
    return redirect(url_for('replit_auth.login'))