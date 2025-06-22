/**
 * Arabic-first Voice of Customer Platform - Main JavaScript
 * Handles client-side interactions, form submissions, and real-time updates
 */

// Global configuration
const CONFIG = {
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
        alert.innerHTML = `
            <span>${message}</span>
            <button type="button" class="btn-close" onclick="this.parentElement.remove()">×</button>
        `;
        
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
            element.innerHTML = originalText;
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
        
        return `
            <div class="feedback-item" data-id="${feedback.id}">
                <div class="feedback-meta">
                    <span class="sentiment-indicator ${sentimentClass}">
                        ${sentimentText}
                    </span>
                    <span class="feedback-date">
                        ${ArabicUtils.formatDate(feedback.created_at)}
                    </span>
                    <span class="feedback-channel">
                        ${this.getChannelName(feedback.channel)}
                    </span>
                </div>
                <div class="feedback-content">
                    ${feedback.content}
                </div>
                ${feedback.ai_summary ? `
                    <div class="feedback-summary">
                        <strong>الملخص:</strong> ${feedback.ai_summary}
                    </div>
                ` : ''}
                <div class="feedback-actions">
                    <button class="btn btn-outline btn-sm" onclick="FeedbackManager.viewDetails(${feedback.id})">
                        عرض التفاصيل
                    </button>
                </div>
            </div>
        `;
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
                container.innerHTML = `
                    <div class="text-center" style="padding: 2rem;">
                        <p class="text-muted">لا توجد تعليقات لعرضها</p>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = feedbackList
                .map(feedback => UI.createFeedbackItem(feedback))
                .join('');
                
        } catch (error) {
            container.innerHTML = `
                <div class="alert alert-danger">
                    خطأ في تحميل التعليقات: ${error.message}
                </div>
            `;
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
     * Show feedback details in modal
     */
    showDetailsModal(feedback) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>تفاصيل التعليق</h3>
                    <button class="btn-close" onclick="this.closest('.modal-overlay').remove()">×</button>
                </div>
                <div class="modal-body">
                    <div class="feedback-details">
                        <div class="detail-row">
                            <strong>المحتوى:</strong>
                            <p>${feedback.content}</p>
                        </div>
                        <div class="detail-row">
                            <strong>القناة:</strong>
                            <span>${UI.getChannelName(feedback.channel)}</span>
                        </div>
                        <div class="detail-row">
                            <strong>تاريخ الإرسال:</strong>
                            <span>${ArabicUtils.formatDate(feedback.created_at)}</span>
                        </div>
                        <div class="detail-row">
                            <strong>تحليل المشاعر:</strong>
                            <span class="${ArabicUtils.getSentimentClass(feedback.sentiment_score)}">
                                ${ArabicUtils.getSentimentText(feedback.sentiment_score)}
                                (${feedback.sentiment_score ? feedback.sentiment_score.toFixed(2) : 'غير محدد'})
                            </span>
                        </div>
                        ${feedback.ai_summary ? `
                            <div class="detail-row">
                                <strong>الملخص التلقائي:</strong>
                                <p>${feedback.ai_summary}</p>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
        
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
            chartContainer.innerHTML = '<p class="text-muted text-center">لا توجد بيانات للعرض</p>';
            return;
        }

        const chartHTML = `
            <div class="sentiment-chart">
                <div class="chart-item">
                    <div class="chart-bar positive" style="width: ${(data.positive / total) * 100}%"></div>
                    <span class="chart-label">إيجابي (${ArabicUtils.formatNumber(data.positive)})</span>
                </div>
                <div class="chart-item">
                    <div class="chart-bar neutral" style="width: ${(data.neutral / total) * 100}%"></div>
                    <span class="chart-label">محايد (${ArabicUtils.formatNumber(data.neutral)})</span>
                </div>
                <div class="chart-item">
                    <div class="chart-bar negative" style="width: ${(data.negative / total) * 100}%"></div>
                    <span class="chart-label">سلبي (${ArabicUtils.formatNumber(data.negative)})</span>
                </div>
            </div>
        `;

        chartContainer.innerHTML = chartHTML;
    },

    /**
     * Update channel distribution chart
     */
    updateChannelChart(channelData) {
        const chartContainer = document.getElementById('channel-chart');
        if (!chartContainer || !channelData?.length) {
            if (chartContainer) {
                chartContainer.innerHTML = '<p class="text-muted text-center">لا توجد بيانات للعرض</p>';
            }
            return;
        }

        const maxCount = Math.max(...channelData.map(ch => ch.feedback_count));

        const chartHTML = channelData.map(channel => `
            <div class="chart-item">
                <div class="chart-bar primary" style="width: ${(channel.feedback_count / maxCount) * 100}%"></div>
                <span class="chart-label">
                    ${UI.getChannelName(channel.channel)} (${ArabicUtils.formatNumber(channel.feedback_count)})
                </span>
            </div>
        `).join('');

        chartContainer.innerHTML = `<div class="channel-chart">${chartHTML}</div>`;
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

// Initialization on DOM load
document.addEventListener('DOMContentLoaded', () => {
    // Initialize navigation enhancements
    Navigation.init();
    
    // Initialize language management
    LanguageManager.initializeLanguage();
    
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

// Language Management System
const LanguageManager = {
    currentLanguage: 'ar',
    
    /**
     * Initialize language system
     */
    initializeLanguage() {
        const savedLang = localStorage.getItem('preferred_language') || 'ar';
        this.switchLanguage(savedLang);
        console.log('Language system initialized:', savedLang);
    },
    
    /**
     * Switch between Arabic and English
     */
    switchLanguage(lang) {
        this.currentLanguage = lang;
        localStorage.setItem('preferred_language', lang);
        
        // Update HTML direction and language
        document.documentElement.setAttribute('lang', lang);
        document.documentElement.setAttribute('dir', lang === 'ar' ? 'rtl' : 'ltr');
        
        // Update text content
        this.updatePageText(lang);
        
        console.log('Switched to language:', lang);
    },
    
    /**
     * Update page text based on language
     */
    updatePageText(lang) {
        const translations = {
            ar: {
                'langText': 'العربية',
                'platform-title-text': 'منصة صوت العميل العربية',
                'feedback-title-text': 'شاركنا رأيك',
                'feedback-subtitle-text': 'نقدر آرائكم وملاحظاتكم لتحسين خدماتنا وتجربتكم معنا',
                'nav-home-text': 'الرئيسية',
                'nav-analytics-text': 'لوحة التحليلات',
                'nav-feedback-text': 'إرسال تعليق',
                'nav-surveys-text': 'الاستطلاعات',
                'nav-login-text': 'تسجيل الدخول',
                'nav-register-text': 'إنشاء حساب',
                'rating-label-text': 'تقييمك العام:',
                'content-label-text': 'تعليقك أو ملاحظاتك:',
                'name-label-text': 'الاسم (اختياري):',
                'submit-btn-text': 'إرسال التعليق',
                'success-title-text': 'شكراً لك!',
                'success-message-text': 'تم إرسال تعليقك بنجاح وسيتم تحليله قريباً',
                'dialect-help-text': 'يمكنك الكتابة بأي لهجة عربية - سنفهمها جميعاً'
            },
            en: {
                'langText': 'English',
                'platform-title-text': 'Arabic Voice of Customer Platform',
                'feedback-title-text': 'Share Your Opinion',
                'feedback-subtitle-text': 'We value your feedback and suggestions to improve our services and your experience',
                'nav-home-text': 'Home',
                'nav-analytics-text': 'Analytics Dashboard',
                'nav-feedback-text': 'Submit Feedback',
                'nav-surveys-text': 'Surveys',
                'nav-login-text': 'Login',
                'nav-register-text': 'Register',
                'rating-label-text': 'Your Rating:',
                'content-label-text': 'Your Feedback:',
                'name-label-text': 'Name (Optional):',
                'submit-btn-text': 'Submit Feedback',
                'success-title-text': 'Thank You!',
                'success-message-text': 'Your feedback has been submitted successfully and will be analyzed shortly',
                'dialect-help-text': 'You can write in any Arabic dialect - we understand them all'
            }
        };
        
        const texts = translations[lang] || translations.ar;
        
        Object.entries(texts).forEach(([key, value]) => {
            const element = document.getElementById(key);
            if (element) {
                element.textContent = value;
                console.log('Updated', key, ':', value);
            }
        });
    }
};

/**
 * Global toggle language function
 */
function toggleLanguage() {
    const currentLang = LanguageManager.currentLanguage;
    const newLang = currentLang === 'ar' ? 'en' : 'ar';
    
    console.log('Switching to:', newLang);
    LanguageManager.switchLanguage(newLang);
}

// Export functions for global access
window.FeedbackManager = FeedbackManager;
window.Dashboard = Dashboard;
window.API = API;
window.UI = UI;
window.ArabicUtils = ArabicUtils;
window.LanguageManager = LanguageManager;
window.toggleLanguage = toggleLanguage;
window.langManager = LanguageManager;
