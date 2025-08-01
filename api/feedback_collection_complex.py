"""
Multi-channel feedback collection API endpoints
Advanced feedback processing with Arabic sentiment analysis
"""

import logging
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from pydantic import BaseModel, Field, validator

from models_unified import Feedback, FeedbackChannel, FeedbackStatus
from models.survey import Response as SurveyResponse, Question, Survey
from utils.database_arabic import get_arabic_db_session
from utils.openai_client import analyze_arabic_feedback
from utils.arabic_processor import process_arabic_text, extract_sentiment
from utils.security import validate_feedback_input, rate_limiter, log_security_event
from utils.performance import optimize_arabic_processing

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/feedback", tags=["feedback"])

# Pydantic models
class FeedbackSubmission(BaseModel):
    """Enhanced feedback submission model"""
    content: str = Field(..., min_length=1, max_length=5000)
    channel: FeedbackChannel = Field(...)
    customer_email: Optional[str] = Field(None, max_length=255)
    customer_phone: Optional[str] = Field(None, max_length=50)
    customer_name: Optional[str] = Field(None, max_length=200)
    customer_name_ar: Optional[str] = Field(None, max_length=200)
    rating: Optional[int] = Field(None, ge=1, le=5)
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    priority: Optional[str] = Field("normal", pattern="^(low|normal|high|urgent)$")
    location: Optional[str] = Field(None, max_length=200)
    location_ar: Optional[str] = Field(None, max_length=200)
    channel_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('content')
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()

class SurveyResponseSubmission(BaseModel):
    """Survey response submission model"""
    survey_uuid: str = Field(..., description="Survey UUID")
    respondent_email: Optional[str] = Field(None, max_length=255)
    respondent_name: Optional[str] = Field(None, max_length=200)
    respondent_name_ar: Optional[str] = Field(None, max_length=200)
    answers: Dict[str, Any] = Field(..., description="Question answers")
    language_used: str = Field("ar", pattern="^(ar|en)$")
    started_at: Optional[datetime] = Field(None)
    
    @validator('answers')
    def validate_answers(cls, v):
        if not v:
            raise ValueError('Answers cannot be empty')
        return v

class FeedbackResponse(BaseModel):
    """Feedback response model"""
    id: int
    content: str
    processed_content: Optional[str]
    channel: str
    status: str
    sentiment_score: Optional[float]
    confidence_score: Optional[float]
    ai_summary: Optional[str]
    ai_categories: Optional[List[str]]
    customer_email: Optional[str]
    rating: Optional[int]
    category: Optional[str]
    priority: str
    created_at: datetime
    processed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class BatchFeedbackSubmission(BaseModel):
    """Batch feedback submission model"""
    feedback_items: List[FeedbackSubmission] = Field(..., min_items=1, max_items=100)
    
class FeedbackAnalytics(BaseModel):
    """Feedback analytics model"""
    total_feedback: int
    by_channel: Dict[str, int]
    by_sentiment: Dict[str, int]
    by_rating: Dict[str, int]
    by_language: Dict[str, int]
    average_sentiment: float
    trending_topics: List[Dict[str, Any]]
    recent_feedback_count: int

# Background processing functions
async def process_feedback_with_ai(feedback_id: int, db: AsyncSession):
    """Process feedback with AI analysis"""
    try:
        # Get feedback
        result = await db.execute(select(Feedback).where(Feedback.id == feedback_id))
        feedback = result.scalar_one_or_none()
        
        if not feedback:
            logger.warning(f"Feedback {feedback_id} not found for processing")
            return
        
        # Update status to processing
        feedback.status = FeedbackStatus.PROCESSING
        await db.commit()
        
        # Process Arabic text
        operations = ["normalize", "sentiment", "reshape"]
        processing_results = await optimize_arabic_processing(feedback.content, operations)
        
        # OpenAI analysis
        ai_analysis = None
        try:
            ai_analysis = analyze_arabic_feedback(feedback.content)
        except Exception as e:
            logger.warning(f"OpenAI analysis failed for feedback {feedback_id}: {e}")
            # Use fallback sentiment analysis
            sentiment_result = extract_sentiment(feedback.content)
            ai_analysis = {
                "sentiment": {"score": sentiment_result["score"], "confidence": sentiment_result["confidence"]},
                "summary": "تم تحليل النص باستخدام النظام المحلي",
                "categories": ["عام"],
                "action_items": []
            }
        
        # Update feedback with results
        feedback.processed_content = processing_results.get("normalize", feedback.content)
        feedback.sentiment_score = ai_analysis["sentiment"]["score"]
        feedback.confidence_score = ai_analysis["sentiment"]["confidence"]
        feedback.ai_summary = ai_analysis.get("summary")
        feedback.ai_categories = ai_analysis.get("categories", [])
        feedback.ai_action_items = ai_analysis.get("action_items", [])
        feedback.status = FeedbackStatus.PROCESSED
        feedback.processed_at = datetime.utcnow()
        
        await db.commit()
        logger.info(f"Feedback {feedback_id} processed successfully")
        
    except Exception as e:
        logger.error(f"Error processing feedback {feedback_id}: {e}")
        # Update status to failed
        try:
            feedback.status = FeedbackStatus.FAILED
            await db.commit()
        except:
            pass

async def process_survey_response_sentiment(response_id: int, db: AsyncSession):
    """Process survey response using simple analyzer"""
    try:
        # Get response
        result = await db.execute(select(SurveyResponse).where(SurveyResponse.id == response_id))
        response = result.scalar_one_or_none()
        
        if not response:
            return
        
        # Extract text content from answers
        text_content = []
        for answer in response.answers.values():
            if isinstance(answer, dict) and answer.get("type") == "text":
                text_content.append(str(answer.get("answer", "")))
            elif isinstance(answer, str):
                text_content.append(answer)
        
        combined_text = " ".join(text_content)
        
        if combined_text and len(combined_text.strip()) > 5:
            # Use simple analyzer for survey responses
            try:
                from utils.simple_arabic_analyzer import SimpleArabicAnalyzer
                analyzer = SimpleArabicAnalyzer()
                analysis_result = analyzer.analyze_feedback_sync(combined_text)
                
                response.sentiment_score = analysis_result["sentiment_score"]
                response.confidence_score = analysis_result["confidence"]
                response.keywords = analysis_result.get("topics", [])
            except Exception as e:
                # Fallback analysis
                logger.warning(f"Simple analyzer failed for survey {response_id}: {e}")
                response.sentiment_score = 0.5
                response.confidence_score = 0.5
                response.keywords = ["general"]
            
            await db.commit()
            
    except Exception as e:
        logger.error(f"Error processing survey response sentiment {response_id}: {e}")

# API Endpoints
@router.post("/submit", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    feedback: FeedbackSubmission,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_arabic_db_session)
):
    """Submit feedback with enhanced processing"""
    client_ip = request.client.host
    
    try:
        # Rate limiting
        allowed, remaining = rate_limiter.is_allowed(client_ip)
        if not allowed:
            log_security_event("RATE_LIMIT_EXCEEDED", client_ip, "Feedback submission")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        # Validate and sanitize input
        validation_result = validate_feedback_input(
            content=feedback.content,
            channel=feedback.channel.value,
            customer_email=feedback.customer_email,
            customer_phone=feedback.customer_phone,
            rating=feedback.rating
        )
        
        if not validation_result["valid"]:
            log_security_event("INVALID_INPUT", client_ip, f"Errors: {validation_result['errors']}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=validation_result["errors"]
            )
        
        # Create feedback record
        db_feedback = Feedback(
            content=validation_result["sanitized_text"],
            channel=feedback.channel,
            customer_email=feedback.customer_email,
            customer_phone=feedback.customer_phone,
            customer_id=feedback.customer_email or feedback.customer_phone,
            rating=feedback.rating,
            channel_metadata={
                **feedback.channel_metadata,
                "customer_name": feedback.customer_name,
                "customer_name_ar": feedback.customer_name_ar,
                "category": feedback.category,
                "subcategory": feedback.subcategory,
                "priority": feedback.priority,
                "location": feedback.location,
                "location_ar": feedback.location_ar,
                "ip_address": client_ip,
                "user_agent": request.headers.get("user-agent")
            },
            status=FeedbackStatus.PENDING
        )
        
        db.add(db_feedback)
        await db.commit()
        await db.refresh(db_feedback)
        
        # Queue background processing
        background_tasks.add_task(process_feedback_with_ai, db_feedback.id, db)
        
        logger.info(f"Feedback submitted: {db_feedback.id} via {feedback.channel}")
        return FeedbackResponse.model_validate(db_feedback)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit feedback"
        )

@router.post("/batch", response_model=List[FeedbackResponse])
async def submit_batch_feedback(
    batch_data: BatchFeedbackSubmission,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_arabic_db_session)
):
    """Submit multiple feedback items in batch"""
    client_ip = request.client.host
    
    try:
        # Enhanced rate limiting for batch operations
        allowed, remaining = rate_limiter.is_allowed(client_ip)
        if not allowed or len(batch_data.feedback_items) > remaining:
            log_security_event("BATCH_RATE_LIMIT", client_ip, f"Batch size: {len(batch_data.feedback_items)}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Batch size exceeds rate limit"
            )
        
        results = []
        
        for feedback_item in batch_data.feedback_items:
            # Validate each item
            validation_result = validate_feedback_input(
                content=feedback_item.content,
                channel=feedback_item.channel.value,
                customer_email=feedback_item.customer_email,
                customer_phone=feedback_item.customer_phone,
                rating=feedback_item.rating
            )
            
            if validation_result["valid"]:
                # Create feedback record
                db_feedback = Feedback(
                    content=validation_result["sanitized_text"],
                    channel=feedback_item.channel,
                    customer_email=feedback_item.customer_email,
                    customer_phone=feedback_item.customer_phone,
                    customer_id=feedback_item.customer_email or feedback_item.customer_phone,
                    rating=feedback_item.rating,
                    channel_metadata={
                        **feedback_item.channel_metadata,
                        "batch_id": f"batch_{datetime.utcnow().timestamp()}",
                        "ip_address": client_ip
                    },
                    status=FeedbackStatus.PENDING
                )
                
                db.add(db_feedback)
                results.append(db_feedback)
        
        await db.commit()
        
        # Queue background processing for all items
        for db_feedback in results:
            await db.refresh(db_feedback)
            background_tasks.add_task(process_feedback_with_ai, db_feedback.id, db)
        
        logger.info(f"Batch feedback submitted: {len(results)} items")
        return [FeedbackResponse.model_validate(fb) for fb in results]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting batch feedback: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit batch feedback"
        )

@router.post("/survey-response", status_code=status.HTTP_201_CREATED)
async def submit_survey_response(
    response_data: SurveyResponseSubmission,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_arabic_db_session)
):
    """Submit survey response with Arabic support"""
    try:
        # Get survey by UUID
        result = await db.execute(
            select(Survey).where(Survey.uuid == response_data.survey_uuid)
        )
        survey = result.scalar_one_or_none()
        
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Survey not found"
            )
        
        if not survey.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Survey is not currently active"
            )
        
        # Calculate completion percentage
        total_questions = len(response_data.answers)
        completed_questions = sum(1 for answer in response_data.answers.values() 
                                if answer and str(answer).strip())
        completion_percentage = (completed_questions / max(total_questions, 1)) * 100
        
        # Calculate duration
        duration_minutes = None
        if response_data.started_at:
            duration_delta = datetime.utcnow() - response_data.started_at
            duration_minutes = duration_delta.total_seconds() / 60
        
        # Create response record
        survey_response = SurveyResponse(
            survey_id=survey.id,
            respondent_email=response_data.respondent_email,
            respondent_name=response_data.respondent_name,
            respondent_name_ar=response_data.respondent_name_ar,
            answers=response_data.answers,
            language_used=response_data.language_used,
            is_complete=completion_percentage >= 50,  # Consider 50%+ as complete
            completion_percentage=completion_percentage,
            started_at=response_data.started_at or datetime.utcnow(),
            completed_at=datetime.utcnow() if completion_percentage >= 50 else None,
            duration_minutes=duration_minutes,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        
        db.add(survey_response)
        await db.commit()
        await db.refresh(survey_response)
        
        # Update survey statistics
        survey.response_count += 1
        if survey_response.is_complete:
            completed_responses = await db.execute(
                select(func.count(SurveyResponse.id))
                .where(and_(
                    SurveyResponse.survey_id == survey.id,
                    SurveyResponse.is_complete == True
                ))
            )
            survey.completion_rate = (completed_responses.scalar() / survey.response_count) * 100
        
        await db.commit()
        
        # Queue sentiment analysis
        background_tasks.add_task(process_survey_response_sentiment, survey_response.id, db)
        
        logger.info(f"Survey response submitted: {survey_response.id} for survey {survey.id}")
        return {
            "id": survey_response.id,
            "survey_id": survey.id,
            "completion_percentage": completion_percentage,
            "is_complete": survey_response.is_complete,
            "message": "Response submitted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting survey response: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit survey response"
        )

@router.get("/analytics", response_model=FeedbackAnalytics)
async def get_feedback_analytics(
    days: int = 30,
    channel: Optional[FeedbackChannel] = None,
    db: AsyncSession = Depends(get_arabic_db_session)
):
    """Get comprehensive feedback analytics"""
    try:
        from datetime import timedelta
        
        # Date filter
        since_date = datetime.utcnow() - timedelta(days=days)
        base_query = select(Feedback).where(Feedback.created_at >= since_date)
        
        if channel:
            base_query = base_query.where(Feedback.channel == channel)
        
        # Total feedback count
        total_result = await db.execute(
            select(func.count(Feedback.id)).where(Feedback.created_at >= since_date)
        )
        total_feedback = total_result.scalar()
        
        # By channel
        channel_result = await db.execute(
            select(Feedback.channel, func.count(Feedback.id))
            .where(Feedback.created_at >= since_date)
            .group_by(Feedback.channel)
        )
        by_channel = {row[0]: row[1] for row in channel_result.fetchall()}
        
        # By sentiment
        sentiment_result = await db.execute(
            select(
                func.case(
                    (Feedback.sentiment_score > 0.3, 'positive'),
                    (Feedback.sentiment_score < -0.3, 'negative'),
                    else_='neutral'
                ).label('sentiment_category'),
                func.count(Feedback.id)
            )
            .where(and_(
                Feedback.created_at >= since_date,
                Feedback.sentiment_score.isnot(None)
            ))
            .group_by('sentiment_category')
        )
        by_sentiment = {row[0]: row[1] for row in sentiment_result.fetchall()}
        
        # By rating
        rating_result = await db.execute(
            select(Feedback.rating, func.count(Feedback.id))
            .where(and_(
                Feedback.created_at >= since_date,
                Feedback.rating.isnot(None)
            ))
            .group_by(Feedback.rating)
        )
        by_rating = {str(row[0]): row[1] for row in rating_result.fetchall()}
        
        # Average sentiment
        avg_sentiment_result = await db.execute(
            select(func.avg(Feedback.sentiment_score))
            .where(and_(
                Feedback.created_at >= since_date,
                Feedback.sentiment_score.isnot(None)
            ))
        )
        average_sentiment = float(avg_sentiment_result.scalar() or 0)
        
        # Recent feedback count (last 24 hours)
        recent_date = datetime.utcnow() - timedelta(hours=24)
        recent_result = await db.execute(
            select(func.count(Feedback.id)).where(Feedback.created_at >= recent_date)
        )
        recent_feedback_count = recent_result.scalar()
        
        # Trending topics (simplified)
        trending_topics = []
        if total_feedback > 0:
            # Get common categories from AI analysis
            categories_result = await db.execute(
                select(Feedback.ai_categories)
                .where(and_(
                    Feedback.created_at >= since_date,
                    Feedback.ai_categories.isnot(None)
                ))
                .limit(100)
            )
            
            category_counts = {}
            for row in categories_result.fetchall():
                if row[0]:  # ai_categories is not None
                    for category in row[0]:
                        category_counts[category] = category_counts.get(category, 0) + 1
            
            trending_topics = [
                {"topic": topic, "count": count}
                for topic, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            ]
        
        return FeedbackAnalytics(
            total_feedback=total_feedback,
            by_channel=by_channel,
            by_sentiment=by_sentiment,
            by_rating=by_rating,
            by_language={"ar": total_feedback},  # Simplified for now
            average_sentiment=average_sentiment,
            trending_topics=trending_topics,
            recent_feedback_count=recent_feedback_count
        )
        
    except Exception as e:
        logger.error(f"Error getting feedback analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics"
        )

@router.get("/search")
async def search_feedback(
    q: str = Query(..., min_length=2, description="Search query"),
    channel: Optional[FeedbackChannel] = None,
    sentiment: Optional[str] = Query(None, pattern="^(positive|negative|neutral)$"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_arabic_db_session)
):
    """Search feedback with Arabic support"""
    try:
        # Use Arabic database manager for search
        from utils.database_arabic import arabic_db_manager
        
        # Perform Arabic-aware search
        search_results = await arabic_db_manager.search_arabic_content(
            query=q,
            table="feedback",
            fields=["content"],
            limit=limit
        )
        
        return {
            "query": q,
            "results": search_results,
            "total": len(search_results)
        }
        
    except Exception as e:
        logger.error(f"Error searching feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed"
        )