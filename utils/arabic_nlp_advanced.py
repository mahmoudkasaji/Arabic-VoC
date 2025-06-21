"""
Advanced Arabic NLP processing for analytics dashboard
Topic modeling, emotion detection, entity recognition with cultural context
"""

import logging
import re
from typing import Dict, List, Any, Tuple
from collections import Counter, defaultdict
import asyncio
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AdvancedArabicNLP:
    """Advanced NLP processing for Arabic content with cultural awareness"""
    
    def __init__(self):
        self.setup_linguistic_resources()
        self.setup_cultural_patterns()
        self.setup_entity_patterns()
    
    def setup_linguistic_resources(self):
        """Initialize linguistic resources for Arabic processing"""
        
        # Arabic root patterns for morphological analysis
        self.arabic_roots = {
            "كتب": ["كتاب", "مكتبة", "كاتب", "مكتوب"],
            "قرأ": ["قراءة", "قارئ", "مقروء"],
            "درس": ["دراسة", "مدرسة", "دارس"],
            "عمل": ["عامل", "معمل", "عمال"],
            "خدم": ["خدمة", "خادم", "مخدوم"]
        }
        
        # Semantic clusters for topic modeling
        self.semantic_clusters = {
            "technology": [
                "تطبيق", "موقع", "نظام", "برنامج", "تقنية", "رقمي",
                "انترنت", "هاتف", "كمبيوتر", "شاشة", "واجهة"
            ],
            "service": [
                "خدمة", "دعم", "مساعدة", "استجابة", "تعامل", "موظف",
                "فريق", "استقبال", "رد", "حل"
            ],
            "quality": [
                "جودة", "نوعية", "مستوى", "معيار", "تميز", "إتقان",
                "احتراف", "كفاءة", "دقة", "عناية"
            ],
            "product": [
                "منتج", "سلعة", "بضاعة", "مادة", "عنصر", "قطعة",
                "طلبية", "شحنة", "تسليم", "عبوة"
            ],
            "experience": [
                "تجربة", "انطباع", "شعور", "احساس", "رأي", "وجهة",
                "نظر", "تقييم", "مراجعة", "ملاحظة"
            ],
            "time": [
                "وقت", "زمن", "مدة", "فترة", "سرعة", "بطء",
                "تأخير", "عجلة", "استعجال", "انتظار"
            ]
        }
        
        # Advanced emotion lexicon
        self.emotion_lexicon = {
            "joy": {
                "primary": ["فرح", "سعادة", "بهجة", "سرور", "حبور"],
                "secondary": ["مبسوط", "فرحان", "مسرور", "مبتهج", "راض"],
                "expressions": ["الحمد لله", "ما شاء الله", "بارك الله"]
            },
            "anger": {
                "primary": ["غضب", "زعل", "انزعاج", "استياء", "سخط"],
                "secondary": ["مضايق", "متضايق", "منرفز", "مستاء", "ساخط"],
                "expressions": ["لا يعقل", "غير مقبول", "محبط"]
            },
            "sadness": {
                "primary": ["حزن", "أسى", "كآبة", "يأس", "إحباط"],
                "secondary": ["حزين", "مكتئب", "محبط", "يائس", "متألم"],
                "expressions": ["للأسف", "يا حسرة", "وا أسفاه"]
            },
            "fear": {
                "primary": ["خوف", "قلق", "هلع", "ذعر", "رعب"],
                "secondary": ["خائف", "قلق", "مذعور", "متوتر", "مرتبك"],
                "expressions": ["لا قدر الله", "نعوذ بالله", "خايف"]
            },
            "surprise": {
                "primary": ["دهشة", "استغراب", "تعجب", "ذهول", "انبهار"],
                "secondary": ["مدهوش", "مستغرب", "متعجب", "مذهول", "منبهر"],
                "expressions": ["يا سلام", "لا يصدق", "عجيب"]
            },
            "disgust": {
                "primary": ["اشمئزاز", "قرف", "نفور", "كراهية", "استهجان"],
                "secondary": ["مقرف", "منفر", "مكروه", "بشع", "سيء"],
                "expressions": ["يا عيب الشوم", "قرف", "مقزز"]
            },
            "gratitude": {
                "primary": ["شكر", "امتنان", "تقدير", "عرفان", "حمد"],
                "secondary": ["شاكر", "ممتن", "مقدر", "حامد", "معترف"],
                "expressions": ["جزاك الله خير", "بارك الله فيك", "شكرا جزيلا"]
            },
            "satisfaction": {
                "primary": ["رضا", "قناعة", "ارتياح", "اطمئنان", "استحسان"],
                "secondary": ["راضي", "مقتنع", "مرتاح", "مطمئن", "مستحسن"],
                "expressions": ["الحمد لله", "راضي تماما", "كله تمام"]
            }
        }
    
    def setup_cultural_patterns(self):
        """Setup cultural context patterns for MENA region"""
        
        self.cultural_contexts = {
            "hospitality": {
                "patterns": ["ضيافة", "كرم", "ترحيب", "استقبال", "حفاوة"],
                "importance": 0.9,
                "regions": ["gulf", "levant", "egypt", "maghreb"]
            },
            "respect": {
                "patterns": ["احترام", "تقدير", "وقار", "أدب", "لياقة"],
                "importance": 0.8,
                "regions": ["all"]
            },
            "family": {
                "patterns": ["عائلة", "أسرة", "أهل", "عيال", "ذرية"],
                "importance": 0.9,
                "regions": ["all"]
            },
            "religion": {
                "patterns": ["الله", "إن شاء الله", "بإذن الله", "الحمد لله", "ما شاء الله"],
                "importance": 0.8,
                "regions": ["all"]
            },
            "time_concepts": {
                "patterns": ["وقت", "صبر", "عجلة", "بكرا", "إن شاء الله"],
                "importance": 0.7,
                "regions": ["all"]
            },
            "social_hierarchy": {
                "patterns": ["أستاذ", "دكتور", "حضرتك", "سيادتك", "معالي"],
                "importance": 0.8,
                "regions": ["egypt", "levant"]
            }
        }
        
        # Temporal cultural events
        self.cultural_events = {
            "ramadan": {
                "keywords": ["رمضان", "الصيام", "إفطار", "سحور", "تراويح", "قيام"],
                "sentiment_modifier": 0.2,  # Generally positive context
                "season": "variable"
            },
            "eid": {
                "keywords": ["عيد", "العيد", "عيد الفطر", "عيد الأضحى", "عيدية"],
                "sentiment_modifier": 0.3,
                "season": "variable"
            },
            "weekend": {
                "keywords": ["جمعة", "سبت", "عطلة", "نهاية الأسبوع", "راحة"],
                "sentiment_modifier": 0.1,
                "season": "weekly"
            },
            "summer": {
                "keywords": ["صيف", "حر", "إجازة", "سفر", "مصيف"],
                "sentiment_modifier": 0.0,
                "season": "summer"
            }
        }
    
    def setup_entity_patterns(self):
        """Setup patterns for Arabic entity recognition"""
        
        self.entity_patterns = {
            "companies": {
                "patterns": [
                    r"شركة\s+(\w+)",
                    r"مؤسسة\s+(\w+)",
                    r"مجموعة\s+(\w+)",
                    r"بنك\s+(\w+)"
                ],
                "common_entities": ["أرامكو", "سابك", "الراجحي", "الأهلي", "زين", "موبايلي"]
            },
            "products": {
                "patterns": [
                    r"منتج\s+(\w+)",
                    r"جهاز\s+(\w+)",
                    r"برنامج\s+(\w+)",
                    r"تطبيق\s+(\w+)"
                ],
                "common_entities": ["آيفون", "سامسونج", "واتساب", "تويتر", "إنستغرام"]
            },
            "locations": {
                "patterns": [
                    r"مدينة\s+(\w+)",
                    r"في\s+(\w+)",
                    r"بـ(\w+)",
                    r"من\s+(\w+)"
                ],
                "common_entities": [
                    "الرياض", "جدة", "مكة", "المدينة", "الدمام", "الخبر",
                    "دبي", "أبوظبي", "الشارقة", "الكويت", "الدوحة", "المنامة",
                    "القاهرة", "الإسكندرية", "الجيزة", "بيروت", "دمشق", "عمان",
                    "الدار البيضاء", "الرباط", "تونس", "الجزائر", "بغداد", "البصرة"
                ]
            },
            "services": {
                "patterns": [
                    r"خدمة\s+(\w+)",
                    r"دعم\s+(\w+)",
                    r"قسم\s+(\w+)"
                ],
                "common_entities": ["العملاء", "التقني", "المبيعات", "الصيانة", "التوصيل"]
            }
        }
    
    def extract_topics_advanced(self, texts: List[str], min_frequency: int = 3) -> Dict[str, Any]:
        """Advanced topic modeling using semantic clustering"""
        
        if not texts:
            return {"topics": [], "clusters": {}, "coherence_score": 0.0}
        
        # Tokenize and clean texts
        all_words = []
        text_clusters = defaultdict(list)
        
        for text in texts:
            words = self._tokenize_arabic(text)
            all_words.extend(words)
            
            # Assign text to clusters based on semantic similarity
            for cluster_name, cluster_words in self.semantic_clusters.items():
                overlap = len(set(words) & set(cluster_words))
                if overlap > 0:
                    text_clusters[cluster_name].append(text)
        
        # Calculate word frequencies
        word_freq = Counter(all_words)
        
        # Extract prominent topics
        topics = []
        for word, freq in word_freq.most_common(20):
            if freq >= min_frequency and len(word) > 2:
                # Find which semantic cluster this word belongs to
                cluster = "general"
                for cluster_name, cluster_words in self.semantic_clusters.items():
                    if word in cluster_words:
                        cluster = cluster_name
                        break
                
                topics.append({
                    "term": word,
                    "frequency": freq,
                    "cluster": cluster,
                    "relative_frequency": freq / len(all_words)
                })
        
        # Calculate cluster coherence
        cluster_coherence = {}
        for cluster_name, cluster_texts in text_clusters.items():
            if cluster_texts:
                cluster_coherence[cluster_name] = {
                    "text_count": len(cluster_texts),
                    "coherence": len(cluster_texts) / len(texts),
                    "sample_texts": cluster_texts[:3]
                }
        
        overall_coherence = sum(c["coherence"] for c in cluster_coherence.values()) / len(cluster_coherence) if cluster_coherence else 0
        
        return {
            "topics": topics,
            "clusters": cluster_coherence,
            "coherence_score": overall_coherence,
            "total_texts": len(texts),
            "total_words": len(all_words),
            "unique_words": len(set(all_words))
        }
    
    def detect_emotions_advanced(self, text: str) -> Dict[str, Any]:
        """Advanced emotion detection with intensity and confidence"""
        
        emotions_detected = {}
        emotion_intensities = {}
        confidence_scores = {}
        
        for emotion, lexicon in self.emotion_lexicon.items():
            total_score = 0
            matches = []
            
            # Check primary emotion words (weight: 1.0)
            for word in lexicon["primary"]:
                if word in text:
                    total_score += 1.0
                    matches.append(("primary", word))
            
            # Check secondary emotion words (weight: 0.7)
            for word in lexicon["secondary"]:
                if word in text:
                    total_score += 0.7
                    matches.append(("secondary", word))
            
            # Check emotional expressions (weight: 0.8)
            for expr in lexicon["expressions"]:
                if expr in text:
                    total_score += 0.8
                    matches.append(("expression", expr))
            
            if total_score > 0:
                # Calculate intensity based on word count and repetition
                word_count = len(text.split())
                intensity = min(1.0, total_score / max(1, word_count / 10))
                
                # Calculate confidence based on match quality
                confidence = min(1.0, len(matches) / 3.0)
                
                emotions_detected[emotion] = total_score
                emotion_intensities[emotion] = intensity
                confidence_scores[emotion] = confidence
        
        # Find dominant emotion
        dominant_emotion = max(emotions_detected.items(), key=lambda x: x[1])[0] if emotions_detected else None
        
        return {
            "emotions": emotions_detected,
            "intensities": emotion_intensities,
            "confidences": confidence_scores,
            "dominant_emotion": dominant_emotion,
            "emotion_diversity": len(emotions_detected),
            "total_emotional_content": sum(emotions_detected.values())
        }
    
    def extract_entities_advanced(self, text: str) -> Dict[str, Any]:
        """Advanced Arabic entity recognition with context"""
        
        entities = {
            "companies": [],
            "products": [],
            "locations": [],
            "services": [],
            "persons": [],
            "temporal": []
        }
        
        # Extract entities using patterns
        for entity_type, config in self.entity_patterns.items():
            # Pattern-based extraction
            for pattern in config["patterns"]:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entity = match.group(1) if match.groups() else match.group(0)
                    entities[entity_type].append({
                        "text": entity,
                        "method": "pattern",
                        "confidence": 0.8
                    })
            
            # Known entity detection
            for known_entity in config["common_entities"]:
                if known_entity in text:
                    entities[entity_type].append({
                        "text": known_entity,
                        "method": "dictionary",
                        "confidence": 0.9
                    })
        
        # Temporal entity extraction
        temporal_patterns = [
            r"(اليوم|أمس|غدا|بكرا)",
            r"(صباح|مساء|ليل|ظهر)",
            r"(الأسبوع|الشهر|السنة)\s*(الماضي|القادم|المقبل)",
            r"(رمضان|عيد|جمعة|سبت)"
        ]
        
        for pattern in temporal_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities["temporal"].append({
                    "text": match.group(0),
                    "method": "pattern",
                    "confidence": 0.7
                })
        
        # Calculate entity statistics
        total_entities = sum(len(ent_list) for ent_list in entities.values())
        entity_density = total_entities / len(text.split()) if text.split() else 0
        
        return {
            "entities": entities,
            "statistics": {
                "total_entities": total_entities,
                "entity_density": entity_density,
                "entity_types_found": len([k for k, v in entities.items() if v])
            }
        }
    
    def analyze_cultural_context(self, text: str, metadata: Dict = None) -> Dict[str, Any]:
        """Analyze cultural context with regional and temporal awareness"""
        
        cultural_markers = {}
        regional_indicators = {}
        temporal_context = {}
        
        # Detect cultural patterns
        for context_name, context_config in self.cultural_contexts.items():
            matches = []
            for pattern in context_config["patterns"]:
                if pattern in text:
                    matches.append(pattern)
            
            if matches:
                cultural_markers[context_name] = {
                    "matches": matches,
                    "importance": context_config["importance"],
                    "regions": context_config["regions"],
                    "strength": len(matches) / len(context_config["patterns"])
                }
        
        # Detect temporal cultural events
        current_time = metadata.get("timestamp", datetime.utcnow()) if metadata else datetime.utcnow()
        
        for event_name, event_config in self.cultural_events.items():
            matches = []
            for keyword in event_config["keywords"]:
                if keyword in text:
                    matches.append(keyword)
            
            if matches:
                temporal_context[event_name] = {
                    "matches": matches,
                    "sentiment_modifier": event_config["sentiment_modifier"],
                    "season": event_config["season"],
                    "strength": len(matches) / len(event_config["keywords"])
                }
        
        # Analyze dialect indicators for regional context
        dialect_indicators = {
            "gulf": ["زين", "يهبل", "مشكور", "يعطيك العافية"],
            "egyptian": ["كويس", "حلو", "جميل", "عجبني", "بجد"],
            "levantine": ["منيح", "حلو", "كتير", "مشان", "ولا شي"],
            "moroccan": ["زوين", "بزاف", "واخا", "فين", "كيف داير"]
        }
        
        for region, indicators in dialect_indicators.items():
            matches = [ind for ind in indicators if ind in text]
            if matches:
                regional_indicators[region] = {
                    "matches": matches,
                    "strength": len(matches) / len(indicators),
                    "confidence": min(1.0, len(matches) / 2.0)
                }
        
        # Calculate overall cultural significance
        cultural_significance = sum(
            marker["importance"] * marker["strength"] 
            for marker in cultural_markers.values()
        )
        
        return {
            "cultural_markers": cultural_markers,
            "regional_indicators": regional_indicators,
            "temporal_context": temporal_context,
            "cultural_significance": cultural_significance,
            "dominant_region": max(regional_indicators.items(), key=lambda x: x[1]["strength"])[0] if regional_indicators else None,
            "cultural_richness": len(cultural_markers)
        }
    
    def _tokenize_arabic(self, text: str) -> List[str]:
        """Advanced Arabic tokenization with normalization"""
        
        # Remove diacritics
        diacritics = 'ًٌٍَُِّْ'
        for diacritic in diacritics:
            text = text.replace(diacritic, '')
        
        # Normalize common variations
        text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        text = text.replace('ة', 'ه').replace('ى', 'ي')
        
        # Remove punctuation and split
        import string
        arabic_punctuation = '،؛؟!'
        all_punctuation = string.punctuation + arabic_punctuation
        
        for punct in all_punctuation:
            text = text.replace(punct, ' ')
        
        # Filter valid Arabic words
        words = []
        for word in text.split():
            if len(word) > 2 and any('\u0600' <= char <= '\u06FF' for char in word):
                words.append(word)
        
        return words
    
    def generate_insights_summary(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive insights summary"""
        
        insights = {
            "key_findings": [],
            "recommendations": [],
            "cultural_notes": [],
            "confidence_score": 0.0
        }
        
        # Analyze topics
        if "topics" in analysis_results:
            top_topics = analysis_results["topics"]["topics"][:5]
            if top_topics:
                insights["key_findings"].append(
                    f"أهم المواضيع المطروحة: {', '.join([t['term'] for t in top_topics])}"
                )
        
        # Analyze emotions
        if "emotions" in analysis_results:
            dominant_emotion = analysis_results["emotions"]["dominant_emotion"]
            if dominant_emotion:
                insights["key_findings"].append(
                    f"المشاعر السائدة: {dominant_emotion}"
                )
        
        # Analyze cultural context
        if "cultural" in analysis_results:
            cultural_markers = analysis_results["cultural"]["cultural_markers"]
            if cultural_markers:
                top_cultural = max(cultural_markers.items(), key=lambda x: x[1]["strength"])
                insights["cultural_notes"].append(
                    f"السياق الثقافي الأبرز: {top_cultural[0]}"
                )
        
        # Generate recommendations
        if analysis_results.get("sentiment_score", 0) < 0:
            insights["recommendations"].append("يُنصح بمراجعة العوامل المؤثرة على رضا العملاء")
        
        if "entities" in analysis_results:
            entity_density = analysis_results["entities"]["statistics"]["entity_density"]
            if entity_density > 0.1:
                insights["recommendations"].append("يحتوي النص على معلومات مفصلة قابلة للتحليل")
        
        # Calculate overall confidence
        confidence_factors = []
        if "emotions" in analysis_results:
            avg_confidence = sum(analysis_results["emotions"]["confidences"].values()) / len(analysis_results["emotions"]["confidences"]) if analysis_results["emotions"]["confidences"] else 0
            confidence_factors.append(avg_confidence)
        
        if "cultural" in analysis_results:
            cultural_significance = analysis_results["cultural"]["cultural_significance"]
            confidence_factors.append(min(1.0, cultural_significance))
        
        insights["confidence_score"] = sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
        
        return insights