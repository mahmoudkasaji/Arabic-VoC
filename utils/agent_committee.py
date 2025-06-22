"""
Agent Committee System for Intelligent AI Model Routing
Uses LangGraph orchestration with specialized committee agents
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import asyncio

logger = logging.getLogger(__name__)

class TextAnalyzerAgent:
    """Specialized agent for analyzing Arabic text characteristics"""
    
    def __init__(self, api_manager):
        self.api_manager = api_manager
        self.name = "TextAnalyzer"
    
    async def analyze_text_characteristics(self, text: str) -> Dict[str, Any]:
        """Deep analysis of text characteristics for routing decisions"""
        
        # Arabic character analysis
        arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
        total_chars = len(text)
        arabic_ratio = arabic_chars / total_chars if total_chars > 0 else 0
        
        # Dialectal markers with regional specificity
        dialectal_patterns = {
            'levantine': ['شو', 'ايش', 'وين', 'كيف', 'ليش', 'هيك', 'هاي', 'شلون', 'مين'],
            'gulf': ['شلون', 'وش', 'ليش', 'شنو', 'متى', 'فين'],
            'egyptian': ['ايه', 'فين', 'ازاي', 'امتى', 'مين', 'ليه'],
            'maghrebi': ['أش', 'فين', 'كيفاش', 'واش', 'شنو']
        }
        
        dialect_scores = {}
        for region, markers in dialectal_patterns.items():
            score = sum(1 for marker in markers if marker in text)
            dialect_scores[region] = score
        
        primary_dialect = max(dialect_scores.items(), key=lambda x: x[1])[0] if any(dialect_scores.values()) else None
        total_dialectal = sum(dialect_scores.values())
        
        # Sentiment complexity indicators
        sentiment_markers = {
            'complex_emotions': ['متضارب', 'معقد', 'متناقض', 'مختلط'],
            'cultural_expressions': ['الحمد لله', 'إن شاء الله', 'ما شاء الله', 'بارك الله'],
            'business_terms': ['خدمة', 'جودة', 'تجربة', 'موظف', 'إدارة', 'شركة']
        }
        
        complexity_indicators = {}
        for category, markers in sentiment_markers.items():
            complexity_indicators[category] = sum(1 for marker in markers if marker in text)
        
        # Linguistic complexity
        sentences = [s.strip() for s in text.replace('!', '.').replace('?', '.').split('.') if s.strip()]
        word_count = len(text.split())
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
                'cultural_markers': complexity_indicators,
                'estimated_tokens': word_count * 1.3
            },
            'metadata': {
                'word_count': word_count,
                'sentence_count': len(sentences),
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'analyzer_confidence': 0.9
            }
        }

class ModelExpertAgent:
    """Agent that provides expertise on AI model capabilities"""
    
    def __init__(self, api_manager):
        self.api_manager = api_manager
        self.name = "ModelExpert"
        
        # Enhanced model profiles
        self.model_profiles = {
            'jais': {
                'arabic_native': True,
                'dialectal_strength': 10,
                'cultural_intelligence': 10,
                'speed': 7,
                'cost_efficiency': 10,
                'max_complexity': 7,
                'best_for': ['dialectal_arabic', 'cultural_context', 'regional_expressions'],
                'limitations': ['complex_reasoning', 'long_texts']
            },
            'anthropic': {
                'arabic_native': False,
                'dialectal_strength': 6,
                'cultural_intelligence': 9,
                'speed': 6,
                'cost_efficiency': 4,
                'max_complexity': 10,
                'best_for': ['complex_reasoning', 'nuanced_analysis', 'cultural_interpretation'],
                'limitations': ['dialectal_nuances', 'cost']
            },
            'openai': {
                'arabic_native': False,
                'dialectal_strength': 5,
                'cultural_intelligence': 7,
                'speed': 9,
                'cost_efficiency': 7,
                'max_complexity': 8,
                'best_for': ['structured_output', 'fast_analysis', 'general_sentiment'],
                'limitations': ['dialectal_understanding', 'cultural_depth']
            }
        }
    
    async def evaluate_models_for_task(self, text_analysis: Dict, task_context: Dict) -> Dict[str, Any]:
        """Evaluate which models are best suited for the given task"""
        
        available_services = self.api_manager.get_available_services()
        evaluations = {}
        
        for model, profile in self.model_profiles.items():
            if not available_services.get(f"{model}_working", False):
                continue
            
            score = 0
            reasoning = []
            
            # Dialectal content evaluation
            if text_analysis['dialectal_analysis']['has_dialectal_content']:
                dialectal_bonus = profile['dialectal_strength'] * 3
                score += dialectal_bonus
                reasoning.append(f"Dialectal content (+{dialectal_bonus} points)")
            
            # Cultural intelligence requirements
            cultural_markers = sum(text_analysis['complexity_analysis']['cultural_markers'].values())
            if cultural_markers > 0:
                cultural_bonus = profile['cultural_intelligence'] * 2
                score += cultural_bonus
                reasoning.append(f"Cultural markers (+{cultural_bonus} points)")
            
            # Complexity handling
            complexity_score = text_analysis['complexity_analysis']['sentence_complexity']
            if complexity_score <= profile['max_complexity']:
                complexity_bonus = 10
                score += complexity_bonus
                reasoning.append(f"Complexity match (+{complexity_bonus} points)")
            else:
                complexity_penalty = -5
                score += complexity_penalty
                reasoning.append(f"Complexity mismatch ({complexity_penalty} points)")
            
            # Speed requirements
            if task_context.get('priority') == 'fast':
                speed_bonus = profile['speed']
                score += speed_bonus
                reasoning.append(f"Speed priority (+{speed_bonus} points)")
            
            # Cost considerations
            if task_context.get('optimize_cost', False):
                cost_bonus = profile['cost_efficiency']
                score += cost_bonus
                reasoning.append(f"Cost optimization (+{cost_bonus} points)")
            
            # Base capability score
            base_score = 5
            score += base_score
            reasoning.append(f"Base capability (+{base_score} points)")
            
            evaluations[model] = {
                'score': score,
                'reasoning': reasoning,
                'profile': profile,
                'confidence': min(0.95, score / 50)  # Normalize confidence
            }
        
        return evaluations

class ContextAgent:
    """Agent that analyzes task context and business requirements"""
    
    def __init__(self):
        self.name = "ContextAnalyzer"
    
    async def analyze_task_context(self, task_type: str, business_context: Dict = None) -> Dict[str, Any]:
        """Analyze the broader context of the analysis task"""
        
        # Task priority mapping
        task_priorities = {
            'real_time_feedback': {'speed': 'high', 'accuracy': 'medium', 'cost': 'medium'},
            'executive_report': {'speed': 'low', 'accuracy': 'high', 'cost': 'low'},
            'customer_service': {'speed': 'high', 'accuracy': 'high', 'cost': 'medium'},
            'market_research': {'speed': 'low', 'accuracy': 'high', 'cost': 'low'},
            'social_monitoring': {'speed': 'high', 'accuracy': 'medium', 'cost': 'high'}
        }
        
        context = task_priorities.get(task_type, {'speed': 'medium', 'accuracy': 'medium', 'cost': 'medium'})
        
        # Business hour considerations
        current_hour = datetime.utcnow().hour
        is_business_hours = 8 <= current_hour <= 18
        
        # Volume considerations
        expected_volume = business_context.get('expected_volume', 'medium') if business_context else 'medium'
        
        return {
            'task_type': task_type,
            'priorities': context,
            'timing_context': {
                'is_business_hours': is_business_hours,
                'current_hour': current_hour,
                'urgency_multiplier': 1.5 if is_business_hours else 1.0
            },
            'volume_context': {
                'expected_volume': expected_volume,
                'cost_sensitivity': 'high' if expected_volume == 'high' else 'medium'
            },
            'business_constraints': business_context or {}
        }

class DeciderAgent:
    """Main orchestrator agent that makes final routing decisions"""
    
    def __init__(self, api_manager):
        self.api_manager = api_manager
        self.name = "DeciderAgent"
        self.text_analyzer = TextAnalyzerAgent(api_manager)
        self.model_expert = ModelExpertAgent(api_manager)
        self.context_agent = ContextAgent()
    
    async def make_routing_decision(self, 
                                  text: str, 
                                  task_type: str = "arabic_analysis",
                                  business_context: Dict = None) -> Dict[str, Any]:
        """Orchestrate committee analysis and make final routing decision"""
        
        logger.info(f"DeciderAgent starting committee analysis for task: {task_type}")
        
        # Step 1: Text Analysis
        text_analysis = await self.text_analyzer.analyze_text_characteristics(text)
        logger.info(f"TextAnalyzer completed analysis: dialectal={text_analysis['dialectal_analysis']['has_dialectal_content']}")
        
        # Step 2: Task Context Analysis  
        task_context = await self.context_agent.analyze_task_context(task_type, business_context)
        logger.info(f"ContextAnalyzer completed: priorities={task_context['priorities']}")
        
        # Step 3: Model Expert Evaluation
        model_evaluations = await self.model_expert.evaluate_models_for_task(text_analysis, task_context)
        logger.info(f"ModelExpert evaluated {len(model_evaluations)} models")
        
        # Step 4: Committee Decision
        if not model_evaluations:
            raise Exception("No available AI models for analysis")
        
        # Select best model based on committee recommendations
        best_model = max(model_evaluations.items(), key=lambda x: x[1]['score'])
        selected_model, evaluation = best_model
        
        # Prepare decision rationale
        decision_rationale = {
            'selected_model': selected_model,
            'confidence': evaluation['confidence'],
            'score': evaluation['score'],
            'reasoning': evaluation['reasoning'],
            'committee_analysis': {
                'text_characteristics': text_analysis,
                'task_context': task_context,
                'model_evaluations': {k: {'score': v['score'], 'confidence': v['confidence']} 
                                    for k, v in model_evaluations.items()}
            },
            'decision_metadata': {
                'decision_timestamp': datetime.utcnow().isoformat(),
                'decider_agent': self.name,
                'committee_members': [self.text_analyzer.name, self.model_expert.name, self.context_agent.name]
            }
        }
        
        logger.info(f"DeciderAgent selected {selected_model} with confidence {evaluation['confidence']:.2f}")
        
        return decision_rationale

class AgentCommitteeOrchestrator:
    """Main orchestrator for the agent committee system"""
    
    def __init__(self, api_manager):
        self.api_manager = api_manager
        self.decider_agent = DeciderAgent(api_manager)
        self.decision_history = []
    
    async def route_analysis_request(self, 
                                   text: str, 
                                   task_type: str = "arabic_analysis",
                                   business_context: Dict = None) -> Dict[str, Any]:
        """Main entry point for agent-based routing"""
        
        try:
            # Get routing decision from committee
            decision = await self.decider_agent.make_routing_decision(text, task_type, business_context)
            
            # Store decision for learning
            self.decision_history.append(decision)
            
            # Execute analysis with selected model
            selected_model = decision['selected_model']
            analysis_result = self.api_manager.analyze_arabic_text(text, selected_model, task_type)
            
            # Enhance result with committee decision context
            analysis_result.update({
                'committee_decision': {
                    'selected_by': 'agent_committee',
                    'model_selected': selected_model,
                    'decision_confidence': decision['confidence'],
                    'reasoning_summary': decision['reasoning'][:3],  # Top 3 reasons
                    'committee_members': decision['decision_metadata']['committee_members']
                }
            })
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Agent committee routing failed: {e}")
            # Fallback to simple routing
            fallback_model = self.api_manager.get_recommended_service(text, task_type)
            if fallback_model:
                result = self.api_manager.analyze_arabic_text(text, fallback_model, task_type)
                result['committee_decision'] = {
                    'selected_by': 'fallback_routing',
                    'model_selected': fallback_model,
                    'fallback_reason': str(e)
                }
                return result
            else:
                raise e
    
    def get_committee_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics of the committee system"""
        
        if not self.decision_history:
            return {'status': 'no_decisions_yet'}
        
        recent_decisions = self.decision_history[-100:]  # Last 100 decisions
        
        model_usage = {}
        avg_confidence = 0
        
        for decision in recent_decisions:
            model = decision['selected_model']
            model_usage[model] = model_usage.get(model, 0) + 1
            avg_confidence += decision['confidence']
        
        avg_confidence /= len(recent_decisions)
        
        return {
            'total_decisions': len(self.decision_history),
            'recent_decisions': len(recent_decisions),
            'model_distribution': model_usage,
            'average_confidence': avg_confidence,
            'committee_health': 'operational'
        }

# Global orchestrator instance
committee_orchestrator = None

def get_committee_orchestrator(api_manager):
    """Get or create the global committee orchestrator"""
    global committee_orchestrator
    if committee_orchestrator is None:
        committee_orchestrator = AgentCommitteeOrchestrator(api_manager)
    return committee_orchestrator