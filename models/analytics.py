"""
Analytics and aggregation models for feedback data
"""

import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

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

class TopicAnalysis(Base):
    """
    Topic analysis and categorization results
    Tracks emerging topics and themes in feedback
    """
    __tablename__ = "topic_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Topic information
    topic_name = Column(String(255), nullable=False, index=True)
    topic_keywords = Column(JSON, nullable=True, comment="Array of Arabic keywords")
    topic_description = Column(String(500), nullable=True)
    
    # Statistics
    frequency_count = Column(Integer, default=0)
    avg_sentiment = Column(Float, nullable=True)
    first_seen = Column(DateTime, nullable=False)
    last_seen = Column(DateTime, nullable=False)
    
    # Trending information
    trend_score = Column(Float, default=0.0, comment="Trending score algorithm")
    is_trending = Column(String(10), default="stable", comment="trending/declining/stable")
    
    # Relations
    related_feedback_ids = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<TopicAnalysis(topic={self.topic_name}, trend={self.is_trending})>"

class AlertRule(Base):
    """
    Configurable alert rules for real-time monitoring
    Triggers notifications based on feedback patterns
    """
    __tablename__ = "alert_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Rule definition
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    is_active = Column(String(10), default="true")
    
    # Conditions
    condition_type = Column(String(50), nullable=False, comment="sentiment/volume/rating/keyword")
    threshold_value = Column(Float, nullable=True)
    time_window_minutes = Column(Integer, default=60)
    
    # Targeting
    target_channels = Column(JSON, nullable=True, comment="Array of channels, NULL for all")
    
    # Notifications
    alert_email = Column(String(255), nullable=True)
    alert_webhook = Column(String(500), nullable=True)
    alert_message_template = Column(String(1000), nullable=True)
    
    # Status
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_triggered = Column(DateTime, nullable=True)
    trigger_count = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<AlertRule(name={self.name}, type={self.condition_type})>"

class FeedbackInsight(Base):
    """
    AI-generated insights and recommendations
    Strategic insights derived from feedback analysis
    """
    __tablename__ = "feedback_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Insight content
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=False)
    insight_type = Column(String(50), nullable=False, comment="trend/alert/recommendation/summary")
    
    # Priority and impact
    priority_level = Column(String(20), default="medium", comment="high/medium/low")
    impact_score = Column(Float, nullable=True, comment="0-1 estimated business impact")
    
    # Supporting data
    supporting_data = Column(JSON, nullable=True, comment="Metrics and evidence")
    related_feedback_count = Column(Integer, default=0)
    confidence_level = Column(Float, nullable=True, comment="AI confidence in insight")
    
    # Time period
    time_period_start = Column(DateTime, nullable=True)
    time_period_end = Column(DateTime, nullable=True)
    
    # Actions
    recommended_actions = Column(JSON, nullable=True, comment="Array of suggested actions")
    
    # Status tracking
    status = Column(String(20), default="new", comment="new/reviewed/acted_upon/dismissed")
    reviewed_by = Column(String(255), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<FeedbackInsight(title={self.title}, type={self.insight_type})>"

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
    
    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    
    # Time period
    period = Column(Enum(AggregationPeriod), nullable=False, index=True)
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False)
    
    # Channel aggregation
    channel = Column(String(50), nullable=True, index=True, comment="NULL for all channels")
    
    # Counts
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
    
    # AI confidence metrics
    avg_confidence_score = Column(Float, nullable=True)
    high_confidence_count = Column(Integer, default=0, comment="Confidence > 0.8")
    low_confidence_count = Column(Integer, default=0, comment="Confidence < 0.5")
    
    # Top categories and topics (JSON array)
    top_categories = Column(JSON, nullable=True)
    trending_topics = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<FeedbackAggregation(period={self.period}, start={self.period_start})>"

class TopicAnalysis(Base):
    """
    Topic analysis and categorization results
    Tracks emerging topics and themes in feedback
    """
    __tablename__ = "topic_analysis"
    
    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    
    # Topic information
    topic_name = Column(String(255), nullable=False, index=True)
    topic_keywords = Column(JSON, nullable=True, comment="Array of Arabic keywords")
    topic_description = Column(String(500), nullable=True)
    
    # Metrics
    frequency_count = Column(Integer, default=0)
    avg_sentiment = Column(Float, nullable=True)
    first_seen = Column(DateTime, nullable=False)
    last_seen = Column(DateTime, nullable=False)
    
    # Trend data
    trend_score = Column(Float, default=0.0, comment="Trending score algorithm")
    is_trending = Column(String(10), default="stable", comment="trending/declining/stable")
    
    # Related feedback IDs (for traceability)
    related_feedback_ids = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<TopicAnalysis(topic={self.topic_name}, frequency={self.frequency_count})>"

class AlertRule(Base):
    """
    Configurable alert rules for real-time monitoring
    Triggers notifications based on feedback patterns
    """
    __tablename__ = "alert_rules"
    
    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    
    # Rule configuration
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    is_active = Column(String(10), default="true")
    
    # Trigger conditions
    condition_type = Column(String(50), nullable=False, comment="sentiment/volume/rating/keyword")
    threshold_value = Column(Float, nullable=True)
    time_window_minutes = Column(Integer, default=60)
    
    # Channel filters
    target_channels = Column(JSON, nullable=True, comment="Array of channels, NULL for all")
    
    # Alert actions
    alert_email = Column(String(255), nullable=True)
    alert_webhook = Column(String(500), nullable=True)
    alert_message_template = Column(String(1000), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_triggered = Column(DateTime, nullable=True)
    trigger_count = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<AlertRule(name={self.name}, condition={self.condition_type})>"

class FeedbackInsight(Base):
    """
    AI-generated insights and recommendations
    Strategic insights derived from feedback analysis
    """
    __tablename__ = "feedback_insights"
    
    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    
    # Insight content
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=False)
    insight_type = Column(String(50), nullable=False, comment="trend/alert/recommendation/summary")
    
    # Priority and impact
    priority_level = Column(String(20), default="medium", comment="high/medium/low")
    impact_score = Column(Float, nullable=True, comment="0-1 estimated business impact")
    
    # Supporting data
    supporting_data = Column(JSON, nullable=True, comment="Metrics and evidence")
    related_feedback_count = Column(Integer, default=0)
    confidence_level = Column(Float, nullable=True, comment="AI confidence in insight")
    
    # Time relevance
    time_period_start = Column(DateTime, nullable=True)
    time_period_end = Column(DateTime, nullable=True)
    
    # Action recommendations
    recommended_actions = Column(JSON, nullable=True, comment="Array of suggested actions")
    
    # Status tracking
    status = Column(String(20), default="new", comment="new/reviewed/acted_upon/dismissed")
    reviewed_by = Column(String(255), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<FeedbackInsight(title={self.title}, type={self.insight_type})>"
