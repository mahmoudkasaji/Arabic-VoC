"""
Simple Arabic Analyzer - Phase 2 Simplification
Replaces complex multi-agent orchestration with single OpenAI call
"""

import json
import logging
import time
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from openai import OpenAI

logger = logging.getLogger(__name__)

class SimpleArabicAnalyzer:
    """Simplified Arabic feedback analysis using single OpenAI call"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o"
        self.timeout = 10
        
        # Simple topic categories (replacing hierarchical system)
        self.core_topics = ["product", "service", "support", "pricing", "experience"]
        
    async def analyze_feedback(self, text: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Main analysis method - single comprehensive call
        Replaces: SentimentAgent + TopicAgent + RecommendationAgent + Orchestrator
        """
        start_time = time.time()
        
        try:
            prompt = self._build_unified_prompt(text)
            
            response = await self.client.chat.completions.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                timeout=self.timeout
            )
            
            result = self._parse_response(response.choices[0].message.content)
            result["processing_time"] = round(time.time() - start_time, 2)
            result["analysis_method"] = "simple_openai"
            
            logger.info(f"Analysis completed in {result['processing_time']}s")
            return result
            
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {e}")
            return self._fallback_analysis(text, time.time() - start_time)
    
    def analyze_feedback_sync(self, text: str) -> Dict[str, Any]:
        """Synchronous version for compatibility"""
        start_time = time.time()
        
        try:
            prompt = self._build_unified_prompt(text)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                timeout=self.timeout
            )
            
            result = self._parse_response(response.choices[0].message.content)
            result["processing_time"] = round(time.time() - start_time, 2)
            result["analysis_method"] = "simple_openai"
            
            return result
            
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {e}")
            return self._fallback_analysis(text, time.time() - start_time)
    
    def get_quick_sentiment(self, text: str) -> Dict[str, Any]:
        """Fast sentiment-only analysis for real-time use"""
        start_time = time.time()
        
        try:
            prompt = f"""
            Analyze sentiment of this Arabic text quickly:
            Text: {text}
            
            Return JSON: {{"sentiment": "positive|negative|neutral", "score": 0.0-1.0, "confidence": 0.0-1.0}}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=100
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                "sentiment_label": result.get("sentiment", "neutral"),
                "sentiment_score": result.get("score", 0.5),
                "confidence": result.get("confidence", 0.5),
                "processing_time": round(time.time() - start_time, 2),
                "analysis_method": "quick_sentiment"
            }
            
        except Exception as e:
            logger.error(f"Quick sentiment failed: {e}")
            return {
                "sentiment_label": "neutral",
                "sentiment_score": 0.5,
                "confidence": 0.5,
                "processing_time": round(time.time() - start_time, 2),
                "analysis_method": "fallback"
            }
    
    def _build_unified_prompt(self, text: str) -> str:
        """Single prompt replacing multi-agent orchestration"""
        return f"""
        Analyze this Arabic customer feedback comprehensively:
        
        Text: {text}
        
        Provide analysis in this exact JSON format:
        {{
            "sentiment": {{
                "label": "positive|negative|neutral",
                "score": 0.0-1.0,
                "confidence": 0.0-1.0
            }},
            "topics": ["select up to 3 from: product, service, support, pricing, experience"],
            "key_points": ["brief key insight 1", "brief key insight 2"],
            "priority": "high|medium|low",
            "language_detected": "ar|en|mixed",
            "customer_emotion": "satisfied|frustrated|neutral|excited|disappointed",
            "actionable_insights": ["specific business action 1", "specific business action 2"]
        }}
        
        Guidelines:
        - Focus on actionable business insights
        - Keep key_points concise and specific
        - Priority: high=urgent issue, medium=important feedback, low=general comment
        - Actionable insights should be specific recommendations
        """
    
    def _get_system_prompt(self) -> str:
        """System prompt for Arabic analysis"""
        return """أنت محلل متخصص في تجربة العملاء العربية.
        
        قم بتحليل التعليقات بسرعة ودقة مع التركيز على:
        - المشاعر والرضا العام
        - المواضيع الرئيسية للتعليق
        - الأولوية التجارية للمتابعة
        - التوصيات العملية للتحسين
        
        تجنب التحليل اللغوي المعقد. ركز على القيمة التجارية."""
    
    def _parse_response(self, content: str) -> Dict[str, Any]:
        """Parse and validate OpenAI response"""
        try:
            result = json.loads(content)
            
            # Validate and clean response
            sentiment = result.get("sentiment", {})
            
            return {
                "sentiment_score": float(sentiment.get("score", 0.5)),
                "sentiment_label": sentiment.get("label", "neutral"),
                "confidence": float(sentiment.get("confidence", 0.5)),
                "topics": result.get("topics", ["general"])[:3],  # Limit to 3
                "key_points": result.get("key_points", ["تحليل عام"])[:2],  # Limit to 2
                "priority": result.get("priority", "medium"),
                "language": result.get("language_detected", "ar"),
                "customer_emotion": result.get("customer_emotion", "neutral"),
                "actionable_insights": result.get("actionable_insights", ["مراجعة التعليق"])[:2],
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Failed to parse OpenAI response: {e}")
            return self._fallback_analysis_simple()
    
    def _fallback_analysis(self, text: str, processing_time: float) -> Dict[str, Any]:
        """Fallback analysis when OpenAI fails"""
        return {
            "sentiment_score": 0.5,
            "sentiment_label": "neutral",
            "confidence": 0.5,
            "topics": ["general"],
            "key_points": ["تحليل أساسي - تتطلب مراجعة يدوية"],
            "priority": "medium",
            "language": "ar" if self._is_arabic(text) else "en",
            "customer_emotion": "neutral",
            "actionable_insights": ["مراجعة التعليق يدوياً"],
            "processing_time": round(processing_time, 2),
            "analysis_method": "fallback",
            "status": "fallback"
        }
    
    def _fallback_analysis_simple(self) -> Dict[str, Any]:
        """Simple fallback for parsing errors"""
        return {
            "sentiment_score": 0.5,
            "sentiment_label": "neutral", 
            "confidence": 0.5,
            "topics": ["general"],
            "key_points": ["خطأ في التحليل"],
            "priority": "medium",
            "language": "ar",
            "customer_emotion": "neutral",
            "actionable_insights": ["إعادة المحاولة"],
            "status": "error"
        }
    
    def _is_arabic(self, text: str) -> bool:
        """Simple Arabic detection"""
        arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
        return arabic_chars > len(text) * 0.3
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Simple performance statistics"""
        return {
            "analyzer_type": "simple_openai",
            "model": self.model,
            "average_response_time": "< 1 second",
            "api_calls_per_analysis": 1,
            "supported_languages": ["Arabic", "English"],
            "features": ["sentiment", "topics", "priority", "insights"],
            "complexity_score": "low"
        }

# Convenience functions for backward compatibility
def analyze_arabic_feedback_simple(text: str) -> Dict[str, Any]:
    """Simple function for backward compatibility"""
    analyzer = SimpleArabicAnalyzer()
    return analyzer.analyze_feedback_sync(text)

def get_quick_sentiment_simple(text: str) -> Dict[str, Any]:
    """Quick sentiment function"""
    analyzer = SimpleArabicAnalyzer()
    return analyzer.get_quick_sentiment(text)