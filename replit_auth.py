import jwt
import os
import uuid
from datetime import datetime
from functools import wraps
from urllib.parse import urlencode

from flask import g, session, redirect, request, render_template, url_for
from flask_dance.consumer import (
    OAuth2ConsumerBlueprint,
    oauth_authorized,
    oauth_error,
)
from flask_dance.consumer.storage import BaseStorage
from flask_login import LoginManager, login_user, logout_user, current_user, UserMixin
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError
from sqlalchemy.exc import NoResultFound
from werkzeug.local import LocalProxy

# Defer imports to avoid circular dependency
def get_app_db():
    from app import app, db
    return app, db

# Get issuer URL for token refresh
issuer_url = os.environ.get('ISSUER_URL', "https://replit.com/oidc")

login_manager = LoginManager()

# Models cache to prevent redefinition during OAuth callbacks
_models_cache = {}

def get_auth_models():
    """Get auth models with proper caching to prevent redefinition issues"""
    if 'models' in _models_cache:
        return _models_cache['models']
    
    app, db = get_app_db()
    
    # Import the model creation function
    from models.auth_models import create_replit_auth_models
    
    # Create models once and cache them
    models = create_replit_auth_models(db)
    _models_cache['models'] = models
    
    return models

def init_login_manager(app):
    """Initialize login manager with app"""
    login_manager.init_app(app)
    
    # Set up user loader
    @login_manager.user_loader
    def load_user(user_id):
        ReplitUser, _ = get_auth_models()
        return ReplitUser.query.get(user_id)


class UserSessionStorage(BaseStorage):

    def get(self, blueprint):
        try:
            _, ReplitOAuth = get_auth_models()
            app, db = get_app_db()
            token = db.session.query(ReplitOAuth).filter_by(
                user_id=current_user.get_id(),
                browser_session_key=g.browser_session_key,
                provider=blueprint.name,
            ).one().token
        except NoResultFound:
            token = None
        return token

    def set(self, blueprint, token):
        _, ReplitOAuth = get_auth_models()
        app, db = get_app_db()
        db.session.query(ReplitOAuth).filter_by(
            user_id=current_user.get_id(),
            browser_session_key=g.browser_session_key,
            provider=blueprint.name,
        ).delete()
        new_model = ReplitOAuth()
        new_model.user_id = current_user.get_id()
        new_model.browser_session_key = g.browser_session_key
        new_model.provider = blueprint.name
        new_model.token = token
        db.session.add(new_model)
        db.session.commit()

    def delete(self, blueprint):
        _, ReplitOAuth = get_auth_models()
        app, db = get_app_db()
        db.session.query(ReplitOAuth).filter_by(
            user_id=current_user.get_id(),
            browser_session_key=g.browser_session_key,
            provider=blueprint.name).delete()
        db.session.commit()


def make_replit_blueprint():
    try:
        repl_id = os.environ['REPL_ID']
    except KeyError:
        raise SystemExit("the REPL_ID environment variable must be set")

    replit_bp = OAuth2ConsumerBlueprint(
        "replit_auth",
        __name__,
        client_id=repl_id,
        client_secret=None,
        base_url=issuer_url,
        authorization_url_params={
            "prompt": "login consent",
        },
        token_url=issuer_url + "/token",
        token_url_params={
            "auth": (),
            "include_client_id": True,
        },
        auto_refresh_url=issuer_url + "/token",
        auto_refresh_kwargs={
            "client_id": repl_id,
        },
        authorization_url=issuer_url + "/auth",
        use_pkce=True,
        code_challenge_method="S256",
        scope=["openid", "profile", "email", "offline_access"],
        storage=UserSessionStorage(),
    )

    @replit_bp.before_app_request
    def set_applocal_session():
        if '_browser_session_key' not in session:
            session['_browser_session_key'] = uuid.uuid4().hex
        session.modified = True
        g.browser_session_key = session['_browser_session_key']
        g.flask_dance_replit = replit_bp.session

    @replit_bp.route("/logout")
    def logout():
        del replit_bp.token
        logout_user()

        end_session_endpoint = issuer_url + "/session/end"
        encoded_params = urlencode({
            "client_id":
            repl_id,
            "post_logout_redirect_uri":
            request.url_root,
        })
        logout_url = f"{end_session_endpoint}?{encoded_params}"

        return redirect(logout_url)

    @replit_bp.route("/error")
    def error():
        return render_template("403.html"), 403

    return replit_bp


def save_user(user_claims):
    ReplitUser, _ = get_auth_models()
    app, db = get_app_db()
    
    import logging
    logger = logging.getLogger(__name__)
    
    user = ReplitUser.query.get(user_claims["sub"])
    if user:
        merged_user = db.session.merge(user)
    else:
        merged_user = ReplitUser()
        merged_user.id = user_claims["sub"]
    
    # Extract user information from OAuth claims
    # Replit may provide name information in different fields
    merged_user.first_name = (
        user_claims.get("given_name") or 
        user_claims.get("name", "").split()[0] if user_claims.get("name") else None
    )
    merged_user.last_name = (
        user_claims.get("family_name") or
        " ".join(user_claims.get("name", "").split()[1:]) if user_claims.get("name") and len(user_claims.get("name", "").split()) > 1 else None
    )
    merged_user.email = user_claims.get("email")
    merged_user.profile_image_url = user_claims.get("picture")
    
    # Log the user information being saved
    logger.info(f"Saving Replit user: {merged_user.first_name} {merged_user.last_name} ({merged_user.email})")
    
    db.session.add(merged_user)
    db.session.commit()
    return merged_user


@oauth_authorized.connect
def logged_in(blueprint, token):
    user_claims = jwt.decode(token['id_token'],
                             options={"verify_signature": False})
    
    # Debug logging to see what user information we receive from Replit
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Replit OAuth user claims: {user_claims}")
    
    user = save_user(user_claims)
    login_user(user)
    blueprint.token = token
    next_url = session.pop("next_url", None)
    if next_url is not None:
        return redirect(next_url)


@oauth_error.connect
def handle_error(blueprint, error, error_description=None, error_uri=None):
    return redirect(url_for('replit_auth.error'))


def require_login(f):
    """Decorator to require authentication for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            session['next_url'] = request.url
            return redirect(url_for('replit_auth.login'))
        
        # Token refresh logic
        app, db = get_app_db()
        try:
            repl_bp = LocalProxy(lambda: g.flask_dance_replit)
            if repl_bp.token and repl_bp.token.get('refresh_token'):
                # Check if access token needs refresh
                # This is handled automatically by Flask-Dance
                pass
        except (AttributeError, InvalidGrantError):
            # Token is invalid, redirect to login
            session['next_url'] = request.url
            return redirect(url_for('replit_auth.login'))
        
        return f(*args, **kwargs)
    return decorated_function