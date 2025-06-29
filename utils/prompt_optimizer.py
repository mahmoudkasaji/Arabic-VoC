"""
Prompt Optimization and Cultural Context Management Utilities
Provides A/B testing, token optimization, and cultural adaptation capabilities
"""

import re
import logging
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class PromptMetrics:
    """Metrics for prompt performance tracking"""
    token_count: int
    compression_ratio: float
    readability_score: float
    cultural_sensitivity_score: float
    effectiveness_score: Optional[float] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class PromptOptimizer:
    """Advanced prompt optimization with A/B testing and compression utilities"""
    
    def __init__(self):
        self.optimization_history = []
        self.performance_baselines = {}
        
        # Compression rules for Arabic and English
        self.compression_rules = {
            "redundant_phrases": {
                "Please analyze": "Analyze",
                "You should": "",
                "Make sure to": "",
                "It's important that": "",
                "I want you to": "",
                "Can you please": "",
                "يرجى تحليل": "حلل",
                "يجب عليك": "",
                "تأكد من": "",
                "من المهم أن": "",
                "أريد منك أن": ""
            },
            "verbose_expressions": {
                "in order to": "to",
                "due to the fact that": "because",
                "for the purpose of": "to",
                "in the event that": "if",
                "at this point in time": "now",
                "من أجل": "لـ",
                "بسبب حقيقة أن": "لأن",
                "في حالة": "إذا",
                "في هذا الوقت": "الآن"
            },
            "formatting_optimizations": {
                r"\n\s*\n": "\n",  # Multiple line breaks
                r" {2,}": " ",      # Multiple spaces
                r"\t+": " ",        # Tabs to spaces
            }
        }
        
        # Token estimation patterns
        self.token_patterns = {
            "arabic_char_ratio": 0.8,  # Arabic characters are roughly 0.8 tokens each
            "english_char_ratio": 0.25, # English ~4 chars per token
            "punctuation_ratio": 0.5,
            "number_ratio": 0.3
        }
    
    def compress_prompt(self, prompt: str, compression_level: str = "balanced") -> Tuple[str, PromptMetrics]:
        """
        Compress prompt while maintaining effectiveness
        
        Args:
            prompt: Original prompt text
            compression_level: 'conservative', 'balanced', 'aggressive'
        
        Returns:
            Tuple of (compressed_prompt, metrics)
        """
        
        original_length = len(prompt)
        compressed = prompt
        
        # Apply compression rules based on level
        if compression_level in ['balanced', 'aggressive']:
            # Remove redundant phrases
            for old, new in self.compression_rules["redundant_phrases"].items():
                compressed = compressed.replace(old, new)
        
        if compression_level == 'aggressive':
            # Remove verbose expressions
            for old, new in self.compression_rules["verbose_expressions"].items():
                compressed = compressed.replace(old, new)
        
        # Apply formatting optimizations for all levels
        for pattern, replacement in self.compression_rules["formatting_optimizations"].items():
            compressed = re.sub(pattern, replacement, compressed)
        
        # Calculate metrics
        compression_ratio = (original_length - len(compressed)) / original_length
        token_count = self.measure_token_usage(compressed)
        readability_score = self._calculate_readability_score(compressed)
        cultural_sensitivity_score = self._calculate_cultural_sensitivity(compressed)
        
        metrics = PromptMetrics(
            token_count=token_count,
            compression_ratio=compression_ratio,
            readability_score=readability_score,
            cultural_sensitivity_score=cultural_sensitivity_score
        )
        
        # Store optimization history
        self.optimization_history.append({
            "original_length": original_length,
            "compressed_length": len(compressed),
            "compression_level": compression_level,
            "metrics": metrics,
            "timestamp": datetime.utcnow()
        })
        
        return compressed.strip(), metrics
    
    def measure_token_usage(self, prompt: str) -> int:
        """
        Advanced token estimation considering Arabic and English text
        """
        
        # Count different character types
        arabic_chars = len(re.findall(r'[\u0600-\u06FF]', prompt))
        english_chars = len(re.findall(r'[a-zA-Z]', prompt))
        punctuation = len(re.findall(r'[^\w\s]', prompt))
        numbers = len(re.findall(r'\d', prompt))
        
        # Calculate tokens based on character type
        arabic_tokens = arabic_chars * self.token_patterns["arabic_char_ratio"]
        english_tokens = english_chars * self.token_patterns["english_char_ratio"]
        punctuation_tokens = punctuation * self.token_patterns["punctuation_ratio"]
        number_tokens = numbers * self.token_patterns["number_ratio"]
        
        estimated_tokens = int(arabic_tokens + english_tokens + punctuation_tokens + number_tokens)
        
        # Add buffer for special tokens and formatting
        return max(1, int(estimated_tokens * 1.1))
    
    def optimize_for_model(self, prompt: str, target_model: str) -> Tuple[str, PromptMetrics]:
        """
        Optimize prompt specifically for target AI model
        """
        
        model_specific_optimizations = {
            "jais": {
                "prefer_arabic": True,
                "compression_level": "conservative",
                "cultural_context": "enhanced"
            },
            "anthropic": {
                "prefer_structure": True,
                "compression_level": "balanced",
                "reasoning_chain": True
            },
            "openai": {
                "prefer_conciseness": True,
                "compression_level": "aggressive",
                "json_format": True
            }
        }
        
        config = model_specific_optimizations.get(target_model, {})
        compression_level = config.get("compression_level", "balanced")
        
        # Apply model-specific optimizations
        optimized_prompt = prompt
        
        if config.get("prefer_arabic") and target_model == "jais":
            # Enhance Arabic instructions for JAIS
            optimized_prompt = self._enhance_arabic_instructions(optimized_prompt)
        
        if config.get("prefer_structure") and target_model == "anthropic":
            # Add structured thinking for Anthropic
            optimized_prompt = self._add_structured_thinking(optimized_prompt)
        
        if config.get("prefer_conciseness") and target_model == "openai":
            # Make more concise for OpenAI
            compression_level = "aggressive"
        
        # Apply compression
        compressed_prompt, metrics = self.compress_prompt(optimized_prompt, compression_level)
        
        return compressed_prompt, metrics
    
    def a_b_test_prompts(self, prompt_variants: List[str], test_name: str) -> Dict[str, Any]:
        """
        Set up A/B testing framework for prompt variants
        """
        
        test_results = {
            "test_name": test_name,
            "variants": {},
            "setup_timestamp": datetime.utcnow(),
            "status": "initialized"
        }
        
        for i, prompt in enumerate(prompt_variants):
            variant_id = f"variant_{chr(65 + i)}"  # A, B, C, etc.
            metrics = self._analyze_prompt_structure(prompt)
            
            test_results["variants"][variant_id] = {
                "prompt": prompt,
                "metrics": metrics,
                "performance_data": [],
                "token_cost": self.measure_token_usage(prompt)
            }
        
        # Store test configuration
        self.performance_baselines[test_name] = test_results
        
        return test_results
    
    def record_performance(self, test_name: str, variant_id: str, 
                          performance_score: float, response_time: float) -> None:
        """
        Record performance data for A/B test variants
        """
        
        if test_name in self.performance_baselines:
            test_data = self.performance_baselines[test_name]
            if variant_id in test_data["variants"]:
                test_data["variants"][variant_id]["performance_data"].append({
                    "score": performance_score,
                    "response_time": response_time,
                    "timestamp": datetime.utcnow()
                })
                
                # Update test status
                test_data["status"] = "collecting_data"
    
    def get_best_performing_variant(self, test_name: str) -> Optional[Dict[str, Any]]:
        """
        Analyze A/B test results and return best performing variant
        """
        
        if test_name not in self.performance_baselines:
            return None
        
        test_data = self.performance_baselines[test_name]
        best_variant = None
        best_score = -1
        
        for variant_id, variant_data in test_data["variants"].items():
            performance_data = variant_data["performance_data"]
            
            if performance_data:
                avg_score = sum(p["score"] for p in performance_data) / len(performance_data)
                avg_time = sum(p["response_time"] for p in performance_data) / len(performance_data)
                
                # Combined score considering performance and efficiency
                combined_score = avg_score * 0.7 + (1.0 / max(avg_time, 0.1)) * 0.3
                
                if combined_score > best_score:
                    best_score = combined_score
                    best_variant = {
                        "variant_id": variant_id,
                        "prompt": variant_data["prompt"],
                        "avg_performance": avg_score,
                        "avg_response_time": avg_time,
                        "combined_score": combined_score,
                        "sample_size": len(performance_data)
                    }
        
        return best_variant
    
    def _calculate_readability_score(self, text: str) -> float:
        """Calculate readability score for the prompt"""
        
        # Simple readability metrics
        sentences = len(re.split(r'[.!?]+', text))
        words = len(text.split())
        avg_sentence_length = words / max(sentences, 1)
        
        # Shorter sentences = higher readability
        readability = max(0.0, min(1.0, 1.0 - (avg_sentence_length - 10) / 20))
        
        return readability
    
    def _calculate_cultural_sensitivity(self, text: str) -> float:
        """Calculate cultural sensitivity score"""
        
        # Check for inclusive language and cultural awareness
        sensitive_phrases = [
            "cultural context", "السياق الثقافي",
            "respectful", "محترم",
            "appropriate", "مناسب"
        ]
        
        sensitivity_score = sum(1 for phrase in sensitive_phrases if phrase in text.lower())
        return min(1.0, sensitivity_score / 3)  # Normalize to 0-1
    
    def _enhance_arabic_instructions(self, prompt: str) -> str:
        """Enhance prompt with better Arabic instructions"""
        
        if "النص:" not in prompt and "text:" in prompt.lower():
            prompt = prompt.replace("text:", "النص:")
        
        if "تحليل" not in prompt and "analyz" in prompt.lower():
            prompt = prompt.replace("Analyze", "حلل").replace("analyze", "حلل")
        
        return prompt
    
    def _add_structured_thinking(self, prompt: str) -> str:
        """Add structured thinking patterns for Anthropic"""
        
        if "step by step" not in prompt.lower():
            prompt += "\n\nThink through this step by step:"
        
        return prompt
    
    def _analyze_prompt_structure(self, prompt: str) -> Dict[str, Any]:
        """Analyze structural characteristics of a prompt"""
        
        return {
            "length": len(prompt),
            "token_estimate": self.measure_token_usage(prompt),
            "sentence_count": len(re.split(r'[.!?]+', prompt)),
            "question_count": prompt.count('?'),
            "instruction_count": len(re.findall(r'\b(analyze|calculate|determine|explain)\b', prompt.lower())),
            "arabic_content_ratio": len(re.findall(r'[\u0600-\u06FF]', prompt)) / max(len(prompt), 1)
        }


class CulturalContextManager:
    """Advanced cultural adaptation and context management for Arabic text analysis"""
    
    def __init__(self):
        self.cultural_mappings = {
            "religious_expressions": {
                "ما شاء الله": {"sentiment_modifier": 0.2, "indicates": "positive", "context": "admiration"},
                "إن شاء الله": {"sentiment_modifier": 0.0, "indicates": "neutral", "context": "future_hope"},
                "الحمد لله": {"sentiment_modifier": 0.1, "indicates": "acceptance", "context": "gratitude"},
                "سبحان الله": {"sentiment_modifier": 0.15, "indicates": "positive", "context": "amazement"},
                "لا حول ولا قوة إلا بالله": {"sentiment_modifier": -0.1, "indicates": "resignation", "context": "difficulty"},
                "أستغفر الله": {"sentiment_modifier": -0.05, "indicates": "regret", "context": "mistake"},
                "توكلت على الله": {"sentiment_modifier": 0.1, "indicates": "confidence", "context": "trust"},
                "بإذن الله": {"sentiment_modifier": 0.05, "indicates": "hopeful", "context": "future_plan"}
            },
            "cultural_intensifiers": {
                "والله": {"intensity_modifier": 1.3, "indicates": "strong_emphasis"},
                "أقسم بالله": {"intensity_modifier": 1.5, "indicates": "oath"},
                "صدقني": {"intensity_modifier": 1.2, "indicates": "sincerity"},
                "بصراحة": {"intensity_modifier": 1.1, "indicates": "honesty"},
                "جداً": {"intensity_modifier": 1.2, "indicates": "emphasis"},
                "أبداً": {"intensity_modifier": 1.4, "indicates": "absolute_negation"},
                "أكيد": {"intensity_modifier": 1.2, "indicates": "certainty"}
            },
            "politeness_markers": {
                "أستاذ": {"politeness_score": 0.8, "formality": "high"},
                "دكتور": {"politeness_score": 0.9, "formality": "high"},
                "أخي": {"politeness_score": 0.6, "formality": "medium"},
                "أختي": {"politeness_score": 0.6, "formality": "medium"},
                "حضرتك": {"politeness_score": 0.9, "formality": "high"},
                "لو سمحت": {"politeness_score": 0.7, "formality": "medium"},
                "من فضلك": {"politeness_score": 0.7, "formality": "medium"},
                "كرماً": {"politeness_score": 0.8, "formality": "high"}
            },
            "regional_variations": {
                "gulf": {
                    "markers": ["أكيد", "زين", "ماشي", "يلا"],
                    "sentiment_tendency": "direct"
                },
                "levantine": {
                    "markers": ["تمام", "ماشي", "يلا", "إيش"],
                    "sentiment_tendency": "expressive"
                },
                "egyptian": {
                    "markers": ["كده", "خلاص", "يلا", "ازيك"],
                    "sentiment_tendency": "humorous"
                },
                "maghrebi": {
                    "markers": ["واخا", "بزاف", "شكون"],
                    "sentiment_tendency": "reserved"
                }
            }
        }
        
        self.cultural_analysis_history = []
    
    def adjust_sentiment_for_culture(self, text: str, base_sentiment: float, 
                                   detected_dialect: str = None) -> Dict[str, Any]:
        """
        Advanced sentiment adjustment based on cultural expressions and regional context
        """
        
        adjustments = {
            "religious_modifier": 0.0,
            "intensity_modifier": 1.0,
            "politeness_modifier": 0.0,
            "regional_modifier": 0.0
        }
        
        cultural_features = {
            "religious_expressions": [],
            "intensity_markers": [],
            "politeness_level": 0.0,
            "formality_level": "medium",
            "detected_region": detected_dialect or "standard"
        }
        
        # Analyze religious expressions
        for expr, data in self.cultural_mappings["religious_expressions"].items():
            if expr in text:
                adjustments["religious_modifier"] += data["sentiment_modifier"]
                cultural_features["religious_expressions"].append({
                    "expression": expr,
                    "context": data["context"],
                    "modifier": data["sentiment_modifier"]
                })
        
        # Analyze cultural intensifiers
        for intensifier, data in self.cultural_mappings["cultural_intensifiers"].items():
            if intensifier in text:
                adjustments["intensity_modifier"] *= data["intensity_modifier"]
                cultural_features["intensity_markers"].append({
                    "marker": intensifier,
                    "type": data["indicates"],
                    "multiplier": data["intensity_modifier"]
                })
        
        # Analyze politeness markers
        politeness_scores = []
        for marker, data in self.cultural_mappings["politeness_markers"].items():
            if marker in text:
                politeness_scores.append(data["politeness_score"])
                cultural_features["formality_level"] = data["formality"]
        
        if politeness_scores:
            cultural_features["politeness_level"] = sum(politeness_scores) / len(politeness_scores)
            adjustments["politeness_modifier"] = cultural_features["politeness_level"] * 0.1
        
        # Apply regional adjustments
        if detected_dialect:
            regional_data = self.cultural_mappings["regional_variations"].get(detected_dialect, {})
            if regional_data:
                # Check for regional markers
                markers_found = sum(1 for marker in regional_data.get("markers", []) if marker in text)
                if markers_found > 0:
                    cultural_features["detected_region"] = detected_dialect
                    # Regional sentiment tendencies
                    tendency = regional_data.get("sentiment_tendency", "neutral")
                    if tendency == "expressive":
                        adjustments["regional_modifier"] = 0.1
                    elif tendency == "reserved":
                        adjustments["regional_modifier"] = -0.05
        
        # Calculate final adjusted sentiment
        adjusted_sentiment = base_sentiment
        adjusted_sentiment += adjustments["religious_modifier"]
        adjusted_sentiment *= adjustments["intensity_modifier"]
        adjusted_sentiment += adjustments["politeness_modifier"]
        adjusted_sentiment += adjustments["regional_modifier"]
        
        # Ensure sentiment stays within bounds
        adjusted_sentiment = max(-1.0, min(1.0, adjusted_sentiment))
        
        # Calculate cultural confidence score
        cultural_features_count = (
            len(cultural_features["religious_expressions"]) +
            len(cultural_features["intensity_markers"]) +
            (1 if cultural_features["politeness_level"] > 0 else 0)
        )
        
        cultural_confidence = min(1.0, cultural_features_count * 0.2)
        
        result = {
            "original_sentiment": base_sentiment,
            "adjusted_sentiment": adjusted_sentiment,
            "sentiment_change": adjusted_sentiment - base_sentiment,
            "cultural_features": cultural_features,
            "adjustments_applied": adjustments,
            "cultural_confidence": cultural_confidence,
            "analysis_timestamp": datetime.utcnow()
        }
        
        # Store analysis history
        self.cultural_analysis_history.append(result)
        
        return result
    
    def detect_cultural_context(self, text: str) -> Dict[str, Any]:
        """
        Detect cultural context markers in Arabic text
        """
        
        context_indicators = {
            "religious_tone": "absent",
            "formality_level": "medium",
            "regional_dialect": "standard",
            "emotional_intensity": "medium",
            "cultural_markers": []
        }
        
        # Check religious tone
        religious_count = sum(1 for expr in self.cultural_mappings["religious_expressions"] if expr in text)
        if religious_count >= 2:
            context_indicators["religious_tone"] = "strong"
        elif religious_count == 1:
            context_indicators["religious_tone"] = "present"
        
        # Determine formality level
        formal_markers = [marker for marker in self.cultural_mappings["politeness_markers"] 
                         if marker in text and self.cultural_mappings["politeness_markers"][marker]["formality"] == "high"]
        if formal_markers:
            context_indicators["formality_level"] = "high"
        
        # Detect regional dialect
        for region, data in self.cultural_mappings["regional_variations"].items():
            markers_found = [marker for marker in data["markers"] if marker in text]
            if len(markers_found) >= 2:
                context_indicators["regional_dialect"] = region
                context_indicators["cultural_markers"].extend(markers_found)
                break
        
        # Assess emotional intensity
        intensity_markers = [marker for marker in self.cultural_mappings["cultural_intensifiers"] if marker in text]
        if len(intensity_markers) >= 2:
            context_indicators["emotional_intensity"] = "high"
        elif len(intensity_markers) == 1:
            context_indicators["emotional_intensity"] = "elevated"
        
        return context_indicators
    
    def get_cultural_recommendations(self, analysis_result: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations for cultural adaptation
        """
        
        recommendations = []
        
        cultural_features = analysis_result.get("cultural_features", {})
        
        # Religious context recommendations
        if cultural_features.get("religious_expressions"):
            recommendations.append("Consider religious context when interpreting sentiment intensity")
            recommendations.append("Religious expressions often indicate acceptance rather than negative sentiment")
        
        # Formality recommendations
        if cultural_features.get("formality_level") == "high":
            recommendations.append("High formality detected - responses should maintain respectful tone")
            recommendations.append("Consider cultural hierarchy and respect markers in communication")
        
        # Regional adaptation
        detected_region = cultural_features.get("detected_region", "standard")
        if detected_region != "standard":
            recommendations.append(f"Regional dialect detected: {detected_region}")
            recommendations.append(f"Adapt response style for {detected_region} cultural expectations")
        
        # Intensity considerations
        if cultural_features.get("intensity_markers"):
            recommendations.append("Emotional intensifiers detected - sentiment may be culturally amplified")
            recommendations.append("Consider cultural expression patterns when measuring sentiment strength")
        
        return recommendations
    
    def get_cultural_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about cultural analysis performance
        """
        
        if not self.cultural_analysis_history:
            return {"error": "No cultural analysis history available"}
        
        recent_analyses = self.cultural_analysis_history[-20:]  # Last 20 analyses
        
        avg_cultural_confidence = sum(a["cultural_confidence"] for a in recent_analyses) / len(recent_analyses)
        avg_sentiment_change = sum(abs(a["sentiment_change"]) for a in recent_analyses) / len(recent_analyses)
        
        # Count feature types
        religious_features = sum(1 for a in recent_analyses if a["cultural_features"]["religious_expressions"])
        regional_features = sum(1 for a in recent_analyses if a["cultural_features"]["detected_region"] != "standard")
        
        return {
            "total_analyses": len(self.cultural_analysis_history),
            "recent_performance": {
                "average_cultural_confidence": avg_cultural_confidence,
                "average_sentiment_change": avg_sentiment_change,
                "religious_context_frequency": religious_features / len(recent_analyses),
                "regional_dialect_frequency": regional_features / len(recent_analyses)
            },
            "feature_coverage": {
                "religious_expressions": len(self.cultural_mappings["religious_expressions"]),
                "cultural_intensifiers": len(self.cultural_mappings["cultural_intensifiers"]),
                "politeness_markers": len(self.cultural_mappings["politeness_markers"]),
                "regional_variations": len(self.cultural_mappings["regional_variations"])
            }
        }