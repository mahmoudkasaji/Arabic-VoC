"""
Unified database models for Arabic Voice of Customer platform
"""

import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

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
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Content fields
    content = Column(Text, nullable=False, comment="Original feedback content in Arabic")
    processed_content = Column(Text, nullable=True, comment="Processed Arabic text (reshaped, normalized)")
    
    # Channel and status
    channel = Column(Enum(FeedbackChannel), nullable=False, index=True)
    status = Column(Enum(FeedbackStatus), default=FeedbackStatus.PENDING, index=True)
    
    # Customer information
    customer_email = Column(String(255), nullable=True)
    customer_phone = Column(String(50), nullable=True)
    customer_id = Column(String(100), nullable=True, index=True)
    
    # Ratings and analysis
    rating = Column(Integer, nullable=True, comment="Customer rating 1-5")
    sentiment_score = Column(Float, nullable=True, comment="AI sentiment score -1 to 1")
    confidence_score = Column(Float, nullable=True, comment="AI confidence score 0 to 1")
    
    # AI analysis results
    ai_summary = Column(Text, nullable=True, comment="AI-generated summary in Arabic")
    ai_categories = Column(JSON, nullable=True, comment="AI-detected categories and topics")
    ai_action_items = Column(JSON, nullable=True, comment="AI-suggested action items")
    
    # Metadata
    channel_metadata = Column(JSON, nullable=True, comment="Additional channel-specific metadata")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # Language and region
    language_detected = Column(String(10), default="ar", comment="Detected language code")
    region = Column(String(10), nullable=True, comment="Geographic region code")
    
    def __repr__(self):
        return f"<Feedback(id={self.id}, channel={self.channel}, status={self.status})>"
    
    def is_processed(self):
        """Check if feedback has been processed"""
        return self.status == FeedbackStatus.PROCESSED
    
    def sentiment_category(self):
        """Get sentiment category based on score"""
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
    """
    Aggregated feedback metrics for performance optimization
    Pre-computed analytics to avoid real-time calculations
    """
    __tablename__ = "feedback_aggregation"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Time period
    period = Column(Enum(AggregationPeriod), nullable=False, index=True)
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False)
    
    # Scope
    channel = Column(String(50), nullable=True, index=True, comment="NULL for all channels")
    
    # Basic counts
    total_feedback = Column(Integer, default=0)
    processed_feedback = Column(Integer, default=0)
    pending_feedback = Column(Integer, default=0)
    failed_feedback = Column(Integer, default=0)
    
    # Sentiment metrics
    avg_sentiment_score = Column(Float, nullable=True)
    positive_count = Column(Integer, default=0)
    neutral_count = Column(Integer, default=0)
    negative_count = Column(Integer, default=0)
    
    # Rating metrics
    avg_rating = Column(Float, nullable=True)
    total_ratings = Column(Integer, default=0)
    
    # Confidence metrics
    avg_confidence_score = Column(Float, nullable=True)
    high_confidence_count = Column(Integer, default=0, comment="Confidence > 0.8")
    low_confidence_count = Column(Integer, default=0, comment="Confidence < 0.5")
    
    # Topics and categories
    top_categories = Column(JSON, nullable=True)
    trending_topics = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<FeedbackAggregation(period={self.period}, start={self.period_start})>"