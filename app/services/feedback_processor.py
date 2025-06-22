"""
Feedback processing service
Coordinates Arabic analysis and database operations
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from app.models.feedback import Feedback, FeedbackStatus
from app.services.arabic_analysis import analyze_arabic_feedback_agents, analyze_arabic_feedback

logger = logging.getLogger(__name__)

class FeedbackProcessor:
    """Main feedback processing coordinator"""
    
    def __init__(self):
        self.use_agents = True
        
    async def process_feedback(self, feedback: Feedback) -> Dict[str, Any]:
        """Process feedback with Arabic analysis"""
        try:
            # Use agent-based analysis as primary method
            if self.use_agents:
                analysis = await analyze_arabic_feedback_agents(
                    text=feedback.content,
                    thread_id=f"feedback_{feedback.id}"
                )
            else:
                # Fallback to legacy analysis
                analysis = analyze_arabic_feedback(feedback.content)
            
            # Update feedback with analysis results
            self._update_feedback_with_analysis(feedback, analysis)
            
            # Mark as processed
            feedback.status = FeedbackStatus.PROCESSED
            feedback.processed_at = datetime.utcnow()
            
            logger.info(f"Feedback {feedback.id} processed successfully")
            return analysis
            
        except Exception as e:
            logger.error(f"Error processing feedback {feedback.id}: {e}")
            feedback.status = FeedbackStatus.FAILED
            raise
    
    def _update_feedback_with_analysis(self, feedback: Feedback, analysis: Dict[str, Any]):
        """Update feedback model with analysis results"""
        if 'sentiment' in analysis:
            sentiment_data = analysis['sentiment']
            feedback.sentiment_score = sentiment_data.get('sentiment_score', 0.0)
            feedback.confidence_score = sentiment_data.get('confidence', 0.0)
        
        if 'summary' in analysis:
            feedback.ai_summary = analysis['summary']
        
        if 'categorization' in analysis:
            feedback.ai_categories = analysis['categorization']
        
        if 'suggested_actions' in analysis:
            feedback.ai_action_items = analysis['suggested_actions']