"""
Replit User Preferences Model
Stores platform-specific preferences for Replit authenticated users
"""

from app import db
from datetime import datetime


class ReplitUserPreferences(db.Model):
    """Platform preferences for Replit authenticated users"""
    __tablename__ = 'replit_user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('replit_users.id'), unique=True, nullable=False)
    
    # Language and localization
    language_preference = db.Column(db.String(10), default='ar')  # ar, en
    timezone = db.Column(db.String(50), default='Asia/Riyadh')
    
    # Platform-specific preferences
    theme = db.Column(db.String(20), default='light')  # light, dark
    dashboard_layout = db.Column(db.String(20), default='standard')  # standard, compact
    
    # Admin designation
    is_admin = db.Column(db.Boolean, default=False)
    admin_level = db.Column(db.String(20), default='user')  # user, analyst, admin, super_admin
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationship back to user
    user = db.relationship('ReplitUser', backref='preferences')
    
    def __repr__(self):
        return f'<ReplitUserPreferences {self.user_id}>'
    
    @classmethod
    def get_or_create(cls, user_id):
        """Get existing preferences or create default ones"""
        prefs = cls.query.filter_by(user_id=user_id).first()
        if not prefs:
            prefs = cls(user_id=user_id)
            db.session.add(prefs)
            db.session.commit()
        return prefs