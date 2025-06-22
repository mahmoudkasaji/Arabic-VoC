/**
 * Advanced Drag-and-Drop Controller for Survey Builder
 * Enhanced UX with visual feedback, animations, and accessibility
 */

class AdvancedDragController {
    constructor(options = {}) {
        this.container = options.container;
        this.questionsArea = options.questionsArea;
        this.sidebar = options.sidebar;
        this.onQuestionAdd = options.onQuestionAdd;
        this.onQuestionReorder = options.onQuestionReorder;
        
        // Component managers
        this.visualFeedback = new DragVisualFeedback();
        this.animations = new DragAnimationController();
        this.touchHandler = new TouchDragHandler();
        this.accessibility = new DragAccessibilityManager();
        
        // State management
        this.dragState = {
            isDragging: false,
            draggedElement: null,
            draggedType: null,
            dropZones: [],
            currentDropZone: null
        };
        
        this.init();
    }
    
    init() {
        this.setupAdvancedSortable();
        this.setupVisualFeedback();
        this.setupTouchSupport();
        this.setupKeyboardNavigation();
        this.setupAccessibility();
    }
    
    setupAdvancedSortable() {
        // Enhanced sidebar sortable for question types
        this.sidebarSortable = Sortable.create(this.sidebar, {
            group: {
                name: 'questionTypes',
                pull: 'clone',
                put: false
            },
            sort: false,
            animation: 200,
            easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
            dragClass: 'drag-active',
            ghostClass: 'drag-ghost',
            chosenClass: 'drag-chosen',
            
            onStart: (evt) => this.handleDragStart(evt),
            onMove: (evt) => this.handleDragMove(evt),
            onEnd: (evt) => this.handleDragEnd(evt)
        });
        
        // Enhanced questions area sortable
        this.questionsSortable = Sortable.create(this.questionsArea, {
            group: {
                name: 'questions',
                pull: false,
                put: ['questionTypes', 'questions']
            },
            animation: 300,
            easing: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
            dragClass: 'question-dragging',
            ghostClass: 'question-ghost',
            chosenClass: 'question-chosen',
            
            onStart: (evt) => this.handleQuestionDragStart(evt),
            onAdd: (evt) => this.handleQuestionAdd(evt),
            onUpdate: (evt) => this.handleQuestionReorder(evt),
            onMove: (evt) => this.handleQuestionMove(evt),
            onEnd: (evt) => this.handleQuestionDragEnd(evt)
        });
    }
    
    setupVisualFeedback() {
        this.visualFeedback.init({
            container: this.container,
            questionsArea: this.questionsArea
        });
    }
    
    setupTouchSupport() {
        this.touchHandler.init({
            sidebar: this.sidebar,
            questionsArea: this.questionsArea,
            onDragStart: (evt) => this.handleDragStart(evt),
            onDragEnd: (evt) => this.handleDragEnd(evt)
        });
    }
    
    setupKeyboardNavigation() {
        this.accessibility.setupKeyboardNavigation({
            container: this.container,
            onQuestionAdd: this.onQuestionAdd,
            onQuestionReorder: this.onQuestionReorder
        });
    }
    
    setupAccessibility() {
        this.accessibility.setupAriaLabels({
            sidebar: this.sidebar,
            questionsArea: this.questionsArea
        });
    }
    
    handleDragStart(evt) {
        this.dragState.isDragging = true;
        this.dragState.draggedElement = evt.item;
        this.dragState.draggedType = evt.item.dataset.type;
        
        // Enhanced visual feedback
        this.visualFeedback.showDropZones();
        this.animations.startDragAnimation(evt.item);
        
        // Update accessibility
        this.accessibility.announceDragStart(this.dragState.draggedType);
        
        // Add global drag class for styling
        document.body.classList.add('dragging-active');
    }
    
    handleDragMove(evt) {
        const dropZone = this.visualFeedback.detectDropZone(evt.originalEvent);
        
        if (dropZone !== this.dragState.currentDropZone) {
            this.visualFeedback.highlightDropZone(dropZone);
            this.dragState.currentDropZone = dropZone;
        }
        
        return this.validateDrop(evt);
    }
    
    handleDragEnd(evt) {
        this.dragState.isDragging = false;
        
        // Clean up visual feedback
        this.visualFeedback.hideDropZones();
        this.animations.endDragAnimation();
        
        // Update accessibility
        this.accessibility.announceDragEnd();
        
        // Remove global drag class
        document.body.classList.remove('dragging-active');
        
        // Reset state
        this.resetDragState();
    }
    
    handleQuestionDragStart(evt) {
        evt.item.classList.add('question-dragging');
        this.visualFeedback.showQuestionDropZones();
        this.accessibility.announceQuestionDragStart(evt.item);
    }
    
    handleQuestionAdd(evt) {
        const questionType = evt.item.dataset.type;
        if (questionType && this.onQuestionAdd) {
            // Remove the cloned element
            evt.item.remove();
            
            // Add question with enhanced feedback
            this.onQuestionAdd(questionType);
            this.visualFeedback.showSuccessAnimation();
            this.accessibility.announceQuestionAdded(questionType);
        }
    }
    
    handleQuestionReorder(evt) {
        if (this.onQuestionReorder) {
            this.onQuestionReorder(evt);
            this.visualFeedback.showReorderAnimation(evt.item);
            this.accessibility.announceQuestionReordered();
        }
    }
    
    handleQuestionMove(evt) {
        return this.validateQuestionMove(evt);
    }
    
    handleQuestionDragEnd(evt) {
        evt.item.classList.remove('question-dragging');
        this.visualFeedback.hideQuestionDropZones();
    }
    
    validateDrop(evt) {
        const isValidDrop = evt.to.classList.contains('questions-container') ||
                           evt.to.id === 'questionsArea';
        
        if (!isValidDrop) {
            this.visualFeedback.showInvalidDropFeedback();
            return false;
        }
        
        return true;
    }
    
    validateQuestionMove(evt) {
        // Prevent dropping questions back into sidebar
        if (evt.to.classList.contains('question-types')) {
            return false;
        }
        
        return true;
    }
    
    resetDragState() {
        this.dragState = {
            isDragging: false,
            draggedElement: null,
            draggedType: null,
            dropZones: [],
            currentDropZone: null
        };
    }
    
    // Public methods for external control
    enableDrag() {
        this.sidebarSortable.option('disabled', false);
        this.questionsSortable.option('disabled', false);
    }
    
    disableDrag() {
        this.sidebarSortable.option('disabled', true);
        this.questionsSortable.option('disabled', true);
    }
    
    destroy() {
        this.sidebarSortable.destroy();
        this.questionsSortable.destroy();
        this.touchHandler.destroy();
        this.accessibility.destroy();
    }
}

class DragVisualFeedback {
    constructor() {
        this.dropZoneIndicators = new Map();
        this.animationQueue = [];
    }
    
    init(options) {
        this.container = options.container;
        this.questionsArea = options.questionsArea;
        this.createDropZoneIndicators();
    }
    
    createDropZoneIndicators() {
        // Create visual drop zone indicator
        this.dropIndicator = document.createElement('div');
        this.dropIndicator.className = 'drop-zone-indicator';
        this.dropIndicator.innerHTML = `
            <div class="drop-zone-content">
                <i class="fas fa-plus-circle"></i>
                <span>اسحب السؤال هنا</span>
            </div>
        `;
        
        // Create insertion line indicator
        this.insertionLine = document.createElement('div');
        this.insertionLine.className = 'insertion-line';
    }
    
    showDropZones() {
        this.questionsArea.classList.add('drop-zones-active');
        
        // Show drop indicator if questions area is empty
        if (!this.questionsArea.hasChildNodes() || 
            this.questionsArea.children.length === 0) {
            this.questionsArea.appendChild(this.dropIndicator);
        }
    }
    
    hideDropZones() {
        this.questionsArea.classList.remove('drop-zones-active');
        
        // Remove drop indicator
        if (this.dropIndicator.parentNode) {
            this.dropIndicator.remove();
        }
        
        // Remove insertion line
        if (this.insertionLine.parentNode) {
            this.insertionLine.remove();
        }
    }
    
    highlightDropZone(dropZone) {
        // Remove previous highlights
        document.querySelectorAll('.drop-zone-highlight').forEach(el => {
            el.classList.remove('drop-zone-highlight');
        });
        
        if (dropZone) {
            dropZone.classList.add('drop-zone-highlight');
        }
    }
    
    showInsertionLine(position) {
        if (position && position.element) {
            position.element.parentNode.insertBefore(this.insertionLine, 
                position.before ? position.element : position.element.nextSibling);
        }
    }
    
    showSuccessAnimation() {
        // Create success ripple effect
        const ripple = document.createElement('div');
        ripple.className = 'success-ripple';
        this.questionsArea.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 1000);
    }
    
    showReorderAnimation(element) {
        element.classList.add('reorder-animation');
        setTimeout(() => element.classList.remove('reorder-animation'), 300);
    }
    
    showInvalidDropFeedback() {
        this.questionsArea.classList.add('invalid-drop');
        setTimeout(() => this.questionsArea.classList.remove('invalid-drop'), 300);
    }
    
    detectDropZone(event) {
        const elements = document.elementsFromPoint(event.clientX, event.clientY);
        return elements.find(el => el.classList.contains('drop-zone') || 
                                  el.classList.contains('question-item'));
    }
    
    showQuestionDropZones() {
        document.querySelectorAll('.question-item').forEach(item => {
            item.classList.add('reorder-drop-zone');
        });
    }
    
    hideQuestionDropZones() {
        document.querySelectorAll('.question-item').forEach(item => {
            item.classList.remove('reorder-drop-zone');
        });
    }
}

class DragAnimationController {
    constructor() {
        this.animationConfig = {
            duration: 300,
            easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
            springConfig: { tension: 300, friction: 30 }
        };
    }
    
    startDragAnimation(element) {
        element.style.transform = 'scale(1.05) rotate(2deg)';
        element.style.transition = 'transform 150ms ease-out';
        element.style.zIndex = '1000';
        element.style.boxShadow = '0 8px 25px rgba(0,0,0,0.15)';
    }
    
    endDragAnimation() {
        // Reset all dragged elements
        document.querySelectorAll('[style*="transform"]').forEach(el => {
            if (el.style.transform.includes('scale') || el.style.transform.includes('rotate')) {
                el.style.transform = '';
                el.style.transition = '';
                el.style.zIndex = '';
                el.style.boxShadow = '';
            }
        });
    }
    
    animateQuestionAdd(element) {
        // Scale in animation for new questions
        element.style.transform = 'scale(0.8)';
        element.style.opacity = '0';
        
        requestAnimationFrame(() => {
            element.style.transition = 'all 300ms cubic-bezier(0.68, -0.55, 0.265, 1.55)';
            element.style.transform = 'scale(1)';
            element.style.opacity = '1';
        });
    }
    
    animateQuestionRemove(element) {
        element.style.transition = 'all 250ms ease-in';
        element.style.transform = 'scale(0.8)';
        element.style.opacity = '0';
        
        setTimeout(() => element.remove(), 250);
    }
}

class TouchDragHandler {
    constructor() {
        this.touchState = {
            startX: 0,
            startY: 0,
            currentX: 0,
            currentY: 0,
            isDragging: false,
            element: null
        };
    }
    
    init(options) {
        this.sidebar = options.sidebar;
        this.questionsArea = options.questionsArea;
        this.onDragStart = options.onDragStart;
        this.onDragEnd = options.onDragEnd;
        
        this.setupTouchEvents();
    }
    
    setupTouchEvents() {
        // Enhanced touch support for mobile devices
        this.sidebar.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: false });
        document.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: false });
        document.addEventListener('touchend', this.handleTouchEnd.bind(this), { passive: false });
    }
    
    handleTouchStart(event) {
        const touch = event.touches[0];
        const element = event.target.closest('.question-type');
        
        if (element) {
            this.touchState.startX = touch.clientX;
            this.touchState.startY = touch.clientY;
            this.touchState.element = element;
            
            // Start long press timer for drag activation
            this.longPressTimer = setTimeout(() => {
                this.startTouchDrag(element, touch);
            }, 500);
        }
    }
    
    handleTouchMove(event) {
        if (this.longPressTimer) {
            clearTimeout(this.longPressTimer);
            this.longPressTimer = null;
        }
        
        if (this.touchState.isDragging) {
            event.preventDefault();
            const touch = event.touches[0];
            this.touchState.currentX = touch.clientX;
            this.touchState.currentY = touch.clientY;
            
            this.updateDragPosition();
        }
    }
    
    handleTouchEnd(event) {
        if (this.longPressTimer) {
            clearTimeout(this.longPressTimer);
            this.longPressTimer = null;
        }
        
        if (this.touchState.isDragging) {
            this.endTouchDrag(event);
        }
        
        this.resetTouchState();
    }
    
    startTouchDrag(element, touch) {
        this.touchState.isDragging = true;
        
        // Haptic feedback if available
        if (navigator.vibrate) {
            navigator.vibrate(50);
        }
        
        // Create drag preview
        this.createTouchDragPreview(element, touch);
        
        if (this.onDragStart) {
            this.onDragStart({ item: element, type: 'touch' });
        }
    }
    
    createTouchDragPreview(element, touch) {
        this.dragPreview = element.cloneNode(true);
        this.dragPreview.className = 'touch-drag-preview';
        this.dragPreview.style.position = 'fixed';
        this.dragPreview.style.pointerEvents = 'none';
        this.dragPreview.style.zIndex = '9999';
        this.dragPreview.style.left = (touch.clientX - 50) + 'px';
        this.dragPreview.style.top = (touch.clientY - 25) + 'px';
        
        document.body.appendChild(this.dragPreview);
    }
    
    updateDragPosition() {
        if (this.dragPreview) {
            this.dragPreview.style.left = (this.touchState.currentX - 50) + 'px';
            this.dragPreview.style.top = (this.touchState.currentY - 25) + 'px';
        }
    }
    
    endTouchDrag(event) {
        // Check if dropped on valid target
        const dropTarget = document.elementFromPoint(
            this.touchState.currentX,
            this.touchState.currentY
        );
        
        if (dropTarget && this.isValidDropTarget(dropTarget)) {
            // Trigger question add
            if (this.onDragEnd) {
                this.onDragEnd({
                    item: this.touchState.element,
                    target: dropTarget,
                    type: 'touch'
                });
            }
        }
        
        // Clean up drag preview
        if (this.dragPreview) {
            this.dragPreview.remove();
            this.dragPreview = null;
        }
    }
    
    isValidDropTarget(element) {
        return element.closest('.questions-container') || 
               element.closest('#questionsArea');
    }
    
    resetTouchState() {
        this.touchState = {
            startX: 0,
            startY: 0,
            currentX: 0,
            currentY: 0,
            isDragging: false,
            element: null
        };
    }
    
    destroy() {
        if (this.longPressTimer) {
            clearTimeout(this.longPressTimer);
        }
        
        this.sidebar.removeEventListener('touchstart', this.handleTouchStart);
        document.removeEventListener('touchmove', this.handleTouchMove);
        document.removeEventListener('touchend', this.handleTouchEnd);
    }
}

class DragAccessibilityManager {
    constructor() {
        this.announcements = {
            ar: {
                dragStart: 'بدء سحب السؤال',
                dragEnd: 'انتهاء سحب السؤال',
                questionAdded: 'تم إضافة السؤال',
                questionReordered: 'تم إعادة ترتيب السؤال',
                invalidDrop: 'موقع إسقاط غير صالح'
            },
            en: {
                dragStart: 'Started dragging question',
                dragEnd: 'Finished dragging question',
                questionAdded: 'Question added',
                questionReordered: 'Question reordered',
                invalidDrop: 'Invalid drop location'
            }
        };
        
        this.currentLanguage = document.documentElement.lang || 'ar';
    }
    
    setupKeyboardNavigation(options) {
        this.container = options.container;
        this.onQuestionAdd = options.onQuestionAdd;
        this.onQuestionReorder = options.onQuestionReorder;
        
        this.container.addEventListener('keydown', this.handleKeyDown.bind(this));
    }
    
    setupAriaLabels(options) {
        this.sidebar = options.sidebar;
        this.questionsArea = options.questionsArea;
        
        // Add ARIA labels to sidebar elements
        const questionTypes = this.sidebar.querySelectorAll('.question-type');
        questionTypes.forEach((type, index) => {
            type.setAttribute('role', 'button');
            type.setAttribute('tabindex', '0');
            type.setAttribute('aria-label', 
                `${type.textContent} - اضغط Enter لإضافة السؤال`);
        });
        
        // Setup live region for announcements
        this.setupLiveRegion();
    }
    
    setupLiveRegion() {
        this.liveRegion = document.createElement('div');
        this.liveRegion.setAttribute('aria-live', 'polite');
        this.liveRegion.setAttribute('aria-atomic', 'true');
        this.liveRegion.className = 'sr-only';
        document.body.appendChild(this.liveRegion);
    }
    
    handleKeyDown(event) {
        const target = event.target;
        
        if (target.classList.contains('question-type')) {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                const questionType = target.dataset.type;
                if (this.onQuestionAdd) {
                    this.onQuestionAdd(questionType);
                    this.announceQuestionAdded(questionType);
                }
            }
        }
        
        // Arrow key navigation for questions
        if (target.classList.contains('question-item')) {
            this.handleQuestionNavigation(event, target);
        }
    }
    
    handleQuestionNavigation(event, questionElement) {
        const questions = Array.from(this.questionsArea.querySelectorAll('.question-item'));
        const currentIndex = questions.indexOf(questionElement);
        
        switch (event.key) {
            case 'ArrowUp':
                event.preventDefault();
                if (currentIndex > 0 && event.ctrlKey) {
                    this.moveQuestion(questionElement, currentIndex - 1);
                } else if (currentIndex > 0) {
                    questions[currentIndex - 1].focus();
                }
                break;
                
            case 'ArrowDown':
                event.preventDefault();
                if (currentIndex < questions.length - 1 && event.ctrlKey) {
                    this.moveQuestion(questionElement, currentIndex + 1);
                } else if (currentIndex < questions.length - 1) {
                    questions[currentIndex + 1].focus();
                }
                break;
        }
    }
    
    moveQuestion(questionElement, newIndex) {
        if (this.onQuestionReorder) {
            this.onQuestionReorder({
                element: questionElement,
                newIndex: newIndex
            });
            this.announceQuestionReordered();
        }
    }
    
    announce(messageKey, params = {}) {
        const messages = this.announcements[this.currentLanguage];
        let message = messages[messageKey] || messageKey;
        
        // Replace parameters in message
        Object.keys(params).forEach(key => {
            message = message.replace(`{${key}}`, params[key]);
        });
        
        this.liveRegion.textContent = message;
    }
    
    announceDragStart(questionType) {
        this.announce('dragStart', { questionType });
    }
    
    announceDragEnd() {
        this.announce('dragEnd');
    }
    
    announceQuestionAdded(questionType) {
        this.announce('questionAdded', { questionType });
    }
    
    announceQuestionReordered() {
        this.announce('questionReordered');
    }
    
    announceQuestionDragStart(element) {
        const questionText = element.querySelector('.question-text')?.textContent || 'سؤال';
        this.announce('dragStart', { questionType: questionText });
    }
    
    announceInvalidDrop() {
        this.announce('invalidDrop');
    }
    
    destroy() {
        if (this.liveRegion) {
            this.liveRegion.remove();
        }
        
        if (this.container) {
            this.container.removeEventListener('keydown', this.handleKeyDown);
        }
    }
}

// Export for use in survey builder
window.AdvancedDragController = AdvancedDragController;