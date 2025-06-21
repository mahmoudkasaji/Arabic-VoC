
class LanguageManager {
    constructor() {
        this.currentLang = 'ar';
        this.translations = {
            ar: {
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
                'dialect-help-text': 'يمكنك الكتابة بأي لهجة عربية - سنفهمها جميعاً',
                'langText': 'English'
            },
            en: {
                'platform-title-text': 'Arabic Voice of Customer Platform',
                'feedback-title-text': 'Share Your Opinion',
                'feedback-subtitle-text': 'We value your feedback and suggestions to improve our services and your experience',
                'nav-home-text': 'Home',
                'nav-analytics-text': 'Analytics Dashboard',
                'nav-feedback-text': 'Send Feedback',
                'nav-surveys-text': 'Surveys',
                'nav-login-text': 'Login',
                'nav-register-text': 'Register',
                'rating-label-text': 'Your Overall Rating:',
                'content-label-text': 'Your Feedback or Comments:',
                'name-label-text': 'Name (Optional):',
                'submit-btn-text': 'Submit Feedback',
                'success-title-text': 'Thank You!',
                'success-message-text': 'Your feedback has been submitted successfully and will be analyzed soon',
                'dialect-help-text': 'You can write in any Arabic dialect - we understand them all',
                'langText': 'العربية'
            }
        };
    }

    initializeLanguage() {
        this.currentLang = localStorage.getItem('preferred-language') || 'ar';
        this.applyLanguage(this.currentLang);
    }

    toggleLanguage() {
        this.currentLang = this.currentLang === 'ar' ? 'en' : 'ar';
        this.applyLanguage(this.currentLang);
        localStorage.setItem('preferred-language', this.currentLang);
    }

    applyLanguage(lang) {
        // Update document attributes
        document.documentElement.lang = lang;
        document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';

        // Update all translatable elements
        const translations = this.translations[lang];
        Object.keys(translations).forEach(key => {
            const elements = document.querySelectorAll(`[data-i18n="${key}"], #${key}`);
            elements.forEach(element => {
                console.log('Updated', key, ':', translations[key]);
                if (element.tagName === 'INPUT' && element.type === 'submit') {
                    element.value = translations[key];
                } else {
                    element.textContent = translations[key];
                }
            });
        });

        // Update language toggle button specifically
        const langText = document.getElementById('langText');
        if (langText) {
            langText.textContent = translations['langText'];
        }

        console.log('Switching to:', lang);
        this.currentLang = lang;
    }
}

// Global functions for backward compatibility
function toggleLanguage() {
    if (window.langManager) {
        window.langManager.toggleLanguage();
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.langManager = new LanguageManager();
    window.langManager.initializeLanguage();
});
