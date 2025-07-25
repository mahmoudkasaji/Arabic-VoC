"""
Delivery Utilities - Consolidated delivery methods
Phase 2C: Consolidates email_delivery.py + sms_delivery.py + whatsapp_delivery.py + web_delivery.py
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class DeliveryResult:
    """Standardized delivery result"""
    success: bool
    message_id: Optional[str] = None
    error_message: Optional[str] = None
    cost: float = 0.0
    delivery_time: Optional[datetime] = None

class UnifiedDeliveryManager:
    """Consolidated delivery manager for all channels"""
    
    def __init__(self):
        # Email: Gmail (preferred) or SendGrid (fallback)
        gmail_configured = bool(os.getenv("GMAIL_USERNAME")) and bool(os.getenv("GMAIL_APP_PASSWORD"))
        sendgrid_configured = bool(os.getenv("SENDGRID_API_KEY"))
        self.email_configured = gmail_configured or sendgrid_configured
        
        self.sms_configured = bool(os.getenv("TWILIO_ACCOUNT_SID")) and bool(os.getenv("TWILIO_AUTH_TOKEN"))
        self.whatsapp_configured = bool(os.getenv("WHATSAPP_API_KEY"))
        
    def send_survey_invitation(self, 
                              channel: str, 
                              recipient: str, 
                              survey_link: str, 
                              survey_title: str,
                              message_template: Optional[str] = None) -> DeliveryResult:
        """Send survey invitation via specified channel"""
        
        try:
            if channel == "email":
                return self._send_email(recipient, survey_link, survey_title, message_template)
            elif channel == "sms":
                return self._send_sms(recipient, survey_link, survey_title, message_template)
            elif channel == "whatsapp":
                return self._send_whatsapp(recipient, survey_link, survey_title, message_template)
            else:
                return DeliveryResult(False, error_message=f"Unsupported channel: {channel}")
                
        except Exception as e:
            logger.error(f"Delivery failed for {channel} to {recipient}: {e}")
            return DeliveryResult(False, error_message=str(e))
    
    def _send_email(self, recipient: str, link: str, title: str, template: Optional[str]) -> DeliveryResult:
        """Send email invitation via Gmail or SendGrid"""
        # Try Gmail first, fallback to SendGrid
        gmail_available = bool(os.getenv("GMAIL_USERNAME")) and bool(os.getenv("GMAIL_APP_PASSWORD"))
        
        if gmail_available:
            try:
                from utils.gmail_delivery import GmailDeliveryService
                gmail_service = GmailDeliveryService()
                # Extract first name from email or use default
                customer_name = recipient.split('@')[0].title() if '@' in recipient else "Customer"
                result = gmail_service.send_survey_invitation(recipient, link, title, "Voice of Customer Platform", template, customer_name)
                
                return DeliveryResult(
                    success=result.success,
                    message_id=result.message_id,
                    error_message=result.error_message,
                    delivery_time=result.delivery_time
                )
            except Exception as e:
                logger.warning(f"Gmail delivery failed, trying SendGrid: {e}")
        
        # Fallback to SendGrid if Gmail is not available or fails
        if not self.email_configured:
            return DeliveryResult(False, error_message="No email service configured. Please set either Gmail (GMAIL_USERNAME, GMAIL_APP_PASSWORD) or SendGrid (SENDGRID_API_KEY) credentials.")
        
        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail
            
            sg = sendgrid.SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))
            
            # Simple email template
            if not template:
                template = f"""
                مرحباً،
                
                يسعدنا دعوتك للمشاركة في استطلاع: {title}
                
                للمشاركة، يرجى الضغط على الرابط التالي:
                {link}
                
                شكراً لوقتك الثمين.
                فريق منصة صوت العميل
                """
            else:
                template = template.replace("{survey_link}", link).replace("{survey_title}", title)
            
            message = Mail(
                from_email=os.getenv("FROM_EMAIL", "noreply@vocplatform.com"),
                to_emails=recipient,
                subject=f"استطلاع رأي: {title}",
                html_content=template.replace("\n", "<br>")
            )
            
            response = sg.send(message)
            
            return DeliveryResult(
                success=True,
                message_id=getattr(response, 'headers', {}).get("X-Message-Id") if hasattr(response, 'headers') else None,
                delivery_time=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"SendGrid delivery failed: {e}")
            return DeliveryResult(False, error_message=f"Email failed: {str(e)}")
    
    def _send_sms(self, recipient: str, link: str, title: str, template: Optional[str]) -> DeliveryResult:
        """Send SMS invitation"""
        if not self.sms_configured:
            return DeliveryResult(False, error_message="SMS service not configured")
        
        try:
            from twilio.rest import Client
            
            client = Client(
                os.getenv("TWILIO_ACCOUNT_SID"),
                os.getenv("TWILIO_AUTH_TOKEN")
            )
            
            # Simple SMS template
            if not template:
                message_body = f"مرحباً! يسعدنا دعوتك لاستطلاع: {title}\n\nللمشاركة: {link}\n\nشكراً لك"
            else:
                message_body = template.replace("{survey_link}", link).replace("{survey_title}", title)
            
            # Limit SMS length
            if len(message_body) > 160:
                message_body = f"استطلاع: {title[:50]}...\n{link}\nشكراً لك"
            
            message = client.messages.create(
                body=message_body,
                from_=os.getenv("TWILIO_PHONE_NUMBER"),
                to=recipient
            )
            )
            
            return DeliveryResult(
                success=True,
                message_id=message.sid,
                cost=float(message.price or 0),
                delivery_time=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"SMS delivery failed: {e}")
            return DeliveryResult(False, error_message=f"SMS failed: {str(e)}")
    
    def _send_whatsapp(self, recipient: str, link: str, title: str, template: Optional[str]) -> DeliveryResult:
        """Send WhatsApp invitation"""
        if not self.whatsapp_configured:
            return DeliveryResult(False, error_message="WhatsApp service not configured")
        
        try:
            # Using Twilio WhatsApp API as fallback
            if self.sms_configured:
                from twilio.rest import Client
                
                client = Client(
                    os.getenv("TWILIO_ACCOUNT_SID"),
                    os.getenv("TWILIO_AUTH_TOKEN")
                )
                
                # WhatsApp template
                if not template:
                    message_body = f"🔔 استطلاع جديد: {title}\n\n📝 للمشاركة اضغط هنا:\n{link}\n\n🙏 شكراً لوقتك"
                else:
                    message_body = template.replace("{survey_link}", link).replace("{survey_title}", title)
                
                # Ensure WhatsApp number format
                whatsapp_number = f"whatsapp:{recipient}"
                
                message = client.messages.create(
                    body=message_body,
                    from_="whatsapp:" + (os.getenv("TWILIO_WHATSAPP_NUMBER") or os.getenv("TWILIO_PHONE_NUMBER") or ""),
                    to=whatsapp_number
                )
                
                return DeliveryResult(
                    success=True,
                    message_id=message.sid,
                    cost=float(message.price or 0),
                    delivery_time=datetime.utcnow()
                )
            else:
                return DeliveryResult(False, error_message="WhatsApp service not configured")
                
        except Exception as e:
            logger.error(f"WhatsApp delivery failed: {e}")
            return DeliveryResult(False, error_message=f"WhatsApp failed: {str(e)}")
    
    def bulk_send(self, 
                  deliveries: List[Dict[str, Any]]) -> Dict[str, DeliveryResult]:
        """Send multiple invitations"""
        results = {}
        
        for delivery in deliveries:
            recipient_id = delivery.get("recipient_id")
            channel = delivery.get("channel")
            recipient = delivery.get("recipient")
            survey_link = delivery.get("survey_link")
            survey_title = delivery.get("survey_title")
            template = delivery.get("template")
            
            if channel and recipient and survey_link and survey_title and self.validate_recipient(channel, recipient):
                result = self.send_survey_invitation(
                    channel=channel,
                    recipient=recipient,
                    survey_link=survey_link,
                    survey_title=survey_title,
                    message_template=template
                )
                results[str(recipient_id)] = result
            else:
                results[str(recipient_id)] = DeliveryResult(False, error_message="Invalid recipient or missing data")
            
            # Brief delay between sends
            import time
            time.sleep(0.1)
        
        return results
    
    def get_delivery_status(self) -> Dict[str, Any]:
        """Get delivery service status"""
        return {
            "email_configured": self.email_configured,
            "sms_configured": self.sms_configured,
            "whatsapp_configured": self.whatsapp_configured,
            "available_channels": [
                channel for channel, configured in [
                    ("email", self.email_configured),
                    ("sms", self.sms_configured),
                    ("whatsapp", self.whatsapp_configured)
                ] if configured
            ],
            "total_channels": sum([
                self.email_configured,
                self.sms_configured,
                self.whatsapp_configured
            ])
        }
    
    def validate_recipient(self, channel: str, recipient: str) -> bool:
        """Validate recipient format for channel"""
        import re
        
        if channel == "email":
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return bool(re.match(email_pattern, recipient))
        
        elif channel in ["sms", "whatsapp"]:
            # Simple phone number validation
            phone_pattern = r'^\+?[1-9]\d{1,14}$'
            return bool(re.match(phone_pattern, recipient.replace(" ", "").replace("-", "")))
        
        return False

# Convenience functions for backward compatibility
def send_email_invitation(recipient: str, survey_link: str, survey_title: str) -> DeliveryResult:
    """Send email invitation"""
    manager = UnifiedDeliveryManager()
    return manager.send_survey_invitation("email", recipient, survey_link, survey_title)

def send_sms_invitation(recipient: str, survey_link: str, survey_title: str) -> DeliveryResult:
    """Send SMS invitation"""
    manager = UnifiedDeliveryManager()
    return manager.send_survey_invitation("sms", recipient, survey_link, survey_title)

def send_whatsapp_invitation(recipient: str, survey_link: str, survey_title: str) -> DeliveryResult:
    """Send WhatsApp invitation"""
    manager = UnifiedDeliveryManager()
    return manager.send_survey_invitation("whatsapp", recipient, survey_link, survey_title)