"""
Authentication models for Replit OAuth integration
Separated to avoid circular imports and model redefinition issues
"""

from datetime import datetime
from flask_login import UserMixin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from sqlalchemy import UniqueConstraint

def create_replit_auth_models(db):
    """Create Replit authentication models with proper database reference"""
    
    class ReplitUser(UserMixin, db.Model):
        """Replit authenticated user model"""
        __tablename__ = 'replit_users'
        __table_args__ = {'extend_existing': True}
        
        id = db.Column(db.String, primary_key=True)  # Replit user ID
        email = db.Column(db.String, unique=True, nullable=True)
        first_name = db.Column(db.String, nullable=True)
        last_name = db.Column(db.String, nullable=True)
        profile_image_url = db.Column(db.String, nullable=True)
        created_at = db.Column(db.DateTime, default=datetime.now)
        updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    class ReplitOAuth(OAuthConsumerMixin, db.Model):
        """OAuth storage for Replit Auth"""
        __tablename__ = 'replit_oauth'
        __table_args__ = (
            UniqueConstraint(
                'user_id',
                'browser_session_key',
                'provider',
                name='uq_replit_user_browser_session_key_provider',
            ),
            {'extend_existing': True}
        )
        
        user_id = db.Column(db.String, db.ForeignKey('replit_users.id'))
        browser_session_key = db.Column(db.String, nullable=False)
        user = db.relationship('ReplitUser')
    
    return ReplitUser, ReplitOAuth