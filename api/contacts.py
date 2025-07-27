"""
Contact Management API
Simple API for managing survey distribution contacts
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from flask import Blueprint, request, jsonify
from sqlalchemy import or_, and_
from sqlalchemy.orm import joinedload

from app import db
from models.contacts import Contact, ContactGroup, ContactGroupMembership, ContactDelivery
from utils.gmail_delivery import GmailDeliveryService

logger = logging.getLogger(__name__)

# Create Blueprint
contacts_bp = Blueprint('contacts', __name__, url_prefix='/api/contacts')

@contacts_bp.route('/', methods=['GET'])
def get_contacts():
    """Get all contacts with optional filtering"""
    try:
        # Get query parameters
        search = request.args.get('search', '').strip()
        group_id = request.args.get('group_id', type=int)
        channel = request.args.get('channel')  # email, sms, whatsapp
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        # Base query
        query = Contact.query
        
        # Apply filters
        if active_only:
            query = query.filter(Contact.is_active == True)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(or_(
                Contact.name.ilike(search_term),
                Contact.email.ilike(search_term),
                Contact.phone.ilike(search_term),
                Contact.company.ilike(search_term)
            ))
        
        if group_id:
            query = query.join(ContactGroupMembership).filter(
                ContactGroupMembership.group_id == group_id
            )
        
        # Channel filter
        if channel == 'email':
            query = query.filter(and_(Contact.email.isnot(None), Contact.email_opt_in == True))
        elif channel == 'sms':
            query = query.filter(and_(Contact.phone.isnot(None), Contact.sms_opt_in == True))
        elif channel == 'whatsapp':
            query = query.filter(and_(Contact.phone.isnot(None), Contact.whatsapp_opt_in == True))
        
        # Execute query
        contacts = query.order_by(Contact.name).all()
        
        return jsonify({
            'status': 'success',
            'contacts': [contact.to_dict() for contact in contacts],
            'total': len(contacts)
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get contacts: {e}")
        return jsonify({'error': 'Failed to retrieve contacts'}), 500

@contacts_bp.route('/', methods=['POST'])
def create_contact():
    """Create a new contact"""
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'error': 'Contact name is required'}), 400
        
        # Validate that at least one contact method is provided
        if not data.get('email') and not data.get('phone'):
            return jsonify({'error': 'Either email or phone is required'}), 400
        
        # Create contact
        contact = Contact(
            name=data['name'],
            email=data.get('email'),
            phone=data.get('phone'),
            company=data.get('company'),
            language_preference=data.get('language_preference', 'ar'),
            tags=data.get('tags', []),
            email_opt_in=data.get('email_opt_in', True),
            sms_opt_in=data.get('sms_opt_in', True),
            whatsapp_opt_in=data.get('whatsapp_opt_in', True),
            notes=data.get('notes'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(contact)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'contact': contact.to_dict(),
            'message': 'Contact created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Failed to create contact: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create contact'}), 500

@contacts_bp.route('/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    """Update an existing contact"""
    try:
        contact = Contact.query.get_or_404(contact_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update fields
        if 'name' in data:
            contact.name = data['name']
        if 'email' in data:
            contact.email = data['email']
        if 'phone' in data:
            contact.phone = data['phone']
        if 'company' in data:
            contact.company = data['company']
        if 'language_preference' in data:
            contact.language_preference = data['language_preference']
        if 'tags' in data:
            contact.tags = data['tags']
        if 'email_opt_in' in data:
            contact.email_opt_in = data['email_opt_in']
        if 'sms_opt_in' in data:
            contact.sms_opt_in = data['sms_opt_in']
        if 'whatsapp_opt_in' in data:
            contact.whatsapp_opt_in = data['whatsapp_opt_in']
        if 'notes' in data:
            contact.notes = data['notes']
        if 'is_active' in data:
            contact.is_active = data['is_active']
        
        contact.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'contact': contact.to_dict(),
            'message': 'Contact updated successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to update contact: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update contact'}), 500

@contacts_bp.route('/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    """Delete a contact"""
    try:
        contact = Contact.query.get_or_404(contact_id)
        
        # Soft delete - just mark as inactive
        contact.is_active = False
        contact.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Contact deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to delete contact: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete contact'}), 500

@contacts_bp.route('/bulk', methods=['POST'])
def create_bulk_contacts():
    """Create multiple contacts from CSV/JSON data"""
    try:
        data = request.get_json()
        
        if not data or 'contacts' not in data:
            return jsonify({'error': 'Contacts data is required'}), 400
        
        contacts_data = data['contacts']
        created_contacts = []
        errors = []
        
        for i, contact_data in enumerate(contacts_data):
            try:
                if not contact_data.get('name'):
                    errors.append(f"Row {i+1}: Contact name is required")
                    continue
                
                if not contact_data.get('email') and not contact_data.get('phone'):
                    errors.append(f"Row {i+1}: Either email or phone is required")
                    continue
                
                contact = Contact(
                    name=contact_data['name'],
                    email=contact_data.get('email'),
                    phone=contact_data.get('phone'),
                    company=contact_data.get('company'),
                    language_preference=contact_data.get('language_preference', 'ar'),
                    tags=contact_data.get('tags', []),
                    email_opt_in=contact_data.get('email_opt_in', True),
                    sms_opt_in=contact_data.get('sms_opt_in', True),
                    whatsapp_opt_in=contact_data.get('whatsapp_opt_in', True),
                    notes=contact_data.get('notes')
                )
                
                db.session.add(contact)
                created_contacts.append(contact)
                
            except Exception as e:
                errors.append(f"Row {i+1}: {str(e)}")
        
        if created_contacts:
            db.session.commit()
        
        return jsonify({
            'status': 'success',
            'created': len(created_contacts),
            'errors': errors,
            'contacts': [contact.to_dict() for contact in created_contacts]
        }), 201 if created_contacts else 400
        
    except Exception as e:
        logger.error(f"Failed to create bulk contacts: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create contacts'}), 500

@contacts_bp.route('/groups', methods=['GET'])
def get_contact_groups():
    """Get all contact groups"""
    try:
        groups = ContactGroup.query.order_by(ContactGroup.name).all()
        
        return jsonify({
            'status': 'success',
            'groups': [group.to_dict() for group in groups],
            'total': len(groups)
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get contact groups: {e}")
        return jsonify({'error': 'Failed to retrieve contact groups'}), 500

@contacts_bp.route('/groups', methods=['POST'])
def create_contact_group():
    """Create a new contact group"""
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'error': 'Group name is required'}), 400
        
        group = ContactGroup(
            name=data['name'],
            description=data.get('description')
        )
        
        db.session.add(group)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'group': group.to_dict(),
            'message': 'Contact group created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Failed to create contact group: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create contact group'}), 500

@contacts_bp.route('/test-email', methods=['POST'])
def test_email_service():
    """Test Gmail email service configuration"""
    try:
        data = request.get_json()
        test_email = data.get('test_email') if data else None
        
        if not test_email:
            return jsonify({'error': 'Test email address is required'}), 400
        
        gmail_service = GmailDeliveryService()
        
        # Test connection first
        connection_result = gmail_service.test_connection()
        if not connection_result.success:
            return jsonify({
                'status': 'error',
                'message': connection_result.error_message,
                'service_status': gmail_service.get_status()
            }), 400
        
        # Send test email with real survey URL
        from utils.url_helpers import get_base_url
        test_survey_url = f"{get_base_url()}/s/nlxjb7kn"  # Use existing survey
        
        result = gmail_service.send_survey_invitation(
            recipient=test_email,
            survey_link=test_survey_url,
            survey_title="Test Survey - Email Configuration",
            sender_name="VoC Platform Test"
        )
        
        if result.success:
            return jsonify({
                'status': 'success',
                'message': 'Test email sent successfully',
                'delivery_time': result.delivery_time.isoformat() if result.delivery_time else None,
                'service_status': gmail_service.get_status()
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': result.error_message,
                'service_status': gmail_service.get_status()
            }), 400
        
    except Exception as e:
        logger.error(f"Email test failed: {e}")
        return jsonify({'error': 'Email test failed'}), 500

@contacts_bp.route('/service-status', methods=['GET'])
def get_service_status():
    """Get delivery service status"""
    try:
        gmail_service = GmailDeliveryService()
        
        return jsonify({
            'status': 'success',
            'services': {
                'gmail': gmail_service.get_status()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get service status: {e}")
        return jsonify({'error': 'Failed to get service status'}), 500