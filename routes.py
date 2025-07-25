from flask import session
from app import app, db
from flask_login import current_user
try:
    from replit_auth import require_login
except ImportError:
    # Fallback decorator if Replit Auth is not available
    def require_login(f):
        return f

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/')
def example_index():
    # Use flask_login.current_user to check if current user is logged in or anonymous.
    user = current_user
    if user.is_authenticated:
        # User is logged in, show dashboard/home
        from flask import render_template
        return render_template('index_simple.html')
    else:
        # User is not logged in, show landing page
        from flask import render_template
        return render_template('index_simple.html')

@app.route('/example_protected_route')
@require_login # protected by Replit Auth
def example_protected_route():
    user = current_user
    # Access user properties: user.id, user.email, user.first_name, etc.
    return f"Hello {user.first_name or 'User'}! Your email is {user.email}"

# Gmail Test Route
@app.route('/gmail-test')
def gmail_test():
    from flask import render_template
    return render_template('gmail_test.html')

# Add any other routes here.
# Use flask_login.current_user to check if current user is logged in or anonymous.
# Use db & models to interact with the database.