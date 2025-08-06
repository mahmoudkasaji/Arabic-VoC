"""
Lightweight Contact Management Models
Simple contact storage for survey distribution
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from core.app import db

class Contact(db.Model):
    """Contact model for survey distribution"""
    __tablename__ = 'contacts'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Optional additional fields
    company = Column(String(100), nullable=True)
    language_preference = Column(String(5), default='ar')  # 'ar' or 'en'
    tags = Column(JSON, default=list)  # List of tags for segmentation
    
    # Preferences
    email_opt_in = Column(Boolean, default=True)
    sms_opt_in = Column(Boolean, default=True)
    whatsapp_opt_in = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=True)  # References user ID without FK constraint
    
    # Status
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    deliveries = relationship("ContactDelivery", back_populates="contact", cascade="all, delete-orphan")
    
    def __repr__(self):
        email_or_phone = getattr(self, 'email', None) or getattr(self, 'phone', None)
        return f"<Contact {getattr(self, 'name', 'Unknown')} ({email_or_phone})>"
    
    def get_preferred_contact_method(self):
        """Get preferred contact method based on available data and preferences"""
        if getattr(self, 'email', None) and getattr(self, 'email_opt_in', False):
            return 'email'
        elif getattr(self, 'phone', None) and getattr(self, 'sms_opt_in', False):
            return 'sms'
        elif getattr(self, 'phone', None) and getattr(self, 'whatsapp_opt_in', False):
            return 'whatsapp'
        return None
    
    def get_available_channels(self):
        """Get list of available contact channels"""
        channels = []
        if getattr(self, 'email', None) and getattr(self, 'email_opt_in', False):
            channels.append('email')
        if getattr(self, 'phone', None) and getattr(self, 'sms_opt_in', False):
            channels.append('sms')
        if getattr(self, 'phone', None) and getattr(self, 'whatsapp_opt_in', False):
            channels.append('whatsapp')
        return channels
    
    def to_dict(self):
        """Convert contact to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'company': self.company,
            'language_preference': self.language_preference,
            'tags': self.tags or [],
            'email_opt_in': self.email_opt_in,
            'sms_opt_in': self.sms_opt_in,
            'whatsapp_opt_in': self.whatsapp_opt_in,
            'is_active': self.is_active,
            'preferred_contact_method': self.get_preferred_contact_method(),
            'available_channels': self.get_available_channels(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'notes': self.notes
        }

class ContactGroup(db.Model):
    """Contact groups for easier management"""
    __tablename__ = 'contact_groups'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, nullable=True)  # References user ID without FK constraint
    
    # Relationships
    memberships = relationship("ContactGroupMembership", back_populates="group", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ContactGroup {self.name}>"
    
    @property
    def contact_count(self):
        """Get number of contacts in this group"""
        return len(self.memberships)
    
    def to_dict(self):
        """Convert group to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'contact_count': self.contact_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ContactGroupMembership(db.Model):
    """Many-to-many relationship between contacts and groups"""
    __tablename__ = 'contact_group_memberships'
    
    id = Column(Integer, primary_key=True)
    contact_id = Column(Integer, ForeignKey('contacts.id'), nullable=False)
    group_id = Column(Integer, ForeignKey('contact_groups.id'), nullable=False)
    
    # Metadata
    added_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    contact = relationship("Contact")
    group = relationship("ContactGroup", back_populates="memberships")

class ContactDelivery(db.Model):
    """Track survey deliveries to contacts"""
    __tablename__ = 'contact_deliveries'
    
    id = Column(Integer, primary_key=True)
    contact_id = Column(Integer, ForeignKey('contacts.id'), nullable=False)
    survey_id = Column(Integer, nullable=False)  # Reference to survey
    
    # Delivery details
    channel = Column(String(20), nullable=False)  # email, sms, whatsapp
    recipient = Column(String(255), nullable=False)  # actual email/phone used
    message_template = Column(Text, nullable=True)
    
    # Status tracking
    status = Column(String(20), default='pending')  # pending, sent, delivered, failed, opened, clicked, responded
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    opened_at = Column(DateTime, nullable=True)
    clicked_at = Column(DateTime, nullable=True)
    responded_at = Column(DateTime, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # External tracking
    external_message_id = Column(String(255), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    contact = relationship("Contact", back_populates="deliveries")
    
    def __repr__(self):
        return f"<ContactDelivery {self.contact_id} via {self.channel} - {self.status}>"
    
    def to_dict(self):
        """Convert delivery to dictionary"""
        return {
            'id': self.id,
            'contact_id': self.contact_id,
            'survey_id': self.survey_id,
            'channel': self.channel,
            'recipient': self.recipient,
            'status': self.status,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'opened_at': self.opened_at.isoformat() if self.opened_at else None,
            'clicked_at': self.clicked_at.isoformat() if self.clicked_at else None,
            'responded_at': self.responded_at.isoformat() if self.responded_at else None,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }