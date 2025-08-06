/**
 * Arabic-first Voice of Customer Platform - Main JavaScript
 * Handles client-side interactions, form submissions, and real-time updates
 */

// Global configuration (prevent redefinition)
if (typeof CONFIG === 'undefined') {
    window.CONFIG = {
        API_BASE_URL: '/api',
        REFRESH_INTERVAL: 30000, // 30 seconds
        CHART_COLORS: {
            positive: '#28a745',
            negative: '#dc3545',
            neutral: '#6c757d',
            primary: '#2c5aa0',
            secondary: '#d4a574'
        },
        ARABIC_LOCALE: 'ar-SA'
    };
}

// CRITICAL: Define toggleLanguage function IMMEDIATELY for onclick handlers
window.toggleLanguage = function() {
    console.log('🔄 toggleLanguage called');
    
    // Show loading state if button exists
    const button = document.querySelector('[onclick="toggleLanguage()"]');
    const originalContent = button ? button.textContent : '';
    
    console.log('Button found:', button);
    
    if (button) {
        button.disabled = true;
        // Safe DOM manipulation: Clear content and add loading text
        button.textContent = 'جاري التحميل...';
        const spinner = document.createElement('i');
        spinner.className = 'fas fa-spinner fa-spin me-1';
        button.insertBefore(spinner, button.firstChild);
    }
    
    console.log('Sending toggle request to /api/language/toggle');
    
    // CRITICAL FIX: Include credentials and proper headers for session persistence
    fetch('/api/language/toggle', {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'
        },
        credentials: 'same-origin',  // CRITICAL: Include session cookies
        body: JSON.stringify({})
    })
    .then(response => {
        console.log('Toggle response status:', response.status);
        if (response.ok) {
            return response.json();
        } else {
            throw new Error(`HTTP ${response.status}`);
        }
    })
    .then(data => {
        console.log('✅ Toggle successful:', data);
        console.log('New language:', data.language);
        console.log('Session language:', data.session_language);
        
        // Update JavaScript translation system if available
        if (window.TranslationManager && window.TranslationManager.setLanguage) {
            window.TranslationManager.setLanguage(data.language);
        }
        
        // Update HTML lang attribute
        document.documentElement.lang = data.language;
        
        // CRITICAL FIX: Add small delay before reload to ensure session is saved
        setTimeout(() => {
            console.log('🔄 Reloading page with new language...');
            window.location.reload(true); // Force reload from server
        }, 100);
    })
    .catch(error => {
        console.error('❌ Error toggling language:', error);
        if (button) {
            button.disabled = false;
            button.textContent = originalContent;
        }
    });
};

// Alternative implementation using addEventListener for better compatibility
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM loaded, setting up bilingual toggle...');
    
    // Find all language toggle buttons and add event listeners
    const toggleButtons = document.querySelectorAll('[onclick="toggleLanguage()"], .language-toggle, #languageToggle');
    
    toggleButtons.forEach(button => {
        console.log('Found toggle button:', button);
        
        // Add click event listener as backup
        button.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('🎯 Button clicked via addEventListener');
            window.toggleLanguage();
        });
    });
    
    console.log(`✅ Set up ${toggleButtons.length} language toggle buttons`);
});

// Utility functions for Arabic text handling
const ArabicUtils = {
    /**
     * Format Arabic numbers for display
     */
    formatNumber: (num) => {
        return new Intl.NumberFormat('ar-SA').format(num);
    },

    /**
     * Format dates in Arabic
     */
    formatDate: (date) => {
        return new Intl.DateTimeFormat('ar-SA', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(new Date(date));
    },

    /**
     * Get sentiment display text in Arabic
     */
    getSentimentText: (score) => {
        if (score > 0.1) return 'إيجابي';
        if (score < -0.1) return 'سلبي';
        return 'محايد';
    },

    /**
     * Get sentiment CSS class
     */
    getSentimentClass: (score) => {
        if (score > 0.1) return 'sentiment-positive';
        if (score < -0.1) return 'sentiment-negative';
        return 'sentiment-neutral';
    }
};

// API helper functions
const API = {
    /**
     * Generic API request handler
     */
    async request(endpoint, options = {}) {
        const url = `${CONFIG.API_BASE_URL}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Accept-Language': 'ar'
            }
        };

        try {
            const response = await fetch(url, { ...defaultOptions, ...options });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'حدث خطأ في الطلب');
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            UI.showAlert('خطأ في الاتصال بالخادم: ' + error.message, 'danger');
            throw error;
        }
    },

    /**
     * Submit feedback
     */
    async submitFeedback(feedbackData) {
        return await this.request('/feedback/submit', {
            method: 'POST',
            body: JSON.stringify(feedbackData)
        });
    },

    /**
     * Get feedback list
     */
    async getFeedbackList(filters = {}) {
        const params = new URLSearchParams(filters);
        return await this.request(`/feedback/list?${params}`);
    },

    /**
     * Get analytics dashboard data
     */
    async getDashboardMetrics(timeRange = {}) {
        const params = new URLSearchParams(timeRange);
        return await this.request(`/analytics/dashboard?${params}`);
    },

    /**
     * Get sentiment metrics
     */
    async getSentimentMetrics(filters = {}) {
        const params = new URLSearchParams(filters);
        return await this.request(`/analytics/sentiment?${params}`);
    }
};

// UI management functions
const UI = {
    /**
     * Show alert message
     */
    showAlert(message, type = 'info', duration = 5000) {
        const alertContainer = document.getElementById('alert-container') || this.createAlertContainer();

        const alert = document.createElement('div');
        alert.className = `alert alert-${type} fade-in`;
        
        // SECURITY FIX: Use safe DOM methods instead of innerHTML
        const messageSpan = document.createElement('span');
        messageSpan.textContent = message; // textContent prevents XSS
        
        const closeButton = document.createElement('button');
        closeButton.type = 'button';
        closeButton.className = 'btn-close';
        closeButton.textContent = '×';
        closeButton.onclick = function() { this.parentElement.remove(); };
        
        alert.appendChild(messageSpan);
        alert.appendChild(closeButton);

        alertContainer.appendChild(alert);

        // Auto-remove after duration
        setTimeout(() => {
            if (alert.parentElement) {
                alert.remove();
            }
        }, duration);
    },

    /**
     * Create alert container if it doesn't exist
     */
    createAlertContainer() {
        const container = document.createElement('div');
        container.id = 'alert-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1050;
            max-width: 400px;
        `;
        document.body.appendChild(container);
        return container;
    },

    /**
     * Show loading spinner
     */
    showLoading(element) {
        if (element) {
            element.innerHTML = '<div class="loading"></div> جارٍ التحميل...';
            element.disabled = true;
        }
    },

    /**
     * Hide loading spinner
     */
    hideLoading(element, originalText = '') {
        if (element) {
            // SECURITY FIX: Use textContent instead of innerHTML for text-only content
            element.textContent = originalText;
            element.disabled = false;
        }
    },

    /**
     * Update feedback counter
     */
    updateCounter(elementId, count) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = ArabicUtils.formatNumber(count);
        }
    },

    /**
     * Create feedback item HTML
     */
    createFeedbackItem(feedback) {
        const sentimentClass = ArabicUtils.getSentimentClass(feedback.sentiment_score);
        const sentimentText = ArabicUtils.getSentimentText(feedback.sentiment_score);

        // SECURITY FIX: Use safe DOM methods instead of innerHTML
        const feedbackItem = document.createElement('div');
        feedbackItem.className = 'feedback-item';
        feedbackItem.setAttribute('data-id', feedback.id);

        // Create meta section
        const feedbackMeta = document.createElement('div');
        feedbackMeta.className = 'feedback-meta';

        const sentimentSpan = document.createElement('span');
        sentimentSpan.className = `sentiment-indicator ${sentimentClass}`;
        sentimentSpan.textContent = sentimentText;
        feedbackMeta.appendChild(sentimentSpan);

        const dateSpan = document.createElement('span');
        dateSpan.className = 'feedback-date';
        dateSpan.textContent = ArabicUtils.formatDate(feedback.created_at);
        feedbackMeta.appendChild(dateSpan);

        const channelSpan = document.createElement('span');
        channelSpan.className = 'feedback-channel';
        channelSpan.textContent = this.getChannelName(feedback.channel);
        feedbackMeta.appendChild(channelSpan);

        feedbackItem.appendChild(feedbackMeta);

        // Create content section
        const contentDiv = document.createElement('div');
        contentDiv.className = 'feedback-content';
        contentDiv.textContent = feedback.content; // SAFE: using textContent
        feedbackItem.appendChild(contentDiv);

        // Create summary section if exists
        if (feedback.ai_summary) {
            const summaryDiv = document.createElement('div');
            summaryDiv.className = 'feedback-summary';
            
            const summaryLabel = document.createElement('strong');
            summaryLabel.textContent = 'الملخص: ';
            summaryDiv.appendChild(summaryLabel);
            
            const summaryText = document.createElement('span');
            summaryText.textContent = feedback.ai_summary; // SAFE: using textContent
            summaryDiv.appendChild(summaryText);
            
            feedbackItem.appendChild(summaryDiv);
        }

        // Create actions section
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'feedback-actions';

        const detailsBtn = document.createElement('button');
        detailsBtn.className = 'btn btn-outline btn-sm';
        detailsBtn.textContent = 'عرض التفاصيل';
        detailsBtn.onclick = () => FeedbackManager.viewDetails(feedback.id);
        actionsDiv.appendChild(detailsBtn);

        feedbackItem.appendChild(actionsDiv);

        return feedbackItem;
    },

    /**
     * Get channel display name in Arabic
     */
    getChannelName(channel) {
        const channelNames = {
            'email': 'البريد الإلكتروني',
            'phone': 'الهاتف',
            'website': 'الموقع الإلكتروني',
            'mobile_app': 'التطبيق المحمول',
            'social_media': 'وسائل التواصل الاجتماعي',
            'whatsapp': 'واتساب',
            'sms': 'رسائل نصية',
            'in_person': 'شخصياً',
            'survey': 'استبيان',
            'chatbot': 'روبوت المحادثة'
        };
        return channelNames[channel] || channel;
    }
};

// Feedback management
const FeedbackManager = {
    /**
     * Initialize feedback form
     */
    initForm() {
        const form = document.getElementById('feedback-form');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;

            try {
                UI.showLoading(submitBtn);

                const formData = new FormData(form);
                const feedbackData = {
                    content: formData.get('content'),
                    channel: formData.get('channel'),
                    customer_email: formData.get('customer_email') || null,
                    customer_phone: formData.get('customer_phone') || null,
                    rating: formData.get('rating') ? parseInt(formData.get('rating')) : null,
                    channel_metadata: {}
                };

                const result = await API.submitFeedback(feedbackData);

                UI.showAlert('تم إرسال التعليق بنجاح وسيتم معالجته قريباً', 'success');
                form.reset();

                // Refresh feedback list if on the same page
                if (typeof this.refreshList === 'function') {
                    this.refreshList();
                }

            } catch (error) {
                console.error('Error submitting feedback:', error);
            } finally {
                UI.hideLoading(submitBtn, originalText);
            }
        });

        // Character counter for feedback content
        const contentField = form.querySelector('textarea[name="content"]');
        if (contentField) {
            this.initCharacterCounter(contentField);
        }
    },

    /**
     * Initialize character counter
     */
    initCharacterCounter(textarea) {
        const maxLength = 5000;
        const counter = document.createElement('div');
        counter.className = 'character-counter';
        counter.style.cssText = `
            text-align: left;
            font-size: 0.875rem;
            color: var(--text-muted);
            margin-top: 0.5rem;
        `;

        textarea.parentNode.appendChild(counter);

        const updateCounter = () => {
            const remaining = maxLength - textarea.value.length;
            counter.textContent = `${ArabicUtils.formatNumber(remaining)} حرف متبقي`;

            if (remaining < 100) {
                counter.style.color = 'var(--danger-color)';
            } else if (remaining < 500) {
                counter.style.color = 'var(--warning-color)';
            } else {
                counter.style.color = 'var(--text-muted)';
            }
        };

        textarea.addEventListener('input', updateCounter);
        updateCounter();
    },

    /**
     * Load and display feedback list
     */
    async loadFeedbackList(filters = {}) {
        const container = document.getElementById('feedback-list');
        if (!container) return;

        try {
            UI.showLoading(container);

            const feedbackList = await API.getFeedbackList(filters);

            if (feedbackList.length === 0) {
                // SECURITY FIX: Use safe DOM methods instead of innerHTML
                container.innerHTML = ''; // Clear container safely
                const emptyDiv = document.createElement('div');
                emptyDiv.className = 'text-center';
                emptyDiv.style.padding = '2rem';
                
                const emptyText = document.createElement('p');
                emptyText.className = 'text-muted';
                emptyText.textContent = 'لا توجد تعليقات لعرضها';
                
                emptyDiv.appendChild(emptyText);
                container.appendChild(emptyDiv);
                return;
            }

            // SECURITY FIX: Use safe DOM methods instead of innerHTML
            container.innerHTML = ''; // Clear container safely
            feedbackList.forEach(feedback => {
                const feedbackElement = UI.createFeedbackItem(feedback);
                container.appendChild(feedbackElement);
            });

        } catch (error) {
            // SECURITY FIX: Use safe DOM methods instead of innerHTML
            container.innerHTML = '';
            const errorDiv = document.createElement('div');
            errorDiv.className = 'alert alert-danger';
            errorDiv.textContent = `خطأ في تحميل التعليقات: ${error.message}`;
            container.appendChild(errorDiv);
        }
    },

    /**
     * View feedback details
     */
    async viewDetails(feedbackId) {
        try {
            const feedback = await API.request(`/feedback/${feedbackId}`);
            this.showDetailsModal(feedback);
        } catch (error) {
            UI.showAlert('خطأ في تحميل تفاصيل التعليق', 'danger');
        }
    },

    /**
     * Show feedback details in modal - XSS SAFE VERSION
     */
    showDetailsModal(feedback) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        
        // SECURITY FIX: Use safe DOM creation instead of innerHTML
        const modalContent = document.createElement('div');
        modalContent.className = 'modal-content';
        
        // Header
        const header = document.createElement('div');
        header.className = 'modal-header';
        
        const title = document.createElement('h3');
        title.textContent = 'تفاصيل التعليق';
        header.appendChild(title);
        
        const closeBtn = document.createElement('button');
        closeBtn.className = 'btn-close';
        closeBtn.textContent = '×';
        closeBtn.onclick = () => modal.remove();
        header.appendChild(closeBtn);
        
        modalContent.appendChild(header);
        
        // Body
        const body = document.createElement('div');
        body.className = 'modal-body';
        
        const details = document.createElement('div');
        details.className = 'feedback-details';
        
        // Content row
        const contentRow = document.createElement('div');
        contentRow.className = 'detail-row';
        
        const contentLabel = document.createElement('strong');
        contentLabel.textContent = 'المحتوى:';
        contentRow.appendChild(contentLabel);
        
        const contentText = document.createElement('p');
        contentText.textContent = feedback.content; // SAFE: using textContent
        contentRow.appendChild(contentText);
        
        details.appendChild(contentRow);
        
        // Channel row
        const channelRow = document.createElement('div');
        channelRow.className = 'detail-row';
        
        const channelLabel = document.createElement('strong');
        channelLabel.textContent = 'القناة:';
        channelRow.appendChild(channelLabel);
        
        const channelText = document.createElement('span');
        channelText.textContent = UI.getChannelName(feedback.channel); // SAFE: using textContent
        channelRow.appendChild(channelText);
        
        details.appendChild(channelRow);
        
        // Date row
        const dateRow = document.createElement('div');
        dateRow.className = 'detail-row';
        
        const dateLabel = document.createElement('strong');
        dateLabel.textContent = 'تاريخ الإرسال:';
        dateRow.appendChild(dateLabel);
        
        const dateText = document.createElement('span');
        dateText.textContent = ArabicUtils.formatDate(feedback.created_at); // SAFE: using textContent
        dateRow.appendChild(dateText);
        
        details.appendChild(dateRow);
        
        // Sentiment row
        const sentimentRow = document.createElement('div');
        sentimentRow.className = 'detail-row';
        
        const sentimentLabel = document.createElement('strong');
        sentimentLabel.textContent = 'تحليل المشاعر:';
        sentimentRow.appendChild(sentimentLabel);
        
        const sentimentSpan = document.createElement('span');
        sentimentSpan.className = ArabicUtils.getSentimentClass(feedback.sentiment_score);
        const sentimentText = ArabicUtils.getSentimentText(feedback.sentiment_score);
        const scoreText = feedback.sentiment_score ? feedback.sentiment_score.toFixed(2) : 'غير محدد';
        sentimentSpan.textContent = `${sentimentText} (${scoreText})`; // SAFE: using textContent
        sentimentRow.appendChild(sentimentSpan);
        
        details.appendChild(sentimentRow);
        
        // AI Summary row (if exists)
        if (feedback.ai_summary) {
            const summaryRow = document.createElement('div');
            summaryRow.className = 'detail-row';
            
            const summaryLabel = document.createElement('strong');
            summaryLabel.textContent = 'الملخص التلقائي:';
            summaryRow.appendChild(summaryLabel);
            
            const summaryText = document.createElement('p');
            summaryText.textContent = feedback.ai_summary; // SAFE: using textContent
            summaryRow.appendChild(summaryText);
            
            details.appendChild(summaryRow);
        }
        
        body.appendChild(details);
        modalContent.appendChild(body);
        modal.appendChild(modalContent);

        // Add modal styles
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        `;

        document.body.appendChild(modal);

        // Close modal on outside click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    },

    /**
     * Refresh feedback list
     */
    async refreshList() {
        await this.loadFeedbackList();
    }
};

// Analytics dashboard
const Dashboard = {
    /**
     * Initialize dashboard
     */
    async init() {
        await this.loadMetrics();
        this.startAutoRefresh();
    },

    /**
     * Load dashboard metrics
     */
    async loadMetrics() {
        try {
            const metrics = await API.getDashboardMetrics();
            this.updateMetrics(metrics);
            this.updateCharts(metrics);
        } catch (error) {
            console.error('Error loading dashboard metrics:', error);
        }
    },

    /**
     * Update metric cards
     */
    updateMetrics(metrics) {
        const metricElements = {
            'total-feedback': metrics.total_feedback,
            'processed-feedback': metrics.processed_feedback,
            'pending-feedback': metrics.pending_feedback,
            'avg-sentiment': metrics.average_sentiment?.toFixed(2) || '0.00'
        };

        Object.entries(metricElements).forEach(([id, value]) => {
            UI.updateCounter(id, value);
        });

        // Update recent feedback count
        const recentElement = document.getElementById('recent-feedback-count');
        if (recentElement) {
            recentElement.textContent = ArabicUtils.formatNumber(metrics.recent_feedback_count);
        }
    },

    /**
     * Update charts with new data
     */
    updateCharts(metrics) {
        this.updateSentimentChart(metrics.sentiment_distribution);
        this.updateChannelChart(metrics.channel_metrics);
    },

    /**
     * Update sentiment distribution chart
     */
    updateSentimentChart(sentimentData) {
        const chartContainer = document.getElementById('sentiment-chart');
        if (!chartContainer) return;

        const data = {
            positive: sentimentData.positive || 0,
            negative: sentimentData.negative || 0,
            neutral: sentimentData.neutral || 0
        };

        const total = Object.values(data).reduce((sum, val) => sum + val, 0);

        if (total === 0) {
            // Clear container and create safe empty state message
            chartContainer.innerHTML = '';
            const emptyMessage = document.createElement('p');
            emptyMessage.className = 'text-muted text-center';
            emptyMessage.textContent = 'لا توجد بيانات للعرض';
            chartContainer.appendChild(emptyMessage);
            return;
        }

        // Clear container and create wrapper using safe DOM methods
        chartContainer.innerHTML = '';
        const chartWrapper = document.createElement('div');
        chartWrapper.className = 'sentiment-chart';

        // Create sentiment items using safe DOM methods
        const sentimentItems = [
            { key: 'positive', label: 'إيجابي', class: 'positive' },
            { key: 'neutral', label: 'محايد', class: 'neutral' },
            { key: 'negative', label: 'سلبي', class: 'negative' }
        ];

        sentimentItems.forEach(item => {
            const chartItem = document.createElement('div');
            chartItem.className = 'chart-item';

            // Create chart bar with safe width calculation
            const chartBar = document.createElement('div');
            chartBar.className = `chart-bar ${item.class}`;
            const percentage = Math.max(0, Math.min(100, (data[item.key] / total) * 100));
            chartBar.style.width = `${percentage}%`;

            // Create chart label with safe text content
            const chartLabel = document.createElement('span');
            chartLabel.className = 'chart-label';
            chartLabel.textContent = `${item.label} (${ArabicUtils.formatNumber(data[item.key])})`;

            // Assemble the chart item
            chartItem.appendChild(chartBar);
            chartItem.appendChild(chartLabel);
            chartWrapper.appendChild(chartItem);
        });

        chartContainer.appendChild(chartWrapper);
    },

    /**
     * Update channel distribution chart
     */
    updateChannelChart(channelData) {
        const chartContainer = document.getElementById('channel-chart');
        if (!chartContainer || !channelData?.length) {
            if (chartContainer) {
                // Clear container and create safe empty state message
                chartContainer.innerHTML = '';
                const emptyMessage = document.createElement('p');
                emptyMessage.className = 'text-muted text-center';
                emptyMessage.textContent = 'لا توجد بيانات للعرض';
                chartContainer.appendChild(emptyMessage);
            }
            return;
        }

        const maxCount = Math.max(...channelData.map(ch => ch.feedback_count));

        // Clear container and create wrapper
        chartContainer.innerHTML = '';
        const chartWrapper = document.createElement('div');
        chartWrapper.className = 'channel-chart';

        // Create chart items using safe DOM methods
        channelData.forEach(channel => {
            const chartItem = document.createElement('div');
            chartItem.className = 'chart-item';

            // Create chart bar
            const chartBar = document.createElement('div');
            chartBar.className = 'chart-bar primary';
            chartBar.style.width = `${(channel.feedback_count / maxCount) * 100}%`;

            // Create chart label with safe text content
            const chartLabel = document.createElement('span');
            chartLabel.className = 'chart-label';
            chartLabel.textContent = `${UI.getChannelName(channel.channel)} (${ArabicUtils.formatNumber(channel.feedback_count)})`;

            // Assemble the chart item
            chartItem.appendChild(chartBar);
            chartItem.appendChild(chartLabel);
            chartWrapper.appendChild(chartItem);
        });

        chartContainer.appendChild(chartWrapper);
    },

    /**
     * Start auto-refresh for real-time updates
     */
    startAutoRefresh() {
        setInterval(() => {
            this.loadMetrics();
        }, CONFIG.REFRESH_INTERVAL);
    }
};

// Navigation Enhancement Functions
const Navigation = {
    /**
     * Initialize navigation enhancements
     */
    init() {
        this.highlightActivePage();
        this.addMobileOptimizations();
        this.addNavigationTooltips();
        this.initBackToTop();
    },

    /**
     * Highlight the current page in navigation
     */
    highlightActivePage() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link');

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });
    },

    /**
     * Add mobile-specific optimizations
     */
    addMobileOptimizations() {
        // Auto-close mobile menu when link is clicked
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        const navbarCollapse = document.getElementById('navbarNav');

        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth < 992 && navbarCollapse.classList.contains('show')) {
                    const bsCollapse = new bootstrap.Collapse(navbarCollapse);
                    bsCollapse.hide();
                }
            });
        });
    },

    /**
     * Add helpful tooltips to navigation items
     */
    addNavigationTooltips() {
        const tooltips = {
            '/': 'الصفحة الرئيسية للمنصة',
            '/dashboard/realtime': 'عرض التحليلات والمقاييس المباشرة',
            '/feedback': 'إرسال تعليق أو ملاحظة جديدة',
            '/surveys': 'إدارة وعرض الاستطلاعات',
            '/survey-builder': 'إنشاء استطلاع جديد',
            '/analytics': 'تحليلات مفصلة ومتقدمة'
        };

        Object.entries(tooltips).forEach(([path, tooltip]) => {
            const link = document.querySelector(`a[href="${path}"]`);
            if (link && !link.hasAttribute('title')) {
                link.setAttribute('title', tooltip);
            }
        });
    },

    /**
     * Initialize back to top functionality
     */
    initBackToTop() {
        // Create back to top button
        const backToTopBtn = document.createElement('button');
        backToTopBtn.innerHTML = '<i class="fas fa-chevron-up"></i>';
        backToTopBtn.className = 'back-to-top';
        backToTopBtn.style.cssText = `
            position: fixed;
            bottom: 30px;
            left: 30px;
            width: 50px;
            height: 50px;
            background: var(--primary-color);
            color: white;
            border: none;
            border-radius: 50%;
            font-size: 1.2rem;
            cursor: pointer;
            display: none;
            z-index: 1000;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        `;

        document.body.appendChild(backToTopBtn);

        // Show/hide button based on scroll position
        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 300) {
                backToTopBtn.style.display = 'block';
            } else {
                backToTopBtn.style.display = 'none';
            }
        });

        // Scroll to top when clicked
        backToTopBtn.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
};

// Enhanced Navigation Management
class NavigationManager {
    constructor() {
        this.initializeNavigation();
        this.handleActiveStates();
        this.initializeScrollEffects();
    }

    initializeNavigation() {
        // Auto-close dropdowns when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.dropdown')) {
                document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                    menu.classList.remove('show');
                });
            }
        });

        // Prevent dropdown close on internal clicks
        document.querySelectorAll('.dropdown-menu').forEach(menu => {
            menu.addEventListener('click', (e) => {
                e.stopPropagation();
            });
        });
    }

    handleActiveStates() {
        const currentPath = window.location.pathname;

        // Clear all active states
        document.querySelectorAll('.nav-link, .dropdown-item').forEach(link => {
            link.classList.remove('active');
        });

        // Set active state for current page
        document.querySelectorAll('.dropdown-item').forEach(item => {
            const href = item.getAttribute('href');
            if (href && currentPath === href) {
                item.classList.add('active');

                // Highlight parent dropdown
                const parentDropdown = item.closest('.dropdown');
                if (parentDropdown) {
                    parentDropdown.querySelector('.dropdown-toggle').classList.add('active');
                }
            }
        });
    }

    initializeScrollEffects() {
        const navbar = document.querySelector('.navbar');
        let lastScrollY = window.scrollY;

        window.addEventListener('scroll', () => {
            const currentScrollY = window.scrollY;

            if (currentScrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }

            lastScrollY = currentScrollY;
        });
    }
}

// Initialize enhanced navigation
document.addEventListener('DOMContentLoaded', () => {
    new NavigationManager();
});

// Initialization on DOM load
document.addEventListener('DOMContentLoaded', () => {
    // Initialize navigation enhancements
    Navigation.init();

    // Initialize language management
    LanguageToggle.init();

    // Initialize feedback form if present
    FeedbackManager.initForm();

    // Initialize dashboard if present
    if (document.getElementById('dashboard')) {
        Dashboard.init();
    }

    // Load feedback list if present
    if (document.getElementById('feedback-list')) {
        FeedbackManager.loadFeedbackList();
    }

    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add click-to-copy functionality for Arabic text
    document.querySelectorAll('.copyable').forEach(element => {
        element.addEventListener('click', async () => {
            try {
                await navigator.clipboard.writeText(element.textContent);
                UI.showAlert('تم نسخ النص', 'success', 2000);
            } catch (error) {
                console.error('Failed to copy text:', error);
            }
        });
    });

    console.log('Arabic Voice of Customer Platform initialized');
});

// Language Toggle System
const LanguageToggle = {
    init() {
        this.bindEvents();
        this.updateLanguageButton();
    },
    
    bindEvents() {
        // Add click handler for language toggle if button exists
        const toggleBtn = document.querySelector('[onclick="toggleLanguage()"]');
        if (toggleBtn) {
            toggleBtn.onclick = (e) => {
                e.preventDefault();
                this.toggleLanguage();
            };
        }
    },
    
    async toggleLanguage() {
        // Show loading state on button
        const button = document.querySelector('[onclick="toggleLanguage()"]');
        let originalContent = null;
        
        if (button) {
            // Store original content safely by cloning elements
            originalContent = Array.from(button.childNodes).map(node => node.cloneNode(true));
            button.disabled = true;
            
            // Clear button and add loading content safely
            button.textContent = '';
            const spinner = document.createElement('i');
            spinner.className = 'fas fa-spinner fa-spin me-1';
            button.appendChild(spinner);
            button.appendChild(document.createTextNode('Loading...'));
        }
        
        try {
            const response = await fetch('/api/language/toggle', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({})
            });
            
            if (response.ok) {
                // Reload page to apply language changes
                window.location.reload();
            } else {
                console.error('Language toggle failed');
                // Restore original button state safely
                if (button && originalContent) {
                    button.disabled = false;
                    button.textContent = '';
                    originalContent.forEach(node => button.appendChild(node));
                }
            }
        } catch (error) {
            console.error('Error toggling language:', error);
            // Restore original button state safely
            if (button && originalContent) {
                button.disabled = false;
                button.textContent = '';
                originalContent.forEach(node => button.appendChild(node));
            }
        }
    },
    
    async updateLanguageButton() {
        try {
            const response = await fetch('/api/language/status');
            if (response.ok) {
                const status = await response.json();
                const button = document.querySelector('[onclick="toggleLanguage()"]');
                if (button) {
                    const switchText = status.current_language === 'ar' ? 'English' : 'العربية';
                    const tooltip = status.current_language === 'ar' ? 'Switch to English' : 'تبديل اللغة إلى الإنجليزية';
                    
                    // Clear button content safely
                    button.textContent = '';
                    
                    // Create and append icon element
                    const icon = document.createElement('i');
                    icon.className = 'fas fa-globe me-1';
                    button.appendChild(icon);
                    
                    // Add text content safely
                    button.appendChild(document.createTextNode(switchText));
                    button.setAttribute('title', tooltip);
                }
            }
        } catch (error) {
            console.error('Error updating language button:', error);
        }
    }
};

// Global function for onclick handlers - Define immediately
function toggleLanguage() {
    if (typeof LanguageToggle !== 'undefined') {
        LanguageToggle.toggleLanguage();
    } else {
        console.error('LanguageToggle not yet loaded');
    }
}

// Make sure toggleLanguage is available globally immediately
window.toggleLanguage = toggleLanguage;

// Export other functions for global access
window.FeedbackManager = FeedbackManager;
window.Dashboard = Dashboard;
window.API = API;
window.UI = UI;
window.ArabicUtils = ArabicUtils;
window.LanguageToggle = LanguageToggle;