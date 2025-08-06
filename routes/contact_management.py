"""
Contact Management Routes
Handles all contact-related operations: CRUD, import/export, and list management
"""

from flask import request, render_template, redirect, url_for, flash, jsonify, Response
from app import app, db
from replit_auth import require_login
from models.contacts import Contact
import csv
import io
import logging

logger = logging.getLogger(__name__)


@app.route('/contacts')
@require_login
def contacts():
    """Display contacts management page with list of all contacts"""
    try:
        # Get all contacts from database, ordered by name
        contacts = Contact.query.order_by(Contact.name).all()
        
        # Convert contacts to dictionaries for template
        contacts_data = []
        for contact in contacts:
            contacts_data.append({
                'id': contact.id,
                'name': contact.name,
                'email': contact.email,
                'phone': contact.phone,
                'company': contact.company,
                'language_preference': contact.language_preference,
                'is_active': contact.is_active,
                'email_opt_in': contact.email_opt_in,
                'sms_opt_in': contact.sms_opt_in,
                'whatsapp_opt_in': contact.whatsapp_opt_in,
                'notes': contact.notes,
                'created_at': contact.created_at
            })
        
        return render_template('contacts_simple.html', contacts=contacts_data)
        
    except Exception as e:
        logger.error(f"Error loading contacts: {e}")
        flash('حدث خطأ في تحميل جهات الاتصال', 'error')
        return render_template('contacts_simple.html', contacts=[])


@app.route('/contacts/edit/<int:contact_id>', methods=['POST'])
@require_login
def edit_contact(contact_id):
    """Handle contact editing form submission"""
    try:
        # Get contact by ID
        contact = Contact.query.get_or_404(contact_id)
        
        # Extract form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip() or None
        phone = request.form.get('phone', '').strip() or None
        company = request.form.get('company', '').strip() or None
        language_preference = request.form.get('language_preference', 'ar')
        is_active = request.form.get('is_active') == 'true'
        email_opt_in = request.form.get('email_opt_in') == 'on'
        sms_opt_in = request.form.get('sms_opt_in') == 'on'
        whatsapp_opt_in = request.form.get('whatsapp_opt_in') == 'on'
        notes = request.form.get('notes', '').strip() or None
        
        # Update contact fields
        contact.name = name
        contact.email = email
        contact.phone = phone
        contact.company = company
        contact.language_preference = language_preference
        contact.is_active = is_active
        contact.email_opt_in = email_opt_in
        contact.sms_opt_in = sms_opt_in
        contact.whatsapp_opt_in = whatsapp_opt_in
        contact.notes = notes
        
        db.session.commit()
        flash('تم تحديث جهة الاتصال بنجاح', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating contact {contact_id}: {e}")
        flash('حدث خطأ في تحديث جهة الاتصال', 'error')
    
    return redirect(url_for('contacts'))


@app.route('/contacts/create', methods=['GET', 'POST'])
@require_login
def create_contact():
    """Handle contact creation form submission"""
    # If GET request, redirect to contacts page
    if request.method == 'GET':
        return redirect(url_for('contacts'))
    
    try:
        # Extract form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip() or None
        phone = request.form.get('phone', '').strip() or None
        company = request.form.get('company', '').strip() or None
        language_preference = request.form.get('language_preference', 'ar')
        is_active = request.form.get('is_active') == 'true'
        email_opt_in = request.form.get('email_opt_in') == 'on'
        sms_opt_in = request.form.get('sms_opt_in') == 'on'
        whatsapp_opt_in = request.form.get('whatsapp_opt_in') == 'on'
        notes = request.form.get('notes', '').strip() or None
        
        # Create new contact
        contact = Contact(
            name=name,
            email=email,
            phone=phone,
            company=company,
            language_preference=language_preference,
            is_active=is_active,
            email_opt_in=email_opt_in,
            sms_opt_in=sms_opt_in,
            whatsapp_opt_in=whatsapp_opt_in,
            notes=notes
        )
        
        db.session.add(contact)
        db.session.commit()
        flash('تم إضافة جهة الاتصال بنجاح', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating contact: {e}")
        flash('حدث خطأ في إضافة جهة الاتصال', 'error')
    
    return redirect(url_for('contacts'))


@app.route('/contacts/delete/<int:contact_id>', methods=['POST'])
@require_login
def delete_contact(contact_id):
    """Delete a contact"""
    try:
        contact = Contact.query.get_or_404(contact_id)
        db.session.delete(contact)
        db.session.commit()
        flash('تم حذف جهة الاتصال بنجاح', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting contact {contact_id}: {e}")
        flash('حدث خطأ في حذف جهة الاتصال', 'error')
    
    return redirect(url_for('contacts'))


@app.route('/contacts/export')
@require_login
def export_contacts():
    """Export all contacts to CSV file"""
    try:
        # Get all contacts from database
        contacts = Contact.query.order_by(Contact.name).all()
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'ID', 'Name', 'Email', 'Phone', 'Company', 
            'Language', 'Active', 'Email Opt-in', 'SMS Opt-in', 
            'WhatsApp Opt-in', 'Notes', 'Created'
        ])
        
        # Write contact data
        for contact in contacts:
            writer.writerow([
                contact.id,
                contact.name,
                contact.email or '',
                contact.phone or '',
                contact.company or '',
                contact.language_preference,
                'Yes' if contact.is_active else 'No',
                'Yes' if contact.email_opt_in else 'No',
                'Yes' if contact.sms_opt_in else 'No',
                'Yes' if contact.whatsapp_opt_in else 'No',
                contact.notes or '',
                contact.created_at.strftime('%Y-%m-%d %H:%M:%S') if contact.created_at else ''
            ])
        
        # Create response
        response = Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=contacts_export.csv'}
        )
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        
        return response
        
    except Exception as e:
        logger.error(f"Error exporting contacts: {e}")
        flash('حدث خطأ في تصدير جهات الاتصال', 'error')
        return redirect(url_for('contacts'))