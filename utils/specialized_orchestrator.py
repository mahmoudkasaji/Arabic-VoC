"""
Specialized Agent Orchestrator for Arabic VoC Analysis
Coordinates sentiment, topic, and recommendation agents with clean separation of concerns
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from .specialized_agents import SentimentAnalysisAgent, TopicalAnalysisAgent, RecommendationAgent

logger = logging.getLogger(__name__)

class SpecializedAnalysisOrchestrator:
    """Orchestrates specialized agents for comprehensive Arabic text analysis"""
    
    def __init__(self, api_manager):
        self.api_manager = api_manager
        
        # Initialize specialized agents
        self.sentiment_agent = SentimentAnalysisAgent(api_manager)
        self.topic_agent = TopicalAnalysisAgent(api_manager)
        self.recommendation_agent = RecommendationAgent(api_manager)
        
        # Analysis history for performance tracking
        self.analysis_history = []
    
    async def analyze_text_comprehensive(self, 
                                       text: str, 
                                       task_type: str = "arabic_analysis",
                                       business_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Comprehensive analysis using specialized agents
        
        Flow:
        1. Text Characteristics Analysis
        2. Sentiment Analysis (SentimentAnalysisAgent)
        3. Topic Analysis (TopicalAnalysisAgent) 
        4. Recommendation Generation (RecommendationAgent)
        5. Result Integration
        """
        
        start_time = datetime.utcnow()
        analysis_id = f"analysis_{int(start_time.timestamp())}"
        
        logger.info(f"Starting comprehensive analysis {analysis_id} for task: {task_type}")
        
        try:
            # Step 1: Analyze text characteristics (shared across agents)
            text_characteristics = await self._analyze_text_characteristics(text)
            logger.info(f"Text characteristics analyzed: {text_characteristics.get('word_count')} words, dialectal: {text_characteristics.get('dialectal_analysis', {}).get('has_dialectal_content', False)}")
            
            # Step 2: Sentiment Analysis
            sentiment_analysis = await self.sentiment_agent.analyze_sentiment(text, text_characteristics)
            logger.info(f"Sentiment analysis completed: {sentiment_analysis.get('sentiment', {}).get('label')} (confidence: {sentiment_analysis.get('sentiment', {}).get('confidence', 0):.2f})")
            
            # Step 3: Topic Analysis (with sentiment context)
            topic_analysis = await self.topic_agent.analyze_topics(text, text_characteristics, sentiment_analysis)
            logger.info(f"Topic analysis completed: {len(topic_analysis.get('primary_topics', []))} topics identified")
            
            # Step 4: Recommendation Generation (with full context)
            recommendations = await self.recommendation_agent.generate_recommendations(
                text, sentiment_analysis, topic_analysis, text_characteristics
            )
            logger.info(f"Recommendations generated: {len(recommendations.get('immediate_actions', []))} immediate actions")
            
            # Step 5: Integrate results
            integrated_result = self._integrate_analysis_results(
                text, text_characteristics, sentiment_analysis, topic_analysis, 
                recommendations, analysis_id, start_time
            )
            
            # Track performance
            self._track_analysis_performance(integrated_result, start_time)
            
            return integrated_result
            
        except Exception as e:
            logger.error(f"Comprehensive analysis failed for {analysis_id}: {e}")
            return await self._fallback_analysis(text, analysis_id, start_time)
    
    async def _analyze_text_characteristics(self, text: str) -> Dict[str, Any]:
        """Analyze text characteristics shared across all agents"""
        
        # Arabic character analysis
        arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
        total_chars = len(text)
        arabic_ratio = arabic_chars / total_chars if total_chars > 0 else 0
        
        # Dialectal analysis
        dialectal_patterns = {
            'levantine': ['شو', 'ايش', 'وين', 'كيف', 'ليش', 'هيك', 'شلون'],
            'gulf': ['شلون', 'وش', 'ليش', 'شنو', 'وين'],
            'egyptian': ['ايه', 'فين', 'ازاي', 'امتى', 'ليه'],
            'maghrebi': ['أش', 'فين', 'كيفاش', 'واش']
        }
        
        dialect_scores = {}
        for region, markers in dialectal_patterns.items():
            score = sum(1 for marker in markers if marker in text)
            dialect_scores[region] = score
        
        primary_dialect = max(dialect_scores.items(), key=lambda x: x[1])[0] if any(dialect_scores.values()) else None
        total_dialectal = sum(dialect_scores.values())
        
        # Linguistic complexity
        sentences = [s.strip() for s in text.replace('!', '.').replace('?', '.').split('.') if s.strip()]
        words = text.split()
        word_count = len(words)
        avg_sentence_length = word_count / len(sentences) if sentences else 0
        
        return {
            'arabic_ratio': arabic_ratio,
            'is_primarily_arabic': arabic_ratio > 0.7,
            'dialectal_analysis': {
                'has_dialectal_content': total_dialectal > 0,
                'primary_dialect': primary_dialect,
                'dialect_density': total_dialectal / word_count if word_count > 0 else 0,
                'regional_scores': dialect_scores
            },
            'complexity_analysis': {
                'sentence_complexity': min(10, avg_sentence_length / 5),
                'estimated_tokens': word_count * 1.3,
                'avg_sentence_length': avg_sentence_length
            },
            'metadata': {
                'word_count': word_count,
                'sentence_count': len(sentences),
                'character_count': total_chars,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
        }
    
    def _integrate_analysis_results(self, 
                                  text: str,
                                  text_characteristics: Dict,
                                  sentiment_analysis: Dict,
                                  topic_analysis: Dict,
                                  recommendations: Dict,
                                  analysis_id: str,
                                  start_time: datetime) -> Dict[str, Any]:
        """Integrate results from all specialized agents"""
        
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        # Determine overall analysis confidence
        sentiment_confidence = sentiment_analysis.get('sentiment', {}).get('confidence', 0)
        topic_confidence = 0.8  # Topic analysis doesn't always return confidence
        recommendation_confidence = recommendations.get('recommendation_confidence', 0)
        overall_confidence = (sentiment_confidence + topic_confidence + recommendation_confidence) / 3
        
        # Extract key services used
        services_used = {
            'sentiment': sentiment_analysis.get('service', 'unknown'),
            'topics': topic_analysis.get('service', 'unknown'),
            'recommendations': recommendations.get('service', 'unknown')
        }
        
        # Create integrated response
        integrated_result = {
            # Core analysis results
            'sentiment': sentiment_analysis.get('sentiment', {}),
            'emotional_dimensions': sentiment_analysis.get('emotional_dimensions', {}),
            'cultural_sentiment': sentiment_analysis.get('cultural_sentiment', {}),
            'topics': topic_analysis.get('primary_topics', []),
            'business_categories': topic_analysis.get('business_categories', {}),
            'topic_sentiment_mapping': topic_analysis.get('topic_sentiment_mapping', {}),
            'action_items': recommendations.get('immediate_actions', []),
            'strategic_recommendations': recommendations.get('strategic_recommendations', []),
            'follow_up_actions': recommendations.get('follow_up_actions', []),
            
            # Enhanced metadata
            'analysis_metadata': {
                'analysis_id': analysis_id,
                'processing_time_seconds': processing_time,
                'overall_confidence': overall_confidence,
                'services_used': services_used,
                'text_characteristics': {
                    'word_count': text_characteristics.get('metadata', {}).get('word_count', 0),
                    'is_dialectal': text_characteristics.get('dialectal_analysis', {}).get('has_dialectal_content', False),
                    'primary_dialect': text_characteristics.get('dialectal_analysis', {}).get('primary_dialect'),
                    'complexity_score': text_characteristics.get('complexity_analysis', {}).get('sentence_complexity', 0)
                },
                'specialized_agents': [
                    self.sentiment_agent.name,
                    self.topic_agent.name,
                    self.recommendation_agent.name
                ]
            },
            
            # Business intelligence
            'business_intelligence': {
                'priority_level': recommendations.get('priority_level', 'medium'),
                'urgency_indicators': topic_analysis.get('urgency_indicators', []),
                'success_metrics': recommendations.get('success_metrics', []),
                'timeline': recommendations.get('timeline', {}),
                'cultural_considerations': recommendations.get('cultural_considerations', [])
            },
            
            # System metadata
            'language': 'ar',
            'service': 'specialized_agents',
            'routing_reason': 'comprehensive_specialized_analysis',
            'committee_decision': {
                'selected_by': 'specialized_orchestrator',
                'committee_members': [agent.name for agent in [self.sentiment_agent, self.topic_agent, self.recommendation_agent]],
                'decision_confidence': overall_confidence,
                'model_selected': 'multi_model_orchestration',
                'reasoning_summary': [
                    f"Sentiment analysis via {services_used['sentiment']}",
                    f"Topic analysis via {services_used['topics']}",
                    f"Recommendations via {services_used['recommendations']}"
                ]
            }
        }
        
        return integrated_result
    
    async def _fallback_analysis(self, text: str, analysis_id: str, start_time: datetime) -> Dict[str, Any]:
        """Fallback analysis when specialized agents fail"""
        
        logger.warning(f"Using fallback analysis for {analysis_id}")
        
        # Simple keyword-based analysis
        positive_words = ['ممتاز', 'جيد', 'رائع', 'شكراً', 'راضي']
        negative_words = ['سيء', 'مشكلة', 'خطأ', 'محبط', 'غير راضي']
        
        positive_score = sum(1 for word in positive_words if word in text)
        negative_score = sum(1 for word in negative_words if word in text)
        
        if positive_score > negative_score:
            sentiment_label = "positive"
            sentiment_score = 0.6
        elif negative_score > positive_score:
            sentiment_label = "negative"
            sentiment_score = -0.6
        else:
            sentiment_label = "neutral"
            sentiment_score = 0.0
        
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        return {
            'sentiment': {
                'score': sentiment_score,
                'label': sentiment_label,
                'confidence': 0.5,
                'intensity': 'moderate'
            },
            'topics': ['general_feedback'],
            'action_items': ['مراجعة التغذية الراجعة مع الفريق'],
            'language': 'ar',
            'service': 'fallback',
            'routing_reason': 'agent_failure_fallback',
            'analysis_metadata': {
                'analysis_id': analysis_id,
                'processing_time_seconds': processing_time,
                'overall_confidence': 0.5,
                'services_used': {'sentiment': 'fallback', 'topics': 'fallback', 'recommendations': 'fallback'},
                'specialized_agents': ['fallback_analyzer']
            },
            'committee_decision': {
                'selected_by': 'fallback_system',
                'committee_members': ['fallback_analyzer'],
                'decision_confidence': 0.5,
                'model_selected': 'keyword_based',
                'reasoning_summary': ['Agent system failure', 'Keyword-based fallback analysis']
            }
        }
    
    def _track_analysis_performance(self, result: Dict, start_time: datetime):
        """Track analysis performance for optimization"""
        
        performance_data = {
            'timestamp': start_time.isoformat(),
            'processing_time': result.get('analysis_metadata', {}).get('processing_time_seconds', 0),
            'confidence': result.get('analysis_metadata', {}).get('overall_confidence', 0),
            'services_used': result.get('analysis_metadata', {}).get('services_used', {}),
            'word_count': result.get('analysis_metadata', {}).get('text_characteristics', {}).get('word_count', 0),
            'is_dialectal': result.get('analysis_metadata', {}).get('text_characteristics', {}).get('is_dialectal', False)
        }
        
        self.analysis_history.append(performance_data)
        
        # Keep only last 100 analyses for memory management
        if len(self.analysis_history) > 100:
            self.analysis_history = self.analysis_history[-100:]
        
        # Log performance summary
        avg_time = sum(p['processing_time'] for p in self.analysis_history[-10:]) / min(10, len(self.analysis_history))
        avg_confidence = sum(p['confidence'] for p in self.analysis_history[-10:]) / min(10, len(self.analysis_history))
        
        logger.info(f"Performance tracking - Avg time: {avg_time:.2f}s, Avg confidence: {avg_confidence:.2f}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the specialized agent system"""
        
        if not self.analysis_history:
            return {'status': 'no_data', 'message': 'No analysis history available'}
        
        recent_analyses = self.analysis_history[-50:]  # Last 50 analyses
        
        return {
            'total_analyses': len(self.analysis_history),
            'recent_performance': {
                'avg_processing_time': sum(a['processing_time'] for a in recent_analyses) / len(recent_analyses),
                'avg_confidence': sum(a['confidence'] for a in recent_analyses) / len(recent_analyses),
                'dialectal_text_percentage': sum(1 for a in recent_analyses if a['is_dialectal']) / len(recent_analyses) * 100
            },
            'service_usage': {
                'sentiment_services': [a['services_used'].get('sentiment') for a in recent_analyses],
                'topic_services': [a['services_used'].get('topics') for a in recent_analyses],
                'recommendation_services': [a['services_used'].get('recommendations') for a in recent_analyses]
            },
            'timestamp': datetime.utcnow().isoformat()
        }


# Global orchestrator instance
_specialized_orchestrator = None

def get_specialized_orchestrator(api_manager):
    """Get the global specialized orchestrator instance"""
    global _specialized_orchestrator
    if _specialized_orchestrator is None:
        _specialized_orchestrator = SpecializedAnalysisOrchestrator(api_manager)
    return _specialized_orchestrator