"""
Real-time analytics API endpoints for Arabic VoC platform
Advanced analytics with cultural context and dialect breakdown
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, text
from pydantic import BaseModel, Field
import json

from models_unified import Feedback, FeedbackChannel, FeedbackStatus
from models.survey import Response as SurveyResponse
from utils.database_arabic import get_arabic_db_session, arabic_db_manager
from utils.arabic_processor import ArabicTextProcessor, extract_sentiment
from api.auth import get_current_user
from models.auth import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/analytics/realtime", tags=["realtime-analytics"])

class ConnectionManager:
    """WebSocket connection manager for real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.organization_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, organization_id: Optional[int] = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if organization_id:
            if organization_id not in self.organization_connections:
                self.organization_connections[organization_id] = []
            self.organization_connections[organization_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, organization_id: Optional[int] = None):
        self.active_connections.remove(websocket)
        
        if organization_id and organization_id in self.organization_connections:
            self.organization_connections[organization_id].remove(websocket)
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_text(json.dumps(message))
    
    async def broadcast_to_organization(self, message: dict, organization_id: int):
        if organization_id in self.organization_connections:
            for connection in self.organization_connections[organization_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    pass  # Connection might be closed
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                pass  # Connection might be closed

manager = ConnectionManager()

# Pydantic models for analytics
class DialectBreakdown(BaseModel):
    """Dialect-specific analytics"""
    dialect: str
    count: int
    avg_sentiment: float
    confidence: float
    sample_phrases: List[str]

class ChannelPerformance(BaseModel):
    """Channel performance metrics"""
    channel: str
    channel_ar: str
    total_feedback: int
    avg_sentiment: float
    avg_rating: Optional[float]
    response_time_hours: Optional[float]
    trending_up: bool

class CulturalInsight(BaseModel):
    """Cultural context insights"""
    insight_type: str
    insight_ar: str
    description: str
    description_ar: str
    impact_score: float
    examples: List[str]

class RegionalMetrics(BaseModel):
    """Regional sentiment metrics"""
    region: str
    region_ar: str
    sentiment_score: float
    feedback_count: int
    cultural_factors: List[str]

class RealTimeMetrics(BaseModel):
    """Real-time dashboard metrics"""
    timestamp: datetime
    total_feedback_today: int
    sentiment_distribution: Dict[str, int]
    dialect_breakdown: List[DialectBreakdown]
    channel_performance: List[ChannelPerformance]
    cultural_insights: List[CulturalInsight]
    regional_metrics: List[RegionalMetrics]
    trending_topics: List[Dict[str, Any]]
    live_sentiment_score: float

class ArabicNLPProcessor:
    """Advanced Arabic NLP processing for analytics"""
    
    def __init__(self):
        self.processor = ArabicTextProcessor()
        
        # Cultural context patterns
        self.cultural_patterns = {
            "ramadan": ["رمضان", "الصيام", "إفطار", "سحور", "تراويح"],
            "eid": ["عيد", "العيد", "عيد الفطر", "عيد الأضحى"],
            "weekend": ["نهاية الأسبوع", "عطلة", "الجمعة", "السبت"],
            "hospitality": ["ضيافة", "كرم", "ترحيب", "استقبال"],
            "family": ["عائلة", "أسرة", "أهل", "عيال"],
            "respect": ["احترام", "تقدير", "وقار", "أدب"]
        }
        
        # Dialect indicators
        self.dialect_indicators = {
            "gulf": ["زين", "يهبل", "مشكور", "يعطيك العافية", "ما شاء الله"],
            "egyptian": ["كويس", "حلو", "جميل", "عجبني", "بجد"],
            "levantine": ["منيح", "حلو", "ولا شي", "مشان", "كتير"],
            "moroccan": ["زوين", "بزاف", "واخا", "بلا ما", "فين"]
        }
        
        # Emotion indicators beyond sentiment
        self.emotion_patterns = {
            "joy": ["فرح", "سعادة", "مبسوط", "فرحان", "مسرور"],
            "frustration": ["إحباط", "زعل", "مضايق", "متضايق", "منرفز"],
            "satisfaction": ["راضي", "مقتنع", "مرتاح", "راحة", "قناعة"],
            "excitement": ["متحمس", "متشوق", "حماس", "إثارة", "تشويق"],
            "gratitude": ["شكر", "امتنان", "تقدير", "عرفان", "شاكر"]
        }
    
    def detect_dialect(self, text: str) -> Dict[str, float]:
        """Detect Arabic dialect with confidence scores"""
        dialect_scores = {}
        
        for dialect, indicators in self.dialect_indicators.items():
            score = 0
            for indicator in indicators:
                if indicator in text:
                    score += 1
            
            # Normalize by text length and indicator count
            normalized_score = score / (len(text.split()) * len(indicators)) if text.split() else 0
            dialect_scores[dialect] = min(1.0, normalized_score * 10)  # Scale up
        
        return dialect_scores
    
    def extract_cultural_context(self, text: str) -> List[str]:
        """Extract cultural context markers"""
        contexts = []
        
        for context, patterns in self.cultural_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    contexts.append(context)
                    break
        
        return contexts
    
    def detect_emotions(self, text: str) -> Dict[str, float]:
        """Detect specific emotions beyond sentiment"""
        emotions = {}
        
        for emotion, patterns in self.emotion_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in text:
                    score += 1
            
            emotions[emotion] = score / len(patterns) if patterns else 0
        
        return emotions
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract Arabic entities (products, services, locations)"""
        # Simplified entity extraction
        entities = {
            "products": [],
            "services": [],
            "locations": []
        }
        
        # Common Arabic service words
        service_words = ["خدمة", "دعم", "تطبيق", "موقع", "نظام", "برنامج"]
        product_words = ["منتج", "سلعة", "بضاعة", "مادة", "أداة"]
        location_words = ["الرياض", "جدة", "دبي", "الكويت", "الدوحة", "القاهرة", "بيروت", "عمان"]
        
        words = text.split()
        for word in words:
            if any(service in word for service in service_words):
                entities["services"].append(word)
            elif any(product in word for product in product_words):
                entities["products"].append(word)
            elif any(location in word for location in location_words):
                entities["locations"].append(word)
        
        return entities

nlp_processor = ArabicNLPProcessor()

async def get_real_time_metrics(db: AsyncSession, organization_id: Optional[int] = None) -> RealTimeMetrics:
    """Generate comprehensive real-time metrics"""
    
    # Time range for "today"
    today = datetime.utcnow().date()
    start_of_day = datetime.combine(today, datetime.min.time())
    
    # Base query
    base_query = select(Feedback).where(Feedback.created_at >= start_of_day)
    if organization_id:
        # Would need to add organization_id to Feedback model
        pass
    
    # Get today's feedback
    result = await db.execute(base_query)
    feedbacks = result.scalars().all()
    
    # Total feedback today
    total_feedback_today = len(feedbacks)
    
    # Sentiment distribution
    sentiment_distribution = {"positive": 0, "neutral": 0, "negative": 0}
    total_sentiment = 0
    
    # Dialect breakdown
    dialect_counts = {"gulf": 0, "egyptian": 0, "levantine": 0, "moroccan": 0, "other": 0}
    dialect_sentiments = {"gulf": [], "egyptian": [], "levantine": [], "moroccan": [], "other": []}
    
    # Channel performance
    channel_data = {}
    
    # Cultural insights
    cultural_contexts = {}
    
    # Process each feedback
    for feedback in feedbacks:
        # Sentiment analysis
        sentiment_score = feedback.sentiment_score or 0
        total_sentiment += sentiment_score
        
        if sentiment_score > 0.3:
            sentiment_distribution["positive"] += 1
        elif sentiment_score < -0.3:
            sentiment_distribution["negative"] += 1
        else:
            sentiment_distribution["neutral"] += 1
        
        # Dialect detection
        dialect_scores = nlp_processor.detect_dialect(feedback.content)
        main_dialect = max(dialect_scores.items(), key=lambda x: x[1])[0] if dialect_scores else "other"
        
        dialect_counts[main_dialect] += 1
        dialect_sentiments[main_dialect].append(sentiment_score)
        
        # Channel analysis
        channel = feedback.channel.value
        if channel not in channel_data:
            channel_data[channel] = {
                "count": 0,
                "sentiment_sum": 0,
                "ratings": []
            }
        
        channel_data[channel]["count"] += 1
        channel_data[channel]["sentiment_sum"] += sentiment_score
        if feedback.rating:
            channel_data[channel]["ratings"].append(feedback.rating)
        
        # Cultural context
        contexts = nlp_processor.extract_cultural_context(feedback.content)
        for context in contexts:
            cultural_contexts[context] = cultural_contexts.get(context, 0) + 1
    
    # Build dialect breakdown
    dialect_breakdown = []
    for dialect, count in dialect_counts.items():
        if count > 0:
            avg_sentiment = sum(dialect_sentiments[dialect]) / count
            sample_phrases = [f.content[:50] + "..." for f in feedbacks[:3] 
                            if nlp_processor.detect_dialect(f.content).get(dialect, 0) > 0.5]
            
            dialect_breakdown.append(DialectBreakdown(
                dialect=dialect,
                count=count,
                avg_sentiment=avg_sentiment,
                confidence=min(1.0, count / max(total_feedback_today, 1)),
                sample_phrases=sample_phrases[:3]
            ))
    
    # Build channel performance
    channel_performance = []
    channel_names_ar = {
        "website": "الموقع الإلكتروني",
        "mobile_app": "التطبيق المحمول", 
        "email": "البريد الإلكتروني",
        "phone": "الهاتف",
        "whatsapp": "واتساب",
        "sms": "الرسائل النصية",
        "social_media": "وسائل التواصل",
        "chatbot": "الدردشة الآلية"
    }
    
    for channel, data in channel_data.items():
        avg_sentiment = data["sentiment_sum"] / data["count"] if data["count"] > 0 else 0
        avg_rating = sum(data["ratings"]) / len(data["ratings"]) if data["ratings"] else None
        
        channel_performance.append(ChannelPerformance(
            channel=channel,
            channel_ar=channel_names_ar.get(channel, channel),
            total_feedback=data["count"],
            avg_sentiment=avg_sentiment,
            avg_rating=avg_rating,
            response_time_hours=None,  # Would calculate from metadata
            trending_up=True  # Would compare with previous period
        ))
    
    # Build cultural insights
    cultural_insights = []
    for context, count in cultural_contexts.items():
        if count > 0:
            cultural_insights.append(CulturalInsight(
                insight_type=context,
                insight_ar=f"سياق {context}",
                description=f"Cultural context '{context}' mentioned {count} times",
                description_ar=f"تم ذكر السياق الثقافي '{context}' {count} مرة",
                impact_score=count / max(total_feedback_today, 1),
                examples=[]
            ))
    
    # Trending topics (simplified)
    trending_topics = [
        {"topic": "خدمة العملاء", "mentions": 15, "sentiment": 0.7},
        {"topic": "جودة المنتج", "mentions": 12, "sentiment": 0.5},
        {"topic": "سرعة التسليم", "mentions": 8, "sentiment": -0.2}
    ]
    
    # Regional metrics (mock data for now)
    regional_metrics = [
        RegionalMetrics(
            region="Gulf",
            region_ar="الخليج",
            sentiment_score=0.6,
            feedback_count=45,
            cultural_factors=["hospitality", "respect"]
        ),
        RegionalMetrics(
            region="Levant",
            region_ar="بلاد الشام",
            sentiment_score=0.4,
            feedback_count=32,
            cultural_factors=["family", "tradition"]
        )
    ]
    
    # Calculate live sentiment score
    live_sentiment_score = total_sentiment / max(total_feedback_today, 1)
    
    return RealTimeMetrics(
        timestamp=datetime.utcnow(),
        total_feedback_today=total_feedback_today,
        sentiment_distribution=sentiment_distribution,
        dialect_breakdown=dialect_breakdown,
        channel_performance=channel_performance,
        cultural_insights=cultural_insights,
        regional_metrics=regional_metrics,
        trending_topics=trending_topics,
        live_sentiment_score=live_sentiment_score
    )

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, organization_id: Optional[int] = None):
    """WebSocket endpoint for real-time analytics updates"""
    await manager.connect(websocket, organization_id)
    
    try:
        while True:
            # Send real-time metrics every 5 seconds
            await asyncio.sleep(5)
            
            # Get database session
            async with arabic_db_manager.session_factory() as db:
                metrics = await get_real_time_metrics(db, organization_id)
                
                await manager.send_personal_message({
                    "type": "metrics_update",
                    "data": metrics.model_dump(mode='json')
                }, websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, organization_id)

@router.get("/dashboard", response_model=RealTimeMetrics)
async def get_dashboard_metrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_arabic_db_session)
):
    """Get current dashboard metrics"""
    try:
        metrics = await get_real_time_metrics(db, current_user.organization_id)
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard metrics"
        )

@router.get("/sentiment-trends")
async def get_sentiment_trends(
    hours: int = 24,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_arabic_db_session)
):
    """Get sentiment trends over time with dialect breakdown"""
    try:
        # Get data for the specified time period
        since = datetime.utcnow() - timedelta(hours=hours)
        
        result = await db.execute(
            select(Feedback)
            .where(Feedback.created_at >= since)
            .where(Feedback.sentiment_score.isnot(None))
            .order_by(Feedback.created_at)
        )
        feedbacks = result.scalars().all()
        
        # Group by hour
        hourly_data = {}
        
        for feedback in feedbacks:
            hour = feedback.created_at.replace(minute=0, second=0, microsecond=0)
            
            if hour not in hourly_data:
                hourly_data[hour] = {
                    "sentiment_sum": 0,
                    "count": 0,
                    "dialects": {"gulf": 0, "egyptian": 0, "levantine": 0, "moroccan": 0}
                }
            
            hourly_data[hour]["sentiment_sum"] += feedback.sentiment_score
            hourly_data[hour]["count"] += 1
            
            # Detect dialect
            dialect_scores = nlp_processor.detect_dialect(feedback.content)
            main_dialect = max(dialect_scores.items(), key=lambda x: x[1])[0] if dialect_scores else "other"
            
            if main_dialect in hourly_data[hour]["dialects"]:
                hourly_data[hour]["dialects"][main_dialect] += 1
        
        # Format for response
        trends = []
        for hour, data in sorted(hourly_data.items()):
            avg_sentiment = data["sentiment_sum"] / data["count"] if data["count"] > 0 else 0
            
            trends.append({
                "timestamp": hour.isoformat(),
                "avg_sentiment": avg_sentiment,
                "feedback_count": data["count"],
                "dialect_breakdown": data["dialects"]
            })
        
        return {"trends": trends, "period_hours": hours}
        
    except Exception as e:
        logger.error(f"Error getting sentiment trends: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sentiment trends"
        )

@router.get("/topic-modeling")
async def get_topic_modeling(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_arabic_db_session)
):
    """Advanced topic modeling for Arabic feedback themes"""
    try:
        # Get recent feedback
        since = datetime.utcnow() - timedelta(days=days)
        
        result = await db.execute(
            select(Feedback.content, Feedback.ai_categories)
            .where(Feedback.created_at >= since)
            .where(Feedback.content.isnot(None))
        )
        feedbacks = result.fetchall()
        
        # Simple topic extraction
        topic_frequencies = {}
        entity_mentions = {"products": {}, "services": {}, "locations": {}}
        
        for feedback in feedbacks:
            # Extract entities
            entities = nlp_processor.extract_entities(feedback.content)
            
            for entity_type, entity_list in entities.items():
                for entity in entity_list:
                    if entity not in entity_mentions[entity_type]:
                        entity_mentions[entity_type][entity] = 0
                    entity_mentions[entity_type][entity] += 1
            
            # Use AI categories if available
            if feedback.ai_categories:
                for category in feedback.ai_categories:
                    if category not in topic_frequencies:
                        topic_frequencies[category] = 0
                    topic_frequencies[category] += 1
        
        # Sort topics by frequency
        sorted_topics = sorted(topic_frequencies.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Sort entities by mentions
        sorted_entities = {}
        for entity_type, mentions in entity_mentions.items():
            sorted_entities[entity_type] = sorted(mentions.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "topics": [{"topic": topic, "frequency": freq} for topic, freq in sorted_topics],
            "entities": sorted_entities,
            "period_days": days
        }
        
    except Exception as e:
        logger.error(f"Error in topic modeling: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform topic modeling"
        )

@router.get("/cultural-analysis")
async def get_cultural_analysis(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_arabic_db_session)
):
    """Cultural context analysis with regional patterns"""
    try:
        # Get recent feedback
        since = datetime.utcnow() - timedelta(days=30)
        
        result = await db.execute(
            select(Feedback.content, Feedback.created_at, Feedback.sentiment_score)
            .where(Feedback.created_at >= since)
        )
        feedbacks = result.fetchall()
        
        cultural_analysis = {
            "cultural_contexts": {},
            "temporal_patterns": {},
            "emotion_analysis": {},
            "regional_insights": []
        }
        
        for feedback in feedbacks:
            # Cultural context detection
            contexts = nlp_processor.extract_cultural_context(feedback.content)
            for context in contexts:
                if context not in cultural_analysis["cultural_contexts"]:
                    cultural_analysis["cultural_contexts"][context] = {
                        "count": 0,
                        "sentiment_sum": 0,
                        "examples": []
                    }
                
                cultural_analysis["cultural_contexts"][context]["count"] += 1
                cultural_analysis["cultural_contexts"][context]["sentiment_sum"] += feedback.sentiment_score or 0
                
                if len(cultural_analysis["cultural_contexts"][context]["examples"]) < 3:
                    cultural_analysis["cultural_contexts"][context]["examples"].append(
                        feedback.content[:100] + "..."
                    )
            
            # Emotion analysis
            emotions = nlp_processor.detect_emotions(feedback.content)
            for emotion, score in emotions.items():
                if score > 0:
                    if emotion not in cultural_analysis["emotion_analysis"]:
                        cultural_analysis["emotion_analysis"][emotion] = {"total_score": 0, "count": 0}
                    
                    cultural_analysis["emotion_analysis"][emotion]["total_score"] += score
                    cultural_analysis["emotion_analysis"][emotion]["count"] += 1
        
        # Calculate averages
        for context, data in cultural_analysis["cultural_contexts"].items():
            data["avg_sentiment"] = data["sentiment_sum"] / data["count"] if data["count"] > 0 else 0
        
        for emotion, data in cultural_analysis["emotion_analysis"].items():
            data["avg_score"] = data["total_score"] / data["count"] if data["count"] > 0 else 0
        
        return cultural_analysis
        
    except Exception as e:
        logger.error(f"Error in cultural analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform cultural analysis"
        )