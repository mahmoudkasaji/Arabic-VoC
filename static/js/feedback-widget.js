/**
 * Persistent Feedback Widget for Voice of Customer Platform
 * Lightweight, accessible, and culturally appropriate for Arabic users
 */

// Prevent redefinition if already loaded
if (typeof window.FeedbackWidget === 'undefined') {

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
                    whyLabel: 'لماذا؟ أخبرنا المزيد',
                    comment: 'شاركنا تفاصيل تجربتك...',
                    characters: 'حرف',
                    selectCategory: 'اختر نوع الملاحظة...',
                    submit: 'إرسال الملاحظة',
                    submitting: 'جاري الإرسال...',
                    success: '✓ تم الإرسال بنجاح!',
                    successMessage: 'شكراً لك على مشاركة رأيك. سنعمل على تحسين تجربتك بناءً على ملاحظاتك.'
                },
                en: {
                    trigger: 'Feedback',
                    title: 'Share Your Feedback',
                    rating: 'How would you rate your experience?',
                    category: 'What type of feedback?',
                    whyLabel: 'Why? Tell us more',
                    comment: 'Share details about your experience...',
                    characters: 'chars',
                    selectCategory: 'Select feedback type...',
                    submit: 'Submit Feedback',
                    submitting: 'Submitting...',
                    success: '✓ Successfully Submitted!',
                    successMessage: 'Thank you for sharing your feedback. We\'ll use your input to improve your experience.'
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

        // Create backdrop for slide mode
        this.backdrop = document.createElement('div');
        this.backdrop.className = 'feedback-modal-backdrop';
        document.body.appendChild(this.backdrop);

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
                            <label class="feedback-rating-label" for="category-select">${labels.category}</label>
                            <select class="category-dropdown" id="category-select" required>
                                <option value="">${labels.selectCategory || 'اختر نوع الملاحظة...'}</option>
                                ${categories.map(cat => `
                                    <option value="${cat}">${cat}</option>
                                `).join('')}
                            </select>
                        </div>

                        <!-- Comment Section -->
                        <div class="feedback-comment">
                            <label class="feedback-rating-label" for="feedback-text">${labels.whyLabel}</label>
                            <textarea class="feedback-textarea" 
                                      id="feedback-text"
                                      name="comment"
                                      placeholder="${labels.comment}"
                                      maxlength="500"
                                      required
                                      aria-describedby="char-count"></textarea>
                            <small id="char-count" class="text-muted">0/500 ${labels.characters}</small>
                        </div>

                        <!-- Submit Button -->
                        <button type="submit" class="feedback-submit incomplete" disabled>
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

        // Backdrop click to close
        this.backdrop.addEventListener('click', () => this.closeModal());

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

        // Category dropdown
        this.modal.querySelector('#category-select').addEventListener('change', (e) => {
            this.setCategory(e.target.value);
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
        if (this.backdrop) {
            this.backdrop.classList.add('active');
        }
        document.body.style.overflow = 'hidden';
        
        // Focus first element
        setTimeout(() => {
            this.focusableElements[0]?.focus();
        }, 300);

        // Track analytics
        this.trackEvent('feedback_widget_opened');
    }

    closeModal() {
        // Clear any active countdown interval immediately
        if (this.countdownInterval) {
            clearInterval(this.countdownInterval);
            this.countdownInterval = null;
        }
        
        this.modal.classList.remove('active');
        if (this.backdrop) {
            this.backdrop.classList.remove('active');
        }
        document.body.style.overflow = '';
        this.triggerBtn.focus();
        
        // Reset form if not submitted
        if (!this.isSubmitting) {
            this.resetForm();
        }
    }

    setRating(rating) {
        this.rating = rating;
        
        // Update UI with enhanced visual feedback
        this.modal.querySelectorAll('.rating-star').forEach((star, index) => {
            star.classList.toggle('active', index < rating);
            star.setAttribute('aria-checked', index < rating ? 'true' : 'false');
            
            // Add selection feedback animation
            if (index < rating) {
                star.style.animation = 'none';
                setTimeout(() => {
                    star.style.animation = `starSelection 0.3s ease-out ${index * 0.05}s both`;
                }, 10);
            } else {
                star.style.animation = '';
            }
        });

        // Show rating confirmation
        this.showRatingFeedback(rating);
        
        // Update validation
        this.validateForm();
        this.trackEvent('feedback_rating_set', { rating });
    }
    
    showRatingFeedback(rating) {
        const ratingLabels = {
            ar: ['', 'ضعيف جداً', 'ضعيف', 'متوسط', 'جيد', 'ممتاز'],
            en: ['', 'Very Poor', 'Poor', 'Average', 'Good', 'Excellent']
        };
        
        const ratingLabel = ratingLabels[this.currentLang][rating] || ratingLabels['ar'][rating];
        const ratingSection = this.modal.querySelector('.feedback-rating');
        
        // Remove existing feedback
        const existingFeedback = ratingSection.querySelector('.rating-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }
        
        // Add new feedback
        const feedbackDiv = document.createElement('div');
        feedbackDiv.className = 'rating-feedback';
        feedbackDiv.textContent = ratingLabel;
        feedbackDiv.style.cssText = `
            color: #ff8c00;
            font-size: 12px;
            font-weight: 600;
            margin-top: 4px;
            text-align: center;
            opacity: 0;
            transform: translateY(-10px);
            transition: all 0.3s ease;
        `;
        
        ratingSection.appendChild(feedbackDiv);
        
        // Animate in
        setTimeout(() => {
            feedbackDiv.style.opacity = '1';
            feedbackDiv.style.transform = 'translateY(0)';
        }, 50);
    }

    setCategory(category) {
        this.category = category;
        
        // Update dropdown value
        this.modal.querySelector('#category-select').value = category;

        // Update validation
        this.validateForm();
        this.trackEvent('feedback_category_set', { category });
    }

    validateForm() {
        const comment = this.modal.querySelector('.feedback-textarea').value.trim();
        const isValid = this.rating > 0 && this.category && comment.length > 0;
        const submitBtn = this.modal.querySelector('.feedback-submit');
        submitBtn.disabled = !isValid;
        
        // Update submit button text based on validation
        const submitText = submitBtn.querySelector('.submit-text');
        if (isValid) {
            submitText.textContent = this.getLabel('submit');
            submitBtn.classList.remove('incomplete');
        } else {
            submitBtn.classList.add('incomplete');
        }
    }

    async submitFeedback() {
        if (this.isSubmitting) return;

        // Validate all required fields
        const comment = this.modal.querySelector('.feedback-textarea').value.trim();
        if (!this.rating || !this.category || !comment) {
            return;
        }

        this.isSubmitting = true;
        const submitBtn = this.modal.querySelector('.feedback-submit');
        const submitText = submitBtn.querySelector('.submit-text');
        const submitSpinner = submitBtn.querySelector('.submit-spinner');

        // Show enhanced submitting state
        submitBtn.disabled = true;
        submitBtn.classList.add('submitting');
        submitBtn.classList.remove('incomplete');
        submitText.textContent = this.getLabel('submitting') || 'جاري الإرسال...';
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
                // Show success button state briefly
                submitBtn.classList.remove('submitting');
                submitBtn.classList.add('success');
                submitText.textContent = this.getLabel('success');
                submitSpinner.style.display = 'none';
                
                // Show success message and auto-close after brief delay
                setTimeout(() => {
                    this.showSuccessMessage();
                    this.trackEvent('feedback_submitted_success', { 
                        rating: this.rating, 
                        category: this.category 
                    });
                    
                    // Auto-close after success message
                    this.autoCloseWithCountdown();
                }, 500);
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
    }
    
    autoCloseWithCountdown() {
        // Auto-close with countdown visual feedback (UX best practice: 4 seconds)
        const countdown = 4;
        let timeLeft = countdown;
        let countdownInterval;
        let isPaused = false;
        
        // Get success message elements
        const successContainer = this.modal.querySelector('.feedback-success');
        const successMessage = this.modal.querySelector('.feedback-success-message');
        const originalMessage = successMessage.textContent;
        
        // Create countdown display
        const countdownDisplay = document.createElement('div');
        countdownDisplay.className = 'auto-close-countdown';
        countdownDisplay.style.cssText = `
            margin-top: 16px;
            text-align: center;
            font-size: 14px;
            color: #666;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        `;
        
        // Create manual close button
        const manualCloseBtn = document.createElement('button');
        manualCloseBtn.textContent = this.currentLang === 'ar' ? 'إغلاق الآن' : 'Close Now';
        manualCloseBtn.className = 'manual-close-btn';
        manualCloseBtn.style.cssText = `
            background: transparent;
            border: 1px solid #ddd;
            color: #666;
            padding: 4px 8px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            margin-left: 8px;
        `;
        manualCloseBtn.onclick = () => {
            clearInterval(countdownInterval);
            this.closeModal();
            setTimeout(() => this.resetForm(), 400);
        };
        
        // Create progress bar
        const progressBar = document.createElement('div');
        progressBar.style.cssText = `
            width: 100%;
            height: 3px;
            background: #f0f0f0;
            border-radius: 2px;
            margin-top: 12px;
            overflow: hidden;
        `;
        
        const progressFill = document.createElement('div');
        progressFill.style.cssText = `
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            width: 100%;
            transition: width 1s linear;
            border-radius: 2px;
        `;
        progressBar.appendChild(progressFill);
        
        // Add countdown elements to success container
        countdownDisplay.appendChild(manualCloseBtn);
        successContainer.appendChild(countdownDisplay);
        successContainer.appendChild(progressBar);
        
        // Pause/resume functions for accessibility
        const pauseCountdown = () => {
            isPaused = true;
            countdownDisplay.style.opacity = '0.7';
        };
        
        const resumeCountdown = () => {
            isPaused = false;
            countdownDisplay.style.opacity = '1';
        };
        
        // Add hover/focus listeners for accessibility
        successContainer.addEventListener('mouseenter', pauseCountdown);
        successContainer.addEventListener('mouseleave', resumeCountdown);
        successContainer.addEventListener('focusin', pauseCountdown);
        successContainer.addEventListener('focusout', resumeCountdown);
        
        // Update countdown display
        const updateCountdown = () => {
            const countdownText = this.currentLang === 'ar' 
                ? `إغلاق تلقائي خلال ${timeLeft} ثوان`
                : `Auto-closing in ${timeLeft} seconds`;
            countdownDisplay.querySelector('span').textContent = countdownText;
            
            // Update progress bar
            const progressPercent = ((countdown - timeLeft) / countdown) * 100;
            progressFill.style.width = `${100 - progressPercent}%`;
        };
        
        // Add countdown text element first
        const countdownText = document.createElement('span');
        countdownDisplay.insertBefore(countdownText, manualCloseBtn);
        
        // Initial countdown display
        updateCountdown();
        
        // Start countdown interval
        countdownInterval = setInterval(() => {
            if (!isPaused) {
                timeLeft--;
                updateCountdown();
                
                if (timeLeft <= 0) {
                    clearInterval(countdownInterval);
                    this.closeModal();
                    // Reset form after closing
                    setTimeout(() => {
                        this.resetForm();
                    }, 400);
                }
            }
        }, 1000);
        
        // Store interval reference for cleanup
        this.countdownInterval = countdownInterval;
    }

    showErrorMessage() {
        // Reset submit button with enhanced states
        const submitBtn = this.modal.querySelector('.feedback-submit');
        const submitText = submitBtn.querySelector('.submit-text');
        const submitSpinner = submitBtn.querySelector('.submit-spinner');
        
        submitBtn.disabled = false;
        submitBtn.classList.remove('submitting', 'success');
        submitBtn.classList.add('incomplete');
        submitText.textContent = this.getLabel('retry') || 'حاول مرة أخرى';
        submitSpinner.style.display = 'none';
        
        // Show user-friendly error message
        const errorMsg = this.getCurrentLanguage() === 'ar' 
            ? 'عذراً، حدث خطأ في إرسال الملاحظة. يرجى المحاولة مرة أخرى.' 
            : 'Sorry, there was an error submitting your feedback. Please try again.';
        alert(errorMsg);
    }

    resetForm() {
        this.rating = 0;
        this.category = '';
        
        // Clear any active countdown interval
        if (this.countdownInterval) {
            clearInterval(this.countdownInterval);
            this.countdownInterval = null;
        }
        
        // Reset UI
        this.modal.querySelectorAll('.rating-star').forEach(star => {
            star.classList.remove('active');
            star.setAttribute('aria-checked', 'false');
            star.style.animation = ''; // Clear animations
        });
        
        // Remove rating feedback
        const existingFeedback = this.modal.querySelector('.rating-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }
        
        // Clean up countdown elements
        const successContainer = this.modal.querySelector('.feedback-success');
        const countdownDisplay = successContainer.querySelector('.auto-close-countdown');
        const progressBar = successContainer.querySelector('div[style*="progress"]');
        if (countdownDisplay) countdownDisplay.remove();
        if (progressBar) progressBar.remove();
        
        this.modal.querySelector('#category-select').selectedIndex = 0;
        
        this.modal.querySelector('.feedback-textarea').value = '';
        this.modal.querySelector('#char-count').textContent = '0/500 حرف';
        
        // Reset success message
        this.form.style.display = 'block';
        successContainer.style.display = 'none';
        
        // Reset submit button
        const submitBtn = this.modal.querySelector('.feedback-submit');
        submitBtn.disabled = true;
        submitBtn.classList.remove('submitting', 'success');
        submitBtn.classList.add('incomplete');
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
        if (this.backdrop && this.backdrop.parentNode) {
            this.backdrop.parentNode.removeChild(this.backdrop);
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

} // End of conditional guard for FeedbackWidget definition