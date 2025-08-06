"""
Simplified Feedback Widget Routes
Direct form submission approach without API complexity
"""

from flask import request, jsonify, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from datetime import datetime
import json
import uuid
from urllib.parse import urlparse
from app import app, db
from models_unified import Feedback
from utils.simple_arabic_analyzer import SimpleArabicAnalyzer

def safe_redirect_url():
    """
    Safely get referrer URL, validating it's from the same domain.
    Returns url_for('index') if referrer is invalid or external.
    """
    referrer = request.referrer
    if not referrer:
        return url_for('index')
    
    try:
        parsed_referrer = urlparse(referrer)
        parsed_host = urlparse(request.host_url)
        
        # Only allow redirects to the same netloc (domain + port)
        if parsed_referrer.netloc == parsed_host.netloc:
            return referrer
        else:
            return url_for('index')
    except Exception:
        # If parsing fails, default to safe redirect
        return url_for('index')

@app.route('/feedback-widget', methods=['POST'])
@login_required
def submit_feedback_widget():
    """Handle feedback widget form submission"""
    try:
        # Get form data
        rating = request.form.get('rating', type=int)
        category = request.form.get('category', '')
        comment = request.form.get('comment', '').strip()
        page_url = request.form.get('page_url', '')
        page_title = request.form.get('page_title', '')
        
        # Validate required fields
        if not rating or not category:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': False,
                    'error': 'Rating and category are required'
                }), 400
            else:
                flash('يرجى تحديد التقييم والفئة', 'error')
                return redirect(safe_redirect_url())
        
        # Validate rating range
        if not 1 <= rating <= 5:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': False,
                    'error': 'Rating must be between 1 and 5'
                }), 400
            else:
                flash('التقييم يجب أن يكون بين 1 و 5', 'error')
                return redirect(safe_redirect_url())
        
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
                'user_agent': request.headers.get('User-Agent', ''),
                'language': 'ar',
                'source_type': 'SIDEBAR_WIDGET',
                'widget_version': '2.0',
                'category': category
            },
            language_detected='ar',
            created_at=datetime.utcnow(),
            status='processed'
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        # Log successful submission
        print(f"Widget feedback submitted: {feedback.id} by user {current_user.id}")
        
        # Return appropriate response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.form.get('ajax') == 'true':
            # AJAX request - return JSON success
            return jsonify({
                'success': True,
                'feedback_id': feedback.id,
                'message': 'تم إرسال ملاحظتك بنجاح'
            })
        else:
            # Regular form submission - redirect back
            flash('تم إرسال ملاحظتك بنجاح. شكراً لك!', 'success')
            return redirect(safe_redirect_url())
        
    except ValueError as e:
        error_msg = 'بيانات غير صحيحة'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        else:
            flash(error_msg, 'error')
            return redirect(safe_redirect_url())
        
    except Exception as e:
        print(f"Error submitting widget feedback: {e}")
        db.session.rollback()
        error_msg = 'حدث خطأ في إرسال الملاحظة'
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'error': error_msg
            }), 500
        else:
            flash(error_msg, 'error')
            return redirect(safe_redirect_url())

@app.route('/feedback-widget/config')
def get_feedback_widget_config():
    """Get widget configuration (public endpoint for JavaScript)"""
    try:
        # Default configuration
        config = {
            'categories': [
                'تحسين المنتج',
                'مشكلة تقنية', 
                'اقتراح ميزة',
                'سهولة الاستخدام',
                'الأداء',
                'أخرى'
            ],
            'language': 'ar',
            'position': 'bottom-left',  # RTL default
            'enabled': True
        }
        
        # Adjust for authenticated users
        if current_user.is_authenticated:
            try:
                from models.replit_user_preferences import ReplitUserPreferences
                prefs = ReplitUserPreferences.query.filter_by(user_id=current_user.id).first()
                if prefs and hasattr(prefs, 'language_preference'):
                    if prefs.language_preference == 'en':
                        config['language'] = 'en'
                        config['position'] = 'bottom-right'
                        config['categories'] = [
                            'Product Improvement',
                            'Technical Issue',
                            'Feature Request', 
                            'Usability',
                            'Performance',
                            'Other'
                        ]
            except Exception as e:
                print(f"Error getting user preferences: {e}")
                # Use defaults
        
        return jsonify({
            'success': True,
            'config': config
        })
        
    except Exception as e:
        print(f"Error getting widget config: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve configuration'
        }), 500