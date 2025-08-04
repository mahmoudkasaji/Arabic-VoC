"""
Enhanced Text Analytics - Phase 3A Implementation
Extends SimpleArabicAnalyzer with emotion detection and topic categorization
"""

import json
import logging
import time
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from openai import OpenAI
from simple_arabic_analyzer import SimpleArabicAnalyzer

logger = logging.getLogger(__name__)

class EnhancedTextAnalytics(SimpleArabicAnalyzer):
    """Enhanced Arabic text analysis with emotion detection and topic categorization"""
    
    def __init__(self):
        super().__init__()
        
        # Enhanced emotion categories (Arabic cultural context)
        self.emotion_categories = {
            "سعادة": ["happy", "joy", "pleased", "satisfied", "content", "grateful"],
            "إحباط": ["frustrated", "annoyed", "disappointed", "upset", "irritated"],
            "قلق": ["confused", "uncertain", "worried", "concerned", "anxious"],
            "رضا": ["satisfied", "pleased", "content", "approving", "positive"],
            "غضب": ["angry", "furious", "mad", "outraged", "indignant"],
            "حزن": ["sad", "depressed", "unhappy", "melancholy", "sorrowful"]
        }
        
        # Business topic categories (expanded from core topics)
        self.business_topics = {
            "product": ["منتج", "سلعة", "جودة", "ميزة", "وظيفة", "أداء"],
            "service": ["خدمة", "دعم", "مساعدة", "استجابة", "تجربة"],
            "pricing": ["سعر", "تكلفة", "رسوم", "قيمة", "مال", "دفع"],
            "support": ["دعم فني", "مساعدة", "حل", "مشكلة", "استفسار"],
            "experience": ["تجربة", "شعور", "انطباع", "رأي", "تقييم"],
            "delivery": ["توصيل", "شحن", "تسليم", "وقت", "سرعة"],
            "interface": ["واجهة", "تصميم", "استخدام", "سهولة", "تطبيق"],
            "communication": ["تواصل", "رد", "معلومات", "وضوح", "شرح"]
        }
    
    def analyze_with_emotions_and_topics(self, text: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Enhanced analysis with emotion detection and topic categorization
        Processes both Arabic and English text with cultural context
        """
        start_time = time.time()
        
        try:
            # Build enhanced prompt for emotion and topic analysis
            prompt = self._build_enhanced_prompt(text)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_enhanced_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                timeout=5.0
            )
            
            content = response.choices[0].message.content
            if content is None:
                raise ValueError("Empty response from OpenAI")
            result = self._parse_enhanced_response(content)
            result["processing_time"] = round(time.time() - start_time, 2)
            result["analysis_method"] = "enhanced_openai"
            result["original_text"] = text
            
            logger.info(f"Enhanced analysis completed in {result['processing_time']}s")
            return result
            
        except Exception as e:
            logger.error(f"Enhanced analysis failed: {e}")
            # Fallback to basic analysis
            basic_result = self.analyze_feedback_sync(text)
            basic_result["emotions"] = self._extract_emotions_fallback(text)
            basic_result["topics"] = self._extract_topics_fallback(text)
            return basic_result
    
    def _build_enhanced_prompt(self, text: str) -> str:
        """Build comprehensive prompt for emotion and topic analysis"""
        return f"""
Analyze this customer feedback for emotions and business topics.

Text: "{text}"

Please provide detailed analysis including:
1. Primary emotion and confidence level
2. Secondary emotions if present
3. Business topics/themes identified
4. Sentiment (positive/negative/neutral) with score
5. Key themes and actionable insights

Consider both Arabic and English cultural contexts for emotion detection.
Focus on business-relevant topics like product, service, pricing, support, experience.
"""
    
    def _get_enhanced_system_prompt(self) -> str:
        """Enhanced system prompt for emotion and topic analysis"""
        return """You are an expert Arabic/English text analyst specializing in customer feedback analysis with cultural sensitivity.

Your task is to analyze customer feedback and provide structured JSON output with:

1. EMOTIONS: Detect specific emotions with cultural context
   - Primary emotion with confidence score (0-1)
   - Secondary emotions if present
   - Consider Arabic cultural expressions and nuances

2. TOPICS: Identify business-relevant topics/themes
   - Categorize into business areas: product, service, pricing, support, experience, delivery, interface, communication
   - Extract specific themes and keywords
   - Identify actionable insights

3. SENTIMENT: Overall sentiment analysis
   - Score (-1 to +1): negative to positive
   - Confidence level (0-1)
   - Brief reasoning

4. INSIGHTS: Actionable business insights
   - Key points for improvement
   - Positive aspects to maintain
   - Recommendations for action

Return valid JSON with this structure:
{
  "primary_emotion": {"emotion": "string", "confidence": float, "reasoning": "string"},
  "secondary_emotions": [{"emotion": "string", "confidence": float}],
  "topics": [{"category": "string", "keywords": ["string"], "relevance": float}],
  "sentiment": {"score": float, "label": "string", "confidence": float, "reasoning": "string"},
  "insights": {
    "key_points": ["string"],
    "positive_aspects": ["string"],
    "improvement_areas": ["string"],
    "recommended_actions": ["string"]
  },
  "keywords": ["string"],
  "language_detected": "string"
}"""
    
    def _parse_enhanced_response(self, response_content: str) -> Dict[str, Any]:
        """Parse enhanced OpenAI response with error handling"""
        try:
            data = json.loads(response_content)
            
            # Ensure all required fields are present
            result = {
                "primary_emotion": data.get("primary_emotion", {"emotion": "neutral", "confidence": 0.5, "reasoning": "Unable to detect"}),
                "secondary_emotions": data.get("secondary_emotions", []),
                "topics": data.get("topics", []),
                "sentiment": data.get("sentiment", {"score": 0.0, "label": "neutral", "confidence": 0.5, "reasoning": "Unable to analyze"}),
                "insights": data.get("insights", {
                    "key_points": [],
                    "positive_aspects": [],
                    "improvement_areas": [],
                    "recommended_actions": []
                }),
                "keywords": data.get("keywords", []),
                "language_detected": data.get("language_detected", "unknown")
            }
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse enhanced response: {e}")
            return self._fallback_enhanced_analysis()
    
    def _extract_emotions_fallback(self, text: str) -> List[Dict[str, Any]]:
        """Fallback emotion detection using keyword matching"""
        detected_emotions = []
        text_lower = text.lower()
        
        for emotion_ar, emotion_keywords in self.emotion_categories.items():
            confidence = 0.0
            matched_keywords = []
            
            for keyword in emotion_keywords:
                if keyword in text_lower:
                    confidence += 0.2
                    matched_keywords.append(keyword)
            
            # Check for Arabic emotion words
            if any(word in text for word in ["سعيد", "مبسوط", "راضي", "شكرا"]):
                if emotion_ar == "سعادة":
                    confidence += 0.4
            elif any(word in text for word in ["زعلان", "مضايق", "مشكلة", "سيء"]):
                if emotion_ar == "إحباط":
                    confidence += 0.4
            
            if confidence > 0.3:
                detected_emotions.append({
                    "emotion": emotion_ar,
                    "confidence": min(confidence, 1.0),
                    "keywords": matched_keywords
                })
        
        return detected_emotions
    
    def _extract_topics_fallback(self, text: str) -> List[Dict[str, Any]]:
        """Fallback topic extraction using keyword matching"""
        detected_topics = []
        text_lower = text.lower()
        
        for topic, keywords in self.business_topics.items():
            relevance = 0.0
            matched_keywords = []
            
            for keyword in keywords:
                if keyword in text_lower or keyword in text:
                    relevance += 0.2
                    matched_keywords.append(keyword)
            
            if relevance > 0.2:
                detected_topics.append({
                    "category": topic,
                    "keywords": matched_keywords,
                    "relevance": min(relevance, 1.0)
                })
        
        return detected_topics
    
    def _fallback_enhanced_analysis(self) -> Dict[str, Any]:
        """Fallback analysis structure when OpenAI fails"""
        return {
            "primary_emotion": {"emotion": "neutral", "confidence": 0.5, "reasoning": "Analysis failed, using fallback"},
            "secondary_emotions": [],
            "topics": [],
            "sentiment": {"score": 0.0, "label": "neutral", "confidence": 0.5, "reasoning": "Fallback analysis"},
            "insights": {
                "key_points": ["Analysis service temporarily unavailable"],
                "positive_aspects": [],
                "improvement_areas": ["Improve analysis service reliability"],
                "recommended_actions": ["Retry analysis when service is available"]
            },
            "keywords": [],
            "language_detected": "unknown"
        }
    
    def process_historical_responses(self, responses: List[Dict]) -> List[Dict[str, Any]]:
        """
        Process historical survey responses with enhanced analytics
        Used for retroactive analysis of existing survey data
        """
        processed_responses = []
        
        for response in responses:
            try:
                # Extract text from response answers
                if isinstance(response.get('answers'), str):
                    answers_data = json.loads(response['answers'])
                else:
                    answers_data = response.get('answers', {})
                
                # Combine all text responses
                text_responses = []
                for question_id, answer in answers_data.items():
                    if isinstance(answer, str) and len(answer.strip()) > 0:
                        text_responses.append(answer.strip())
                
                combined_text = " ".join(text_responses)
                
                if combined_text:
                    # Perform enhanced analysis
                    analysis = self.analyze_with_emotions_and_topics(combined_text)
                    analysis['response_id'] = response.get('id')
                    analysis['survey_id'] = response.get('survey_id')
                    analysis['created_at'] = response.get('created_at')
                    
                    processed_responses.append(analysis)
                    
                    logger.info(f"Processed response {response.get('id')} with {len(analysis.get('topics', []))} topics")
                
            except Exception as e:
                logger.error(f"Failed to process response {response.get('id')}: {e}")
                continue
        
        return processed_responses