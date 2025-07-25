"""
Live Analytics Data Processor
Connects real survey data to dashboard metrics with multilingual text analytics
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session
from app import db
from models.survey_flask import SurveyFlask, ResponseFlask, QuestionResponseFlask, QuestionFlask
import logging

logger = logging.getLogger(__name__)


class LiveAnalyticsProcessor:
    """Processes live survey data for analytics dashboard"""
    
    def __init__(self):
        self.db = db.session
    
    def get_dashboard_metrics(self, time_range: str = "7d") -> Dict[str, Any]:
        """
        Calculate live dashboard metrics from real survey data
        
        Args:
            time_range: "1d", "7d", "30d", "all"
        
        Returns:
            Dict with CSAT, volume, sentiment, completion metrics
        """
        try:
            # Calculate time filter
            start_date = self._get_start_date(time_range)
            
            # Base query for responses in time range
            base_query = self.db.query(ResponseFlask)
            if start_date:
                base_query = base_query.filter(ResponseFlask.created_at >= start_date)
            
            # 1. CSAT Score - from rating questions
            csat_score = self._calculate_csat_score(start_date)
            
            # 2. Response Volume
            total_responses = base_query.count()
            previous_period_responses = self._get_previous_period_responses(time_range)
            response_change = self._calculate_percentage_change(total_responses, previous_period_responses)
            
            # 3. Sentiment Score - from text analytics
            sentiment_data = self._calculate_sentiment_metrics(start_date)
            
            # 4. Completion Rate
            completion_data = self._calculate_completion_metrics(start_date)
            
            # 5. Channel Performance
            channel_performance = self._get_channel_performance(start_date)
            
            return {
                "csat": {
                    "score": csat_score["average"],
                    "count": csat_score["total_ratings"],
                    "change_percentage": csat_score["change_percentage"],
                    "trend": "up" if csat_score["change_percentage"] > 0 else "down" if csat_score["change_percentage"] < 0 else "stable"
                },
                "responses": {
                    "total": total_responses,
                    "change_percentage": response_change,
                    "trend": "up" if response_change > 0 else "down" if response_change < 0 else "stable"
                },
                "sentiment": {
                    "score": sentiment_data["average_sentiment"],
                    "confidence": sentiment_data["average_confidence"],
                    "distribution": sentiment_data["distribution"],
                    "change_percentage": sentiment_data["change_percentage"]
                },
                "completion": {
                    "rate": completion_data["completion_rate"],
                    "average_duration": completion_data["average_duration"],
                    "change_percentage": completion_data["change_percentage"]
                },
                "channels": channel_performance,
                "last_updated": datetime.utcnow().isoformat(),
                "time_range": time_range
            }
            
        except Exception as e:
            logger.error(f"Error calculating dashboard metrics: {e}")
            return self._get_fallback_metrics()
    
    def get_insights_feed(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get real-time insights feed from recent responses
        
        Args:
            limit: Maximum number of insights to return
            
        Returns:
            List of recent response insights with text analytics
        """
        try:
            # Get recent responses with text content
            recent_responses = self.db.query(QuestionResponseFlask)\
                .join(ResponseFlask)\
                .join(QuestionFlask)\
                .filter(
                    QuestionResponseFlask.answer_text.isnot(None),
                    QuestionResponseFlask.answer_text != ""
                )\
                .order_by(QuestionResponseFlask.created_at.desc())\
                .limit(limit).all()
            
            insights = []
            for response in recent_responses:
                # Get survey and question context
                survey_response = response.response
                question = response.question
                survey = survey_response.survey
                
                # Determine sentiment
                sentiment = self._classify_sentiment(response.sentiment_score) if response.sentiment_score else "neutral"
                
                # Extract keywords
                keywords = self._extract_keywords(response.answer_text)
                
                insight = {
                    "id": response.id,
                    "survey_id": survey.id,
                    "survey_title": survey.display_title,
                    "question_text": question.display_text,
                    "response_text": response.answer_text,
                    "sentiment": sentiment,
                    "sentiment_score": response.sentiment_score,
                    "confidence_score": response.confidence_score,
                    "keywords": keywords,
                    "respondent_name": survey_response.respondent_name or "مجهول",
                    "device_type": survey_response.device_type or "غير محدد",
                    "language_used": survey_response.language_used,
                    "created_at": response.created_at.isoformat(),
                    "time_ago": self._format_time_ago(response.created_at)
                }
                insights.append(insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting insights feed: {e}")
            return []
    
    def get_trending_topics(self, time_range: str = "7d", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get trending topics from text analytics of recent responses
        
        Args:
            time_range: Time period to analyze
            limit: Maximum number of topics to return
            
        Returns:
            List of trending topics with frequency and sentiment
        """
        try:
            start_date = self._get_start_date(time_range)
            
            # Get text responses in time range
            text_responses = self.db.query(QuestionResponseFlask)\
                .join(ResponseFlask)\
                .filter(
                    QuestionResponseFlask.answer_text.isnot(None),
                    QuestionResponseFlask.answer_text != ""
                )
            
            if start_date:
                text_responses = text_responses.filter(ResponseFlask.created_at >= start_date)
            
            text_responses = text_responses.all()
            
            # Extract and count keywords
            keyword_counts = {}
            keyword_sentiments = {}
            
            for response in text_responses:
                keywords = self._extract_keywords(response.answer_text)
                sentiment = response.sentiment_score or 0.0
                
                for keyword in keywords:
                    if keyword not in keyword_counts:
                        keyword_counts[keyword] = 0
                        keyword_sentiments[keyword] = []
                    
                    keyword_counts[keyword] += 1
                    keyword_sentiments[keyword].append(sentiment)
            
            # Sort by frequency and calculate average sentiment
            trending_topics = []
            for keyword, count in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:limit]:
                avg_sentiment = sum(keyword_sentiments[keyword]) / len(keyword_sentiments[keyword])
                
                trending_topics.append({
                    "topic": keyword,
                    "frequency": count,
                    "percentage": round((count / len(text_responses)) * 100, 1) if text_responses else 0,
                    "sentiment": self._classify_sentiment(avg_sentiment),
                    "sentiment_score": round(avg_sentiment, 2),
                    "trend": "up"  # Could be enhanced with historical comparison
                })
            
            return trending_topics
            
        except Exception as e:
            logger.error(f"Error getting trending topics: {e}")
            return []
    
    def _calculate_csat_score(self, start_date: Optional[datetime]) -> Dict[str, Any]:
        """Calculate CSAT score from rating questions"""
        try:
            # Find rating questions (type = 'rating' or 'nps')
            rating_query = self.db.query(QuestionResponseFlask)\
                .join(ResponseFlask)\
                .join(QuestionFlask)\
                .filter(
                    or_(
                        QuestionFlask.type == "rating",
                        QuestionFlask.type == "nps"
                    ),
                    QuestionResponseFlask.answer_number.isnot(None)
                )
            
            if start_date:
                rating_query = rating_query.filter(ResponseFlask.created_at >= start_date)
            
            ratings = rating_query.all()
            
            if not ratings:
                return {"average": 0.0, "total_ratings": 0, "change_percentage": 0.0}
            
            # Calculate average rating
            total_score = sum(r.answer_number for r in ratings)
            average_score = total_score / len(ratings)
            
            # Convert to percentage (assuming 5-point scale)
            csat_percentage = (average_score / 5) * 100
            
            # Calculate change from previous period
            previous_csat = self._get_previous_period_csat(start_date)
            change_percentage = self._calculate_percentage_change(csat_percentage, previous_csat)
            
            return {
                "average": round(csat_percentage, 1),
                "total_ratings": len(ratings),
                "change_percentage": change_percentage
            }
            
        except Exception as e:
            logger.error(f"Error calculating CSAT: {e}")
            return {"average": 0.0, "total_ratings": 0, "change_percentage": 0.0}
    
    def _calculate_sentiment_metrics(self, start_date: Optional[datetime]) -> Dict[str, Any]:
        """Calculate sentiment metrics from text analytics"""
        try:
            sentiment_query = self.db.query(QuestionResponseFlask)\
                .join(ResponseFlask)\
                .filter(
                    QuestionResponseFlask.sentiment_score.isnot(None),
                    QuestionResponseFlask.answer_text.isnot(None)
                )
            
            if start_date:
                sentiment_query = sentiment_query.filter(ResponseFlask.created_at >= start_date)
            
            sentiment_responses = sentiment_query.all()
            
            if not sentiment_responses:
                return {
                    "average_sentiment": 0.0,
                    "average_confidence": 0.0,
                    "distribution": {"positive": 0, "neutral": 0, "negative": 0},
                    "change_percentage": 0.0
                }
            
            # Calculate averages
            total_sentiment = sum(r.sentiment_score for r in sentiment_responses)
            avg_sentiment = total_sentiment / len(sentiment_responses)
            
            total_confidence = sum(r.confidence_score or 0.0 for r in sentiment_responses)
            avg_confidence = total_confidence / len(sentiment_responses)
            
            # Calculate distribution
            distribution = {"positive": 0, "neutral": 0, "negative": 0}
            for response in sentiment_responses:
                sentiment_class = self._classify_sentiment(response.sentiment_score)
                distribution[sentiment_class] += 1
            
            # Convert to percentages
            total_count = len(sentiment_responses)
            distribution = {
                key: round((count / total_count) * 100, 1)
                for key, count in distribution.items()
            }
            
            # Calculate change from previous period
            previous_sentiment = self._get_previous_period_sentiment(start_date)
            change_percentage = self._calculate_percentage_change(avg_sentiment, previous_sentiment)
            
            return {
                "average_sentiment": round(avg_sentiment, 2),
                "average_confidence": round(avg_confidence, 2),
                "distribution": distribution,
                "change_percentage": change_percentage
            }
            
        except Exception as e:
            logger.error(f"Error calculating sentiment metrics: {e}")
            return {
                "average_sentiment": 0.0,
                "average_confidence": 0.0,
                "distribution": {"positive": 0, "neutral": 0, "negative": 0},
                "change_percentage": 0.0
            }
    
    def _calculate_completion_metrics(self, start_date: Optional[datetime]) -> Dict[str, Any]:
        """Calculate completion rate and duration metrics"""
        try:
            completion_query = self.db.query(ResponseFlask)
            
            if start_date:
                completion_query = completion_query.filter(ResponseFlask.created_at >= start_date)
            
            all_responses = completion_query.all()
            
            if not all_responses:
                return {"completion_rate": 0.0, "average_duration": 0.0, "change_percentage": 0.0}
            
            # Calculate completion rate
            completed_responses = [r for r in all_responses if r.is_complete]
            completion_rate = (len(completed_responses) / len(all_responses)) * 100
            
            # Calculate average duration
            durations = [r.duration_minutes for r in completed_responses if r.duration_minutes]
            avg_duration = sum(durations) / len(durations) if durations else 0.0
            
            # Calculate change from previous period
            previous_completion = self._get_previous_period_completion(start_date)
            change_percentage = self._calculate_percentage_change(completion_rate, previous_completion)
            
            return {
                "completion_rate": round(completion_rate, 1),
                "average_duration": round(avg_duration, 1),
                "change_percentage": change_percentage
            }
            
        except Exception as e:
            logger.error(f"Error calculating completion metrics: {e}")
            return {"completion_rate": 0.0, "average_duration": 0.0, "change_percentage": 0.0}
    
    def _get_channel_performance(self, start_date: Optional[datetime]) -> List[Dict[str, Any]]:
        """Get performance metrics by channel"""
        try:
            channel_query = self.db.query(ResponseFlask)
            
            if start_date:
                channel_query = channel_query.filter(ResponseFlask.created_at >= start_date)
            
            responses = channel_query.all()
            
            # Group by device type (proxy for channel)
            channels = {}
            for response in responses:
                channel = response.device_type or "غير محدد"
                if channel not in channels:
                    channels[channel] = {
                        "responses": 0,
                        "completed": 0,
                        "total_duration": 0,
                        "duration_count": 0
                    }
                
                channels[channel]["responses"] += 1
                if response.is_complete:
                    channels[channel]["completed"] += 1
                if response.duration_minutes:
                    channels[channel]["total_duration"] += response.duration_minutes
                    channels[channel]["duration_count"] += 1
            
            # Calculate metrics for each channel
            channel_performance = []
            for channel, data in channels.items():
                completion_rate = (data["completed"] / data["responses"]) * 100 if data["responses"] > 0 else 0
                avg_duration = data["total_duration"] / data["duration_count"] if data["duration_count"] > 0 else 0
                
                channel_performance.append({
                    "channel": channel,
                    "response_count": data["responses"],
                    "completion_rate": round(completion_rate, 1),
                    "average_duration": round(avg_duration, 1),
                    "percentage_of_total": round((data["responses"] / len(responses)) * 100, 1) if responses else 0
                })
            
            # Sort by response count
            channel_performance.sort(key=lambda x: x["response_count"], reverse=True)
            
            return channel_performance
            
        except Exception as e:
            logger.error(f"Error getting channel performance: {e}")
            return []
    
    # Helper methods
    def _get_start_date(self, time_range: str) -> Optional[datetime]:
        """Get start date for time range filter"""
        if time_range == "1d":
            return datetime.utcnow() - timedelta(days=1)
        elif time_range == "7d":
            return datetime.utcnow() - timedelta(days=7)
        elif time_range == "30d":
            return datetime.utcnow() - timedelta(days=30)
        else:  # "all"
            return None
    
    def _classify_sentiment(self, score: float) -> str:
        """Classify sentiment score into positive/neutral/negative"""
        if score > 0.1:
            return "positive"
        elif score < -0.1:
            return "negative"
        else:
            return "neutral"
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text (simple implementation)"""
        if not text:
            return []
        
        # Simple keyword extraction - can be enhanced with NLP libraries
        common_words = {
            'في', 'من', 'إلى', 'على', 'هذا', 'هذه', 'التي', 'الذي', 'كان', 'كانت',
            'هو', 'هي', 'أن', 'إن', 'لا', 'نعم', 'قد', 'لقد', 'كل', 'بعض',
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of',
            'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has'
        }
        
        words = text.lower().split()
        keywords = [word.strip('.,!?;:"()[]{}') for word in words 
                   if len(word) > 2 and word not in common_words]
        
        # Return most frequent words (simple approach)
        from collections import Counter
        word_counts = Counter(keywords)
        return [word for word, count in word_counts.most_common(5)]
    
    def _format_time_ago(self, timestamp: datetime) -> str:
        """Format timestamp as 'time ago' string"""
        now = datetime.utcnow()
        diff = now - timestamp
        
        if diff.days > 0:
            return f"منذ {diff.days} يوم"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"منذ {hours} ساعة"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"منذ {minutes} دقيقة"
        else:
            return "منذ قليل"
    
    def _calculate_percentage_change(self, current: float, previous: float) -> float:
        """Calculate percentage change between current and previous values"""
        if previous == 0:
            return 0.0
        return round(((current - previous) / previous) * 100, 1)
    
    def _get_previous_period_responses(self, time_range: str) -> int:
        """Get response count for previous period (for comparison)"""
        # Simplified implementation - returns 0 for now
        # Could be enhanced to calculate actual previous period data
        return 0
    
    def _get_previous_period_csat(self, start_date: Optional[datetime]) -> float:
        """Get CSAT for previous period"""
        # Simplified implementation
        return 0.0
    
    def _get_previous_period_sentiment(self, start_date: Optional[datetime]) -> float:
        """Get sentiment for previous period"""
        # Simplified implementation
        return 0.0
    
    def _get_previous_period_completion(self, start_date: Optional[datetime]) -> float:
        """Get completion rate for previous period"""
        # Simplified implementation
        return 0.0
    
    def _get_fallback_metrics(self) -> Dict[str, Any]:
        """Return fallback metrics in case of error"""
        return {
            "csat": {"score": 0.0, "count": 0, "change_percentage": 0.0, "trend": "stable"},
            "responses": {"total": 0, "change_percentage": 0.0, "trend": "stable"},
            "sentiment": {
                "score": 0.0, "confidence": 0.0,
                "distribution": {"positive": 0, "neutral": 0, "negative": 0},
                "change_percentage": 0.0
            },
            "completion": {"rate": 0.0, "average_duration": 0.0, "change_percentage": 0.0},
            "channels": [],
            "last_updated": datetime.utcnow().isoformat(),
            "time_range": "7d"
        }