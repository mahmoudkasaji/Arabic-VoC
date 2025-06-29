"""
Enhanced Committee Orchestration for Arabic VoC Analysis
Implements consensus mechanisms and self-consistency checking with multiple strategy validation
"""

import logging
import asyncio
import time
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from statistics import median, mode

from .specialized_agents import SentimentAnalysisAgent, TopicalAnalysisAgent, RecommendationAgent, PromptStrategy

logger = logging.getLogger(__name__)

class VoCAnalysisCommittee:
    """Enhanced committee orchestration with consensus mechanisms and self-consistency checking"""
    
    def __init__(self, api_manager):
        self.api_manager = api_manager
        
        # Initialize specialized agents
        self.agents = {
            "sentiment": SentimentAnalysisAgent(api_manager),
            "topical": TopicalAnalysisAgent(api_manager),
            "recommendation": RecommendationAgent(api_manager)
        }
        
        # Consensus configuration
        self.consensus_threshold = 0.7
        self.outlier_threshold = 0.3  # For outlier detection in score averaging
        
        # Performance tracking
        self.analysis_history = []
        self.processing_times = []
    
    async def analyze_with_consensus(self, text: str, context: Dict = None) -> Dict[str, Any]:
        """Run comprehensive analysis with self-consistency checking and consensus mechanisms"""
        
        start_time = time.time()
        analysis_id = f"consensus_{int(start_time)}"
        
        if context is None:
            context = {}
        
        logger.info(f"Starting consensus analysis {analysis_id}")
        
        try:
            # Step 1: Multi-strategy sentiment analysis for consensus
            sentiment_consensus = await self._run_sentiment_consensus(text, context)
            
            # Step 2: Enhanced topical analysis with uncertainty quantification
            topics_analysis = await self.agents["topical"].analyze_with_uncertainty(text, {
                'text_characteristics': context.get('text_characteristics', {}),
                'sentiment_context': sentiment_consensus
            })
            
            # Step 3: Generate recommendations based on consensus results
            combined_analysis = {
                "sentiment": sentiment_consensus,
                "topics": topics_analysis,
                "consensus_confidence": sentiment_consensus.get("consensus_confidence", 0.0)
            }
            
            recommendations = await self.agents["recommendation"].generate_recommendations(
                text, combined_analysis, context
            )
            
            # Step 4: Calculate final processing metrics
            processing_time = time.time() - start_time
            self.processing_times.append(processing_time)
            
            # Step 5: Compile comprehensive results
            final_result = {
                "analysis_id": analysis_id,
                "text": text,
                "sentiment": sentiment_consensus,
                "topics": topics_analysis,
                "recommendations": recommendations,
                "metadata": {
                    "analysis_strategies_used": ["direct", "chain_of_thought", "few_shot"],
                    "consensus_score": sentiment_consensus.get("consensus_confidence", 0.0),
                    "validation_agreement": topics_analysis.get("validation_agreement", 0.0),
                    "processing_time": processing_time,
                    "uncertainty_levels": {
                        "sentiment": sentiment_consensus.get("uncertainty_score", 0.0),
                        "topics": self._calculate_topic_uncertainty(topics_analysis)
                    },
                    "enhanced_features": {
                        "consensus_mechanism": True,
                        "uncertainty_quantification": True,
                        "multi_strategy_validation": True,
                        "hierarchical_topics": True,
                        "emerging_trend_detection": True
                    }
                }
            }
            
            # Store in analysis history
            self.analysis_history.append({
                "timestamp": datetime.utcnow(),
                "analysis_id": analysis_id,
                "processing_time": processing_time,
                "consensus_score": sentiment_consensus.get("consensus_confidence", 0.0),
                "validation_agreement": topics_analysis.get("validation_agreement", 0.0)
            })
            
            logger.info(f"Consensus analysis {analysis_id} completed in {processing_time:.2f}s")
            return final_result
            
        except Exception as e:
            logger.error(f"Consensus analysis failed: {e}")
            # Fallback to single-strategy analysis
            return await self._fallback_analysis(text, context, analysis_id)
    
    async def _run_sentiment_consensus(self, text: str, context: Dict) -> Dict[str, Any]:
        """Run sentiment analysis with multiple strategies and calculate consensus"""
        
        strategies = [PromptStrategy.DIRECT, PromptStrategy.CHAIN_OF_THOUGHT, PromptStrategy.FEW_SHOT]
        sentiment_results = []
        
        # Execute sentiment analysis with different strategies
        for strategy in strategies:
            try:
                # Set strategy for this iteration
                original_strategy = getattr(self.agents["sentiment"], 'current_strategy', PromptStrategy.DIRECT)
                
                # Perform analysis with specific strategy
                result = await self.agents["sentiment"].analyze_with_strategy(text, strategy, context)
                sentiment_results.append({
                    "strategy": strategy.value,
                    "result": result
                })
                
                # Restore original strategy
                setattr(self.agents["sentiment"], 'current_strategy', original_strategy)
                
            except Exception as e:
                logger.warning(f"Strategy {strategy.value} failed: {e}")
                continue
        
        if not sentiment_results:
            # If all strategies failed, use fallback
            fallback_result = await self.agents["sentiment"].analyze_sentiment(text, {}, context)
            return {
                "score": fallback_result.get("sentiment_score", 0.0),
                "label": fallback_result.get("sentiment_label", "neutral"),
                "confidence": 0.3,  # Low confidence for fallback
                "consensus_confidence": 0.3,
                "reasoning": "Fallback analysis due to strategy failures",
                "strategies_used": ["fallback"]
            }
        
        # Calculate consensus from multiple results
        return self._calculate_sentiment_consensus(sentiment_results)
    
    def _calculate_sentiment_consensus(self, results: List[Dict]) -> Dict[str, Any]:
        """Synthesize multiple sentiment results into consensus with outlier detection"""
        
        if not results:
            return {"error": "No results to synthesize"}
        
        # Extract scores and labels
        scores = []
        labels = []
        confidences = []
        reasoning_parts = []
        
        for result_data in results:
            result = result_data["result"]
            if "sentiment_score" in result:
                scores.append(result["sentiment_score"])
                labels.append(result.get("sentiment_label", "neutral"))
                confidences.append(result.get("confidence_score", 0.5))
                reasoning_parts.append(result.get("reasoning", ""))
        
        if not scores:
            return {"error": "No valid sentiment scores found"}
        
        # Majority vote for label with confidence weighting
        label_weights = {}
        for i, label in enumerate(labels):
            weight = confidences[i] if i < len(confidences) else 0.5
            label_weights[label] = label_weights.get(label, 0) + weight
        
        consensus_label = max(label_weights.keys(), key=lambda k: label_weights[k])
        
        # Robust score averaging with outlier detection
        consensus_score = self._calculate_robust_average(scores)
        
        # Calculate consensus confidence based on agreement
        consensus_confidence = self._calculate_consensus_confidence(results)
        
        # Calculate uncertainty score
        uncertainty_score = self._calculate_uncertainty_score(scores, labels)
        
        # Synthesize reasoning
        combined_reasoning = self._synthesize_reasoning(reasoning_parts, consensus_label, consensus_score)
        
        return {
            "score": consensus_score,
            "label": consensus_label,
            "confidence": consensus_confidence,
            "consensus_confidence": consensus_confidence,
            "uncertainty_score": uncertainty_score,
            "reasoning": combined_reasoning,
            "strategies_used": [r["strategy"] for r in results],
            "individual_scores": scores,
            "score_variance": self._calculate_variance(scores),
            "label_agreement": sum(1 for l in labels if l == consensus_label) / len(labels)
        }
    
    def _calculate_robust_average(self, scores: List[float]) -> float:
        """Calculate average with outlier removal for more robust consensus"""
        
        if len(scores) <= 2:
            return sum(scores) / len(scores)
        
        # Use median for outlier detection
        median_score = median(scores)
        
        # Remove outliers (scores that deviate too much from median)
        filtered_scores = []
        for score in scores:
            if abs(score - median_score) <= self.outlier_threshold:
                filtered_scores.append(score)
        
        # If too many outliers, use all scores
        if len(filtered_scores) < len(scores) * 0.5:
            filtered_scores = scores
        
        return sum(filtered_scores) / len(filtered_scores)
    
    def _calculate_consensus_confidence(self, results: List[Dict]) -> float:
        """Calculate confidence based on agreement between different strategies"""
        
        if len(results) < 2:
            return 0.5  # Medium confidence for single result
        
        scores = [r["result"].get("sentiment_score", 0) for r in results]
        labels = [r["result"].get("sentiment_label", "neutral") for r in results]
        
        # Score agreement (lower variance = higher confidence)
        score_variance = self._calculate_variance(scores)
        score_confidence = max(0.0, 1.0 - (score_variance * 2))  # Scale variance to confidence
        
        # Label agreement
        most_common_label = mode(labels) if len(set(labels)) < len(labels) else labels[0]
        label_agreement = sum(1 for l in labels if l == most_common_label) / len(labels)
        
        # Combined confidence
        consensus_confidence = (score_confidence * 0.6 + label_agreement * 0.4)
        
        return min(1.0, max(0.0, consensus_confidence))
    
    def _calculate_uncertainty_score(self, scores: List[float], labels: List[str]) -> float:
        """Calculate uncertainty score based on disagreement between methods"""
        
        # Score disagreement
        score_variance = self._calculate_variance(scores)
        
        # Label disagreement
        unique_labels = len(set(labels))
        label_disagreement = (unique_labels - 1) / max(1, len(labels) - 1) if len(labels) > 1 else 0
        
        # Combined uncertainty (higher variance and disagreement = higher uncertainty)
        uncertainty = (score_variance * 0.7 + label_disagreement * 0.3)
        
        return min(1.0, max(0.0, uncertainty))
    
    def _calculate_variance(self, scores: List[float]) -> float:
        """Calculate variance of scores"""
        if len(scores) <= 1:
            return 0.0
        
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        return variance
    
    def _synthesize_reasoning(self, reasoning_parts: List[str], consensus_label: str, consensus_score: float) -> str:
        """Synthesize reasoning from multiple analyses"""
        
        # Filter out empty reasoning
        valid_reasoning = [r for r in reasoning_parts if r and r.strip()]
        
        if not valid_reasoning:
            return f"Consensus analysis indicates {consensus_label} sentiment with score {consensus_score:.2f}"
        
        # Combine unique insights
        unique_insights = []
        for reasoning in valid_reasoning:
            # Extract key phrases (simplified approach)
            insights = [phrase.strip() for phrase in reasoning.split('.') if phrase.strip()]
            for insight in insights[:2]:  # Take first 2 insights from each
                if insight not in unique_insights and len(insight) > 10:
                    unique_insights.append(insight)
        
        # Construct synthesized reasoning
        if len(unique_insights) >= 2:
            synthesized = f"Multiple analysis strategies converge on {consensus_label} sentiment. {unique_insights[0]}. {unique_insights[1]}."
        elif len(unique_insights) == 1:
            synthesized = f"Consensus analysis indicates {consensus_label} sentiment. {unique_insights[0]}."
        else:
            synthesized = f"Consensus analysis indicates {consensus_label} sentiment with score {consensus_score:.2f}."
        
        return synthesized
    
    def _calculate_topic_uncertainty(self, topics_analysis: Dict) -> float:
        """Calculate topic uncertainty from uncertainty analysis"""
        
        uncertainty_analysis = topics_analysis.get("uncertainty_analysis", {})
        
        # Count topics by confidence level
        high_conf = len(uncertainty_analysis.get("high_confidence", []))
        medium_conf = len(uncertainty_analysis.get("medium_confidence", []))
        low_conf = len(uncertainty_analysis.get("low_confidence", []))
        
        total_topics = high_conf + medium_conf + low_conf
        
        if total_topics == 0:
            return 0.5  # Medium uncertainty when no topics detected
        
        # Calculate weighted uncertainty (low confidence topics increase uncertainty)
        uncertainty = (low_conf * 1.0 + medium_conf * 0.5 + high_conf * 0.0) / total_topics
        
        return min(1.0, max(0.0, uncertainty))
    
    async def _fallback_analysis(self, text: str, context: Dict, analysis_id: str) -> Dict[str, Any]:
        """Fallback analysis when consensus mechanism fails"""
        
        logger.warning(f"Using fallback analysis for {analysis_id}")
        
        try:
            # Simple single-strategy analysis
            sentiment_result = await self.agents["sentiment"].analyze_sentiment(text, {}, context)
            topics_result = await self.agents["topical"].analyze_topics(text, context.get('text_characteristics', {}), sentiment_result)
            recommendations_result = await self.agents["recommendation"].generate_recommendations(text, {
                "sentiment": sentiment_result,
                "topics": topics_result
            }, context)
            
            return {
                "analysis_id": analysis_id,
                "text": text,
                "sentiment": sentiment_result,
                "topics": topics_result,
                "recommendations": recommendations_result,
                "metadata": {
                    "analysis_mode": "fallback",
                    "consensus_score": 0.0,
                    "processing_time": 0.0,
                    "enhanced_features": {
                        "consensus_mechanism": False,
                        "uncertainty_quantification": False,
                        "multi_strategy_validation": False
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Fallback analysis also failed: {e}")
            return {
                "analysis_id": analysis_id,
                "error": "Analysis failed completely",
                "text": text,
                "metadata": {
                    "analysis_mode": "error",
                    "error_message": str(e)
                }
            }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get committee performance metrics"""
        
        if not self.analysis_history:
            return {"error": "No analysis history available"}
        
        recent_analyses = self.analysis_history[-10:]  # Last 10 analyses
        
        avg_processing_time = sum(a["processing_time"] for a in recent_analyses) / len(recent_analyses)
        avg_consensus_score = sum(a["consensus_score"] for a in recent_analyses) / len(recent_analyses)
        avg_validation_agreement = sum(a.get("validation_agreement", 0) for a in recent_analyses) / len(recent_analyses)
        
        return {
            "total_analyses": len(self.analysis_history),
            "recent_performance": {
                "average_processing_time": avg_processing_time,
                "average_consensus_score": avg_consensus_score,
                "average_validation_agreement": avg_validation_agreement
            },
            "consensus_threshold": self.consensus_threshold,
            "committee_agents": list(self.agents.keys()),
            "enhanced_features_active": True
        }


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