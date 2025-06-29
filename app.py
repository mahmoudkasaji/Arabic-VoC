"""
Flask Arabic Voice of Customer Platform
Main application with proper Arabic support and WSGI compatibility
"""

import os
import logging
from datetime import datetime, timedelta
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
    """Redirect to executive dashboard (replaces old real-time dashboard)"""
    return redirect(url_for('executive_dashboard_page'))

@app.route('/surveys')
def surveys_page():
    """Survey management page"""
    return render_template('surveys.html',
                         title='إدارة الاستطلاعات')



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

# Updated navigation routes - Surveys
@app.route('/surveys/create')
@app.route('/surveys/builder')  # Keep old route for compatibility
@app.route('/survey-builder')  # Keep old route for compatibility
def survey_create_page():
    """Survey creation page with templates"""
    return render_template('survey_builder.html', 
                         title='إنشاء استطلاع جديد')

@app.route('/surveys/manage')
def surveys_manage_page():
    """Survey management page"""
    return render_template('surveys.html', 
                         title='إدارة الاستطلاعات')

@app.route('/surveys/distribution-demo')
def survey_distribution_demo():
    """MVP Survey distribution system"""
    return render_template('survey_delivery_mvp.html', 
                         title='توزيع الاستطلاعات')

@app.route('/surveys/access')
def survey_distribution_access():
    """Quick access page for survey distribution system"""
    return render_template('survey_distribution_access.html',
                         title='الوصول لنظام التوزيع')

@app.route('/surveys/responses')
def survey_responses_page():
    """Survey responses management page"""
    return render_template('survey_responses.html', 
                         title='الردود والنتائج')

# Updated navigation routes - Dashboards
@app.route('/dashboards/executive')
@app.route('/executive-dashboard')  # Keep old route for compatibility
def dashboards_executive():
    """Executive dashboard page"""
    return render_template('executive_dashboard.html',
                         title='العرض التنفيذي')

@app.route('/dashboards/analyst')
def dashboards_analyst():
    """Analyst dashboard page"""
    return render_template('dashboards_analyst.html', 
                         title='عرض المحلل')

# Updated navigation routes - Analytics
@app.route('/analytics/insights')
def analytics_insights():
    """Real-time insights page"""
    return render_template('analytics_insights.html', 
                         title='الرؤى المباشرة')

@app.route('/analytics/reports')
def analytics_reports_page():
    """Reports and export page"""
    return render_template('analytics_reports.html', 
                         title='التقارير والتصدير')

@app.route('/analytics/ai-lab')
def analytics_ai_lab():
    """AI Testing Lab page"""
    return render_template('analytics_ai_lab.html', 
                         title='مختبر الذكاء الاصطناعي')

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

# Updated navigation routes - Settings
@app.route('/settings/users')
def settings_users_page():
    """User management page"""
    return render_template('settings_users.html', 
                         title='إدارة المستخدمين')

@app.route('/settings/system')
def settings_system_page():
    """System configuration page - includes language, AI keys, preferences"""
    return render_template('settings_system.html', 
                         title='إعدادات النظام')

# Keep old routes for compatibility
@app.route('/settings/account')
def settings_account_page():
    """Account management page - redirect to users"""
    return redirect(url_for('settings_users_page'))

@app.route('/settings/security')
def settings_security_page():
    """Security page - redirect to system"""
    return redirect(url_for('settings_system_page'))

@app.route('/settings/admin')
def settings_admin_page():
    """Admin page - redirect to users"""
    return redirect(url_for('settings_users_page'))

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

@app.route('/api/ai-services-status')
def ai_services_status():
    """Get AI services configuration status"""
    try:
        from datetime import datetime
        import os
        
        # Check API key availability
        openai_available = bool(os.environ.get('OPENAI_API_KEY'))
        anthropic_available = bool(os.environ.get('ANTHROPIC_API_KEY'))
        
        status = {
            'openai': {
                'configured': openai_available,
                'model': 'gpt-4o',
                'status': 'active' if openai_available else 'unavailable',
                'description': 'OpenAI GPT-4o - Latest multimodal model'
            },
            'anthropic': {
                'configured': anthropic_available,
                'model': 'claude-3-sonnet-20240229',
                'status': 'active' if anthropic_available else 'unavailable',
                'description': 'Anthropic Claude 3 Sonnet - Advanced reasoning'
            },
            'jais': {
                'configured': False,
                'model': 'jais-30b-chat',
                'status': 'not_configured',
                'description': 'JAIS 30B - Native Arabic language model'
            },
            'intelligent_routing': {
                'enabled': True,
                'description': 'Automatic model selection based on content complexity'
            },
            'summary': {
                'total_models': 3,
                'active_models': sum([openai_available, anthropic_available]),
                'primary_model': 'gpt-4o' if openai_available else 'claude-3-sonnet' if anthropic_available else 'none'
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error checking AI services: {e}")
        return jsonify({'error': f'AI services check failed: {str(e)}'}), 500

@app.route('/api/test-ai-analysis', methods=['POST'])
def test_ai_analysis():
    """Test CX Analysis with business-focused intelligence"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        service = data.get('service', 'auto')
        use_committee = data.get('use_committee', True)
        task_type = data.get('task_type', 'cx_analysis')
        
        if not text.strip():
            return jsonify({
                'error': 'Text is required'
            }), 400
        
        # Use new CX Analysis Engine for business intelligence
        if use_committee and task_type == 'cx_analysis':
            import asyncio
            from utils.cx_analysis_engine import CXAnalysisEngine
            
            async def run_cx_analysis():
                cx_engine = CXAnalysisEngine()
                return await cx_engine.analyze_feedback(text)
            
            # Run async analysis
            result = asyncio.run(run_cx_analysis())
            
            return jsonify({
                'status': 'success',
                'text_analyzed': text,
                'analysis': result,
                'analysis_type': 'cx_business_intelligence',
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            # Fallback to legacy system for compatibility
            from utils.api_key_manager import api_manager
            
            business_context = {
                'priority': data.get('priority', 'medium'),
                'optimize_cost': data.get('optimize_cost', False),
                'expected_volume': data.get('expected_volume', 'low')
            }
            
            analysis = api_manager.analyze_arabic_text(
                text, 
                service, 
                task_type='arabic_analysis',
                use_agent_committee=use_committee,
                business_context=business_context if use_committee else None
            )
            
            return jsonify({
                'status': 'success',
                'text_analyzed': text,
                'analysis': analysis,
                'analysis_type': 'legacy_cultural_analysis',
                'test_parameters': {
                    'use_committee': use_committee,
                    'task_type': 'arabic_analysis',
                    'business_context': business_context if use_committee else None
                },
                'timestamp': datetime.utcnow().isoformat()
            })
        
    except Exception as e:
        logger.error(f"CX analysis test failed: {str(e)}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/committee-performance')
def committee_performance():
    """Get agent committee performance metrics"""
    try:
        from datetime import datetime
        
        # Return mock performance data for demo
        metrics = {
            'total_analyses': 156,
            'success_rate': 94.2,
            'average_processing_time': 2.3,
            'agent_performance': {
                'sentiment_agent': {'accuracy': 92.5, 'avg_time': 0.8},
                'topic_agent': {'accuracy': 89.1, 'avg_time': 1.2},
                'action_agent': {'accuracy': 91.7, 'avg_time': 0.9}
            },
            'last_24h': {
                'analyses': 23,
                'success_rate': 96.1
            }
        }
        
        return jsonify({
            'status': 'success',
            'committee_metrics': metrics,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting committee performance: {e}")
        return jsonify({'error': f'Failed to get committee metrics: {str(e)}'}), 500

@app.route('/api/specialized-agents-performance', methods=['GET'])
def specialized_agents_performance():
    """Get performance metrics for specialized agents system"""
    try:
        from utils.api_key_manager import api_manager
        from utils.specialized_orchestrator import get_specialized_orchestrator
        orchestrator = get_specialized_orchestrator(api_manager)
        
        performance_metrics = orchestrator.get_performance_metrics()
        
        return jsonify({
            "status": "success",
            "performance_data": performance_metrics,
            "agent_system": "specialized_agents",
            "agents": [
                {"name": "SentimentAnalyst", "purpose": "Arabic sentiment analysis with cultural context"},
                {"name": "TopicalAnalyst", "purpose": "Business topic detection and categorization"},
                {"name": "RecommendationSpecialist", "purpose": "Actionable business recommendations"}
            ]
        })
        
    except Exception as e:
        logger.error(f"Performance metrics failed: {e}")
        return jsonify({
            "error": "Failed to get performance metrics",
            "details": str(e)
        }), 500

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

# Register survey distribution API routes
@app.route('/api/surveys/campaigns', methods=['GET'])
def get_survey_campaigns():
    """List survey campaigns"""
    try:
        return jsonify({
            'campaigns': [
                {
                    'id': 1,
                    'name': 'استطلاع رضا العملاء - يونيو 2025',
                    'status': 'active',
                    'target_count': 100,
                    'sent_count': 97,
                    'response_count': 42,
                    'response_rate': 43.3,
                    'created_at': '2025-06-23T10:00:00Z'
                }
            ],
            'pagination': {'limit': 10, 'offset': 0, 'total': 1}
        }), 200
    except Exception as e:
        logger.error(f"Campaign listing failed: {e}")
        return jsonify({'error': 'Failed to fetch campaigns'}), 500

@app.route('/api/surveys/distribute', methods=['POST'])
def distribute_survey():
    """Simulate survey distribution"""
    try:
        data = request.get_json() or {}
        return jsonify({
            'status': 'success',
            'message': 'Survey distribution simulated successfully',
            'result': {
                'campaign_id': data.get('campaign_id', 1),
                'target_audience_size': 100,
                'deliveries_created': 97,
                'distribution_status': 'initiated',
                'channels_used': ['email', 'whatsapp', 'sms']
            }
        }), 200
    except Exception as e:
        logger.error(f"Survey distribution failed: {e}")
        return jsonify({'error': 'Distribution failed'}), 500

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