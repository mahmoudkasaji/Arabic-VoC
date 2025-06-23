"""
Survey Delivery Models
Extends existing feedback infrastructure for structured survey distribution
"""

import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Enum, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from models_unified import Base, FeedbackChannel

class SurveyStatus(str, enum.Enum):
    """Survey campaign status"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class DeliveryStatus(str, enum.Enum):
    """Individual survey delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"

class ResponseStatus(str, enum.Enum):
    """Survey response completion status"""
    NOT_STARTED = "not_started"
    PARTIAL = "partial"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

class SurveyTemplate(Base):
    """Survey template with questions and configuration"""
    __tablename__ = "survey_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, comment="Arabic survey title")
    description = Column(Text, nullable=True, comment="Arabic survey description")
    questions = Column(JSON, nullable=False, comment="Questions with Arabic text and types")
    estimated_duration = Column(Integer, nullable=True, comment="Estimated completion time in minutes")
    target_channels = Column(JSON, nullable=True, comment="Preferred delivery channels")
    settings = Column(JSON, nullable=True, comment="Survey behavior settings")
    
    # Metadata
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    campaigns = relationship("SurveyCampaign", back_populates="template")
    
    def __repr__(self):
        return f"<SurveyTemplate(id={self.id}, title='{self.title[:30]}...')>"

class SurveyCampaign(Base):
    """Survey distribution campaign"""
    __tablename__ = "survey_campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey('survey_templates.id'), nullable=False)
    
    # Campaign details
    name = Column(String(255), nullable=False, comment="Campaign name in Arabic")
    description = Column(Text, nullable=True, comment="Campaign description")
    status = Column(Enum(SurveyStatus), default=SurveyStatus.DRAFT, index=True)
    
    # Distribution configuration
    target_audience = Column(JSON, nullable=False, comment="Audience segmentation criteria")
    channels_config = Column(JSON, nullable=False, comment="Channel-specific delivery settings")
    schedule_config = Column(JSON, nullable=True, comment="Timing and frequency settings")
    
    # Campaign timing
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    
    # Campaign metrics
    target_count = Column(Integer, default=0, comment="Target audience size")
    sent_count = Column(Integer, default=0, comment="Successfully sent surveys")
    delivered_count = Column(Integer, default=0, comment="Successfully delivered surveys")
    response_count = Column(Integer, default=0, comment="Received responses")
    completion_count = Column(Integer, default=0, comment="Completed responses")
    
    # Metadata
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    template = relationship("SurveyTemplate", back_populates="campaigns")
    deliveries = relationship("SurveyDelivery", back_populates="campaign")
    responses = relationship("SurveyResponse", back_populates="campaign")
    
    def __repr__(self):
        return f"<SurveyCampaign(id={self.id}, name='{self.name[:30]}...', status={self.status})>"
    
    @property
    def response_rate(self):
        """Calculate response rate percentage"""
        if self.sent_count == 0:
            return 0.0
        return (self.response_count / self.sent_count) * 100
    
    @property
    def completion_rate(self):
        """Calculate completion rate percentage"""
        if self.response_count == 0:
            return 0.0
        return (self.completion_count / self.response_count) * 100

class SurveyDelivery(Base):
    """Individual survey delivery tracking"""
    __tablename__ = "survey_deliveries"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey('survey_campaigns.id'), nullable=False)
    
    # Recipient information
    recipient_id = Column(String(100), nullable=True, comment="Customer ID")
    recipient_email = Column(String(255), nullable=True)
    recipient_phone = Column(String(50), nullable=True)
    recipient_whatsapp = Column(String(50), nullable=True)
    recipient_name = Column(String(255), nullable=True)
    
    # Delivery details
    channel = Column(Enum(FeedbackChannel), nullable=False, index=True)
    status = Column(Enum(DeliveryStatus), default=DeliveryStatus.PENDING, index=True)
    delivery_token = Column(String(255), nullable=True, comment="Unique response token")
    
    # Channel-specific metadata
    channel_metadata = Column(JSON, nullable=True, comment="Channel-specific delivery data")
    
    # Timing
    scheduled_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaign = relationship("SurveyCampaign", back_populates="deliveries")
    responses = relationship("SurveyResponse", back_populates="delivery")
    
    def __repr__(self):
        return f"<SurveyDelivery(id={self.id}, channel={self.channel}, status={self.status})>"
    
    @property
    def can_retry(self):
        """Check if delivery can be retried"""
        return self.status == DeliveryStatus.FAILED and self.retry_count < self.max_retries

class SurveyResponse(Base):
    """Survey response with structured answers"""
    __tablename__ = "survey_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey('survey_campaigns.id'), nullable=False)
    delivery_id = Column(Integer, ForeignKey('survey_deliveries.id'), nullable=True)
    
    # Response identification
    response_token = Column(String(255), nullable=True, comment="Unique response identifier")
    respondent_id = Column(String(100), nullable=True, comment="Customer ID")
    
    # Response data
    responses = Column(JSON, nullable=False, comment="Structured survey answers")
    completion_status = Column(Enum(ResponseStatus), default=ResponseStatus.NOT_STARTED, index=True)
    completion_percentage = Column(Float, default=0.0, comment="Percentage of questions answered")
    
    # Timing data
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    last_interaction_at = Column(DateTime, nullable=True)
    total_time_seconds = Column(Integer, nullable=True, comment="Total completion time")
    
    # Channel and device info
    submission_channel = Column(Enum(FeedbackChannel), nullable=False, index=True)
    device_info = Column(JSON, nullable=True, comment="Device and browser information")
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Analysis results
    sentiment_scores = Column(JSON, nullable=True, comment="AI sentiment analysis per question")
    satisfaction_score = Column(Float, nullable=True, comment="Overall satisfaction score")
    nps_score = Column(Integer, nullable=True, comment="Net Promoter Score if applicable")
    
    # Quality metrics
    quality_score = Column(Float, nullable=True, comment="Response quality assessment")
    is_suspicious = Column(Boolean, default=False, comment="Flagged for suspicious activity")
    
    # Language and processing
    language_detected = Column(String(10), default="ar", comment="Detected response language")
    processed_responses = Column(JSON, nullable=True, comment="AI-processed response data")
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaign = relationship("SurveyCampaign", back_populates="responses")
    delivery = relationship("SurveyDelivery", back_populates="responses")
    
    def __repr__(self):
        return f"<SurveyResponse(id={self.id}, status={self.completion_status}, score={self.satisfaction_score})>"
    
    @property
    def is_complete(self):
        """Check if response is completed"""
        return self.completion_status == ResponseStatus.COMPLETED
    
    @property
    def response_time_minutes(self):
        """Get response time in minutes"""
        if self.total_time_seconds:
            return round(self.total_time_seconds / 60, 2)
        return None

class ChannelPreference(Base):
    """Customer channel preferences for survey delivery"""
    __tablename__ = "channel_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(100), nullable=False, index=True)
    
    # Channel preferences
    preferred_channels = Column(JSON, nullable=False, comment="Ordered list of preferred channels")
    blocked_channels = Column(JSON, nullable=True, comment="Channels to avoid")
    
    # Timing preferences
    preferred_times = Column(JSON, nullable=True, comment="Preferred contact times by day")
    time_zone = Column(String(50), default="Asia/Riyadh")
    
    # Communication preferences
    language_preference = Column(String(10), default="ar")
    frequency_limit = Column(Integer, default=2, comment="Max surveys per month")
    
    # Performance tracking
    response_history = Column(JSON, nullable=True, comment="Historical response rates by channel")
    last_response_date = Column(DateTime, nullable=True)
    total_surveys_received = Column(Integer, default=0)
    total_surveys_completed = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ChannelPreference(customer_id='{self.customer_id}', preferred={self.preferred_channels})>"
    
    @property
    def response_rate(self):
        """Calculate customer's overall response rate"""
        if self.total_surveys_received == 0:
            return 0.0
        return (self.total_surveys_completed / self.total_surveys_received) * 100

class SurveyAnalytics(Base):
    """Aggregated survey analytics data"""
    __tablename__ = "survey_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey('survey_campaigns.id'), nullable=False)
    
    # Date aggregation
    date = Column(DateTime, nullable=False, index=True)
    period_type = Column(String(20), nullable=False, comment="daily, weekly, monthly")
    
    # Delivery metrics
    sent_count = Column(Integer, default=0)
    delivered_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    bounce_count = Column(Integer, default=0)
    
    # Response metrics
    response_count = Column(Integer, default=0)
    completion_count = Column(Integer, default=0)
    abandonment_count = Column(Integer, default=0)
    
    # Quality metrics
    avg_response_time = Column(Float, nullable=True, comment="Average completion time in minutes")
    avg_satisfaction_score = Column(Float, nullable=True)
    avg_nps_score = Column(Float, nullable=True)
    
    # Channel breakdown
    channel_performance = Column(JSON, nullable=True, comment="Performance metrics by channel")
    
    # Text analysis
    common_themes = Column(JSON, nullable=True, comment="Most common response themes")
    sentiment_distribution = Column(JSON, nullable=True, comment="Sentiment score distribution")
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<SurveyAnalytics(campaign_id={self.campaign_id}, date={self.date}, responses={self.response_count})>"