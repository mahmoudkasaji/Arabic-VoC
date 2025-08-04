/**
 * Survey Builder JavaScript - Arabic VoC Platform
 * Interactive drag-and-drop survey builder with RTL support
 */

class SurveyBuilder {
    constructor() {
        this.questions = [];
        this.currentQuestionId = null;
        this.questionIdCounter = 1;
        this.sortable = null;
        this.sidebarSortable = null;
        
        this.init();
    }

    init() {
        console.log('Initializing SurveyBuilder...');
        this.setupDragAndDrop();
        this.setupEventListeners();
        this.loadSurveyData();
        this.setupExpandableQuestions();
        console.log('SurveyBuilder initialized');
    }

    setupExpandableQuestions() {
        const expandToggle = document.getElementById('expandAdvanced');
        const advancedQuestions = document.getElementById('advancedQuestionTypes');
        
        if (expandToggle && advancedQuestions) {
            expandToggle.addEventListener('click', () => {
                const isExpanded = !advancedQuestions.classList.contains('hide-advanced');
                
                if (isExpanded) {
                    advancedQuestions.classList.add('hide-advanced');
                    expandToggle.querySelector('span').textContent = 'عرض المزيد من أنواع الأسئلة';
                    expandToggle.classList.remove('expanded');
                } else {
                    advancedQuestions.classList.remove('hide-advanced');
                    expandToggle.querySelector('span').textContent = 'إخفاء الأسئلة المتقدمة';
                    expandToggle.classList.add('expanded');
                }
            });
        }
    }

    setupDragAndDrop() {
        // Support both original and progressive disclosure structures
        let questionTypes = document.getElementById('questionTypes');
        const questionsArea = document.getElementById('questionsArea');
        
        // Check for progressive disclosure structure
        if (!questionTypes) {
            const essentialTypes = document.getElementById('essentialQuestionTypes');
            const advancedTypes = document.getElementById('advancedQuestionTypes');
            
            if (essentialTypes) {
                questionTypes = essentialTypes.parentNode; // Use the sidebar container
                console.log('Using progressive disclosure structure');
            }
        }
        
        if (!questionTypes || !questionsArea) {
            console.error('Required elements not found for drag and drop', {
                questionTypes: !!questionTypes,
                questionsArea: !!questionsArea
            });
            return;
        }

        // Setup sortable for questions area with enhanced reordering
        this.sortable = Sortable.create(questionsArea, {
            group: {
                name: 'questions',
                pull: false,
                put: ['questionTypes']
            },
            animation: 250,
            easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
            ghostClass: 'sortable-ghost',
            chosenClass: 'sortable-chosen',
            dragClass: 'sortable-drag',
            handle: '.drag-handle, .question-item',
            scroll: true,
            scrollSensitivity: 100,
            scrollSpeed: 15,
            bubbleScroll: true,
            onAdd: (evt) => {
                const questionType = evt.item.dataset.type;
                console.log('Adding question type:', questionType);
                if (questionType) {
                    this.addQuestion(questionType);
                    evt.item.remove();
                }
            },
            onUpdate: (evt) => {
                console.log('Question reordered from', evt.oldIndex, 'to', evt.newIndex);
                this.handleQuestionReorder(evt);
            },
            onStart: (evt) => {
                console.log('Started reordering question');
                document.body.classList.add('question-reordering');
            },
            onEnd: (evt) => {
                console.log('Finished reordering question');
                document.body.classList.remove('question-reordering');
            }
        });

        // Setup drag and drop for both essential and advanced question types
        this.setupQuestionTypeDragging();

        console.log('Drag and drop initialized');
    }

    setupQuestionTypeDragging() {
        // Get all question type containers
        const containers = [
            'essentialQuestionTypes',
            'advancedQuestionTypes',
            'questionTypes' // fallback for old structure
        ];

        containers.forEach(containerId => {
            const container = document.getElementById(containerId);
            if (container) {
                console.log('Setting up drag for container:', containerId);
                Sortable.create(container, {
                    group: {
                        name: 'questionTypes',
                        pull: 'clone',
                        put: false
                    },
                    sort: false,
                    animation: 200,
                    onStart: (evt) => {
                        console.log('Started dragging question type:', evt.item.dataset.type);
                        evt.item.classList.add('dragging');
                        document.body.classList.add('drag-active');
                        
                        // Show drop zone hints
                        this.showDropZoneHints();
                    },
                    onEnd: (evt) => {
                        console.log('Ended dragging');
                        evt.item.classList.remove('dragging');
                        document.body.classList.remove('drag-active');
                        
                        // Hide drop zone hints
                        this.hideDropZoneHints();
                    }
                });
            }
        });
    }

    showDropZoneHints() {
        const questionsArea = document.getElementById('questionsArea');
        if (questionsArea) {
            questionsArea.classList.add('drop-zone-active');
        }
    }

    hideDropZoneHints() {
        const questionsArea = document.getElementById('questionsArea');
        if (questionsArea) {
            questionsArea.classList.remove('drop-zone-active');
        }
    }

    addNextStepButton() {
        // Add a "Next Step" button to proceed to delivery configuration
        const questionsArea = document.getElementById('questionsArea');
        let nextStepBtn = document.getElementById('nextStepButton');
        
        if (!nextStepBtn && questionsArea && this.questions.length > 0) {
            nextStepBtn = document.createElement('div');
            nextStepBtn.id = 'nextStepButton';
            nextStepBtn.className = 'text-center mt-4';
            nextStepBtn.innerHTML = `
                <button class="btn btn-primary btn-lg" onclick="transitionToStep(4)" style="margin: 2rem auto;">
                    <i class="fas fa-arrow-left me-2"></i>
                    التالي: إعداد التوزيع
                </button>
            `;
            questionsArea.appendChild(nextStepBtn);
        }
    }

    setupEventListeners() {
        // Survey header fields
        const titleField = document.getElementById('surveyTitle');
        const titleArField = document.getElementById('surveyTitleAr');
        const descField = document.getElementById('surveyDescription');
        const descArField = document.getElementById('surveyDescriptionAr');

        if (titleField) titleField.addEventListener('input', () => this.updateSurveyHeader());
        if (titleArField) titleArField.addEventListener('input', () => this.updateSurveyHeader());
        if (descField) descField.addEventListener('input', () => this.updateSurveyHeader());
        if (descArField) descArField.addEventListener('input', () => this.updateSurveyHeader());

        // Mobile question type selector
        this.setupMobileQuestionSelector();
        
        // Click-to-add functionality for question types
        this.setupClickToAdd();
    }

    setupMobileQuestionSelector() {
        const mobileSelect = document.getElementById('mobileQuestionTypeSelect');
        const mobileAddBtn = document.getElementById('mobileAddQuestionBtn');

        if (mobileSelect && mobileAddBtn) {
            // Enable/disable add button based on selection
            mobileSelect.addEventListener('change', () => {
                const selectedType = mobileSelect.value;
                mobileAddBtn.disabled = !selectedType;
                
                if (selectedType) {
                    mobileAddBtn.textContent = `إضافة: ${this.getQuestionTypeLabel(selectedType)}`;
                } else {
                    mobileAddBtn.textContent = 'إضافة السؤال';
                }
            });

            // Mobile add button click handler
            mobileAddBtn.addEventListener('click', () => {
                const selectedType = mobileSelect.value;
                if (selectedType) {
                    this.addQuestion(selectedType);
                    mobileSelect.value = '';
                    mobileAddBtn.disabled = true;
                    mobileAddBtn.textContent = 'إضافة السؤال';
                    
                    // Transition to step 3 (editing mode)
                    if (typeof transitionToStep === 'function') {
                        transitionToStep(3);
                    }
                }
            });
        }
    }

    setupClickToAdd() {
        // Add click functionality to all question type elements
        document.addEventListener('click', (e) => {
            const questionTypeElement = e.target.closest('.question-type');
            if (questionTypeElement && questionTypeElement.dataset.type) {
                const questionType = questionTypeElement.dataset.type;
                console.log('Click to add question type:', questionType);
                
                // Add question
                this.addQuestion(questionType);
                
                // Transition to step 3 (editing mode) if we have questions
                if (this.questions.length >= 1 && typeof transitionToStep === 'function') {
                    transitionToStep(3);
                }
                
                // Visual feedback
                questionTypeElement.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    questionTypeElement.style.transform = '';
                }, 150);
            }
        });
    }

    setupMobileQuestionSelector() {
        const mobileSelect = document.getElementById('mobileQuestionTypeSelect');
        const mobileAddBtn = document.getElementById('mobileAddQuestionBtn');

        if (mobileSelect && mobileAddBtn) {
            // Enable/disable add button based on selection
            mobileSelect.addEventListener('change', () => {
                const selectedType = mobileSelect.value;
                mobileAddBtn.disabled = !selectedType;
                
                if (selectedType) {
                    mobileAddBtn.innerHTML = `<i class="fas fa-plus"></i> إضافة: `;
                    const textNode = document.createTextNode(this.getQuestionTypeLabel(selectedType));
                    mobileAddBtn.appendChild(textNode);
                } else {
                    mobileAddBtn.innerHTML = '<i class="fas fa-plus"></i> إضافة السؤال';
                }
            });

            // Add question when button is clicked
            mobileAddBtn.addEventListener('click', () => {
                const selectedType = mobileSelect.value;
                if (selectedType) {
                    this.addQuestion(selectedType);
                    // Reset selection
                    mobileSelect.value = '';
                    mobileAddBtn.disabled = true;
                    
                    // Show success feedback
                    mobileAddBtn.innerHTML = '<i class="fas fa-check"></i> تم الإضافة!';
                    mobileAddBtn.style.background = '#28a745';
                    
                    setTimeout(() => {
                        mobileAddBtn.innerHTML = '<i class="fas fa-plus"></i> إضافة السؤال';
                        mobileAddBtn.style.background = '';
                    }, 1500);
                }
            });
        }
    }

    addQuestion(type) {
        const question = {
            id: this.questionIdCounter++,
            type: type,
            text: this.getDefaultQuestionText(type),
            text_ar: this.getDefaultQuestionTextAr(type),
            description: '',
            description_ar: '',
            is_required: false,
            order_index: this.questions.length,
            options: this.getDefaultOptions(type),
            validation_rules: {}
        };

        this.questions.push(question);
        this.renderQuestion(question);
        this.updateQuestionsArea();
        
        // Update question counter
        const questionCountElement = document.getElementById('questionCount');
        if (questionCountElement) {
            questionCountElement.textContent = this.questions.length;
        }
        
        // Auto-transition to step 3 if we have questions and transition function exists
        if (this.questions.length >= 1 && typeof transitionToStep === 'function') {
            transitionToStep(3);
            this.addNextStepButton();
        }
    }

    getDefaultQuestionText(type) {
        const defaults = {
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
        };
        return defaults[type] || 'New question';
    }

    getDefaultQuestionTextAr(type) {
        const defaults = {
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
        };
        return defaults[type] || 'سؤال جديد';
    }

    getDefaultOptions(type) {
        if (['multiple_choice', 'checkbox', 'dropdown'].includes(type)) {
            return {
                choices: [
                    { text: 'الخيار الأول', text_en: 'Option 1', value: 'option1' },
                    { text: 'الخيار الثاني', text_en: 'Option 2', value: 'option2' }
                ]
            };
        } else if (type === 'rating') {
            return {
                max_rating: 5,
                rating_labels: {
                    ar: ['ضعيف جداً', 'ضعيف', 'متوسط', 'جيد', 'ممتاز'],
                    en: ['Very Poor', 'Poor', 'Average', 'Good', 'Excellent']
                }
            };
        } else if (type === 'slider') {
            return {
                min_value: 0,
                max_value: 10,
                step: 1,
                labels: {
                    ar: { min: 'الأدنى', max: 'الأعلى' },
                    en: { min: 'Minimum', max: 'Maximum' }
                }
            };
        } else if (type === 'nps') {
            return {
                min_value: 0,
                max_value: 10,
                labels: {
                    ar: { min: 'لن أوصي أبداً', max: 'سأوصي بقوة' },
                    en: { min: 'Not at all likely', max: 'Extremely likely' }
                }
            };
        }
        return {};
    }

    renderQuestion(question) {
        const questionsArea = document.getElementById('questionsArea');
        
        if (this.questions.length === 1) {
            questionsArea.innerHTML = '<div class="questions-container"></div>';
            questionsArea.classList.add('has-questions');
        }
        
        const questionsContainer = questionsArea.querySelector('.questions-container');

        const questionElement = document.createElement('div');
        questionElement.className = 'question-item';
        questionElement.dataset.questionId = question.id;
        
        // Create header section safely
        const questionHeader = document.createElement('div');
        questionHeader.className = 'question-header';
        
        const headerAlign = document.createElement('div');
        headerAlign.className = 'd-flex align-items-center';
        
        const dragHandle = document.createElement('i');
        dragHandle.className = 'fas fa-grip-vertical drag-handle me-3';
        dragHandle.title = 'اسحب لإعادة الترتيب';
        headerAlign.appendChild(dragHandle);
        
        const typeBadge = document.createElement('span');
        typeBadge.className = 'badge bg-primary me-2';
        typeBadge.textContent = this.getQuestionTypeLabel(question.type);
        headerAlign.appendChild(typeBadge);
        
        const questionNumber = document.createElement('span');
        questionNumber.className = 'question-number';
        questionNumber.textContent = `السؤال ${question.order_index + 1}`;
        headerAlign.appendChild(questionNumber);
        
        questionHeader.appendChild(headerAlign);
        
        // Create action buttons safely
        const actionDiv = document.createElement('div');
        actionDiv.className = 'question-actions';
        
        const duplicateBtn = document.createElement('button');
        duplicateBtn.className = 'btn btn-sm btn-outline-primary';
        duplicateBtn.title = 'نسخ السؤال';
        duplicateBtn.onclick = () => this.duplicateQuestion(question.id);
        const duplicateIcon = document.createElement('i');
        duplicateIcon.className = 'fas fa-copy';
        duplicateBtn.appendChild(duplicateIcon);
        actionDiv.appendChild(duplicateBtn);
        
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'btn btn-sm btn-outline-danger';
        deleteBtn.title = 'حذف السؤال';
        deleteBtn.onclick = () => this.deleteQuestion(question.id);
        const deleteIcon = document.createElement('i');
        deleteIcon.className = 'fas fa-trash';
        deleteBtn.appendChild(deleteIcon);
        actionDiv.appendChild(deleteBtn);
        
        questionHeader.appendChild(actionDiv);
        questionElement.appendChild(questionHeader);
        
        // Create content section safely
        const questionContent = document.createElement('div');
        questionContent.className = 'question-content';
        
        const questionTextEl = document.createElement('h6');
        questionTextEl.className = 'question-text';
        questionTextEl.textContent = question.text_ar || question.text || '';
        questionContent.appendChild(questionTextEl);
        
        // Add description if present
        if (question.description_ar || question.description) {
            const descriptionEl = document.createElement('p');
            descriptionEl.className = 'text-muted';
            descriptionEl.textContent = question.description_ar || question.description;
            questionContent.appendChild(descriptionEl);
        }
        
        // Create preview container
        const previewDiv = document.createElement('div');
        previewDiv.className = 'question-preview';
        const previewContent = this.renderQuestionPreviewSafe(question);
        previewDiv.appendChild(previewContent);
        questionContent.appendChild(previewDiv);
        
        questionElement.appendChild(questionContent);

        questionElement.addEventListener('click', () => {
            this.selectQuestion(question.id);
        });

        questionElement.setAttribute('tabindex', '0');
        questionElement.setAttribute('role', 'button');
        questionElement.setAttribute('aria-label', `تحرير السؤال: ${question.text_ar || question.text}`);
        
        questionElement.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.selectQuestion(question.id);
            }
        });

        questionsContainer.appendChild(questionElement);
    }

    renderQuestionPreviewSafe(question) {
        const container = document.createElement('div');
        
        switch (question.type) {
            case 'text':
                const textInput = document.createElement('input');
                textInput.type = 'text';
                textInput.className = 'form-control';
                textInput.placeholder = 'إجابة نصية قصيرة';
                textInput.disabled = true;
                container.appendChild(textInput);
                break;
            
            case 'textarea':
                const textarea = document.createElement('textarea');
                textarea.className = 'form-control';
                textarea.rows = 3;
                textarea.placeholder = 'إجابة نصية طويلة';
                textarea.disabled = true;
                container.appendChild(textarea);
                break;
            
            case 'multiple_choice':
                question.options.choices.forEach(choice => {
                    const checkDiv = document.createElement('div');
                    checkDiv.className = 'form-check';
                    
                    const radio = document.createElement('input');
                    radio.className = 'form-check-input';
                    radio.type = 'radio';
                    radio.disabled = true;
                    checkDiv.appendChild(radio);
                    
                    const label = document.createElement('label');
                    label.className = 'form-check-label';
                    label.textContent = choice.text || '';
                    checkDiv.appendChild(label);
                    
                    container.appendChild(checkDiv);
                });
                break;
            
            case 'checkbox':
                question.options.choices.forEach(choice => {
                    const checkDiv = document.createElement('div');
                    checkDiv.className = 'form-check';
                    
                    const checkbox = document.createElement('input');
                    checkbox.className = 'form-check-input';
                    checkbox.type = 'checkbox';
                    checkbox.disabled = true;
                    checkDiv.appendChild(checkbox);
                    
                    const label = document.createElement('label');
                    label.className = 'form-check-label';
                    label.textContent = choice.text || '';
                    checkDiv.appendChild(label);
                    
                    container.appendChild(checkDiv);
                });
                break;
            
            case 'dropdown':
                const select = document.createElement('select');
                select.className = 'form-select';
                select.disabled = true;
                
                const defaultOption = document.createElement('option');
                defaultOption.textContent = 'اختر إجابة...';
                select.appendChild(defaultOption);
                
                question.options.choices.forEach(choice => {
                    const option = document.createElement('option');
                    option.textContent = choice.text || '';
                    select.appendChild(option);
                });
                
                container.appendChild(select);
                break;
            
            case 'rating':
                const ratingDiv = document.createElement('div');
                ratingDiv.className = 'rating-preview';
                
                const maxRating = question.options.max_rating || 5;
                for (let i = 0; i < maxRating; i++) {
                    const star = document.createElement('i');
                    star.className = 'fas fa-star text-warning me-1';
                    star.style.fontSize = '1.5rem';
                    ratingDiv.appendChild(star);
                }
                
                container.appendChild(ratingDiv);
                break;
            
            case 'slider':
                const sliderDiv = document.createElement('div');
                sliderDiv.className = 'slider-preview';
                
                const slider = document.createElement('input');
                slider.type = 'range';
                slider.className = 'form-range';
                slider.min = question.options.min_value || 0;
                slider.max = question.options.max_value || 10;
                slider.disabled = true;
                sliderDiv.appendChild(slider);
                
                const labelDiv = document.createElement('div');
                labelDiv.className = 'd-flex justify-content-between';
                
                const minLabel = document.createElement('small');
                minLabel.textContent = question.options.labels?.ar?.min || 'الأدنى';
                labelDiv.appendChild(minLabel);
                
                const maxLabel = document.createElement('small');
                maxLabel.textContent = question.options.labels?.ar?.max || 'الأعلى';
                labelDiv.appendChild(maxLabel);
                
                sliderDiv.appendChild(labelDiv);
                container.appendChild(sliderDiv);
                break;
            
            case 'nps':
                const npsDiv = document.createElement('div');
                npsDiv.className = 'nps-preview';
                
                const buttonDiv = document.createElement('div');
                buttonDiv.className = 'mb-2';
                
                for (let i = 0; i <= 10; i++) {
                    const btn = document.createElement('button');
                    btn.className = 'btn btn-outline-primary btn-sm me-1';
                    btn.textContent = i.toString();
                    btn.disabled = true;
                    buttonDiv.appendChild(btn);
                }
                
                npsDiv.appendChild(buttonDiv);
                
                const npsLabelDiv = document.createElement('div');
                npsLabelDiv.className = 'd-flex justify-content-between';
                
                const npsMinLabel = document.createElement('small');
                npsMinLabel.textContent = question.options.labels?.ar?.min || 'لن أوصي أبداً';
                npsLabelDiv.appendChild(npsMinLabel);
                
                const npsMaxLabel = document.createElement('small');
                npsMaxLabel.textContent = question.options.labels?.ar?.max || 'سأوصي بقوة';
                npsLabelDiv.appendChild(npsMaxLabel);
                
                npsDiv.appendChild(npsLabelDiv);
                container.appendChild(npsDiv);
                break;
            
            case 'date':
                const dateInput = document.createElement('input');
                dateInput.type = 'date';
                dateInput.className = 'form-control';
                dateInput.disabled = true;
                container.appendChild(dateInput);
                break;
            
            case 'email':
                const emailInput = document.createElement('input');
                emailInput.type = 'email';
                emailInput.className = 'form-control';
                emailInput.placeholder = 'example@domain.com';
                emailInput.disabled = true;
                container.appendChild(emailInput);
                break;
            
            case 'phone':
                const phoneInput = document.createElement('input');
                phoneInput.type = 'tel';
                phoneInput.className = 'form-control';
                phoneInput.placeholder = '+966501234567';
                phoneInput.disabled = true;
                container.appendChild(phoneInput);
                break;
            
            default:
                const defaultText = document.createElement('div');
                defaultText.className = 'text-muted';
                defaultText.textContent = 'معاينة السؤال';
                container.appendChild(defaultText);
                break;
        }
        
        return container;
    }

    renderQuestionPreview(question) {
        switch (question.type) {
            case 'text':
                return '<input type="text" class="form-control" placeholder="إجابة نصية قصيرة" disabled>';
            
            case 'textarea':
                return '<textarea class="form-control" rows="3" placeholder="إجابة نصية طويلة" disabled></textarea>';
            
            case 'multiple_choice':
                return question.options.choices.map(choice => `
                    <div class="form-check">
                        <input class="form-check-input" type="radio" disabled>
                        <label class="form-check-label">${choice.text}</label>
                    </div>
                `).join('');
            
            case 'checkbox':
                return question.options.choices.map(choice => `
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" disabled>
                        <label class="form-check-label">${choice.text}</label>
                    </div>
                `).join('');
            
            case 'dropdown':
                return `
                    <select class="form-select" disabled>
                        <option>اختر إجابة...</option>
                        ${question.options.choices.map(choice => `<option>${choice.text}</option>`).join('')}
                    </select>
                `;
            
            case 'rating':
                const stars = Array.from({length: question.options.max_rating || 5}, (_, i) => 
                    `<i class="fas fa-star text-warning me-1" style="font-size: 1.5rem;"></i>`
                ).join('');
                return `<div class="rating-preview">${stars}</div>`;
            
            case 'slider':
                return `
                    <div class="slider-preview">
                        <input type="range" class="form-range" min="${question.options.min_value || 0}" 
                               max="${question.options.max_value || 10}" disabled>
                        <div class="d-flex justify-content-between">
                            <small>${question.options.labels?.ar?.min || 'الأدنى'}</small>
                            <small>${question.options.labels?.ar?.max || 'الأعلى'}</small>
                        </div>
                    </div>
                `;
            
            case 'nps':
                const npsButtons = Array.from({length: 11}, (_, i) => 
                    `<button class="btn btn-outline-primary btn-sm me-1" disabled>${i}</button>`
                ).join('');
                return `
                    <div class="nps-preview">
                        <div class="mb-2">${npsButtons}</div>
                        <div class="d-flex justify-content-between">
                            <small>${question.options.labels?.ar?.min || 'لن أوصي أبداً'}</small>
                            <small>${question.options.labels?.ar?.max || 'سأوصي بقوة'}</small>
                        </div>
                    </div>
                `;
            
            case 'date':
                return '<input type="date" class="form-control" disabled>';
            
            case 'email':
                return '<input type="email" class="form-control" placeholder="example@domain.com" disabled>';
            
            case 'phone':
                return '<input type="tel" class="form-control" placeholder="+966501234567" disabled>';
            
            default:
                return '<div class="text-muted">معاينة السؤال</div>';
        }
    }

    renderQuestionPreviewSafe(question) {
        const container = document.createElement('div');
        
        switch (question.type) {
            case 'text':
                const textInput = document.createElement('input');
                textInput.type = 'text';
                textInput.className = 'form-control';
                textInput.placeholder = 'إجابة نصية قصيرة';
                textInput.disabled = true;
                return textInput;
            
            case 'textarea':
                const textarea = document.createElement('textarea');
                textarea.className = 'form-control';
                textarea.rows = 3;
                textarea.placeholder = 'إجابة نصية طويلة';
                textarea.disabled = true;
                return textarea;
            
            case 'multiple_choice':
                question.options.choices.forEach(choice => {
                    const checkDiv = document.createElement('div');
                    checkDiv.className = 'form-check';
                    
                    const input = document.createElement('input');
                    input.className = 'form-check-input';
                    input.type = 'radio';
                    input.disabled = true;
                    
                    const label = document.createElement('label');
                    label.className = 'form-check-label';
                    label.textContent = choice.text;
                    
                    checkDiv.appendChild(input);
                    checkDiv.appendChild(label);
                    container.appendChild(checkDiv);
                });
                return container;
            
            case 'checkbox':
                question.options.choices.forEach(choice => {
                    const checkDiv = document.createElement('div');
                    checkDiv.className = 'form-check';
                    
                    const input = document.createElement('input');
                    input.className = 'form-check-input';
                    input.type = 'checkbox';
                    input.disabled = true;
                    
                    const label = document.createElement('label');
                    label.className = 'form-check-label';
                    label.textContent = choice.text;
                    
                    checkDiv.appendChild(input);
                    checkDiv.appendChild(label);
                    container.appendChild(checkDiv);
                });
                return container;
            
            case 'dropdown':
                const select = document.createElement('select');
                select.className = 'form-select';
                select.disabled = true;
                
                const defaultOption = document.createElement('option');
                defaultOption.textContent = 'اختر إجابة...';
                select.appendChild(defaultOption);
                
                question.options.choices.forEach(choice => {
                    const option = document.createElement('option');
                    option.textContent = choice.text;
                    select.appendChild(option);
                });
                return select;
            
            case 'rating':
                const ratingDiv = document.createElement('div');
                ratingDiv.className = 'rating-preview';
                
                const numStars = question.options.max_rating || 5;
                for (let i = 0; i < numStars; i++) {
                    const star = document.createElement('i');
                    star.className = 'fas fa-star text-warning me-1';
                    star.style.fontSize = '1.5rem';
                    ratingDiv.appendChild(star);
                }
                return ratingDiv;
            
            case 'slider':
                const sliderDiv = document.createElement('div');
                sliderDiv.className = 'slider-preview';
                
                const range = document.createElement('input');
                range.type = 'range';
                range.className = 'form-range';
                range.min = question.options.min_value || 0;
                range.max = question.options.max_value || 10;
                range.disabled = true;
                
                const labelsDiv = document.createElement('div');
                labelsDiv.className = 'd-flex justify-content-between';
                
                const minLabel = document.createElement('small');
                minLabel.textContent = question.options.labels?.ar?.min || 'الأدنى';
                
                const maxLabel = document.createElement('small');
                maxLabel.textContent = question.options.labels?.ar?.max || 'الأعلى';
                
                labelsDiv.appendChild(minLabel);
                labelsDiv.appendChild(maxLabel);
                
                sliderDiv.appendChild(range);
                sliderDiv.appendChild(labelsDiv);
                return sliderDiv;
            
            case 'nps':
                const npsDiv = document.createElement('div');
                npsDiv.className = 'nps-preview';
                
                const buttonsDiv = document.createElement('div');
                buttonsDiv.className = 'mb-2';
                
                for (let i = 0; i <= 10; i++) {
                    const button = document.createElement('button');
                    button.className = 'btn btn-outline-primary btn-sm me-1';
                    button.textContent = i.toString();
                    button.disabled = true;
                    buttonsDiv.appendChild(button);
                }
                
                const npsLabelsDiv = document.createElement('div');
                npsLabelsDiv.className = 'd-flex justify-content-between';
                
                const npsMinLabel = document.createElement('small');
                npsMinLabel.textContent = question.options.labels?.ar?.min || 'لن أوصي أبداً';
                
                const npsMaxLabel = document.createElement('small');
                npsMaxLabel.textContent = question.options.labels?.ar?.max || 'سأوصي بقوة';
                
                npsLabelsDiv.appendChild(npsMinLabel);
                npsLabelsDiv.appendChild(npsMaxLabel);
                
                npsDiv.appendChild(buttonsDiv);
                npsDiv.appendChild(npsLabelsDiv);
                return npsDiv;
            
            case 'date':
                const dateInput = document.createElement('input');
                dateInput.type = 'date';
                dateInput.className = 'form-control';
                dateInput.disabled = true;
                return dateInput;
            
            case 'email':
                const emailInput = document.createElement('input');
                emailInput.type = 'email';
                emailInput.className = 'form-control';
                emailInput.placeholder = 'example@domain.com';
                emailInput.disabled = true;
                return emailInput;
            
            case 'phone':
                const phoneInput = document.createElement('input');
                phoneInput.type = 'tel';
                phoneInput.className = 'form-control';
                phoneInput.placeholder = '+966501234567';
                phoneInput.disabled = true;
                return phoneInput;
            
            default:
                const defaultDiv = document.createElement('div');
                defaultDiv.className = 'text-muted';
                defaultDiv.textContent = 'معاينة السؤال';
                return defaultDiv;
        }
    }

    getQuestionTypeLabel(type) {
        const labels = {
            text: 'نص قصير',
            textarea: 'نص طويل',
            multiple_choice: 'اختيار متعدد',
            checkbox: 'مربعات اختيار',
            dropdown: 'قائمة منسدلة',
            rating: 'تقييم',
            slider: 'مؤشر تمرير',
            nps: 'مؤشر الترشيح',
            date: 'تاريخ',
            email: 'بريد إلكتروني',
            phone: 'هاتف'
        };
        return labels[type] || type;
    }

    selectQuestion(questionId) {
        document.querySelectorAll('.question-item').forEach(item => {
            item.classList.remove('active');
        });

        const questionElement = document.querySelector(`[data-question-id="${questionId}"]`);
        if (questionElement) {
            questionElement.classList.add('active');
        }

        this.currentQuestionId = questionId;
        this.renderQuestionProperties(questionId);
    }

    renderQuestionProperties(questionId) {
        const question = this.questions.find(q => q.id === questionId);
        if (!question) return;

        const propertiesContainer = document.getElementById('questionProperties');
        
        // Clear container first
        propertiesContainer.innerHTML = '';
        
        // Create safe DOM structure
        const propertyGroup = document.createElement('div');
        propertyGroup.className = 'property-group';
        
        const title = document.createElement('h6');
        title.textContent = 'النص والمحتوى';
        propertyGroup.appendChild(title);
        
        // Arabic question text
        const arDiv = document.createElement('div');
        arDiv.className = 'mb-3';
        
        const arLabel = document.createElement('label');
        arLabel.className = 'form-label';
        arLabel.textContent = 'نص السؤال (عربي)';
        arDiv.appendChild(arLabel);
        
        const arTextarea = document.createElement('textarea');
        arTextarea.className = 'form-control form-control-modern';
        arTextarea.rows = 2;
        arTextarea.id = 'questionTextAr';
        arTextarea.placeholder = 'أدخل نص السؤال بالعربية';
        arTextarea.value = question.text_ar || '';
        arDiv.appendChild(arTextarea);
        
        propertyGroup.appendChild(arDiv);
        
        // English question text
        const enDiv = document.createElement('div');
        enDiv.className = 'mb-3';
        
        const enLabel = document.createElement('label');
        enLabel.className = 'form-label';
        enLabel.textContent = 'نص السؤال (إنجليزي)';
        enDiv.appendChild(enLabel);
        
        const enTextarea = document.createElement('textarea');
        enTextarea.className = 'form-control form-control-modern';
        enTextarea.rows = 2;
        enTextarea.id = 'questionText';
        enTextarea.placeholder = 'Enter question text in English';
        enTextarea.value = question.text || '';
        enDiv.appendChild(enTextarea);
        
        propertyGroup.appendChild(enDiv);
        
        // Required checkbox
        const checkDiv = document.createElement('div');
        checkDiv.className = 'form-check mb-3';
        
        const checkbox = document.createElement('input');
        checkbox.className = 'form-check-input';
        checkbox.type = 'checkbox';
        checkbox.id = 'isRequired';
        checkbox.checked = question.is_required || false;
        checkDiv.appendChild(checkbox);
        
        const checkLabel = document.createElement('label');
        checkLabel.className = 'form-check-label';
        checkLabel.setAttribute('for', 'isRequired');
        checkLabel.textContent = 'سؤال إجباري';
        checkDiv.appendChild(checkLabel);
        
        propertyGroup.appendChild(checkDiv);
        propertiesContainer.appendChild(propertyGroup);

        this.setupPropertyEventListeners(questionId);
    }

    setupPropertyEventListeners(questionId) {
        const question = this.questions.find(q => q.id === questionId);
        if (!question) return;

        const questionTextAr = document.getElementById('questionTextAr');
        const questionText = document.getElementById('questionText');
        const isRequired = document.getElementById('isRequired');

        if (questionTextAr) {
            questionTextAr.addEventListener('input', () => {
                question.text_ar = questionTextAr.value;
                this.updateQuestionDisplay(question.id);
            });
        }

        if (questionText) {
            questionText.addEventListener('input', () => {
                question.text = questionText.value;
                this.updateQuestionDisplay(question.id);
            });
        }

        if (isRequired) {
            isRequired.addEventListener('change', () => {
                question.is_required = isRequired.checked;
            });
        }
    }

    updateQuestionDisplay(questionId) {
        const question = this.questions.find(q => q.id === questionId);
        if (!question) return;

        const questionElement = document.querySelector(`[data-question-id="${questionId}"]`);
        if (questionElement) {
            const questionText = questionElement.querySelector('.question-text');
            if (questionText) {
                questionText.textContent = question.text_ar || question.text;
            }
        }
    }

    duplicateQuestion(questionId) {
        const question = this.questions.find(q => q.id === questionId);
        if (question) {
            const duplicatedQuestion = {
                ...question,
                id: this.questionIdCounter++,
                order_index: this.questions.length,
                text: question.text + ' (نسخة)',
                text_ar: question.text_ar + ' (نسخة)'
            };
            this.questions.push(duplicatedQuestion);
            this.renderQuestion(duplicatedQuestion);
            this.updateQuestionsArea();
        }
    }

    deleteQuestion(questionId) {
        const questionIndex = this.questions.findIndex(q => q.id === questionId);
        if (questionIndex !== -1) {
            this.questions.splice(questionIndex, 1);
            
            const questionElement = document.querySelector(`[data-question-id="${questionId}"]`);
            if (questionElement) {
                questionElement.remove();
            }
            
            if (this.currentQuestionId === questionId) {
                document.getElementById('questionProperties').innerHTML = 
                    '<p class="text-muted text-center">حدد سؤالاً لتحرير خصائصه</p>';
                this.currentQuestionId = null;
            }
            
            this.updateQuestionsArea();
            this.reorderQuestions();
        }
    }

    handleQuestionReorder(evt) {
        // Get the actual DOM order and update the questions array
        const questionsContainer = document.querySelector('.questions-container');
        const questionElements = Array.from(questionsContainer.querySelectorAll('.question-item'));
        
        // Create new ordered array based on DOM order
        const newQuestions = [];
        questionElements.forEach((element, index) => {
            const questionId = parseInt(element.dataset.questionId);
            const question = this.questions.find(q => q.id === questionId);
            if (question) {
                question.order_index = index;
                newQuestions.push(question);
            }
        });
        
        // Update the questions array
        this.questions = newQuestions;
        
        // Update question numbers in the display
        this.updateQuestionNumbers();
        
        console.log('Questions reordered:', this.questions.map(q => q.id));
    }

    updateQuestionNumbers() {
        const questionElements = document.querySelectorAll('.question-item');
        questionElements.forEach((element, index) => {
            const questionNumber = element.querySelector('.question-number');
            if (questionNumber) {
                questionNumber.textContent = `السؤال ${index + 1}`;
            }
        });
    }

    reorderQuestions() {
        this.questions.forEach((question, index) => {
            question.order_index = index;
        });
        this.updateQuestionNumbers();
    }

    updateQuestionsArea() {
        const questionsArea = document.getElementById('questionsArea');
        if (this.questions.length === 0) {
            questionsArea.innerHTML = `
                <div class="questions-container">
                    <div class="empty-state">
                        <i class="fas fa-plus-circle empty-state-icon"></i>
                        <h4 class="text-muted mb-3">منطقة بناء الاستطلاع</h4>
                        <p class="text-muted mb-3">اسحب أنواع الأسئلة من الشريط الجانبي لبناء استطلاعك</p>
                        <div class="empty-state-tips">
                            <div class="tip-item">
                                <i class="fas fa-drag me-2"></i>
                                <span>اسحب الأسئلة لإعادة ترتيبها</span>
                            </div>
                            <div class="tip-item">
                                <i class="fas fa-edit me-2"></i>
                                <span>اضغط على السؤال لتحرير خصائصه</span>
                            </div>
                            <div class="tip-item">
                                <i class="fas fa-lightbulb me-2"></i>
                                <span>ابدأ بسؤال ترحيبي</span>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            questionsArea.classList.remove('has-questions');
        } else {
            questionsArea.classList.add('has-questions');
        }
    }

    updateSurveyHeader() {
        // Update survey header display if needed
    }

    loadSurveyData() {
        // Load existing survey data if editing
    }

    getSurveyData() {
        const titleField = document.getElementById('surveyTitle');
        const titleArField = document.getElementById('surveyTitleAr');
        const descField = document.getElementById('surveyDescription');
        const descArField = document.getElementById('surveyDescriptionAr');

        return {
            title: titleField ? titleField.value : '',
            title_ar: titleArField ? titleArField.value : '',
            description: descField ? descField.value : '',
            description_ar: descArField ? descArField.value : '',
            questions: this.questions
        };
    }
}

// Global functions
function previewSurvey() {
    const surveyData = surveyBuilder.getSurveyData();
    const previewContent = document.getElementById('previewContent');
    
    // Clear existing content safely
    previewContent.textContent = '';
    
    // Create main container
    const surveyContainer = document.createElement('div');
    surveyContainer.className = 'survey-preview-content';
    
    // Create and append title
    const title = document.createElement('h3');
    title.className = 'text-center mb-4';
    title.textContent = surveyData.title_ar || surveyData.title;
    surveyContainer.appendChild(title);
    
    // Create and append description if exists
    if (surveyData.description_ar || surveyData.description) {
        const description = document.createElement('p');
        description.className = 'text-center text-muted mb-4';
        description.textContent = surveyData.description_ar || surveyData.description;
        surveyContainer.appendChild(description);
    }
    
    // Add questions
    surveyData.questions.forEach((question, index) => {
        const questionDiv = document.createElement('div');
        questionDiv.className = 'preview-question';
        
        const questionHeader = document.createElement('h6');
        questionHeader.textContent = `${index + 1}. ${question.text_ar || question.text}`;
        
        if (question.is_required) {
            const requiredSpan = document.createElement('span');
            requiredSpan.className = 'text-danger';
            requiredSpan.textContent = '*';
            questionHeader.appendChild(requiredSpan);
        }
        
        questionDiv.appendChild(questionHeader);
        
        const questionContent = document.createElement('div');
        questionContent.className = 'mt-2';
        
        // Use safe rendering for question preview
        const previewElement = surveyBuilder.renderQuestionPreviewSafe(question);
        questionContent.appendChild(previewElement);
        
        questionDiv.appendChild(questionContent);
        surveyContainer.appendChild(questionDiv);
    });
    
    previewContent.appendChild(surveyContainer);
    
    const modal = new bootstrap.Modal(document.getElementById('previewModal'));
    modal.show();
}

async function saveSurvey() {
    const surveyData = surveyBuilder.getSurveyData();
    
    if (!surveyData.title && !surveyData.title_ar) {
        alert('يرجى إدخال عنوان الاستطلاع');
        return;
    }
    
    if (surveyData.questions.length === 0) {
        alert('يرجى إضافة سؤال واحد على الأقل');
        return;
    }
    
    try {
        console.log('Survey data to save:', surveyData);
        
        // Show saving status
        const saveBtn = document.querySelector('[onclick="saveSurvey()"]');
        if (saveBtn) {
            saveBtn.disabled = true;
            saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>جاري الحفظ...';
        }
        
        const response = await fetch('/api/surveys/save-builder', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                surveyTitle: surveyData.title,
                surveyTitleAr: surveyData.title_ar,
                surveyDescription: surveyData.description,
                surveyDescriptionAr: surveyData.description_ar,
                questions: surveyData.questions
            })
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            alert(`تم حفظ الاستطلاع بنجاح!\n\nرابط الاستطلاع المباشر: ${window.location.origin}${result.survey.live_url}\nالرقم المختصر: ${result.survey.short_id}`);
            
            // Store survey info for potential use
            window.savedSurvey = result.survey;
            
            // Show live link display
            updateLiveLinkDisplay(result.survey);
            
            if (confirm('هل تريد فتح الاستطلاع المباشر في نافذة جديدة؟')) {
                window.open(`${window.location.origin}${result.survey.live_url}`, '_blank');
            }
        } else {
            throw new Error(result.error || 'خطأ في حفظ الاستطلاع');
        }
        
    } catch (error) {
        console.error('Error saving survey:', error);
        alert('خطأ في حفظ الاستطلاع: ' + error.message);
    } finally {
        // Reset save button
        const saveBtn = document.querySelector('[onclick="saveSurvey()"]');
        if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.innerHTML = '<i class="fas fa-save me-2"></i>حفظ الاستطلاع';
        }
    }
}

async function publishSurvey() {
    if (confirm('هل أنت متأكد من نشر الاستطلاع؟ سيصبح متاحاً للجمهور.')) {
        try {
            await saveSurvey();
            alert('تم نشر الاستطلاع بنجاح');
        } catch (error) {
            console.error('Error publishing survey:', error);
            alert('خطأ في نشر الاستطلاع');
        }
    }
}

function updateLiveLinkDisplay(survey) {
    // Create or update a live link display area
    let linkDisplay = document.getElementById('liveLinkDisplay');
    
    if (!linkDisplay) {
        linkDisplay = document.createElement('div');
        linkDisplay.id = 'liveLinkDisplay';
        linkDisplay.className = 'alert alert-success mt-3';
        
        // Find a good place to insert it (after survey title or at top of form)
        const surveySettings = document.querySelector('.survey-settings') || document.querySelector('.container');
        if (surveySettings) {
            surveySettings.appendChild(linkDisplay);
        }
    }
    
    linkDisplay.innerHTML = `
        <div class="d-flex align-items-center justify-content-between">
            <div>
                <h6 class="mb-1"><i class="fas fa-link me-2"></i>رابط الاستطلاع المباشر</h6>
                <small class="text-muted">يمكن مشاركة هذا الرابط مع المشاركين</small>
            </div>
            <div class="text-end">
                <div class="input-group" style="width: 300px;">
                    <input type="text" class="form-control" value="${window.location.origin}${survey.live_url}" readonly>
                    <button class="btn btn-outline-primary" onclick="copyToClipboard('${window.location.origin}${survey.live_url}')">
                        <i class="fas fa-copy"></i>
                    </button>
                    <button class="btn btn-primary" onclick="window.open('${window.location.origin}${survey.live_url}', '_blank')">
                        <i class="fas fa-external-link-alt"></i>
                    </button>
                </div>
            </div>
        </div>
    `;
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Show temporary success message
        const notification = document.createElement('div');
        notification.className = 'alert alert-success position-fixed';
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 200px;';
        notification.innerHTML = '<i class="fas fa-check me-2"></i>تم نسخ الرابط';
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 2000);
    });
}