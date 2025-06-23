"""
WhatsApp Survey Delivery Engine
WhatsApp Business API integration for Arabic surveys
"""

import logging
import asyncio
import json
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from models.survey_delivery import SurveyDelivery, DeliveryStatus

logger = logging.getLogger(__name__)

class WhatsAppDeliveryEngine:
    """WhatsApp delivery engine using Business API"""
    
    def __init__(self):
        self.api_base_url = "https://graph.facebook.com/v18.0"
        self.access_token = None
        self.phone_number_id = None
        self.initialize_whatsapp()
    
    def initialize_whatsapp(self):
        """Initialize WhatsApp Business API"""
        try:
            import os
            
            self.access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
            self.phone_number_id = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')
            
            if self.access_token and self.phone_number_id:
                logger.info("WhatsApp Business API initialized")
            else:
                logger.warning("WhatsApp credentials not found - WhatsApp delivery disabled")
        except Exception as e:
            logger.error(f"WhatsApp initialization failed: {e}")
    
    async def send_surveys(self, deliveries: List[SurveyDelivery], db: AsyncSession) -> Dict[str, int]:
        """Send survey messages via WhatsApp"""
        results = {'successful': 0, 'failed': 0}
        
        if not self.access_token:
            logger.warning("WhatsApp not available - marking messages as failed")
            for delivery in deliveries:
                delivery.status = DeliveryStatus.FAILED
                delivery.error_message = "WhatsApp API not configured"
                delivery.failed_at = datetime.utcnow()
                results['failed'] += 1
            await db.commit()
            return results
        
        # Process deliveries with rate limiting
        for delivery in deliveries:
            try:
                success = await self.send_single_whatsapp(delivery)
                
                if success:
                    delivery.status = DeliveryStatus.SENT
                    delivery.sent_at = datetime.utcnow()
                    results['successful'] += 1
                    logger.info(f"Survey WhatsApp sent to {delivery.recipient_whatsapp}")
                else:
                    delivery.status = DeliveryStatus.FAILED
                    delivery.failed_at = datetime.utcnow()
                    results['failed'] += 1
                
                # Rate limiting for WhatsApp API
                await asyncio.sleep(1.0)
                
            except Exception as e:
                logger.error(f"WhatsApp delivery failed for {delivery.id}: {e}")
                delivery.status = DeliveryStatus.FAILED
                delivery.error_message = str(e)
                delivery.failed_at = datetime.utcnow()
                results['failed'] += 1
        
        await db.commit()
        return results
    
    async def send_single_whatsapp(self, delivery: SurveyDelivery) -> bool:
        """Send individual WhatsApp message"""
        try:
            import aiohttp
            
            # Get survey details
            campaign = delivery.campaign
            template = campaign.template
            
            # Generate survey URL
            survey_url = self.generate_survey_url(delivery)
            
            # Prepare WhatsApp message
            message_data = await self.prepare_whatsapp_message(template, delivery, survey_url)
            
            # Send via WhatsApp API
            url = f"{self.api_base_url}/{self.phone_number_id}/messages"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=message_data, headers=headers) as response:
                    response_data = await response.json()
                    
                    if response.status == 200 and 'messages' in response_data:
                        # Update delivery metadata
                        delivery.channel_metadata = {
                            'whatsapp_message_id': response_data['messages'][0]['id'],
                            'api_response': response_data
                        }
                        return True
                    else:
                        logger.error(f"WhatsApp API error: {response_data}")
                        delivery.error_message = json.dumps(response_data)
                        return False
            
        except Exception as e:
            logger.error(f"WhatsApp send failed: {e}")
            delivery.error_message = str(e)
            return False
    
    def generate_survey_url(self, delivery: SurveyDelivery) -> str:
        """Generate survey URL for WhatsApp"""
        base_url = "https://arabic-voc.replit.app"
        return f"{base_url}/surveys/respond/{delivery.delivery_token}"
    
    async def prepare_whatsapp_message(
        self, 
        template: Any, 
        delivery: SurveyDelivery, 
        survey_url: str
    ) -> Dict[str, Any]:
        """Prepare WhatsApp message with interactive elements"""
        
        recipient_phone = delivery.recipient_whatsapp.replace('+', '')
        recipient_name = delivery.recipient_name or "عزيزي العميل"
        
        # WhatsApp message with interactive buttons
        message_data = {
            "messaging_product": "whatsapp",
            "to": recipient_phone,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "header": {
                    "type": "text",
                    "text": "منصة صوت العميل العربية"
                },
                "body": {
                    "text": f"""مرحباً {recipient_name},

نأمل مشاركتك في استطلاع رأي قصير ({template.estimated_duration or 5} دقائق) لتحسين خدماتنا.

📋 *{template.title}*

{template.description or 'استطلاع لجمع آرائكم وتحسين تجربتكم معنا'}

شكراً لوقتك الثمين 🙏"""
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": f"start_survey_{delivery.delivery_token}",
                                "title": "ابدأ الاستطلاع"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": f"later_{delivery.delivery_token}",
                                "title": "لاحقاً"
                            }
                        }
                    ]
                }
            }
        }
        
        return message_data
    
    async def send_survey_link(self, delivery: SurveyDelivery, survey_url: str) -> bool:
        """Send survey link as follow-up message"""
        try:
            import aiohttp
            
            recipient_phone = delivery.recipient_whatsapp.replace('+', '')
            
            message_data = {
                "messaging_product": "whatsapp",
                "to": recipient_phone,
                "type": "text",
                "text": {
                    "body": f"""رابط الاستطلاع:
{survey_url}

أو يمكنك النقر على الرابط مباشرة للبدء.

شكراً لك! 🌟"""
                }
            }
            
            url = f"{self.api_base_url}/{self.phone_number_id}/messages"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=message_data, headers=headers) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.error(f"WhatsApp link send failed: {e}")
            return False

class WhatsAppWebhookHandler:
    """Handle incoming WhatsApp messages and interactions"""
    
    def __init__(self):
        self.delivery_engine = WhatsAppDeliveryEngine()
    
    async def process_webhook(self, webhook_data: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        """Process incoming WhatsApp webhook"""
        try:
            if not self.is_valid_webhook(webhook_data):
                return {'status': 'invalid_webhook'}
            
            # Extract message data
            entry = webhook_data.get('entry', [{}])[0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})
            
            # Handle different message types
            if 'messages' in value:
                return await self.handle_incoming_message(value['messages'][0], db)
            elif 'statuses' in value:
                return await self.handle_message_status(value['statuses'][0], db)
            
            return {'status': 'no_action_needed'}
            
        except Exception as e:
            logger.error(f"WhatsApp webhook processing failed: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def is_valid_webhook(self, data: Dict[str, Any]) -> bool:
        """Validate WhatsApp webhook structure"""
        try:
            return (
                'entry' in data and
                len(data['entry']) > 0 and
                'changes' in data['entry'][0]
            )
        except:
            return False
    
    async def handle_incoming_message(self, message: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        """Handle incoming WhatsApp message"""
        try:
            from_phone = '+' + message['from']
            message_type = message.get('type', 'text')
            
            if message_type == 'interactive':
                # Handle button interactions
                button_reply = message['interactive']['button_reply']
                button_id = button_reply['id']
                
                if button_id.startswith('start_survey_'):
                    token = button_id.replace('start_survey_', '')
                    return await self.handle_survey_start(from_phone, token, db)
                elif button_id.startswith('later_'):
                    return await self.handle_later_response(from_phone, db)
                    
            elif message_type == 'text':
                # Handle text responses
                text_body = message['text']['body']
                return await self.handle_text_response(from_phone, text_body, db)
            
            return {'status': 'message_received'}
            
        except Exception as e:
            logger.error(f"Message handling failed: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def handle_survey_start(self, from_phone: str, token: str, db: AsyncSession) -> Dict[str, Any]:
        """Handle survey start button click"""
        try:
            # Find delivery by token
            from sqlalchemy import select
            
            result = await db.execute(
                select(SurveyDelivery)
                .where(SurveyDelivery.delivery_token == token)
            )
            delivery = result.scalar_one_or_none()
            
            if delivery:
                # Send survey link
                survey_url = self.delivery_engine.generate_survey_url(delivery)
                await self.delivery_engine.send_survey_link(delivery, survey_url)
                
                return {'status': 'survey_link_sent'}
            else:
                return {'status': 'invalid_token'}
                
        except Exception as e:
            logger.error(f"Survey start handling failed: {e}")
            return {'status': 'error'}
    
    async def handle_later_response(self, from_phone: str, db: AsyncSession) -> Dict[str, Any]:
        """Handle 'later' button response"""
        try:
            # Send acknowledgment
            import aiohttp
            
            phone_number = from_phone.replace('+', '')
            
            message_data = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "text",
                "text": {
                    "body": "لا بأس، سنتواصل معك في وقت آخر. شكراً لك! 😊"
                }
            }
            
            # Send via API (simplified - would use proper engine)
            return {'status': 'later_acknowledged'}
            
        except Exception as e:
            logger.error(f"Later response handling failed: {e}")
            return {'status': 'error'}
    
    async def handle_text_response(self, from_phone: str, text: str, db: AsyncSession) -> Dict[str, Any]:
        """Handle text message responses"""
        try:
            # Use SMS response handler logic for text parsing
            from utils.sms_delivery import SMSResponseHandler
            
            sms_handler = SMSResponseHandler()
            result = await sms_handler.process_sms_response(from_phone, text, db)
            
            # Send confirmation via WhatsApp
            if result['status'] == 'processed':
                await self.send_whatsapp_confirmation(from_phone)
            
            return result
            
        except Exception as e:
            logger.error(f"Text response handling failed: {e}")
            return {'status': 'error'}
    
    async def send_whatsapp_confirmation(self, to_phone: str):
        """Send confirmation message via WhatsApp"""
        try:
            phone_number = to_phone.replace('+', '')
            
            message_data = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "text",
                "text": {
                    "body": "شكراً لمشاركتك! تم استلام إجابتك بنجاح ✅\n\nمنصة صوت العميل العربية"
                }
            }
            
            # Would send via proper API call
            logger.info(f"WhatsApp confirmation would be sent to {to_phone}")
            
        except Exception as e:
            logger.warning(f"Failed to send WhatsApp confirmation: {e}")
    
    async def handle_message_status(self, status: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        """Handle message delivery status updates"""
        try:
            message_id = status.get('id')
            status_value = status.get('status')  # sent, delivered, read, failed
            
            # Update delivery record if needed
            if message_id and status_value in ['delivered', 'read', 'failed']:
                # Find delivery by WhatsApp message ID
                from sqlalchemy import select, update
                
                await db.execute(
                    update(SurveyDelivery)
                    .where(SurveyDelivery.channel_metadata['whatsapp_message_id'].astext == message_id)
                    .values(
                        status=DeliveryStatus.DELIVERED if status_value in ['delivered', 'read'] else DeliveryStatus.FAILED,
                        delivered_at=datetime.utcnow() if status_value in ['delivered', 'read'] else None,
                        failed_at=datetime.utcnow() if status_value == 'failed' else None
                    )
                )
                await db.commit()
            
            return {'status': 'status_updated', 'message_status': status_value}
            
        except Exception as e:
            logger.error(f"Status handling failed: {e}")
            return {'status': 'error'}