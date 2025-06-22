/**
 * Modern Survey Builder JavaScript
 * Handles survey management interface with Arabic support
 */

class SurveyManager {
    constructor() {
        this.surveys = [];
        this.currentSurvey = null;
        this.init();
    }

    init() {
        this.loadSurveys();
        this.bindEvents();
    }

    bindEvents() {
        // Tab switching
        document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
            tab.addEventListener('shown.bs.tab', (e) => {
                this.handleTabSwitch(e.target.getAttribute('data-bs-target'));
            });
        });

        // Survey card actions
        document.addEventListener('click', (e) => {
            if (e.target.closest('[data-action]')) {
                const action = e.target.closest('[data-action]').getAttribute('data-action');
                const surveyId = e.target.closest('[data-survey-id]')?.getAttribute('data-survey-id');
                this.handleSurveyAction(action, surveyId);
            }
        });
    }

    async loadSurveys() {
        try {
            const response = await fetch('/api/surveys/list');
            const data = await response.json();
            
            if (data.success) {
                this.surveys = data.surveys;
                this.renderSurveys();
            } else {
                console.error('Failed to load surveys:', data.error);
            }
        } catch (error) {
            console.error('Error loading surveys:', error);
        }
    }

    renderSurveys() {
        const container = document.getElementById('surveysList');
        if (!container) return;

        container.innerHTML = '';

        this.surveys.forEach(survey => {
            const surveyCard = this.createSurveyCard(survey);
            container.appendChild(surveyCard);
        });
    }

    createSurveyCard(survey) {
        const col = document.createElement('div');
        col.className = 'col-lg-6';

        const statusBadge = survey.status === 'active' ? 
            '<span class="badge badge-active">Active</span>' :
            '<span class="badge badge-draft">Draft</span>';

        col.innerHTML = `
            <div class="survey-card-modern" data-survey-id="${survey.id}">
                <div class="survey-card-header">
                    <div class="d-flex justify-content-between align-items-start">
                        <h5 class="survey-title">${survey.title}</h5>
                        ${statusBadge}
                    </div>
                    <p class="survey-description">${survey.description}</p>
                </div>
                <div class="survey-card-body">
                    <div class="survey-stats">
                        <span class="stat-item">
                            <strong>${survey.question_count} questions</strong>
                        </span>
                        <span class="stat-divider">|</span>
                        <span class="stat-item">
                            Updated ${survey.days_since_update} days ago
                        </span>
                    </div>
                </div>
                <div class="survey-card-actions">
                    <button class="btn btn-outline-secondary btn-sm" data-action="view">
                        <i class="fas fa-eye me-1"></i>
                        View
                    </button>
                    <button class="btn btn-outline-primary btn-sm" data-action="edit">
                        <i class="fas fa-edit me-1"></i>
                        Edit
                    </button>
                    <button class="btn btn-outline-danger btn-sm" data-action="delete">
                        <i class="fas fa-trash me-1"></i>
                        Delete
                    </button>
                </div>
            </div>
        `;

        return col;
    }

    async handleSurveyAction(action, surveyId) {
        const survey = this.surveys.find(s => s.id == surveyId);
        if (!survey) return;

        switch (action) {
            case 'view':
                this.viewSurvey(survey);
                break;
            case 'edit':
                this.editSurvey(survey);
                break;
            case 'delete':
                this.deleteSurvey(survey);
                break;
        }
    }

    viewSurvey(survey) {
        // Implement survey viewing
        console.log('Viewing survey:', survey);
        alert(`عرض الاستطلاع: ${survey.title}`);
    }

    editSurvey(survey) {
        // Redirect to survey builder with survey ID
        window.location.href = `/survey-builder?edit=${survey.id}`;
    }

    async deleteSurvey(survey) {
        if (!confirm(`هل أنت متأكد من حذف الاستطلاع "${survey.title}"؟`)) {
            return;
        }

        try {
            const response = await fetch(`/api/surveys/${survey.id}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (data.success) {
                this.surveys = this.surveys.filter(s => s.id !== survey.id);
                this.renderSurveys();
                this.showNotification('تم حذف الاستطلاع بنجاح', 'success');
            } else {
                this.showNotification(data.error, 'error');
            }
        } catch (error) {
            console.error('Error deleting survey:', error);
            this.showNotification('حدث خطأ في حذف الاستطلاع', 'error');
        }
    }

    handleTabSwitch(targetTab) {
        console.log('Switched to tab:', targetTab);
        
        switch (targetTab) {
            case '#my-surveys':
                this.loadSurveys();
                break;
            case '#custom-build':
                // Handle custom build tab
                break;
            case '#templates':
                // Handle templates tab
                break;
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '9999';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
}

// Global functions
function createNewSurvey() {
    window.location.href = '/survey-builder';
}

async function exportData() {
    try {
        const response = await fetch('/api/surveys/export?format=json');
        const data = await response.json();
        
        if (data.success) {
            // Create download link
            const blob = new Blob([JSON.stringify(data.data, null, 2)], 
                { type: 'application/json' });
            const url = window.URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = `surveys_export_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            surveyManager.showNotification('تم تصدير البيانات بنجاح', 'success');
        } else {
            surveyManager.showNotification(data.error, 'error');
        }
    } catch (error) {
        console.error('Export error:', error);
        surveyManager.showNotification('حدث خطأ في تصدير البيانات', 'error');
    }
}

// Initialize survey manager when page loads
let surveyManager;
document.addEventListener('DOMContentLoaded', function() {
    surveyManager = new SurveyManager();
});