/**
 * Internationalization (i18n) System for Arabic Voice of Customer Platform
 * Comprehensive bilingual support with Arabic-first design
 */

class LanguageManager {
    constructor() {
        this.currentLang = 'ar';
        this.translations = {
            ar: {
                // Navigation
                nav: {
                    home: 'الرئيسية',
                    feedback: 'إرسال تعليق',
                    analytics: 'التحليلات المباشرة',
                    surveys: 'الاستطلاعات',
                    login: 'تسجيل الدخول',
                    register: 'إنشاء حساب'
                },
                // Homepage
                home: {
                    title: 'منصة صوت العميل العربية',
                    subtitle: 'منصة متقدمة لتحليل آراء العملاء باللغة العربية مع دعم اللهجات المختلفة والذكاء الثقافي',
                    cta_feedback: 'شارك رأيك الآن',
                    cta_analytics: 'اعرض لوحة التحليلات',
                    features_title: 'المميزات الرئيسية',
                    features_subtitle: 'منصة شاملة مصممة خصيصاً للسوق العربي'
                },
                // Features
                features: {
                    realtime_title: 'تحليلات في الوقت الفعلي',
                    realtime_desc: 'اطلع على تحليل المشاعر والاتجاهات لحظة بلحظة مع لوحة تحكم تفاعلية تدعم التحديثات المباشرة أقل من ثانية واحدة',
                    dialect_title: 'دعم اللهجات العربية',
                    dialect_desc: 'معالجة متقدمة للهجات الخليجية والمصرية والشامية والمغربية مع فهم السياق الثقافي والتعبيرات المحلية',
                    multichannel_title: 'متعدد القنوات',
                    multichannel_desc: 'جمع التعليقات من الموقع الإلكتروني ووسائل التواصل الاجتماعي والهاتف والبريد الإلكتروني والمزيد'
                },
                // Feedback Form
                feedback: {
                    title: 'شاركنا رأيك',
                    subtitle: 'نقدر آراءكم وملاحظاتكم لتطوير خدماتنا',
                    content_label: 'التعليق *',
                    content_placeholder: 'اكتب تعليقك هنا...',
                    channel_label: 'القناة',
                    channel_placeholder: 'اختر القناة...',
                    channel_website: 'الموقع الإلكتروني',
                    channel_mobile: 'التطبيق الجوال',
                    channel_social: 'وسائل التواصل الاجتماعي',
                    channel_email: 'البريد الإلكتروني',
                    channel_phone: 'الهاتف',
                    channel_whatsapp: 'واتساب',
                    channel_person: 'شخصياً',
                    rating_label: 'التقييم',
                    email_label: 'البريد الإلكتروني (اختياري)',
                    submit: 'إرسال التعليق',
                    success: 'تم إرسال تعليقك بنجاح!'
                },
                // Dashboard
                dashboard: {
                    title: 'لوحة التحليلات المباشرة',
                    sentiment_title: 'تحليل المشاعر',
                    trends_title: 'الاتجاهات',
                    channels_title: 'القنوات',
                    metrics_title: 'المقاييس الرئيسية'
                },
                // Common
                common: {
                    loading: 'جاري التحميل...',
                    error: 'حدث خطأ',
                    success: 'تم بنجاح',
                    cancel: 'إلغاء',
                    save: 'حفظ',
                    delete: 'حذف',
                    edit: 'تعديل',
                    back: 'العودة'
                }
            },
            en: {
                // Navigation
                nav: {
                    home: 'Home',
                    feedback: 'Submit Feedback',
                    analytics: 'Real-time Analytics',
                    surveys: 'Surveys',
                    login: 'Login',
                    register: 'Register'
                },
                // Homepage
                home: {
                    title: 'Arabic Voice of Customer Platform',
                    subtitle: 'Advanced platform for Arabic customer feedback analysis with dialect support and cultural intelligence',
                    cta_feedback: 'Share Your Feedback',
                    cta_analytics: 'View Analytics Dashboard',
                    features_title: 'Key Features',
                    features_subtitle: 'Comprehensive platform designed specifically for the Arabic market'
                },
                // Features
                features: {
                    realtime_title: 'Real-time Analytics',
                    realtime_desc: 'View sentiment analysis and trends moment by moment with an interactive dashboard supporting real-time updates in less than one second',
                    dialect_title: 'Arabic Dialect Support',
                    dialect_desc: 'Advanced processing for Gulf, Egyptian, Levantine, and Maghrebi dialects with cultural context understanding and local expressions',
                    multichannel_title: 'Multi-Channel',
                    multichannel_desc: 'Collect feedback from website, social media, phone, email, and more channels seamlessly'
                },
                // Feedback Form
                feedback: {
                    title: 'Share Your Feedback',
                    subtitle: 'We value your opinions and feedback to improve our services',
                    content_label: 'Feedback *',
                    content_placeholder: 'Write your feedback here...',
                    channel_label: 'Channel',
                    channel_placeholder: 'Select channel...',
                    channel_website: 'Website',
                    channel_mobile: 'Mobile App',
                    channel_social: 'Social Media',
                    channel_email: 'Email',
                    channel_phone: 'Phone',
                    channel_whatsapp: 'WhatsApp',
                    channel_person: 'In Person',
                    rating_label: 'Rating',
                    email_label: 'Email (Optional)',
                    submit: 'Submit Feedback',
                    success: 'Your feedback has been submitted successfully!'
                },
                // Dashboard
                dashboard: {
                    title: 'Real-time Analytics Dashboard',
                    sentiment_title: 'Sentiment Analysis',
                    trends_title: 'Trends',
                    channels_title: 'Channels',
                    metrics_title: 'Key Metrics'
                },
                // Common
                common: {
                    loading: 'Loading...',
                    error: 'An error occurred',
                    success: 'Success',
                    cancel: 'Cancel',
                    save: 'Save',
                    delete: 'Delete',
                    edit: 'Edit',
                    back: 'Back'
                }
            }
        };
        
        this.init();
    }
    
    init() {
        // Load saved language preference
        const savedLang = localStorage.getItem('preferred-language') || 'ar';
        this.setLanguage(savedLang);
        
        // Set up language toggle button
        this.setupToggleButton();
    }
    
    setLanguage(lang) {
        this.currentLang = lang;
        
        // Update document attributes
        document.documentElement.setAttribute('lang', lang);
        document.documentElement.setAttribute('dir', lang === 'ar' ? 'rtl' : 'ltr');
        
        // Update all translatable elements
        this.updateAllTranslations();
        
        // Update layout direction
        this.updateLayoutDirection();
        
        // Update toggle button
        this.updateToggleButton();
        
        // Save preference
        localStorage.setItem('preferred-language', lang);
    }
    
    toggleLanguage() {
        const newLang = this.currentLang === 'ar' ? 'en' : 'ar';
        this.setLanguage(newLang);
    }
    
    getText(key) {
        const keys = key.split('.');
        let value = this.translations[this.currentLang];
        
        for (const k of keys) {
            value = value?.[k];
        }
        
        return value || key;
    }
    
    updateAllTranslations() {
        // Update elements with data-i18n attributes
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            const text = this.getText(key);
            
            if (element.tagName === 'INPUT' && (element.type === 'text' || element.type === 'email')) {
                element.placeholder = text;
            } else if (element.tagName === 'TEXTAREA') {
                element.placeholder = text;
            } else if (element.tagName === 'OPTION') {
                element.textContent = text;
            } else {
                element.textContent = text;
            }
        });
        
        // Update elements with data-i18n-placeholder attributes
        document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
            const key = element.getAttribute('data-i18n-placeholder');
            const text = this.getText(key);
            element.placeholder = text;
        });
        
        // Update legacy class-based elements
        this.updateLegacyElements();
    }
    
    updateLegacyElements() {
        const arElements = document.querySelectorAll('.nav-text-ar, .hero-text-ar, .hero-desc-ar, .btn-text-ar, .feature-title-ar, .feature-desc-ar, .card-title-ar, .card-text-ar');
        const enElements = document.querySelectorAll('.nav-text-en, .hero-text-en, .hero-desc-en, .btn-text-en, .feature-title-en, .feature-desc-en, .card-title-en, .card-text-en');
        
        if (this.currentLang === 'ar') {
            arElements.forEach(el => el.classList.remove('d-none'));
            enElements.forEach(el => el.classList.add('d-none'));
        } else {
            arElements.forEach(el => el.classList.add('d-none'));
            enElements.forEach(el => el.classList.remove('d-none'));
        }
    }
    
    updateLayoutDirection() {
        const body = document.body;
        
        if (this.currentLang === 'ar') {
            body.style.direction = 'rtl';
            body.style.textAlign = 'right';
            body.classList.add('rtl-layout');
            body.classList.remove('ltr-layout');
        } else {
            body.style.direction = 'ltr';
            body.style.textAlign = 'left';
            body.classList.add('ltr-layout');
            body.classList.remove('rtl-layout');
        }
    }
    
    updateToggleButton() {
        const langText = document.getElementById('langText');
        const brandText = document.getElementById('brandText');
        
        if (langText) {
            langText.textContent = this.currentLang === 'ar' ? 'English' : 'العربية';
        }
        
        if (brandText) {
            brandText.textContent = this.getText('home.title');
        }
        
        // Update page title
        const titleKey = this.getPageTitleKey();
        if (titleKey) {
            document.title = this.getText(titleKey);
        }
    }
    
    getPageTitleKey() {
        const path = window.location.pathname;
        const titleMap = {
            '/': 'home.title',
            '/feedback': 'feedback.title',
            '/dashboard/realtime': 'dashboard.title',
            '/surveys': 'surveys.title'
        };
        return titleMap[path];
    }
    
    setupToggleButton() {
        // Make toggle function globally available
        window.toggleLanguage = () => this.toggleLanguage();
    }
    
    // Utility method for dynamic content
    formatDate(date, format = 'short') {
        const options = {
            short: { year: 'numeric', month: 'short', day: 'numeric' },
            long: { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' }
        };
        
        const locale = this.currentLang === 'ar' ? 'ar-SA' : 'en-US';
        return new Intl.DateTimeFormat(locale, options[format]).format(date);
    }
    
    formatNumber(number, decimals = 0) {
        const locale = this.currentLang === 'ar' ? 'ar-SA' : 'en-US';
        return new Intl.NumberFormat(locale, {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(number);
    }
}

// Initialize language manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.languageManager = new LanguageManager();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LanguageManager;
}