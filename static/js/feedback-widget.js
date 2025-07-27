/**
 * Persistent Feedback Widget for Voice of Customer Platform
 * Lightweight, accessible, and culturally appropriate for Arabic users
 */

class FeedbackWidget {
    constructor(options = {}) {
        this.options = {
            position: 'bottom-right', // bottom-left for RTL
            submitEndpoint: '/feedback-widget',
            configEndpoint: '/feedback-widget/config',
            categories: [
                'تحسين المنتج', 'مشكلة تقنية', 'اقتراح ميزة', 
                'سهولة الاستخدام', 'الأداء', 'أخرى'
            ],
            labels: {
                ar: {
                    trigger: 'رأيك',
                    title: 'شاركنا رأيك',
                    rating: 'كيف تقيم تجربتك؟',
                    category: 'ما نوع الملاحظة؟',
                    comment: 'اكتب ملاحظتك هنا...',
                    submit: 'إرسال الملاحظة',
                    success: 'شكراً لك!',
                    successMessage: 'تم إرسال ملاحظتك بنجاح. سنعمل على تحسين تجربتك.'
                },
                en: {
                    trigger: 'Feedback',
                    title: 'Share Your Feedback',
                    rating: 'How would you rate your experience?',
                    category: 'What type of feedback?',
                    comment: 'Write your feedback here...',
                    submit: 'Submit Feedback',
                    success: 'Thank You!',
                    successMessage: 'Your feedback has been submitted successfully. We value your input.'
                }
            },
            ...options
        };

        this.currentLang = document.documentElement.lang || 'ar';
        this.isRTL = document.documentElement.dir === 'rtl';
        this.rating = 0;
        this.category = '';
        this.isSubmitting = false;

        this.init();
    }

    init() {
        this.createWidget();
        this.attachEventListeners();
        this.setupAccessibility();
    }

    createWidget() {
        // Create main widget container
        this.widget = document.createElement('div');
        this.widget.className = 'feedback-widget';
        this.widget.setAttribute('dir', this.isRTL ? 'rtl' : 'ltr');

        // Create trigger button
        const trigger = document.createElement('button');
        trigger.className = 'feedback-trigger';
        trigger.setAttribute('aria-label', this.getLabel('trigger'));
        trigger.innerHTML = `
            <i class="fas fa-comment feedback-icon" aria-hidden="true"></i>
            <span class="feedback-text">${this.getLabel('trigger')}</span>
        `;

        // Create modal
        const modal = document.createElement('div');
        modal.className = 'feedback-modal';
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-modal', 'true');
        modal.setAttribute('aria-labelledby', 'feedback-title');
        modal.innerHTML = this.createModalContent();

        this.widget.appendChild(trigger);
        this.widget.appendChild(modal);
        document.body.appendChild(this.widget);

        // Store references
        this.triggerBtn = trigger;
        this.modal = modal;
        this.form = modal.querySelector('.feedback-form');
    }

    createModalContent() {
        const labels = this.options.labels[this.currentLang];
        const categories = this.options.categories;

        return `
            <div class="feedback-modal-content">
                <div class="feedback-modal-header">
                    <h2 id="feedback-title" class="feedback-modal-title">${labels.title}</h2>
                    <button class="feedback-modal-close" aria-label="Close feedback modal">
                        <i class="fas fa-times" aria-hidden="true"></i>
                    </button>
                </div>
                <div class="feedback-modal-body">
                    <form class="feedback-form" role="form" method="POST" action="/feedback-widget">
                        <!-- Hidden fields for tracking -->
                        <input type="hidden" name="page_url" id="page-url" value="">
                        <input type="hidden" name="page_title" id="page-title" value="">
                        <input type="hidden" name="rating" id="selected-rating" value="">
                        <input type="hidden" name="category" id="selected-category" value="">
                        
                        <!-- Rating Section -->
                        <div class="feedback-rating">
                            <label class="feedback-rating-label">${labels.rating}</label>
                            <div class="rating-stars" role="radiogroup" aria-label="${labels.rating}">
                                ${[1,2,3,4,5].map(num => `
                                    <span class="rating-star" 
                                          data-rating="${num}" 
                                          role="radio" 
                                          aria-checked="false"
                                          tabindex="0"
                                          aria-label="${num} نجمة">⭐</span>
                                `).join('')}
                            </div>
                        </div>

                        <!-- Category Section -->
                        <div class="feedback-category">
                            <label class="feedback-rating-label">${labels.category}</label>
                            <div class="category-buttons" role="radiogroup" aria-label="${labels.category}">
                                ${categories.map(cat => `
                                    <button type="button" 
                                            class="category-btn" 
                                            data-category="${cat}"
                                            role="radio"
                                            aria-checked="false">${cat}</button>
                                `).join('')}
                            </div>
                        </div>

                        <!-- Comment Section -->
                        <div class="feedback-comment">
                            <label class="feedback-rating-label" for="feedback-text">تفاصيل إضافية (اختياري)</label>
                            <textarea class="feedback-textarea" 
                                      id="feedback-text"
                                      name="comment"
                                      placeholder="${labels.comment}"
                                      maxlength="500"
                                      aria-describedby="char-count"></textarea>
                            <small id="char-count" class="text-muted">0/500 حرف</small>
                        </div>

                        <!-- Submit Button -->
                        <button type="submit" class="feedback-submit" disabled>
                            <span class="submit-text">${labels.submit}</span>
                            <div class="submit-spinner" style="display: none;"></div>
                        </button>
                    </form>

                    <!-- Success Message (hidden initially) -->
                    <div class="feedback-success" style="display: none;">
                        <div class="feedback-success-icon">✅</div>
                        <h3 class="feedback-success-title">${labels.success}</h3>
                        <p class="feedback-success-message">${labels.successMessage}</p>
                    </div>
                </div>
            </div>
        `;
    }

    attachEventListeners() {
        // Trigger button
        this.triggerBtn.addEventListener('click', () => this.openModal());

        // Close button
        this.modal.querySelector('.feedback-modal-close').addEventListener('click', () => this.closeModal());

        // Modal backdrop click
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) this.closeModal();
        });

        // Rating stars
        this.modal.querySelectorAll('.rating-star').forEach(star => {
            star.addEventListener('click', () => this.setRating(parseInt(star.dataset.rating)));
            star.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.setRating(parseInt(star.dataset.rating));
                }
            });
        });

        // Category buttons
        this.modal.querySelectorAll('.category-btn').forEach(btn => {
            btn.addEventListener('click', () => this.setCategory(btn.dataset.category));
        });

        // Form submission
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitFeedback();
        });

        // Character counter
        const textarea = this.modal.querySelector('.feedback-textarea');
        const charCount = this.modal.querySelector('#char-count');
        textarea.addEventListener('input', () => {
            const count = textarea.value.length;
            charCount.textContent = `${count}/500 حرف`;
        });

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.classList.contains('active')) {
                this.closeModal();
            }
        });

        // Form validation
        this.modal.addEventListener('input', () => this.validateForm());
    }

    setupAccessibility() {
        // Set up focus management
        this.focusableElements = this.modal.querySelectorAll(
            'button, input, textarea, select, a[href], [tabindex]:not([tabindex="-1"])'
        );
        
        // Ensure proper tab order
        this.modal.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                this.handleTabKey(e);
            }
        });
    }

    handleTabKey(e) {
        const firstElement = this.focusableElements[0];
        const lastElement = this.focusableElements[this.focusableElements.length - 1];

        if (e.shiftKey) {
            if (document.activeElement === firstElement) {
                e.preventDefault();
                lastElement.focus();
            }
        } else {
            if (document.activeElement === lastElement) {
                e.preventDefault();
                firstElement.focus();
            }
        }
    }

    openModal() {
        this.modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        // Focus first element
        setTimeout(() => {
            this.focusableElements[0]?.focus();
        }, 300);

        // Track analytics
        this.trackEvent('feedback_widget_opened');
    }

    closeModal() {
        this.modal.classList.remove('active');
        document.body.style.overflow = '';
        this.triggerBtn.focus();
        
        // Reset form if not submitted
        if (!this.isSubmitting) {
            this.resetForm();
        }
    }

    setRating(rating) {
        this.rating = rating;
        
        // Update UI
        this.modal.querySelectorAll('.rating-star').forEach((star, index) => {
            star.classList.toggle('active', index < rating);
            star.setAttribute('aria-checked', index < rating ? 'true' : 'false');
        });

        // Update validation
        this.validateForm();
        this.trackEvent('feedback_rating_set', { rating });
    }

    setCategory(category) {
        this.category = category;
        
        // Update UI
        this.modal.querySelectorAll('.category-btn').forEach(btn => {
            const isActive = btn.dataset.category === category;
            btn.classList.toggle('active', isActive);
            btn.setAttribute('aria-checked', isActive ? 'true' : 'false');
        });

        // Update validation
        this.validateForm();
        this.trackEvent('feedback_category_set', { category });
    }

    validateForm() {
        const isValid = this.rating > 0 && this.category;
        const submitBtn = this.modal.querySelector('.feedback-submit');
        submitBtn.disabled = !isValid;
    }

    async submitFeedback() {
        if (this.isSubmitting) return;

        this.isSubmitting = true;
        const submitBtn = this.modal.querySelector('.feedback-submit');
        const submitText = submitBtn.querySelector('.submit-text');
        const submitSpinner = submitBtn.querySelector('.submit-spinner');

        // Update UI
        submitBtn.disabled = true;
        submitText.style.display = 'none';
        submitSpinner.style.display = 'inline-block';

        try {
            // Update hidden form fields
            document.getElementById('page-url').value = window.location.href;
            document.getElementById('page-title').value = document.title;
            document.getElementById('selected-rating').value = this.rating;
            document.getElementById('selected-category').value = this.category;

            // Create FormData from the form
            const formData = new FormData(this.form);

            const response = await fetch(this.options.submitEndpoint, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            });

            const result = await response.json();

            if (response.ok && result.success) {
                this.showSuccessMessage();
                this.trackEvent('feedback_submitted_success', { 
                    rating: this.rating, 
                    category: this.category 
                });
            } else {
                throw new Error(result.error || `HTTP ${response.status}: ${response.statusText}`);
            }

        } catch (error) {
            console.error('Feedback submission error:', error);
            this.showErrorMessage();
            this.trackEvent('feedback_submitted_error', { error: error.message });
        } finally {
            this.isSubmitting = false;
        }
    }

    showSuccessMessage() {
        this.form.style.display = 'none';
        this.modal.querySelector('.feedback-success').style.display = 'block';
        
        // Auto-close after 3 seconds
        setTimeout(() => {
            this.closeModal();
        }, 3000);
    }

    showErrorMessage() {
        // Reset submit button
        const submitBtn = this.modal.querySelector('.feedback-submit');
        const submitText = submitBtn.querySelector('.submit-text');
        const submitSpinner = submitBtn.querySelector('.submit-spinner');
        
        submitBtn.disabled = false;
        submitText.style.display = 'inline';
        submitSpinner.style.display = 'none';
        submitText.textContent = 'حاول مرة أخرى';
        
        // Show error message
        alert('عذراً، حدث خطأ في إرسال الملاحظة. يرجى المحاولة مرة أخرى.');
    }

    resetForm() {
        this.rating = 0;
        this.category = '';
        
        // Reset UI
        this.modal.querySelectorAll('.rating-star').forEach(star => {
            star.classList.remove('active');
            star.setAttribute('aria-checked', 'false');
        });
        
        this.modal.querySelectorAll('.category-btn').forEach(btn => {
            btn.classList.remove('active');
            btn.setAttribute('aria-checked', 'false');
        });
        
        this.modal.querySelector('.feedback-textarea').value = '';
        this.modal.querySelector('#char-count').textContent = '0/500 حرف';
        
        // Reset success message
        this.form.style.display = 'block';
        this.modal.querySelector('.feedback-success').style.display = 'none';
        
        // Reset submit button
        const submitBtn = this.modal.querySelector('.feedback-submit');
        submitBtn.disabled = true;
        submitBtn.querySelector('.submit-text').textContent = this.getLabel('submit');
    }

    getLabel(key) {
        return this.options.labels[this.currentLang][key] || this.options.labels['ar'][key];
    }

    trackEvent(eventName, data = {}) {
        // Integration with existing analytics
        if (typeof gtag !== 'undefined') {
            gtag('event', eventName, {
                event_category: 'feedback_widget',
                ...data
            });
        }
        
        // Console logging for development
        console.log(`Feedback Widget Event: ${eventName}`, data);
    }

    // Public methods
    destroy() {
        if (this.widget && this.widget.parentNode) {
            this.widget.parentNode.removeChild(this.widget);
        }
    }

    updateLanguage(lang) {
        this.currentLang = lang;
        // Recreate widget with new language
        this.destroy();
        this.init();
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if not already present
    if (!document.querySelector('.feedback-widget')) {
        window.feedbackWidget = new FeedbackWidget();
    }
});

// Export for manual initialization
window.FeedbackWidget = FeedbackWidget;