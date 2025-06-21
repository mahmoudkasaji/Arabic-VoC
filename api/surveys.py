"""
Survey management API endpoints for Arabic VoC platform
Comprehensive survey CRUD operations with Arabic content support
"""

import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from pydantic import BaseModel, Field, validator

from models.auth import User
from models.survey import Survey, Question, QuestionType, SurveyStatus
from utils.database_arabic import get_arabic_db_session
from api.auth import get_current_user
from utils.auth import name_validator
from utils.security import validate_feedback_input

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/surveys", tags=["surveys"])

# Pydantic models
class QuestionCreate(BaseModel):
    """Question creation model with Arabic support"""
    text: str = Field(..., min_length=5, max_length=1000)
    text_ar: Optional[str] = Field(None, max_length=1000)
    description: Optional[str] = Field(None, max_length=500)
    description_ar: Optional[str] = Field(None, max_length=500)
    type: QuestionType = Field(...)
    is_required: bool = Field(False)
    order_index: int = Field(0, ge=0)
    rtl_enabled: bool = Field(True)
    min_value: Optional[int] = Field(None)
    max_value: Optional[int] = Field(None)
    options: Optional[dict] = Field(None)
    
    @validator('text_ar')
    def validate_arabic_text(cls, v):
        if v and not name_validator.is_arabic_text(v):
            raise ValueError('Question text must contain Arabic characters')
        return v

class SurveyCreate(BaseModel):
    """Survey creation model with bilingual support"""
    title: str = Field(..., min_length=3, max_length=200)
    title_ar: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    description_ar: Optional[str] = Field(None, max_length=2000)
    
    # Survey settings
    is_public: bool = Field(False)
    requires_login: bool = Field(False)
    allow_anonymous: bool = Field(True)
    multiple_responses: bool = Field(False)
    
    # Language settings
    primary_language: str = Field("ar", pattern="^(ar|en)$")
    supported_languages: List[str] = Field(["ar", "en"])
    rtl_enabled: bool = Field(True)
    
    # Display messages
    welcome_message: Optional[str] = Field(None, max_length=1000)
    welcome_message_ar: Optional[str] = Field(None, max_length=1000)
    thank_you_message: Optional[str] = Field(None, max_length=1000)
    thank_you_message_ar: Optional[str] = Field(None, max_length=1000)
    
    # Timing
    start_date: Optional[datetime] = Field(None)
    end_date: Optional[datetime] = Field(None)
    estimated_duration: Optional[int] = Field(None, ge=1, le=180)
    
    @validator('title_ar')
    def validate_arabic_title(cls, v):
        if v and not name_validator.is_arabic_text(v):
            raise ValueError('Arabic title must contain Arabic characters')
        return v
    
    @validator('end_date')
    def validate_dates(cls, v, values):
        if v and 'start_date' in values and values['start_date']:
            if v <= values['start_date']:
                raise ValueError('End date must be after start date')
        return v

class SurveyUpdate(BaseModel):
    """Survey update model"""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    title_ar: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    description_ar: Optional[str] = Field(None, max_length=2000)
    status: Optional[SurveyStatus] = Field(None)
    is_public: Optional[bool] = Field(None)
    requires_login: Optional[bool] = Field(None)
    allow_anonymous: Optional[bool] = Field(None)
    multiple_responses: Optional[bool] = Field(None)
    start_date: Optional[datetime] = Field(None)
    end_date: Optional[datetime] = Field(None)

class SurveyResponse(BaseModel):
    """Survey response model"""
    id: int
    uuid: str
    title: str
    title_ar: Optional[str]
    description: Optional[str]
    description_ar: Optional[str]
    status: str
    is_public: bool
    primary_language: str
    supported_languages: List[str]
    rtl_enabled: bool
    response_count: int
    completion_rate: float
    created_at: datetime
    published_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class QuestionResponse(BaseModel):
    """Question response model"""
    id: int
    text: str
    text_ar: Optional[str]
    description: Optional[str]
    description_ar: Optional[str]
    type: str
    is_required: bool
    order_index: int
    rtl_enabled: bool
    min_value: Optional[int]
    max_value: Optional[int]
    options: Optional[dict]
    
    class Config:
        from_attributes = True

class SurveyDetailResponse(SurveyResponse):
    """Detailed survey response with questions"""
    questions: List[QuestionResponse]

# API Endpoints
@router.post("/", response_model=SurveyResponse, status_code=status.HTTP_201_CREATED)
async def create_survey(
    survey_data: SurveyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_arabic_db_session)
):
    """Create new survey with Arabic support"""
    try:
        # Validate organization access
        if not current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must belong to an organization to create surveys"
            )
        
        # Create survey
        survey = Survey(
            title=survey_data.title,
            title_ar=survey_data.title_ar,
            description=survey_data.description,
            description_ar=survey_data.description_ar,
            is_public=survey_data.is_public,
            requires_login=survey_data.requires_login,
            allow_anonymous=survey_data.allow_anonymous,
            multiple_responses=survey_data.multiple_responses,
            primary_language=survey_data.primary_language,
            supported_languages=survey_data.supported_languages,
            rtl_enabled=survey_data.rtl_enabled,
            welcome_message=survey_data.welcome_message,
            welcome_message_ar=survey_data.welcome_message_ar,
            thank_you_message=survey_data.thank_you_message,
            thank_you_message_ar=survey_data.thank_you_message_ar,
            start_date=survey_data.start_date,
            end_date=survey_data.end_date,
            estimated_duration=survey_data.estimated_duration,
            organization_id=current_user.organization_id,
            created_by=current_user.id
        )
        
        db.add(survey)
        await db.commit()
        await db.refresh(survey)
        
        logger.info(f"Survey created: {survey.id} by user {current_user.id}")
        return SurveyResponse.model_validate(survey)
        
    except Exception as e:
        logger.error(f"Error creating survey: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create survey"
        )

@router.get("/", response_model=List[SurveyResponse])
async def list_surveys(
    status_filter: Optional[SurveyStatus] = Query(None, alias="status"),
    public_only: bool = Query(False),
    search: Optional[str] = Query(None, min_length=2),
    language: Optional[str] = Query(None, regex="^(ar|en)$"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_arabic_db_session)
):
    """List surveys with filtering and search"""
    try:
        query = select(Survey)
        
        # Base filter - user's organization surveys or public surveys
        if public_only:
            query = query.where(Survey.is_public == True)
        else:
            query = query.where(
                or_(
                    Survey.organization_id == current_user.organization_id,
                    Survey.is_public == True
                )
            )
        
        # Apply filters
        if status_filter:
            query = query.where(Survey.status == status_filter)
        
        if language:
            if language == "ar":
                query = query.where(Survey.title_ar.isnot(None))
            else:
                query = query.where(Survey.primary_language == language)
        
        # Search functionality
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Survey.title.ilike(search_term),
                    Survey.title_ar.ilike(search_term),
                    Survey.description.ilike(search_term),
                    Survey.description_ar.ilike(search_term)
                )
            )
        
        # Pagination and ordering
        query = query.order_by(Survey.created_at.desc())
        query = query.offset(offset).limit(limit)
        
        result = await db.execute(query)
        surveys = result.scalars().all()
        
        return [SurveyResponse.model_validate(survey) for survey in surveys]
        
    except Exception as e:
        logger.error(f"Error listing surveys: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve surveys"
        )

@router.get("/{survey_id}", response_model=SurveyDetailResponse)
async def get_survey(
    survey_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_arabic_db_session)
):
    """Get survey details with questions"""
    try:
        # Get survey with questions
        result = await db.execute(
            select(Survey)
            .where(Survey.id == survey_id)
        )
        survey = result.scalar_one_or_none()
        
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Survey not found"
            )
        
        # Check access permissions
        if not survey.is_public and survey.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this survey"
            )
        
        # Get questions
        questions_result = await db.execute(
            select(Question)
            .where(Question.survey_id == survey_id)
            .order_by(Question.order_index)
        )
        questions = questions_result.scalars().all()
        
        # Build response
        survey_dict = SurveyResponse.model_validate(survey).model_dump()
        survey_dict["questions"] = [
            QuestionResponse.model_validate(q) for q in questions
        ]
        
        return SurveyDetailResponse(**survey_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting survey {survey_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve survey"
        )

@router.put("/{survey_id}", response_model=SurveyResponse)
async def update_survey(
    survey_id: int,
    survey_data: SurveyUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_arabic_db_session)
):
    """Update survey"""
    try:
        # Get survey
        result = await db.execute(
            select(Survey).where(Survey.id == survey_id)
        )
        survey = result.scalar_one_or_none()
        
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Survey not found"
            )
        
        # Check permissions
        if survey.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this survey"
            )
        
        # Update fields
        update_data = survey_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(survey, field, value)
        
        # Set published date if status changed to published
        if survey_data.status == SurveyStatus.PUBLISHED and not survey.published_at:
            survey.published_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(survey)
        
        logger.info(f"Survey updated: {survey_id} by user {current_user.id}")
        return SurveyResponse.model_validate(survey)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating survey {survey_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update survey"
        )

@router.delete("/{survey_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_survey(
    survey_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_arabic_db_session)
):
    """Delete survey"""
    try:
        # Get survey
        result = await db.execute(
            select(Survey).where(Survey.id == survey_id)
        )
        survey = result.scalar_one_or_none()
        
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Survey not found"
            )
        
        # Check permissions
        if survey.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this survey"
            )
        
        # Prevent deletion of surveys with responses
        if survey.response_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete survey with existing responses"
            )
        
        await db.delete(survey)
        await db.commit()
        
        logger.info(f"Survey deleted: {survey_id} by user {current_user.id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting survey {survey_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete survey"
        )

@router.post("/{survey_id}/questions", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def add_question(
    survey_id: int,
    question_data: QuestionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_arabic_db_session)
):
    """Add question to survey"""
    try:
        # Verify survey access
        result = await db.execute(
            select(Survey).where(Survey.id == survey_id)
        )
        survey = result.scalar_one_or_none()
        
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Survey not found"
            )
        
        if survey.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this survey"
            )
        
        # Create question
        question = Question(
            survey_id=survey_id,
            text=question_data.text,
            text_ar=question_data.text_ar,
            description=question_data.description,
            description_ar=question_data.description_ar,
            type=question_data.type,
            is_required=question_data.is_required,
            order_index=question_data.order_index,
            rtl_enabled=question_data.rtl_enabled,
            min_value=question_data.min_value,
            max_value=question_data.max_value,
            options=question_data.options
        )
        
        db.add(question)
        await db.commit()
        await db.refresh(question)
        
        logger.info(f"Question added to survey {survey_id} by user {current_user.id}")
        return QuestionResponse.model_validate(question)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding question to survey {survey_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add question"
        )

@router.get("/{survey_id}/analytics")
async def get_survey_analytics(
    survey_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_arabic_db_session)
):
    """Get survey analytics"""
    try:
        # Verify survey access
        result = await db.execute(
            select(Survey).where(Survey.id == survey_id)
        )
        survey = result.scalar_one_or_none()
        
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Survey not found"
            )
        
        if survey.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this survey"
            )
        
        # Get analytics data
        from sqlalchemy import func
        from models.survey import Response as SurveyResponse
        
        # Basic stats
        stats_result = await db.execute(
            select(
                func.count(SurveyResponse.id).label('total_responses'),
                func.count(SurveyResponse.id).filter(SurveyResponse.is_complete == True).label('completed_responses'),
                func.avg(SurveyResponse.duration_minutes).label('avg_duration'),
                func.avg(SurveyResponse.sentiment_score).label('avg_sentiment')
            ).where(SurveyResponse.survey_id == survey_id)
        )
        stats = stats_result.fetchone()
        
        # Language distribution
        lang_result = await db.execute(
            select(
                SurveyResponse.language_used,
                func.count(SurveyResponse.id).label('count')
            )
            .where(SurveyResponse.survey_id == survey_id)
            .group_by(SurveyResponse.language_used)
        )
        language_distribution = {row.language_used: row.count for row in lang_result.fetchall()}
        
        return {
            "survey_id": survey_id,
            "total_responses": stats.total_responses or 0,
            "completed_responses": stats.completed_responses or 0,
            "completion_rate": (stats.completed_responses / max(stats.total_responses, 1)) * 100 if stats.total_responses else 0,
            "average_duration_minutes": float(stats.avg_duration) if stats.avg_duration else 0,
            "average_sentiment": float(stats.avg_sentiment) if stats.avg_sentiment else 0,
            "language_distribution": language_distribution
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting survey analytics {survey_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics"
        )