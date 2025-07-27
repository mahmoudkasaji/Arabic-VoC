"""
Unified database models for Arabic Voice of Customer platform
Single source of truth for all database models
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
    WIDGET = "widget"
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
    """
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False, comment="Original feedback content in Arabic")
    processed_content = Column(Text, nullable=True, comment="Processed Arabic text")
    channel = Column(Enum(FeedbackChannel), nullable=False, index=True)
    status = Column(Enum(FeedbackStatus), default=FeedbackStatus.PENDING, index=True)
    customer_email = Column(String(255), nullable=True)
    customer_phone = Column(String(50), nullable=True)
    customer_id = Column(String(100), nullable=True, index=True)
    rating = Column(Integer, nullable=True, comment="Customer rating 1-5")
    sentiment_score = Column(Float, nullable=True, comment="AI sentiment score -1 to 1")
    confidence_score = Column(Float, nullable=True, comment="AI confidence score 0 to 1")
    ai_summary = Column(Text, nullable=True, comment="AI-generated summary in Arabic")
    ai_categories = Column(JSON, nullable=True, comment="AI-detected categories")
    ai_action_items = Column(JSON, nullable=True, comment="AI-suggested actions")
    channel_metadata = Column(JSON, nullable=True, comment="Channel metadata")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    language_detected = Column(String(10), default="ar", comment="Detected language")
    region = Column(String(10), nullable=True, comment="Geographic region")
    
    def __repr__(self):
        return f"<Feedback(id={self.id}, channel={self.channel}, status={self.status})>"
    
    def is_processed(self):
        return self.status == FeedbackStatus.PROCESSED
    
    def sentiment_category(self):
        if self.sentiment_score is None:
            return "غير محدد"
        elif self.sentiment_score > 0.3:
            return "إيجابي"
        elif self.sentiment_score < -0.3:
            return "سلبي"
        else:
            return "محايد"

class AggregationPeriod(str, enum.Enum):
    """Time periods for data aggregation"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class FeedbackAggregation(Base):
    """Aggregated feedback metrics"""
    __tablename__ = "feedback_aggregation"
    
    id = Column(Integer, primary_key=True, index=True)
    period = Column(Enum(AggregationPeriod), nullable=False, index=True)
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False)
    channel = Column(String(50), nullable=True, index=True)
    total_feedback = Column(Integer, default=0)
    processed_feedback = Column(Integer, default=0)
    pending_feedback = Column(Integer, default=0)
    failed_feedback = Column(Integer, default=0)
    avg_sentiment_score = Column(Float, nullable=True)
    positive_count = Column(Integer, default=0)
    neutral_count = Column(Integer, default=0)
    negative_count = Column(Integer, default=0)
    avg_rating = Column(Float, nullable=True)
    total_ratings = Column(Integer, default=0)
    avg_confidence_score = Column(Float, nullable=True)
    high_confidence_count = Column(Integer, default=0)
    low_confidence_count = Column(Integer, default=0)
    top_categories = Column(JSON, nullable=True)
    trending_topics = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<FeedbackAggregation(period={self.period}, start={self.period_start})>"