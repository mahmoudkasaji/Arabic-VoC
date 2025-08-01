from flask import session
from app import app, db
from flask_login import current_user
try:
    from replit_auth import require_login
except ImportError:
    # Fallback decorator if Replit Auth is not available
    def require_login(f):
        return f

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/')
def example_index():
    # Use flask_login.current_user to check if current user is logged in or anonymous.
    user = current_user
    if user.is_authenticated:
        # User is logged in, show dashboard/home
        from flask import render_template
        return render_template('index_simple.html')
    else:
        # User is not logged in, show landing page
        from flask import render_template
        return render_template('index_simple.html')

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

# Enterprise Architecture Visualization
@app.route('/architecture')
@require_login
def enterprise_architecture():
    """Enterprise architecture visualization"""
    from flask import send_from_directory
    return send_from_directory('.', 'enterprise_architecture_visualization.html')

# Public Architecture Visualization (no auth required)
@app.route('/public/architecture')
def public_enterprise_architecture():
    """Public enterprise architecture visualization"""
    import os
    from flask import Response
    
    # Read the HTML file directly
    file_path = 'enterprise_architecture_visualization.html'
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return Response(content, mimetype='text/html')
    else:
        return "Architecture visualization file not found", 404

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

# Technical Integration Catalog Route
@app.route('/integrations/catalog')
@app.route('/integrations/technical')
@require_login
def integrations_catalog():
    """Technical integration catalog with real-time status monitoring"""
    from flask import render_template
    return render_template('integrations_technical_catalog.html')

# Add any other routes here.
# Use flask_login.current_user to check if current user is logged in or anonymous.
# Use db & models to interact with the database.