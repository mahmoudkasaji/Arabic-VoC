from flask import session, jsonify
from app import app, db
from flask_login import current_user
# Use simplified import utility
from utils.imports import safe_import_replit_auth
require_login, _ = safe_import_replit_auth()

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

# Home route is handled in app.py to avoid duplication

@app.route('/example_protected_route')
@require_login # protected by Replit Auth
def example_protected_route():
    user = current_user
    # Access user properties: user.id, user.email, user.first_name, etc.
    return f"Hello {user.first_name or 'User'}! Your email is {user.email}"

# Gmail Test Route
@app.route('/gmail-test')
def gmail_test():
    from flask import render_template
    return render_template('gmail_test.html')

# Survey Builder Route
@app.route('/surveys/builder')
@require_login
def survey_builder():
    """Survey builder interface"""
    from flask import render_template
    return render_template('survey_builder.html')



# Contacts Management Route
@app.route('/contacts')
@require_login
def contacts():
    """Contacts management page with direct database access"""
    from flask import render_template, request
    from models.contacts import Contact
    
    # Get all contacts from database
    contacts = Contact.query.order_by(Contact.created_at.desc()).all()
    
    return render_template('contacts.html', contacts=contacts)

# Contact Edit Route
@app.route('/contacts/edit/<int:contact_id>', methods=['POST'])
@require_login
def edit_contact(contact_id):
    """Handle contact edit form submission"""
    from flask import request, redirect, url_for, flash
    from models.contacts import Contact
    
    contact = Contact.query.get_or_404(contact_id)
    
    # Update contact fields from form
    contact.name = request.form.get('name', '').strip()
    contact.email = request.form.get('email', '').strip() or None
    contact.phone = request.form.get('phone', '').strip() or None
    contact.company = request.form.get('company', '').strip() or None
    contact.language_preference = request.form.get('language_preference', 'ar')
    contact.is_active = request.form.get('is_active') == 'true'
    contact.email_opt_in = request.form.get('email_opt_in') == 'on'
    contact.sms_opt_in = request.form.get('sms_opt_in') == 'on'
    contact.whatsapp_opt_in = request.form.get('whatsapp_opt_in') == 'on'
    contact.notes = request.form.get('notes', '').strip() or None
    
    try:
        db.session.commit()
        flash('تم تحديث جهة الاتصال بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash('حدث خطأ في تحديث جهة الاتصال', 'error')
    
    return redirect(url_for('contacts'))

# Contact Create Route
@app.route('/contacts/create', methods=['GET', 'POST'])
@require_login
def create_contact():
    """Handle contact creation form submission"""
    from flask import request, redirect, url_for, flash
    from models.contacts import Contact
    
    # If GET request, redirect to contacts page
    if request.method == 'GET':
        return redirect(url_for('contacts'))
    
    # Create new contact from form data
    contact = Contact()
    contact.name = request.form.get('name', '').strip()
    contact.email = request.form.get('email', '').strip() or None
    contact.phone = request.form.get('phone', '').strip() or None
    contact.company = request.form.get('company', '').strip() or None
    contact.language_preference = request.form.get('language_preference', 'ar')
    contact.is_active = request.form.get('is_active') == 'true'
    contact.email_opt_in = request.form.get('email_opt_in') == 'on'
    contact.sms_opt_in = request.form.get('sms_opt_in') == 'on'
    contact.whatsapp_opt_in = request.form.get('whatsapp_opt_in') == 'on'
    contact.notes = request.form.get('notes', '').strip() or None
    
    try:
        db.session.add(contact)
        db.session.commit()
        flash('تم إضافة جهة الاتصال بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash('حدث خطأ في إضافة جهة الاتصال', 'error')
    
    return redirect(url_for('contacts'))


# Bulk Export Route
@app.route('/contacts/export')
@require_login
def export_contacts():
    """Export all contacts to CSV file"""
    from flask import Response
    from models.contacts import Contact
    import csv
    import io
    
    # Get all contacts from database
    contacts = Contact.query.order_by(Contact.name).all()
    
    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'الاسم', 'البريد الإلكتروني', 'الهاتف', 'الشركة', 
        'اللغة المفضلة', 'الحالة', 'البريد الإلكتروني مفعل', 
        'الرسائل النصية مفعل', 'واتساب مفعل', 'ملاحظات', 'تاريخ الإنشاء'
    ])
    
    # Write contact data
    for contact in contacts:
        writer.writerow([
            contact.name,
            contact.email or '',
            contact.phone or '',
            contact.company or '',
            'العربية' if contact.language_preference == 'ar' else 'English',
            'نشط' if contact.is_active else 'غير نشط',
            'نعم' if contact.email_opt_in else 'لا',
            'نعم' if contact.sms_opt_in else 'لا',
            'نعم' if contact.whatsapp_opt_in else 'لا',
            contact.notes or '',
            contact.created_at.strftime('%Y-%m-%d %H:%M') if contact.created_at else ''
        ])
    
    # Create response
    output.seek(0)
    response = Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment; filename=contacts_export.csv"}
    )
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    
    return response

# Technical Integration Catalog Route - Updated with API-focused design
@app.route('/integrations/catalog')
@app.route('/integrations/technical')
@require_login
def integrations_catalog():
    """API-focused integration catalog for developers with technical details"""
    from flask import render_template
    return render_template('integrations_technical_catalog.html')

# Integration Testing Routes (Flask-based)
@app.route('/integrations/test/<integration_id>', methods=['POST'])
@require_login
def test_integration(integration_id):
    """Test specific integration and return results"""
    from utils.integration_registry import integration_registry
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        if integration_id not in integration_registry.integrations:
            return jsonify({
                'success': False,
                'error': 'Integration not found'
            }), 404
        
        # Perform integration test
        test_result = integration_registry.test_integration(integration_id)
        
        return jsonify({
            'success': test_result.get('success', False),
            'message': test_result.get('message', 'Test completed'),
            'details': test_result.get('details', {}),
            'response_time': test_result.get('response_time'),
            'timestamp': test_result.get('timestamp')
        })
        
    except Exception as e:
        logger.error(f"Integration test failed for {integration_id}: {e}")
        return jsonify({
            'success': False,
            'error': f'Test failed: {str(e)}'
        }), 500

# User Preferences Routes (Flask-based)
@app.route('/user/preferences', methods=['GET'])
@require_login
def get_user_preferences():
    """Get user preferences as JSON"""
    from models.replit_user_preferences import ReplitUserPreferences
    from flask_login import current_user
    
    try:
        preferences = ReplitUserPreferences.get_or_create(current_user.id)
        return jsonify({
            'success': True,
            'preferences': {
                'language_preference': preferences.language_preference,
                'timezone': preferences.timezone,
                'theme': preferences.theme,
                'dashboard_layout': preferences.dashboard_layout,
                'is_admin': preferences.is_admin,
                'admin_level': preferences.admin_level
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/user/preferences', methods=['POST'])
@require_login
def update_user_preferences():
    """Update user preferences"""
    from models.replit_user_preferences import ReplitUserPreferences
    from flask_login import current_user
    from flask import request
    
    try:
        data = request.get_json()
        preferences = ReplitUserPreferences.get_or_create(current_user.id)
        
        # Update preferences
        if 'language_preference' in data:
            preferences.language_preference = data['language_preference']
        if 'timezone' in data:
            preferences.timezone = data['timezone']
        if 'theme' in data:
            preferences.theme = data['theme']
        if 'dashboard_layout' in data:
            preferences.dashboard_layout = data['dashboard_layout']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Preferences updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Survey Management Routes (Flask-based for simple operations)
@app.route('/surveys/list', methods=['GET'])
@require_login
def list_surveys():
    """List surveys with basic filtering"""
    from models.survey import Survey
    from flask import request
    
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
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Simple Feedback Collection (Flask-based)
@app.route('/feedback/submit', methods=['POST'])
def submit_simple_feedback():
    """Submit feedback from widgets or forms"""
    from flask import request
    
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
        return jsonify({
            'success': False,
            'error': 'فشل في إرسال التعليق'
        }), 500

# Survey Distribution Routes (Flask-based for simple operations)
@app.route('/surveys/<int:survey_id>/distribute', methods=['POST'])
@require_login
def distribute_survey(survey_id):
    """Distribute survey via email/SMS"""
    from flask import request
    import logging
    
    logger = logging.getLogger(__name__)
    
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

# Contact Search and Filter (Flask-based)
@app.route('/contacts/search', methods=['GET'])
@require_login
def search_contacts():
    """Search contacts with filters"""
    from models.contacts import Contact
    from flask import request
    from sqlalchemy import or_
    
    try:
        search_term = request.args.get('q', '').strip()
        channel = request.args.get('channel')
        limit = min(int(request.args.get('limit', 20)), 100)
        
        query = Contact.query.filter(Contact.is_active == True)
        
        if search_term:
            search_pattern = f"%{search_term}%"
            query = query.filter(or_(
                Contact.name.ilike(search_pattern),
                Contact.email.ilike(search_pattern),
                Contact.company.ilike(search_pattern)
            ))
        
        if channel:
            if channel == 'email':
                query = query.filter(Contact.email_opt_in == True)
            elif channel == 'sms':
                query = query.filter(Contact.sms_opt_in == True)
        
        contacts = query.limit(limit).all()
        
        return jsonify({
            'success': True,
            'contacts': [
                {
                    'id': c.id,
                    'name': c.name,
                    'email': c.email,
                    'phone': c.phone,
                    'company': c.company
                } for c in contacts
            ],
            'total': len(contacts)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Add any other routes here.
# Use flask_login.current_user to check if current user is logged in or anonymous.
# Use db & models to interact with the database.