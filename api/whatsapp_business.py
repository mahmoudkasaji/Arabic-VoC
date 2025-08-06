"""
WhatsApp Business API Integration
Provides feedback collection and survey distribution via WhatsApp
"""

import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from flask import Blueprint, request, jsonify, flash, redirect, url_for
from dataclasses import dataclass
from enum import Enum
import requests
import json

from models_unified import Feedback, FeedbackChannel, FeedbackStatus
# Remove unused import - using direct requests instead

logger = logging.getLogger(__name__)

# Create WhatsApp Business API blueprint
whatsapp_bp = Blueprint('whatsapp_business', __name__)

class WhatsAppMessageType(Enum):
    TEXT = "text"
    TEMPLATE = "template"
    INTERACTIVE = "interactive"
    DOCUMENT = "document"
    IMAGE = "image"

class WhatsAppWebhookEvent(Enum):
    MESSAGE_RECEIVED = "messages"
    MESSAGE_STATUS = "message_status"
    DELIVERY_STATUS = "delivery_status"

@dataclass
class WhatsAppMessage:
    """Represents a WhatsApp message"""
    phone_number: str
    message_type: WhatsAppMessageType
    content: str
    timestamp: datetime
    message_id: Optional[str] = None
    contact_name: Optional[str] = None
    media_url: Optional[str] = None

class WhatsAppBusinessAPI:
    """WhatsApp Business API client wrapper"""
    
    def __init__(self):
        self.api_token = os.getenv("WHATSAPP_API_TOKEN")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID") 
        self.business_account_id = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID")
        self.webhook_verify_token = os.getenv("WHATSAPP_WEBHOOK_VERIFY_TOKEN")
        self.base_url = "https://graph.facebook.com/v18.0"
        self.configured = bool(self.api_token and self.phone_number_id)
        
    def send_text_message(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Send a text message via WhatsApp Business API"""
        if not self.configured:
            return {"success": False, "error": "WhatsApp API not configured"}
        
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {"body": message}
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            return {
                "success": True, 
                "message_id": response.json().get("messages", [{}])[0].get("id"),
                "response": response.json()
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"WhatsApp API error: {e}")
            return {"success": False, "error": str(e)}
    
    def send_survey_invitation(self, phone_number: str, survey_title: str, survey_link: str, language: str = "ar") -> Dict[str, Any]:
        """Send survey invitation via WhatsApp"""
        
        # Arabic and English templates
        templates = {
            "ar": f"""
🔍 دعوة للمشاركة في الاستطلاع

عزيزي العميل،
نود دعوتك للمشاركة في استطلاع: *{survey_title}*

رأيك مهم لنا ويساعدنا في تحسين خدماتنا.

🔗 الرابط: {survey_link}

⏱️ المدة المتوقعة: 3-5 دقائق
🎁 شكراً لوقتك الثمين

فريق صوت العميل
            """,
            "en": f"""
🔍 Survey Invitation

Dear Valued Customer,
We invite you to participate in our survey: *{survey_title}*

Your feedback is important to us and helps improve our services.

🔗 Link: {survey_link}

⏱️ Estimated time: 3-5 minutes
🎁 Thank you for your time

Voice of Customer Team
            """
        }
        
        message = templates.get(language, templates["ar"])
        return self.send_text_message(phone_number, message)
    
    def send_feedback_confirmation(self, phone_number: str, feedback_id: str, language: str = "ar") -> Dict[str, Any]:
        """Send feedback received confirmation"""
        
        templates = {
            "ar": f"""
✅ تم استلام ملاحظاتك بنجاح

شكراً لك على ملاحظاتك القيمة!
رقم المرجع: #{feedback_id}

سيقوم فريقنا بمراجعة ملاحظاتك والرد عليك قريباً.

🕐 وقت الاستجابة المتوقع: 24-48 ساعة

فريق صوت العميل
            """,
            "en": f"""
✅ Feedback Received Successfully

Thank you for your valuable feedback!
Reference ID: #{feedback_id}

Our team will review your feedback and respond soon.

🕐 Expected response time: 24-48 hours

Voice of Customer Team
            """
        }
        
        message = templates.get(language, templates["ar"])
        return self.send_text_message(phone_number, message)

# Initialize WhatsApp client
whatsapp_client = WhatsAppBusinessAPI()

# === WEBHOOK ENDPOINTS ===

@whatsapp_bp.route('/webhook', methods=['GET'])
def webhook_verification():
    """WhatsApp webhook verification endpoint"""
    verify_token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if verify_token == whatsapp_client.webhook_verify_token:
        logger.info("WhatsApp webhook verified successfully")
        return challenge
    else:
        logger.warning("WhatsApp webhook verification failed")
        return "Verification failed", 403

@whatsapp_bp.route('/webhook', methods=['POST'])
def webhook_handler():
    """Process incoming WhatsApp messages"""
    try:
        data = request.get_json()
        logger.info(f"WhatsApp webhook received: {json.dumps(data, indent=2)}")
        
        # Extract message data from webhook
        if 'entry' in data:
            for entry in data['entry']:
                if 'changes' in entry:
                    for change in entry['changes']:
                        if change.get('field') == 'messages':
                            messages = change.get('value', {}).get('messages', [])
                            for message in messages:
                                process_incoming_message(message, change.get('value', {}))
        
        return jsonify({"success": True}), 200
        
    except Exception as e:
        logger.error(f"WhatsApp webhook processing error: {e}")
        return jsonify({"error": str(e)}), 500

def process_incoming_message(message_data: Dict, webhook_value: Dict):
    """Process individual incoming WhatsApp message"""
    try:
        # Extract message details
        phone_number = message_data.get('from', '')
        message_id = message_data.get('id', '')
        timestamp = datetime.fromtimestamp(int(message_data.get('timestamp', 0)))
        
        # Get contact info
        contacts = webhook_value.get('contacts', [])
        contact_name = None
        if contacts:
            contact_name = contacts[0].get('profile', {}).get('name', 'Unknown')
        
        # Extract message content based on type
        message_type = message_data.get('type', 'text')
        content = ""
        
        if message_type == 'text':
            content = message_data.get('text', {}).get('body', '')
        elif message_type == 'image':
            content = message_data.get('image', {}).get('caption', 'Image received')
        elif message_type == 'document':
            content = f"Document received: {message_data.get('document', {}).get('filename', 'Unknown')}"
        elif message_type == 'voice':
            content = "Voice message received"
        else:
            content = f"Message type: {message_type}"
        
        # Save feedback to database
        if content.strip():
            save_whatsapp_feedback(
                phone_number=phone_number,
                content=content,
                contact_name=contact_name,
                message_id=message_id,
                message_type=message_type
            )
            
            # Send confirmation
            whatsapp_client.send_feedback_confirmation(
                phone_number=phone_number,
                feedback_id=message_id,
                language="ar"  # Could be detected from content
            )
        
    except Exception as e:
        logger.error(f"Error processing WhatsApp message: {e}")

def save_whatsapp_feedback(phone_number: str, content: str, contact_name: Optional[str] = None, 
                          message_id: Optional[str] = None, message_type: str = "text"):
    """Save WhatsApp feedback to database"""
    try:
        from app import db
        
        # Create feedback record
        feedback = Feedback(
            content=content,
            channel=FeedbackChannel.WHATSAPP,
            status=FeedbackStatus.PENDING,
            customer_phone=phone_number,
            customer_id=contact_name or phone_number,
            channel_metadata={
                "message_id": message_id,
                "message_type": message_type,
                "contact_name": contact_name,
                "platform": "whatsapp_business"
            },
            language_detected="ar",  # Could be auto-detected
            created_at=datetime.utcnow()
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        logger.info(f"WhatsApp feedback saved: ID {feedback.id}, Phone: {phone_number}")
        return feedback.id
        
    except Exception as e:
        logger.error(f"Error saving WhatsApp feedback: {e}")
        return None

# === API ENDPOINTS ===

@whatsapp_bp.route('/api/whatsapp/send-message', methods=['POST'])
def send_message():
    """API endpoint to send WhatsApp message"""
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        message = data.get('message')
        
        if not phone_number or not message:
            return jsonify({"error": "Phone number and message required"}), 400
        
        result = whatsapp_client.send_text_message(phone_number, message)
        return jsonify(result), 200 if result.get("success") else 400
        
    except Exception as e:
        logger.error(f"Send WhatsApp message API error: {e}")
        return jsonify({"error": str(e)}), 500

@whatsapp_bp.route('/api/whatsapp/send-survey', methods=['POST'])
def send_survey_invitation():
    """API endpoint to send survey invitation via WhatsApp"""
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        survey_title = data.get('survey_title')
        survey_link = data.get('survey_link')
        language = data.get('language', 'ar')
        
        if not all([phone_number, survey_title, survey_link]):
            return jsonify({"error": "Phone number, survey title, and link required"}), 400
        
        result = whatsapp_client.send_survey_invitation(
            phone_number, survey_title, survey_link, language
        )
        return jsonify(result), 200 if result.get("success") else 400
        
    except Exception as e:
        logger.error(f"Send WhatsApp survey API error: {e}")
        return jsonify({"error": str(e)}), 500

@whatsapp_bp.route('/api/whatsapp/status')
def whatsapp_status():
    """Check WhatsApp Business API configuration status"""
    return jsonify({
        "configured": whatsapp_client.configured,
        "phone_number_id": whatsapp_client.phone_number_id,
        "business_account_id": whatsapp_client.business_account_id,
        "webhook_configured": bool(whatsapp_client.webhook_verify_token),
        "required_env_vars": [
            "WHATSAPP_API_TOKEN",
            "WHATSAPP_PHONE_NUMBER_ID", 
            "WHATSAPP_BUSINESS_ACCOUNT_ID",
            "WHATSAPP_WEBHOOK_VERIFY_TOKEN"
        ]
    })

@whatsapp_bp.route('/admin/whatsapp')
def admin_dashboard():
    """WhatsApp admin dashboard (placeholder)"""
    return jsonify({
        "status": "WhatsApp Business API endpoint configured",
        "integration_status": "ROADMAP - Ready for configuration",
        "features": [
            "Inbound message handling",
            "Survey distribution", 
            "Feedback collection",
            "Template messaging",
            "Webhook processing"
        ]
    })

# Test endpoint
@whatsapp_bp.route('/api/whatsapp/test', methods=['POST'])
def test_whatsapp():
    """Test WhatsApp Business API connection"""
    if not whatsapp_client.configured:
        return jsonify({
            "success": False,
            "message": "WhatsApp Business API not configured",
            "required_vars": ["WHATSAPP_API_TOKEN", "WHATSAPP_PHONE_NUMBER_ID"]
        }), 400
    
    try:
        # Test by getting business profile info
        url = f"{whatsapp_client.base_url}/{whatsapp_client.phone_number_id}"
        headers = {"Authorization": f"Bearer {whatsapp_client.api_token}"}
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        return jsonify({
            "success": True,
            "message": "WhatsApp Business API connection successful",
            "phone_info": response.json()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"WhatsApp API test failed: {str(e)}"
        }), 400