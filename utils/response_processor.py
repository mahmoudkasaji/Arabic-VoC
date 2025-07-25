"""
Survey Response Processor
Handles real-time analytics calculation on survey submission
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from utils.simple_arabic_analyzer import SimpleArabicAnalyzer
from models.survey_flask import ResponseFlask, QuestionResponseFlask, QuestionFlask

logger = logging.getLogger(__name__)


class SurveyResponseProcessor:
    """Processes survey responses and calculates analytics in real-time"""
    
    def __init__(self):
        self.analyzer = SimpleArabicAnalyzer()
    
    def process_response_submission(self, response: ResponseFlask, questions_data: list) -> Dict[str, Any]:
        """
        Process a survey response submission and calculate analytics
        
        Args:
            response: ResponseFlask instance
            questions_data: List of question/answer pairs
            
        Returns:
            Dict with processing results and analytics
        """
        try:
            processing_results = {
                "response_id": response.id,
                "analytics_calculated": False,
                "sentiment_analysis": None,
                "keywords_extracted": [],
                "satisfaction_score": None,
                "channel_attribution": None,
                "processing_time": 0,
                "errors": []
            }
            
            start_time = datetime.utcnow()
            
            # 1. Extract channel attribution
            channel_info = self._extract_channel_attribution(response)
            processing_results["channel_attribution"] = channel_info
            
            # 2. Process text responses for sentiment and keywords
            text_analytics = self._process_text_responses(questions_data)
            processing_results["sentiment_analysis"] = text_analytics["sentiment"]
            processing_results["keywords_extracted"] = text_analytics["keywords"]
            
            # 3. Calculate satisfaction score from ratings
            satisfaction_score = self._calculate_satisfaction_score(questions_data)
            processing_results["satisfaction_score"] = satisfaction_score
            
            # 4. Update response record with analytics
            self._update_response_analytics(response, processing_results)
            
            # 5. Update survey aggregations
            self._update_survey_metrics(response.survey_id)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            processing_results["processing_time"] = processing_time
            processing_results["analytics_calculated"] = True
            
            logger.info(f"Response {response.id} processed successfully in {processing_time:.2f}s")
            
            return processing_results
            
        except Exception as e:
            logger.error(f"Error processing response {response.id}: {e}")
            processing_results["errors"].append(str(e))
            return processing_results
    
    def _extract_channel_attribution(self, response: ResponseFlask) -> Dict[str, str]:
        """Extract channel attribution from response metadata"""
        try:
            channel_info = {
                "primary_channel": "web",  # Default
                "device_type": response.device_type or "unknown",
                "user_agent": response.user_agent or "",
                "source": "direct"
            }
            
            # Determine channel from user agent or other metadata
            if response.user_agent:
                user_agent = response.user_agent.lower()
                if "mobile" in user_agent or "android" in user_agent or "iphone" in user_agent:
                    channel_info["primary_channel"] = "mobile"
                elif "whatsapp" in user_agent:
                    channel_info["primary_channel"] = "whatsapp"
                elif "telegram" in user_agent:
                    channel_info["primary_channel"] = "telegram"
                else:
                    channel_info["primary_channel"] = "web"
            
            # Check for email campaign attribution
            # This could be enhanced with UTM parameters or referrer data
            
            return channel_info
            
        except Exception as e:
            logger.warning(f"Error extracting channel attribution: {e}")
            return {"primary_channel": "unknown", "device_type": "unknown", "source": "unknown"}
    
    def _process_text_responses(self, questions_data: list) -> Dict[str, Any]:
        """Process text responses for sentiment analysis and keyword extraction"""
        try:
            text_analytics = {
                "sentiment": {"average_score": 0.0, "confidence": 0.0, "classification": "neutral"},
                "keywords": []
            }
            
            text_responses = []
            sentiment_scores = []
            confidence_scores = []
            all_keywords = []
            
            # Extract text responses
            for question_data in questions_data:
                answer = question_data.get("answer", "")
                question_type = question_data.get("type", "")
                
                if question_type in ["text", "textarea"] and answer and isinstance(answer, str):
                    text_responses.append(answer)
            
            # Analyze each text response
            for text in text_responses:
                if len(text.strip()) > 3:  # Only analyze meaningful text
                    try:
                        analysis = self.analyzer.analyze_text(text)
                        
                        if analysis and analysis.get("sentiment_score") is not None:
                            sentiment_scores.append(analysis["sentiment_score"])
                            confidence_scores.append(analysis.get("confidence", 0.0))
                            
                            # Extract keywords
                            keywords = analysis.get("topics", [])
                            if keywords:
                                all_keywords.extend(keywords)
                        
                    except Exception as e:
                        logger.warning(f"Text analysis failed for response: {e}")
            
            # Calculate averages
            if sentiment_scores:
                avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
                avg_confidence = sum(confidence_scores) / len(confidence_scores)
                
                # Classify sentiment
                if avg_sentiment > 0.1:
                    classification = "positive"
                elif avg_sentiment < -0.1:
                    classification = "negative"
                else:
                    classification = "neutral"
                
                text_analytics["sentiment"] = {
                    "average_score": round(avg_sentiment, 3),
                    "confidence": round(avg_confidence, 3),
                    "classification": classification
                }
            
            # Extract most common keywords
            if all_keywords:
                from collections import Counter
                keyword_counts = Counter(all_keywords)
                text_analytics["keywords"] = [
                    {"keyword": word, "frequency": count}
                    for word, count in keyword_counts.most_common(5)
                ]
            
            return text_analytics
            
        except Exception as e:
            logger.error(f"Error processing text responses: {e}")
            return {
                "sentiment": {"average_score": 0.0, "confidence": 0.0, "classification": "neutral"},
                "keywords": []
            }
    
    def _calculate_satisfaction_score(self, questions_data: list) -> Optional[float]:
        """Calculate satisfaction score from rating questions"""
        try:
            ratings = []
            
            for question_data in questions_data:
                question_type = question_data.get("type", "")
                answer = question_data.get("answer")
                
                if question_type in ["rating", "nps"] and answer is not None:
                    try:
                        rating_value = float(answer)
                        
                        # Normalize to 0-1 scale based on question type
                        if question_type == "rating":
                            # Assuming 5-point rating scale
                            normalized_rating = rating_value / 5.0
                        elif question_type == "nps":
                            # NPS scale is 0-10
                            normalized_rating = rating_value / 10.0
                        else:
                            normalized_rating = rating_value
                        
                        ratings.append(normalized_rating)
                        
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid rating value: {answer}")
            
            if ratings:
                return round(sum(ratings) / len(ratings), 3)
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating satisfaction score: {e}")
            return None
    
    def _update_response_analytics(self, response: ResponseFlask, results: Dict[str, Any]) -> None:
        """Update response record with calculated analytics"""
        try:
            # Update sentiment fields
            sentiment_data = results.get("sentiment_analysis", {})
            if sentiment_data and sentiment_data.get("sentiment"):
                response.sentiment_score = sentiment_data["sentiment"]["average_score"]
                response.confidence_score = sentiment_data["sentiment"]["confidence"]
            
            # Update keywords
            keywords = results.get("keywords_extracted", [])
            if keywords:
                keywords_json = json.dumps(keywords, ensure_ascii=False)
                response.keywords = keywords_json
            
            # Update channel attribution
            channel_info = results.get("channel_attribution", {})
            if channel_info.get("primary_channel"):
                # Store channel info in device_type field for now
                response.device_type = channel_info["primary_channel"]
            
            logger.debug(f"Response analytics updated for response {response.id}")
            
        except Exception as e:
            logger.error(f"Error updating response analytics: {e}")
    
    def _update_survey_metrics(self, survey_id: int) -> None:
        """Update survey-level aggregated metrics"""
        try:
            from app import db
            from models.survey_flask import SurveyFlask
            from sqlalchemy import func
            
            # Get survey
            survey = db.session.query(SurveyFlask).get(survey_id)
            if not survey:
                return
            
            # Calculate aggregated metrics
            responses = db.session.query(ResponseFlask).filter_by(survey_id=survey_id).all()
            
            if responses:
                # Update response count
                survey.response_count = len(responses)
                
                # Calculate completion rate
                completed_responses = [r for r in responses if r.is_complete]
                if responses:
                    survey.completion_rate = len(completed_responses) / len(responses)
                
                # Calculate average duration
                durations = [r.duration_minutes for r in completed_responses if r.duration_minutes]
                if durations:
                    survey.average_duration = sum(durations) / len(durations)
                
                # Calculate average satisfaction (would need additional field)
                # This could be added to the SurveyFlask model
                
                db.session.commit()
                logger.debug(f"Survey metrics updated for survey {survey_id}")
            
        except Exception as e:
            logger.error(f"Error updating survey metrics: {e}")
            db.session.rollback()
    
    def calculate_nps_score(self, ratings: list) -> Dict[str, Any]:
        """Calculate Net Promoter Score from rating responses"""
        try:
            if not ratings:
                return {"nps": 0, "promoters": 0, "passives": 0, "detractors": 0}
            
            promoters = len([r for r in ratings if r >= 9])
            passives = len([r for r in ratings if 7 <= r <= 8])
            detractors = len([r for r in ratings if r <= 6])
            
            total = len(ratings)
            nps = ((promoters - detractors) / total) * 100 if total > 0 else 0
            
            return {
                "nps": round(nps, 1),
                "promoters": promoters,
                "passives": passives,
                "detractors": detractors,
                "total_responses": total
            }
            
        except Exception as e:
            logger.error(f"Error calculating NPS: {e}")
            return {"nps": 0, "promoters": 0, "passives": 0, "detractors": 0}