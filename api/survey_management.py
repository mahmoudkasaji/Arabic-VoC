"""
Survey Management API for Arabic VoC Platform
Handles survey CRUD operations, templates, and dashboard data
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
from flask import request, jsonify
from sqlalchemy import desc, func, and_

from app import app, db
from models.survey_flask import SurveyFlask as Survey, QuestionFlask as Question, SurveyStatus, QuestionType

logger = logging.getLogger(__name__)

@app.route('/api/surveys/dashboard', methods=['GET'])
def get_survey_dashboard():
    """Get dashboard data for survey management"""
    try:
        # Get surveys with basic stats
        surveys = db.session.query(
            Survey.id,
            Survey.title,
            Survey.title_ar,
            Survey.description,
            Survey.description_ar,
            Survey.status,
            Survey.question_count,
            Survey.response_count,
            Survey.updated_at,
            Survey.created_at,
            Survey.is_template
        ).filter(
            Survey.is_template == False
        ).order_by(desc(Survey.updated_at)).limit(10).all()
        
        # Format survey data
        survey_list = []
        for survey in surveys:
            # Calculate days since update
            days_ago = (datetime.utcnow() - survey.updated_at).days if survey.updated_at else 0
            
            survey_data = {
                'id': survey.id,
                'title': survey.title_ar or survey.title or 'استطلاع بدون عنوان',
                'title_en': survey.title,
                'description': survey.description_ar or survey.description,
                'status': survey.status.value,
                'status_display': get_status_display(survey.status),
                'question_count': survey.question_count or 0,
                'response_count': survey.response_count or 0,
                'updated_days_ago': days_ago,
                'created_at': survey.created_at.isoformat() if survey.created_at else None,
                'updated_at': survey.updated_at.isoformat() if survey.updated_at else None
            }
            survey_list.append(survey_data)
        
        # Get templates
        templates = db.session.query(Survey).filter(
            Survey.is_template == True
        ).order_by(Survey.title_ar).all()
        
        template_list = []
        for template in templates:
            template_data = {
                'id': template.id,
                'title': template.title_ar or template.title,
                'title_en': template.title,
                'description': template.description_ar or template.description,
                'category': template.template_category or 'عام',
                'question_count': template.question_count or 0
            }
            template_list.append(template_data)
        
        # Get summary statistics
        total_surveys = db.session.query(Survey).filter(Survey.is_template == False).count()
        active_surveys = db.session.query(Survey).filter(
            and_(Survey.is_template == False, Survey.status == SurveyStatus.ACTIVE)
        ).count()
        draft_surveys = db.session.query(Survey).filter(
            and_(Survey.is_template == False, Survey.status == SurveyStatus.DRAFT)
        ).count()
        
        return jsonify({
            'surveys': survey_list,
            'templates': template_list,
            'statistics': {
                'total_surveys': total_surveys,
                'active_surveys': active_surveys,
                'draft_surveys': draft_surveys,
                'templates_count': len(template_list)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting survey dashboard: {e}")
        return jsonify({'error': 'حدث خطأ في جلب بيانات الاستطلاعات'}), 500

@app.route('/api/surveys', methods=['POST'])
def create_survey():
    """Create a new survey"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'لا توجد بيانات'}), 400
        
        # Create new survey
        survey = Survey(
            title=data.get('title'),
            title_ar=data.get('title_ar'),
            description=data.get('description'),
            description_ar=data.get('description_ar'),
            status=SurveyStatus.DRAFT,
            primary_language=data.get('primary_language', 'ar'),
            supported_languages=data.get('supported_languages', ['ar', 'en']),
            rtl_enabled=data.get('rtl_enabled', True),
            is_public=data.get('is_public', False),
            requires_login=data.get('requires_login', False),
            allow_anonymous=data.get('allow_anonymous', True),
            multiple_responses=data.get('multiple_responses', False),
            question_count=0
        )
        
        db.session.add(survey)
        db.session.commit()
        
        # Add questions if provided
        questions = data.get('questions', [])
        question_count = 0
        
        for question_data in questions:
            question = Question(
                survey_id=survey.id,
                text=question_data.get('text'),
                text_ar=question_data.get('text_ar'),
                description=question_data.get('description'),
                description_ar=question_data.get('description_ar'),
                type=QuestionType(question_data.get('type', 'text')),
                is_required=question_data.get('is_required', False),
                order_index=question_data.get('order_index', question_count),
                options=question_data.get('options'),
                validation_rules=question_data.get('validation_rules'),
                display_logic=question_data.get('display_logic')
            )
            db.session.add(question)
            question_count += 1
        
        # Update question count
        survey.question_count = question_count
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم إنشاء الاستطلاع بنجاح',
            'survey_id': survey.id,
            'survey': {
                'id': survey.id,
                'title': survey.title_ar or survey.title,
                'status': survey.status.value,
                'question_count': survey.question_count
            }
        })
        
    except Exception as e:
        logger.error(f"Error creating survey: {e}")
        db.session.rollback()
        return jsonify({'error': 'حدث خطأ في إنشاء الاستطلاع'}), 500

@app.route('/api/surveys/<int:survey_id>', methods=['PUT'])
def update_survey(survey_id):
    """Update an existing survey"""
    try:
        survey = db.session.query(Survey).filter_by(id=survey_id).first()
        if not survey:
            return jsonify({'error': 'الاستطلاع غير موجود'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'لا توجد بيانات'}), 400
        
        # Update survey fields
        if 'title' in data:
            survey.title = data['title']
        if 'title_ar' in data:
            survey.title_ar = data['title_ar']
        if 'description' in data:
            survey.description = data['description']
        if 'description_ar' in data:
            survey.description_ar = data['description_ar']
        if 'status' in data:
            survey.status = SurveyStatus(data['status'])
        
        survey.updated_at = datetime.utcnow()
        
        # Update questions if provided
        if 'questions' in data:
            # Remove existing questions
            db.session.query(Question).filter_by(survey_id=survey.id).delete()
            
            # Add new questions
            questions = data['questions']
            question_count = 0
            
            for question_data in questions:
                question = Question(
                    survey_id=survey.id,
                    text=question_data.get('text'),
                    text_ar=question_data.get('text_ar'),
                    description=question_data.get('description'),
                    description_ar=question_data.get('description_ar'),
                    type=QuestionType(question_data.get('type', 'text')),
                    is_required=question_data.get('is_required', False),
                    order_index=question_data.get('order_index', question_count),
                    options=question_data.get('options'),
                    validation_rules=question_data.get('validation_rules'),
                    display_logic=question_data.get('display_logic')
                )
                db.session.add(question)
                question_count += 1
            
            survey.question_count = question_count
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم تحديث الاستطلاع بنجاح',
            'survey': {
                'id': survey.id,
                'title': survey.title_ar or survey.title,
                'status': survey.status.value,
                'question_count': survey.question_count,
                'updated_at': survey.updated_at.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error updating survey: {e}")
        db.session.rollback()
        return jsonify({'error': 'حدث خطأ في تحديث الاستطلاع'}), 500

@app.route('/api/surveys/<int:survey_id>', methods=['DELETE'])
def delete_survey(survey_id):
    """Delete a survey"""
    try:
        survey = db.session.query(Survey).filter_by(id=survey_id).first()
        if not survey:
            return jsonify({'error': 'الاستطلاع غير موجود'}), 404
        
        # Delete associated questions first
        db.session.query(Question).filter_by(survey_id=survey.id).delete()
        
        # Delete survey
        db.session.delete(survey)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم حذف الاستطلاع بنجاح'
        })
        
    except Exception as e:
        logger.error(f"Error deleting survey: {e}")
        db.session.rollback()
        return jsonify({'error': 'حدث خطأ في حذف الاستطلاع'}), 500

@app.route('/api/surveys/<int:survey_id>/duplicate', methods=['POST'])
def duplicate_survey(survey_id):
    """Duplicate an existing survey"""
    try:
        original_survey = db.session.query(Survey).filter_by(id=survey_id).first()
        if not original_survey:
            return jsonify({'error': 'الاستطلاع غير موجود'}), 404
        
        # Create new survey as copy
        new_survey = Survey(
            title=f"{original_survey.title} - نسخة" if original_survey.title else None,
            title_ar=f"{original_survey.title_ar} - نسخة" if original_survey.title_ar else None,
            description=original_survey.description,
            description_ar=original_survey.description_ar,
            status=SurveyStatus.DRAFT,
            primary_language=original_survey.primary_language,
            supported_languages=original_survey.supported_languages,
            rtl_enabled=original_survey.rtl_enabled,
            is_public=False,  # Reset to private
            requires_login=original_survey.requires_login,
            allow_anonymous=original_survey.allow_anonymous,
            multiple_responses=original_survey.multiple_responses,
            clone_source_id=original_survey.id,
            question_count=original_survey.question_count
        )
        
        db.session.add(new_survey)
        db.session.flush()  # Get the new survey ID
        
        # Copy questions
        original_questions = db.session.query(Question).filter_by(
            survey_id=original_survey.id
        ).order_by(Question.order_index).all()
        
        for orig_question in original_questions:
            new_question = Question(
                survey_id=new_survey.id,
                text=orig_question.text,
                text_ar=orig_question.text_ar,
                description=orig_question.description,
                description_ar=orig_question.description_ar,
                type=orig_question.type,
                is_required=orig_question.is_required,
                order_index=orig_question.order_index,
                options=orig_question.options,
                validation_rules=orig_question.validation_rules,
                display_logic=orig_question.display_logic
            )
            db.session.add(new_question)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم نسخ الاستطلاع بنجاح',
            'survey_id': new_survey.id,
            'survey': {
                'id': new_survey.id,
                'title': new_survey.title_ar or new_survey.title,
                'status': new_survey.status.value,
                'question_count': new_survey.question_count
            }
        })
        
    except Exception as e:
        logger.error(f"Error duplicating survey: {e}")
        db.session.rollback()
        return jsonify({'error': 'حدث خطأ في نسخ الاستطلاع'}), 500

def get_status_display(status):
    """Get Arabic display name for status"""
    status_map = {
        SurveyStatus.DRAFT: 'مسودة',
        SurveyStatus.ACTIVE: 'نشط',
        SurveyStatus.PUBLISHED: 'منشور',
        SurveyStatus.PAUSED: 'متوقف',
        SurveyStatus.COMPLETED: 'مكتمل',
        SurveyStatus.ARCHIVED: 'مؤرشف'
    }
    return status_map.get(status, status.value)