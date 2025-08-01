"""
Consolidated Communication Utilities
Combines functionality from delivery_utils.py, gmail_delivery.py, and survey_distribution.py
"""

import smtplib
import logging
from typing import Dict, List, Any, Optional, Union
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders
import os
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class CommunicationManager:
    """Unified communication management for all channels"""
    
    def __init__(self):
        self.smtp_config = {
            "server": "smtp.gmail.com",
            "port": 587,
            "username": os.getenv("GMAIL_USERNAME"),
            "password": os.getenv("GMAIL_PASSWORD")
        }
        
        self.twilio_config = {
            "account_sid": os.getenv("TWILIO_ACCOUNT_SID"),
            "auth_token": os.getenv("TWILIO_AUTH_TOKEN"),
            "phone_number": os.getenv("TWILIO_PHONE_NUMBER")
        }
        
        self.whatsapp_config = {
            "api_key": os.getenv("WHATSAPP_API_KEY"),
            "base_url": "https://api.whatsapp.com/send"
        }
        
        # Message templates
        self.templates = {
            "ar": {
                "survey_invitation": {
                    "subject": "دعوة للمشاركة في استبيان رأي العملاء",
                    "body": """
                    عزيزي {name},
                    
                    نود دعوتك للمشاركة في استبيان سريع لتحسين خدماتنا.
                    
                    رابط الاستبيان: {survey_link}
                    
                    شكراً لوقتك الثمين.
                    
                    مع التقدير،
                    فريق خدمة العملاء
                    """
                },
                "feedback_confirmation": {
                    "subject": "شكراً لك على ملاحظاتك القيمة",
                    "body": """
                    عزيزي {name},
                    
                    شكراً لك على مشاركة ملاحظاتك معنا. نقدر وقتك وآراءك.
                    
                    سنقوم بمراجعة تعليقاتك والرد عليك قريباً.
                    
                    مع التقدير،
                    فريق خدمة العملاء
                    """
                }
            },
            "en": {
                "survey_invitation": {
                    "subject": "Invitation to Participate in Customer Survey",
                    "body": """
                    Dear {name},
                    
                    We would like to invite you to participate in a quick survey to help us improve our services.
                    
                    Survey link: {survey_link}
                    
                    Thank you for your valuable time.
                    
                    Best regards,
                    Customer Service Team
                    """
                },
                "feedback_confirmation": {
                    "subject": "Thank You for Your Valuable Feedback",
                    "body": """
                    Dear {name},
                    
                    Thank you for sharing your feedback with us. We appreciate your time and insights.
                    
                    We will review your comments and get back to you soon.
                    
                    Best regards,
                    Customer Service Team
                    """
                }
            }
        }
    
    def send_email(self, 
                   to_email: str, 
                   subject: str, 
                   body: str, 
                   html_body: Optional[str] = None,
                   attachments: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Send email with enhanced error handling"""
        try:
            # Create message
            msg = MimeMultipart('alternative')
            msg['From'] = self.smtp_config["username"]
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add text body
            text_part = MimeText(body, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # Add HTML body if provided
            if html_body:
                html_part = MimeText(html_body, 'html', 'utf-8')
                msg.attach(html_part)
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    self._add_attachment(msg, attachment)
            
            # Send email
            with smtplib.SMTP(self.smtp_config["server"], self.smtp_config["port"]) as server:
                server.starttls()
                server.login(self.smtp_config["username"], self.smtp_config["password"])
                server.send_message(msg)
            
            return {
                "success": True,
                "message": "Email sent successfully",
                "delivery_id": f"email_{datetime.utcnow().timestamp()}"
            }
            
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {e}")
            return {
                "success": False,
                "error": str(e),
                "delivery_id": None
            }
    
    def send_sms(self, to_phone: str, message: str) -> Dict[str, Any]:
        """Send SMS via Twilio"""
        try:
            # Import Twilio client when needed
            try:
                from twilio.rest import Client
                
                client = Client(self.twilio_config["account_sid"], 
                              self.twilio_config["auth_token"])
                
                message = client.messages.create(
                    body=message,
                    from_=self.twilio_config["phone_number"],
                    to=to_phone
                )
                
                return {
                    "success": True,
                    "message": "SMS sent successfully",
                    "delivery_id": message.sid
                }
                
            except ImportError:
                return {
                    "success": False,
                    "error": "Twilio SDK not available",
                    "delivery_id": None
                }
                
        except Exception as e:
            logger.error(f"Error sending SMS to {to_phone}: {e}")
            return {
                "success": False,
                "error": str(e),
                "delivery_id": None
            }
    
    def send_whatsapp(self, to_phone: str, message: str) -> Dict[str, Any]:
        """Send WhatsApp message"""
        try:
            # Placeholder for WhatsApp Business API integration
            # In real implementation, would use official WhatsApp Business API
            
            return {
                "success": False,
                "error": "WhatsApp integration not implemented yet",
                "delivery_id": None
            }
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp to {to_phone}: {e}")
            return {
                "success": False,
                "error": str(e),
                "delivery_id": None
            }
    
    def distribute_survey(self, 
                         survey_data: Dict[str, Any], 
                         contacts: List[Dict[str, Any]], 
                         channels: List[str]) -> Dict[str, Any]:
        """Distribute survey to multiple contacts via multiple channels"""
        
        results = {
            "total_contacts": len(contacts),
            "successful_deliveries": 0,
            "failed_deliveries": 0,
            "delivery_details": [],
            "errors": []
        }
        
        for contact in contacts:
            contact_results = self._distribute_to_contact(survey_data, contact, channels)
            results["delivery_details"].append(contact_results)
            
            if contact_results["success"]:
                results["successful_deliveries"] += 1
            else:
                results["failed_deliveries"] += 1
                results["errors"].append(contact_results)
        
        return results
    
    def send_feedback_confirmation(self, 
                                 contact_email: str, 
                                 contact_name: str, 
                                 language: str = "ar") -> Dict[str, Any]:
        """Send feedback confirmation to customer"""
        
        template = self.templates.get(language, self.templates["ar"])["feedback_confirmation"]
        
        subject = template["subject"]
        body = template["body"].format(name=contact_name or "العميل الكريم")
        
        return self.send_email(contact_email, subject, body)
    
    def _distribute_to_contact(self, 
                             survey_data: Dict[str, Any], 
                             contact: Dict[str, Any], 
                             channels: List[str]) -> Dict[str, Any]:
        """Distribute survey to a single contact"""
        
        contact_name = contact.get("name", "العميل الكريم")
        language = contact.get("language_preference", "ar")
        survey_link = survey_data.get("public_url", "#")
        
        # Get appropriate template
        template = self.templates.get(language, self.templates["ar"])["survey_invitation"]
        
        subject = template["subject"]
        body = template["body"].format(name=contact_name, survey_link=survey_link)
        
        # Try channels in order of preference
        for channel in channels:
            if channel == "email" and contact.get("email") and contact.get("email_opt_in"):
                result = self.send_email(contact["email"], subject, body)
                if result["success"]:
                    return {
                        "contact_id": contact.get("id"),
                        "contact_name": contact_name,
                        "channel": "email",
                        "success": True,
                        "delivery_id": result["delivery_id"]
                    }
            
            elif channel == "sms" and contact.get("phone") and contact.get("sms_opt_in"):
                sms_message = f"{contact_name}, {survey_link}"
                result = self.send_sms(contact["phone"], sms_message)
                if result["success"]:
                    return {
                        "contact_id": contact.get("id"),
                        "contact_name": contact_name,
                        "channel": "sms",
                        "success": True,
                        "delivery_id": result["delivery_id"]
                    }
            
            elif channel == "whatsapp" and contact.get("phone") and contact.get("whatsapp_opt_in"):
                whatsapp_message = f"{contact_name}, {survey_link}"
                result = self.send_whatsapp(contact["phone"], whatsapp_message)
                if result["success"]:
                    return {
                        "contact_id": contact.get("id"),
                        "contact_name": contact_name,
                        "channel": "whatsapp",
                        "success": True,
                        "delivery_id": result["delivery_id"]
                    }
        
        return {
            "contact_id": contact.get("id"),
            "contact_name": contact_name,
            "channel": None,
            "success": False,
            "error": "No available communication channel"
        }
    
    def _add_attachment(self, msg: MimeMultipart, attachment: Dict[str, Any]) -> None:
        """Add attachment to email message"""
        try:
            filename = attachment.get("filename")
            filepath = attachment.get("filepath")
            content = attachment.get("content")
            
            if filepath and os.path.exists(filepath):
                with open(filepath, "rb") as f:
                    part = MimeBase('application', 'octet-stream')
                    part.set_payload(f.read())
            elif content:
                part = MimeBase('application', 'octet-stream')
                part.set_payload(content)
            else:
                return
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}'
            )
            msg.attach(part)
            
        except Exception as e:
            logger.error(f"Error adding attachment {attachment.get('filename')}: {e}")
    
    def get_delivery_status(self, delivery_id: str) -> Dict[str, Any]:
        """Get delivery status for a specific delivery"""
        # Placeholder for delivery tracking
        return {
            "delivery_id": delivery_id,
            "status": "delivered",
            "delivered_at": datetime.utcnow().isoformat(),
            "channel": "email"
        }
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate communication channel configurations"""
        status = {
            "email": bool(self.smtp_config["username"] and self.smtp_config["password"]),
            "sms": bool(self.twilio_config["account_sid"] and self.twilio_config["auth_token"]),
            "whatsapp": bool(self.whatsapp_config["api_key"])
        }
        
        return {
            "configured_channels": [channel for channel, configured in status.items() if configured],
            "missing_config": [channel for channel, configured in status.items() if not configured],
            "all_configured": all(status.values())
        }

# Singleton instance
communication_manager = CommunicationManager()