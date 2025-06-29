"""
Specialized Analysis Agents for Arabic VoC Platform
Clean separation of concerns: Sentiment, Topics, and Recommendations
"""

import logging
import json
import hashlib
from enum import Enum
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class PromptStrategy(Enum):
    DIRECT = "direct"
    CHAIN_OF_THOUGHT = "cot"
    FEW_SHOT = "few_shot"
    SELF_CONSISTENCY = "self_consistency"

class BaseAgent:
    def __init__(self, name: str):
        self.name = name
        self.prompt_variants = {}
        self.few_shot_examples = {}
        self.prompt_strategy = PromptStrategy.DIRECT
        
    def add_prompt_variant(self, variant_name: str, prompt_template: str):
        """Add A/B testing variant"""
        self.prompt_variants[variant_name] = prompt_template
        
    def add_few_shot_examples(self, service: str, examples: List[Dict]):
        """Add dialect-specific examples for each service"""
        self.few_shot_examples[service] = examples
        
    def select_prompt_strategy(self, text: str, context: Dict) -> PromptStrategy:
        """Dynamically select strategy based on input complexity"""
        text_length = len(text.split())
        
        # Complex texts benefit from CoT
        if text_length > 50 or "؟" in text:  # Questions often need more reasoning
            return PromptStrategy.CHAIN_OF_THOUGHT
        
        # Dialectal text benefits from few-shot
        dialect_markers = ["والله", "يعني", "ايش", "ليش", "وايد"]
        if any(marker in text for marker in dialect_markers):
            return PromptStrategy.FEW_SHOT
            
        return PromptStrategy.DIRECT

class SentimentAnalysisAgent(BaseAgent):
    """Dedicated agent for Arabic sentiment analysis with cultural context"""
    
    def __init__(self, api_manager):
        super().__init__("SentimentAnalyst")
        self.api_manager = api_manager
        self.setup_prompts()
        self.setup_few_shot_examples()
        
        # Cultural sentiment markers for Arabic
        self.cultural_sentiment_patterns = {
            'positive_religious': ['الحمد لله', 'بارك الله', 'ما شاء الله', 'جزاكم الله خير'],
            'positive_gratitude': ['شكراً', 'أشكركم', 'ممتن', 'مقدر'],
            'positive_satisfaction': ['ممتاز', 'رائع', 'جيد جداً', 'مذهل', 'فوق التوقعات'],
            'negative_disappointment': ['محبط', 'مخيب للآمال', 'سيء', 'فاشل'],
            'negative_complaints': ['أشكو', 'مشكلة', 'خطأ', 'عيب', 'نقص'],
            'neutral_inquiry': ['استفسار', 'سؤال', 'معلومات', 'توضيح']
        }
    
    def setup_prompts(self):
        """Setup advanced prompting strategies for each AI service"""
        self.prompts = {
            "jais": {
                PromptStrategy.DIRECT: """
                حلل مشاعر هذا النص العربي مع مراعاة السياق الثقافي والديني:
                
                النص: {text}
                {dialect_note}
                
                أجب بصيغة JSON فقط:
                {{
                    "sentiment": {{
                        "score": 0.0,
                        "label": "إيجابي/سلبي/محايد", 
                        "confidence": 0.0,
                        "intensity": "ضعيف/متوسط/قوي"
                    }},
                    "emotional_dimensions": {{
                        "satisfaction": 0.0,
                        "frustration": 0.0,
                        "gratitude": 0.0,
                        "concern": 0.0
                    }},
                    "cultural_sentiment": {{
                        "religious_tone": "موجود/غير موجود",
                        "formality_level": "رسمي/غير رسمي/محايد",
                        "cultural_appropriateness": 0.0
                    }},
                    "service": "jais",
                    "analysis_method": "native_arabic_sentiment"
                }}
                """,
                
                PromptStrategy.CHAIN_OF_THOUGHT: """
                أنت محلل متخصص في اللغة العربية. حلل هذا النص خطوة بخطوة:

                النص: {text}

                الخطوة ١: حدد اللهجة ومستوى الرسمية
                - ما هي علامات اللهجة الموجودة؟
                - هل النص رسمي أم غير رسمي؟

                الخطوة ٢: حلل المؤشرات العاطفية
                - اذكر المؤشرات الإيجابية
                - اذكر المؤشرات السلبية
                - حدد أي مشاعر متضاربة

                الخطوة ٣: قيّم السياق الثقافي
                - كيف تؤثر المعايير الثقافية على التفسير؟
                - هل هناك تعبيرات غير مباشرة؟

                الخطوة ٤: الحكم النهائي
                بناءً على تحليلك، قدم JSON:
                {{
                    "reasoning": "تفسير موجز للتحليل",
                    "sentiment": {{
                        "score": 0.0,
                        "label": "إيجابي/سلبي/محايد",
                        "confidence": 0.0,
                        "intensity": "ضعيف/متوسط/قوي"
                    }},
                    "emotional_dimensions": {{
                        "satisfaction": 0.0,
                        "frustration": 0.0,
                        "gratitude": 0.0,
                        "concern": 0.0
                    }},
                    "cultural_sentiment": {{
                        "religious_tone": "موجود/غير موجود",
                        "formality_level": "رسمي/غير رسمي/محايد",
                        "cultural_appropriateness": 0.0
                    }},
                    "service": "jais",
                    "analysis_method": "chain_of_thought_arabic"
                }}
                """,
                
                PromptStrategy.FEW_SHOT: """
                حلل مشاعر هذا النص العربي مستعيناً بهذه الأمثلة:

                {examples}

                النص المطلوب تحليله: {text}

                استخدم نفس صيغة JSON في الأمثلة:
                {{
                    "sentiment": {{
                        "score": 0.0,
                        "label": "إيجابي/سلبي/محايد",
                        "confidence": 0.0,
                        "intensity": "ضعيف/متوسط/قوي"
                    }},
                    "reasoning": "سبب التصنيف",
                    "service": "jais",
                    "analysis_method": "few_shot_arabic"
                }}
                """
            },
            
            "anthropic": {
                PromptStrategy.DIRECT: """
                Analyze the sentiment of this Arabic text with deep cultural understanding. {cultural_note}
                
                Text: {text}
                
                Respond with JSON only:
                {{
                    "sentiment": {{
                        "score": 0.0,
                        "label": "positive/negative/neutral",
                        "confidence": 0.0,
                        "intensity": "weak/moderate/strong"
                    }},
                    "emotional_dimensions": {{
                        "satisfaction": 0.0,
                        "frustration": 0.0,
                        "gratitude": 0.0,
                        "concern": 0.0
                    }},
                    "cultural_sentiment": {{
                        "religious_tone": "present/absent",
                        "formality_level": "formal/informal/neutral",
                        "cultural_appropriateness": 0.0
                    }},
                    "service": "anthropic",
                    "analysis_method": "nuanced_cultural_sentiment"
                }}
                """,
                
                PromptStrategy.CHAIN_OF_THOUGHT: """
                You are an expert Arabic sentiment analyst. Analyze this text step by step:

                Text: {text}

                Step 1: Identify dialectal and formality markers
                - What dialect indicators are present?
                - Is this formal or informal language?

                Step 2: Analyze emotional indicators  
                - List positive sentiment markers
                - List negative sentiment markers
                - Identify any conflicting emotions

                Step 3: Evaluate cultural context
                - How do cultural norms affect interpretation?
                - Are there indirect expressions?

                Step 4: Cultural sensitivity assessment
                - Consider religious expressions
                - Evaluate appropriateness of response tone

                Step 5: Final judgment
                Based on your analysis, provide JSON:
                {{
                    "reasoning": "Brief explanation of analysis",
                    "sentiment": {{
                        "score": 0.0,
                        "label": "positive/negative/neutral",
                        "confidence": 0.0,
                        "intensity": "weak/moderate/strong"
                    }},
                    "cultural_sentiment": {{
                        "religious_tone": "present/absent",
                        "formality_level": "formal/informal/neutral",
                        "cultural_appropriateness": 0.0
                    }},
                    "service": "anthropic",
                    "analysis_method": "chain_of_thought_cultural"
                }}
                """,
                
                PromptStrategy.FEW_SHOT: """
                Analyze the sentiment of this Arabic text using these examples as reference:

                {examples}

                Text to analyze: {text}

                Use the same JSON format as the examples:
                {{
                    "sentiment": {{
                        "score": 0.0,
                        "label": "positive/negative/neutral",
                        "confidence": 0.0,
                        "intensity": "weak/moderate/strong"
                    }},
                    "reasoning": "Explanation for classification",
                    "service": "anthropic",
                    "analysis_method": "few_shot_cultural"
                }}
                """
            },
            
            "openai": {
                PromptStrategy.DIRECT: """
                Analyze the sentiment of this Arabic text efficiently and accurately.
                
                Text: {text}
                
                Respond with JSON format:
                {{
                    "sentiment": {{
                        "score": 0.0,
                        "label": "positive/negative/neutral",
                        "confidence": 0.0,
                        "intensity": "weak/moderate/strong"
                    }},
                    "emotional_dimensions": {{
                        "satisfaction": 0.0,
                        "frustration": 0.0,
                        "gratitude": 0.0,
                        "concern": 0.0
                    }},
                    "cultural_sentiment": {{
                        "religious_tone": "present/absent",
                        "formality_level": "formal/informal/neutral",
                        "cultural_appropriateness": 0.0
                    }},
                    "service": "openai",
                    "analysis_method": "fast_sentiment_analysis"
                }}
                """,
                
                PromptStrategy.CHAIN_OF_THOUGHT: """
                Analyze this Arabic text sentiment using step-by-step reasoning:

                Text: {text}

                Step 1: Language analysis
                - Identify key sentiment words
                - Note any cultural expressions

                Step 2: Emotional assessment
                - Evaluate positive vs negative indicators
                - Consider emotional intensity

                Step 3: Cultural context
                - Account for Arabic communication patterns
                - Consider indirect expressions

                Step 4: Final scoring
                Provide detailed JSON analysis:
                {{
                    "reasoning": "Step-by-step explanation",
                    "sentiment": {{
                        "score": 0.0,
                        "label": "positive/negative/neutral",
                        "confidence": 0.0,
                        "intensity": "weak/moderate/strong"
                    }},
                    "service": "openai",
                    "analysis_method": "chain_of_thought_fast"
                }}
                """,
                
                PromptStrategy.FEW_SHOT: """
                Analyze Arabic text sentiment using these examples:

                {examples}

                Text: {text}

                Follow the same JSON structure:
                {{
                    "sentiment": {{
                        "score": 0.0,
                        "label": "positive/negative/neutral",
                        "confidence": 0.0,
                        "intensity": "weak/moderate/strong"
                    }},
                    "reasoning": "Classification rationale",
                    "service": "openai",
                    "analysis_method": "few_shot_fast"
                }}
                """
            }
        }
    
    def setup_few_shot_examples(self):
        """Setup dialect-specific examples for few-shot learning"""
        self.few_shot_examples = {
            "gulf": [
                {
                    "text": "والله الخدمة وايد زينة ما شاء الله",
                    "analysis": {
                        "sentiment": {"score": 0.9, "label": "positive", "confidence": 0.95, "intensity": "strong"},
                        "reasoning": "Gulf dialect with religious expressions showing strong satisfaction"
                    }
                },
                {
                    "text": "يا ويلي شلون كذا؟ ما صار شي زين",
                    "analysis": {
                        "sentiment": {"score": -0.7, "label": "negative", "confidence": 0.85, "intensity": "moderate"},
                        "reasoning": "Gulf dialect expressing disappointment and dissatisfaction"
                    }
                }
            ],
            "egyptian": [
                {
                    "text": "الموضوع ده مش ولا بد خالص",
                    "analysis": {
                        "sentiment": {"score": -0.8, "label": "negative", "confidence": 0.9, "intensity": "strong"},
                        "reasoning": "Egyptian colloquial expressing strong dissatisfaction"
                    }
                },
                {
                    "text": "ده حلو قوي بجد ربنا يبارك",
                    "analysis": {
                        "sentiment": {"score": 0.85, "label": "positive", "confidence": 0.9, "intensity": "strong"},
                        "reasoning": "Egyptian dialect with religious blessing showing strong approval"
                    }
                }
            ],
            "levantine": [
                {
                    "text": "يعني منيح بس في مجال للتحسين",
                    "analysis": {
                        "sentiment": {"score": 0.1, "label": "neutral", "confidence": 0.8, "intensity": "weak"},
                        "reasoning": "Levantine hedging showing mild satisfaction with constructive criticism"
                    }
                },
                {
                    "text": "والله شغل ممتاز ما في أحسن من هيك",
                    "analysis": {
                        "sentiment": {"score": 0.95, "label": "positive", "confidence": 0.95, "intensity": "strong"},
                        "reasoning": "Levantine with religious emphasis expressing exceptional satisfaction"
                    }
                }
            ],
            "moroccan": [
                {
                    "text": "واخا هاذي زوينة بزاف الله يعطيك الصحة",
                    "analysis": {
                        "sentiment": {"score": 0.8, "label": "positive", "confidence": 0.85, "intensity": "strong"},
                        "reasoning": "Moroccan dialect with blessing showing strong appreciation"
                    }
                }
            ]
        }
    
    async def analyze_sentiment(self, text: str, text_characteristics: Dict) -> Dict[str, Any]:
        """Enhanced sentiment analysis with advanced prompting strategies"""
        
        # Pre-analysis: Detect cultural patterns and dialect
        cultural_context = self._detect_cultural_patterns(text)
        dialectal_info = text_characteristics.get('dialectal_analysis', {})
        
        # Select prompting strategy based on text complexity
        strategy = self.select_prompt_strategy(text, {
            'cultural_context': cultural_context,
            'dialectal_info': dialectal_info
        })
        
        # Choose best AI service for sentiment analysis
        best_service = self._select_sentiment_model(text_characteristics, dialectal_info)
        
        try:
            return await self._analyze_with_strategy(text, strategy, best_service, cultural_context, dialectal_info)
                
        except Exception as e:
            logger.error(f"Sentiment analysis failed with {best_service} using {strategy.value}: {e}")
            # Fallback to simpler analysis
            return self._fallback_sentiment_analysis(text, cultural_context)
    
    async def _analyze_with_strategy(self, text: str, strategy: PromptStrategy, service: str, 
                                   cultural_context: Dict, dialectal_info: Dict) -> Dict[str, Any]:
        """Execute analysis using selected strategy and service"""
        
        # Get appropriate prompt template
        prompt_template = self.prompts[service][strategy]
        
        # Prepare context for prompt formatting
        context = {
            'cultural_note': self._format_cultural_note(cultural_context),
            'dialect_note': self._format_dialect_note(dialectal_info)
        }
        
        # Add few-shot examples if using that strategy
        if strategy == PromptStrategy.FEW_SHOT:
            dialect = self._detect_primary_dialect(text)
            examples = self._format_few_shot_examples(dialect, service)
            context['examples'] = examples
        
        # Format prompt with confidence anchors
        prompt = self._format_prompt_with_anchors(prompt_template, text, context)
        
        # Call appropriate AI service
        if service == "jais":
            return await self._call_jais_with_prompt(prompt)
        elif service == "anthropic":
            return await self._call_anthropic_with_prompt(prompt)
        else:
            return await self._call_openai_with_prompt(prompt)
    
    def _detect_primary_dialect(self, text: str) -> str:
        """Detect the primary Arabic dialect in the text"""
        
        # Gulf dialect markers
        gulf_markers = ['والله', 'وايد', 'زين', 'شلون', 'يا ويلي', 'ما شاء الله']
        gulf_score = sum(1 for marker in gulf_markers if marker in text)
        
        # Egyptian dialect markers  
        egyptian_markers = ['ده', 'دي', 'مش', 'ولا بد', 'قوي', 'خالص', 'ربنا']
        egyptian_score = sum(1 for marker in egyptian_markers if marker in text)
        
        # Levantine dialect markers
        levantine_markers = ['يعني', 'منيح', 'هيك', 'بدي', 'عم', 'شو', 'كتير']
        levantine_score = sum(1 for marker in levantine_markers if marker in text)
        
        # Moroccan dialect markers
        moroccan_markers = ['واخا', 'بزاف', 'زوين', 'فين', 'غير', 'الله يعطيك']
        moroccan_score = sum(1 for marker in moroccan_markers if marker in text)
        
        # Determine primary dialect
        scores = {
            'gulf': gulf_score,
            'egyptian': egyptian_score, 
            'levantine': levantine_score,
            'moroccan': moroccan_score
        }
        
        primary_dialect = max(scores, key=scores.get)
        return primary_dialect if scores[primary_dialect] > 0 else 'standard'
    
    def _format_few_shot_examples(self, dialect: str, service: str) -> str:
        """Format few-shot examples for the detected dialect"""
        
        examples = self.few_shot_examples.get(dialect, self.few_shot_examples['gulf'])
        
        if service == "jais":
            # Arabic format for JAIS
            formatted = []
            for example in examples[:2]:  # Limit to 2 examples
                formatted.append(f"""
مثال:
النص: {example['text']}
التحليل: {json.dumps(example['analysis'], ensure_ascii=False, indent=2)}
""")
            return "\n".join(formatted)
        else:
            # English format for Anthropic/OpenAI
            formatted = []
            for example in examples[:2]:
                formatted.append(f"""
Example:
Text: {example['text']}
Analysis: {json.dumps(example['analysis'], ensure_ascii=False, indent=2)}
""")
            return "\n".join(formatted)
    
    def _format_cultural_note(self, cultural_context: Dict) -> str:
        """Format cultural context note for prompts"""
        if cultural_context.get('has_cultural_markers'):
            return "This text contains cultural/religious expressions."
        return ""
    
    def _format_dialect_note(self, dialectal_info: Dict) -> str:
        """Format dialect information note for prompts"""
        if dialectal_info.get('has_dialectal_content'):
            dialect = dialectal_info.get('primary_dialect', 'غير محددة')
            return f"اللهجة المكتشفة: {dialect}"
        return ""
    
    def _format_prompt_with_anchors(self, template: str, text: str, context: Dict) -> str:
        """Add dynamic scoring anchors to improve consistency"""
        
        # Confidence anchors for sentiment scoring
        anchors = {
            "-1.0": "سيئ جداً - لن أتعامل معكم مرة أخرى",
            "-0.5": "سيئ - يحتاج تحسين كبير", 
            "0.0": "عادي - مثل الآخرين",
            "0.5": "جيد - مع بعض الملاحظات",
            "1.0": "ممتاز - ما شاء الله"
        }
        
        # Add anchors if template supports them
        if "{anchors}" in template:
            anchor_text = "\n".join([f"{score}: {desc}" for score, desc in anchors.items()])
            context['anchors'] = anchor_text
        
        # Format template with all context
        return template.format(text=text, **context)
    
    async def _call_jais_with_prompt(self, prompt: str) -> Dict[str, Any]:
        """Call JAIS with formatted prompt"""
        client = self.api_manager.get_jais_client()
        
        response = client.chat.completions.create(
            model="jais-30b-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.2
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def _call_anthropic_with_prompt(self, prompt: str) -> Dict[str, Any]:
        """Call Anthropic with formatted prompt"""
        client = self.api_manager.get_anthropic_client()
        
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        
        return json.loads(response.content[0].text)
    
    async def _call_openai_with_prompt(self, prompt: str) -> Dict[str, Any]:
        """Call OpenAI with formatted prompt"""
        client = self.api_manager.get_openai_client()
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=500,
            temperature=0.2
        )
        
        return json.loads(response.choices[0].message.content)
    
    def _validate_output(self, result: Dict, strategy: PromptStrategy) -> Dict[str, Any]:
        """Validate and normalize analysis output"""
        
        # Ensure required fields exist
        if 'sentiment' not in result:
            result['sentiment'] = {"score": 0.0, "label": "neutral", "confidence": 0.5}
        
        # Add strategy metadata
        result['prompt_strategy'] = strategy.value
        result['enhanced_analysis'] = True
        
        # Normalize confidence scores
        if 'sentiment' in result and 'confidence' in result['sentiment']:
            confidence = result['sentiment']['confidence']
            if confidence > 1.0:
                result['sentiment']['confidence'] = confidence / 100.0
        
        return result
    
    def _detect_cultural_patterns(self, text: str) -> Dict[str, Any]:
        """Detect cultural sentiment patterns in Arabic text"""
        detected_patterns = {}
        
        for category, patterns in self.cultural_sentiment_patterns.items():
            matches = [pattern for pattern in patterns if pattern in text]
            if matches:
                detected_patterns[category] = matches
        
        # Detect formality level
        formal_indicators = ['حضرتك', 'سيادتك', 'المحترم', 'تفضلوا']
        informal_indicators = ['شو', 'ايش', 'يا رجل', 'والله']
        
        formality = 'formal' if any(ind in text for ind in formal_indicators) else \
                   'informal' if any(ind in text for ind in informal_indicators) else 'neutral'
        
        return {
            'cultural_patterns': detected_patterns,
            'formality_level': formality,
            'religious_expressions': len(detected_patterns.get('positive_religious', [])),
            'has_cultural_markers': bool(detected_patterns)
        }
    
    def _select_sentiment_model(self, text_characteristics: Dict, dialectal_info: Dict) -> str:
        """Select best model specifically for sentiment analysis"""
        
        # JAIS is best for dialectal content
        if dialectal_info.get('has_dialectal_content') and dialectal_info.get('dialect_density', 0) > 0.2:
            return "jais"
        
        # Anthropic for complex emotional nuance
        complexity = text_characteristics.get('complexity_analysis', {}).get('sentence_complexity', 0)
        if complexity > 6:
            return "anthropic"
        
        # OpenAI for fast, reliable sentiment
        return "openai"
    
    async def _analyze_with_jais(self, text: str, cultural_context: Dict, dialectal_info: Dict) -> Dict[str, Any]:
        """JAIS-specific sentiment analysis (Arabic native)"""
        client = self.api_manager.get_jais_client()
        
        dialect_note = f"اللهجة المكتشفة: {dialectal_info.get('primary_dialect', 'غير محددة')}" if dialectal_info.get('has_dialectal_content') else ""
        
        prompt = f"""
        حلل مشاعر هذا النص العربي مع مراعاة السياق الثقافي والديني:
        
        النص: {text}
        {dialect_note}
        
        أجب بصيغة JSON فقط:
        {{
            "sentiment": {{
                "score": 0.0,
                "label": "إيجابي/سلبي/محايد", 
                "confidence": 0.0,
                "intensity": "ضعيف/متوسط/قوي"
            }},
            "emotional_dimensions": {{
                "satisfaction": 0.0,
                "frustration": 0.0,
                "gratitude": 0.0,
                "concern": 0.0
            }},
            "cultural_sentiment": {{
                "religious_tone": "موجود/غير موجود",
                "formality_level": "رسمي/غير رسمي/محايد",
                "cultural_appropriateness": 0.0
            }},
            "service": "jais",
            "analysis_method": "native_arabic_sentiment"
        }}
        """
        
        response = client.chat.completions.create(
            model="jais-30b-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.2
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def _analyze_with_anthropic(self, text: str, cultural_context: Dict, dialectal_info: Dict) -> Dict[str, Any]:
        """Anthropic sentiment analysis for complex emotional nuance"""
        client = self.api_manager.get_anthropic_client()
        
        cultural_note = "This text contains cultural/religious expressions." if cultural_context.get('has_cultural_markers') else ""
        
        prompt = f"""
        Analyze the sentiment of this Arabic text with deep cultural understanding. {cultural_note}
        
        Text: {text}
        
        Respond with JSON only:
        {{
            "sentiment": {{
                "score": 0.0,
                "label": "positive/negative/neutral",
                "confidence": 0.0,
                "intensity": "weak/moderate/strong"
            }},
            "emotional_dimensions": {{
                "satisfaction": 0.0,
                "frustration": 0.0,
                "gratitude": 0.0,
                "concern": 0.0
            }},
            "cultural_sentiment": {{
                "religious_tone": "present/absent",
                "formality_level": "formal/informal/neutral",
                "cultural_appropriateness": 0.0
            }},
            "service": "anthropic",
            "analysis_method": "nuanced_cultural_sentiment"
        }}
        """
        
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        
        return json.loads(response.content[0].text)
    
    async def _analyze_with_openai(self, text: str, cultural_context: Dict, dialectal_info: Dict) -> Dict[str, Any]:
        """OpenAI sentiment analysis for fast, reliable results"""
        client = self.api_manager.get_openai_client()
        
        prompt = f"""
        Analyze the sentiment of this Arabic text efficiently and accurately.
        
        Text: {text}
        
        Respond with JSON format:
        {{
            "sentiment": {{
                "score": 0.0,
                "label": "positive/negative/neutral",
                "confidence": 0.0,
                "intensity": "weak/moderate/strong"
            }},
            "emotional_dimensions": {{
                "satisfaction": 0.0,
                "frustration": 0.0,
                "gratitude": 0.0,
                "concern": 0.0
            }},
            "cultural_sentiment": {{
                "religious_tone": "present/absent",
                "formality_level": "formal/informal/neutral",
                "cultural_appropriateness": 0.0
            }},
            "service": "openai",
            "analysis_method": "fast_sentiment_analysis"
        }}
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=400,
            temperature=0.2
        )
        
        return json.loads(response.choices[0].message.content)
    
    def _fallback_sentiment_analysis(self, text: str, cultural_context: Dict) -> Dict[str, Any]:
        """Simple fallback sentiment analysis"""
        
        # Basic keyword sentiment
        positive_words = ['ممتاز', 'جيد', 'رائع', 'شكراً', 'مفيد']
        negative_words = ['سيء', 'مشكلة', 'خطأ', 'محبط', 'فاشل']
        
        positive_score = sum(1 for word in positive_words if word in text)
        negative_score = sum(1 for word in negative_words if word in text)
        
        if positive_score > negative_score:
            sentiment = {"score": 0.7, "label": "positive", "confidence": 0.6}
        elif negative_score > positive_score:
            sentiment = {"score": -0.7, "label": "negative", "confidence": 0.6}
        else:
            sentiment = {"score": 0.0, "label": "neutral", "confidence": 0.5}
        
        return {
            "sentiment": {**sentiment, "intensity": "moderate"},
            "emotional_dimensions": {
                "satisfaction": max(0, positive_score * 0.2),
                "frustration": max(0, negative_score * 0.2),
                "gratitude": 0.3 if any(word in text for word in ['شكر', 'ممتن']) else 0.0,
                "concern": 0.3 if any(word in text for word in ['قلق', 'مشكلة']) else 0.0
            },
            "cultural_sentiment": {
                "religious_tone": "present" if cultural_context.get('religious_expressions', 0) > 0 else "absent",
                "formality_level": cultural_context.get('formality_level', 'neutral'),
                "cultural_appropriateness": 0.8
            },
            "service": "fallback",
            "analysis_method": "keyword_based_fallback"
        }


class TopicalAnalysisAgent(BaseAgent):
    """Dedicated agent for topic detection and categorization"""
    
    def __init__(self, api_manager):
        super().__init__("TopicalAnalyst")
        self.api_manager = api_manager
        
        # Arabic business topic categories
        self.topic_categories = {
            'customer_service': ['خدمة العملاء', 'موظف', 'تعامل', 'اهتمام', 'رد'],
            'product_quality': ['جودة', 'منتج', 'سلعة', 'مواصفات', 'عيب'],
            'pricing': ['سعر', 'تكلفة', 'مبلغ', 'رسوم', 'مصاريف'],
            'delivery': ['توصيل', 'شحن', 'وقت', 'تأخير', 'سرعة'],
            'technical_support': ['دعم فني', 'مساعدة', 'حل', 'مشكلة تقنية'],
            'billing': ['فاتورة', 'دفع', 'حساب', 'رسوم'],
            'experience': ['تجربة', 'استخدام', 'سهولة', 'صعوبة']
        }
    
    async def analyze_topics(self, text: str, text_characteristics: Dict, sentiment_context: Dict) -> Dict[str, Any]:
        """Comprehensive topic analysis with business intelligence"""
        
        # Pre-analysis: Detect obvious topic categories
        detected_categories = self._detect_topic_categories(text)
        
        # Choose model based on text complexity and topic depth needed
        best_service = self._select_topic_model(text_characteristics, detected_categories)
        
        try:
            if best_service == "anthropic":
                return await self._analyze_with_anthropic(text, detected_categories, sentiment_context)
            elif best_service == "jais":
                return await self._analyze_with_jais(text, detected_categories, sentiment_context)
            else:
                return await self._analyze_with_openai(text, detected_categories, sentiment_context)
                
        except Exception as e:
            logger.error(f"Topic analysis failed with {best_service}: {e}")
            return self._fallback_topic_analysis(text, detected_categories)
    
    def _detect_topic_categories(self, text: str) -> Dict[str, List[str]]:
        """Pre-detect topic categories using keyword matching"""
        detected = {}
        
        for category, keywords in self.topic_categories.items():
            matches = [keyword for keyword in keywords if keyword in text]
            if matches:
                detected[category] = matches
        
        return detected
    
    def _select_topic_model(self, text_characteristics: Dict, detected_categories: Dict) -> str:
        """Select best model for topic analysis"""
        
        # Anthropic for complex business categorization
        if len(detected_categories) > 3 or text_characteristics.get('complexity_analysis', {}).get('sentence_complexity', 0) > 5:
            return "anthropic"
        
        # JAIS for Arabic business context
        if text_characteristics.get('is_primarily_arabic', False):
            return "jais"
        
        # OpenAI for standard categorization
        return "openai"
    
    async def _analyze_with_anthropic(self, text: str, detected_categories: Dict, sentiment_context: Dict) -> Dict[str, Any]:
        """Anthropic topic analysis for complex business intelligence"""
        client = self.api_manager.get_anthropic_client()
        
        category_hint = f"Pre-detected categories: {list(detected_categories.keys())}" if detected_categories else ""
        
        prompt = f"""
        Analyze this Arabic business text for topics and themes with deep business intelligence. {category_hint}
        
        Text: {text}
        
        Respond with JSON only:
        {{
            "primary_topics": ["topic1", "topic2"],
            "business_categories": {{
                "customer_service": 0.0,
                "product_quality": 0.0,
                "pricing": 0.0,
                "delivery": 0.0,
                "technical_support": 0.0,
                "billing": 0.0,
                "user_experience": 0.0
            }},
            "topic_sentiment_mapping": {{
                "topic1": "positive/negative/neutral",
                "topic2": "positive/negative/neutral"
            }},
            "business_priority": "high/medium/low",
            "urgency_indicators": ["indicator1", "indicator2"],
            "service": "anthropic",
            "analysis_method": "business_intelligence_topics"
        }}
        """
        
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        return json.loads(response.content[0].text)
    
    async def _analyze_with_jais(self, text: str, detected_categories: Dict, sentiment_context: Dict) -> Dict[str, Any]:
        """JAIS topic analysis with Arabic business context"""
        client = self.api_manager.get_jais_client()
        
        prompt = f"""
        حلل هذا النص التجاري العربي واستخرج المواضيع والفئات:
        
        النص: {text}
        
        أجب بصيغة JSON فقط:
        {{
            "primary_topics": ["موضوع1", "موضوع2"],
            "business_categories": {{
                "customer_service": 0.0,
                "product_quality": 0.0,
                "pricing": 0.0,
                "delivery": 0.0,
                "technical_support": 0.0,
                "billing": 0.0,
                "user_experience": 0.0
            }},
            "topic_sentiment_mapping": {{
                "موضوع1": "إيجابي/سلبي/محايد",
                "موضوع2": "إيجابي/سلبي/محايد"
            }},
            "business_priority": "عالي/متوسط/منخفض",
            "urgency_indicators": ["مؤشر1", "مؤشر2"],
            "service": "jais",
            "analysis_method": "arabic_business_topics"
        }}
        """
        
        response = client.chat.completions.create(
            model="jais-30b-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.3
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def _analyze_with_openai(self, text: str, detected_categories: Dict, sentiment_context: Dict) -> Dict[str, Any]:
        """OpenAI topic analysis for fast categorization"""
        client = self.api_manager.get_openai_client()
        
        prompt = f"""
        Analyze this Arabic business text for topics and business categories efficiently.
        
        Text: {text}
        
        Respond with JSON format:
        {{
            "primary_topics": ["topic1", "topic2"],
            "business_categories": {{
                "customer_service": 0.0,
                "product_quality": 0.0,
                "pricing": 0.0,
                "delivery": 0.0,
                "technical_support": 0.0,
                "billing": 0.0,
                "user_experience": 0.0
            }},
            "topic_sentiment_mapping": {{
                "topic1": "positive/negative/neutral",
                "topic2": "positive/negative/neutral"
            }},
            "business_priority": "high/medium/low",
            "urgency_indicators": ["indicator1", "indicator2"],
            "service": "openai",
            "analysis_method": "fast_topic_categorization"
        }}
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=500,
            temperature=0.3
        )
        
        return json.loads(response.choices[0].message.content)
    
    def _fallback_topic_analysis(self, text: str, detected_categories: Dict) -> Dict[str, Any]:
        """Fallback topic analysis using keyword matching"""
        
        # Use detected categories to assign scores
        business_categories = {
            "customer_service": 0.8 if 'customer_service' in detected_categories else 0.0,
            "product_quality": 0.8 if 'product_quality' in detected_categories else 0.0,
            "pricing": 0.8 if 'pricing' in detected_categories else 0.0,
            "delivery": 0.8 if 'delivery' in detected_categories else 0.0,
            "technical_support": 0.8 if 'technical_support' in detected_categories else 0.0,
            "billing": 0.8 if 'billing' in detected_categories else 0.0,
            "user_experience": 0.5  # Default moderate score
        }
        
        primary_topics = list(detected_categories.keys())[:3] if detected_categories else ["general_feedback"]
        
        return {
            "primary_topics": primary_topics,
            "business_categories": business_categories,
            "topic_sentiment_mapping": {topic: "neutral" for topic in primary_topics},
            "business_priority": "medium",
            "urgency_indicators": [],
            "service": "fallback",
            "analysis_method": "keyword_based_topics"
        }


class RecommendationAgent(BaseAgent):
    """Dedicated agent for generating actionable business recommendations"""
    
    def __init__(self, api_manager):
        super().__init__("RecommendationSpecialist")
        self.api_manager = api_manager
        
        # Recommendation templates by business scenario
        self.recommendation_templates = {
            'negative_customer_service': [
                "تدريب إضافي لفريق خدمة العملاء",
                "مراجعة عمليات التعامل مع العملاء",
                "تحسين أوقات الاستجابة"
            ],
            'product_quality_issues': [
                "مراجعة معايير ضمان الجودة",
                "تحسين عمليات التصنيع",
                "زيادة فحص المنتجات"
            ],
            'positive_feedback': [
                "مشاركة التجربة الإيجابية مع الفريق",
                "توثيق أفضل الممارسات",
                "طلب مراجعة من العميل"
            ]
        }
    
    async def generate_recommendations(self, 
                                    text: str, 
                                    sentiment_analysis: Dict, 
                                    topic_analysis: Dict,
                                    text_characteristics: Dict) -> Dict[str, Any]:
        """Generate contextual business recommendations"""
        
        # Determine recommendation strategy
        recommendation_context = self._analyze_recommendation_context(
            sentiment_analysis, topic_analysis, text_characteristics
        )
        
        # Choose model for recommendation generation
        best_service = self._select_recommendation_model(recommendation_context)
        
        try:
            if best_service == "anthropic":
                return await self._generate_with_anthropic(text, sentiment_analysis, topic_analysis, recommendation_context)
            elif best_service == "jais":
                return await self._generate_with_jais(text, sentiment_analysis, topic_analysis, recommendation_context)
            else:
                return await self._generate_with_openai(text, sentiment_analysis, topic_analysis, recommendation_context)
                
        except Exception as e:
            logger.error(f"Recommendation generation failed with {best_service}: {e}")
            return self._fallback_recommendations(sentiment_analysis, topic_analysis)
    
    def _analyze_recommendation_context(self, sentiment_analysis: Dict, topic_analysis: Dict, text_characteristics: Dict) -> Dict[str, Any]:
        """Analyze context to determine recommendation strategy"""
        
        sentiment_score = sentiment_analysis.get('sentiment', {}).get('score', 0)
        primary_topics = topic_analysis.get('primary_topics', [])
        business_priority = topic_analysis.get('business_priority', 'medium')
        
        # Determine urgency
        urgency = 'high' if sentiment_score < -0.5 and business_priority == 'high' else \
                 'medium' if sentiment_score < 0 or business_priority == 'high' else 'low'
        
        # Determine recommendation type
        if sentiment_score > 0.3:
            rec_type = 'positive_reinforcement'
        elif sentiment_score < -0.3:
            rec_type = 'issue_resolution'
        else:
            rec_type = 'improvement_opportunity'
        
        return {
            'urgency_level': urgency,
            'recommendation_type': rec_type,
            'primary_focus_areas': primary_topics[:2],
            'sentiment_context': sentiment_analysis.get('sentiment', {}),
            'business_context': topic_analysis.get('business_categories', {}),
            'cultural_considerations': sentiment_analysis.get('cultural_sentiment', {})
        }
    
    def _select_recommendation_model(self, context: Dict) -> str:
        """Select best model for recommendation generation"""
        
        # Anthropic for complex, strategic recommendations
        if context.get('urgency_level') == 'high' or context.get('recommendation_type') == 'issue_resolution':
            return "anthropic"
        
        # JAIS for culturally appropriate Arabic recommendations
        if context.get('cultural_considerations', {}).get('religious_tone') == 'present':
            return "jais"
        
        # OpenAI for standard business recommendations
        return "openai"
    
    async def _generate_with_anthropic(self, text: str, sentiment: Dict, topics: Dict, context: Dict) -> Dict[str, Any]:
        """Anthropic recommendation generation for complex scenarios"""
        client = self.api_manager.get_anthropic_client()
        
        context_note = f"Urgency: {context.get('urgency_level')}, Type: {context.get('recommendation_type')}"
        
        prompt = f"""
        Generate strategic business recommendations for this Arabic customer feedback. {context_note}
        
        Original text: {text}
        Sentiment: {sentiment.get('sentiment', {}).get('label')} (score: {sentiment.get('sentiment', {}).get('score')})
        Key topics: {', '.join(topics.get('primary_topics', []))}
        
        Respond with JSON only:
        {{
            "immediate_actions": ["action1", "action2"],
            "strategic_recommendations": ["strategy1", "strategy2"],
            "follow_up_actions": ["followup1", "followup2"],
            "priority_level": "high/medium/low",
            "timeline": {{
                "immediate": "24-48 hours",
                "short_term": "1-2 weeks", 
                "long_term": "1-3 months"
            }},
            "success_metrics": ["metric1", "metric2"],
            "cultural_considerations": ["consideration1", "consideration2"],
            "service": "anthropic",
            "recommendation_confidence": 0.0
        }}
        """
        
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        
        return json.loads(response.content[0].text)
    
    async def _generate_with_jais(self, text: str, sentiment: Dict, topics: Dict, context: Dict) -> Dict[str, Any]:
        """JAIS recommendation generation with Arabic cultural context"""
        client = self.api_manager.get_jais_client()
        
        prompt = f"""
        اقترح توصيات عملية لهذه التغذية الراجعة من العميل مع مراعاة السياق الثقافي العربي:
        
        النص: {text}
        المشاعر: {sentiment.get('sentiment', {}).get('label')}
        المواضيع: {', '.join(topics.get('primary_topics', []))}
        
        أجب بصيغة JSON فقط:
        {{
            "immediate_actions": ["إجراء1", "إجراء2"],
            "strategic_recommendations": ["استراتيجية1", "استراتيجية2"],
            "follow_up_actions": ["متابعة1", "متابعة2"],
            "priority_level": "عالي/متوسط/منخفض",
            "timeline": {{
                "immediate": "24-48 ساعة",
                "short_term": "1-2 أسبوع",
                "long_term": "1-3 أشهر"
            }},
            "success_metrics": ["مقياس1", "مقياس2"],
            "cultural_considerations": ["اعتبار1", "اعتبار2"],
            "service": "jais",
            "recommendation_confidence": 0.0
        }}
        """
        
        response = client.chat.completions.create(
            model="jais-30b-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.4
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def _generate_with_openai(self, text: str, sentiment: Dict, topics: Dict, context: Dict) -> Dict[str, Any]:
        """OpenAI recommendation generation for standard scenarios"""
        client = self.api_manager.get_openai_client()
        
        prompt = f"""
        Generate practical business recommendations for this Arabic customer feedback.
        
        Text: {text}
        Sentiment: {sentiment.get('sentiment', {}).get('label')} (score: {sentiment.get('sentiment', {}).get('score')})
        Topics: {', '.join(topics.get('primary_topics', []))}
        
        Respond with JSON format:
        {{
            "immediate_actions": ["action1", "action2"],
            "strategic_recommendations": ["strategy1", "strategy2"],
            "follow_up_actions": ["followup1", "followup2"],
            "priority_level": "high/medium/low",
            "timeline": {{
                "immediate": "24-48 hours",
                "short_term": "1-2 weeks",
                "long_term": "1-3 months"
            }},
            "success_metrics": ["metric1", "metric2"],
            "cultural_considerations": ["consideration1", "consideration2"],
            "service": "openai",
            "recommendation_confidence": 0.0
        }}
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=700,
            temperature=0.4
        )
        
        return json.loads(response.choices[0].message.content)
    
    def _fallback_recommendations(self, sentiment: Dict, topics: Dict) -> Dict[str, Any]:
        """Generate fallback recommendations using templates"""
        
        sentiment_score = sentiment.get('sentiment', {}).get('score', 0)
        primary_topics = topics.get('primary_topics', [])
        
        # Choose template based on sentiment and topics
        if sentiment_score < -0.3 and 'customer_service' in primary_topics:
            actions = self.recommendation_templates['negative_customer_service']
        elif sentiment_score < -0.3 and 'product_quality' in primary_topics:
            actions = self.recommendation_templates['product_quality_issues']
        elif sentiment_score > 0.3:
            actions = self.recommendation_templates['positive_feedback']
        else:
            actions = ["مراجعة التغذية الراجعة مع الفريق المختص", "متابعة مع العميل للتوضيح"]
        
        return {
            "immediate_actions": actions[:2],
            "strategic_recommendations": ["تحليل أعمق للتغذية الراجعة", "وضع خطة تحسين"],
            "follow_up_actions": ["متابعة مع العميل خلال أسبوع"],
            "priority_level": "high" if sentiment_score < -0.5 else "medium",
            "timeline": {
                "immediate": "24-48 hours",
                "short_term": "1-2 weeks",
                "long_term": "1-3 months"
            },
            "success_metrics": ["رضا العميل", "تحسين الخدمة"],
            "cultural_considerations": ["مراعاة الأدب العربي في التواصل"],
            "service": "fallback",
            "recommendation_confidence": 0.6
        }