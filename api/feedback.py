"""
Feedback API endpoints for multi-channel feedback collection
Supports Arabic text processing and real-time analytics
"""

import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession

from database_models import Feedback, FeedbackChannel, FeedbackStatus
from utils.database import get_db
from utils.arabic_processor import process_arabic_text, extract_sentiment
from utils.openai_client import analyze_arabic_feedback

logger = logging.getLogger(__name__)
router = APIRouter()

class FeedbackCreate(BaseModel):
    """Pydantic model for feedback creation"""
    content: str = Field(..., min_length=1, max_length=5000, description="Feedback content in Arabic")
    channel: FeedbackChannel = Field(..., description="Channel through which feedback was received")
    customer_email: Optional[str] = Field(None, description="Customer email if provided")
    customer_phone: Optional[str] = Field(None, description="Customer phone if provided")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Customer rating 1-5")
    channel_metadata: Optional[dict] = Field(default_factory=dict, description="Additional metadata")

    @validator('content')
    def validate_arabic_content(cls, v):
        """Ensure content contains valid text"""
        if not v.strip():
            raise ValueError('محتوى التعليق لا يمكن أن يكون فارغاً')
        return v.strip()

class FeedbackResponse(BaseModel):
    """Pydantic model for feedback response"""
    id: int
    content: str
    processed_content: str
    channel: FeedbackChannel
    status: FeedbackStatus
    sentiment_score: float
    confidence_score: float
    ai_summary: Optional[str]
    customer_email: Optional[str]
    rating: Optional[int]
    created_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True

class FeedbackFilter(BaseModel):
    """Pydantic model for feedback filtering"""
    channel: Optional[FeedbackChannel] = None
    status: Optional[FeedbackStatus] = None
    min_sentiment: Optional[float] = Field(None, ge=-1.0, le=1.0)
    max_sentiment: Optional[float] = Field(None, ge=-1.0, le=1.0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)

async def process_feedback_background(feedback_id: int, db: AsyncSession):
    """Background task to process feedback with AI analysis"""
    try:
        # Get feedback from database
        result = await db.execute(
            "SELECT * FROM feedback WHERE id = :id",
            {"id": feedback_id}
        )
        feedback_data = result.fetchone()
        
        if not feedback_data:
            logger.error(f"Feedback {feedback_id} not found for processing")
            return

        # Process Arabic text
        processed_text = process_arabic_text(feedback_data.content)
        
        # Extract sentiment
        sentiment_data = extract_sentiment(processed_text)
        
        # Get AI analysis
        ai_analysis = analyze_arabic_feedback(processed_text)
        
        # Update feedback with processed data
        await db.execute(
            """
            UPDATE feedback 
            SET processed_content = :processed_content,
                sentiment_score = :sentiment_score,
                confidence_score = :confidence_score,
                ai_summary = :ai_summary,
                status = :status,
                processed_at = :processed_at
            WHERE id = :id
            """,
            {
                "id": feedback_id,
                "processed_content": processed_text,
                "sentiment_score": sentiment_data["sentiment"],
                "confidence_score": sentiment_data["confidence"],
                "ai_summary": ai_analysis["summary"],
                "status": FeedbackStatus.PROCESSED,
                "processed_at": datetime.utcnow()
            }
        )
        await db.commit()
        
        logger.info(f"Successfully processed feedback {feedback_id}")
        
    except Exception as e:
        logger.error(f"Error processing feedback {feedback_id}: {str(e)}")
        await db.rollback()

@router.post("/submit", response_model=FeedbackResponse)
async def submit_feedback(
    feedback: FeedbackCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Submit new feedback for processing"""
    try:
        # Create new feedback record
        new_feedback = Feedback(
            content=feedback.content,
            channel=feedback.channel,
            customer_email=feedback.customer_email,
            customer_phone=feedback.customer_phone,
            rating=feedback.rating,
            channel_metadata=feedback.channel_metadata,
            status=FeedbackStatus.PENDING,
            created_at=datetime.utcnow()
        )
        
        db.add(new_feedback)
        await db.commit()
        await db.refresh(new_feedback)
        
        # Schedule background processing
        background_tasks.add_task(process_feedback_background, new_feedback.id, db)
        
        logger.info(f"New feedback submitted: {new_feedback.id}")
        
        return FeedbackResponse.from_orm(new_feedback)
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="خطأ في إرسال التعليق")

@router.get("/list", response_model=List[FeedbackResponse])
async def list_feedback(
    filters: FeedbackFilter = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """List feedback with optional filtering"""
    try:
        # Build query with filters
        query_parts = ["SELECT * FROM feedback WHERE 1=1"]
        params = {}
        
        if filters.channel:
            query_parts.append("AND channel = :channel")
            params["channel"] = filters.channel
            
        if filters.status:
            query_parts.append("AND status = :status")
            params["status"] = filters.status
            
        if filters.min_sentiment is not None:
            query_parts.append("AND sentiment_score >= :min_sentiment")
            params["min_sentiment"] = filters.min_sentiment
            
        if filters.max_sentiment is not None:
            query_parts.append("AND sentiment_score <= :max_sentiment")
            params["max_sentiment"] = filters.max_sentiment
            
        if filters.start_date:
            query_parts.append("AND created_at >= :start_date")
            params["start_date"] = filters.start_date
            
        if filters.end_date:
            query_parts.append("AND created_at <= :end_date")
            params["end_date"] = filters.end_date
        
        query_parts.append("ORDER BY created_at DESC")
        query_parts.append("LIMIT :limit OFFSET :offset")
        params["limit"] = filters.limit
        params["offset"] = filters.offset
        
        query = " ".join(query_parts)
        
        result = await db.execute(query, params)
        feedback_list = result.fetchall()
        
        return [FeedbackResponse.from_orm(feedback) for feedback in feedback_list]
        
    except Exception as e:
        logger.error(f"Error listing feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="خطأ في استرجاع التعليقات")

@router.get("/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback(
    feedback_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get specific feedback by ID"""
    try:
        result = await db.execute(
            "SELECT * FROM feedback WHERE id = :id",
            {"id": feedback_id}
        )
        feedback = result.fetchone()
        
        if not feedback:
            raise HTTPException(status_code=404, detail="التعليق غير موجود")
            
        return FeedbackResponse.from_orm(feedback)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feedback {feedback_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="خطأ في استرجاع التعليق")

@router.delete("/{feedback_id}")
async def delete_feedback(
    feedback_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete specific feedback"""
    try:
        result = await db.execute(
            "DELETE FROM feedback WHERE id = :id RETURNING id",
            {"id": feedback_id}
        )
        deleted = result.fetchone()
        
        if not deleted:
            raise HTTPException(status_code=404, detail="التعليق غير موجود")
            
        await db.commit()
        
        logger.info(f"Feedback {feedback_id} deleted")
        return {"message": "تم حذف التعليق بنجاح", "id": feedback_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting feedback {feedback_id}: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="خطأ في حذف التعليق")
