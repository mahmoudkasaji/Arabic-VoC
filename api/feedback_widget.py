"""
Feedback Widget API
Handles persistent feedback widget submissions across all pages
"""

from flask import Blueprint, request, jsonify, session
from flask_login import current_user, login_required
from datetime import datetime
import json
import uuid
from core.app import db
from core.models_unified import Feedback
from utils.simple_arabic_analyzer import SimpleArabicAnalyzer

feedback_widget_api = Blueprint('feedback_widget_api', __name__)

@feedback_widget_api.route('/api/feedback-widget', methods=['POST'])
@login_required
def submit_widget_feedback():
    """Submit feedback from the persistent widget"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('rating') or not data.get('category'):
            return jsonify({
                'success': False,
                'error': 'Rating and category are required'
            }), 400
        
        # Extract feedback data
        rating = int(data.get('rating', 0))
        category = data.get('category', '')
        comment = data.get('comment', '').strip()
        page_url = data.get('page_url', '')
        page_title = data.get('page_title', '')
        user_agent = data.get('user_agent', '')
        language = data.get('language', 'ar')
        
        # Validate rating range
        if not 1 <= rating <= 5:
            return jsonify({
                'success': False,
                'error': 'Rating must be between 1 and 5'
            }), 400
        
        # Process comment with AI if provided
        ai_analysis = None
        if comment:
            try:
                analyzer = SimpleArabicAnalyzer()
                import asyncio
                ai_analysis = asyncio.run(analyzer.analyze_feedback(comment))
            except Exception as e:
                print(f"AI analysis failed: {e}")
                # Continue without AI analysis
        
        # Create feedback entry using the correct model fields
        feedback = Feedback(
            content=comment,
            processed_content=comment,
            channel='widget',
            rating=rating,
            customer_id=str(current_user.id),
            ai_summary=ai_analysis.get('summary', '') if ai_analysis else None,
            ai_categories=ai_analysis.get('categories', []) if ai_analysis else None,
            sentiment_score=ai_analysis.get('sentiment_score', 0.0) if ai_analysis else None,
            confidence_score=ai_analysis.get('confidence_score', 0.0) if ai_analysis else None,
            channel_metadata={
                'page_url': page_url,
                'page_title': page_title,
                'user_agent': user_agent,
                'language': language,
                'widget_version': '2.0',
                'source_type': 'FOOTER_WIDGET',
                'category': category
            },
            language_detected=language,
            created_at=datetime.utcnow(),
            status='processed'
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        # Log successful submission
        print(f"Widget feedback submitted: {feedback.id} by user {current_user.id}")
        
        return jsonify({
            'success': True,
            'feedback_id': feedback.id,
            'message': 'تم إرسال ملاحظتك بنجاح' if language == 'ar' else 'Feedback submitted successfully'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid data format'
        }), 400
        
    except Exception as e:
        print(f"Error submitting widget feedback: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@feedback_widget_api.route('/api/feedback-widget/stats', methods=['GET'])
@login_required
def get_widget_stats():
    """Get widget feedback statistics for analytics"""
    try:
        # Get feedback from widget channel
        widget_feedback = Feedback.query.filter_by(
            channel='widget',
            user_id=current_user.id
        ).all()
        
        # Calculate statistics
        total_submissions = len(widget_feedback)
        avg_rating = sum(f.rating for f in widget_feedback if f.rating) / total_submissions if total_submissions > 0 else 0
        
        # Category breakdown
        categories = {}
        for feedback in widget_feedback:
            cat = feedback.category or 'أخرى'
            categories[cat] = categories.get(cat, 0) + 1
        
        # Recent submissions (last 7 days)
        from datetime import timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_count = len([f for f in widget_feedback if f.created_at >= week_ago])
        
        return jsonify({
            'success': True,
            'stats': {
                'total_submissions': total_submissions,
                'average_rating': round(avg_rating, 1),
                'categories': categories,
                'recent_submissions': recent_count,
                'last_submission': widget_feedback[-1].created_at.isoformat() if widget_feedback else None
            }
        })
        
    except Exception as e:
        print(f"Error getting widget stats: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve statistics'
        }), 500

@feedback_widget_api.route('/api/feedback-widget/config', methods=['GET'])
def get_widget_config():
    """Get widget configuration based on user preferences"""
    try:
        # Get user language preference
        language = 'ar'  # Default
        if current_user.is_authenticated:
            from models.replit_user_preferences import ReplitUserPreferences
            prefs = ReplitUserPreferences.query.filter_by(user_id=current_user.id).first()
            if prefs:
                language = prefs.language
        
        # Define categories based on language
        categories = {
            'ar': [
                'تحسين المنتج',
                'مشكلة تقنية', 
                'اقتراح ميزة',
                'سهولة الاستخدام',
                'الأداء',
                'أخرى'
            ],
            'en': [
                'Product Improvement',
                'Technical Issue',
                'Feature Request', 
                'Usability',
                'Performance',
                'Other'
            ]
        }
        
        return jsonify({
            'success': True,
            'config': {
                'language': language,
                'categories': categories.get(language, categories['ar']),
                'position': 'bottom-left' if language == 'ar' else 'bottom-right',
                'enabled': True
            }
        })
        
    except Exception as e:
        print(f"Error getting widget config: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve configuration'
        }), 500