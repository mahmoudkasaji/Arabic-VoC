/**
 * JavaScript Translation System for Voice of Customer Platform
 * Provides client-side bilingual support
 */

// Global translation loader
window.TranslationManager = {
    currentLanguage: 'ar',
    translations: {
        ar: {
            // Survey Builder
            survey_builder: {
                drag_hint: 'اسحب السؤال هنا',
                next_step: 'الخطوة التالية',
                add_question: 'إضافة سؤال',
                question_types: {
                    short_text: 'نص قصير',
                    long_text: 'نص طويل',
                    multiple_choice: 'اختيار متعدد',
                    checkbox: 'مربعات اختيار',
                    dropdown: 'قائمة منسدلة',
                    rating: 'تقييم',
                    slider: 'شريط التمرير',
                    nps: 'مقياس التوصية',
                    email: 'بريد إلكتروني',
                    phone: 'رقم الهاتف',
                    date: 'تاريخ',
                    time: 'وقت'
                },
                default_questions: {
                    text: 'سؤال نص قصير',
                    textarea: 'سؤال نص طويل',
                    multiple_choice: 'سؤال اختيار متعدد',
                    checkbox: 'سؤال مربعات اختيار',
                    dropdown: 'سؤال قائمة منسدلة',
                    rating: 'سؤال تقييم',
                    slider: 'سؤال مؤشر تمرير',
                    nps: 'ما مدى احتمالية أن توصي بنا؟',
                    date: 'سؤال تاريخ',
                    email: 'سؤال بريد إلكتروني',
                    phone: 'سؤال رقم هاتف'
                },
                placeholders: {
                    short_text: 'إجابة نصية قصيرة',
                    long_text: 'اكتب إجابة نصية طويلة',
                    email: 'example@domain.com',
                    phone: '+966 50 123 4567'
                },
                options: {
                    option_1: 'الخيار الأول',
                    option_2: 'الخيار الثاني',
                    option_3: 'الخيار الثالث',
                    add_option: 'إضافة خيار'
                },
                rating_labels: {
                    very_poor: 'ضعيف جداً',
                    poor: 'ضعيف',
                    average: 'متوسط',
                    good: 'جيد',
                    excellent: 'ممتاز'
                },
                slider_labels: {
                    min: 'الأدنى',
                    max: 'الأعلى'
                },
                nps_labels: {
                    not_recommend: 'لن أوصي أبداً',
                    will_recommend: 'سأوصي بقوة'
                },
                mobile_add: {
                    prefix: 'إضافة: '
                }
            },
            // Feedback Widget
            feedback: {
                title: 'إرسال تعليق',
                placeholder: 'اكتب تعليقك هنا...',
                submit: 'إرسال',
                cancel: 'إلغاء',
                success: 'تم إرسال التعليق بنجاح',
                error: 'حدث خطأ في إرسال التعليق'
            },
            // Common UI
            common: {
                loading: 'جاري التحميل...',
                save: 'حفظ',
                cancel: 'إلغاء',
                edit: 'تعديل',
                delete: 'حذف',
                confirm: 'تأكيد',
                close: 'إغلاق',
                back: 'رجوع',
                next: 'التالي',
                previous: 'السابق'
            }
        },
        en: {
            // Survey Builder
            survey_builder: {
                drag_hint: 'Drag question here',
                next_step: 'Next Step',
                add_question: 'Add Question',
                question_types: {
                    short_text: 'Short Text',
                    long_text: 'Long Text',
                    multiple_choice: 'Multiple Choice',
                    checkbox: 'Checkboxes',
                    dropdown: 'Dropdown',
                    rating: 'Rating',
                    slider: 'Slider',
                    nps: 'NPS Score',
                    email: 'Email',
                    phone: 'Phone',
                    date: 'Date',
                    time: 'Time'
                },
                default_questions: {
                    text: 'Short text question',
                    textarea: 'Long text question',
                    multiple_choice: 'Multiple choice question',
                    checkbox: 'Checkbox question',
                    dropdown: 'Dropdown question',
                    rating: 'Rating question',
                    slider: 'Slider question',
                    nps: 'How likely are you to recommend us?',
                    date: 'Date question',
                    email: 'Email question',
                    phone: 'Phone question'
                },
                placeholders: {
                    short_text: 'Short text answer',
                    long_text: 'Write a longer text answer',
                    email: 'example@domain.com',
                    phone: '+966 50 123 4567'
                },
                options: {
                    option_1: 'Option 1',
                    option_2: 'Option 2',
                    option_3: 'Option 3',
                    add_option: 'Add Option'
                },
                rating_labels: {
                    very_poor: 'Very Poor',
                    poor: 'Poor',
                    average: 'Average',
                    good: 'Good',
                    excellent: 'Excellent'
                },
                slider_labels: {
                    min: 'Minimum',
                    max: 'Maximum'
                },
                nps_labels: {
                    not_recommend: 'Not at all likely',
                    will_recommend: 'Extremely likely'
                },
                mobile_add: {
                    prefix: 'Add: '
                }
            },
            // Feedback Widget
            feedback: {
                title: 'Submit Feedback',
                placeholder: 'Write your feedback here...',
                submit: 'Submit',
                cancel: 'Cancel',
                success: 'Feedback submitted successfully',
                error: 'Error submitting feedback'
            },
            // Common UI
            common: {
                loading: 'Loading...',
                save: 'Save',
                cancel: 'Cancel',
                edit: 'Edit',
                delete: 'Delete',
                confirm: 'Confirm',
                close: 'Close',
                back: 'Back',
                next: 'Next',
                previous: 'Previous'
            }
        }
    },

    // Initialize with current language from HTML
    init() {
        const htmlLang = document.documentElement.lang || 'ar';
        this.currentLanguage = htmlLang;
        console.log(`🌐 Translation Manager initialized with language: ${this.currentLanguage} (from HTML lang attribute)`);
        
        // Validate language is supported
        if (!this.translations[this.currentLanguage]) {
            console.warn(`⚠️ Language ${this.currentLanguage} not supported, falling back to Arabic`);
            this.currentLanguage = 'ar';
        }
    },

    // Get translation for a key
    t(key, defaultValue = null) {
        const keys = key.split('.');
        let translation = this.translations[this.currentLanguage];
        
        for (const k of keys) {
            if (translation && translation[k]) {
                translation = translation[k];
            } else {
                // Fallback to other language
                const fallbackLang = this.currentLanguage === 'ar' ? 'en' : 'ar';
                let fallbackTranslation = this.translations[fallbackLang];
                
                for (const k of keys) {
                    if (fallbackTranslation && fallbackTranslation[k]) {
                        fallbackTranslation = fallbackTranslation[k];
                    } else {
                        return defaultValue || `[${key}]`;
                    }
                }
                return fallbackTranslation;
            }
        }
        
        return translation || defaultValue || `[${key}]`;
    },

    // Update language
    setLanguage(lang) {
        if (this.translations[lang]) {
            this.currentLanguage = lang;
            console.log(`🌐 Language changed to: ${lang}`);
            return true;
        }
        return false;
    },

    // Get current language
    getCurrentLanguage() {
        return this.currentLanguage;
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.TranslationManager.init();
});

// Make available globally as shorthand
window.t = function(key, defaultValue) {
    return window.TranslationManager.t(key, defaultValue);
};