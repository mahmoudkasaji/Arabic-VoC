"""
Executive Dashboard API endpoints for Arabic VoC platform
Provides real-time KPI metrics for executive consumption
"""

from flask import Blueprint, jsonify, render_template
from datetime import datetime, timedelta
from sqlalchemy import func, and_, text
from sqlalchemy.orm import sessionmaker
from models_unified import Feedback, FeedbackChannel, FeedbackStatus, FeedbackAggregation
from app import db
import logging

# Create blueprint
executive_bp = Blueprint('executive', __name__, url_prefix='/api/executive-dashboard')

logger = logging.getLogger(__name__)

def calculate_csat_score(days=30):
    """
    Calculate Customer Satisfaction Score based on sentiment analysis
    """
    try:
        # Get date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query for processed feedback with sentiment scores
        feedback_query = db.session.query(Feedback).filter(
            and_(
                Feedback.created_at >= start_date,
                Feedback.created_at <= end_date,
                Feedback.status == FeedbackStatus.PROCESSED,
                Feedback.sentiment_score.isnot(None)
            )
        )
        
        # Calculate current period CSAT
        current_feedback = feedback_query.all()
        
        if not current_feedback:
            return {
                'score': 0.0,
                'trend': 0.0,
                'total_responses': 0,
                'confidence': 0.0
            }
        
        # Convert sentiment scores (-1 to 1) to satisfaction scores (0 to 1)
        # Positive sentiment (>0.1) = Satisfied
        satisfied_count = sum(1 for f in current_feedback if f.sentiment_score > 0.1)
        total_count = len(current_feedback)
        current_csat = satisfied_count / total_count if total_count > 0 else 0.0
        
        # Calculate average confidence
        avg_confidence = sum(f.confidence_score or 0.0 for f in current_feedback) / total_count
        
        # Calculate trend (previous period comparison)
        prev_start = start_date - timedelta(days=days)
        prev_end = start_date
        
        prev_feedback = db.session.query(Feedback).filter(
            and_(
                Feedback.created_at >= prev_start,
                Feedback.created_at < prev_end,
                Feedback.status == FeedbackStatus.PROCESSED,
                Feedback.sentiment_score.isnot(None)
            )
        ).all()
        
        if prev_feedback:
            prev_satisfied = sum(1 for f in prev_feedback if f.sentiment_score > 0.1)
            prev_total = len(prev_feedback)
            prev_csat = prev_satisfied / prev_total if prev_total > 0 else 0.0
            trend = ((current_csat - prev_csat) / prev_csat * 100) if prev_csat > 0 else 0.0
        else:
            trend = 0.0
        
        return {
            'score': current_csat,
            'trend': trend,
            'total_responses': total_count,
            'confidence': avg_confidence
        }
        
    except Exception as e:
        logger.error(f"Error calculating CSAT: {e}")
        return {
            'score': 0.0,
            'trend': 0.0,
            'total_responses': 0,
            'confidence': 0.0
        }

def calculate_volume_metrics():
    """
    Calculate response volume metrics
    """
    try:
        now = datetime.utcnow()
        
        # Today
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_count = db.session.query(func.count(Feedback.id)).filter(
            Feedback.created_at >= today_start
        ).scalar() or 0
        
        # This week
        week_start = now - timedelta(days=now.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_count = db.session.query(func.count(Feedback.id)).filter(
            Feedback.created_at >= week_start
        ).scalar() or 0
        
        # This month
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_count = db.session.query(func.count(Feedback.id)).filter(
            Feedback.created_at >= month_start
        ).scalar() or 0
        
        # Total (last 30 days)
        thirty_days_ago = now - timedelta(days=30)
        total_count = db.session.query(func.count(Feedback.id)).filter(
            Feedback.created_at >= thirty_days_ago
        ).scalar() or 0
        
        # Calculate trend (this week vs last week)
        last_week_start = week_start - timedelta(days=7)
        last_week_count = db.session.query(func.count(Feedback.id)).filter(
            and_(
                Feedback.created_at >= last_week_start,
                Feedback.created_at < week_start
            )
        ).scalar() or 0
        
        trend = ((week_count - last_week_count) / last_week_count * 100) if last_week_count > 0 else 0.0
        
        return {
            'total': total_count,
            'today': today_count,
            'week': week_count,
            'month': month_count,
            'trend': trend
        }
        
    except Exception as e:
        logger.error(f"Error calculating volume metrics: {e}")
        return {
            'total': 0,
            'today': 0,
            'week': 0,
            'month': 0,
            'trend': 0.0
        }

def calculate_sentiment_metrics(days=30):
    """
    Calculate Arabic sentiment metrics
    """
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get current period sentiment data
        current_feedback = db.session.query(Feedback.sentiment_score, Feedback.confidence_score).filter(
            and_(
                Feedback.created_at >= start_date,
                Feedback.created_at <= end_date,
                Feedback.status == FeedbackStatus.PROCESSED,
                Feedback.sentiment_score.isnot(None)
            )
        ).all()
        
        if not current_feedback:
            return {
                'score': 0.0,
                'trend': 0.0,
                'confidence': 0.0,
                'distribution': {'positive': 0, 'neutral': 0, 'negative': 0}
            }
        
        # Calculate average sentiment score
        sentiment_scores = [f.sentiment_score for f in current_feedback]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        
        # Calculate confidence
        confidence_scores = [f.confidence_score or 0.0 for f in current_feedback]
        avg_confidence = sum(confidence_scores) / len(confidence_scores)
        
        # Calculate distribution
        positive = sum(1 for score in sentiment_scores if score > 0.1)
        negative = sum(1 for score in sentiment_scores if score < -0.1)
        neutral = len(sentiment_scores) - positive - negative
        
        # Calculate trend
        prev_start = start_date - timedelta(days=days)
        prev_end = start_date
        
        prev_sentiment = db.session.query(func.avg(Feedback.sentiment_score)).filter(
            and_(
                Feedback.created_at >= prev_start,
                Feedback.created_at < prev_end,
                Feedback.status == FeedbackStatus.PROCESSED,
                Feedback.sentiment_score.isnot(None)
            )
        ).scalar() or 0.0
        
        trend = ((avg_sentiment - prev_sentiment) / abs(prev_sentiment) * 100) if prev_sentiment != 0 else 0.0
        
        return {
            'score': avg_sentiment,
            'trend': trend,
            'confidence': avg_confidence,
            'distribution': {
                'positive': positive,
                'neutral': neutral,
                'negative': negative
            }
        }
        
    except Exception as e:
        logger.error(f"Error calculating sentiment metrics: {e}")
        return {
            'score': 0.0,
            'trend': 0.0,
            'confidence': 0.0,
            'distribution': {'positive': 0, 'neutral': 0, 'negative': 0}
        }

def get_trend_data(days=30):
    """
    Get trend data for the last 30 days
    """
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Generate daily CSAT data
        daily_data = []
        labels = []
        
        for i in range(days):
            day = start_date + timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            # Get feedback for this day
            day_feedback = db.session.query(Feedback.sentiment_score).filter(
                and_(
                    Feedback.created_at >= day_start,
                    Feedback.created_at < day_end,
                    Feedback.status == FeedbackStatus.PROCESSED,
                    Feedback.sentiment_score.isnot(None)
                )
            ).all()
            
            if day_feedback:
                satisfied = sum(1 for f in day_feedback if f.sentiment_score > 0.1)
                total = len(day_feedback)
                csat = (satisfied / total * 100) if total > 0 else 0
            else:
                csat = 0
            
            daily_data.append(csat)
            labels.append(day.strftime('%m/%d'))
        
        return {
            'labels': labels,
            'values': daily_data
        }
        
    except Exception as e:
        logger.error(f"Error getting trend data: {e}")
        return {
            'labels': [],
            'values': []
        }

def get_channel_distribution(days=30):
    """
    Get feedback distribution by channel
    """
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query channel distribution
        channel_data = db.session.query(
            Feedback.channel,
            func.count(Feedback.id).label('count')
        ).filter(
            and_(
                Feedback.created_at >= start_date,
                Feedback.created_at <= end_date
            )
        ).group_by(Feedback.channel).all()
        
        # Arabic channel names
        channel_names = {
            FeedbackChannel.EMAIL: 'البريد الإلكتروني',
            FeedbackChannel.PHONE: 'الهاتف',
            FeedbackChannel.WEBSITE: 'الموقع الإلكتروني',
            FeedbackChannel.MOBILE_APP: 'التطبيق المحمول',
            FeedbackChannel.SOCIAL_MEDIA: 'وسائل التواصل',
            FeedbackChannel.WHATSAPP: 'واتساب',
            FeedbackChannel.SMS: 'الرسائل النصية',
            FeedbackChannel.IN_PERSON: 'وجهاً لوجه',
            FeedbackChannel.SURVEY: 'الاستطلاعات',
            FeedbackChannel.CHATBOT: 'الدردشة الآلية'
        }
        
        labels = []
        values = []
        
        for channel, count in channel_data:
            labels.append(channel_names.get(channel, channel.value))
            values.append(count)
        
        return {
            'labels': labels,
            'values': values
        }
        
    except Exception as e:
        logger.error(f"Error getting channel distribution: {e}")
        return {
            'labels': [],
            'values': []
        }

@executive_bp.route('/metrics')
def get_dashboard_metrics():
    """
    Get all executive dashboard metrics
    """
    try:
        # Calculate all metrics
        csat = calculate_csat_score()
        volume = calculate_volume_metrics()
        sentiment = calculate_sentiment_metrics()
        trends = get_trend_data()
        channels = get_channel_distribution()
            
            return jsonify({
                'csat': csat,
                'volume': volume,
                'sentiment': sentiment,
                'trends': trends,
                'channels': channels,
                'timestamp': datetime.utcnow().isoformat()
            })
            
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}")
        return jsonify({'error': 'Failed to load metrics'}), 500

@executive_bp.route('/csat')
def get_csat_metrics():
    """
    Get detailed CSAT metrics
    """
    try:
        csat = calculate_csat_score()
        return jsonify(csat)
            
    except Exception as e:
        logger.error(f"Error getting CSAT metrics: {e}")
        return jsonify({'error': 'Failed to load CSAT metrics'}), 500

@executive_bp.route('/volume')
def get_volume_metrics():
    """
    Get detailed volume metrics
    """
    try:
        volume = calculate_volume_metrics()
        return jsonify(volume)
            
    except Exception as e:
        logger.error(f"Error getting volume metrics: {e}")
        return jsonify({'error': 'Failed to load volume metrics'}), 500

@executive_bp.route('/sentiment')
def get_sentiment_metrics_endpoint():
    """
    Get detailed sentiment metrics
    """
    try:
        sentiment = calculate_sentiment_metrics()
        return jsonify(sentiment)
            
    except Exception as e:
        logger.error(f"Error getting sentiment metrics: {e}")
        return jsonify({'error': 'Failed to load sentiment metrics'}), 500