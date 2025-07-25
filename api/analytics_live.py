"""
Live Analytics API Endpoints
Provides real-time analytics data from survey responses
"""

from flask import Blueprint, jsonify, request
from utils.live_analytics import LiveAnalyticsProcessor
import logging

logger = logging.getLogger(__name__)

# Create blueprint
analytics_live_bp = Blueprint('analytics_live', __name__, url_prefix='/api/analytics')

# Initialize processor
analytics_processor = LiveAnalyticsProcessor()


@analytics_live_bp.route('/live-dashboard', methods=['GET'])
def get_live_dashboard():
    """
    Get live dashboard metrics from real survey data
    
    Query Parameters:
        time_range: "1d", "7d", "30d", "all" (default: "7d")
    
    Returns:
        JSON with CSAT, response volume, sentiment, completion metrics
    """
    try:
        time_range = request.args.get('time_range', '7d')
        
        # Validate time_range parameter
        valid_ranges = ['1d', '7d', '30d', 'all']
        if time_range not in valid_ranges:
            return jsonify({
                'error': 'Invalid time_range parameter',
                'valid_options': valid_ranges
            }), 400
        
        # Get live metrics
        metrics = analytics_processor.get_dashboard_metrics(time_range)
        
        return jsonify({
            'success': True,
            'data': metrics,
            'message': 'Live dashboard metrics retrieved successfully'
        })
        
    except Exception as e:
        logger.error(f"Error in live dashboard API: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve dashboard metrics',
            'message': str(e)
        }), 500


@analytics_live_bp.route('/insights-feed', methods=['GET'])
def get_insights_feed():
    """
    Get real-time insights feed from recent survey responses
    
    Query Parameters:
        limit: Maximum number of insights to return (default: 50)
    
    Returns:
        JSON with recent response insights and text analytics
    """
    try:
        limit = int(request.args.get('limit', 50))
        
        # Validate limit parameter
        if limit < 1 or limit > 200:
            return jsonify({
                'error': 'Limit must be between 1 and 200'
            }), 400
        
        # Get insights feed
        insights = analytics_processor.get_insights_feed(limit)
        
        return jsonify({
            'success': True,
            'data': insights,
            'count': len(insights),
            'message': 'Insights feed retrieved successfully'
        })
        
    except ValueError:
        return jsonify({
            'error': 'Invalid limit parameter - must be a number'
        }), 400
    except Exception as e:
        logger.error(f"Error in insights feed API: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve insights feed',
            'message': str(e)
        }), 500


@analytics_live_bp.route('/trending-topics', methods=['GET'])
def get_trending_topics():
    """
    Get trending topics from text analytics of recent responses
    
    Query Parameters:
        time_range: "1d", "7d", "30d", "all" (default: "7d")
        limit: Maximum number of topics to return (default: 10)
    
    Returns:
        JSON with trending topics, frequency, and sentiment data
    """
    try:
        time_range = request.args.get('time_range', '7d')
        limit = int(request.args.get('limit', 10))
        
        # Validate parameters
        valid_ranges = ['1d', '7d', '30d', 'all']
        if time_range not in valid_ranges:
            return jsonify({
                'error': 'Invalid time_range parameter',
                'valid_options': valid_ranges
            }), 400
        
        if limit < 1 or limit > 50:
            return jsonify({
                'error': 'Limit must be between 1 and 50'
            }), 400
        
        # Get trending topics
        topics = analytics_processor.get_trending_topics(time_range, limit)
        
        return jsonify({
            'success': True,
            'data': topics,
            'count': len(topics),
            'time_range': time_range,
            'message': 'Trending topics retrieved successfully'
        })
        
    except ValueError:
        return jsonify({
            'error': 'Invalid limit parameter - must be a number'
        }), 400
    except Exception as e:
        logger.error(f"Error in trending topics API: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve trending topics',
            'message': str(e)
        }), 500


@analytics_live_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for analytics service
    
    Returns:
        JSON with service status and basic metrics
    """
    try:
        # Test basic functionality
        metrics = analytics_processor.get_dashboard_metrics("1d")
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'service': 'live-analytics',
            'last_updated': metrics.get('last_updated'),
            'message': 'Analytics service is operational'
        })
        
    except Exception as e:
        logger.error(f"Analytics health check failed: {e}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'service': 'live-analytics',
            'error': str(e),
            'message': 'Analytics service is experiencing issues'
        }), 500


@analytics_live_bp.route('/summary', methods=['GET'])
def get_analytics_summary():
    """
    Get summarized analytics data for quick overview
    
    Returns:
        JSON with key metrics summary
    """
    try:
        # Get data for multiple time ranges
        today_metrics = analytics_processor.get_dashboard_metrics("1d")
        week_metrics = analytics_processor.get_dashboard_metrics("7d")
        
        # Get recent insights
        recent_insights = analytics_processor.get_insights_feed(10)
        
        # Get top trending topics
        trending_topics = analytics_processor.get_trending_topics("7d", 5)
        
        summary = {
            "today": {
                "responses": today_metrics["responses"]["total"],
                "csat": today_metrics["csat"]["score"],
                "completion_rate": today_metrics["completion"]["rate"]
            },
            "this_week": {
                "responses": week_metrics["responses"]["total"],
                "csat": week_metrics["csat"]["score"],
                "completion_rate": week_metrics["completion"]["rate"]
            },
            "recent_activity": {
                "latest_responses": len(recent_insights),
                "trending_topics_count": len(trending_topics),
                "top_sentiment": week_metrics["sentiment"]["distribution"]
            },
            "top_topics": [topic["topic"] for topic in trending_topics[:3]],
            "last_updated": week_metrics["last_updated"]
        }
        
        return jsonify({
            'success': True,
            'data': summary,
            'message': 'Analytics summary retrieved successfully'
        })
        
    except Exception as e:
        logger.error(f"Error in analytics summary API: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve analytics summary',
            'message': str(e)
        }), 500