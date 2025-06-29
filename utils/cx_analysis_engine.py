"""
CX Analysis Engine - Business-Focused Customer Experience Intelligence
Replaces cultural analysis with actionable business metrics and KPI correlation
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from utils.api_key_manager import APIKeyManager

logger = logging.getLogger(__name__)

class CXAnalysisEngine:
    """Core engine focused on business metrics, not cultural theater"""
    
    def __init__(self):
        self.api_key_manager = APIKeyManager()
        self.agents = {
            "sentiment": SentimentImpactAgent(self.api_key_manager),
            "drivers": DriverAnalysisAgent(self.api_key_manager),
            "impact": BusinessImpactAgent(self.api_key_manager)
        }
        
        # Business assumptions for calculations
        self.business_config = {
            "average_customer_value": 500,  # Monthly
            "average_contract_length": 12,  # Months
            "referral_value": 250,          # Per referral
            "support_hour_cost": 50         # Per hour
        }
        
    async def analyze_feedback(self, text: str, customer_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Complete CX analysis pipeline: Sentiment → Drivers → Business Impact
        """
        analysis_id = f"cx_analysis_{int(datetime.now().timestamp())}"
        logger.info(f"Starting CX analysis {analysis_id}")
        
        try:
            # Stage 1: Sentiment Impact Analysis
            sentiment_result = await self.agents["sentiment"].analyze(text)
            
            # Stage 2: Driver Analysis
            driver_result = await self.agents["drivers"].analyze(text)
            
            # Stage 3: Business Impact Assessment
            impact_result = await self.agents["impact"].assess_impact(
                text=text,
                sentiment_result=sentiment_result,
                driver_result=driver_result,
                customer_context=customer_context
            )
            
            # Combine results into comprehensive business intelligence
            cx_intelligence = {
                "analysis_id": analysis_id,
                "timestamp": datetime.now().isoformat(),
                "input_text": text,
                "sentiment_analysis": sentiment_result,
                "driver_analysis": driver_result,
                "business_impact": impact_result,
                "executive_summary": self._generate_executive_summary(
                    sentiment_result, driver_result, impact_result
                ),
                "action_required": impact_result.get("resolution_priority", "P4") in ["P1", "P2"]
            }
            
            logger.info(f"CX analysis {analysis_id} completed successfully")
            return cx_intelligence
            
        except Exception as e:
            logger.error(f"CX analysis {analysis_id} failed: {str(e)}")
            return self._create_fallback_analysis(text, analysis_id, str(e))
    
    def _generate_executive_summary(self, sentiment: Dict, driver: Dict, impact: Dict) -> Dict[str, Any]:
        """Generate executive summary for business stakeholders"""
        return {
            "customer_satisfaction": {
                "predicted_csat": sentiment.get("csat_prediction", 3),
                "churn_risk": sentiment.get("churn_risk", "medium"),
                "requires_intervention": sentiment.get("requires_followup", False)
            },
            "business_issue": {
                "primary_problem": driver.get("specific_issue", "Unknown issue"),
                "affected_process": driver.get("affected_journey_stage", "unknown"),
                "severity": driver.get("impact_severity", "medium")
            },
            "financial_impact": {
                "revenue_at_risk": impact.get("revenue_impact", {}).get("monthly_value_at_risk", 0),
                "resolution_cost": impact.get("operational_impact", {}).get("total_support_cost", 0),
                "roi_ratio": impact.get("resolution_roi", {}).get("roi_ratio", 0)
            },
            "recommended_action": {
                "priority": impact.get("resolution_priority", "P4"),
                "urgency": sentiment.get("urgency", "low"),
                "expected_effort": impact.get("operational_impact", {}).get("estimated_support_hours", 0)
            }
        }
    
    def _create_fallback_analysis(self, text: str, analysis_id: str, error: str) -> Dict[str, Any]:
        """Create basic analysis when full pipeline fails"""
        return {
            "analysis_id": analysis_id,
            "timestamp": datetime.now().isoformat(),
            "input_text": text,
            "status": "fallback_analysis",
            "error": error,
            "sentiment_analysis": {
                "csat_prediction": 3,
                "churn_risk": "medium",
                "actionable": False,
                "requires_followup": True
            },
            "driver_analysis": {
                "primary_driver": "unknown",
                "specific_issue": "Analysis failed - manual review required",
                "impact_severity": "medium"
            },
            "business_impact": {
                "resolution_priority": "P3",
                "revenue_impact": {"monthly_value_at_risk": 500}
            }
        }


class SentimentImpactAgent:
    """Analyzes sentiment and predicts CSAT impact with business focus"""
    
    def __init__(self, api_key_manager: APIKeyManager):
        self.api_key_manager = api_key_manager
        self.prompt_template = """
Analyze this customer feedback for business impact:

Text: {text}

Rate sentiment on CSAT scale (1-5):
1 = Very Dissatisfied (will churn)
2 = Dissatisfied (at risk)  
3 = Neutral (passive)
4 = Satisfied (stable)
5 = Very Satisfied (promoter)

Extract EXACT phrases from the text, not interpretations.

IMPORTANT: Return ONLY valid JSON with no additional text or explanation.

{{
    "csat_prediction": 3,
    "churn_risk": "medium",
    "churn_indicators": ["exact phrases suggesting churn"],
    "sentiment_drivers": ["exact customer phrases"],
    "actionable": true,
    "actionable_reason": "specific reason",
    "requires_followup": false,
    "urgency": "medium"
}}

Rules:
- Actionable = Has specific issue + clear owner + fixable
- Requires followup = Customer expects response OR issue is critical
- Return complete JSON only
"""
    
    async def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment with business impact focus"""
        try:
            prompt = self.prompt_template.format(text=text)
            
            # Use OpenAI for analysis
            client = self.api_key_manager.get_openai_client()
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1000
            )
            
            # Parse JSON response with validation
            result_text = response.choices[0].message.content
            if not result_text:
                raise ValueError("Empty response from AI")
            
            result_text = result_text.strip()
            
            # Extract JSON from code blocks if present
            if result_text.startswith('```json'):
                result_text = result_text.replace('```json', '').replace('```', '').strip()
            elif result_text.startswith('```'):
                result_text = result_text.replace('```', '').strip()
            
            try:
                result = json.loads(result_text)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error in SentimentImpactAgent: {str(e)}, Response: {result_text}")
                raise ValueError(f"Invalid JSON response: {str(e)}")
            
            # Add calculated churn risk based on phrases
            result["churn_risk"] = self._calculate_churn_risk(text, result.get("csat_prediction", 3))
            
            return result
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {str(e)}")
            return self._create_fallback_sentiment(text)
    
    def _calculate_churn_risk(self, text: str, csat_prediction: int) -> str:
        """Calculate churn risk based on language patterns"""
        high_risk_phrases = ["cancel", "never again", "switching to", "last chance", "unacceptable"]
        medium_risk_phrases = ["disappointed", "frustrated", "considering options", "not happy"]
        
        text_lower = text.lower()
        
        if csat_prediction <= 2 and any(phrase in text_lower for phrase in high_risk_phrases):
            return "high"
        elif csat_prediction <= 3 or any(phrase in text_lower for phrase in medium_risk_phrases):
            return "medium"
        else:
            return "low"
    
    def _create_fallback_sentiment(self, text: str) -> Dict[str, Any]:
        """Basic sentiment analysis when AI fails"""
        return {
            "csat_prediction": 3,
            "churn_risk": "medium",
            "churn_indicators": [],
            "sentiment_drivers": ["analysis_failed"],
            "actionable": False,
            "actionable_reason": "AI analysis failed - requires manual review",
            "requires_followup": True,
            "urgency": "medium"
        }


class DriverAnalysisAgent:
    """Extracts specific CX drivers that impact satisfaction"""
    
    def __init__(self, api_key_manager: APIKeyManager):
        self.api_key_manager = api_key_manager
        self.prompt_template = """
Extract specific CX drivers from this feedback:

Text: {text}

Identify the PRIMARY issue impacting satisfaction:

Categories:
- Service failures (response time, resolution quality, agent competence)
- Product issues (bugs, missing features, performance, reliability)
- Process friction (billing errors, complex procedures, system failures)
- Value perception (pricing concerns, competitor comparison, ROI questions)

Journey Stages:
- Awareness, Purchase, Onboarding, Usage, Support, Renewal

IMPORTANT: Return ONLY valid JSON with no additional text.

{{
    "primary_driver": "service_failures",
    "specific_issue": "exact problem in customer's words",
    "impact_severity": "medium",
    "affected_journey_stage": "support",
    "quantifiable_impact": "2 hours",
    "friction_points": ["specific obstacles"],
    "root_cause_hint": "potential underlying issue"
}}

Severity: critical/high/medium/low
"""
    
    async def analyze(self, text: str) -> Dict[str, Any]:
        """Extract specific drivers affecting customer satisfaction"""
        try:
            prompt = self.prompt_template.format(text=text)
            
            client = self.api_key_manager.get_openai_client()
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1000
            )
            
            # Parse JSON response with validation
            result_text = response.choices[0].message.content
            if not result_text:
                raise ValueError("Empty response from AI")
            
            result_text = result_text.strip()
            try:
                result = json.loads(result_text)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error in DriverAnalysisAgent: {str(e)}, Response: {result_text}")
                raise ValueError(f"Invalid JSON response: {str(e)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Driver analysis failed: {str(e)}")
            return self._create_fallback_driver(text)
    
    def _create_fallback_driver(self, text: str) -> Dict[str, Any]:
        """Basic driver analysis when AI fails"""
        return {
            "primary_driver": "unknown",
            "specific_issue": "Unable to identify specific issue - manual review required",
            "impact_severity": "medium",
            "affected_journey_stage": "unknown",
            "quantifiable_impact": "unknown",
            "friction_points": ["analysis_failed"],
            "root_cause_hint": "AI analysis failed"
        }


class BusinessImpactAgent:
    """Calculates business impact and KPI correlation"""
    
    def __init__(self, api_key_manager: APIKeyManager):
        self.api_key_manager = api_key_manager
        self.prompt_template = """
Calculate business impact of this customer feedback:

Feedback: {text}
CSAT Prediction: {csat_score}
Primary Driver: {primary_driver}
Severity: {severity}

IMPORTANT: Return ONLY valid JSON with no additional text.

{{
    "revenue_impact": {{
        "monthly_value_at_risk": 1000,
        "risk_type": "churn",
        "risk_probability": 0.5,
        "expected_loss": 500.0
    }},
    "operational_impact": {{
        "estimated_support_hours": 2.0,
        "escalation_probability": 0.3,
        "total_support_cost": 100
    }},
    "brand_impact": {{
        "nps_change": -5,
        "review_likelihood": 0.4,
        "predicted_review_rating": 3,
        "viral_risk": "medium"
    }},
    "resolution_priority": "P3",
    "resolution_roi": {{
        "cost_to_resolve": 100,
        "value_preserved": 500.0,
        "roi_ratio": 5.0
    }}
}}

Priority: P1=Critical+High$ P2=High$ P3=Medium$ P4=Low$
"""
    
    async def assess_impact(self, text: str, sentiment_result: Dict, driver_result: Dict, 
                          customer_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Assess business impact and calculate KPI correlation"""
        try:
            prompt = self.prompt_template.format(
                text=text,
                csat_score=sentiment_result.get("csat_prediction", 3),
                primary_driver=driver_result.get("primary_driver", "unknown"),
                severity=driver_result.get("impact_severity", "medium")
            )
            
            client = self.api_key_manager.get_openai_client()
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1000
            )
            
            # Parse JSON response with validation
            result_text = response.choices[0].message.content
            if not result_text or not result_text.strip():
                raise ValueError("Empty response from AI")
            
            result_text = result_text.strip()
            try:
                result = json.loads(result_text)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error in BusinessImpactAgent: {str(e)}, Response: {result_text}")
                raise ValueError(f"Invalid JSON response: {str(e)}")
            
            # Calculate numeric values from string expressions
            result = self._calculate_numeric_impacts(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Business impact analysis failed: {str(e)}")
            return self._create_fallback_impact(sentiment_result, driver_result)
    
    def _calculate_numeric_impacts(self, result: Dict) -> Dict:
        """Convert string expressions to numeric values"""
        try:
            # Calculate expected loss
            monthly_value = result.get("revenue_impact", {}).get("monthly_value_at_risk", 500)
            probability = result.get("revenue_impact", {}).get("risk_probability", 0.5)
            result["revenue_impact"]["expected_loss"] = monthly_value * probability
            
            # Calculate support cost
            hours = result.get("operational_impact", {}).get("estimated_support_hours", 2)
            result["operational_impact"]["total_support_cost"] = hours * 50
            
            # Calculate ROI
            cost_to_resolve = result["operational_impact"]["total_support_cost"]
            value_preserved = result["revenue_impact"]["expected_loss"]
            if cost_to_resolve > 0:
                roi_ratio = value_preserved / cost_to_resolve
            else:
                roi_ratio = 0
            
            result["resolution_roi"] = {
                "cost_to_resolve": cost_to_resolve,
                "value_preserved": value_preserved,
                "roi_ratio": roi_ratio
            }
            
        except Exception as e:
            logger.warning(f"Failed to calculate numeric impacts: {str(e)}")
        
        return result
    
    def _create_fallback_impact(self, sentiment_result: Dict, driver_result: Dict) -> Dict[str, Any]:
        """Basic impact analysis when AI fails"""
        csat = sentiment_result.get("csat_prediction", 3)
        severity = driver_result.get("impact_severity", "medium")
        
        # Simple risk calculation
        if csat <= 2 and severity in ["critical", "high"]:
            risk_amount = 2500
            priority = "P2"
        elif csat <= 3:
            risk_amount = 1000
            priority = "P3"
        else:
            risk_amount = 250
            priority = "P4"
        
        return {
            "revenue_impact": {
                "monthly_value_at_risk": risk_amount,
                "risk_type": "churn",
                "risk_probability": 0.5,
                "expected_loss": risk_amount * 0.5
            },
            "operational_impact": {
                "estimated_support_hours": 2.0,
                "escalation_probability": 0.3,
                "total_support_cost": 100
            },
            "brand_impact": {
                "nps_change": -10 if csat <= 2 else 0,
                "review_likelihood": 0.3,
                "predicted_review_rating": csat,
                "viral_risk": "medium"
            },
            "resolution_priority": priority,
            "resolution_roi": {
                "cost_to_resolve": 100,
                "value_preserved": risk_amount * 0.5,
                "roi_ratio": (risk_amount * 0.5) / 100
            }
        }