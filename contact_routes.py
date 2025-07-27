"""
Contact management routes for direct database operations
"""

from flask import request, redirect, url_for, flash, Response
from app import app, db
try:
    from replit_auth import require_login
except ImportError:
    def require_login(f):
        return f

# Contact Edit Route
@app.route('/contacts/edit/<int:contact_id>', methods=['POST'])
@require_login
def edit_contact(contact_id):
    """Handle contact edit form submission"""
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
    
    return redirect(url_for('contacts_page'))

# Contact Create Route
@app.route('/contacts/create', methods=['GET', 'POST'])
@require_login
def create_contact():
    """Handle contact creation form submission"""
    from models.contacts import Contact
    
    # If GET request, redirect to contacts page
    if request.method == 'GET':
        return redirect(url_for('contacts_page'))
    
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
    
    return redirect(url_for('contacts_page'))

# Bulk Export Route
@app.route('/contacts/export')
@require_login
def export_contacts():
    """Export all contacts to CSV file"""
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