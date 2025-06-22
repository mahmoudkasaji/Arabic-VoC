"""
Analytics and reporting models
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Text
from datetime import datetime
from app.main import Base

class AnalyticsReport(Base):
    """Store generated analytics reports"""
    __tablename__ = "analytics_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(String(100), nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    data = Column(JSON, nullable=True)
    created_by = Column(String(100), nullable=True)

class DashboardMetrics(Base):
    """Cache dashboard metrics for performance"""
    __tablename__ = "dashboard_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_date = Column(DateTime, default=datetime.utcnow, index=True)
    total_feedback = Column(Integer, default=0)
    avg_sentiment = Column(Float, nullable=True)
    processed_count = Column(Integer, default=0)
    cached_data = Column(JSON, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)