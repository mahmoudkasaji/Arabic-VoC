"""
Survey Hosting API for Email-to-Web Integration
Simple API for creating and managing web-hosted surveys
"""

import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from app import db
from models.survey_flask import SurveyFlask, QuestionFlask, SurveyStatus, QuestionType
from utils.delivery_utils import send_email_invitation

logger = logging.getLogger(__name__)

# Create blueprint for survey hosting API
survey_hosting_bp = Blueprint('survey_hosting', __name__, url_prefix='/api/survey-hosting')

@survey_hosting_bp.route('/create-simple', methods=['POST'])
def create_simple_survey():
    """Create a simple survey for email delivery testing"""
    try:
        data = request.get_json()
        
        # Create survey
        survey = SurveyFlask(
            title=data.get('title', 'مسح رضا العملاء'),
            title_ar=data.get('title_ar', 'مسح رضا العملاء'),
            description=data.get('description', 'نود معرفة رأيكم في خدماتنا'),
            description_ar=data.get('description_ar', 'نود معرفة رأيكم في خدماتنا'),
            status=SurveyStatus.PUBLISHED.value,
            is_public=True,
            allow_anonymous=True,
            primary_language='ar',
            created_by='system',  # Temporary - should be current user
            welcome_message_ar='مرحباً بكم في استطلاع رأي العملاء',
            thank_you_message_ar='شكراً لك على وقتك الثمين ومشاركتك معنا'
        )
        
        # Generate short ID for easy sharing
        survey.generate_short_id()
        
        db.session.add(survey)
        db.session.flush()  # Get survey ID
        
        # Add default questions
        questions_data = [
            {
                'text': 'How would you rate our service?',
                'text_ar': 'كيف تقيم خدماتنا؟',
                'type': QuestionType.RATING.value,
                'is_required': True,
                'min_value': 1,
                'max_value': 5,
                'order_index': 1
            },
            {
                'text': 'What can we improve?',
                'text_ar': 'ما الذي يمكننا تحسينه؟',
                'type': QuestionType.TEXTAREA.value,
                'is_required': False,
                'order_index': 2
            },
            {
                'text': 'Would you recommend us to others?',
                'text_ar': 'هل توصي بخدماتنا للآخرين؟',
                'type': QuestionType.NPS.value,
                'is_required': True,
                'order_index': 3
            }
        ]
        
        for q_data in questions_data:
            question = QuestionFlask(
                survey_id=survey.id,
                text=q_data['text'],
                text_ar=q_data['text_ar'],
                type=q_data['type'],
                is_required=q_data['is_required'],
                order_index=q_data['order_index'],
                min_value=q_data.get('min_value'),
                max_value=q_data.get('max_value')
            )
            db.session.add(question)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Survey created successfully',
            'survey': {
                'id': survey.id,
                'uuid': survey.uuid,
                'short_id': survey.short_id,
                'title': survey.display_title,
                'public_url': survey.public_url,
                'full_url': f'/survey/{survey.uuid}',
                'short_url': f'/s/{survey.short_id}' if survey.short_id else None,
                'status': survey.status,
                'questions_count': len(questions_data)
            }
        })
        
    except Exception as e:
        logger.error(f"Error creating simple survey: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Failed to create survey'
        }), 500

@survey_hosting_bp.route('/test-email-delivery', methods=['POST'])
def test_email_delivery():
    """Test complete email-to-survey workflow"""
    try:
        data = request.get_json()
        email = data.get('email')
        survey_uuid = data.get('survey_uuid')
        
        if not email or not survey_uuid:
            return jsonify({
                'success': False,
                'error': 'Email and survey_uuid are required'
            }), 400
        
        # Find survey
        survey = SurveyFlask.query.filter_by(uuid=survey_uuid).first()
        if not survey:
            return jsonify({
                'success': False,
                'error': 'Survey not found'
            }), 404
        
        # Send email with real survey link
        result = send_email_invitation(
            recipient=email,
            link=f'/survey/{survey.uuid}',  # Placeholder - will be replaced with real URL
            title=survey.display_title,
            survey_id=survey.uuid  # Pass survey UUID for real URL generation
        )
        
        if result.success:
            return jsonify({
                'success': True,
                'message': 'Email sent successfully',
                'survey_url': f'/survey/{survey.uuid}',
                'delivery_result': {
                    'message_id': result.message_id,
                    'delivery_time': result.delivery_time.isoformat() if result.delivery_time else None
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': result.error_message or 'Failed to send email'
            }), 500
        
    except Exception as e:
        logger.error(f"Error testing email delivery: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to send test email'
        }), 500

@survey_hosting_bp.route('/list', methods=['GET'])
def list_surveys():
    """List all hosted surveys"""
    try:
        surveys = SurveyFlask.query.order_by(SurveyFlask.created_at.desc()).all()
        
        surveys_data = []
        for survey in surveys:
            surveys_data.append({
                'id': survey.id,
                'uuid': survey.uuid,
                'short_id': survey.short_id,
                'title': survey.display_title,
                'description': survey.display_description,
                'status': survey.status,
                'response_count': survey.response_count,
                'public_url': survey.public_url,
                'is_active': survey.is_active,
                'created_at': survey.created_at.isoformat(),
                'questions_count': len(survey.questions)
            })
        
        return jsonify({
            'success': True,
            'surveys': surveys_data,
            'total': len(surveys_data)
        })
        
    except Exception as e:
        logger.error(f"Error listing surveys: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to list surveys'
        }), 500