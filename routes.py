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



# === MODULAR ROUTE IMPORTS ===
# Clean separation of concerns - routes organized by business domain

# Contact Management - All contact CRUD operations
import routes.contact_management

# Integration Management - All integration testing and monitoring
import routes.integration_management

# User Preferences - All user preference management
import routes.user_preferences

# Core Routes - General application routes
import routes.core_routes



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

# === CLEAN SEPARATION OF CONCERNS IMPLEMENTED ===
# All routes are now organized into modular files by business domain:
# - routes/contact_management.py: Contact CRUD operations
# - routes/integration_management.py: Integration testing & monitoring  
# - routes/user_preferences.py: User preference management
# - routes/core_routes.py: General application routes

# === LEGACY ROUTES REMOVED ===
# Contact management routes moved to routes/contact_management.py
# Integration routes moved to routes/integration_management.py
# User preference routes moved to routes/user_preferences.py
# Core application routes moved to routes/core_routes.py
        
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