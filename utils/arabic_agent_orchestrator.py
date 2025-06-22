"""
LangGraph-based Arabic Analysis Agent Orchestrator
Multi-agent system for efficient Arabic feedback processing
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict

logger = logging.getLogger(__name__)

# Data Models for Agent Communication
class SentimentAnalysis(BaseModel):
    """Sentiment analysis result structure"""
    sentiment_score: float = Field(description="Sentiment score from -1 to 1")
    confidence: float = Field(description="Confidence level 0-1")
    emotion: str = Field(description="Primary emotion in Arabic")
    intensity: str = Field(description="Emotional intensity level")
    reasoning: str = Field(description="Analysis reasoning")

class TopicCategorization(BaseModel):
    """Topic categorization result structure"""
    primary_category: str = Field(description="Main business category")
    secondary_categories: List[str] = Field(description="Additional categories")
    topics: List[str] = Field(description="Specific topics mentioned")
    urgency_level: str = Field(description="Priority level")
    requires_action: bool = Field(description="Needs immediate action")
    customer_type: str = Field(description="Customer type classification")

class ActionRecommendations(BaseModel):
    """Action recommendations result structure"""
    immediate_actions: List[str] = Field(description="Immediate actions needed")
    follow_up_actions: List[str] = Field(description="Follow-up actions")
    prevention_actions: List[str] = Field(description="Prevention measures")
    escalation_required: bool = Field(description="Needs escalation")

class AnalysisState(TypedDict):
    """Shared state across all agents"""
    original_text: str
    normalized_text: str
    sentiment_result: Optional[Dict[str, Any]]
    topic_result: Optional[Dict[str, Any]]
    action_result: Optional[Dict[str, Any]]
    processing_stage: str
    error_messages: List[str]
    
class ArabicAnalysisOrchestrator:
    """LangGraph orchestrator for Arabic feedback analysis"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY", "default_key")
        )
        
        # Memory for conversation state
        self.memory = MemorySaver()
        
        # Initialize specialized agents
        self.sentiment_agent = SentimentAgent(self.llm)
        self.topic_agent = TopicAgent(self.llm)
        self.action_agent = ActionAgent(self.llm)
        
        # Build the analysis workflow graph
        self.workflow = self._build_workflow()
        
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for analysis"""
        
        workflow = StateGraph(AnalysisState)
        
        # Add agent nodes
        workflow.add_node("text_preprocessing", self._preprocess_text)
        workflow.add_node("sentiment_analysis", self._run_sentiment_analysis)
        workflow.add_node("topic_categorization", self._run_topic_analysis)
        workflow.add_node("action_recommendations", self._run_action_analysis)
        workflow.add_node("result_compilation", self._compile_results)
        
        # Define the workflow edges
        workflow.add_edge("text_preprocessing", "sentiment_analysis")
        workflow.add_edge("sentiment_analysis", "topic_categorization")
        workflow.add_edge("topic_categorization", "action_recommendations")
        workflow.add_edge("action_recommendations", "result_compilation")
        workflow.add_edge("result_compilation", END)
        
        # Set entry point
        workflow.set_entry_point("text_preprocessing")
        
        return workflow.compile(checkpointer=self.memory)
    
    def _preprocess_text(self, state: AnalysisState) -> AnalysisState:
        """Preprocess Arabic text for analysis"""
        try:
            from utils.arabic_processor import ArabicTextProcessor
            processor = ArabicTextProcessor()
            
            # Normalize Arabic text
            normalized = processor.normalize_arabic(state["original_text"])
            state["normalized_text"] = normalized
            state["processing_stage"] = "preprocessed"
            
            logger.info(f"Text preprocessing completed: {len(normalized)} characters")
            return state
            
        except Exception as e:
            state["error_messages"].append(f"Preprocessing error: {str(e)}")
            state["normalized_text"] = state["original_text"]  # Fallback
            return state
    
    def _run_sentiment_analysis(self, state: AnalysisState) -> AnalysisState:
        """Execute sentiment analysis agent"""
        try:
            result = self.sentiment_agent.analyze(state["normalized_text"])
            state["sentiment_result"] = result
            state["processing_stage"] = "sentiment_completed"
            
            logger.info(f"Sentiment analysis completed: {result.get('sentiment_score')}")
            return state
            
        except Exception as e:
            state["error_messages"].append(f"Sentiment analysis error: {str(e)}")
            # Fallback sentiment
            state["sentiment_result"] = {
                "sentiment_score": 0.0,
                "confidence": 0.0,
                "emotion": "غير محدد",
                "intensity": "منخفض",
                "reasoning": "خطأ في التحليل"
            }
            return state
    
    def _run_topic_analysis(self, state: AnalysisState) -> AnalysisState:
        """Execute topic categorization agent"""
        try:
            # Pass sentiment context to topic agent
            sentiment_data = state.get("sentiment_result", {})
            context = {
                "text": state["normalized_text"],
                "sentiment_score": sentiment_data.get("sentiment_score", 0.0),
                "emotion": sentiment_data.get("emotion", "محايد")
            }
            
            result = self.topic_agent.analyze(context)
            state["topic_result"] = result
            state["processing_stage"] = "topic_completed"
            
            logger.info(f"Topic analysis completed: {result.get('primary_category')}")
            return state
            
        except Exception as e:
            state["error_messages"].append(f"Topic analysis error: {str(e)}")
            # Fallback categorization
            state["topic_result"] = {
                "primary_category": "غير محدد",
                "secondary_categories": [],
                "topics": [],
                "urgency_level": "منخفض",
                "requires_action": False,
                "customer_type": "غير محدد"
            }
            return state
    
    def _run_action_analysis(self, state: AnalysisState) -> AnalysisState:
        """Execute action recommendations agent"""
        try:
            # Combine previous analysis results
            context = {
                "text": state["normalized_text"],
                "sentiment": state.get("sentiment_result", {}),
                "categorization": state.get("topic_result", {})
            }
            
            result = self.action_agent.analyze(context)
            state["action_result"] = result
            state["processing_stage"] = "action_completed"
            
            logger.info(f"Action analysis completed: {len(result.get('immediate_actions', []))} actions")
            return state
            
        except Exception as e:
            state["error_messages"].append(f"Action analysis error: {str(e)}")
            # Fallback actions
            state["action_result"] = {
                "immediate_actions": ["مراجعة التعليق"],
                "follow_up_actions": [],
                "prevention_actions": [],
                "escalation_required": False
            }
            return state
    
    def _compile_results(self, state: AnalysisState) -> AnalysisState:
        """Compile final analysis results"""
        state["processing_stage"] = "completed"
        logger.info("Analysis compilation completed")
        return state
    
    async def analyze_feedback(self, text: str, thread_id: str = None) -> Dict[str, Any]:
        """Main method to analyze Arabic feedback"""
        try:
            # Initialize state
            initial_state = AnalysisState(
                original_text=text,
                normalized_text="",
                sentiment_result=None,
                topic_result=None, 
                action_result=None,
                processing_stage="initial",
                error_messages=[]
            )
            
            # Run the workflow
            config = {"configurable": {"thread_id": thread_id or f"analysis_{datetime.now().isoformat()}"}}
            result = await self.workflow.ainvoke(initial_state, config=config)
            
            # Format output for compatibility with existing system
            return {
                "summary": self._generate_summary(result),
                "sentiment": result.get("sentiment_result", {}),
                "categorization": result.get("topic_result", {}),
                "suggested_actions": self._format_actions(result.get("action_result")),
                "analysis_timestamp": datetime.now().isoformat(),
                "model_used": "gpt-4o-langgraph",
                "processing_stages": result.get("processing_stage"),
                "errors": result.get("error_messages", [])
            }
            
        except Exception as e:
            logger.error(f"Orchestrator error: {str(e)}")
            return self._fallback_analysis(text, str(e))
    
    def _generate_summary(self, state: AnalysisState) -> str:
        """Generate analysis summary"""
        sentiment_data = state.get("sentiment_result", {})
        topic_data = state.get("topic_result", {})
        
        if not sentiment_data or not topic_data:
            return "تعذر إنشاء ملخص شامل"
        
        sentiment = sentiment_data.get("emotion", "محايد")
        category = topic_data.get("primary_category", "عام")
        urgency = topic_data.get("urgency_level", "متوسط")
        
        return f"تعليق {sentiment} في فئة {category} بمستوى أولوية {urgency}"
    
    def _format_actions(self, actions: Optional[Dict[str, Any]]) -> List[str]:
        """Format action recommendations for output"""
        if not actions:
            return []
        
        all_actions = []
        all_actions.extend(actions.get("immediate_actions", []))
        all_actions.extend(actions.get("follow_up_actions", []))
        all_actions.extend(actions.get("prevention_actions", []))
        
        return all_actions
    
    def _fallback_analysis(self, text: str, error: str) -> Dict[str, Any]:
        """Fallback analysis when workflow fails"""
        return {
            "summary": "تعذر تحليل التعليق بالكامل",
            "sentiment": {
                "sentiment_score": 0.0,
                "confidence": 0.0,
                "emotion": "غير محدد",
                "intensity": "منخفض",
                "reasoning": f"خطأ في النظام: {error}"
            },
            "categorization": {
                "primary_category": "غير محدد",
                "secondary_categories": [],
                "topics": [],
                "urgency_level": "منخفض",
                "requires_action": False,
                "customer_type": "غير محدد"
            },
            "suggested_actions": ["مراجعة التعليق يدوياً"],
            "analysis_timestamp": datetime.now().isoformat(),
            "model_used": "fallback",
            "error": error
        }


class SentimentAgent:
    """Specialized agent for Arabic sentiment analysis"""
    
    def __init__(self, llm):
        self.llm = llm
        self.parser = JsonOutputParser(pydantic_object=SentimentAnalysis)
        
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""أنت خبير متخصص في تحليل المشاعر للنصوص العربية. 
            مهمتك الوحيدة هي تحليل المشاعر وإرجاع النتيجة بدقة عالية.
            
            ركز على:
            - دقة تحديد المشاعر الأساسية
            - مستوى الثقة في التحليل
            - شدة المشاعر المعبر عنها
            - السياق الثقافي العربي"""),
            
            HumanMessage(content="""حلل مشاعر النص التالي وأرجع النتيجة بصيغة JSON:

النص: {text}

المطلوب:
- sentiment_score: رقم من -1 إلى 1
- confidence: مستوى الثقة من 0 إلى 1  
- emotion: المشاعر الرئيسية (فرح، غضب، حزن، إعجاب، إحباط، محايد)
- intensity: شدة المشاعر (عالي، متوسط، منخفض)
- reasoning: تفسير مختصر للتحليل

{format_instructions}""")
        ])
        
        self.chain = self.prompt | self.llm | self.parser
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of Arabic text"""
        try:
            result = self.chain.invoke({
                "text": text,
                "format_instructions": self.parser.get_format_instructions()
            })
            return result
        except Exception as e:
            logger.error(f"Sentiment agent error: {e}")
            raise


class TopicAgent:
    """Specialized agent for Arabic topic categorization"""
    
    def __init__(self, llm):
        self.llm = llm
        self.parser = JsonOutputParser(pydantic_object=TopicCategorization)
        
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""أنت خبير متخصص في تصنيف تعليقات العملاء حسب فئات الأعمال.
            مهمتك تحديد الفئة والموضوع ومستوى الأولوية بدقة.
            
            الفئات الرئيسية:
            - خدمة العملاء
            - المنتج  
            - التسعير
            - التسليم
            - التقنية
            - أخرى"""),
            
            HumanMessage(content="""صنف التعليق التالي وأرجع النتيجة بصيغة JSON:

النص: {text}
السياق العاطفي: {emotion} (درجة المشاعر: {sentiment_score})

المطلوب:
- primary_category: الفئة الرئيسية
- secondary_categories: فئات فرعية (قائمة)
- topics: المواضيع المحددة (قائمة)
- urgency_level: مستوى الأولوية (عالي، متوسط، منخفض)
- requires_action: يتطلب إجراء فوري (true/false)  
- customer_type: نوع العميل (جديد، حالي، سابق، غير محدد)

{format_instructions}""")
        ])
        
        self.chain = self.prompt | self.llm | self.parser
    
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze topic categorization with sentiment context"""
        try:
            result = self.chain.invoke({
                "text": context["text"],
                "sentiment_score": context.get("sentiment_score", 0.0),
                "emotion": context.get("emotion", "محايد"),
                "format_instructions": self.parser.get_format_instructions()
            })
            return result
        except Exception as e:
            logger.error(f"Topic agent error: {e}")
            raise


class ActionAgent:
    """Specialized agent for action recommendations"""
    
    def __init__(self, llm):
        self.llm = llm
        self.parser = JsonOutputParser(pydantic_object=ActionRecommendations)
        
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""أنت مستشار خدمة عملاء محترف متخصص في اقتراح الإجراءات.
            مهمتك تحديد الإجراءات العملية القابلة للتنفيذ بناءً على تحليل التعليق.
            
            أنواع الإجراءات:
            - إجراءات فورية: تتطلب تدخل مباشر
            - إجراءات المتابعة: خطوات لاحقة
            - إجراءات وقائية: لتجنب تكرار المشكلة"""),
            
            HumanMessage(content="""اقترح إجراءات محددة للتعليق التالي:

النص: {text}

السياق:
- تحليل المشاعر: {sentiment}
- التصنيف: {categorization}

المطلوب:
- immediate_actions: إجراءات فورية (قائمة)
- follow_up_actions: إجراءات متابعة (قائمة)  
- prevention_actions: إجراءات وقائية (قائمة)
- escalation_required: يحتاج تصعيد (true/false)

{format_instructions}""")
        ])
        
        self.chain = self.prompt | self.llm | self.parser
    
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate action recommendations based on analysis"""
        try:
            result = self.chain.invoke({
                "text": context["text"],
                "sentiment": json.dumps(context.get("sentiment", {}), ensure_ascii=False),
                "categorization": json.dumps(context.get("categorization", {}), ensure_ascii=False),
                "format_instructions": self.parser.get_format_instructions()
            })
            return result
        except Exception as e:
            logger.error(f"Action agent error: {e}")
            raise


# Global orchestrator instance
arabic_orchestrator = ArabicAnalysisOrchestrator()

async def analyze_arabic_feedback_agents(text: str, thread_id: str = None) -> Dict[str, Any]:
    """Main function to analyze Arabic feedback using agent orchestration"""
    return await arabic_orchestrator.analyze_feedback(text, thread_id)