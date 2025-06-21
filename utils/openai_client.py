"""
OpenAI client for Arabic feedback analysis
Integrates with OpenAI API for advanced Arabic text processing
"""

import json
import os
import logging
from typing import Dict, Any, Optional, List
from openai import OpenAI

logger = logging.getLogger(__name__)

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "default_key")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

class ArabicFeedbackAnalyzer:
    """Advanced Arabic feedback analysis using OpenAI"""
    
    def __init__(self):
        self.model = "gpt-4o"  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
        
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of Arabic feedback text"""
        try:
            prompt = f"""
            أنت خبير في تحليل المشاعر للنصوص العربية. حلل النص التالي وحدد المشاعر والتقييم.
            
            النص: {text}
            
            يرجى تحليل النص وإرجاع النتيجة بصيغة JSON مع الحقول التالية:
            - sentiment_score: رقم من -1 إلى 1 (-1 سلبي جداً، 0 محايد، 1 إيجابي جداً)
            - confidence: مستوى الثقة من 0 إلى 1
            - emotion: المشاعر الرئيسية (فرح، غضب، حزن، إعجاب، إحباط، محايد)
            - intensity: شدة المشاعر (عالي، متوسط، منخفض)
            - reasoning: تفسير قصير للتحليل
            """
            
            response = openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "أنت مختص في تحليل المشاعر للنصوص العربية. قدم تحليلاً دقيقاً ومفصلاً."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                "sentiment_score": float(result.get("sentiment_score", 0)),
                "confidence": float(result.get("confidence", 0)),
                "emotion": result.get("emotion", "محايد"),
                "intensity": result.get("intensity", "منخفض"),
                "reasoning": result.get("reasoning", "")
            }
            
        except Exception as e:
            logger.error(f"Error in Arabic sentiment analysis: {str(e)}")
            return {
                "sentiment_score": 0.0,
                "confidence": 0.0,
                "emotion": "غير محدد",
                "intensity": "منخفض",
                "reasoning": "خطأ في التحليل"
            }
    
    def categorize_feedback(self, text: str) -> Dict[str, Any]:
        """Categorize Arabic feedback into business categories"""
        try:
            prompt = f"""
            أنت خبير في تصنيف التعليقات والملاحظات في مجال خدمة العملاء. صنف النص التالي:
            
            النص: {text}
            
            صنف النص إلى فئات الأعمال التالية وأرجع النتيجة بصيغة JSON:
            - primary_category: الفئة الرئيسية (خدمة العملاء، المنتج، التسعير، التسليم، التقنية، أخرى)
            - secondary_categories: فئات فرعية (قائمة)
            - topics: المواضيع المحددة المذكورة (قائمة)
            - urgency_level: مستوى الأولوية (عالي، متوسط، منخفض)
            - requires_action: هل يتطلب إجراء فوري (true/false)
            - customer_type: نوع العميل المحتمل (جديد، حالي، سابق، غير محدد)
            """
            
            response = openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "أنت مختص في تصنيف تعليقات العملاء وتحديد الأولويات."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                "primary_category": result.get("primary_category", "أخرى"),
                "secondary_categories": result.get("secondary_categories", []),
                "topics": result.get("topics", []),
                "urgency_level": result.get("urgency_level", "منخفض"),
                "requires_action": result.get("requires_action", False),
                "customer_type": result.get("customer_type", "غير محدد")
            }
            
        except Exception as e:
            logger.error(f"Error in Arabic feedback categorization: {str(e)}")
            return {
                "primary_category": "غير محدد",
                "secondary_categories": [],
                "topics": [],
                "urgency_level": "منخفض",
                "requires_action": False,
                "customer_type": "غير محدد"
            }
    
    def generate_summary(self, text: str) -> str:
        """Generate Arabic summary of feedback"""
        try:
            prompt = f"""
            لخص التعليق التالي في جملتين أو ثلاث جمل مع الحفاظ على النقاط الرئيسية:
            
            {text}
            
            الملخص يجب أن يكون:
            - واضح ومفهوم
            - يحتوي على النقاط الرئيسية
            - باللغة العربية الفصحى
            - لا يتجاوز 100 كلمة
            """
            
            response = openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "أنت مختص في تلخيص النصوص العربية بطريقة واضحة ومفيدة."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating Arabic summary: {str(e)}")
            return "لا يمكن إنشاء ملخص في الوقت الحالي"
    
    def suggest_actions(self, text: str, categories: Dict[str, Any]) -> List[str]:
        """Suggest action items based on feedback analysis"""
        try:
            urgency = categories.get("urgency_level", "منخفض")
            category = categories.get("primary_category", "أخرى")
            requires_action = categories.get("requires_action", False)
            
            prompt = f"""
            بناءً على تحليل التعليق التالي، اقترح إجراءات محددة وقابلة للتنفيذ:
            
            النص: {text}
            الفئة: {category}
            مستوى الأولوية: {urgency}
            يتطلب إجراء فوري: {requires_action}
            
            اقترح 2-4 إجراءات محددة بصيغة JSON كقائمة من النصوص:
            - إجراءات فورية إذا كانت مطلوبة
            - إجراءات تحسينية
            - متابعة مع العميل إذا لزم الأمر
            - إجراءات وقائية لتجنب تكرار المشكلة
            
            أرجع النتيجة بصيغة: {"actions": ["إجراء 1", "إجراء 2", ...]}
            """
            
            response = openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "أنت مستشار خدمة عملاء محترف تقترح إجراءات عملية وقابلة للتنفيذ."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.4
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("actions", [])
            
        except Exception as e:
            logger.error(f"Error suggesting actions: {str(e)}")
            return ["مراجعة التعليق وتحديد الإجراءات المناسبة"]

# Global analyzer instance
arabic_analyzer = ArabicFeedbackAnalyzer()

def analyze_arabic_feedback(text: str) -> Dict[str, Any]:
    """Complete analysis of Arabic feedback text"""
    try:
        logger.info(f"Starting comprehensive analysis of Arabic feedback")
        
        # Run sentiment analysis
        sentiment_data = arabic_analyzer.analyze_sentiment(text)
        
        # Run categorization
        category_data = arabic_analyzer.categorize_feedback(text)
        
        # Generate summary
        summary = arabic_analyzer.generate_summary(text)
        
        # Suggest actions if needed
        actions = []
        if category_data.get("requires_action", False):
            actions = arabic_analyzer.suggest_actions(text, category_data)
        
        # Combine all analysis results
        analysis_result = {
            "summary": summary,
            "sentiment": sentiment_data,
            "categorization": category_data,
            "suggested_actions": actions,
            "analysis_timestamp": "2024-01-01T00:00:00Z",  # Would use actual timestamp
            "model_used": arabic_analyzer.model
        }
        
        logger.info(f"Completed Arabic feedback analysis")
        return analysis_result
        
    except Exception as e:
        logger.error(f"Error in comprehensive Arabic feedback analysis: {str(e)}")
        return {
            "summary": "خطأ في تحليل التعليق",
            "sentiment": {
                "sentiment_score": 0.0,
                "confidence": 0.0,
                "emotion": "غير محدد",
                "intensity": "منخفض",
                "reasoning": "خطأ في التحليل"
            },
            "categorization": {
                "primary_category": "غير محدد",
                "secondary_categories": [],
                "topics": [],
                "urgency_level": "منخفض",
                "requires_action": False,
                "customer_type": "غير محدد"
            },
            "suggested_actions": [],
            "analysis_timestamp": "2024-01-01T00:00:00Z",
            "model_used": arabic_analyzer.model,
            "error": str(e)
        }

def batch_analyze_feedback(feedback_list: List[str]) -> List[Dict[str, Any]]:
    """Analyze multiple feedback texts in batch"""
    results = []
    
    for text in feedback_list:
        try:
            analysis = analyze_arabic_feedback(text)
            results.append(analysis)
        except Exception as e:
            logger.error(f"Error in batch analysis: {str(e)}")
            results.append({
                "error": str(e),
                "text": text[:100] + "..." if len(text) > 100 else text
            })
    
    return results
