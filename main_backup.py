"""
Flask Arabic Voice of Customer Platform
Main application with proper Arabic support and WSGI compatibility
"""

import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging for Arabic text
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Import configuration
from config import get_config

# Create Flask app
app = Flask(__name__)

# Load environment-specific configuration
config_class = get_config()
app.config.from_object(config_class)

# Configure proxy fix for Replit
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize database
db.init_app(app)

# Import models after db initialization
from models_unified import Feedback, FeedbackChannel, FeedbackStatus

# Import and register survey blueprint
from api.surveys_flask import surveys_bp
app.register_blueprint(surveys_bp)
from models.survey import Survey, Question, SurveyStatus, QuestionType

# Import survey management API
import api.survey_management

# Register executive dashboard API blueprint
from api.executive_dashboard import executive_bp
app.register_blueprint(executive_bp, url_prefix='/api/executive-dashboard')

@app.route('/')
def index():
    """Main Arabic dashboard page"""
    return render_template('index.html', 
                         lang='ar', 
                         dir='rtl',
                         title='منصة صوت العميل العربية')

@app.route('/feedback')
def feedback_page():
    """Feedback submission page"""
    return render_template('feedback.html', 
                         title='إرسال تعليق',
                         channels=list(FeedbackChannel))

@app.route('/api/feedback/submit', methods=['POST'])
def submit_feedback():
    """Submit new feedback"""
    try:
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({'error': 'Missing feedback content'}), 400
            
        content = data.get('content', '').strip()
        if not content:
            return jsonify({'error': 'Feedback content cannot be empty'}), 400
            
        channel = data.get('channel', 'website')
        if channel not in [c.value for c in FeedbackChannel]:
            channel = 'website'
            
        # Create feedback record
        feedback = Feedback(
            content=content,
            channel=FeedbackChannel(channel),
            status=FeedbackStatus.PENDING,
            customer_email=data.get('customer_email'),
            customer_phone=data.get('customer_phone'),
            rating=data.get('rating'),
            language_detected='ar'
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم إرسال التعليق بنجاح',
            'feedback_id': feedback.id
        })
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        db.session.rollback()
        return jsonify({'error': 'حدث خطأ في إرسال التعليق'}), 500

@app.route('/api/feedback/list')
def list_feedback():
    """Get feedback list"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        feedback_query = db.session.query(Feedback).order_by(Feedback.created_at.desc())
        feedback_paginated = db.paginate(
            feedback_query, page=page, per_page=per_page, error_out=False
        )
        
        feedback_list = []
        for feedback in feedback_paginated.items:
            feedback_list.append({
                'id': feedback.id,
                'content': feedback.content[:100] + '...' if len(feedback.content) > 100 else feedback.content,
                'channel': feedback.channel.value,
                'status': feedback.status.value,
                'rating': feedback.rating,
                'sentiment_score': feedback.sentiment_score,
                'created_at': feedback.created_at.isoformat() if feedback.created_at else None
            })
        
        return jsonify({
            'feedback': feedback_list,
            'total': feedback_paginated.total,
            'pages': feedback_paginated.pages,
            'current_page': page
        })
        
    except Exception as e:
        logger.error(f"Error listing feedback: {e}")
        return jsonify({'error': 'حدث خطأ في جلب التعليقات'}), 500

@app.route('/dashboard/realtime')
def realtime_dashboard():
    """Real-time analytics dashboard"""
    return render_template('dashboard_realtime.html', 
                         title='لوحة التحليلات المباشرة')

@app.route('/surveys')
def surveys_page():
    """Survey management page"""
    return render_template('surveys_modern.html', 
                         title='Survey Builder')



@app.route('/analytics')
def analytics_page():
    """Redirect analytics to executive dashboard"""
    return redirect(url_for('executive_dashboard_page'))

@app.route('/analytics/executive')
@app.route('/executive-dashboard')
def executive_dashboard_page():
    """Executive dashboard page"""
    return render_template('executive_dashboard.html',
                         title='لوحة القيادة التنفيذية')

# New navigation routes
@app.route('/surveys/builder')
@app.route('/survey-builder')  # Keep old route for compatibility
def survey_builder_new():
    """Survey builder page"""
    return render_template('survey_builder.html', 
                         title='منشئ الاستطلاعات')

@app.route('/surveys/feedback')
@app.route('/feedback')  # Keep old route for compatibility  
def feedback_new():
    """Feedback submission page"""
    return render_template('feedback.html', 
                         title='إرسال تعليق',
                         channels=list(FeedbackChannel))

@app.route('/surveys/manage')
def surveys_manage_page():
    """Survey management page"""
    return render_template('surveys.html', 
                         title='إدارة الاستطلاعات')

@app.route('/surveys/responses')
def survey_responses_page():
    """Survey responses management page"""
    return render_template('survey_responses.html', 
                         title='إدارة الردود')

@app.route('/analytics/detailed')
def analytics_detailed_page():
    """Detailed analytics page"""
    return render_template('analytics_detailed.html', 
                         title='التحليلات التفصيلية')

@app.route('/analytics/arabic')
def analytics_arabic_page():
    """Arabic-specific insights page"""
    return render_template('analytics_arabic.html', 
                         title='الرؤى العربية')

@app.route('/analytics/reports')
def analytics_reports_page():
    """Reports and export page"""
    return render_template('analytics_reports.html', 
                         title='التقارير والتصدير')

@app.route('/integrations')
def integrations_redirect():
    """Redirect to data sources by default"""
    return redirect(url_for('integrations_sources_page'))

@app.route('/integrations/sources')
def integrations_sources_page():
    """Data sources catalog page"""
    return render_template('integrations_sources.html', 
                         title='مصادر البيانات')

@app.route('/integrations/destinations')
def integrations_destinations_page():
    """Data destinations catalog page"""
    return render_template('integrations_destinations.html', 
                         title='وجهات البيانات')

@app.route('/integrations/ai')
def integrations_ai_page():
    """AI & LLM management page"""
    return render_template('integrations_ai.html', 
                         title='إدارة الذكاء الاصطناعي')

@app.route('/settings/account')
def settings_account_page():
    """Account management page"""
    return render_template('settings_account.html', 
                         title='إدارة الحساب')

@app.route('/settings/system')
def settings_system_page():
    """System configuration page"""
    return render_template('settings_system.html', 
                         title='إعدادات النظام')

@app.route('/settings/security')
def settings_security_page():
    """Security and privacy page"""
    return render_template('settings_security.html', 
                         title='الأمان والخصوصية')

@app.route('/settings/admin')
def settings_admin_page():
    """Platform administration page"""
    return render_template('settings_admin.html', 
                         title='إدارة المنصة')

@app.route('/login')
def login_page():
    """Login page"""
    return render_template('login.html', 
                         title='تسجيل الدخول')

@app.route('/register')
def register_page():
    """Registration page"""
    return render_template('register.html', 
                         title='إنشاء حساب')

@app.route('/api/dashboard/metrics')
def dashboard_metrics():
    """Dashboard metrics API"""
    try:
        # Get basic metrics
        total_feedback = db.session.query(Feedback).count()
        processed_feedback = db.session.query(Feedback).filter_by(status=FeedbackStatus.PROCESSED).count()
        pending_feedback = db.session.query(Feedback).filter_by(status=FeedbackStatus.PENDING).count()
        
        # Calculate average sentiment
        avg_sentiment = db.session.query(
            db.func.avg(Feedback.sentiment_score)
        ).filter(Feedback.sentiment_score.isnot(None)).scalar() or 0.0
        
        # Channel breakdown
        channel_stats = db.session.query(
            Feedback.channel,
            db.func.count(Feedback.id).label('count')
        ).group_by(Feedback.channel).all()
        
        channel_metrics = []
        for channel, count in channel_stats:
            channel_metrics.append({
                'channel': channel.value,
                'count': count,
                'percentage': round((count / total_feedback * 100) if total_feedback > 0 else 0, 1)
            })
        
        return jsonify({
            'total_feedback': total_feedback,
            'processed_feedback': processed_feedback,
            'pending_feedback': pending_feedback,
            'average_sentiment': round(avg_sentiment, 2),
            'channel_metrics': channel_metrics,
            'sentiment_distribution': {
                'positive': processed_feedback // 3,  # Mock data for now
                'neutral': processed_feedback // 3,
                'negative': processed_feedback // 3
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}")
        return jsonify({'error': 'حدث خطأ في جلب البيانات'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'arabic_support': 'enabled'
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

# Initialize database tables
with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")

if __name__ == '__main__':
    # Configure for Arabic text
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)