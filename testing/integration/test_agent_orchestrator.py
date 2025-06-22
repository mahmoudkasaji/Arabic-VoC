"""
Tests for the LangGraph Arabic Analysis Agent Orchestrator
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from utils.arabic_agent_orchestrator import (
    ArabicAnalysisOrchestrator, 
    analyze_arabic_feedback_agents,
    SentimentAgent,
    TopicAgent, 
    ActionAgent
)

class TestAgentOrchestrator:
    """Test the LangGraph orchestrator"""
    
    @pytest.mark.asyncio
    async def test_complete_analysis_workflow(self):
        """Test complete analysis workflow with agents"""
        orchestrator = ArabicAnalysisOrchestrator()
        
        test_text = "الخدمة ممتازة جداً وأنصح بها بشدة للجميع"
        
        # Mock the LLM responses to avoid API calls in tests
        with patch.object(orchestrator.sentiment_agent, 'analyze') as mock_sentiment, \
             patch.object(orchestrator.topic_agent, 'analyze') as mock_topic, \
             patch.object(orchestrator.action_agent, 'analyze') as mock_action:
            
            # Mock responses
            mock_sentiment.return_value = {
                "sentiment_score": 0.9,
                "confidence": 0.95,
                "emotion": "إعجاب",
                "intensity": "عالي",
                "reasoning": "تعبير إيجابي قوي"
            }
            
            mock_topic.return_value = {
                "primary_category": "خدمة العملاء",
                "secondary_categories": ["جودة الخدمة"],
                "topics": ["رضا العميل", "توصية"],
                "urgency_level": "منخفض",
                "requires_action": False,
                "customer_type": "حالي"
            }
            
            mock_action.return_value = {
                "immediate_actions": ["شكر العميل"],
                "follow_up_actions": ["مشاركة التجربة الإيجابية"],
                "prevention_actions": ["الحفاظ على مستوى الخدمة"],
                "escalation_required": False
            }
            
            # Run analysis
            result = await orchestrator.analyze_feedback(test_text)
            
            # Verify structure
            assert "sentiment" in result
            assert "categorization" in result
            assert "suggested_actions" in result
            assert result["model_used"] == "gpt-4o-langgraph"
            
            # Verify sentiment data
            assert result["sentiment"]["sentiment_score"] == 0.9
            assert result["sentiment"]["emotion"] == "إعجاب"
            
            # Verify categorization
            assert result["categorization"]["primary_category"] == "خدمة العملاء"
            assert "رضا العميل" in result["categorization"]["topics"]
            
            # Verify actions
            assert "شكر العميل" in result["suggested_actions"]
    
    @pytest.mark.asyncio
    async def test_agent_error_handling(self):
        """Test error handling in agent workflow"""
        orchestrator = ArabicAnalysisOrchestrator()
        
        test_text = "نص تجريبي للاختبار"
        
        # Mock sentiment agent to raise error
        with patch.object(orchestrator.sentiment_agent, 'analyze') as mock_sentiment:
            mock_sentiment.side_effect = Exception("Sentiment analysis failed")
            
            result = await orchestrator.analyze_feedback(test_text)
            
            # Should handle error gracefully
            assert result is not None
            assert "errors" in result
            assert len(result["errors"]) > 0
            assert "Sentiment analysis error" in result["errors"][0]
            
            # Should provide fallback data
            assert result["sentiment"]["sentiment_score"] == 0.0
            assert result["sentiment"]["emotion"] == "غير محدد"
    
    @pytest.mark.asyncio 
    async def test_workflow_state_progression(self):
        """Test that workflow state progresses correctly"""
        orchestrator = ArabicAnalysisOrchestrator()
        
        # Mock all agents
        with patch.object(orchestrator.sentiment_agent, 'analyze') as mock_sentiment, \
             patch.object(orchestrator.topic_agent, 'analyze') as mock_topic, \
             patch.object(orchestrator.action_agent, 'analyze') as mock_action:
            
            mock_sentiment.return_value = {
                "sentiment_score": 0.5, "confidence": 0.8,
                "emotion": "محايد", "intensity": "متوسط", "reasoning": "تحليل"
            }
            mock_topic.return_value = {
                "primary_category": "عام", "secondary_categories": [],
                "topics": [], "urgency_level": "منخفض",
                "requires_action": False, "customer_type": "غير محدد"
            }
            mock_action.return_value = {
                "immediate_actions": [], "follow_up_actions": [],
                "prevention_actions": [], "escalation_required": False
            }
            
            result = await orchestrator.analyze_feedback("اختبار")
            
            # Check that processing completed
            assert result["processing_stages"] == "completed"


class TestIndividualAgents:
    """Test individual specialized agents"""
    
    def test_sentiment_agent_structure(self):
        """Test sentiment agent initialization"""
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
        agent = SentimentAgent(llm)
        
        assert agent.llm is not None
        assert agent.parser is not None
        assert agent.chain is not None
    
    def test_topic_agent_structure(self):
        """Test topic agent initialization"""
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
        agent = TopicAgent(llm)
        
        assert agent.llm is not None
        assert agent.parser is not None
        assert agent.chain is not None
    
    def test_action_agent_structure(self):
        """Test action agent initialization"""
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
        agent = ActionAgent(llm)
        
        assert agent.llm is not None
        assert agent.parser is not None
        assert agent.chain is not None


class TestDataModels:
    """Test Pydantic data models"""
    
    def test_sentiment_analysis_model(self):
        """Test SentimentAnalysis model validation"""
        from utils.arabic_agent_orchestrator import SentimentAnalysis
        
        # Valid data
        sentiment = SentimentAnalysis(
            sentiment_score=0.8,
            confidence=0.9,
            emotion="فرح",
            intensity="عالي",
            reasoning="تحليل إيجابي"
        )
        
        assert sentiment.sentiment_score == 0.8
        assert sentiment.emotion == "فرح"
        
        # Test validation
        with pytest.raises(Exception):
            SentimentAnalysis(sentiment_score=2.0)  # Out of range
    
    def test_topic_categorization_model(self):
        """Test TopicCategorization model validation"""
        from utils.arabic_agent_orchestrator import TopicCategorization
        
        categorization = TopicCategorization(
            primary_category="خدمة العملاء",
            secondary_categories=["جودة", "سرعة"],
            topics=["رضا العميل"],
            urgency_level="متوسط",
            requires_action=True,
            customer_type="جديد"
        )
        
        assert categorization.primary_category == "خدمة العملاء"
        assert len(categorization.secondary_categories) == 2
        assert categorization.requires_action is True
    
    def test_action_recommendations_model(self):
        """Test ActionRecommendations model validation"""
        from utils.arabic_agent_orchestrator import ActionRecommendations
        
        actions = ActionRecommendations(
            immediate_actions=["اتصال فوري"],
            follow_up_actions=["متابعة بعد يوم"],
            prevention_actions=["تدريب الفريق"],
            escalation_required=False
        )
        
        assert len(actions.immediate_actions) == 1
        assert actions.escalation_required is False


@pytest.mark.asyncio
async def test_global_analyze_function():
    """Test the global analysis function"""
    with patch('utils.arabic_agent_orchestrator.arabic_orchestrator.analyze_feedback') as mock_analyze:
        mock_analyze.return_value = {
            "sentiment": {"sentiment_score": 0.7},
            "categorization": {"primary_category": "تجربة"},
            "suggested_actions": ["متابعة"]
        }
        
        result = await analyze_arabic_feedback_agents("اختبار")
        
        assert result is not None
        assert "sentiment" in result
        mock_analyze.assert_called_once()


if __name__ == "__main__":
    # Run basic functionality test
    import asyncio
    
    async def test_basic_functionality():
        try:
            print("Testing LangGraph orchestrator...")
            result = await analyze_arabic_feedback_agents("الخدمة جيدة")
            print(f"✅ Analysis completed: {result.keys()}")
            return True
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False
    
    success = asyncio.run(test_basic_functionality())
    print(f"Basic test {'passed' if success else 'failed'}")