"""
Survey models for Flask Arabic VoC platform
Simplified survey models using Flask-SQLAlchemy
"""

import uuid
from datetime import datetime
from enum import Enum
from app import db


class SurveyStatus(Enum):
    """Survey status options"""
    DRAFT = "draft"
    PUBLISHED = "published"
    PAUSED = "paused"
    CLOSED = "closed"
    ARCHIVED = "archived"


class QuestionType(Enum):
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


class SurveyFlask(db.Model):
    """Survey model using Flask-SQLAlchemy"""
    __tablename__ = "surveys_flask"
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False, index=True)
    short_id = db.Column(db.String(10), unique=True, nullable=True, index=True)
    
    # Basic information
    title = db.Column(db.String(200), nullable=False)
    title_ar = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    description_ar = db.Column(db.Text, nullable=True)
    
    # Survey settings
    status = db.Column(db.String(20), default=SurveyStatus.DRAFT.value, nullable=False, index=True)
    is_public = db.Column(db.Boolean, default=False, nullable=False)
    requires_login = db.Column(db.Boolean, default=False, nullable=False)
    allow_anonymous = db.Column(db.Boolean, default=True, nullable=False)
    multiple_responses = db.Column(db.Boolean, default=False, nullable=False)
    
    # Language and localization
    primary_language = db.Column(db.String(10), default="ar", nullable=False)
    rtl_enabled = db.Column(db.Boolean, default=True, nullable=False)
    
    # Display settings
    welcome_message = db.Column(db.Text, nullable=True)
    welcome_message_ar = db.Column(db.Text, nullable=True)
    thank_you_message = db.Column(db.Text, nullable=True)
    thank_you_message_ar = db.Column(db.Text, nullable=True)
    
    # Timing and scheduling
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    estimated_duration = db.Column(db.Integer, nullable=True)
    
    # User association (using Replit Auth)
    created_by = db.Column(db.String, nullable=False)  # Reference to User.id without FK constraint for now
    
    # Analytics and metrics
    response_count = db.Column(db.Integer, default=0, nullable=False)
    completion_rate = db.Column(db.Float, default=0.0, nullable=False)
    average_duration = db.Column(db.Float, nullable=True)
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    questions = db.relationship("QuestionFlask", back_populates="survey", cascade="all, delete-orphan")
    responses = db.relationship("ResponseFlask", back_populates="survey")
    
    def __repr__(self):
        return f"<SurveyFlask(id={self.id}, title='{self.title}', status='{self.status}')>"
    
    @property
    def public_url(self):
        """Generate public survey URL"""
        if self.short_id:
            return f"/s/{self.short_id}"
        return f"/survey/{self.uuid}"
    
    @property
    def display_title(self):
        """Get survey title in primary language"""
        if self.primary_language == "ar" and self.title_ar:
            return self.title_ar
        return self.title
    
    @property
    def display_description(self):
        """Get survey description in primary language"""
        if self.primary_language == "ar" and self.description_ar:
            return self.description_ar
        return self.description or ""
    
    @property
    def is_active(self):
        """Check if survey is currently active"""
        if self.status != SurveyStatus.PUBLISHED.value:
            return False
        
        now = datetime.utcnow()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        
        return True
    
    def generate_short_id(self):
        """Generate a unique short ID for easy sharing"""
        import random
        import string
        
        while True:
            short_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            existing = SurveyFlask.query.filter_by(short_id=short_id).first()
            if not existing:
                self.short_id = short_id
                break
        return short_id


class QuestionFlask(db.Model):
    """Question model using Flask-SQLAlchemy"""
    __tablename__ = "questions_flask"
    
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey("surveys_flask.id"), nullable=False)
    
    # Question content
    text = db.Column(db.Text, nullable=False)
    text_ar = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    description_ar = db.Column(db.Text, nullable=True)
    
    # Question settings
    type = db.Column(db.String(20), nullable=False)
    is_required = db.Column(db.Boolean, default=False, nullable=False)
    order_index = db.Column(db.Integer, nullable=False, default=0)
    
    # Display settings
    rtl_enabled = db.Column(db.Boolean, default=True, nullable=False)
    show_description = db.Column(db.Boolean, default=True, nullable=False)
    
    # Question configuration (JSON stored as text)
    options = db.Column(db.Text, nullable=True)  # JSON string
    validation_rules = db.Column(db.Text, nullable=True)  # JSON string
    
    # Rating/Scale specific
    min_value = db.Column(db.Integer, nullable=True)
    max_value = db.Column(db.Integer, nullable=True)
    step_value = db.Column(db.Integer, nullable=True)
    scale_labels = db.Column(db.Text, nullable=True)  # JSON string
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    survey = db.relationship("SurveyFlask", back_populates="questions")
    question_responses = db.relationship("QuestionResponseFlask", back_populates="question")
    
    def __repr__(self):
        return f"<QuestionFlask(id={self.id}, survey_id={self.survey_id}, type='{self.type}')>"
    
    @property
    def display_text(self):
        """Get question text in appropriate language"""
        if self.survey.primary_language == "ar" and self.text_ar:
            return self.text_ar
        return self.text
    
    @property
    def display_description(self):
        """Get question description in appropriate language"""
        if self.survey.primary_language == "ar" and self.description_ar:
            return self.description_ar
        return self.description or ""


class ResponseFlask(db.Model):
    """Response model using Flask-SQLAlchemy"""
    __tablename__ = "responses_flask"
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False, index=True)
    survey_id = db.Column(db.Integer, db.ForeignKey("surveys_flask.id"), nullable=False)
    
    # Respondent information
    user_id = db.Column(db.String, nullable=True)  # Reference to User.id, null for anonymous
    respondent_email = db.Column(db.String(255), nullable=True)
    respondent_name = db.Column(db.String(200), nullable=True)
    respondent_name_ar = db.Column(db.Text, nullable=True)
    
    # Response data (JSON stored as text)
    answers = db.Column(db.Text, nullable=False)  # JSON string
    language_used = db.Column(db.String(10), default="ar", nullable=False)
    
    # Completion tracking
    is_complete = db.Column(db.Boolean, default=False, nullable=False)
    completion_percentage = db.Column(db.Float, default=0.0, nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    duration_minutes = db.Column(db.Float, nullable=True)
    
    # Technical metadata
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    device_type = db.Column(db.String(50), nullable=True)
    browser = db.Column(db.String(100), nullable=True)
    
    # Analytics and sentiment
    sentiment_score = db.Column(db.Float, nullable=True)
    confidence_score = db.Column(db.Float, nullable=True)
    keywords = db.Column(db.Text, nullable=True)  # JSON string
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    survey = db.relationship("SurveyFlask", back_populates="responses")
    question_responses = db.relationship("QuestionResponseFlask", back_populates="response")
    
    def __repr__(self):
        return f"<ResponseFlask(id={self.id}, survey_id={self.survey_id}, complete={self.is_complete})>"


class QuestionResponseFlask(db.Model):
    """Individual question response using Flask-SQLAlchemy"""
    __tablename__ = "question_responses_flask"
    
    id = db.Column(db.Integer, primary_key=True)
    response_id = db.Column(db.Integer, db.ForeignKey("responses_flask.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions_flask.id"), nullable=False)
    
    # Response data
    answer_text = db.Column(db.Text, nullable=True)
    answer_number = db.Column(db.Float, nullable=True)
    answer_json = db.Column(db.Text, nullable=True)  # JSON string
    answer_boolean = db.Column(db.Boolean, nullable=True)
    
    # Response metadata
    is_skipped = db.Column(db.Boolean, default=False, nullable=False)
    time_spent_seconds = db.Column(db.Integer, nullable=True)
    
    # Sentiment analysis for text responses
    sentiment_score = db.Column(db.Float, nullable=True)
    confidence_score = db.Column(db.Float, nullable=True)
    extracted_keywords = db.Column(db.Text, nullable=True)  # JSON string
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    response = db.relationship("ResponseFlask", back_populates="question_responses")
    question = db.relationship("QuestionFlask", back_populates="question_responses")
    
    def __repr__(self):
        return f"<QuestionResponseFlask(id={self.id}, question_id={self.question_id})>"