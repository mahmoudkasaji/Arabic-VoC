"""
Email Survey Delivery Engine
SendGrid integration for Arabic email surveys
"""

import logging
import asyncio
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from models.survey_delivery import SurveyDelivery, DeliveryStatus
from utils.arabic_processor import process_arabic_text

logger = logging.getLogger(__name__)

class EmailDeliveryEngine:
    """Email delivery engine using SendGrid"""
    
    def __init__(self):
        self.sendgrid_client = None
        self.initialize_sendgrid()
    
    def initialize_sendgrid(self):
        """Initialize SendGrid client"""
        try:
            import os
            from sendgrid import SendGridAPIClient
            
            api_key = os.environ.get('SENDGRID_API_KEY')
            if api_key:
                self.sendgrid_client = SendGridAPIClient(api_key)
                logger.info("SendGrid client initialized")
            else:
                logger.warning("SENDGRID_API_KEY not found - email delivery disabled")
        except ImportError:
            logger.warning("SendGrid package not installed - email delivery disabled")
        except Exception as e:
            logger.error(f"SendGrid initialization failed: {e}")
    
    async def send_surveys(self, deliveries: List[SurveyDelivery], db: AsyncSession) -> Dict[str, int]:
        """Send survey emails to recipients"""
        results = {'successful': 0, 'failed': 0}
        
        if not self.sendgrid_client:
            logger.warning("SendGrid not available - marking emails as failed")
            for delivery in deliveries:
                delivery.status = DeliveryStatus.FAILED
                delivery.error_message = "SendGrid not configured"
                delivery.failed_at = datetime.utcnow()
                results['failed'] += 1
            await db.commit()
            return results
        
        # Process deliveries in batches
        batch_size = 10
        for i in range(0, len(deliveries), batch_size):
            batch = deliveries[i:i + batch_size]
            batch_results = await self.send_email_batch(batch, db)
            results['successful'] += batch_results['successful']
            results['failed'] += batch_results['failed']
            
            # Small delay between batches to respect rate limits
            await asyncio.sleep(0.5)
        
        return results
    
    async def send_email_batch(self, deliveries: List[SurveyDelivery], db: AsyncSession) -> Dict[str, int]:
        """Send a batch of survey emails"""
        results = {'successful': 0, 'failed': 0}
        
        for delivery in deliveries:
            try:
                # Get survey template
                campaign = delivery.campaign
                template = campaign.template
                
                # Generate survey URL
                survey_url = self.generate_survey_url(delivery)
                
                # Prepare email content
                email_content = await self.prepare_email_content(
                    template, delivery, survey_url
                )
                
                # Send email
                success = await self.send_single_email(delivery, email_content)
                
                if success:
                    delivery.status = DeliveryStatus.SENT
                    delivery.sent_at = datetime.utcnow()
                    results['successful'] += 1
                    logger.info(f"Survey email sent to {delivery.recipient_email}")
                else:
                    delivery.status = DeliveryStatus.FAILED
                    delivery.failed_at = datetime.utcnow()
                    results['failed'] += 1
                
            except Exception as e:
                logger.error(f"Email delivery failed for {delivery.id}: {e}")
                delivery.status = DeliveryStatus.FAILED
                delivery.error_message = str(e)
                delivery.failed_at = datetime.utcnow()
                results['failed'] += 1
        
        await db.commit()
        return results
    
    def generate_survey_url(self, delivery: SurveyDelivery) -> str:
        """Generate survey participation URL"""
        base_url = "https://arabic-voc.replit.app"  # Replace with actual domain
        return f"{base_url}/surveys/respond/{delivery.delivery_token}"
    
    async def prepare_email_content(
        self, 
        template: Any, 
        delivery: SurveyDelivery, 
        survey_url: str
    ) -> Dict[str, str]:
        """Prepare Arabic email content"""
        
        # Arabic email template
        subject = f"استطلاع رأي: {template.title}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{subject}</title>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    direction: rtl;
                    text-align: right;
                    background-color: #f8f9fa;
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #2E8B57, #4169E1);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .content {{
                    padding: 30px;
                }}
                .survey-button {{
                    display: inline-block;
                    background: #2E8B57;
                    color: white;
                    padding: 15px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                    font-weight: bold;
                }}
                .footer {{
                    background: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    color: #6c757d;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>منصة صوت العميل العربية</h1>
                    <p>نقدر رأيك ونهتم بتجربتك</p>
                </div>
                
                <div class="content">
                    <h2>مرحباً {delivery.recipient_name or 'عزيزي العميل'},</h2>
                    
                    <p>نأمل أن تكون بخير. نحن في منصة صوت العميل العربية نسعى دائماً لتحسين خدماتنا وتقديم أفضل تجربة لعملائنا الكرام.</p>
                    
                    <p><strong>عنوان الاستطلاع:</strong> {template.title}</p>
                    <p><strong>الوصف:</strong> {template.description or 'استطلاع لتحسين خدماتنا'}</p>
                    <p><strong>الوقت المتوقع:</strong> {template.estimated_duration or 5} دقائق</p>
                    
                    <p>مشاركتك في هذا الاستطلاع ستساعدنا على فهم احتياجاتك بشكل أفضل وتطوير خدماتنا لتلبي توقعاتك.</p>
                    
                    <div style="text-align: center;">
                        <a href="{survey_url}" class="survey-button">
                            ابدأ الاستطلاع الآن
                        </a>
                    </div>
                    
                    <p><strong>أو انسخ الرابط التالي في متصفحك:</strong></p>
                    <p style="word-break: break-all; background: #f8f9fa; padding: 10px; border-radius: 5px;">
                        {survey_url}
                    </p>
                    
                    <p>شكراً لوقتك الثمين ولثقتك بنا.</p>
                </div>
                
                <div class="footer">
                    <p>منصة صوت العميل العربية</p>
                    <p>هذه رسالة آلية، يرجى عدم الرد عليها</p>
                    <p>إذا كنت لا ترغب في استقبال هذه الرسائل، <a href="#">انقر هنا لإلغاء الاشتراك</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_content = f"""
        منصة صوت العميل العربية
        
        مرحباً {delivery.recipient_name or 'عزيزي العميل'},
        
        نأمل أن تكون بخير. نحن نسعى دائماً لتحسين خدماتنا وتقديم أفضل تجربة لعملائنا.
        
        عنوان الاستطلاع: {template.title}
        الوصف: {template.description or 'استطلاع لتحسين خدماتنا'}
        الوقت المتوقع: {template.estimated_duration or 5} دقائق
        
        للمشاركة في الاستطلاع، يرجى زيارة الرابط التالي:
        {survey_url}
        
        شكراً لوقتك الثمين ولثقتك بنا.
        
        منصة صوت العميل العربية
        """
        
        return {
            'subject': subject,
            'html_content': html_content,
            'text_content': text_content
        }
    
    async def send_single_email(self, delivery: SurveyDelivery, content: Dict[str, str]) -> bool:
        """Send individual email using SendGrid"""
        try:
            from sendgrid.helpers.mail import Mail, Email, To, Content
            
            message = Mail(
                from_email=Email("surveys@arabic-voc.replit.app", "منصة صوت العميل العربية"),
                to_emails=To(delivery.recipient_email),
                subject=content['subject']
            )
            
            # Add both HTML and text content
            message.content = [
                Content("text/plain", content['text_content']),
                Content("text/html", content['html_content'])
            ]
            
            # Send email
            response = self.sendgrid_client.send(message)
            
            # Check response status
            if response.status_code in [200, 201, 202]:
                return True
            else:
                logger.warning(f"SendGrid returned status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"SendGrid send failed: {e}")
            return False