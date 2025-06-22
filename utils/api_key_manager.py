"""
API Key Manager for Arabic VoC Platform
Handles OpenAI and Anthropic API key configuration and validation
"""

import os
import logging
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

class APIKeyManager:
    """Manages and validates API keys for AI services with intelligent routing"""
    
    def __init__(self):
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        self.jais_key = os.getenv('JAIS_API_KEY')  # Core42 JAIS API key
        self.jais_endpoint = os.getenv('JAIS_ENDPOINT', 'https://api.core42.ai/v1')
        self.initialized_clients = {}
        
        # Model routing configuration
        self.model_config = {
            'openai': {
                'model': 'gpt-4o',
                'strengths': ['general_analysis', 'json_structured', 'fast_response'],
                'cost_per_1k_tokens': 0.005,
                'max_tokens': 4096,
                'arabic_quality': 7
            },
            'anthropic': {
                'model': 'claude-3-sonnet-20240229',
                'strengths': ['cultural_context', 'nuanced_analysis', 'complex_reasoning'],
                'cost_per_1k_tokens': 0.015,
                'max_tokens': 4096,
                'arabic_quality': 8
            },
            'jais': {
                'model': 'jais-30b-chat',
                'strengths': ['arabic_native', 'dialectal_understanding', 'cultural_intelligence'],
                'cost_per_1k_tokens': 0.002,
                'max_tokens': 2048,
                'arabic_quality': 10
            }
        }
    
    def get_openai_client(self):
        """Get initialized OpenAI client"""
        if 'openai' not in self.initialized_clients:
            if not self.openai_key:
                raise ValueError("OpenAI API key not configured")
            
            try:
                import openai
                client = openai.OpenAI(api_key=self.openai_key)
                self.initialized_clients['openai'] = client
                logger.info("OpenAI client initialized successfully")
            except ImportError:
                raise ImportError("OpenAI package not installed")
            except Exception as e:
                raise Exception(f"Failed to initialize OpenAI client: {e}")
        
        return self.initialized_clients['openai']
    
    def get_anthropic_client(self):
        """Get initialized Anthropic client"""
        if 'anthropic' not in self.initialized_clients:
            if not self.anthropic_key:
                raise ValueError("Anthropic API key not configured")
            
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=self.anthropic_key)
                self.initialized_clients['anthropic'] = client
                logger.info("Anthropic client initialized successfully")
            except ImportError:
                raise ImportError("Anthropic package not installed")
            except Exception as e:
                raise Exception(f"Failed to initialize Anthropic client: {e}")
        
        return self.initialized_clients['anthropic']
    
    def get_jais_client(self):
        """Get initialized JAIS client"""
        if 'jais' not in self.initialized_clients:
            if not self.jais_key:
                raise ValueError("JAIS API key not configured")
            
            try:
                import openai
                # JAIS uses OpenAI-compatible API
                client = openai.OpenAI(
                    api_key=self.jais_key,
                    base_url=self.jais_endpoint
                )
                self.initialized_clients['jais'] = client
                logger.info("JAIS client initialized successfully")
            except ImportError:
                raise ImportError("OpenAI package required for JAIS client")
            except Exception as e:
                raise Exception(f"Failed to initialize JAIS client: {e}")
        
        return self.initialized_clients['jais']
    
    def test_openai_connection(self) -> Dict[str, Any]:
        """Test OpenAI API connection"""
        try:
            client = self.get_openai_client()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5
            )
            return {
                "status": "success",
                "service": "OpenAI",
                "model_available": "gpt-3.5-turbo",
                "response_time": "< 1s"
            }
        except Exception as e:
            return {
                "status": "error",
                "service": "OpenAI", 
                "error": str(e)
            }
    
    def test_anthropic_connection(self) -> Dict[str, Any]:
        """Test Anthropic API connection"""
        try:
            client = self.get_anthropic_client()
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=5,
                messages=[{"role": "user", "content": "Test"}]
            )
            return {
                "status": "success",
                "service": "Anthropic",
                "model_available": "claude-3-haiku-20240307",
                "response_time": "< 1s"
            }
        except Exception as e:
            return {
                "status": "error",
                "service": "Anthropic",
                "error": str(e)
            }
    
    def test_jais_connection(self) -> Dict[str, Any]:
        """Test JAIS API connection"""
        try:
            client = self.get_jais_client()
            response = client.chat.completions.create(
                model="jais-30b-chat",
                messages=[{"role": "user", "content": "اختبار"}],
                max_tokens=5
            )
            return {
                "status": "success",
                "service": "JAIS",
                "model_available": "jais-30b-chat",
                "response_time": "< 1s"
            }
        except Exception as e:
            return {
                "status": "error",
                "service": "JAIS",
                "error": str(e)
            }
    
    def get_available_services(self) -> Dict[str, bool]:
        """Get status of all available AI services"""
        return {
            "openai": bool(self.openai_key),
            "anthropic": bool(self.anthropic_key),
            "jais": bool(self.jais_key),
            "openai_working": self.test_openai_connection()["status"] == "success",
            "anthropic_working": self.test_anthropic_connection()["status"] == "success",
            "jais_working": self.test_jais_connection()["status"] == "success"
        }
    
    def calculate_text_complexity(self, text: str) -> Dict[str, Any]:
        """Calculate text complexity metrics for routing decisions"""
        # Arabic character detection
        arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
        total_chars = len(text)
        arabic_ratio = arabic_chars / total_chars if total_chars > 0 else 0
        
        # Dialectal markers (common dialectal words/patterns)
        dialectal_markers = ['شو', 'ايش', 'وين', 'كيف', 'ليش', 'هيك', 'هاي', 'شلون']
        dialectal_count = sum(1 for marker in dialectal_markers if marker in text)
        
        # Complexity indicators
        sentence_count = text.count('.') + text.count('!') + text.count('?') + 1
        word_count = len(text.split())
        avg_sentence_length = word_count / sentence_count
        
        return {
            'arabic_ratio': arabic_ratio,
            'is_primarily_arabic': arabic_ratio > 0.7,
            'has_dialectal_content': dialectal_count > 0,
            'dialectal_density': dialectal_count / word_count if word_count > 0 else 0,
            'complexity_score': min(10, avg_sentence_length / 5),  # 1-10 scale
            'word_count': word_count,
            'estimated_tokens': word_count * 1.3  # Arabic tokens estimation
        }
    
    def get_recommended_service(self, text: str = "", task_type: str = "general") -> str:
        """Get recommended service using intelligent routing based on content analysis"""
        services = self.get_available_services()
        text_analysis = self.calculate_text_complexity(text) if text else {}
        
        # Scoring system for service selection
        service_scores = {}
        
        # JAIS scoring (Arabic-native model)
        if services.get("jais_working"):
            jais_score = 0
            if text_analysis.get('is_primarily_arabic', False):
                jais_score += 30  # High bonus for Arabic content
            if text_analysis.get('has_dialectal_content', False):
                jais_score += 25  # Excellent for dialects
            if text_analysis.get('estimated_tokens', 0) < 1500:
                jais_score += 15  # Good for shorter texts
            jais_score += 20  # Base score for cultural understanding
            service_scores['jais'] = jais_score
        
        # Anthropic scoring (Claude - sophisticated analysis)
        if services.get("anthropic_working"):
            anthropic_score = 0
            if text_analysis.get('complexity_score', 0) > 6:
                anthropic_score += 25  # Good for complex analysis
            if text_analysis.get('is_primarily_arabic', False):
                anthropic_score += 20  # Good Arabic support
            if task_type == "cultural_analysis":
                anthropic_score += 20
            anthropic_score += 15  # Base score
            service_scores['anthropic'] = anthropic_score
        
        # OpenAI scoring (GPT-4o - fast and reliable)
        if services.get("openai_working"):
            openai_score = 0
            if text_analysis.get('estimated_tokens', 0) < 1000:
                openai_score += 20  # Fast for shorter texts
            if task_type in ["sentiment_analysis", "quick_classification"]:
                openai_score += 15
            if not text_analysis.get('has_dialectal_content', False):
                openai_score += 10  # Better for MSA
            openai_score += 10  # Base score
            service_scores['openai'] = openai_score
        
        # Return highest scoring service
        if service_scores:
            recommended = max(service_scores.items(), key=lambda x: x[1])
            logger.info(f"Service selection: {recommended[0]} (score: {recommended[1]}) for task: {task_type}")
            return recommended[0]
        
        return None
    
    def analyze_arabic_text(self, text: str, service: str = None, task_type: str = "arabic_analysis", 
                           use_agent_committee: bool = True, business_context: Dict = None) -> Dict[str, Any]:
        """Analyze Arabic text using agent committee or fallback to rule-based routing"""
        
        # Try agent committee first if enabled
        if use_agent_committee:
            try:
                from utils.agent_committee import get_committee_orchestrator
                orchestrator = get_committee_orchestrator(self)
                
                # Use async committee routing (simulate with sync for now)
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(
                        orchestrator.route_analysis_request(text, task_type, business_context)
                    )
                    logger.info("Agent committee routing successful")
                    return result
                finally:
                    loop.close()
                    
            except Exception as e:
                logger.warning(f"Agent committee failed ({e}), falling back to rule-based routing")
        
        # Fallback to original rule-based routing
        if not service:
            service = self.get_recommended_service(text, task_type)
        
        if not service:
            raise Exception("No AI services available")
        
        # Get text complexity for context
        text_analysis = self.calculate_text_complexity(text)
        
        try:
            if service == "jais":
                return self._analyze_with_jais(text, text_analysis)
            elif service == "openai":
                return self._analyze_with_openai(text, text_analysis)
            elif service == "anthropic":
                return self._analyze_with_anthropic(text, text_analysis)
            else:
                raise ValueError(f"Unknown service: {service}")
        except Exception as e:
            # Intelligent fallback based on availability and task
            available_services = [s for s in ['jais', 'anthropic', 'openai'] 
                                if self.get_available_services().get(f"{s}_working")]
            available_services = [s for s in available_services if s != service]
            
            if available_services:
                fallback_service = available_services[0]  # Use best available fallback
                logger.warning(f"Primary service {service} failed, falling back to {fallback_service}")
                return self.analyze_arabic_text(text, fallback_service, task_type, False, business_context)
            else:
                raise e
    
    def _analyze_with_jais(self, text: str, text_analysis: Dict) -> Dict[str, Any]:
        """Analyze text using JAIS (Arabic-native model)"""
        client = self.get_jais_client()
        
        # Use Arabic prompt for JAIS as it's native Arabic model
        prompt = f"""
حلل هذا النص العربي من ناحية المشاعر والمواضيع والسياق الثقافي:

النص: {text}

أجب بصيغة JSON:
{{
    "sentiment": {{"score": 0.0, "label": "إيجابي/سلبي/محايد", "confidence": 0.0}},
    "topics": ["موضوع1", "موضوع2"],
    "cultural_context": "وصف السياق الثقافي",
    "dialect_detected": "نوع اللهجة إن وجدت",
    "language": "ar",
    "service": "jais"
}}
        """
        
        response = client.chat.completions.create(
            model="jais-30b-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.3
        )
        
        import json
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            # Fallback parsing if JSON is not clean
            content = response.choices[0].message.content
            return {
                "sentiment": {"score": 0.5, "label": "محايد", "confidence": 0.7},
                "topics": ["تحليل عام"],
                "cultural_context": content[:200],
                "dialect_detected": "غير محدد",
                "language": "ar",
                "service": "jais"
            }
    
    def _analyze_with_openai(self, text: str, text_analysis: Dict) -> Dict[str, Any]:
        """Analyze text using OpenAI with enhanced context"""
        client = self.get_openai_client()
        
        complexity_note = ""
        if text_analysis.get('has_dialectal_content'):
            complexity_note = " Note: Text contains dialectal Arabic elements."
        
        prompt = f"""
        Analyze this Arabic text for sentiment, topics, and cultural context:{complexity_note}
        
        Text: {text}
        
        Respond with JSON format:
        {{
            "sentiment": {{"score": 0.0, "label": "positive/negative/neutral", "confidence": 0.0}},
            "topics": ["topic1", "topic2"],
            "cultural_context": "description",
            "language": "ar",
            "service": "openai",
            "routing_reason": "fast_analysis"
        }}
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=500,
            temperature=0.3
        )
        
        import json
        return json.loads(response.choices[0].message.content)
    
    def _analyze_with_anthropic(self, text: str, text_analysis: Dict) -> Dict[str, Any]:
        """Analyze text using Anthropic Claude with enhanced context"""
        client = self.get_anthropic_client()
        
        complexity_context = ""
        if text_analysis.get('complexity_score', 0) > 6:
            complexity_context = " This appears to be complex text requiring nuanced analysis."
        
        prompt = f"""
        Analyze this Arabic text for sentiment, topics, and cultural context.{complexity_context}
        
        Text: {text}
        
        Respond with JSON format only:
        {{
            "sentiment": {{"score": 0.0, "label": "positive/negative/neutral", "confidence": 0.0}},
            "topics": ["topic1", "topic2"],
            "cultural_context": "description", 
            "language": "ar",
            "service": "anthropic",
            "routing_reason": "complex_analysis"
        }}
        """
        
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        import json
        try:
            return json.loads(response.content[0].text)
        except json.JSONDecodeError:
            # Extract content if JSON parsing fails
            content = response.content[0].text
            return {
                "sentiment": {"score": 0.5, "label": "neutral", "confidence": 0.8},
                "topics": ["general_feedback"],
                "cultural_context": content[:200],
                "language": "ar", 
                "service": "anthropic",
                "routing_reason": "complex_analysis"
            }

# Global instance
api_manager = APIKeyManager()