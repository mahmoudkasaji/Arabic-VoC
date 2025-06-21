/**
 * Simple, reliable language toggle for immediate UX feedback
 * No complex frameworks - just direct DOM manipulation
 */

// Translation data
const translations = {
    'ar': {
        // Navigation
        'nav-home': 'الرئيسية',
        'nav-analytics': 'لوحة التحليلات', 
        'nav-feedback': 'إرسال تعليق',
        'nav-surveys': 'الاستطلاعات',
        'nav-login': 'تسجيل الدخول',
        'nav-register': 'إنشاء حساب',
        'platform-title': 'منصة صوت العميل العربية',
        
        // Feedback page
        'feedback-title': 'شاركنا رأيك',
        'feedback-subtitle': 'نقدر آرائكم وملاحظاتكم لتحسين خدماتنا وتجربتكم معنا',
        'rating-label': 'تقييمك العام:',
        'content-label': 'تعليقك أو ملاحظاتك:',
        'content-placeholder': 'شاركنا تجربتك ورأيك بالتفصيل...',
        'name-label': 'الاسم (اختياري):',
        'name-placeholder': 'أدخل اسمك',
        'submit-btn': 'إرسال التعليق',
        'success-title': 'شكراً لك!',
        'success-message': 'تم إرسال تعليقك بنجاح وسيتم تحليله قريباً',
        'dialect-help': 'يمكنك الكتابة بأي لهجة عربية - سنفهمها جميعاً',
        
        // Button text
        'lang-toggle': 'English'
    },
    'en': {
        // Navigation  
        'nav-home': 'Home',
        'nav-analytics': 'Analytics Dashboard',
        'nav-feedback': 'Submit Feedback', 
        'nav-surveys': 'Surveys',
        'nav-login': 'Login',
        'nav-register': 'Register',
        'platform-title': 'Arabic Voice of Customer Platform',
        
        // Feedback page
        'feedback-title': 'Share Your Opinion',
        'feedback-subtitle': 'We value your feedback and suggestions to improve our services and your experience',
        'rating-label': 'Your Overall Rating:',
        'content-label': 'Your Comments or Feedback:',
        'content-placeholder': 'Share your experience and opinion in detail...',
        'name-label': 'Name (Optional):',
        'name-placeholder': 'Enter your name',
        'submit-btn': 'Submit Feedback',
        'success-title': 'Thank You!',
        'success-message': 'Your feedback has been successfully submitted and will be analyzed soon',
        'dialect-help': 'You can write in any Arabic dialect - we understand them all',
        
        // Button text
        'lang-toggle': 'العربية'
    }
};

// Current language state
let currentLang = localStorage.getItem('language') || 'ar';

// Toggle language function
function toggleLanguage() {
    // Switch language
    currentLang = currentLang === 'ar' ? 'en' : 'ar';
    
    // Update document attributes immediately
    document.documentElement.lang = currentLang;
    document.documentElement.dir = currentLang === 'ar' ? 'rtl' : 'ltr';
    
    // Update body direction and alignment
    document.body.style.direction = currentLang === 'ar' ? 'rtl' : 'ltr';
    document.body.style.textAlign = currentLang === 'ar' ? 'right' : 'left';
    
    // Update all translatable elements immediately
    updateAllTexts();
    
    // Save preference
    localStorage.setItem('language', currentLang);
    
    console.log('Language switched to:', currentLang);
}

// Update all text elements
function updateAllTexts() {
    const langData = translations[currentLang];
    
    // Update elements by ID
    const idMappings = {
        'platform-title-text': 'platform-title',
        'feedback-title-text': 'feedback-title', 
        'feedback-subtitle-text': 'feedback-subtitle',
        'nav-home-text': 'nav-home',
        'nav-analytics-text': 'nav-analytics',
        'nav-feedback-text': 'nav-feedback',
        'nav-surveys-text': 'nav-surveys',
        'nav-login-text': 'nav-login',
        'nav-register-text': 'nav-register',
        'rating-label-text': 'rating-label',
        'content-label-text': 'content-label',
        'name-label-text': 'name-label',
        'submit-btn-text': 'submit-btn',
        'success-title-text': 'success-title',
        'success-message-text': 'success-message',
        'dialect-help-text': 'dialect-help'
    };
    
    // Update text content
    Object.keys(idMappings).forEach(elementId => {
        const element = document.getElementById(elementId);
        const translationKey = idMappings[elementId];
        if (element && langData[translationKey]) {
            element.textContent = langData[translationKey];
        }
    });
    
    // Update placeholders
    const placeholderMappings = {
        'content': 'content-placeholder',
        'customerName': 'name-placeholder'
    };
    
    Object.keys(placeholderMappings).forEach(elementId => {
        const element = document.getElementById(elementId);
        const translationKey = placeholderMappings[elementId];
        if (element && langData[translationKey]) {
            element.placeholder = langData[translationKey];
        }
    });
    
    // Update toggle button
    const langText = document.getElementById('langText');
    if (langText && langData['lang-toggle']) {
        langText.textContent = langData['lang-toggle'];
    }
}

// Initialize language on page load
document.addEventListener('DOMContentLoaded', function() {
    // Set initial language attributes
    document.documentElement.lang = currentLang;
    document.documentElement.dir = currentLang === 'ar' ? 'rtl' : 'ltr';
    document.body.style.direction = currentLang === 'ar' ? 'rtl' : 'ltr';
    document.body.style.textAlign = currentLang === 'ar' ? 'right' : 'left';
    
    // Update all texts
    updateAllTexts();
    
    console.log('Language system initialized with:', currentLang);
});