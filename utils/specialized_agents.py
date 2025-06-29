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
        
        primary_dialect = max(scores.keys(), key=lambda k: scores[k])
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
    """Enhanced agent for hierarchical topic detection with uncertainty quantification"""
    
    def __init__(self, api_manager):
        super().__init__("TopicalAnalyst")
        self.api_manager = api_manager
        self.setup_prompts()
        self.setup_few_shot_examples()
        self.category_hierarchy = self._load_category_hierarchy()
        
        # Emerging topic detection patterns
        self.emerging_patterns = {
            'new_technology': ['ذكي', 'تطبيق', 'رقمي', 'تقنية جديدة', 'ابتكار'],
            'sustainability': ['بيئة', 'استدامة', 'أخضر', 'طبيعي', 'صديق البيئة'],
            'remote_services': ['عن بعد', 'أونلاين', 'إلكتروني', 'رقمي', 'افتراضي'],
            'health_safety': ['صحة', 'أمان', 'سلامة', 'تعقيم', 'احتياطات']
        }
    
    def _load_category_hierarchy(self):
        """Hierarchical categories for sophisticated topic detection"""
        return {
            "customer_service": {
                "subcategories": {
                    "response_time": ["سرعة الرد", "وقت الاستجابة", "تأخير", "بطء"],
                    "staff_behavior": ["تعامل", "أدب", "احترام", "لطف", "مساعدة"],
                    "problem_resolution": ["حل المشكلة", "متابعة", "إنجاز", "نتيجة"],
                    "communication": ["توضيح", "شرح", "فهم", "تواصل", "إعلام"]
                },
                "keywords": ["خدمة العملاء", "موظف", "تعامل", "اهتمام", "رد", "دعم"],
                "weight": 1.0
            },
            "product_quality": {
                "subcategories": {
                    "durability": ["متانة", "قوة", "تحمل", "عمر افتراضي"],
                    "features": ["مميزات", "خصائص", "وظائف", "إمكانيات"],
                    "defects": ["عيب", "خلل", "مشكلة", "كسر", "تلف"],
                    "design": ["تصميم", "شكل", "مظهر", "جمال", "أناقة"]
                },
                "keywords": ["جودة", "منتج", "سلعة", "مواصفات", "عيب", "نوعية"],
                "weight": 1.0
            },
            "pricing": {
                "subcategories": {
                    "cost_effectiveness": ["قيمة مقابل المال", "يستحق", "مناسب", "معقول"],
                    "competitive_pricing": ["مقارنة", "منافس", "أرخص", "أغلى"],
                    "hidden_fees": ["رسوم مخفية", "إضافية", "مفاجئة", "غير متوقعة"],
                    "discounts": ["خصم", "تخفيض", "عرض", "تخفيضات"]
                },
                "keywords": ["سعر", "تكلفة", "مبلغ", "رسوم", "مصاريف", "فلوس"],
                "weight": 0.9
            },
            "delivery": {
                "subcategories": {
                    "speed": ["سرعة", "سريع", "بطيء", "وقت التوصيل"],
                    "accuracy": ["دقة", "صحيح", "خطأ", "مكان التسليم"],
                    "packaging": ["تغليف", "حماية", "تالف", "سليم"],
                    "tracking": ["تتبع", "معرفة", "موقع", "حالة الطلب"]
                },
                "keywords": ["توصيل", "شحن", "وقت", "تأخير", "سرعة", "وصول"],
                "weight": 0.8
            },
            "technical_support": {
                "subcategories": {
                    "expertise": ["خبرة", "معرفة", "فهم", "تخصص"],
                    "availability": ["متاح", "موجود", "ساعات العمل", "وقت"],
                    "tools": ["أدوات", "برامج", "تقنية", "نظام"],
                    "documentation": ["شرح", "دليل", "تعليمات", "وثائق"]
                },
                "keywords": ["دعم فني", "مساعدة", "حل", "مشكلة تقنية", "تقني"],
                "weight": 0.9
            },
            "billing": {
                "subcategories": {
                    "accuracy": ["دقة", "صحيح", "خطأ", "حساب"],
                    "transparency": ["وضوح", "شفافية", "مفهوم", "واضح"],
                    "payment_methods": ["طريقة الدفع", "بطاقة", "نقد", "تحويل"],
                    "invoicing": ["فاتورة", "إيصال", "كشف", "بيان"]
                },
                "keywords": ["فاتورة", "دفع", "حساب", "رسوم", "مالي"],
                "weight": 0.7
            },
            "user_experience": {
                "subcategories": {
                    "ease_of_use": ["سهولة", "بساطة", "مريح", "معقد"],
                    "navigation": ["تنقل", "قائمة", "بحث", "وصول"],
                    "performance": ["أداء", "سرعة", "بطء", "تعليق"],
                    "accessibility": ["إتاحة", "وصول", "متاح", "صعوبة"]
                },
                "keywords": ["تجربة", "استخدام", "سهولة", "صعوبة", "واجهة"],
                "weight": 0.8
            }
        }
    
    def setup_prompts(self):
        """Setup advanced prompting strategies for topic analysis"""
        self.prompts = {
            "jais": {
                PromptStrategy.DIRECT: """
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
                """,
                
                PromptStrategy.CHAIN_OF_THOUGHT: """
                أنت محلل أعمال متخصص. حلل هذا النص خطوة بخطوة:

                النص: {text}

                الخطوة ١: تحديد الكلمات المفتاحية
                - اذكر الكلمات المفتاحية المتعلقة بالأعمال
                - حدد المصطلحات التقنية

                الخطوة ٢: تصنيف المواضيع الرئيسية
                - ما هي المجالات التجارية المذكورة؟
                - أي قسم من الشركة متأثر؟

                الخطوة ٣: تقييم الأولوية التجارية
                - ما مدى إلحاح هذا الموضوع؟
                - كيف يؤثر على العمليات؟

                الخطوة ٤: التصنيف النهائي
                {{
                    "reasoning": "تفسير التحليل",
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
                    "hierarchical_analysis": {{
                        "main_category": "الفئة الرئيسية",
                        "subcategories": ["فئة فرعية1", "فئة فرعية2"]
                    }},
                    "service": "jais",
                    "analysis_method": "chain_of_thought_business"
                }}
                """,
                
                PromptStrategy.FEW_SHOT: """
                حلل المواضيع التجارية في هذا النص مستعيناً بهذه الأمثلة:

                {examples}

                النص المطلوب تحليله: {text}

                استخدم نفس صيغة JSON:
                {{
                    "primary_topics": ["موضوع1", "موضوع2"],
                    "business_categories": {{...}},
                    "confidence_scores": {{...}},
                    "service": "jais",
                    "analysis_method": "few_shot_business_arabic"
                }}
                """
            },
            
            "anthropic": {
                PromptStrategy.DIRECT: """
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
                """,
                
                PromptStrategy.CHAIN_OF_THOUGHT: """
                You are a business intelligence analyst. Analyze this Arabic text systematically:

                Text: {text}

                Step 1: Keyword Extraction
                - Identify business-relevant keywords
                - Note industry-specific terms

                Step 2: Topic Categorization
                - Which business domains are mentioned?
                - What departments are affected?

                Step 3: Hierarchical Classification
                - Map topics to main categories and subcategories
                - Assess topic relationships

                Step 4: Business Impact Assessment
                - Evaluate urgency and priority
                - Consider operational implications

                Step 5: Final Analysis
                {{
                    "reasoning": "Step-by-step analysis explanation",
                    "primary_topics": ["topic1", "topic2"],
                    "business_categories": {{...}},
                    "hierarchical_structure": {{
                        "main_category": "category",
                        "subcategories": ["sub1", "sub2"],
                        "confidence_levels": {{...}}
                    }},
                    "emerging_patterns": ["pattern1", "pattern2"],
                    "service": "anthropic",
                    "analysis_method": "hierarchical_business_intelligence"
                }}
                """
            },
            
            "openai": {
                PromptStrategy.DIRECT: """
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
            }
        }
    
    def setup_few_shot_examples(self):
        """Setup business topic examples for few-shot learning"""
        self.few_shot_examples = {
            "customer_service": [
                {
                    "text": "الموظف كان مفيد جداً وحل مشكلتي بسرعة",
                    "analysis": {
                        "primary_topics": ["staff_behavior", "problem_resolution"],
                        "business_categories": {"customer_service": 0.9, "user_experience": 0.3},
                        "confidence_scores": {"staff_behavior": 0.95, "problem_resolution": 0.85}
                    }
                }
            ],
            "product_quality": [
                {
                    "text": "المنتج وصل مكسور والجودة سيئة",
                    "analysis": {
                        "primary_topics": ["defects", "durability"],
                        "business_categories": {"product_quality": 0.95, "delivery": 0.4},
                        "confidence_scores": {"defects": 0.9, "durability": 0.8}
                    }
                }
            ],
            "pricing": [
                {
                    "text": "السعر غالي مقارنة بالمنافسين",
                    "analysis": {
                        "primary_topics": ["competitive_pricing", "cost_effectiveness"],
                        "business_categories": {"pricing": 0.9},
                        "confidence_scores": {"competitive_pricing": 0.85}
                    }
                }
            ]
        }
    
    async def analyze_topics(self, text: str, text_characteristics: Dict, sentiment_context: Dict) -> Dict[str, Any]:
        """Enhanced topic analysis with uncertainty quantification"""
        
        # Use uncertainty quantification for better confidence scoring
        return await self.analyze_with_uncertainty(text, {
            'text_characteristics': text_characteristics,
            'sentiment_context': sentiment_context
        })
    
    async def analyze_with_uncertainty(self, text: str, context: Dict) -> Dict[str, Any]:
        """Enhanced analysis with uncertainty quantification"""
        
        # First pass: Extract initial topics using keyword detection
        initial_topics = self._extract_topics(text)
        
        # Second pass: Validate with AI-powered analysis
        strategy = self.select_prompt_strategy(text, context)
        ai_service = self._select_topic_model(context.get('text_characteristics', {}), {})
        
        try:
            validation_analysis = await self._analyze_with_strategy(text, strategy, ai_service, context)
            validation_topics = validation_analysis.get('primary_topics', [])
        except Exception as e:
            logger.warning(f"AI validation failed: {e}")
            validation_topics = initial_topics
        
        # Calculate confidence based on agreement between methods
        confidence_scores = self._calculate_topic_confidence(initial_topics, validation_topics)
        
        # Detect emerging topics and hierarchical structure
        emerging_topics = self._detect_emerging_topics(text)
        hierarchical_categories = self._map_to_hierarchy(initial_topics + validation_topics)
        
        return {
            "primary_topics": list(set(initial_topics + validation_topics))[:3],
            "confidence_scores": confidence_scores,
            "emerging_topics": emerging_topics,
            "hierarchical_categories": hierarchical_categories,
            "business_categories": self._calculate_business_category_scores(initial_topics + validation_topics),
            "validation_agreement": len(set(initial_topics) & set(validation_topics)) / max(len(initial_topics), 1),
            "uncertainty_analysis": {
                "high_confidence": [topic for topic, conf in confidence_scores.items() if conf > 0.8],
                "medium_confidence": [topic for topic, conf in confidence_scores.items() if 0.5 < conf <= 0.8],
                "low_confidence": [topic for topic, conf in confidence_scores.items() if conf <= 0.5]
            },
            "enhanced_analysis": True,
            "analysis_method": f"uncertainty_quantification_{strategy.value}"
        }
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics using hierarchical keyword matching"""
        detected_topics = []
        
        for category, details in self.category_hierarchy.items():
            # Check main category keywords
            main_keywords = details.get('keywords', [])
            if any(keyword in text for keyword in main_keywords):
                detected_topics.append(category)
                
                # Check subcategory keywords for more specific topics
                for subcat, sub_keywords in details.get('subcategories', {}).items():
                    if any(keyword in text for keyword in sub_keywords):
                        detected_topics.append(f"{category}_{subcat}")
        
        return detected_topics
    
    def _calculate_topic_confidence(self, initial_topics: List[str], validation_topics: List[str]) -> Dict[str, float]:
        """Calculate confidence scores based on method agreement"""
        confidence_scores = {}
        all_topics = set(initial_topics + validation_topics)
        
        for topic in all_topics:
            in_initial = topic in initial_topics
            in_validation = topic in validation_topics
            
            if in_initial and in_validation:
                confidence_scores[topic] = 0.9  # High confidence - both methods agree
            elif in_initial or in_validation:
                confidence_scores[topic] = 0.6  # Medium confidence - one method detected
            else:
                confidence_scores[topic] = 0.3  # Low confidence - edge case
        
        return confidence_scores
    
    def _detect_emerging_topics(self, text: str) -> List[str]:
        """Detect emerging business trends and topics"""
        emerging_topics = []
        
        for pattern_name, keywords in self.emerging_patterns.items():
            if any(keyword in text for keyword in keywords):
                emerging_topics.append(pattern_name)
        
        # Additional dynamic pattern detection
        modern_indicators = ['رقمنة', 'ذكاء اصطناعي', 'بلوك تشين', 'العملة الرقمية']
        if any(indicator in text for indicator in modern_indicators):
            emerging_topics.append('digital_transformation')
            
        return emerging_topics
    
    def _map_to_hierarchy(self, topics: List[str]) -> Dict[str, Any]:
        """Map detected topics to hierarchical structure"""
        hierarchical_structure = {}
        
        for topic in topics:
            # Handle subcategory topics (format: category_subcategory)
            if '_' in topic:
                main_category, subcategory = topic.split('_', 1)
                if main_category in self.category_hierarchy:
                    if main_category not in hierarchical_structure:
                        hierarchical_structure[main_category] = {
                            'subcategories': [],
                            'weight': self.category_hierarchy[main_category].get('weight', 1.0)
                        }
                    hierarchical_structure[main_category]['subcategories'].append(subcategory)
            else:
                # Main category topic
                if topic in self.category_hierarchy:
                    if topic not in hierarchical_structure:
                        hierarchical_structure[topic] = {
                            'subcategories': [],
                            'weight': self.category_hierarchy[topic].get('weight', 1.0)
                        }
        
        return hierarchical_structure
    
    def _calculate_business_category_scores(self, topics: List[str]) -> Dict[str, float]:
        """Calculate weighted scores for business categories"""
        category_scores = {
            "customer_service": 0.0,
            "product_quality": 0.0,
            "pricing": 0.0,
            "delivery": 0.0,
            "technical_support": 0.0,
            "billing": 0.0,
            "user_experience": 0.0
        }
        
        for topic in topics:
            # Extract main category from subcategory topics
            main_topic = topic.split('_')[0] if '_' in topic else topic
            
            if main_topic in category_scores:
                # Apply weight from hierarchy
                weight = self.category_hierarchy.get(main_topic, {}).get('weight', 1.0)
                category_scores[main_topic] = min(1.0, category_scores[main_topic] + (0.3 * weight))
        
        return category_scores
    
    async def _analyze_with_strategy(self, text: str, strategy: PromptStrategy, service: str, context: Dict) -> Dict[str, Any]:
        """Execute topic analysis using selected strategy and AI service"""
        
        # Get appropriate prompt template
        prompt_template = self.prompts[service][strategy]
        
        # Prepare context for prompt formatting
        prompt_context = {
            'category_hint': self._format_category_hint(context)
        }
        
        # Add few-shot examples if using that strategy
        if strategy == PromptStrategy.FEW_SHOT:
            primary_category = self._identify_primary_category(text)
            examples = self._format_business_examples(primary_category, service)
            prompt_context['examples'] = examples
        
        # Format prompt
        prompt = prompt_template.format(text=text, **prompt_context)
        
        # Call appropriate AI service
        if service == "jais":
            return await self._call_jais_analysis(prompt)
        elif service == "anthropic":
            return await self._call_anthropic_analysis(prompt)
        else:
            return await self._call_openai_analysis(prompt)
    
    def _identify_primary_category(self, text: str) -> str:
        """Identify primary business category for few-shot example selection"""
        category_scores = {}
        
        for category, details in self.category_hierarchy.items():
            keywords = details.get('keywords', [])
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            return max(category_scores.keys(), key=lambda k: category_scores[k])
        return "customer_service"  # Default fallback
    
    def _format_business_examples(self, category: str, service: str) -> str:
        """Format business examples for the detected category"""
        examples = self.few_shot_examples.get(category, self.few_shot_examples['customer_service'])
        
        if service == "jais":
            # Arabic format for JAIS
            formatted = []
            for example in examples:
                formatted.append(f"""
مثال:
النص: {example['text']}
التحليل: {json.dumps(example['analysis'], ensure_ascii=False, indent=2)}
""")
            return "\n".join(formatted)
        else:
            # English format for Anthropic/OpenAI
            formatted = []
            for example in examples:
                formatted.append(f"""
Example:
Text: {example['text']}
Analysis: {json.dumps(example['analysis'], ensure_ascii=False, indent=2)}
""")
            return "\n".join(formatted)
    
    def _format_category_hint(self, context: Dict) -> str:
        """Format category hint based on detected patterns"""
        text_chars = context.get('text_characteristics', {})
        if text_chars.get('is_primarily_arabic', False):
            return "This text contains Arabic business terminology."
        return ""
    
    async def _call_jais_analysis(self, prompt: str) -> Dict[str, Any]:
        """Call JAIS for topic analysis"""
        client = self.api_manager.get_jais_client()
        
        response = client.chat.completions.create(
            model="jais-30b-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=700,
            temperature=0.3
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def _call_anthropic_analysis(self, prompt: str) -> Dict[str, Any]:
        """Call Anthropic for topic analysis"""
        client = self.api_manager.get_anthropic_client()
        
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=700,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        return json.loads(response.content[0].text)
    
    async def _call_openai_analysis(self, prompt: str) -> Dict[str, Any]:
        """Call OpenAI for topic analysis"""
        client = self.api_manager.get_openai_client()
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=600,
            temperature=0.3
        )
        
        return json.loads(response.choices[0].message.content)
    
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
                                    combined_analysis: Dict, 
                                    context: Dict = None) -> Dict[str, Any]:
        """Generate contextual business recommendations based on consensus analysis"""
        
        if context is None:
            context = {}
            
        # Extract sentiment and topic data from combined analysis
        sentiment_analysis = combined_analysis.get("sentiment", {})
        topic_analysis = combined_analysis.get("topics", {})
        
        # Determine recommendation strategy
        recommendation_context = self._analyze_recommendation_context(
            sentiment_analysis, topic_analysis, context
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
    
    def _analyze_recommendation_context(self, sentiment_analysis: Dict, topic_analysis: Dict, context: Dict) -> Dict[str, Any]:
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