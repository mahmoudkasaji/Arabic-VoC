"""
Unified Survey Management API
Combines survey management and distribution into a single interface
"""

from flask import Blueprint, jsonify, request, current_app
from app import db
from models.survey_flask import SurveyFlask
from models.survey_campaigns import SurveyCampaign, DistributionMethod
from models_unified import Contact
from sqlalchemy import text, func
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

surveys_unified_bp = Blueprint('surveys_unified', __name__, url_prefix='/api/surveys')

@surveys_unified_bp.route('/dashboard-stats')
def get_dashboard_stats():
    """Get unified dashboard statistics for survey management"""
    try:
        # Basic survey counts
        total_surveys = SurveyFlask.query.count()
        active_surveys = SurveyFlask.query.filter_by(status='published').count()
        draft_surveys = SurveyFlask.query.filter_by(status='draft').count()
        
        # Response counts from survey responses
        total_responses = db.session.query(func.sum(SurveyFlask.response_count)).scalar() or 0
        
        # Campaign statistics
        total_campaigns = SurveyCampaign.query.count()
        active_campaigns = SurveyCampaign.query.filter_by(status='active').count()
        
        # Recent activity (last 7 days)
        recent_date = datetime.now() - timedelta(days=7)
        recent_surveys = SurveyFlask.query.filter(SurveyFlask.created_at >= recent_date).count()
        recent_responses = db.session.query(func.count()).select_from(
            text("responses WHERE created_at >= :recent_date")
        ).params(recent_date=recent_date).scalar() or 0
        
        # Calculate average completion rate
        surveys_with_responses = SurveyFlask.query.filter(SurveyFlask.response_count > 0).all()
        if surveys_with_responses:
            completion_rates = [s.response_count / max(s.view_count, 1) * 100 for s in surveys_with_responses if hasattr(s, 'view_count')]
            avg_completion_rate = sum(completion_rates) / len(completion_rates) if completion_rates else 75.0
        else:
            avg_completion_rate = 0
        
        return jsonify({
            'surveys': {
                'total': total_surveys,
                'active': active_surveys,
                'draft': draft_surveys,
                'recent': recent_surveys
            },
            'responses': {
                'total': total_responses,
                'recent': recent_responses,
                'avg_completion_rate': round(avg_completion_rate, 1)
            },
            'campaigns': {
                'total': total_campaigns,
                'active': active_campaigns
            }
        })
        
    except Exception as e:
        logger.error(f"Error loading dashboard stats: {e}")
        return jsonify({'error': str(e)}), 500

@surveys_unified_bp.route('/list')
def get_surveys_list():
    """Get enhanced survey list with distribution and performance data"""
    try:
        # Get surveys with campaign data
        surveys_query = text("""
            SELECT 
                s.*,
                COUNT(DISTINCT sc.id) as campaign_count,
                COALESCE(SUM(sc.sent_count), 0) as total_sent,
                COALESCE(SUM(sc.response_count), 0) as campaign_responses,
                MAX(sc.created_at) as last_campaign_date,
                COUNT(DISTINCT CASE WHEN sc.status = 'active' THEN sc.id END) as active_campaigns
            FROM surveys s
            LEFT JOIN survey_campaigns sc ON s.id = sc.survey_id
            GROUP BY s.id
            ORDER BY s.created_at DESC
        """)
        
        result = db.session.execute(surveys_query)
        surveys_data = []
        
        for row in result:
            # Calculate distribution status
            distribution_status = 'none'
            if row.active_campaigns > 0:
                distribution_status = 'active'
            elif row.campaign_count > 0:
                distribution_status = 'completed'
            elif row.public_url:
                distribution_status = 'ready'
            
            surveys_data.append({
                'id': row.id,
                'title': row.title,
                'description': row.description,
                'status': row.status,
                'created_at': row.created_at.isoformat() if row.created_at else None,
                'updated_at': row.updated_at.isoformat() if row.updated_at else None,
                'uuid': row.uuid,
                'short_id': row.short_id,
                'public_url': row.public_url,
                'question_count': len(row.questions) if row.questions else 0,
                'response_count': row.response_count or 0,
                'distribution': {
                    'status': distribution_status,
                    'campaign_count': row.campaign_count or 0,
                    'total_sent': row.total_sent or 0,
                    'campaign_responses': row.campaign_responses or 0,
                    'last_campaign_date': row.last_campaign_date.isoformat() if row.last_campaign_date else None,
                    'active_campaigns': row.active_campaigns or 0
                }
            })
        
        return jsonify({
            'surveys': surveys_data,
            'total_count': len(surveys_data)
        })
        
    except Exception as e:
        logger.error(f"Error loading surveys list: {e}")
        return jsonify({'error': str(e)}), 500

@surveys_unified_bp.route('/<int:survey_id>/overview')
def get_survey_overview(survey_id):
    """Get comprehensive survey overview including distribution and analytics"""
    try:
        survey = SurveyFlask.query.get_or_404(survey_id)
        
        # Get campaign data
        campaigns = SurveyCampaign.query.filter_by(survey_id=survey_id).order_by(SurveyCampaign.created_at.desc()).all()
        active_campaigns = [c for c in campaigns if c.status == 'active']
        
        # Get recent responses
        recent_responses_query = text("""
            SELECT created_at, response_data, sentiment_score, ai_analysis
            FROM responses 
            WHERE survey_id = :survey_id 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        recent_responses = db.session.execute(
            recent_responses_query, 
            {'survey_id': survey_id}
        ).fetchall()
        
        # Calculate performance metrics
        total_sent = sum(c.sent_count for c in campaigns)
        total_campaign_responses = sum(c.response_count for c in campaigns)
        response_rate = (total_campaign_responses / total_sent * 100) if total_sent > 0 else 0
        
        return jsonify({
            'survey': {
                'id': survey.id,
                'title': survey.title,
                'description': survey.description,
                'status': survey.status,
                'created_at': survey.created_at.isoformat() if survey.created_at else None,
                'uuid': survey.uuid,
                'short_id': survey.short_id,
                'public_url': survey.public_url,
                'questions': survey.questions,
                'question_count': len(survey.questions) if survey.questions else 0,
                'response_count': survey.response_count or 0
            },
            'distribution': {
                'campaigns_count': len(campaigns),
                'active_campaigns_count': len(active_campaigns),
                'total_sent': total_sent,
                'total_responses': total_campaign_responses,
                'response_rate': round(response_rate, 2),
                'distribution_ready': bool(survey.public_url and survey.status == 'published')
            },
            'campaigns': [
                {
                    'id': c.id,
                    'name': c.name,
                    'status': c.status,
                    'channels': c.channels,
                    'sent_count': c.sent_count,
                    'response_count': c.response_count,
                    'created_at': c.created_at.isoformat() if c.created_at else None
                } for c in campaigns
            ],
            'recent_responses': [
                {
                    'created_at': r.created_at.isoformat() if r.created_at else None,
                    'preview': str(r.response_data)[:100] + '...' if r.response_data else '',
                    'sentiment_score': r.sentiment_score,
                    'has_analysis': bool(r.ai_analysis)
                } for r in recent_responses
            ]
        })
        
    except Exception as e:
        logger.error(f"Error loading survey overview: {e}")
        return jsonify({'error': str(e)}), 500

@surveys_unified_bp.route('/<int:survey_id>/quick-share')
def get_quick_share_options(survey_id):
    """Get quick sharing options for survey"""
    try:
        survey = SurveyFlask.query.get_or_404(survey_id)
        
        if not survey.public_url:
            return jsonify({'error': 'Survey not published or missing public URL'}), 400
        
        # Generate QR code URL
        qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={survey.public_url}"
        
        # Generate embeddable widget code
        widget_code = f'''<iframe src="{survey.public_url}?embedded=true" 
                         width="100%" height="600" frameborder="0"
                         title="{survey.title}">
                      </iframe>'''
        
        return jsonify({
            'survey_url': survey.public_url,
            'short_url': f"{request.host_url}s/{survey.short_id}" if survey.short_id else None,
            'qr_code_url': qr_code_url,
            'widget_code': widget_code,
            'sharing_ready': survey.status == 'published'
        })
        
    except Exception as e:
        logger.error(f"Error getting quick share options: {e}")
        return jsonify({'error': str(e)}), 500

@surveys_unified_bp.route('/<int:survey_id>/create-campaign', methods=['POST'])
def create_campaign(survey_id):
    """Create new distribution campaign for survey"""
    try:
        data = request.get_json()
        survey = SurveyFlask.query.get_or_404(survey_id)
        
        if survey.status != 'published':
            return jsonify({'error': 'Survey must be published to create campaigns'}), 400
        
        # Create new campaign
        campaign = SurveyCampaign(
            survey_id=survey_id,
            name=data.get('name', f"Campaign for {survey.title}"),
            description=data.get('description', ''),
            channels=data.get('channels', ['email']),
            target_audience=data.get('target_audience', {}),
            message_template=data.get('message_template', ''),
            status='draft',
            created_at=datetime.now()
        )
        
        db.session.add(campaign)
        db.session.commit()
        
        return jsonify({
            'campaign_id': campaign.id,
            'message': 'Campaign created successfully',
            'status': 'draft'
        })
        
    except Exception as e:
        logger.error(f"Error creating campaign: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@surveys_unified_bp.route('/<int:survey_id>/pause', methods=['POST'])
def pause_survey(survey_id):
    """Pause survey and all active campaigns"""
    try:
        survey = SurveyFlask.query.get_or_404(survey_id)
        
        # Pause survey
        survey.status = 'paused'
        
        # Pause all active campaigns
        active_campaigns = SurveyCampaign.query.filter_by(survey_id=survey_id, status='active').all()
        for campaign in active_campaigns:
            campaign.status = 'paused'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Survey and campaigns paused successfully',
            'paused_campaigns': len(active_campaigns)
        })
        
    except Exception as e:
        logger.error(f"Error pausing survey: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@surveys_unified_bp.route('/<int:survey_id>/activate', methods=['POST'])
def activate_survey(survey_id):
    """Activate survey (resume from paused state)"""
    try:
        survey = SurveyFlask.query.get_or_404(survey_id)
        survey.status = 'published'
        db.session.commit()
        
        return jsonify({'message': 'Survey activated successfully'})
        
    except Exception as e:
        logger.error(f"Error activating survey: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500