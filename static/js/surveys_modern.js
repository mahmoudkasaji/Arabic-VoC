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

        // Create survey card container
        const cardDiv = document.createElement('div');
        cardDiv.className = 'survey-card-modern';
        cardDiv.setAttribute('data-survey-id', survey.id);

        // Create header section
        const headerDiv = document.createElement('div');
        headerDiv.className = 'survey-card-header';

        const headerInner = document.createElement('div');
        headerInner.className = 'd-flex justify-content-between align-items-start';

        // Title (safely set with textContent)
        const titleH5 = document.createElement('h5');
        titleH5.className = 'survey-title';
        titleH5.textContent = survey.title || 'Untitled Survey';

        // Status badge
        const statusBadge = document.createElement('span');
        statusBadge.className = survey.status === 'active' ? 'badge badge-active' : 'badge badge-draft';
        statusBadge.textContent = survey.status === 'active' ? 'Active' : 'Draft';

        headerInner.appendChild(titleH5);
        headerInner.appendChild(statusBadge);

        // Description (safely set with textContent)
        const descP = document.createElement('p');
        descP.className = 'survey-description';
        descP.textContent = survey.description || '';

        headerDiv.appendChild(headerInner);
        headerDiv.appendChild(descP);

        // Create body section
        const bodyDiv = document.createElement('div');
        bodyDiv.className = 'survey-card-body';

        const statsDiv = document.createElement('div');
        statsDiv.className = 'survey-stats';

        // Question count
        const questionSpan = document.createElement('span');
        questionSpan.className = 'stat-item';
        const strongQuestion = document.createElement('strong');
        strongQuestion.textContent = `${survey.question_count || 0} questions`;
        questionSpan.appendChild(strongQuestion);

        // Divider
        const dividerSpan = document.createElement('span');
        dividerSpan.className = 'stat-divider';
        dividerSpan.textContent = '|';

        // Update time
        const updateSpan = document.createElement('span');
        updateSpan.className = 'stat-item';
        updateSpan.textContent = `Updated ${survey.days_since_update || 0} days ago`;

        statsDiv.appendChild(questionSpan);
        statsDiv.appendChild(dividerSpan);
        statsDiv.appendChild(updateSpan);
        bodyDiv.appendChild(statsDiv);

        // Create actions section
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'survey-card-actions';

        // View button
        const viewBtn = document.createElement('button');
        viewBtn.className = 'btn btn-outline-secondary btn-sm';
        viewBtn.setAttribute('data-action', 'view');
        viewBtn.innerHTML = '<i class="fas fa-eye me-1"></i>View';

        // Edit button
        const editBtn = document.createElement('button');
        editBtn.className = 'btn btn-outline-primary btn-sm';
        editBtn.setAttribute('data-action', 'edit');
        editBtn.innerHTML = '<i class="fas fa-edit me-1"></i>Edit';

        // Delete button
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'btn btn-outline-danger btn-sm';
        deleteBtn.setAttribute('data-action', 'delete');
        deleteBtn.innerHTML = '<i class="fas fa-trash me-1"></i>Delete';

        actionsDiv.appendChild(viewBtn);
        actionsDiv.appendChild(editBtn);
        actionsDiv.appendChild(deleteBtn);

        // Assemble the card
        cardDiv.appendChild(headerDiv);
        cardDiv.appendChild(bodyDiv);
        cardDiv.appendChild(actionsDiv);
        col.appendChild(cardDiv);

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
        
        // Create message text safely using textContent
        const messageSpan = document.createElement('span');
        messageSpan.textContent = message;
        
        // Create close button safely
        const closeButton = document.createElement('button');
        closeButton.type = 'button';
        closeButton.className = 'btn-close';
        closeButton.setAttribute('data-bs-dismiss', 'alert');
        
        // Assemble notification safely
        notification.appendChild(messageSpan);
        notification.appendChild(closeButton);

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