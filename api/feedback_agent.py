"""
Agent-based feedback processing API
Uses LangGraph orchestration for efficient Arabic analysis
"""

import asyncio
import logging
from typing import Dict, Any
from flask import Flask, request, jsonify
from datetime import datetime

from utils.arabic_agent_orchestrator import analyze_arabic_feedback_agents
from utils.openai_client import analyze_arabic_feedback  # Fallback

logger = logging.getLogger(__name__)

class FeedbackProcessor:
    """Agent-based feedback processor with fallback"""
    
    def __init__(self):
        self.use_agents = True
        
    async def process_feedback(self, content: str, channel: str = "api", **kwargs) -> Dict[str, Any]:
        """Process feedback using agent orchestration"""
        try:
            if self.use_agents:
                # Use LangGraph agent orchestration
                analysis = await analyze_arabic_feedback_agents(
                    text=content,
                    thread_id=f"feedback_{datetime.now().timestamp()}"
                )
                
                # Add processing metadata
                analysis.update({
                    "channel": channel,
                    "processing_method": "langgraph_agents",
                    "timestamp": datetime.now().isoformat()
                })
                
                return analysis
            else:
                # Fallback to legacy analysis
                return self._fallback_analysis(content, channel)
                
        except Exception as e:
            logger.error(f"Agent processing failed: {e}")
            # Always fallback gracefully
            return self._fallback_analysis(content, channel, error=str(e))
    
    def _fallback_analysis(self, content: str, channel: str, error: str = None) -> Dict[str, Any]:
        """Fallback to legacy analysis method"""
        try:
            analysis = analyze_arabic_feedback(content)
            analysis.update({
                "channel": channel,
                "processing_method": "legacy_openai",
                "fallback_reason": error,
                "timestamp": datetime.now().isoformat()
            })
            return analysis
        except Exception as e:
            logger.error(f"Fallback analysis also failed: {e}")
            return self._emergency_fallback(content, channel, str(e))
    
    def _emergency_fallback(self, content: str, channel: str, error: str) -> Dict[str, Any]:
        """Emergency fallback when all analysis fails"""
        return {
            "summary": "تعذر تحليل التعليق تلقائياً",
            "sentiment": {
                "sentiment_score": 0.0,
                "confidence": 0.0,
                "emotion": "غير محدد",
                "intensity": "منخفض",
                "reasoning": f"خطأ في النظام: {error}"
            },
            "categorization": {
                "primary_category": "يتطلب مراجعة يدوية",
                "secondary_categories": [],
                "topics": [],
                "urgency_level": "متوسط",
                "requires_action": True,
                "customer_type": "غير محدد"
            },
            "suggested_actions": ["مراجعة يدوية ضرورية", "تصعيد للفريق التقني"],
            "channel": channel,
            "processing_method": "emergency_fallback",
            "error": error,
            "timestamp": datetime.now().isoformat()
        }

# Global processor instance
feedback_processor = FeedbackProcessor()

async def analyze_feedback_with_agents(content: str, **kwargs) -> Dict[str, Any]:
    """Main API function for agent-based feedback analysis"""
    return await feedback_processor.process_feedback(content, **kwargs)

def batch_analyze_with_agents(feedback_list: list) -> list:
    """Batch analysis using agent orchestration"""
    async def process_batch():
        tasks = [
            feedback_processor.process_feedback(
                content=item.get("content", ""),
                channel=item.get("channel", "batch"),
                feedback_id=item.get("id")
            )
            for item in feedback_list
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    # Run async batch processing
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        results = loop.run_until_complete(process_batch())
        return results
    finally:
        loop.close()

# Performance comparison utilities
class AnalysisComparison:
    """Compare agent vs legacy analysis performance"""
    
    @staticmethod
    async def compare_methods(text: str) -> Dict[str, Any]:
        """Compare agent vs legacy analysis"""
        start_time = datetime.now()
        
        # Agent-based analysis
        agent_start = datetime.now()
        try:
            agent_result = await analyze_arabic_feedback_agents(text)
            agent_time = (datetime.now() - agent_start).total_seconds()
            agent_success = True
        except Exception as e:
            agent_result = {"error": str(e)}
            agent_time = (datetime.now() - agent_start).total_seconds()
            agent_success = False
        
        # Legacy analysis
        legacy_start = datetime.now()
        try:
            legacy_result = analyze_arabic_feedback(text)
            legacy_time = (datetime.now() - legacy_start).total_seconds()
            legacy_success = True
        except Exception as e:
            legacy_result = {"error": str(e)}
            legacy_time = (datetime.now() - legacy_start).total_seconds()
            legacy_success = False
        
        total_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "input_text": text,
            "agent_analysis": {
                "result": agent_result,
                "execution_time": agent_time,
                "success": agent_success,
                "method": "langgraph_agents"
            },
            "legacy_analysis": {
                "result": legacy_result,
                "execution_time": legacy_time,
                "success": legacy_success,
                "method": "direct_openai"
            },
            "performance_comparison": {
                "agent_faster": agent_time < legacy_time,
                "time_difference": abs(agent_time - legacy_time),
                "total_comparison_time": total_time
            },
            "recommendation": (
                "Use agents" if agent_success and agent_time <= legacy_time * 1.2
                else "Use legacy" if legacy_success
                else "Manual review required"
            )
        }

if __name__ == "__main__":
    # Test the agent system
    async def test_agents():
        test_texts = [
            "الخدمة ممتازة جداً وأنصح بها للجميع",
            "للأسف الخدمة سيئة ولا أنصح بها",
            "التطبيق جيد ولكن يحتاج تحسينات"
        ]
        
        for text in test_texts:
            print(f"\n--- Testing: {text[:30]}... ---")
            try:
                result = await analyze_feedback_with_agents(text)
                print(f"✅ Success: {result['processing_method']}")
                print(f"Sentiment: {result['sentiment']['emotion']}")
                print(f"Category: {result['categorization']['primary_category']}")
            except Exception as e:
                print(f"❌ Failed: {e}")
    
    # Run test
    asyncio.run(test_agents())