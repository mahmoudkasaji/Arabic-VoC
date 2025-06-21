"""
Survey models for Arabic VoC platform
Survey, Question, Response models with comprehensive Arabic support
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Float, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func
import enum
import uuid

Base = declarative_base()

class SurveyStatus(str, enum.Enum):
    """Survey status options"""
    DRAFT = "draft"
    PUBLISHED = "published"
    PAUSED = "paused"
    CLOSED = "closed"
    ARCHIVED = "archived"

class QuestionType(str, enum.Enum):
    """Question types for surveys"""
    TEXT = "text"
    TEXTAREA = "textarea"
    RATING = "rating"
    MULTIPLE_CHOICE = "multiple_choice"
    CHECKBOX = "checkbox"
    DROPDOWN = "dropdown"
    SLIDER = "slider"
    DATE = "date"
    EMAIL = "email"
    PHONE = "phone"
    NPS = "nps"  # Net Promoter Score

class Survey(Base):
    """
    Survey model with bilingual Arabic support
    Comprehensive survey management with Arabic content
    """
    __tablename__ = "surveys"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    
    # Basic information
    title = Column(String(200), nullable=False)
    title_ar = Column(Text, nullable=True, comment="Arabic survey title")
    description = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True, comment="Arabic survey description")
    
    # Survey settings
    status = Column(String(20), default=SurveyStatus.DRAFT, nullable=False, index=True)
    is_public = Column(Boolean, default=False, nullable=False)
    requires_login = Column(Boolean, default=False, nullable=False)
    allow_anonymous = Column(Boolean, default=True, nullable=False)
    multiple_responses = Column(Boolean, default=False, nullable=False)
    
    # Language and localization
    primary_language = Column(String(10), default="ar", nullable=False)
    supported_languages = Column(JSONB, default=["ar", "en"], nullable=False)
    rtl_enabled = Column(Boolean, default=True, nullable=False)
    
    # Display settings
    welcome_message = Column(Text, nullable=True)
    welcome_message_ar = Column(Text, nullable=True, comment="Arabic welcome message")
    thank_you_message = Column(Text, nullable=True)
    thank_you_message_ar = Column(Text, nullable=True, comment="Arabic thank you message")
    
    # Timing and scheduling
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    estimated_duration = Column(Integer, nullable=True, comment="Estimated duration in minutes")
    
    # Organization and ownership
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Analytics and metrics
    response_count = Column(Integer, default=0, nullable=False)
    completion_rate = Column(Float, default=0.0, nullable=False)
    average_duration = Column(Float, nullable=True, comment="Average completion time in minutes")
    
    # Audit fields
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    published_at = Column(DateTime, nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="surveys")
    creator = relationship("User", foreign_keys=[created_by])
    questions = relationship("Question", back_populates="survey", cascade="all, delete-orphan")
    responses = relationship("Response", back_populates="survey")
    
    def __repr__(self):
        return f"<Survey(id={self.id}, title='{self.title}', status='{self.status}')>"
    
    @property
    def display_title(self) -> str:
        """Get survey title in primary language"""
        if self.primary_language == "ar" and self.title_ar:
            return self.title_ar
        return self.title
    
    @property
    def display_description(self) -> str:
        """Get survey description in primary language"""
        if self.primary_language == "ar" and self.description_ar:
            return self.description_ar
        return self.description or ""
    
    @property
    def is_active(self) -> bool:
        """Check if survey is currently active"""
        if self.status != SurveyStatus.PUBLISHED:
            return False
        
        now = datetime.utcnow()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        
        return True

class Question(Base):
    """
    Question model with Arabic text and RTL support
    Flexible question types with bilingual content
    """
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id"), nullable=False)
    
    # Question content
    text = Column(Text, nullable=False)
    text_ar = Column(Text, nullable=True, comment="Arabic question text")
    description = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True, comment="Arabic question description")
    
    # Question settings
    type = Column(String(20), nullable=False)
    is_required = Column(Boolean, default=False, nullable=False)
    order_index = Column(Integer, nullable=False, default=0)
    
    # Display settings
    rtl_enabled = Column(Boolean, default=True, nullable=False)
    show_description = Column(Boolean, default=True, nullable=False)
    
    # Question configuration
    options = Column(JSONB, nullable=True, comment="Question options for multiple choice, etc.")
    validation_rules = Column(JSONB, nullable=True, comment="Validation rules for the question")
    display_logic = Column(JSONB, nullable=True, comment="Conditional display logic")
    
    # Rating/Scale specific
    min_value = Column(Integer, nullable=True)
    max_value = Column(Integer, nullable=True)
    step_value = Column(Integer, nullable=True)
    scale_labels = Column(JSONB, nullable=True, comment="Labels for scale endpoints")
    
    # Audit fields
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    survey = relationship("Survey", back_populates="questions")
    question_responses = relationship("QuestionResponse", back_populates="question")
    
    def __repr__(self):
        return f"<Question(id={self.id}, survey_id={self.survey_id}, type='{self.type}')>"
    
    @property
    def display_text(self) -> str:
        """Get question text in appropriate language"""
        if self.survey.primary_language == "ar" and self.text_ar:
            return self.text_ar
        return self.text
    
    @property
    def display_description(self) -> str:
        """Get question description in appropriate language"""
        if self.survey.primary_language == "ar" and self.description_ar:
            return self.description_ar
        return self.description or ""

class Response(Base):
    """
    Response model with JSONB for Arabic responses
    Comprehensive response tracking with analytics
    """
    __tablename__ = "responses"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id"), nullable=False)
    
    # Respondent information
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null for anonymous
    respondent_email = Column(String(255), nullable=True)
    respondent_name = Column(String(200), nullable=True)
    respondent_name_ar = Column(Text, nullable=True, comment="Arabic respondent name")
    
    # Response data
    answers = Column(JSONB, nullable=False, comment="All question answers in JSONB format")
    language_used = Column(String(10), default="ar", nullable=False)
    
    # Completion tracking
    is_complete = Column(Boolean, default=False, nullable=False)
    completion_percentage = Column(Float, default=0.0, nullable=False)
    started_at = Column(DateTime, default=func.now(), nullable=False)
    completed_at = Column(DateTime, nullable=True)
    duration_minutes = Column(Float, nullable=True)
    
    # Technical metadata
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    device_type = Column(String(50), nullable=True)
    browser = Column(String(100), nullable=True)
    
    # Analytics and sentiment
    sentiment_score = Column(Float, nullable=True, comment="Overall sentiment score -1 to 1")
    confidence_score = Column(Float, nullable=True, comment="AI confidence score 0 to 1")
    keywords = Column(JSONB, nullable=True, comment="Extracted keywords from responses")
    
    # Audit fields
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    survey = relationship("Survey", back_populates="responses")
    user = relationship("User")
    question_responses = relationship("QuestionResponse", back_populates="response")
    
    def __repr__(self):
        return f"<Response(id={self.id}, survey_id={self.survey_id}, complete={self.is_complete})>"
    
    @property
    def respondent_display_name(self) -> str:
        """Get respondent name in appropriate language"""
        if self.language_used == "ar" and self.respondent_name_ar:
            return self.respondent_name_ar
        return self.respondent_name or "Anonymous"

class QuestionResponse(Base):
    """
    Individual question response with Arabic content support
    Links responses to specific questions with detailed tracking
    """
    __tablename__ = "question_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("responses.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    
    # Response data
    answer_text = Column(Text, nullable=True, comment="Text answer with Arabic support")
    answer_number = Column(Float, nullable=True, comment="Numeric answer for ratings/scales")
    answer_json = Column(JSONB, nullable=True, comment="Complex answer data")
    answer_boolean = Column(Boolean, nullable=True, comment="Boolean answer for yes/no questions")
    
    # Response metadata
    is_skipped = Column(Boolean, default=False, nullable=False)
    time_spent_seconds = Column(Integer, nullable=True)
    
    # Sentiment analysis for text responses
    sentiment_score = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    extracted_keywords = Column(JSONB, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    response = relationship("Response", back_populates="question_responses")
    question = relationship("Question", back_populates="question_responses")
    
    def __repr__(self):
        return f"<QuestionResponse(id={self.id}, question_id={self.question_id})>"

# Indexes for performance optimization
Index('idx_surveys_status_org', Survey.status, Survey.organization_id)
Index('idx_surveys_dates', Survey.start_date, Survey.end_date)
Index('idx_questions_survey_order', Question.survey_id, Question.order_index)
Index('idx_responses_survey_complete', Response.survey_id, Response.is_complete)
Index('idx_responses_created_at', Response.created_at)
Index('idx_question_responses_question', QuestionResponse.question_id)

# GIN indexes for JSONB columns (Arabic content search)
Index('idx_questions_options_gin', Question.options, postgresql_using='gin')
Index('idx_responses_answers_gin', Response.answers, postgresql_using='gin')
Index('idx_responses_keywords_gin', Response.keywords, postgresql_using='gin')
Index('idx_question_responses_answer_gin', QuestionResponse.answer_json, postgresql_using='gin')