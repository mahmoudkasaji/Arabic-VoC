# Phase 1 Implementation Guide: Survey Consolidation

## Quick Start Implementation (First 2 Weeks)

### Step 1: Database Schema Enhancement

#### Migration File: `migrations/001_consolidate_surveys.sql`
```sql
-- Add new columns to surveys table
ALTER TABLE surveys ADD COLUMN IF NOT EXISTS distribution_enabled BOOLEAN DEFAULT TRUE;
ALTER TABLE surveys ADD COLUMN IF NOT EXISTS default_distribution_message TEXT;
ALTER TABLE surveys ADD COLUMN IF NOT EXISTS total_campaign_responses INTEGER DEFAULT 0;
ALTER TABLE surveys ADD COLUMN IF NOT EXISTS last_distributed_at TIMESTAMP;

-- Create consolidated performance view
CREATE OR REPLACE VIEW survey_performance AS
SELECT 
    s.id as survey_id,
    s.title,
    s.status,
    s.created_at,
    COUNT(DISTINCT sc.id) as campaign_count,
    COALESCE(SUM(sc.sent_count), 0) as total_sent,
    COALESCE(SUM(sc.response_count), 0) as total_responses,
    CASE 
        WHEN SUM(sc.sent_count) > 0 
        THEN ROUND((SUM(sc.response_count)::DECIMAL / SUM(sc.sent_count)) * 100, 2)
        ELSE 0 
    END as response_rate,
    MAX(sc.created_at) as last_campaign_date
FROM surveys s
LEFT JOIN survey_campaigns sc ON s.id = sc.survey_id
GROUP BY s.id, s.title, s.status, s.created_at;

-- Update existing surveys with campaign response counts
UPDATE surveys SET total_campaign_responses = (
    SELECT COALESCE(SUM(response_count), 0) 
    FROM survey_campaigns 
    WHERE survey_id = surveys.id
);
```

### Step 2: Unified Backend API

#### Create: `api/surveys_unified.py`
```python
from flask import Blueprint, jsonify, request
from app import db
from models.survey_flask import SurveyFlask
from models.survey_campaigns import SurveyCampaign
from sqlalchemy import text

surveys_unified_bp = Blueprint('surveys_unified', __name__, url_prefix='/api/surveys')

@surveys_unified_bp.route('/<int:survey_id>/overview')
def get_survey_overview(survey_id):
    """Get comprehensive survey overview including distribution status"""
    try:
        # Get survey with performance data
        survey_query = text("""
            SELECT sp.*, s.description, s.questions, s.uuid, s.public_url
            FROM survey_performance sp
            JOIN surveys s ON sp.survey_id = s.id
            WHERE sp.survey_id = :survey_id
        """)
        
        result = db.session.execute(survey_query, {'survey_id': survey_id}).fetchone()
        
        if not result:
            return jsonify({'error': 'Survey not found'}), 404
        
        # Get active campaigns
        active_campaigns = SurveyCampaign.query.filter_by(
            survey_id=survey_id, 
            status='active'
        ).all()
        
        # Get recent responses (last 10)
        recent_responses_query = text("""
            SELECT created_at, channel, response_preview
            FROM responses 
            WHERE survey_id = :survey_id 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        
        recent_responses = db.session.execute(
            recent_responses_query, 
            {'survey_id': survey_id}
        ).fetchall()
        
        return jsonify({
            'survey': {
                'id': result.survey_id,
                'title': result.title,
                'status': result.status,
                'description': result.description,
                'created_at': result.created_at,
                'uuid': result.uuid,
                'public_url': result.public_url,
                'questions_count': len(result.questions) if result.questions else 0
            },
            'performance': {
                'campaign_count': result.campaign_count,
                'total_sent': result.total_sent,
                'total_responses': result.total_responses,
                'response_rate': float(result.response_rate),
                'last_campaign_date': result.last_campaign_date
            },
            'active_campaigns': [
                {
                    'id': campaign.id,
                    'name': campaign.name,
                    'status': campaign.status,
                    'channels': campaign.channels,
                    'sent_count': campaign.sent_count,
                    'response_count': campaign.response_count
                } for campaign in active_campaigns
            ],
            'recent_responses': [
                {
                    'created_at': response.created_at,
                    'channel': response.channel,
                    'preview': response.response_preview
                } for response in recent_responses
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@surveys_unified_bp.route('/<int:survey_id>/quick-distribute', methods=['POST'])
def quick_distribute(survey_id):
    """Quick distribution without campaign creation"""
    try:
        data = request.get_json()
        method = data.get('method', 'link')  # link, qr, email
        
        survey = SurveyFlask.query.get_or_404(survey_id)
        
        if method == 'link':
            return jsonify({
                'link': survey.public_url,
                'qr_code_url': f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={survey.public_url}"
            })
        
        elif method == 'email':
            recipients = data.get('recipients', [])
            # Quick email sending logic here
            return jsonify({
                'status': 'sent',
                'recipient_count': len(recipients),
                'message': f'Survey sent to {len(recipients)} recipients'
            })
        
        return jsonify({'error': 'Invalid distribution method'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@surveys_unified_bp.route('/dashboard-stats')
def get_dashboard_stats():
    """Get unified dashboard statistics"""
    try:
        stats_query = text("""
            SELECT 
                COUNT(*) as total_surveys,
                COUNT(CASE WHEN status = 'published' THEN 1 END) as active_surveys,
                COUNT(CASE WHEN status = 'draft' THEN 1 END) as draft_surveys,
                SUM(total_campaign_responses) as total_responses,
                COUNT(CASE WHEN last_distributed_at > NOW() - INTERVAL '7 days' THEN 1 END) as recently_distributed
            FROM surveys
        """)
        
        result = db.session.execute(stats_query).fetchone()
        
        return jsonify({
            'total_surveys': result.total_surveys,
            'active_surveys': result.active_surveys,
            'draft_surveys': result.draft_surveys,
            'total_responses': result.total_responses,
            'recently_distributed': result.recently_distributed,
            'avg_response_rate': 0  # Calculate from survey_performance view
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Step 3: Enhanced Survey Model

#### Update: `models/survey_flask.py`
```python
# Add new methods to existing SurveyFlask class

class SurveyFlask(db.Model):
    # ... existing fields ...
    
    distribution_enabled = db.Column(db.Boolean, default=True)
    default_distribution_message = db.Column(db.Text)
    total_campaign_responses = db.Column(db.Integer, default=0)
    last_distributed_at = db.Column(db.DateTime)
    
    def get_performance_summary(self):
        """Get performance metrics for this survey"""
        campaigns = SurveyCampaign.query.filter_by(survey_id=self.id).all()
        
        total_sent = sum(c.sent_count for c in campaigns)
        total_responses = sum(c.response_count for c in campaigns)
        response_rate = (total_responses / total_sent * 100) if total_sent > 0 else 0
        
        return {
            'campaign_count': len(campaigns),
            'total_sent': total_sent,
            'total_responses': total_responses,
            'response_rate': round(response_rate, 2),
            'last_campaign': max([c.created_at for c in campaigns]) if campaigns else None
        }
    
    def can_distribute(self):
        """Check if survey is ready for distribution"""
        return (
            self.status == 'published' and 
            self.distribution_enabled and 
            len(self.questions) > 0
        )
    
    def get_distribution_options(self):
        """Get available distribution methods for this survey"""
        return {
            'quick_link': self.public_url,
            'qr_code': f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={self.public_url}",
            'embeddable_widget': self.generate_widget_code(),
            'campaign_ready': self.can_distribute()
        }
    
    def generate_widget_code(self):
        """Generate embeddable widget code"""
        return f"""
        <div id="survey-widget-{self.id}">
            <iframe src="{self.public_url}?embedded=true" 
                    width="100%" height="600" frameborder="0">
            </iframe>
        </div>
        """
```

### Step 4: Frontend Component Structure

#### Create: `static/js/survey-hub.js`
```javascript
/**
 * Unified Survey Hub - Frontend Controller
 */
class SurveyHub {
    constructor() {
        this.surveys = [];
        this.selectedSurvey = null;
        this.activeView = 'dashboard'; // dashboard, list, detail
        this.init();
    }
    
    async init() {
        await this.loadDashboardStats();
        await this.loadSurveyList();
        this.bindEvents();
        this.renderDashboard();
    }
    
    async loadDashboardStats() {
        try {
            const response = await fetch('/api/surveys/dashboard-stats');
            this.dashboardStats = await response.json();
        } catch (error) {
            console.error('Failed to load dashboard stats:', error);
        }
    }
    
    async loadSurveyList() {
        try {
            const response = await fetch('/api/surveys/list');
            const data = await response.json();
            this.surveys = data.surveys || [];
        } catch (error) {
            console.error('Failed to load surveys:', error);
        }
    }
    
    async loadSurveyOverview(surveyId) {
        try {
            const response = await fetch(`/api/surveys/${surveyId}/overview`);
            return await response.json();
        } catch (error) {
            console.error('Failed to load survey overview:', error);
        }
    }
    
    renderDashboard() {
        const container = document.getElementById('survey-hub-container');
        const stats = this.dashboardStats;
        
        container.innerHTML = `
            <div class="dashboard-header">
                <h1>مركز إدارة الاستطلاعات</h1>
                <button class="btn btn-primary" onclick="surveyHub.createNewSurvey()">
                    <i class="fas fa-plus me-2"></i>إنشاء استطلاع جديد
                </button>
            </div>
            
            <div class="dashboard-stats">
                <div class="stat-card">
                    <h3>${stats.total_surveys}</h3>
                    <p>إجمالي الاستطلاعات</p>
                </div>
                <div class="stat-card">
                    <h3>${stats.active_surveys}</h3>
                    <p>الاستطلاعات النشطة</p>
                </div>
                <div class="stat-card">
                    <h3>${stats.total_responses}</h3>
                    <p>إجمالي الاستجابات</p>
                </div>
                <div class="stat-card">
                    <h3>${stats.recently_distributed}</h3>
                    <p>تم توزيعها مؤخراً</p>
                </div>
            </div>
            
            <div class="survey-list">
                ${this.renderSurveyList()}
            </div>
        `;
    }
    
    renderSurveyList() {
        return this.surveys.map(survey => `
            <div class="survey-card" data-survey-id="${survey.id}">
                <div class="survey-header">
                    <h3>${survey.title}</h3>
                    <span class="status-badge status-${survey.status}">${survey.status}</span>
                </div>
                <div class="survey-stats">
                    <span>${survey.question_count} أسئلة</span>
                    <span>${survey.response_count} استجابة</span>
                    <span>آخر تحديث: ${new Date(survey.updated_at).toLocaleDateString('ar-SA')}</span>
                </div>
                <div class="survey-actions">
                    <button class="btn btn-sm btn-outline-primary" onclick="surveyHub.editSurvey(${survey.id})">
                        <i class="fas fa-edit"></i> تحرير
                    </button>
                    <button class="btn btn-sm btn-outline-success" onclick="surveyHub.showDistributionPanel(${survey.id})">
                        <i class="fas fa-share-alt"></i> توزيع
                    </button>
                    <button class="btn btn-sm btn-outline-info" onclick="surveyHub.showAnalytics(${survey.id})">
                        <i class="fas fa-chart-bar"></i> التحليلات
                    </button>
                </div>
            </div>
        `).join('');
    }
    
    async showDistributionPanel(surveyId) {
        const overview = await this.loadSurveyOverview(surveyId);
        const modal = document.createElement('div');
        modal.className = 'distribution-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>توزيع الاستطلاع: ${overview.survey.title}</h3>
                    <button class="btn-close" onclick="this.closest('.distribution-modal').remove()">×</button>
                </div>
                <div class="modal-body">
                    <div class="distribution-options">
                        <div class="quick-actions">
                            <h4>مشاركة سريعة</h4>
                            <button class="btn btn-primary" onclick="surveyHub.copyLink(${surveyId})">
                                <i class="fas fa-link"></i> نسخ الرابط
                            </button>
                            <button class="btn btn-secondary" onclick="surveyHub.downloadQR(${surveyId})">
                                <i class="fas fa-qrcode"></i> رمز QR
                            </button>
                        </div>
                        <div class="campaign-actions">
                            <h4>إنشاء حملة متقدمة</h4>
                            <button class="btn btn-success" onclick="surveyHub.createCampaign(${surveyId})">
                                <i class="fas fa-bullhorn"></i> إنشاء حملة توزيع
                            </button>
                        </div>
                    </div>
                    
                    ${overview.active_campaigns.length > 0 ? `
                        <div class="active-campaigns">
                            <h4>الحملات النشطة</h4>
                            ${overview.active_campaigns.map(campaign => `
                                <div class="campaign-item">
                                    <span>${campaign.name}</span>
                                    <span>${campaign.sent_count} تم الإرسال</span>
                                    <span>${campaign.response_count} استجابة</span>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }
    
    async copyLink(surveyId) {
        try {
            const response = await fetch(`/api/surveys/${surveyId}/quick-distribute`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({method: 'link'})
            });
            
            const data = await response.json();
            
            await navigator.clipboard.writeText(data.link);
            this.showNotification('تم نسخ الرابط بنجاح!', 'success');
        } catch (error) {
            this.showNotification('فشل في نسخ الرابط', 'error');
        }
    }
    
    showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => notification.remove(), 3000);
    }
    
    bindEvents() {
        // Event delegation for dynamic content
        document.addEventListener('click', (e) => {
            if (e.target.closest('[data-survey-id]')) {
                const surveyId = e.target.closest('[data-survey-id]').dataset.surveyId;
                // Handle survey card interactions
            }
        });
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.surveyHub = new SurveyHub();
});
```

### Step 5: Updated Routes Registration

#### Update: `app.py`
```python
# Add to app.py after existing route registrations

# Register unified surveys API
from api.surveys_unified import surveys_unified_bp
app.register_blueprint(surveys_unified_bp)

# Update existing surveys route to use new unified interface
@app.route('/surveys')
def surveys_unified():
    """Unified survey management hub"""
    try:
        # Get basic stats for initial load
        total_surveys = SurveyFlask.query.count()
        active_surveys = SurveyFlask.query.filter_by(status='published').count()
        
        return render_template('surveys/hub_unified.html',
                             title='مركز إدارة الاستطلاعات',
                             total_surveys=total_surveys,
                             active_surveys=active_surveys)
    except Exception as e:
        logger.error(f"Error loading surveys hub: {e}")
        flash('حدث خطأ في تحميل الصفحة', 'error')
        return redirect(url_for('dashboard'))
```

## Next Steps

1. **Run Database Migration**: Execute the SQL migration to add new columns
2. **Deploy Backend Changes**: Add the new API endpoints and model methods
3. **Create New Template**: Build the unified hub template
4. **Test Integration**: Verify that old functionality still works
5. **Gradual Feature Toggle**: Add feature flag to switch between old/new interface

This Phase 1 implementation provides the foundation for consolidation while maintaining backward compatibility. The new unified API endpoints can be tested alongside the existing system before full migration.