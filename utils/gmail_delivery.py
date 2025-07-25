"""
Gmail-based Email Delivery Service
Simple Gmail SMTP integration for survey delivery
"""

import os
import smtplib
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class GmailDeliveryResult:
    """Gmail delivery result"""
    success: bool
    message_id: Optional[str] = None
    error_message: Optional[str] = None
    delivery_time: Optional[datetime] = None

class GmailDeliveryService:
    """Gmail SMTP delivery service"""
    
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.username = os.getenv("GMAIL_USERNAME")
        self.password = os.getenv("GMAIL_APP_PASSWORD")  # Gmail App Password, not regular password
        self.configured = bool(self.username and self.password)
        
    def send_survey_invitation(self,
                              recipient: str,
                              survey_link: str,
                              survey_title: str,
                              sender_name: str = "Voice of Customer Platform",
                              message_template: Optional[str] = None) -> GmailDeliveryResult:
        """Send survey invitation via Gmail"""
        
        if not self.configured:
            return GmailDeliveryResult(
                success=False,
                error_message="Gmail service not configured. Please set GMAIL_USERNAME and GMAIL_APP_PASSWORD environment variables."
            )
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{sender_name} <{self.username}>"
            msg['To'] = recipient
            msg['Subject'] = f"استطلاع رأي: {survey_title}"
            
            # Create email content
            if message_template:
                # Use custom template
                email_body = message_template.replace("{survey_link}", survey_link).replace("{survey_title}", survey_title)
            else:
                # Default template
                email_body = f"""
السلام عليكم ورحمة الله وبركاته،

يسعدنا دعوتكم للمشاركة في استطلاع رأي مهم حول: {survey_title}

للمشاركة في الاستطلاع، يرجى الضغط على الرابط التالي:
{survey_link}

نقدر وقتكم الثمين ومشاركتكم معنا في تحسين خدماتنا.

مع أطيب التحيات،
فريق منصة صوت العميل
                """.strip()
            
            # Create HTML version
            html_body = f"""
            <html dir="rtl" lang="ar">
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; direction: rtl; text-align: right; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
                    .content {{ background-color: #ffffff; padding: 20px; border: 1px solid #dee2e6; border-radius: 10px; }}
                    .button {{ background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }}
                    .footer {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #dee2e6; font-size: 14px; color: #6c757d; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>استطلاع رأي مهم</h2>
                    </div>
                    <div class="content">
                        <p>السلام عليكم ورحمة الله وبركاته،</p>
                        <p>يسعدنا دعوتكم للمشاركة في استطلاع رأي حول: <strong>{survey_title}</strong></p>
                        <p>مشاركتكم مهمة جداً لنا وستساعدنا في تحسين خدماتنا.</p>
                        <div style="text-align: center;">
                            <a href="{survey_link}" class="button">المشاركة في الاستطلاع</a>
                        </div>
                        <p>أو يمكنكم نسخ ولصق الرابط التالي في المتصفح:</p>
                        <p style="word-break: break-all; background-color: #f8f9fa; padding: 10px; border-radius: 5px;">{survey_link}</p>
                    </div>
                    <div class="footer">
                        <p>مع أطيب التحيات،<br>فريق منصة صوت العميل</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Attach parts
            text_part = MIMEText(email_body, 'plain', 'utf-8')
            html_part = MIMEText(html_body, 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                text = msg.as_string()
                server.sendmail(self.username, recipient, text)
                
            return GmailDeliveryResult(
                success=True,
                message_id=f"gmail_{int(datetime.utcnow().timestamp())}",
                delivery_time=datetime.utcnow()
            )
            
        except smtplib.SMTPAuthenticationError:
            return GmailDeliveryResult(
                success=False,
                error_message="Gmail authentication failed. Please check your Gmail username and app password."
            )
        except smtplib.SMTPRecipientsRefused:
            return GmailDeliveryResult(
                success=False,
                error_message=f"Invalid recipient email address: {recipient}"
            )
        except Exception as e:
            logger.error(f"Gmail delivery failed: {e}")
            return GmailDeliveryResult(
                success=False,
                error_message=f"Gmail delivery failed: {str(e)}"
            )
    
    def test_connection(self) -> GmailDeliveryResult:
        """Test Gmail connection"""
        if not self.configured:
            return GmailDeliveryResult(
                success=False,
                error_message="Gmail service not configured"
            )
        
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                
            return GmailDeliveryResult(
                success=True,
                message_id="connection_test_success"
            )
            
        except Exception as e:
            return GmailDeliveryResult(
                success=False,
                error_message=f"Gmail connection test failed: {str(e)}"
            )
    
    def get_status(self) -> dict:
        """Get Gmail service status"""
        return {
            "service": "Gmail SMTP",
            "configured": self.configured,
            "username": self.username if self.configured else None,
            "server": f"{self.smtp_server}:{self.smtp_port}",
            "requirements": [
                "GMAIL_USERNAME (your Gmail address)",
                "GMAIL_APP_PASSWORD (Gmail App Password, not regular password)"
            ]
        }