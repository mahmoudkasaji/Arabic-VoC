"""
Survey Distribution Routes - Direct Flask Implementation
Handles campaign management and distribution tracking
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from core.app import db
from models.survey_campaigns import SurveyCampaign, DistributionMethod
from models.survey_flask import SurveyFlask
from models_unified import Contact, ContactGroup
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

distribution_bp = Blueprint('distribution', __name__, url_prefix='/surveys/distribution')

@distribution_bp.route('/')
def distribution_hub():
    """Main distribution dashboard"""
    try:
        # Get dashboard metrics
        total_campaigns = SurveyCampaign.query.count()
        active_campaigns = SurveyCampaign.query.filter_by(status='active').count()
        
        # Recent campaigns
        recent_campaigns = SurveyCampaign.query.order_by(SurveyCampaign.created_at.desc()).limit(5).all()
        
        # Calculate total sent and response rates
        total_sent = db.session.query(db.func.sum(SurveyCampaign.sent_count)).scalar() or 0
        total_responses = db.session.query(db.func.sum(SurveyCampaign.response_count)).scalar() or 0
        overall_response_rate = round((total_responses / total_sent) * 100, 1) if total_sent > 0 else 0
        
        dashboard_stats = {
            'total_campaigns': total_campaigns,
            'active_campaigns': active_campaigns,
            'total_sent': total_sent,
            'total_responses': total_responses,
            'overall_response_rate': overall_response_rate
        }
        
        return render_template('distribution/hub.html',
                             title='مركز توزيع الاستطلاعات',
                             dashboard_stats=dashboard_stats,
                             recent_campaigns=recent_campaigns)
        
    except Exception as e:
        logger.error(f"Error loading distribution hub: {e}")
        return render_template('distribution/hub.html',
                             title='مركز توزيع الاستطلاعات',
                             error='حدث خطأ في تحميل لوحة التحكم')

@distribution_bp.route('/campaigns')
def campaign_list():
    """List all campaigns with filtering"""
    try:
        # Get filter parameters
        status_filter = request.args.get('status', 'all')
        survey_filter = request.args.get('survey_id')
        
        # Build query
        query = SurveyCampaign.query
        
        if status_filter != 'all':
            query = query.filter_by(status=status_filter)
        if survey_filter:
            query = query.filter_by(survey_id=survey_filter)
            
        campaigns = query.order_by(SurveyCampaign.created_at.desc()).all()
        
        # Get surveys for filter dropdown
        surveys = SurveyFlask.query.all()
        
        return render_template('distribution/campaigns.html',
                             title='إدارة الحملات',
                             campaigns=campaigns,
                             surveys=surveys,
                             current_status_filter=status_filter,
                             current_survey_filter=survey_filter)
        
    except Exception as e:
        logger.error(f"Error loading campaigns: {e}")
        return render_template('distribution/campaigns.html',
                             title='إدارة الحملات',
                             error='حدث خطأ في تحميل الحملات')

@distribution_bp.route('/campaign/create')
def create_campaign_form():
    """Campaign creation form"""
    try:
        surveys = SurveyFlask.query.filter_by(status='published').all()
        contact_groups = ContactGroup.query.all()
        
        return render_template('distribution/create_campaign.html',
                             title='إنشاء حملة جديدة',
                             surveys=surveys,
                             contact_groups=contact_groups)
        
    except Exception as e:
        logger.error(f"Error loading campaign creation form: {e}")
        return render_template('distribution/create_campaign.html',
                             title='إنشاء حملة جديدة',
                             error='حدث خطأ في تحميل النموذج')

@distribution_bp.route('/campaign/create', methods=['POST'])
def create_campaign():
    """Create new campaign - Direct DB operation"""
    try:
        # Get form data
        campaign_name = request.form.get('name')
        survey_id = request.form.get('survey_id')
        description = request.form.get('description', '')
        method_type = request.form.get('method_type')
        target_audience = request.form.getlist('target_audience')
        schedule_type = request.form.get('schedule_type', 'now')
        schedule_date = request.form.get('schedule_date')
        
        # Validation
        if not campaign_name or not survey_id or not method_type:
            flash('يرجى ملء جميع الحقول المطلوبة', 'error')
            return redirect(url_for('distribution.create_campaign_form'))
            
        # Create campaign
        campaign = SurveyCampaign(
            name=campaign_name,
            survey_id=int(survey_id),
            created_by='demo@replit.com',  # TODO: Get from session
            description=description,
            status='draft'
        )
        
        # Set schedule if specified
        if schedule_type == 'scheduled' and schedule_date:
            campaign.scheduled_at = datetime.fromisoformat(schedule_date)
            
        db.session.add(campaign)
        db.session.flush()  # Get campaign ID
        
        # Create distribution method
        distribution_method = DistributionMethod(
            campaign_id=campaign.id,
            method_type=method_type,
            target_audience={'groups': target_audience} if target_audience else {'all': True},
            status='pending'
        )
        
        db.session.add(distribution_method)
        db.session.commit()
        
        flash(f'تم إنشاء الحملة "{campaign_name}" بنجاح', 'success')
        return redirect(url_for('distribution.campaign_detail', campaign_id=campaign.id))
        
    except Exception as e:
        logger.error(f"Error creating campaign: {e}")
        db.session.rollback()
        flash('حدث خطأ في إنشاء الحملة', 'error')
        return redirect(url_for('distribution.create_campaign_form'))

@distribution_bp.route('/campaign/<int:campaign_id>')
def campaign_detail(campaign_id):
    """Campaign detail view with distribution methods"""
    try:
        campaign = SurveyCampaign.query.get_or_404(campaign_id)
        
        # Get campaign distribution methods
        distribution_methods = DistributionMethod.query.filter_by(campaign_id=campaign_id).all()
        
        # Get delivery history if exists
        from models_unified import ContactDelivery
        deliveries = ContactDelivery.query.filter_by(campaign_id=campaign_id).limit(10).all()
        
        return render_template('distribution/campaign_detail.html',
                             title=f'تفاصيل الحملة: {campaign.name}',
                             campaign=campaign,
                             distribution_methods=distribution_methods,
                             deliveries=deliveries)
        
    except Exception as e:
        logger.error(f"Error loading campaign detail: {e}")
        return render_template('distribution/campaign_detail.html',
                             title='تفاصيل الحملة',
                             error='حدث خطأ في تحميل تفاصيل الحملة')

@distribution_bp.route('/campaign/<int:campaign_id>/launch', methods=['POST'])
def launch_campaign(campaign_id):
    """Launch campaign - Updates status and triggers distribution"""
    try:
        campaign = SurveyCampaign.query.get_or_404(campaign_id)
        
        if campaign.status != 'draft':
            flash('يمكن إطلاق الحملات في مرحلة المسودة فقط', 'error')
            return redirect(url_for('distribution.campaign_detail', campaign_id=campaign_id))
        
        # Update campaign status
        campaign.status = 'active'
        campaign.scheduled_at = datetime.utcnow()
        
        # Count target contacts (simplified - count all contacts for now)
        total_contacts = Contact.query.count()
        campaign.total_contacts = total_contacts
        
        db.session.commit()
        
        flash(f'تم إطلاق الحملة "{campaign.name}" بنجاح', 'success')
        logger.info(f"Campaign {campaign_id} launched successfully")
        
        return redirect(url_for('distribution.campaign_detail', campaign_id=campaign_id))
        
    except Exception as e:
        logger.error(f"Error launching campaign: {e}")
        db.session.rollback()
        flash('حدث خطأ في إطلاق الحملة', 'error')
        return redirect(url_for('distribution.campaign_detail', campaign_id=campaign_id))

@distribution_bp.route('/campaign/<int:campaign_id>/pause', methods=['POST'])
def pause_campaign(campaign_id):
    """Pause active campaign"""
    try:
        campaign = SurveyCampaign.query.get_or_404(campaign_id)
        campaign.status = 'paused'
        db.session.commit()
        
        flash(f'تم إيقاف الحملة "{campaign.name}" مؤقتاً', 'info')
        return redirect(url_for('distribution.campaign_detail', campaign_id=campaign_id))
        
    except Exception as e:
        logger.error(f"Error pausing campaign: {e}")
        db.session.rollback()
        flash('حدث خطأ في إيقاف الحملة', 'error')
        return redirect(url_for('distribution.campaign_detail', campaign_id=campaign_id))

@distribution_bp.route('/campaign/<int:campaign_id>/delete', methods=['POST'])
def delete_campaign(campaign_id):
    """Delete campaign and related data"""
    try:
        campaign = SurveyCampaign.query.get_or_404(campaign_id)
        campaign_name = campaign.name
        
        # Delete related distribution methods (cascade should handle this)
        db.session.delete(campaign)
        db.session.commit()
        
        flash(f'تم حذف الحملة "{campaign_name}" بنجاح', 'success')
        return redirect(url_for('distribution.campaign_list'))
        
    except Exception as e:
        logger.error(f"Error deleting campaign: {e}")
        db.session.rollback()
        flash('حدث خطأ في حذف الحملة', 'error')
        return redirect(url_for('distribution.campaign_detail', campaign_id=campaign_id))