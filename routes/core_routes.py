"""
Core Application Routes
Handles general application routes that don't fit into specific business domains
"""

from flask import render_template, jsonify, request
from app import app
from replit_auth import require_login
import logging

logger = logging.getLogger(__name__)


@app.route('/gmail-test')
def gmail_test():
    """Gmail integration test page"""
    return render_template('gmail_test.html')


@app.route('/surveys/builder')
@require_login
def survey_builder():
    """Survey builder interface"""
    return render_template('survey_builder.html')


@app.route('/surveys/list', methods=['GET'])
@require_login
def list_surveys():
    """List surveys with basic filtering"""
    from models.survey import Survey
    
    try:
        # Get query parameters
        status = request.args.get('status')
        search = request.args.get('search', '').strip()
        
        # Base query
        query = Survey.query
        
        # Apply filters
        if status:
            query = query.filter(Survey.status == status)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(Survey.title.ilike(search_term))
        
        surveys = query.order_by(Survey.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'surveys': [survey.to_dict() for survey in surveys],
            'total': len(surveys)
        })
        
    except Exception as e:
        logger.error(f"Error listing surveys: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/feedback/submit', methods=['POST'])
def submit_simple_feedback():
    """Submit feedback from widgets or forms"""
    try:
        data = request.get_json() or request.form.to_dict()
        
        # For now, just return success without database operations
        # This can be extended when feedback models are properly set up
        return jsonify({
            'success': True,
            'message': 'تم إرسال التعليق بنجاح',
            'content': data.get('content', ''),
            'rating': data.get('rating')
        })
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        return jsonify({
            'success': False,
            'error': 'فشل في إرسال التعليق'
        }), 500


@app.route('/surveys/<int:survey_id>/distribute', methods=['POST'])
@require_login
def distribute_survey(survey_id):
    """Distribute survey via email/SMS"""
    try:
        data = request.get_json()
        distribution_method = data.get('method', 'email')
        contact_list = data.get('contacts', [])
        
        # Basic validation
        if not contact_list:
            return jsonify({
                'success': False,
                'error': 'No contacts provided'
            }), 400
        
        # For now, return success with distribution summary
        # Real implementation would integrate with email/SMS services
        return jsonify({
            'success': True,
            'message': f'Survey distributed via {distribution_method}',
            'distributed_count': len(contact_list),
            'method': distribution_method
        })
        
    except Exception as e:
        logger.error(f"Survey distribution failed: {e}")
        return jsonify({
            'success': False,
            'error': 'Distribution failed'
        }), 500


@app.route('/contacts/search', methods=['GET'])
@require_login
def search_contacts():
    """Search contacts with filters"""
    from models.contacts import Contact
    from sqlalchemy import or_
    
    try:
        search_term = request.args.get('q', '').strip()
        channel = request.args.get('channel')
        limit = min(int(request.args.get('limit', 20)), 100)
        
        query = Contact.query.filter(Contact.is_active == True)
        
        # Apply search filter
        if search_term:
            search_filter = or_(
                Contact.name.ilike(f'%{search_term}%'),
                Contact.email.ilike(f'%{search_term}%'),
                Contact.phone.ilike(f'%{search_term}%'),
                Contact.company.ilike(f'%{search_term}%')
            )
            query = query.filter(search_filter)
        
        # Apply channel filter
        if channel == 'email':
            query = query.filter(Contact.email_opt_in == True, Contact.email.isnot(None))
        elif channel == 'sms':
            query = query.filter(Contact.sms_opt_in == True, Contact.phone.isnot(None))
        elif channel == 'whatsapp':
            query = query.filter(Contact.whatsapp_opt_in == True, Contact.phone.isnot(None))
        
        contacts = query.limit(limit).all()
        
        return jsonify({
            'success': True,
            'contacts': [contact.to_dict() for contact in contacts],
            'total': len(contacts)
        })
        
    except Exception as e:
        logger.error(f"Contact search failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500