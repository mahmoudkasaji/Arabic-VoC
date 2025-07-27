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
    import logging
    
    logger = logging.getLogger(__name__)
    logger.info(f"=== EDIT CONTACT ROUTE START ===")
    logger.info(f"Contact ID: {contact_id}")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Form data: {dict(request.form)}")
    logger.info(f"Request headers: {dict(request.headers)}")
    
    try:
        contact = Contact.query.get_or_404(contact_id)
        logger.info(f"Found contact: {contact.name} ({contact.email})")
        
        # Store original values for logging
        original_name = contact.name
        original_email = contact.email
    
        # Update contact fields from form
        contact.name = request.form.get('name', '').strip() or contact.name
        contact.email = request.form.get('email', '').strip() or None
        contact.phone = request.form.get('phone', '').strip() or None
        contact.company = request.form.get('company', '').strip() or None
        contact.language_preference = request.form.get('language_preference', 'ar')
        contact.is_active = request.form.get('is_active') == 'true'
        contact.email_opt_in = request.form.get('email_opt_in') == 'on'
        contact.sms_opt_in = request.form.get('sms_opt_in') == 'on'
        contact.whatsapp_opt_in = request.form.get('whatsapp_opt_in') == 'on'
        contact.notes = request.form.get('notes', '').strip() or None
        
        logger.info(f"Updated values - Name: {original_name} -> {contact.name}")
        logger.info(f"Updated values - Email: {original_email} -> {contact.email}")
        
        # Validate required fields
        if not contact.name:
            flash('اسم جهة الاتصال مطلوب', 'error')
            return redirect(url_for('contacts_page'))
    
        try:
            db.session.commit()
            logger.info(f"SUCCESS: Contact {contact_id} updated successfully")
            logger.info(f"Final values - Name: {contact.name}, Email: {contact.email}")
            flash('تم تحديث جهة الاتصال بنجاح', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f"DATABASE ERROR: Failed to update contact {contact_id}: {e}")
            flash('حدث خطأ في تحديث جهة الاتصال', 'error')
        
        logger.info("=== REDIRECTING TO CONTACTS PAGE ===")
        return redirect(url_for('contacts_page'))
        
    except Exception as e:
        logger.error(f"CRITICAL ERROR in edit_contact: {e}")
        flash('حدث خطأ غير متوقع', 'error')
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

# Bulk Import Route
@app.route('/contacts/import', methods=['GET', 'POST'])
@require_login
def import_contacts():
    """Handle bulk contact import from CSV file"""
    from models.contacts import Contact
    import csv
    import io
    
    if request.method == 'GET':
        return redirect(url_for('contacts_page'))
    
    # Check if file was uploaded
    if 'file' not in request.files:
        flash('لم يتم اختيار ملف للاستيراد', 'error')
        return redirect(url_for('contacts_page'))
    
    file = request.files['file']
    if file.filename == '':
        flash('لم يتم اختيار ملف للاستيراد', 'error')
        return redirect(url_for('contacts_page'))
    
    if not (file.filename and file.filename.endswith('.csv')):
        flash('يرجى اختيار ملف CSV فقط', 'error')
        return redirect(url_for('contacts_page'))
    
    try:
        # Read CSV content
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)
        
        # Skip header row
        next(csv_input, None)
        
        imported_count = 0
        error_count = 0
        
        for row_num, row in enumerate(csv_input, start=2):
            try:
                # Ensure we have enough columns
                if len(row) < 4:  # At least name, email, phone, company
                    error_count += 1
                    continue
                
                # Extract data from row
                name = row[0].strip() if len(row) > 0 and row[0] else None
                email = row[1].strip() if len(row) > 1 and row[1] else None
                phone = row[2].strip() if len(row) > 2 and row[2] else None
                company = row[3].strip() if len(row) > 3 and row[3] else None
                language = 'ar' if len(row) > 4 and row[4] in ['العربية', 'ar'] else 'en'
                is_active = True if len(row) <= 5 or row[5] in ['نشط', 'active', 'true', '1'] else False
                email_opt_in = True if len(row) <= 6 or row[6] in ['نعم', 'yes', 'true', '1'] else False
                sms_opt_in = True if len(row) <= 7 or row[7] in ['نعم', 'yes', 'true', '1'] else False
                whatsapp_opt_in = True if len(row) <= 8 or row[8] in ['نعم', 'yes', 'true', '1'] else False
                notes = row[9].strip() if len(row) > 9 and row[9] else None
                
                # Validate required fields
                if not name:
                    error_count += 1
                    continue
                
                # Check if contact already exists
                existing_contact = None
                if email:
                    existing_contact = Contact.query.filter_by(email=email).first()
                if not existing_contact and phone:
                    existing_contact = Contact.query.filter_by(phone=phone).first()
                
                if existing_contact:
                    # Update existing contact
                    existing_contact.name = name
                    existing_contact.company = company
                    existing_contact.language_preference = language
                    existing_contact.is_active = is_active
                    existing_contact.email_opt_in = email_opt_in
                    existing_contact.sms_opt_in = sms_opt_in
                    existing_contact.whatsapp_opt_in = whatsapp_opt_in
                    if notes:
                        existing_contact.notes = notes
                else:
                    # Create new contact
                    contact = Contact()
                    contact.name = name
                    contact.email = email
                    contact.phone = phone
                    contact.company = company
                    contact.language_preference = language
                    contact.is_active = is_active
                    contact.email_opt_in = email_opt_in
                    contact.sms_opt_in = sms_opt_in
                    contact.whatsapp_opt_in = whatsapp_opt_in
                    contact.notes = notes
                    
                    db.session.add(contact)
                
                imported_count += 1
                
            except Exception as e:
                # Add logging capability since logger is already used above
                import logging
                local_logger = logging.getLogger(__name__)
                local_logger.error(f"Error importing row {row_num}: {e}")
                error_count += 1
                continue
        
        # Commit all changes
        db.session.commit()
        
        if imported_count > 0:
            flash(f'تم استيراد {imported_count} جهة اتصال بنجاح', 'success')
        if error_count > 0:
            flash(f'فشل في استيراد {error_count} صف', 'warning')
            
    except Exception as e:
        db.session.rollback()
        # Add logging capability
        import logging
        local_logger = logging.getLogger(__name__)
        local_logger.error(f"Failed to import contacts: {e}")
        flash('حدث خطأ أثناء استيراد جهات الاتصال', 'error')
    
    return redirect(url_for('contacts_page'))

# CSV Template Download Route
@app.route('/contacts/template')
@require_login
def download_csv_template():
    """Download a CSV template for bulk import"""
    import csv
    import io
    
    # Create CSV template
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'الاسم', 'البريد الإلكتروني', 'الهاتف', 'الشركة', 
        'اللغة المفضلة', 'الحالة', 'البريد الإلكتروني مفعل', 
        'الرسائل النصية مفعل', 'واتساب مفعل', 'ملاحظات'
    ])
    
    # Add sample row
    writer.writerow([
        'أحمد محمد', 'ahmed@example.com', '+966501234567', 'شركة ABC',
        'العربية', 'نشط', 'نعم', 'نعم', 'لا', 'عميل مهم'
    ])
    
    # Create response
    output.seek(0)
    response = Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment; filename=contacts_template.csv"}
    )
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    
    return response