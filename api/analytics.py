"""
Analytics API endpoints for real-time feedback analytics
Provides insights and metrics for Arabic feedback data
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
import time
import psutil

from models_unified import FeedbackChannel, FeedbackStatus
from utils.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

class AnalyticsTimeRange(BaseModel):
    """Time range for analytics queries"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class SentimentMetrics(BaseModel):
    """Sentiment analysis metrics"""
    average_sentiment: float
    positive_count: int
    neutral_count: int
    negative_count: int
    total_feedback: int
    confidence_score: float

class ChannelMetrics(BaseModel):
    """Channel-specific metrics"""
    channel: FeedbackChannel
    feedback_count: int
    average_sentiment: float
    average_rating: Optional[float]
    latest_feedback: Optional[datetime]

class DashboardMetrics(BaseModel):
    """Complete dashboard metrics"""
    total_feedback: int
    processed_feedback: int
    pending_feedback: int
    average_sentiment: float
    sentiment_distribution: Dict[str, int]
    channel_metrics: List[ChannelMetrics]
    trending_topics: List[Dict[str, Any]]
    recent_feedback_count: int

class TrendAnalysis(BaseModel):
    """Trend analysis over time"""
    date: datetime
    feedback_count: int
    average_sentiment: float
    positive_percentage: float
    negative_percentage: float

class PerformanceMetrics(BaseModel):
    """Performance metrics for the API"""
    endpoint: str
    execution_time: float
    cpu_usage: float
    memory_usage: float
    timestamp: datetime

performance_metrics = []

def track_performance(func):
    """Decorator to track performance of API endpoints"""
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        cpu_before = psutil.cpu_percent()
        memory_before = psutil.virtual_memory().percent
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            execution_time = end_time - start_time
            cpu_after = psutil.cpu_percent()
            memory_after = psutil.virtual_memory().percent
            cpu_usage = (cpu_after - cpu_before)
            memory_usage = (memory_after - memory_before)

            metrics = PerformanceMetrics(
                endpoint=func.__name__,
                execution_time=execution_time,
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                timestamp=datetime.utcnow()
            )
            performance_metrics.append(metrics)
            logger.info(f"Performance metrics for {func.__name__}: {metrics}")
    return wrapper

@router.get("/dashboard", response_model=DashboardMetrics)
@track_performance
async def get_dashboard_metrics(
    time_range: AnalyticsTimeRange = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive dashboard metrics"""
    """
    This endpoint retrieves comprehensive dashboard metrics for the feedback analytics system.

    For non-technical users:
    This provides an overview of all feedback data, including total feedback count,
    the distribution of sentiment (positive, negative, neutral), metrics for each channel,
    and trending topics.  You can specify a time range to focus on specific periods.
    """
    try:
        # Set default time range if not provided
        if not time_range.end_date:
            time_range.end_date = datetime.utcnow()
        if not time_range.start_date:
            time_range.start_date = time_range.end_date - timedelta(days=30)

        # Total feedback metrics
        total_result = await db.execute(
            """
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN status = 'PROCESSED' THEN 1 END) as processed,
                COUNT(CASE WHEN status = 'PENDING' THEN 1 END) as pending,
                AVG(sentiment_score) as avg_sentiment
            FROM feedback 
            WHERE created_at BETWEEN :start_date AND :end_date
            """,
            {
                "start_date": time_range.start_date,
                "end_date": time_range.end_date
            }
        )
        total_metrics = total_result.fetchone()

        # Sentiment distribution
        sentiment_result = await db.execute(
            """
            SELECT 
                CASE 
                    WHEN sentiment_score > 0.1 THEN 'positive'
                    WHEN sentiment_score < -0.1 THEN 'negative'
                    ELSE 'neutral'
                END as sentiment_category,
                COUNT(*) as count
            FROM feedback 
            WHERE created_at BETWEEN :start_date AND :end_date
            AND sentiment_score IS NOT NULL
            GROUP BY sentiment_category
            """,
            {
                "start_date": time_range.start_date,
                "end_date": time_range.end_date
            }
        )
        sentiment_dist = {row[0]: row[1] for row in sentiment_result.fetchall()}

        # Channel metrics
        channel_result = await db.execute(
            """
            SELECT 
                channel,
                COUNT(*) as feedback_count,
                AVG(sentiment_score) as avg_sentiment,
                AVG(rating) as avg_rating,
                MAX(created_at) as latest_feedback
            FROM feedback 
            WHERE created_at BETWEEN :start_date AND :end_date
            GROUP BY channel
            ORDER BY feedback_count DESC
            """,
            {
                "start_date": time_range.start_date,
                "end_date": time_range.end_date
            }
        )

        channel_metrics = []
        for row in channel_result.fetchall():
            channel_metrics.append(ChannelMetrics(
                channel=row[0],
                feedback_count=row[1],
                average_sentiment=row[2] or 0.0,
                average_rating=row[3],
                latest_feedback=row[4]
            ))

        # Recent feedback count (last 24 hours)
        recent_result = await db.execute(
            """
            SELECT COUNT(*) 
            FROM feedback 
            WHERE created_at >= :recent_date
            """,
            {"recent_date": datetime.utcnow() - timedelta(hours=24)}
        )
        recent_count = recent_result.scalar()

        # Trending topics (simplified - would need more advanced NLP in production)
        trending_result = await db.execute(
            """
            SELECT ai_summary, COUNT(*) as frequency
            FROM feedback 
            WHERE created_at BETWEEN :start_date AND :end_date
            AND ai_summary IS NOT NULL
            AND LENGTH(ai_summary) > 10
            GROUP BY ai_summary
            ORDER BY frequency DESC
            LIMIT 5
            """,
            {
                "start_date": time_range.start_date,
                "end_date": time_range.end_date
            }
        )

        trending_topics = []
        for row in trending_result.fetchall():
            trending_topics.append({
                "topic": row[0],
                "frequency": row[1]
            })

        return DashboardMetrics(
            total_feedback=total_metrics[0] or 0,
            processed_feedback=total_metrics[1] or 0,
            pending_feedback=total_metrics[2] or 0,
            average_sentiment=total_metrics[3] or 0.0,
            sentiment_distribution=sentiment_dist,
            channel_metrics=channel_metrics,
            trending_topics=trending_topics,
            recent_feedback_count=recent_count or 0
        )

    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="خطأ في استرجاع البيانات التحليلية")

@router.get("/sentiment", response_model=SentimentMetrics)
@track_performance
async def get_sentiment_metrics(
    time_range: AnalyticsTimeRange = Depends(),
    channel: Optional[FeedbackChannel] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed sentiment analysis metrics"""
    """
    This endpoint provides detailed sentiment analysis metrics for the feedback data.

    For non-technical users:
    This endpoint shows the average sentiment score, the number of positive, neutral,
    and negative feedback entries, the total feedback count, and a confidence score.
    You can filter the results by channel and specify a time range.
    """
    try:
        # Set default time range
        if not time_range.end_date:
            time_range.end_date = datetime.utcnow()
        if not time_range.start_date:
            time_range.start_date = time_range.end_date - timedelta(days=7)

        # Build query with optional channel filter
        query_parts = [
            """
            SELECT 
                AVG(sentiment_score) as avg_sentiment,
                AVG(confidence_score) as avg_confidence,
                COUNT(*) as total,
                COUNT(CASE WHEN sentiment_score > 0.1 THEN 1 END) as positive,
                COUNT(CASE WHEN sentiment_score BETWEEN -0.1 AND 0.1 THEN 1 END) as neutral,
                COUNT(CASE WHEN sentiment_score < -0.1 THEN 1 END) as negative
            FROM feedback 
            WHERE created_at BETWEEN :start_date AND :end_date
            AND sentiment_score IS NOT NULL
            """
        ]

        params = {
            "start_date": time_range.start_date,
            "end_date": time_range.end_date
        }

        if channel:
            query_parts.append("AND channel = :channel")
            params["channel"] = channel

        query = " ".join(query_parts)

        result = await db.execute(query, params)
        metrics = result.fetchone()

        if not metrics or metrics[2] == 0:  # No data found
            return SentimentMetrics(
                average_sentiment=0.0,
                positive_count=0,
                neutral_count=0,
                negative_count=0,
                total_feedback=0,
                confidence_score=0.0
            )

        return SentimentMetrics(
            average_sentiment=metrics[0] or 0.0,
            positive_count=metrics[3] or 0,
            neutral_count=metrics[4] or 0,
            negative_count=metrics[5] or 0,
            total_feedback=metrics[2] or 0,
            confidence_score=metrics[1] or 0.0
        )

    except Exception as e:
        logger.error(f"Error getting sentiment metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="خطأ في تحليل المشاعر")

@router.get("/trends", response_model=List[TrendAnalysis])
@track_performance
async def get_trend_analysis(
    time_range: AnalyticsTimeRange = Depends(),
    granularity: str = "daily",
    db: AsyncSession = Depends(get_db)
):
    """Get trend analysis over time"""
    """
    This endpoint provides trend analysis of feedback data over time.

    For non-technical users:
    This endpoint visualizes how feedback changes over time, showing the count of feedback,
    average sentiment, and the percentage of positive and negative feedback.
    You can specify the time range and the granularity (daily, hourly, weekly, monthly).
    """
    try:
        # Set default time range
        if not time_range.end_date:
            time_range.end_date = datetime.utcnow()
        if not time_range.start_date:
            time_range.start_date = time_range.end_date - timedelta(days=30)

        # Determine date truncation based on granularity
        date_trunc = "day"
        if granularity == "hourly":
            date_trunc = "hour"
        elif granularity == "weekly":
            date_trunc = "week"
        elif granularity == "monthly":
            date_trunc = "month"

        result = await db.execute(
            f"""
            SELECT 
                DATE_TRUNC('{date_trunc}', created_at) as period,
                COUNT(*) as feedback_count,
                AVG(sentiment_score) as avg_sentiment,
                COUNT(CASE WHEN sentiment_score > 0.1 THEN 1 END) * 100.0 / COUNT(*) as positive_pct,
                COUNT(CASE WHEN sentiment_score < -0.1 THEN 1 END) * 100.0 / COUNT(*) as negative_pct
            FROM feedback 
            WHERE created_at BETWEEN :start_date AND :end_date
            AND sentiment_score IS NOT NULL
            GROUP BY DATE_TRUNC('{date_trunc}', created_at)
            ORDER BY period
            """,
            {
                "start_date": time_range.start_date,
                "end_date": time_range.end_date
            }
        )

        trends = []
        for row in result.fetchall():
            trends.append(TrendAnalysis(
                date=row[0],
                feedback_count=row[1] or 0,
                average_sentiment=row[2] or 0.0,
                positive_percentage=row[3] or 0.0,
                negative_percentage=row[4] or 0.0
            ))

        return trends

    except Exception as e:
        logger.error(f"Error getting trend analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="خطأ في تحليل الاتجاهات")

@router.get("/export")
@track_performance
async def export_analytics(
    time_range: AnalyticsTimeRange = Depends(),
    format: str = "json",
    db: AsyncSession = Depends(get_db)
):
    """Export analytics data in various formats"""
    """
    This endpoint exports analytics data in various formats.

    For non-technical users:
    This allows you to download the feedback data for further analysis or reporting.
    You can specify the time range and the format (currently only JSON is supported).
    """
    try:
        # Set default time range
        if not time_range.end_date:
            time_range.end_date = datetime.utcnow()
        if not time_range.start_date:
            time_range.start_date = time_range.end_date - timedelta(days=30)

        # Get comprehensive data
        result = await db.execute(
            """
            SELECT 
                id,
                content,
                processed_content,
                channel,
                status,
                sentiment_score,
                confidence_score,
                rating,
                ai_summary,
                created_at,
                processed_at
            FROM feedback 
            WHERE created_at BETWEEN :start_date AND :end_date
            ORDER BY created_at DESC
            """,
            {
                "start_date": time_range.start_date,
                "end_date": time_range.end_date
            }
        )

        data = []
        for row in result.fetchall():
            data.append({
                "id": row[0],
                "content": row[1],
                "processed_content": row[2],
                "channel": row[3],
                "status": row[4],
                "sentiment_score": row[5],
                "confidence_score": row[6],
                "rating": row[7],
                "ai_summary": row[8],
                "created_at": row[9].isoformat() if row[9] else None,
                "processed_at": row[10].isoformat() if row[10] else None
            })

        if format.lower() == "csv":
            # Would implement CSV export here
            raise HTTPException(status_code=501, detail="تصدير CSV غير مدعوم حالياً")

        return {
            "data": data,
            "total_records": len(data),
            "time_range": {
                "start": time_range.start_date.isoformat(),
                "end": time_range.end_date.isoformat()
            },
            "exported_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error exporting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="خطأ في تصدير البيانات")

@router.get("/performance_summary")
async def get_performance_summary():
    """
    Get a summary of performance metrics for the API.

    For non-technical users:
    This endpoint provides a summary of the API's performance, including average execution time,
    CPU usage, and memory usage for each endpoint. This helps monitor the efficiency of the system.
    """
    if not performance_metrics:
        return {"message": "No performance data available yet."}

    summary = {}
    for metric in performance_metrics:
        if metric.endpoint not in summary:
            summary[metric.endpoint] = {
                "count": 0,
                "total_execution_time": 0,
                "total_cpu_usage": 0,
                "total_memory_usage": 0
            }
        summary[metric.endpoint]["count"] += 1
        summary[metric.endpoint]["total_execution_time"] += metric.execution_time
        summary[metric.endpoint]["total_cpu_usage"] += metric.cpu_usage
        summary[metric.endpoint]["total_memory_usage"] += metric.memory_usage

    for endpoint, data in summary.items():
        count = data["count"]
        summary[endpoint] = {
            "average_execution_time": data["total_execution_time"] / count,
            "average_cpu_usage": data["total_cpu_usage"] / count,
            "average_memory_usage": data["total_memory_usage"] / count
        }

    return summary