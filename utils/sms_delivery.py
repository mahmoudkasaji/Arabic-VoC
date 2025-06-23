"""
SMS Survey Delivery Engine
Twilio integration for Arabic SMS surveys
"""

import logging
import asyncio
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from models.survey_delivery import SurveyDelivery, DeliveryStatus

logger = logging.getLogger(__name__)

class SMSDeliveryEngine:
    """SMS delivery engine using Twilio"""
    
    def __init__(self):
        self.twilio_client = None
        self.from_phone = None
        self.initialize_twilio()
    
    def initialize_twilio(self):
        """Initialize Twilio client"""
        try:
            import os
            from twilio.rest import Client
            
            account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
            auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
            self.from_phone = os.environ.get('TWILIO_PHONE_NUMBER')
            
            if account_sid and auth_token and self.from_phone:
                self.twilio_client = Client(account_sid, auth_token)
                logger.info("Twilio client initialized")
            else:
                logger.warning("Twilio credentials not found - SMS delivery disabled")
        except ImportError:
            logger.warning("Twilio package not installed - SMS delivery disabled")
        except Exception as e:
            logger.error(f"Twilio initialization failed: {e}")
    
    async def send_surveys(self, deliveries: List[SurveyDelivery], db: AsyncSession) -> Dict[str, int]:
        """Send survey SMS messages to recipients"""
        results = {'successful': 0, 'failed': 0}
        
        if not self.twilio_client:
            logger.warning("Twilio not available - marking SMS as failed")
            for delivery in deliveries:
                delivery.status = DeliveryStatus.FAILED
                delivery.error_message = "Twilio not configured"
                delivery.failed_at = datetime.utcnow()
                results['failed'] += 1
            await db.commit()
            return results
        
        # Process deliveries with rate limiting
        for delivery in deliveries:
            try:
                success = await self.send_single_sms(delivery)
                
                if success:
                    delivery.status = DeliveryStatus.SENT
                    delivery.sent_at = datetime.utcnow()
                    results['successful'] += 1
                    logger.info(f"Survey SMS sent to {delivery.recipient_phone}")
                else:
                    delivery.status = DeliveryStatus.FAILED
                    delivery.failed_at = datetime.utcnow()
                    results['failed'] += 1
                
                # Rate limiting - Twilio allows 1 message per second
                await asyncio.sleep(1.1)
                
            except Exception as e:
                logger.error(f"SMS delivery failed for {delivery.id}: {e}")
                delivery.status = DeliveryStatus.FAILED
                delivery.error_message = str(e)
                delivery.failed_at = datetime.utcnow()
                results['failed'] += 1
        
        await db.commit()
        return results
    
    async def send_single_sms(self, delivery: SurveyDelivery) -> bool:
        """Send individual SMS using Twilio"""
        try:
            # Get survey details
            campaign = delivery.campaign
            template = campaign.template
            
            # Generate survey URL
            survey_url = self.generate_survey_url(delivery)
            
            # Prepare SMS content (Arabic)
            message_text = await self.prepare_sms_content(template, delivery, survey_url)
            
            # Send SMS
            message = self.twilio_client.messages.create(
                body=message_text,
                from_=self.from_phone,
                to=delivery.recipient_phone
            )
            
            # Update delivery metadata with Twilio SID
            delivery.channel_metadata = {
                'twilio_sid': message.sid,
                'twilio_status': message.status,
                'message_length': len(message_text)
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Twilio SMS send failed: {e}")
            delivery.error_message = str(e)
            return False
    
    def generate_survey_url(self, delivery: SurveyDelivery) -> str:
        """Generate short survey URL for SMS"""
        base_url = "https://arabic-voc.replit.app"
        return f"{base_url}/s/{delivery.delivery_token[:8]}"  # Shortened URL
    
    async def prepare_sms_content(
        self, 
        template: Any, 
        delivery: SurveyDelivery, 
        survey_url: str
    ) -> str:
        """Prepare Arabic SMS content (160 character limit consideration)"""
        
        # Short Arabic SMS message
        recipient_name = delivery.recipient_name or "عزيزي العميل"
        first_name = recipient_name.split()[0] if recipient_name else "عزيزي"
        
        # Keep message concise for SMS
        message = f"""مرحباً {first_name},
        
نأمل مشاركتك في استطلاع قصير ({template.estimated_duration or 3} دقائق) لتحسين خدماتنا.

{template.title}

شارك الآن: {survey_url}

شكراً لك
منصة صوت العميل العربية"""
        
        # Ensure message is within reasonable SMS length
        if len(message) > 450:  # Leave room for Arabic encoding
            # Fallback to shorter message
            message = f"""استطلاع رأي سريع من منصة صوت العميل العربية

{template.title}

المشاركة: {survey_url}

شكراً لوقتك"""
        
        return message

class SMSResponseHandler:
    """Handle incoming SMS responses to surveys"""
    
    def __init__(self):
        self.response_patterns = {
            # Arabic response patterns
            'positive': ['نعم', 'موافق', 'ممتاز', 'راضي', 'جيد', '5', '4'],
            'negative': ['لا', 'غير موافق', 'سيء', 'غير راضي', '1', '2'],
            'neutral': ['متوسط', 'عادي', 'لا بأس', '3']
        }
    
    async def process_sms_response(
        self, 
        from_phone: str, 
        message_body: str, 
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Process incoming SMS response"""
        try:
            # Find active survey delivery for this phone number
            delivery = await self.find_active_delivery(from_phone, db)
            if not delivery:
                return {'status': 'no_active_survey'}
            
            # Parse response
            parsed_response = self.parse_arabic_response(message_body)
            
            # Store response
            from utils.survey_distribution import SurveyResponseCollector
            collector = SurveyResponseCollector()
            
            response_data = {
                'responses': {'sms_response': parsed_response},
                'metadata': {
                    'sms_body': message_body,
                    'response_method': 'sms_reply'
                },
                'language': 'ar'
            }
            
            result = await collector.collect_response(
                delivery.delivery_token,
                response_data,
                delivery.channel,
                db
            )
            
            # Send confirmation SMS
            await self.send_confirmation_sms(from_phone, parsed_response)
            
            return {
                'status': 'processed',
                'response_id': result.get('response_id'),
                'parsed_response': parsed_response
            }
            
        except Exception as e:
            logger.error(f"SMS response processing failed: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def find_active_delivery(self, phone: str, db: AsyncSession):
        """Find active survey delivery for phone number"""
        from sqlalchemy import select, and_
        from datetime import timedelta
        
        # Look for recent deliveries (within last 7 days)
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        
        result = await db.execute(
            select(SurveyDelivery)
            .where(and_(
                SurveyDelivery.recipient_phone == phone,
                SurveyDelivery.status == DeliveryStatus.SENT,
                SurveyDelivery.sent_at >= cutoff_date
            ))
            .order_by(SurveyDelivery.sent_at.desc())
        )
        
        return result.first()
    
    def parse_arabic_response(self, message: str) -> Dict[str, Any]:
        """Parse Arabic SMS response"""
        message_lower = message.lower().strip()
        
        # Check for rating numbers
        for char in message:
            if char.isdigit() and 1 <= int(char) <= 5:
                return {
                    'type': 'rating',
                    'value': int(char),
                    'text': message
                }
        
        # Check for Arabic sentiment words
        for sentiment, patterns in self.response_patterns.items():
            for pattern in patterns:
                if pattern in message_lower:
                    return {
                        'type': 'sentiment',
                        'value': sentiment,
                        'text': message
                    }
        
        # Default to text response
        return {
            'type': 'text',
            'value': message,
            'text': message
        }
    
    async def send_confirmation_sms(self, to_phone: str, parsed_response: Dict[str, Any]):
        """Send confirmation SMS for received response"""
        try:
            # Simple confirmation message
            confirmation = "شكراً لمشاركتك في الاستطلاع. تم استلام إجابتك بنجاح.\nمنصة صوت العميل العربية"
            
            # Use same Twilio client as delivery engine
            engine = SMSDeliveryEngine()
            if engine.twilio_client:
                engine.twilio_client.messages.create(
                    body=confirmation,
                    from_=engine.from_phone,
                    to=to_phone
                )
                logger.info(f"Confirmation SMS sent to {to_phone}")
                
        except Exception as e:
            logger.warning(f"Failed to send confirmation SMS: {e}")