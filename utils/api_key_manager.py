"""
API Key Manager for Arabic VoC Platform
Handles OpenAI and Anthropic API key configuration and validation
"""

import os
import logging
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

class APIKeyManager:
    """Manages and validates API keys for AI services"""
    
    def __init__(self):
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        self.initialized_clients = {}
    
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
    
    def get_available_services(self) -> Dict[str, bool]:
        """Get status of all available AI services"""
        return {
            "openai": bool(self.openai_key),
            "anthropic": bool(self.anthropic_key),
            "openai_working": self.test_openai_connection()["status"] == "success",
            "anthropic_working": self.test_anthropic_connection()["status"] == "success"
        }
    
    def get_recommended_service(self, task_type: str = "general") -> str:
        """Get recommended service for specific task"""
        services = self.get_available_services()
        
        # Priority order based on task type and availability
        if task_type == "arabic_analysis":
            if services.get("anthropic_working"):
                return "anthropic"  # Claude is often better for Arabic
            elif services.get("openai_working"):
                return "openai"
        else:
            if services.get("openai_working"):
                return "openai"
            elif services.get("anthropic_working"):
                return "anthropic"
        
        return None
    
    def analyze_arabic_text(self, text: str, service: str = None) -> Dict[str, Any]:
        """Analyze Arabic text using best available service"""
        if not service:
            service = self.get_recommended_service("arabic_analysis")
        
        if not service:
            raise Exception("No AI services available")
        
        try:
            if service == "openai":
                return self._analyze_with_openai(text)
            elif service == "anthropic":
                return self._analyze_with_anthropic(text)
            else:
                raise ValueError(f"Unknown service: {service}")
        except Exception as e:
            # Fallback to other service if available
            fallback_service = "anthropic" if service == "openai" else "openai"
            if self.get_available_services().get(f"{fallback_service}_working"):
                logger.warning(f"Primary service {service} failed, falling back to {fallback_service}")
                return self.analyze_arabic_text(text, fallback_service)
            else:
                raise e
    
    def _analyze_with_openai(self, text: str) -> Dict[str, Any]:
        """Analyze text using OpenAI"""
        client = self.get_openai_client()
        
        prompt = f"""
        Analyze this Arabic text for sentiment, topics, and cultural context:
        
        Text: {text}
        
        Respond with JSON format:
        {{
            "sentiment": {{"score": 0.0, "label": "positive/negative/neutral", "confidence": 0.0}},
            "topics": ["topic1", "topic2"],
            "cultural_context": "description",
            "language": "ar",
            "service": "openai"
        }}
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=500
        )
        
        import json
        return json.loads(response.choices[0].message.content)
    
    def _analyze_with_anthropic(self, text: str) -> Dict[str, Any]:
        """Analyze text using Anthropic Claude"""
        client = self.get_anthropic_client()
        
        prompt = f"""
        Analyze this Arabic text for sentiment, topics, and cultural context:
        
        Text: {text}
        
        Respond with JSON format only:
        {{
            "sentiment": {{"score": 0.0, "label": "positive/negative/neutral", "confidence": 0.0}},
            "topics": ["topic1", "topic2"],
            "cultural_context": "description", 
            "language": "ar",
            "service": "anthropic"
        }}
        """
        
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        import json
        return json.loads(response.content[0].text)

# Global instance
api_manager = APIKeyManager()