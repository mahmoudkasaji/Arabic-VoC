class LanguageManager {
    constructor() {
        this.currentLang = localStorage.getItem('language') || 'en';
        this.translations = {
            'ar': {
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
            'en': {
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
                'rating-label-text': 'Your Overall Rating:',
                'content-label-text': 'Your Feedback or Comments:',
                'name-label-text': 'Name (Optional):',
                'submit-btn-text': 'Submit Feedback',
                'success-title-text': 'Thank You!',
                'success-message-text': 'Your feedback has been submitted successfully and will be analyzed soon',
                'dialect-help-text': 'You can write in any Arabic dialect - we understand them all'
            }
        };
    }

    init() {
        this.applyLanguage(this.currentLang);
        this.setupLanguageToggle();
    }

    initializeLanguage() {
        this.init();
    }

    setupLanguageToggle() {
        const toggleBtn = document.getElementById('languageToggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggleLanguage());
        }
    }

    toggleLanguage() {
        this.currentLang = this.currentLang === 'ar' ? 'en' : 'ar';
        this.applyLanguage(this.currentLang);
        localStorage.setItem('language', this.currentLang);
    }

    applyLanguage(lang) {
        console.log('Switching to:', lang);

        // Update text content
        Object.keys(this.translations[lang]).forEach(key => {
            const element = document.getElementById(key);
            if (element) {
                element.textContent = this.translations[lang][key];
                console.log('Updated', key, ':', this.translations[lang][key]);
            }
        });

        // Update document direction
        document.documentElement.setAttribute('dir', lang === 'ar' ? 'rtl' : 'ltr');
        document.documentElement.setAttribute('lang', lang);

        // Update body class for styling
        document.body.className = document.body.className.replace(/lang-\w+/, '');
        document.body.classList.add(`lang-${lang}`);
    }
}

// Global toggle function for backward compatibility
function toggleLanguage() {
    if (window.langManager) {
        window.langManager.toggleLanguage();
    } else {
        console.warn('Language manager not initialized');
    }
}

// Make LanguageManager available globally
window.LanguageManager = LanguageManager;
window.toggleLanguage = toggleLanguage;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.langManager = new LanguageManager();
    window.langManager.init();
});