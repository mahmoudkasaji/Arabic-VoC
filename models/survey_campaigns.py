"""
Survey Campaign Models for Distribution System
Direct database integration with Flask routes
"""

from app import db
from datetime import datetime
import json

class SurveyCampaign(db.Model):
    __tablename__ = 'survey_campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys_flask.id'))
    created_by = db.Column(db.String(255))  # User email from Replit Auth
    status = db.Column(db.String(50), default='draft')  # draft, active, paused, completed
    total_contacts = db.Column(db.Integer, default=0)
    sent_count = db.Column(db.Integer, default=0)
    response_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    scheduled_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    description = db.Column(db.Text)
    
    # Relationships
    survey = db.relationship('SurveyFlask', backref='campaigns')
    distribution_methods = db.relationship('DistributionMethod', backref='campaign', cascade='all, delete-orphan')
    
    @property
    def response_rate(self):
        """Calculate response rate percentage"""
        if self.sent_count == 0:
            return 0
        return round((self.response_count / self.sent_count) * 100, 1)
    
    @property
    def status_badge_class(self):
        """CSS class for status badge"""
        status_classes = {
            'draft': 'badge-secondary',
            'active': 'badge-primary',
            'paused': 'badge-warning',
            'completed': 'badge-success'
        }
        return status_classes.get(self.status, 'badge-secondary')
    
    def to_dict(self):
        """Convert to dictionary for JSON responses"""
        return {
            'id': self.id,
            'name': self.name,
            'survey_id': self.survey_id,
            'survey_title': self.survey.display_title if self.survey else None,
            'status': self.status,
            'total_contacts': self.total_contacts,
            'sent_count': self.sent_count,
            'response_count': self.response_count,
            'response_rate': self.response_rate,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None
        }


class DistributionMethod(db.Model):
    __tablename__ = 'distribution_methods'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('survey_campaigns.id'))
    method_type = db.Column(db.String(50), nullable=False)  # email, sms, whatsapp, qr_code, embed_widget
    target_audience = db.Column(db.JSON)  # contact_groups, individual_contacts
    message_template = db.Column(db.Text)
    delivery_schedule = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='pending')  # pending, sending, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def method_display_name(self):
        """Human-readable method names"""
        method_names = {
            'email': 'البريد الإلكتروني',
            'sms': 'الرسائل النصية',
            'whatsapp': 'واتساب',
            'qr_code': 'رمز QR',
            'embed_widget': 'ويدجت مدمج'
        }
        return method_names.get(self.method_type, self.method_type)
    
    @property
    def method_icon(self):
        """Font Awesome icons for methods"""
        method_icons = {
            'email': 'fas fa-envelope',
            'sms': 'fas fa-sms',
            'whatsapp': 'fab fa-whatsapp',
            'qr_code': 'fas fa-qrcode',
            'embed_widget': 'fas fa-code'
        }
        return method_icons.get(self.method_type, 'fas fa-share')
    
    def to_dict(self):
        """Convert to dictionary for JSON responses"""
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'method_type': self.method_type,
            'method_display_name': self.method_display_name,
            'method_icon': self.method_icon,
            'target_audience': self.target_audience,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }