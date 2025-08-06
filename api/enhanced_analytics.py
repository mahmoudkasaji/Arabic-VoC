"""
Enhanced Analytics API - Phase 3A
API endpoints for emotion detection and topic categorization
"""

from flask import Blueprint, jsonify, request
from typing import Dict, Any, List
import logging
import json
from datetime import datetime, timedelta
from sqlalchemy import text, and_
from core.app import db
import sys
import os
# Add the parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.enhanced_text_analytics import EnhancedTextAnalytics

logger = logging.getLogger(__name__)

# Create blueprint
enhanced_analytics_bp = Blueprint('enhanced_analytics', __name__, url_prefix='/api/enhanced-analytics')

# Initialize analyzer
analyzer = EnhancedTextAnalytics()

@enhanced_analytics_bp.route('/analyze-text', methods=['POST'])
def analyze_text():
    """
    Analyze single text input with enhanced analytics
    
    Expected JSON:
    {
        "text": "Customer feedback text",
        "context": {"optional": "context"}
    }
    """
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        context = data.get('context', {})
        
        if not text:
            return jsonify({
                'success': False,
                'error': 'Text input is required'
            }), 400
        
        # Perform enhanced analysis
        analysis = analyzer.analyze_with_emotions_and_topics(text, context)
        
        return jsonify({
            'success': True,
            'data': analysis,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in analyze_text: {e}")
        return jsonify({
            'success': False,
            'error': 'Analysis failed'
        }), 500

@enhanced_analytics_bp.route('/historical-analysis', methods=['GET'])
def get_historical_analysis():
    """
    Get enhanced analysis for historical survey responses
    
    Query parameters:
    - time_range: "1d", "7d", "30d", "all" (default: "all")
    - survey_id: specific survey ID (optional)
    - limit: number of responses to analyze (default: 10)
    """
    try:
        time_range = request.args.get('time_range', 'all')
        survey_id = request.args.get('survey_id')
        limit = int(request.args.get('limit', 10))
        
        # Build query using SQLAlchemy query builder for better security
        from core.app import db
        from models.survey import Response, Survey
        
        # Start with base query using SQLAlchemy ORM
        query = db.session.query(
            Response.id,
            Response.survey_id, 
            Response.answers,
            Response.created_at,
            Survey.title,
            Response.sentiment_score,
            Response.keywords
        ).join(Survey, Response.survey_id == Survey.id)
        
        # Add time filter
        if time_range != 'all':
            if time_range == '1d':
                start_date = datetime.now() - timedelta(days=1)
            elif time_range == '7d':
                start_date = datetime.now() - timedelta(days=7)
            elif time_range == '30d':
                start_date = datetime.now() - timedelta(days=30)
            else:
                start_date = datetime.now() - timedelta(days=7)  # Default
            
            query = query.filter(Response.created_at >= start_date)
        
        # Add survey filter
        if survey_id:
            query = query.filter(Response.survey_id == survey_id)
        
        # Add ordering and limit
        query = query.order_by(Response.created_at.desc()).limit(limit)
        
        # Execute query
        result = query.all()
        
        responses = []
        for row in result:
            responses.append({
                'id': row.id,
                'survey_id': row.survey_id,
                'answers': row.answers,
                'created_at': row.created_at.isoformat() if row.created_at else None,
                'survey_title': row.title,
                'existing_sentiment': row.sentiment_score,
                'existing_keywords': row.keywords
            })
        
        if not responses:
            return jsonify({
                'success': True,
                'data': {
                    'total_responses': 0,
                    'analyzed_responses': [],
                    'summary': {
                        'emotion_distribution': {},
                        'topic_distribution': {},
                        'sentiment_comparison': {}
                    }
                }
            })
        
        # Process responses with enhanced analytics
        analyzed_responses = analyzer.process_historical_responses(responses)
        
        # Generate summary statistics
        summary = _generate_analysis_summary(analyzed_responses)
        
        return jsonify({
            'success': True,
            'data': {
                'total_responses': len(responses),
                'analyzed_responses': analyzed_responses,
                'summary': summary,
                'filters_applied': {
                    'time_range': time_range,
                    'survey_id': survey_id,
                    'limit': limit
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error in historical_analysis: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to analyze historical data'
        }), 500

@enhanced_analytics_bp.route('/emotion-trends', methods=['GET'])
def get_emotion_trends():
    """
    Get emotion trends over time from enhanced analytics
    
    Query parameters:
    - days: number of days to look back (default: 7)
    - survey_id: specific survey ID (optional)
    """
    try:
        days = int(request.args.get('days', 7))
        survey_id = request.args.get('survey_id')
        
        # For now, use sample data since we need to build emotion history
        # In production, this would query a table with stored enhanced analysis results
        
        emotion_trends = {
            'time_series': [
                {
                    'date': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'),
                    'emotions': {
                        'سعادة': max(0, 0.3 + (i * 0.1)),
                        'رضا': max(0, 0.4 - (i * 0.05)),
                        'إحباط': max(0, 0.2 + (i * 0.03)),
                        'قلق': max(0, 0.1 + (i * 0.02))
                    }
                }
                for i in range(days)
            ],
            'summary': {
                'dominant_emotion': 'رضا',
                'trend_direction': 'improving',
                'confidence': 0.75
            }
        }
        
        return jsonify({
            'success': True,
            'data': emotion_trends
        })
        
    except Exception as e:
        logger.error(f"Error in emotion_trends: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get emotion trends'
        }), 500

@enhanced_analytics_bp.route('/topic-insights', methods=['GET'])
def get_topic_insights():
    """
    Get business topic insights from enhanced analytics
    
    Query parameters:
    - time_range: "1d", "7d", "30d", "all" (default: "7d")
    - min_relevance: minimum relevance score (default: 0.3)
    """
    try:
        time_range = request.args.get('time_range', '7d')
        min_relevance_str = request.args.get('min_relevance', '0.3')
        
        # Validate min_relevance input to prevent NaN injection
        if min_relevance_str.lower() in ('nan', '+nan', '-nan'):
            return jsonify({
                'success': False,
                'error': 'Invalid min_relevance value'
            }), 400
        
        try:
            min_relevance = float(min_relevance_str)
            # Additional validation: ensure it's a valid number and within reasonable bounds
            if not (0.0 <= min_relevance <= 1.0):
                return jsonify({
                    'success': False,
                    'error': 'min_relevance must be between 0.0 and 1.0'
                }), 400
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'min_relevance must be a valid number'
            }), 400
        
        # Get historical analysis directly by calling the internal function
        try:
            analysis_response = get_historical_analysis()
            # Check if it's a tuple (response, status_code) or just a response
            if isinstance(analysis_response, tuple):
                response_data = analysis_response[0].get_json()
            else:
                response_data = analysis_response.get_json()
            
            if not response_data.get('success'):
                return jsonify({
                    'success': False,
                    'error': 'Failed to get historical data'
                }), 500
                
            analyzed_data = response_data['data']
        except Exception as e:
            logger.error(f"Error getting historical analysis: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to retrieve historical data'
            }), 500
        analyzed_responses = analyzed_data.get('analyzed_responses', [])
        
        # Extract topic insights
        topic_insights = {}
        
        for response in analyzed_responses:
            topics = response.get('topics', [])
            for topic in topics:
                relevance = topic.get('relevance', 0)
                if relevance >= min_relevance:
                    category = topic.get('category', 'unknown')
                    
                    if category not in topic_insights:
                        topic_insights[category] = {
                            'total_mentions': 0,
                            'avg_relevance': 0,
                            'keywords': set(),
                            'responses': []
                        }
                    
                    topic_insights[category]['total_mentions'] += 1
                    topic_insights[category]['avg_relevance'] += relevance
                    topic_insights[category]['keywords'].update(topic.get('keywords', []))
                    topic_insights[category]['responses'].append(response.get('response_id'))
        
        # Calculate averages and convert sets to lists
        for category, data in topic_insights.items():
            if data['total_mentions'] > 0:
                data['avg_relevance'] = round(data['avg_relevance'] / data['total_mentions'], 2)
            data['keywords'] = list(data['keywords'])
        
        # Sort by relevance
        sorted_topics = sorted(
            topic_insights.items(), 
            key=lambda x: x[1]['avg_relevance'], 
            reverse=True
        )
        
        return jsonify({
            'success': True,
            'data': {
                'topic_insights': dict(sorted_topics),
                'filters_applied': {
                    'time_range': time_range,
                    'min_relevance': min_relevance
                },
                'total_categories': len(topic_insights),
                'total_responses_analyzed': len(analyzed_responses)
            }
        })
        
    except Exception as e:
        logger.error(f"Error in topic_insights: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get topic insights'
        }), 500

def _generate_analysis_summary(analyzed_responses: List[Dict]) -> Dict[str, Any]:
    """Generate summary statistics from analyzed responses"""
    if not analyzed_responses:
        return {
            'emotion_distribution': {},
            'topic_distribution': {},
            'sentiment_comparison': {}
        }
    
    # Emotion distribution
    emotion_counts = {}
    topic_counts = {}
    sentiment_scores = []
    
    for response in analyzed_responses:
        # Count primary emotions
        primary_emotion = response.get('primary_emotion', {}).get('emotion')
        if primary_emotion:
            emotion_counts[primary_emotion] = emotion_counts.get(primary_emotion, 0) + 1
        
        # Count topics
        topics = response.get('topics', [])
        for topic in topics:
            category = topic.get('category')
            if category:
                topic_counts[category] = topic_counts.get(category, 0) + 1
        
        # Collect sentiment scores
        sentiment = response.get('sentiment', {}).get('score')
        if sentiment is not None:
            sentiment_scores.append(sentiment)
    
    # Calculate averages
    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
    
    return {
        'emotion_distribution': emotion_counts,
        'topic_distribution': topic_counts,
        'sentiment_comparison': {
            'average_sentiment': round(avg_sentiment, 2),
            'total_responses': len(analyzed_responses),
            'sentiment_range': {
                'min': min(sentiment_scores) if sentiment_scores else 0,
                'max': max(sentiment_scores) if sentiment_scores else 0
            }
        }
    }