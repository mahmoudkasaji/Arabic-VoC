"""
Feedback database models with Arabic support
"""

import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class FeedbackChannel(str, enum.Enum):
    """Channels through which feedback can be received"""
    EMAIL = "email"
    PHONE = "phone"
    WEBSITE = "website"
    MOBILE_APP = "mobile_app"
    SOCIAL_MEDIA = "social_media"
    WHATSAPP = "whatsapp"
    SMS = "sms"
    IN_PERSON = "in_person"
    SURVEY = "survey"
    CHATBOT = "chatbot"

class FeedbackStatus(str, enum.Enum):
    """Processing status of feedback"""
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    ARCHIVED = "archived"

class Feedback(Base):
    """
    Main feedback model with Arabic text support
    Stores customer feedback from multiple channels
    """
    __tablename__ = "feedback"
    
    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    
    # Content (supporting Arabic UTF-8)
    content = Column(Text, nullable=False, comment="Original feedback content in Arabic")
    processed_content = Column(Text, nullable=True, comment="Processed Arabic text (reshaped, normalized)")
    
    # Channel and metadata
    channel = Column(Enum(FeedbackChannel), nullable=False, index=True)
    status = Column(Enum(FeedbackStatus), default=FeedbackStatus.PENDING, index=True)
    
    # Customer information (optional)
    customer_email = Column(String(255), nullable=True)
    customer_phone = Column(String(50), nullable=True)
    customer_id = Column(String(100), nullable=True, index=True)
    
    # Ratings and scores
    rating = Column(Integer, nullable=True, comment="Customer rating 1-5")
    sentiment_score = Column(Float, nullable=True, comment="AI sentiment score -1 to 1")
    confidence_score = Column(Float, nullable=True, comment="AI confidence score 0 to 1")
    
    # AI Analysis results
    ai_summary = Column(Text, nullable=True, comment="AI-generated summary in Arabic")
    ai_categories = Column(JSON, nullable=True, comment="AI-detected categories and topics")
    ai_action_items = Column(JSON, nullable=True, comment="AI-suggested action items")
    
    # Additional metadata
    metadata = Column(JSON, nullable=True, comment="Additional channel-specific metadata")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # Geographic and language info
    language_detected = Column(String(10), default="ar", comment="Detected language code")
    region = Column(String(10), nullable=True, comment="Geographic region code")
    
    def __repr__(self):
        return f"<Feedback(id={self.id}, channel={self.channel}, status={self.status})>"
    
    @property
    def is_processed(self):
        """Check if feedback has been processed"""
        return self.status == FeedbackStatus.PROCESSED
    
    @property
    def sentiment_category(self):
        """Get sentiment category based on score"""
        if self.sentiment_score is None:
            return "unknown"
        elif self.sentiment_score > 0.1:
            return "positive"
        elif self.sentiment_score < -0.1:
            return "negative"
        else:
            return "neutral"
