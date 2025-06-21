
from flask import session, render_template, redirect, url_for, request, jsonify
from flask_login import current_user

def setup_routes(app):
    """Setup all routes for the application"""
    from main import db
    from replit_auth import init_auth
    
    # Initialize authentication
    replit_bp, require_login, replit = init_auth(app, db)

    # Make session permanent
    @app.before_request
    def make_session_permanent():
        session.permanent = True

    @app.route('/')
    def index():
        """Main page - show different content based on auth status"""
        if current_user.is_authenticated:
            return render_template('index.html', user=current_user)
        else:
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

    # API endpoints
    @app.route('/api/feedback', methods=['POST'])
    def submit_feedback():
        """Submit feedback - no authentication required"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            content = data.get('content', '').strip()
            if not content:
                return jsonify({'error': 'Content is required'}), 400
            
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

    # Health check
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({'status': 'healthy', 'message': 'Arabic VoC Platform is running'})

    return app
