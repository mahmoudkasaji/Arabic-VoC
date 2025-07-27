"""
Simplified Feedback Widget Routes
Direct form submission approach without API complexity
"""

from flask import request, jsonify, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from datetime import datetime
import json
import uuid
from app import app, db
from models_unified import Feedback
from utils.simple_arabic_analyzer import SimpleArabicAnalyzer

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
                return redirect(request.referrer or url_for('index'))
        
        # Validate rating range
        if not 1 <= rating <= 5:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': False,
                    'error': 'Rating must be between 1 and 5'
                }), 400
            else:
                flash('التقييم يجب أن يكون بين 1 و 5', 'error')
                return redirect(request.referrer or url_for('index'))
        
        # Process comment with AI if provided
        ai_analysis = None
        if comment:
            try:
                analyzer = SimpleArabicAnalyzer()
                ai_analysis = analyzer.analyze_feedback(comment)
            except Exception as e:
                print(f"AI analysis failed: {e}")
                # Continue without AI analysis
        
        # Create feedback entry
        feedback = Feedback(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            original_text=comment,
            processed_text=comment,
            channel='widget',
            source=f"Widget - {page_title}",
            rating=rating,
            category=category,
            metadata=json.dumps({
                'page_url': page_url,
                'page_title': page_title,
                'user_agent': request.headers.get('User-Agent', ''),
                'language': 'ar',  # Default to Arabic
                'widget_version': '2.0',
                'submission_type': 'persistent_widget'
            }),
            ai_analysis=json.dumps(ai_analysis) if ai_analysis else None,
            created_at=datetime.utcnow(),
            status='processed'
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        # Log successful submission
        print(f"Widget feedback submitted: {feedback.id} by user {current_user.id}")
        
        # Return appropriate response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # AJAX request
            return jsonify({
                'success': True,
                'feedback_id': feedback.id,
                'message': 'تم إرسال ملاحظتك بنجاح'
            })
        else:
            # Regular form submission
            flash('تم إرسال ملاحظتك بنجاح. شكراً لك!', 'success')
            return redirect(request.referrer or url_for('index'))
        
    except ValueError as e:
        error_msg = 'بيانات غير صحيحة'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        else:
            flash(error_msg, 'error')
            return redirect(request.referrer or url_for('index'))
        
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
            return redirect(request.referrer or url_for('index'))

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