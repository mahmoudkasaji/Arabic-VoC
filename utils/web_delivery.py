"""
Web Survey Delivery Engine
Website integration for survey distribution
"""

import logging
import asyncio
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from models.survey_delivery import SurveyDelivery, DeliveryStatus

logger = logging.getLogger(__name__)

class WebDeliveryEngine:
    """Web delivery engine for website surveys"""
    
    def __init__(self):
        self.base_url = "https://arabic-voc.replit.app"
    
    async def send_surveys(self, deliveries: List[SurveyDelivery], db: AsyncSession) -> Dict[str, int]:
        """Create web survey links and mark as ready"""
        results = {'successful': 0, 'failed': 0}
        
        for delivery in deliveries:
            try:
                # Generate web survey configuration
                web_config = await self.create_web_survey_config(delivery)
                
                if web_config:
                    delivery.status = DeliveryStatus.SENT
                    delivery.sent_at = datetime.utcnow()
                    delivery.channel_metadata = web_config
                    results['successful'] += 1
                    logger.info(f"Web survey configured for {delivery.recipient_id}")
                else:
                    delivery.status = DeliveryStatus.FAILED
                    delivery.failed_at = datetime.utcnow()
                    results['failed'] += 1
                
            except Exception as e:
                logger.error(f"Web delivery failed for {delivery.id}: {e}")
                delivery.status = DeliveryStatus.FAILED
                delivery.error_message = str(e)
                delivery.failed_at = datetime.utcnow()
                results['failed'] += 1
        
        await db.commit()
        return results
    
    async def create_web_survey_config(self, delivery: SurveyDelivery) -> Dict[str, Any]:
        """Create web survey configuration"""
        try:
            campaign = delivery.campaign
            template = campaign.template
            
            # Generate survey URLs
            survey_url = f"{self.base_url}/surveys/respond/{delivery.delivery_token}"
            embed_url = f"{self.base_url}/surveys/embed/{delivery.delivery_token}"
            qr_url = f"{self.base_url}/surveys/qr/{delivery.delivery_token}"
            
            config = {
                'survey_url': survey_url,
                'embed_url': embed_url,
                'qr_code_url': qr_url,
                'delivery_method': 'web',
                'survey_title': template.title,
                'estimated_duration': template.estimated_duration,
                'created_at': datetime.utcnow().isoformat(),
                'recipient_info': {
                    'customer_id': delivery.recipient_id,
                    'name': delivery.recipient_name,
                    'email': delivery.recipient_email
                }
            }
            
            return config
            
        except Exception as e:
            logger.error(f"Web config creation failed: {e}")
            return None

class QRCodeGenerator:
    """Generate QR codes for survey links"""
    
    def __init__(self):
        self.qr_cache = {}
    
    async def generate_qr_code(self, survey_url: str, delivery_token: str) -> Dict[str, Any]:
        """Generate QR code for survey URL"""
        try:
            import qrcode
            import io
            import base64
            
            # Check cache first
            if delivery_token in self.qr_cache:
                return self.qr_cache[delivery_token]
            
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(survey_url)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            qr_data = {
                'qr_code_base64': img_str,
                'survey_url': survey_url,
                'format': 'PNG',
                'size': '300x300',
                'generated_at': datetime.utcnow().isoformat()
            }
            
            # Cache the result
            self.qr_cache[delivery_token] = qr_data
            
            return qr_data
            
        except ImportError:
            logger.warning("qrcode package not installed - QR generation disabled")
            return {'error': 'QR code generation not available'}
        except Exception as e:
            logger.error(f"QR code generation failed: {e}")
            return {'error': str(e)}

class WebSurveyRenderer:
    """Render survey pages for web delivery"""
    
    def __init__(self):
        self.template_cache = {}
    
    async def render_survey_page(self, delivery_token: str, db: AsyncSession) -> Dict[str, Any]:
        """Render survey page HTML"""
        try:
            # Get delivery and survey data
            delivery = await self.get_delivery_by_token(delivery_token, db)
            if not delivery:
                return {'error': 'Survey not found', 'status_code': 404}
            
            campaign = delivery.campaign
            template = campaign.template
            
            # Generate survey HTML
            survey_html = await self.generate_survey_html(template, delivery)
            
            return {
                'html': survey_html,
                'survey_data': {
                    'title': template.title,
                    'description': template.description,
                    'questions': template.questions,
                    'estimated_duration': template.estimated_duration,
                    'token': delivery_token
                },
                'status_code': 200
            }
            
        except Exception as e:
            logger.error(f"Survey page rendering failed: {e}")
            return {'error': str(e), 'status_code': 500}
    
    async def get_delivery_by_token(self, token: str, db: AsyncSession):
        """Get delivery record by token"""
        from sqlalchemy import select
        
        result = await db.execute(
            select(SurveyDelivery)
            .where(SurveyDelivery.delivery_token == token)
        )
        return result.scalar_one_or_none()
    
    async def generate_survey_html(self, template: Any, delivery: SurveyDelivery) -> str:
        """Generate Arabic survey HTML"""
        
        questions_html = ""
        for i, question in enumerate(template.questions, 1):
            question_html = await self.render_question(question, i)
            questions_html += question_html
        
        survey_html = f"""
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{template.title} - منصة صوت العميل العربية</title>
            
            <!-- Bootstrap RTL CSS -->
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
            
            <!-- Arabic Fonts -->
            <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&family=Amiri:wght@400;700&display=swap" rel="stylesheet">
            
            <!-- Font Awesome -->
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            
            <!-- Design System CSS -->
            <link rel="stylesheet" href="/static/css/design-system.css">
            
            <style>
                .survey-container {{
                    max-width: 800px;
                    margin: 2rem auto;
                    padding: 0 1rem;
                }}
                
                .question-card {{
                    background: var(--bg-primary);
                    border-radius: var(--radius-xl);
                    padding: var(--space-6);
                    margin-bottom: var(--space-6);
                    box-shadow: var(--shadow-base);
                    border: 1px solid var(--border-light);
                }}
                
                .question-number {{
                    background: var(--primary-500);
                    color: white;
                    width: 2rem;
                    height: 2rem;
                    border-radius: 50%;
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: bold;
                    margin-bottom: var(--space-3);
                }}
                
                .progress-bar-container {{
                    background: var(--neutral-200);
                    height: 8px;
                    border-radius: var(--radius-full);
                    margin-bottom: var(--space-8);
                }}
                
                .progress-bar {{
                    background: var(--primary-500);
                    height: 100%;
                    border-radius: var(--radius-full);
                    transition: width 0.3s ease;
                }}
                
                .rating-stars {{
                    display: flex;
                    gap: var(--space-2);
                    direction: ltr;
                }}
                
                .rating-star {{
                    font-size: 2rem;
                    color: var(--neutral-300);
                    cursor: pointer;
                    transition: color var(--transition-base);
                }}
                
                .rating-star:hover,
                .rating-star.active {{
                    color: var(--warning);
                }}
            </style>
        </head>
        <body>
            <div class="survey-container">
                <!-- Header -->
                <div class="card-custom mb-4">
                    <div class="text-center">
                        <h1 class="arabic-title text-primary-custom">
                            <i class="fas fa-clipboard-list me-2"></i>
                            {template.title}
                        </h1>
                        {f'<p class="text-muted">{template.description}</p>' if template.description else ''}
                        <div class="d-flex justify-content-center align-items-center gap-3 mt-3">
                            <span class="badge bg-primary-custom">
                                <i class="fas fa-clock me-1"></i>
                                {template.estimated_duration or 5} دقائق
                            </span>
                            <span class="badge bg-secondary-custom">
                                <i class="fas fa-user me-1"></i>
                                {delivery.recipient_name or 'عزيزي العميل'}
                            </span>
                        </div>
                    </div>
                </div>
                
                <!-- Progress Bar -->
                <div class="progress-bar-container">
                    <div class="progress-bar" id="progressBar" style="width: 0%"></div>
                </div>
                
                <!-- Survey Form -->
                <form id="surveyForm" onsubmit="submitSurvey(event)">
                    <input type="hidden" name="delivery_token" value="{delivery.delivery_token}">
                    
                    {questions_html}
                    
                    <!-- Submit Button -->
                    <div class="text-center mt-5">
                        <button type="submit" class="btn-primary-custom btn-lg-custom">
                            <i class="fas fa-paper-plane me-2"></i>
                            إرسال الإجابات
                        </button>
                    </div>
                </form>
                
                <!-- Thank You Message (Hidden) -->
                <div id="thankYouMessage" class="card-custom text-center" style="display: none;">
                    <i class="fas fa-check-circle fa-3x text-success-custom mb-3"></i>
                    <h2 class="arabic-title text-success-custom">شكراً لمشاركتك!</h2>
                    <p class="text-muted">تم استلام إجاباتك بنجاح. نقدر وقتك واهتمامك.</p>
                    <a href="/" class="btn-outline-custom">
                        <i class="fas fa-home me-2"></i>
                        العودة للصفحة الرئيسية
                    </a>
                </div>
            </div>
            
            <!-- Bootstrap JS -->
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
            
            <!-- Survey JavaScript -->
            <script>
                let totalQuestions = {len(template.questions)};
                let answeredQuestions = 0;
                
                function updateProgress() {{
                    const progress = (answeredQuestions / totalQuestions) * 100;
                    document.getElementById('progressBar').style.width = progress + '%';
                }}
                
                function handleQuestionAnswer(questionId) {{
                    const question = document.querySelector(`[data-question="${{questionId}}"]`);
                    if (question && !question.dataset.answered) {{
                        question.dataset.answered = 'true';
                        answeredQuestions++;
                        updateProgress();
                    }}
                }}
                
                function setRating(questionId, rating) {{
                    const stars = document.querySelectorAll(`[data-question="${{questionId}}"] .rating-star`);
                    const input = document.querySelector(`input[name="${{questionId}}"]`);
                    
                    stars.forEach((star, index) => {{
                        if (index < rating) {{
                            star.classList.add('active');
                        }} else {{
                            star.classList.remove('active');
                        }}
                    }});
                    
                    if (input) {{
                        input.value = rating;
                        handleQuestionAnswer(questionId);
                    }}
                }}
                
                async function submitSurvey(event) {{
                    event.preventDefault();
                    
                    const form = event.target;
                    const formData = new FormData(form);
                    const responses = {{}};
                    
                    // Collect all responses
                    for (let [key, value] of formData.entries()) {{
                        if (key !== 'delivery_token') {{
                            responses[key] = value;
                        }}
                    }}
                    
                    try {{
                        const response = await fetch('/api/surveys/respond', {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json',
                            }},
                            body: JSON.stringify({{
                                delivery_token: formData.get('delivery_token'),
                                responses: responses,
                                metadata: {{
                                    completion_time: Date.now(),
                                    user_agent: navigator.userAgent,
                                    language: 'ar'
                                }}
                            }})
                        }});
                        
                        if (response.ok) {{
                            document.getElementById('surveyForm').style.display = 'none';
                            document.getElementById('thankYouMessage').style.display = 'block';
                        }} else {{
                            alert('حدث خطأ في إرسال الإجابات. يرجى المحاولة مرة أخرى.');
                        }}
                    }} catch (error) {{
                        console.error('Survey submission error:', error);
                        alert('حدث خطأ في الاتصال. يرجى المحاولة مرة أخرى.');
                    }}
                }}
                
                // Add event listeners for form inputs
                document.addEventListener('DOMContentLoaded', function() {{
                    const inputs = document.querySelectorAll('input, textarea, select');
                    inputs.forEach(input => {{
                        input.addEventListener('change', function() {{
                            const questionId = this.name;
                            if (questionId && questionId !== 'delivery_token') {{
                                handleQuestionAnswer(questionId);
                            }}
                        }});
                    }});
                }});
            </script>
        </body>
        </html>
        """
        
        return survey_html
    
    async def render_question(self, question: Dict[str, Any], number: int) -> str:
        """Render individual question HTML"""
        question_type = question.get('type', 'text')
        question_text = question.get('question', f'السؤال {number}')
        question_id = f"question_{number}"
        required = question.get('required', True)
        
        if question_type == 'text':
            return f"""
            <div class="question-card" data-question="{question_id}">
                <div class="question-number">{number}</div>
                <label class="form-label-custom">{question_text}</label>
                <input type="text" class="form-control-custom" name="{question_id}" 
                       placeholder="اكتب إجابتك هنا..." {'required' if required else ''}>
            </div>
            """
        
        elif question_type == 'textarea':
            return f"""
            <div class="question-card" data-question="{question_id}">
                <div class="question-number">{number}</div>
                <label class="form-label-custom">{question_text}</label>
                <textarea class="form-control-custom" name="{question_id}" rows="4"
                          placeholder="اكتب إجابتك بالتفصيل..." {'required' if required else ''}></textarea>
            </div>
            """
        
        elif question_type == 'rating':
            stars_html = ""
            for i in range(1, 6):
                stars_html += f'<span class="rating-star" onclick="setRating(\'{question_id}\', {i})">★</span>'
            
            return f"""
            <div class="question-card" data-question="{question_id}">
                <div class="question-number">{number}</div>
                <label class="form-label-custom">{question_text}</label>
                <div class="rating-stars mt-3">
                    {stars_html}
                </div>
                <input type="hidden" name="{question_id}" {'required' if required else ''}>
                <div class="text-muted mt-2">انقر على النجوم للتقييم (1 = ضعيف، 5 = ممتاز)</div>
            </div>
            """
        
        elif question_type == 'choice':
            options = question.get('options', ['نعم', 'لا'])
            options_html = ""
            for i, option in enumerate(options):
                options_html += f"""
                <div class="form-check-custom">
                    <input class="form-check-input-custom" type="radio" name="{question_id}" 
                           id="{question_id}_option_{i}" value="{option}" {'required' if required else ''}>
                    <label class="form-check-label-custom" for="{question_id}_option_{i}">
                        {option}
                    </label>
                </div>
                """
            
            return f"""
            <div class="question-card" data-question="{question_id}">
                <div class="question-number">{number}</div>
                <label class="form-label-custom">{question_text}</label>
                <div class="mt-3">
                    {options_html}
                </div>
            </div>
            """
        
        # Default text input
        return f"""
        <div class="question-card" data-question="{question_id}">
            <div class="question-number">{number}</div>
            <label class="form-label-custom">{question_text}</label>
            <input type="text" class="form-control-custom" name="{question_id}" 
                   placeholder="اكتب إجابتك هنا..." {'required' if required else ''}>
        </div>
        """