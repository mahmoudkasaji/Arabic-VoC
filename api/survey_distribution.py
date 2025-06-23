"""
Survey Distribution API
Multi-channel survey delivery and response collection endpoints
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from flask import Blueprint, request, jsonify, render_template_string
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
import asyncio

from models.survey_delivery import (
    SurveyCampaign, SurveyDelivery, SurveyTemplate, SurveyResponse,
    SurveyStatus, DeliveryStatus, ResponseStatus
)
from models_unified import FeedbackChannel
from utils.survey_distribution import SurveyDistributionManager, SurveyResponseCollector
from utils.web_delivery import WebSurveyRenderer, QRCodeGenerator
from utils.whatsapp_delivery import WhatsAppWebhookHandler
from utils.sms_delivery import SMSResponseHandler
from utils.database import get_db
from utils.security import validate_survey_input, rate_limiter

logger = logging.getLogger(__name__)

# Create Blueprint
survey_bp = Blueprint('surveys', __name__, url_prefix='/api/surveys')

@survey_bp.route('/distribute', methods=['POST'])
async def distribute_survey():
    """
    Distribute survey campaign across multiple channels
    
    Expected JSON:
    {
        "campaign_id": 123,
        "channels": ["email", "sms", "whatsapp"],
        "audience": {
            "segments": ["high_value_customers"],
            "filters": {"region": "riyadh", "language": "ar"}
        },
        "schedule": {
            "start_time": "2025-06-24T09:00:00Z",
            "frequency": "once"
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'campaign_id' not in data:
            return jsonify({'error': 'campaign_id is required'}), 400
        
        campaign_id = data['campaign_id']
        
        # Initialize distribution manager
        distribution_manager = SurveyDistributionManager()
        
        # Start distribution
        result = await distribution_manager.distribute_campaign(campaign_id, get_db())
        
        return jsonify({
            'status': 'success',
            'message': 'Survey distribution initiated',
            'result': result
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Survey distribution failed: {e}")
        return jsonify({'error': 'Distribution failed'}), 500

@survey_bp.route('/respond', methods=['POST'])
async def collect_survey_response():
    """
    Collect survey response from any channel
    
    Expected JSON:
    {
        "delivery_token": "abc123...",
        "responses": {
            "question_1": "إجابة ممتازة",
            "question_2": 5,
            "question_3": ["الجودة", "السعر"]
        },
        "metadata": {
            "completion_time": 120,
            "device_type": "mobile",
            "user_agent": "Mozilla/5.0...",
            "language": "ar"
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'delivery_token' not in data:
            return jsonify({'error': 'delivery_token is required'}), 400
        
        delivery_token = data['delivery_token']
        responses = data.get('responses', {})
        metadata = data.get('metadata', {})
        
        # Validate input
        if not responses:
            return jsonify({'error': 'responses are required'}), 400
        
        # Collect response
        collector = SurveyResponseCollector()
        result = await collector.collect_response(
            delivery_token=delivery_token,
            response_data={
                'responses': responses,
                'metadata': metadata,
                'language': data.get('language', 'ar')
            },
            channel=FeedbackChannel.WEBSITE,  # Default to website
            db=get_db()
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Response collected successfully',
            'result': result
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Response collection failed: {e}")
        return jsonify({'error': 'Response collection failed'}), 500

@survey_bp.route('/respond/<token>', methods=['GET'])
async def render_web_survey(token: str):
    """
    Render survey page for web delivery
    """
    try:
        renderer = WebSurveyRenderer()
        result = await renderer.render_survey_page(token, get_db())
        
        if result.get('error'):
            return jsonify({'error': result['error']}), result.get('status_code', 500)
        
        return result['html'], 200, {'Content-Type': 'text/html; charset=utf-8'}
        
    except Exception as e:
        logger.error(f"Survey rendering failed: {e}")
        return jsonify({'error': 'Survey not available'}), 500

@survey_bp.route('/qr/<token>', methods=['GET'])
async def generate_survey_qr(token: str):
    """
    Generate QR code for survey
    """
    try:
        # Get survey URL
        survey_url = f"https://arabic-voc.replit.app/surveys/respond/{token}"
        
        # Generate QR code
        qr_generator = QRCodeGenerator()
        qr_data = await qr_generator.generate_qr_code(survey_url, token)
        
        if 'error' in qr_data:
            return jsonify({'error': qr_data['error']}), 500
        
        return jsonify({
            'status': 'success',
            'qr_code': qr_data['qr_code_base64'],
            'survey_url': survey_url,
            'format': 'base64_png'
        }), 200
        
    except Exception as e:
        logger.error(f"QR generation failed: {e}")
        return jsonify({'error': 'QR code generation failed'}), 500

@survey_bp.route('/webhook/whatsapp', methods=['POST'])
async def whatsapp_webhook():
    """
    Handle WhatsApp webhook for interactive surveys
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Invalid webhook data'}), 400
        
        # Process webhook
        webhook_handler = WhatsAppWebhookHandler()
        result = await webhook_handler.process_webhook(data, get_db())
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"WhatsApp webhook failed: {e}")
        return jsonify({'error': 'Webhook processing failed'}), 500

@survey_bp.route('/webhook/whatsapp', methods=['GET'])
def whatsapp_webhook_verify():
    """
    Verify WhatsApp webhook (Facebook requirement)
    """
    try:
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        # Verify token (should match your configured verify token)
        verify_token = "arabic_voc_webhook_verify_token"
        
        if mode == 'subscribe' and token == verify_token:
            return challenge, 200
        else:
            return 'Verification failed', 403
            
    except Exception as e:
        logger.error(f"WhatsApp webhook verification failed: {e}")
        return 'Verification failed', 403

@survey_bp.route('/webhook/sms', methods=['POST'])
async def sms_webhook():
    """
    Handle SMS responses via Twilio webhook
    """
    try:
        # Twilio sends form data, not JSON
        from_phone = request.form.get('From')
        message_body = request.form.get('Body')
        
        if not from_phone or not message_body:
            return jsonify({'error': 'Invalid SMS data'}), 400
        
        # Process SMS response
        sms_handler = SMSResponseHandler()
        result = await sms_handler.process_sms_response(from_phone, message_body, get_db())
        
        # Return TwiML response
        twiml_response = '<?xml version="1.0" encoding="UTF-8"?><Response></Response>'
        return twiml_response, 200, {'Content-Type': 'text/xml'}
        
    except Exception as e:
        logger.error(f"SMS webhook failed: {e}")
        return '<?xml version="1.0" encoding="UTF-8"?><Response></Response>', 200, {'Content-Type': 'text/xml'}

@survey_bp.route('/campaigns', methods=['GET'])
async def list_campaigns():
    """
    List survey campaigns with filters
    """
    try:
        # Get query parameters
        status = request.args.get('status')
        limit = min(int(request.args.get('limit', 10)), 100)
        offset = int(request.args.get('offset', 0))
        
        db = get_db()
        
        # Build query
        query = select(SurveyCampaign)
        
        if status:
            query = query.where(SurveyCampaign.status == status)
        
        query = query.order_by(SurveyCampaign.created_at.desc()).limit(limit).offset(offset)
        
        # Execute query
        result = await db.execute(query)
        campaigns = result.scalars().all()
        
        # Format response
        campaigns_data = []
        for campaign in campaigns:
            campaigns_data.append({
                'id': campaign.id,
                'name': campaign.name,
                'status': campaign.status.value,
                'target_count': campaign.target_count,
                'sent_count': campaign.sent_count,
                'response_count': campaign.response_count,
                'response_rate': campaign.response_rate,
                'created_at': campaign.created_at.isoformat(),
                'start_date': campaign.start_date.isoformat() if campaign.start_date else None,
                'end_date': campaign.end_date.isoformat() if campaign.end_date else None
            })
        
        return jsonify({
            'campaigns': campaigns_data,
            'pagination': {
                'limit': limit,
                'offset': offset,
                'total': len(campaigns_data)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Campaign listing failed: {e}")
        return jsonify({'error': 'Failed to fetch campaigns'}), 500

@survey_bp.route('/campaigns/<int:campaign_id>/analytics', methods=['GET'])
async def get_campaign_analytics(campaign_id: int):
    """
    Get detailed analytics for a survey campaign
    """
    try:
        db = get_db()
        
        # Get campaign
        campaign = await db.get(SurveyCampaign, campaign_id)
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        
        # Get delivery statistics
        delivery_stats = await db.execute(
            select(
                SurveyDelivery.channel,
                SurveyDelivery.status,
                func.count(SurveyDelivery.id).label('count')
            )
            .where(SurveyDelivery.campaign_id == campaign_id)
            .group_by(SurveyDelivery.channel, SurveyDelivery.status)
        )
        
        # Get response statistics
        response_stats = await db.execute(
            select(
                func.avg(SurveyResponse.satisfaction_score).label('avg_satisfaction'),
                func.avg(SurveyResponse.total_time_seconds).label('avg_completion_time'),
                func.count(SurveyResponse.id).label('total_responses')
            )
            .where(SurveyResponse.campaign_id == campaign_id)
        )
        
        # Format delivery statistics
        delivery_by_channel = {}
        for row in delivery_stats:
            channel = row.channel.value
            status = row.status.value
            count = row.count
            
            if channel not in delivery_by_channel:
                delivery_by_channel[channel] = {}
            delivery_by_channel[channel][status] = count
        
        # Format response statistics
        response_data = response_stats.first()
        avg_satisfaction = float(response_data.avg_satisfaction) if response_data.avg_satisfaction else 0
        avg_completion_time = int(response_data.avg_completion_time) if response_data.avg_completion_time else 0
        total_responses = response_data.total_responses or 0
        
        analytics = {
            'campaign_info': {
                'id': campaign.id,
                'name': campaign.name,
                'status': campaign.status.value,
                'created_at': campaign.created_at.isoformat()
            },
            'delivery_metrics': {
                'target_audience': campaign.target_count,
                'total_sent': campaign.sent_count,
                'total_delivered': campaign.delivered_count,
                'total_failed': campaign.sent_count - campaign.delivered_count,
                'by_channel': delivery_by_channel
            },
            'response_metrics': {
                'total_responses': total_responses,
                'response_rate': campaign.response_rate,
                'completion_rate': campaign.completion_rate,
                'avg_satisfaction_score': round(avg_satisfaction, 2),
                'avg_completion_time_seconds': avg_completion_time
            },
            'performance_summary': {
                'delivery_success_rate': (campaign.delivered_count / campaign.sent_count * 100) if campaign.sent_count > 0 else 0,
                'engagement_score': min(100, campaign.response_rate * 2),  # Simple engagement calculation
                'quality_score': avg_satisfaction * 20 if avg_satisfaction > 0 else 0  # Convert to 0-100 scale
            }
        }
        
        return jsonify(analytics), 200
        
    except Exception as e:
        logger.error(f"Campaign analytics failed: {e}")
        return jsonify({'error': 'Failed to fetch analytics'}), 500

@survey_bp.route('/responses/<int:response_id>', methods=['GET'])
async def get_survey_response(response_id: int):
    """
    Get detailed survey response
    """
    try:
        db = get_db()
        
        # Get response with related data
        response = await db.get(SurveyResponse, response_id)
        if not response:
            return jsonify({'error': 'Response not found'}), 404
        
        response_data = {
            'id': response.id,
            'campaign_id': response.campaign_id,
            'respondent_id': response.respondent_id,
            'responses': response.responses,
            'processed_responses': response.processed_responses,
            'completion_status': response.completion_status.value,
            'completion_percentage': response.completion_percentage,
            'satisfaction_score': response.satisfaction_score,
            'nps_score': response.nps_score,
            'submission_channel': response.submission_channel.value,
            'language_detected': response.language_detected,
            'started_at': response.started_at.isoformat() if response.started_at else None,
            'completed_at': response.completed_at.isoformat() if response.completed_at else None,
            'response_time_minutes': response.response_time_minutes,
            'device_info': response.device_info,
            'quality_score': response.quality_score
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Response fetch failed: {e}")
        return jsonify({'error': 'Failed to fetch response'}), 500

# Route registration function
def register_survey_routes(app):
    """Register survey distribution routes with Flask app"""
    app.register_blueprint(survey_bp)