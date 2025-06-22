
/**
 * Survey Builder JavaScript - Arabic VoC Platform
 * Interactive drag-and-drop survey builder with RTL support
 */

class SurveyBuilder {
    constructor() {
        this.questions = [];
        this.currentQuestionId = null;
        this.questionIdCounter = 1;
        this.dragController = null;
        
        this.init();
    }

    init() {
        console.log('Initializing SurveyBuilder...');
        this.setupAdvancedDragAndDrop();
        this.setupEventListeners();
        this.loadSurveyData();
        console.log('SurveyBuilder initialized');
    }

    setupAdvancedDragAndDrop() {
        // First check if AdvancedDragController is available
        if (typeof AdvancedDragController !== 'undefined') {
            try {
                this.dragController = new AdvancedDragController({
                    container: document.querySelector('.builder-container'),
                    questionsArea: document.getElementById('questionsArea'),
                    sidebar: document.getElementById('questionTypes'),
                    onQuestionAdd: (questionType) => this.addQuestion(questionType),
                    onQuestionReorder: (evt) => this.reorderQuestions(evt)
                });
                console.log('Advanced drag controller initialized');
            } catch (error) {
                console.warn('Advanced drag controller failed, falling back to basic:', error);
                this.setupBasicDragAndDrop();
            }
        } else {
            console.warn('AdvancedDragController not found, using basic drag and drop');
            this.setupBasicDragAndDrop();
        }
    }

    setupBasicDragAndDrop() {
        // Fallback to basic SortableJS implementation
        const questionTypes = document.getElementById('questionTypes');
        const questionsArea = document.getElementById('questionsArea');
        
        if (!questionTypes || !questionsArea) {
            console.error('Required elements not found for drag and drop');
            return;
        }

        // Setup sortable for questions area
        this.sortable = Sortable.create(questionsArea, {
            group: {
                name: 'questions',
                pull: false,
                put: ['questionTypes']
            },
            animation: 300,
            easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
            ghostClass: 'sortable-ghost',
            chosenClass: 'sortable-chosen',
            dragClass: 'sortable-drag',
            onAdd: (evt) => {
                const questionType = evt.item.dataset.type;
                console.log('Adding question type:', questionType);
                if (questionType) {
                    this.addQuestion(questionType);
                    evt.item.remove(); // Remove the dragged element
                }
            },
            onUpdate: (evt) => {
                console.log('Question reordered');
                this.reorderQuestions();
            }
        });

        // Make question types sortable (for dragging)
        this.sidebarSortable = Sortable.create(questionTypes, {
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
            },
            onEnd: (evt) => {
                console.log('Ended dragging');
                evt.item.classList.remove('dragging');
                document.body.classList.remove('drag-active');
            }
        });

        console.log('Basic drag and drop initialized');
    }

    setupEventListeners() {
        // Survey header fields
        document.getElementById('surveyTitle').addEventListener('input', () => {
            this.updateSurveyData();
        });

        document.getElementById('surveyTitleEn').addEventListener('input', () => {
            this.updateSurveyData();
        });

        document.getElementById('surveyDescription').addEventListener('input', () => {
            this.updateSurveyData();
        });

        document.getElementById('surveyDescriptionEn').addEventListener('input', () => {
            this.updateSurveyData();
        });
    }

    addQuestion(type) {
        const questionId = this.questionIdCounter++;
        const question = {
            id: questionId,
            type: type,
            text: this.getDefaultQuestionText(type),
            text_ar: this.getDefaultQuestionTextAr(type),
            description: '',
            description_ar: '',
            is_required: false,
            order_index: this.questions.length,
            options: this.getDefaultOptions(type),
            validation_rules: {},
            display_logic: {}
        };

        this.questions.push(question);
        this.renderQuestion(question);
        this.selectQuestion(questionId);
        this.updateQuestionsArea();
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
        
        // Remove placeholder if this is the first question
        if (this.questions.length === 1) {
            questionsArea.innerHTML = '';
            questionsArea.classList.add('has-questions');
        }

        const questionElement = document.createElement('div');
        questionElement.className = 'question-item';
        questionElement.dataset.questionId = question.id;
        questionElement.setAttribute('tabindex', '0');
        questionElement.setAttribute('role', 'button');
        questionElement.setAttribute('aria-label', `${question.text_ar || question.text} - ${this.getQuestionTypeLabel(question.type)}`);
        
        questionElement.innerHTML = `
            <div class="question-header">
                <div class="d-flex align-items-center">
                    <i class="fas fa-grip-vertical drag-handle me-3" 
                       title="اسحب لإعادة الترتيب" 
                       aria-label="مقبض السحب لإعادة ترتيب السؤال"></i>
                    <span class="badge bg-primary me-2">${this.getQuestionTypeLabel(question.type)}</span>
                    <span class="question-number">السؤال ${question.order_index + 1}</span>
                </div>
                <div class="question-actions">
                    <button class="btn btn-sm btn-outline-primary" 
                            onclick="surveyBuilder.duplicateQuestion(${question.id})"
                            title="نسخ السؤال"
                            aria-label="نسخ السؤال">
                        <i class="fas fa-copy"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" 
                            onclick="surveyBuilder.deleteQuestion(${question.id})"
                            title="حذف السؤال"
                            aria-label="حذف السؤال">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
            <div class="question-content">
                <h6 class="question-text">${question.text_ar || question.text}</h6>
                ${question.description_ar || question.description ? `<p class="text-muted">${question.description_ar || question.description}</p>` : ''}
                <div class="question-preview">
                    ${this.renderQuestionPreview(question)}
                </div>
            </div>
        `;

        // Enhanced event listeners
        questionElement.addEventListener('click', () => {
            this.selectQuestion(question.id);
        });

        // Add keyboard support
        questionElement.setAttribute('tabindex', '0');
        questionElement.setAttribute('role', 'button');
        questionElement.setAttribute('aria-label', `تحرير السؤال: ${question.text_ar || question.text}`);
        
        questionElement.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.selectQuestion(question.id);
            }
        });

        // Keyboard navigation support
        questionElement.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.selectQuestion(question.id);
            }
        });

        questionsArea.appendChild(questionElement);
        
        // Animate question addition
        if (this.dragController && this.dragController.animations) {
            this.dragController.animations.animateQuestionAdd(questionElement);
        }
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
        // Remove active class from all questions
        document.querySelectorAll('.question-item').forEach(item => {
            item.classList.remove('active');
        });

        // Add active class to selected question
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
        
        propertiesContainer.innerHTML = `
            <div class="property-group">
                <h6>النص والمحتوى</h6>
                
                <div class="mb-3">
                    <label class="form-label">نص السؤال (عربي)</label>
                    <textarea class="form-control form-control-modern" rows="2" 
                              id="questionTextAr" placeholder="أدخل نص السؤال بالعربية">${question.text_ar}</textarea>
                </div>
                
                <div class="mb-3">
                    <label class="form-label">نص السؤال (إنجليزي)</label>
                    <textarea class="form-control form-control-modern" rows="2" 
                              id="questionText" placeholder="Enter question text in English">${question.text}</textarea>
                </div>
                
                <div class="mb-3">
                    <label class="form-label">وصف إضافي (عربي)</label>
                    <textarea class="form-control form-control-modern" rows="2" 
                              id="questionDescAr" placeholder="وصف اختياري للسؤال">${question.description_ar}</textarea>
                </div>
                
                <div class="mb-3">
                    <label class="form-label">وصف إضافي (إنجليزي)</label>
                    <textarea class="form-control form-control-modern" rows="2" 
                              id="questionDesc" placeholder="Optional question description">${question.description}</textarea>
                </div>
            </div>

            <div class="property-group">
                <h6>الإعدادات</h6>
                
                <div class="form-check mb-3">
                    <input class="form-check-input" type="checkbox" id="isRequired" 
                           ${question.is_required ? 'checked' : ''}>
                    <label class="form-check-label" for="isRequired">
                        سؤال إجباري
                    </label>
                </div>
            </div>

            ${this.renderQuestionTypeOptions(question)}
        `;

        // Setup event listeners for property changes
        this.setupPropertyEventListeners(questionId);
    }

    renderQuestionTypeOptions(question) {
        switch (question.type) {
            case 'multiple_choice':
            case 'checkbox':
            case 'dropdown':
                return `
                    <div class="property-group">
                        <h6>خيارات الإجابة</h6>
                        <div id="optionsList">
                            ${question.options.choices.map((choice, index) => `
                                <div class="option-input" data-index="${index}">
                                    <input type="text" class="form-control form-control-modern" 
                                           value="${choice.text}" placeholder="الخيار ${index + 1}">
                                    <button class="btn btn-sm btn-outline-danger" onclick="surveyBuilder.removeOption(${index})">
                                        <i class="fas fa-times"></i>
                                    </button>
                                </div>
                            `).join('')}
                        </div>
                        <button class="btn btn-sm btn-outline-primary mt-2" onclick="surveyBuilder.addOption()">
                            <i class="fas fa-plus me-2"></i>
                            إضافة خيار
                        </button>
                    </div>
                `;

            case 'rating':
                return `
                    <div class="property-group">
                        <h6>إعدادات التقييم</h6>
                        <div class="mb-3">
                            <label class="form-label">أقصى تقييم</label>
                            <select class="form-select form-control-modern" id="maxRating">
                                <option value="3" ${question.options.max_rating === 3 ? 'selected' : ''}>3 نجوم</option>
                                <option value="5" ${question.options.max_rating === 5 ? 'selected' : ''}>5 نجوم</option>
                                <option value="7" ${question.options.max_rating === 7 ? 'selected' : ''}>7 نجوم</option>
                                <option value="10" ${question.options.max_rating === 10 ? 'selected' : ''}>10 نجوم</option>
                            </select>
                        </div>
                    </div>
                `;

            case 'slider':
                return `
                    <div class="property-group">
                        <h6>إعدادات المؤشر</h6>
                        <div class="row">
                            <div class="col-6">
                                <label class="form-label">القيمة الدنيا</label>
                                <input type="number" class="form-control form-control-modern" 
                                       id="minValue" value="${question.options.min_value || 0}">
                            </div>
                            <div class="col-6">
                                <label class="form-label">القيمة العليا</label>
                                <input type="number" class="form-control form-control-modern" 
                                       id="maxValue" value="${question.options.max_value || 10}">
                            </div>
                        </div>
                        <div class="mt-3">
                            <label class="form-label">خطوة التدرج</label>
                            <input type="number" class="form-control form-control-modern" 
                                   id="stepValue" value="${question.options.step || 1}" min="1">
                        </div>
                    </div>
                `;

            default:
                return '';
        }
    }

    setupPropertyEventListeners(questionId) {
        const question = this.questions.find(q => q.id === questionId);
        if (!question) return;

        // Text fields
        ['questionTextAr', 'questionText', 'questionDescAr', 'questionDesc'].forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.addEventListener('input', () => {
                    const property = fieldId.replace('question', '').toLowerCase();
                    if (property.includes('ar')) {
                        question[property.replace('ar', '_ar')] = field.value;
                    } else {
                        question[property.replace('text', 'text').replace('desc', 'description')] = field.value;
                    }
                    this.updateQuestionDisplay(questionId);
                });
            }
        });

        // Required checkbox
        const isRequiredField = document.getElementById('isRequired');
        if (isRequiredField) {
            isRequiredField.addEventListener('change', () => {
                question.is_required = isRequiredField.checked;
                this.updateQuestionDisplay(questionId);
            });
        }

        // Type-specific listeners
        this.setupTypeSpecificListeners(question);
    }

    setupTypeSpecificListeners(question) {
        // Rating max value
        const maxRatingField = document.getElementById('maxRating');
        if (maxRatingField) {
            maxRatingField.addEventListener('change', () => {
                question.options.max_rating = parseInt(maxRatingField.value);
                this.updateQuestionDisplay(question.id);
            });
        }

        // Slider values
        ['minValue', 'maxValue', 'stepValue'].forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.addEventListener('input', () => {
                    const property = fieldId.replace('Value', '_value').toLowerCase();
                    question.options[property] = parseInt(field.value) || 0;
                    this.updateQuestionDisplay(question.id);
                });
            }
        });

        // Options for choice-based questions
        this.setupOptionListeners(question);
    }

    setupOptionListeners(question) {
        const optionInputs = document.querySelectorAll('#optionsList .option-input input');
        optionInputs.forEach((input, index) => {
            input.addEventListener('input', () => {
                if (question.options.choices && question.options.choices[index]) {
                    question.options.choices[index].text = input.value;
                    this.updateQuestionDisplay(question.id);
                }
            });
        });
    }

    addOption() {
        if (!this.currentQuestionId) return;
        
        const question = this.questions.find(q => q.id === this.currentQuestionId);
        if (!question || !question.options.choices) return;

        const newIndex = question.options.choices.length + 1;
        question.options.choices.push({
            text: `الخيار ${newIndex}`,
            text_en: `Option ${newIndex}`,
            value: `option${newIndex}`
        });

        this.renderQuestionProperties(this.currentQuestionId);
        this.updateQuestionDisplay(this.currentQuestionId);
    }

    removeOption(index) {
        if (!this.currentQuestionId) return;
        
        const question = this.questions.find(q => q.id === this.currentQuestionId);
        if (!question || !question.options.choices) return;

        if (question.options.choices.length <= 2) {
            alert('يجب أن يكون هناك خياران على الأقل');
            return;
        }

        question.options.choices.splice(index, 1);
        this.renderQuestionProperties(this.currentQuestionId);
        this.updateQuestionDisplay(this.currentQuestionId);
    }

    renderQuestionPreview(question) {
        switch (question.type) {
            case 'text':
                return '<input type="text" class="form-control" placeholder="إدخال نص قصير..." disabled>';
            
            case 'textarea':
                return '<textarea class="form-control" rows="3" placeholder="إدخال نص طويل..." disabled></textarea>';
            
            case 'multiple_choice':
                return question.options.choices.map((choice, index) => 
                    `<div class="form-check">
                        <input class="form-check-input" type="radio" name="preview_${question.id}" disabled>
                        <label class="form-check-label">${choice.text}</label>
                    </div>`
                ).join('');
            
            case 'checkbox':
                return question.options.choices.map((choice, index) => 
                    `<div class="form-check">
                        <input class="form-check-input" type="checkbox" disabled>
                        <label class="form-check-label">${choice.text}</label>
                    </div>`
                ).join('');
            
            case 'dropdown':
                return `<select class="form-select" disabled>
                    <option>اختر من القائمة...</option>
                    ${question.options.choices.map(choice => 
                        `<option>${choice.text}</option>`
                    ).join('')}
                </select>`;
            
            case 'rating':
                const stars = Array.from({length: question.options.max_rating}, (_, i) => 
                    `<i class="fas fa-star text-warning"></i>`
                ).join('');
                return `<div class="rating-preview">${stars}</div>`;
            
            case 'slider':
                return `<div class="slider-preview">
                    <input type="range" class="form-range" 
                           min="${question.options.min_value}" 
                           max="${question.options.max_value}" 
                           step="${question.options.step}" disabled>
                    <div class="d-flex justify-content-between small text-muted">
                        <span>${question.options.labels?.ar?.min || question.options.min_value}</span>
                        <span>${question.options.labels?.ar?.max || question.options.max_value}</span>
                    </div>
                </div>`;
            
            case 'nps':
                const npsButtons = Array.from({length: 11}, (_, i) => 
                    `<button class="btn btn-outline-primary btn-sm me-1" disabled>${i}</button>`
                ).join('');
                return `<div class="nps-preview">
                    ${npsButtons}
                    <div class="d-flex justify-content-between small text-muted mt-2">
                        <span>لن أوصي أبداً</span>
                        <span>سأوصي بقوة</span>
                    </div>
                </div>`;
            
            case 'date':
                return '<input type="date" class="form-control" disabled>';
            
            case 'email':
                return '<input type="email" class="form-control" placeholder="example@domain.com" disabled>';
            
            case 'phone':
                return '<input type="tel" class="form-control" placeholder="+966 50 123 4567" disabled>';
            
            default:
                return '<div class="text-muted">معاينة غير متوفرة</div>';
        }
    }
        ['minValue', 'maxValue', 'stepValue'].forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.addEventListener('input', () => {
                    const property = fieldId.replace('Value', '_value').toLowerCase();
                    question.options[property] = parseInt(field.value);
                    this.updateQuestionDisplay(question.id);
                });
            }
        });
    }

    addOption() {
        const question = this.questions.find(q => q.id === this.currentQuestionId);
        if (!question || !question.options.choices) return;

        const newIndex = question.options.choices.length + 1;
        question.options.choices.push({
            text: `الخيار ${newIndex}`,
            text_en: `Option ${newIndex}`,
            value: `option${newIndex}`
        });

        this.renderQuestionProperties(this.currentQuestionId);
        this.updateQuestionDisplay(this.currentQuestionId);
    }

    removeOption(index) {
        const question = this.questions.find(q => q.id === this.currentQuestionId);
        if (!question || !question.options.choices) return;

        question.options.choices.splice(index, 1);
        this.renderQuestionProperties(this.currentQuestionId);
        this.updateQuestionDisplay(this.currentQuestionId);
    }

    updateQuestionDisplay(questionId) {
        const question = this.questions.find(q => q.id === questionId);
        if (!question) return;

        const questionElement = document.querySelector(`[data-question-id="${questionId}"]`);
        if (!questionElement) return;

        // Update question text
        const questionTextElement = questionElement.querySelector('.question-text');
        if (questionTextElement) {
            questionTextElement.textContent = question.text_ar || question.text;
        }

        // Update description
        const descElement = questionElement.querySelector('.text-muted');
        if (descElement) {
            if (question.description_ar || question.description) {
                descElement.textContent = question.description_ar || question.description;
                descElement.style.display = 'block';
            } else {
                descElement.style.display = 'none';
            }
        }

        // Update preview
        const previewElement = questionElement.querySelector('.question-preview');
        if (previewElement) {
            previewElement.innerHTML = this.renderQuestionPreview(question);
        }
    }

    duplicateQuestion(questionId) {
        const question = this.questions.find(q => q.id === questionId);
        if (!question) return;

        const newQuestion = {
            ...JSON.parse(JSON.stringify(question)),
            id: this.questionIdCounter++,
            order_index: this.questions.length
        };

        this.questions.push(newQuestion);
        this.renderQuestion(newQuestion);
        this.selectQuestion(newQuestion.id);
    }

    deleteQuestion(questionId) {
        if (confirm('هل أنت متأكد من حذف هذا السؤال؟')) {
            this.questions = this.questions.filter(q => q.id !== questionId);
            
            // Remove from DOM
            const questionElement = document.querySelector(`[data-question-id="${questionId}"]`);
            if (questionElement) {
                questionElement.remove();
            }

            // Clear properties if this was the selected question
            if (this.currentQuestionId === questionId) {
                this.currentQuestionId = null;
                document.getElementById('questionProperties').innerHTML = 
                    '<p class="text-muted text-center">حدد سؤالاً لتحرير خصائصه</p>';
            }

            // Update question numbering
            this.reorderQuestions();
            this.updateQuestionsArea();
        }
    }

    reorderQuestions() {
        this.questions.forEach((question, index) => {
            question.order_index = index;
        });

        // Update display numbers
        document.querySelectorAll('.question-number').forEach((element, index) => {
            element.textContent = `السؤال ${index + 1}`;
        });
    }

    updateQuestionsArea() {
        const questionsArea = document.getElementById('questionsArea');
        
        if (this.questions.length === 0) {
            questionsArea.innerHTML = `
                <i class="fas fa-plus-circle" style="font-size: 3rem; color: var(--primary-color); margin-bottom: 1rem;"></i>
                <h4>ابدأ ببناء استطلاعك</h4>
                <p class="text-muted">اسحب أنواع الأسئلة من الشريط الجانبي لإضافتها هنا</p>
            `;
            questionsArea.classList.remove('has-questions');
        }
    }

    updateSurveyData() {
        // This would typically save to a data store
        console.log('Survey data updated');
    }

    loadSurveyData() {
        // Load existing survey data if editing
        const urlParams = new URLSearchParams(window.location.search);
        const surveyId = urlParams.get('id');
        
        if (surveyId) {
            // Load survey data from API
            this.loadExistingSurvey(surveyId);
        }
    }

    async loadExistingSurvey(surveyId) {
        try {
            const response = await fetch(`/api/surveys/${surveyId}`);
            const surveyData = await response.json();
            
            // Populate survey header
            document.getElementById('surveyTitle').value = surveyData.title || '';
            document.getElementById('surveyTitleEn').value = surveyData.title_ar || '';
            document.getElementById('surveyDescription').value = surveyData.description || '';
            document.getElementById('surveyDescriptionEn').value = surveyData.description_ar || '';
            
            // Load questions
            if (surveyData.questions) {
                this.questions = surveyData.questions.map(q => ({
                    ...q,
                    id: this.questionIdCounter++
                }));
                
                this.questions.forEach(question => {
                    this.renderQuestion(question);
                });
                
                this.updateQuestionsArea();
            }
        } catch (error) {
            console.error('Error loading survey:', error);
            alert('خطأ في تحميل بيانات الاستطلاع');
        }
    }

    getSurveyData() {
        return {
            title: document.getElementById('surveyTitleEn').value,
            title_ar: document.getElementById('surveyTitle').value,
            description: document.getElementById('surveyDescriptionEn').value,
            description_ar: document.getElementById('surveyDescription').value,
            primary_language: 'ar',
            supported_languages: ['ar', 'en'],
            rtl_enabled: true,
            is_public: false,
            requires_login: false,
            allow_anonymous: true,
            multiple_responses: false,
            questions: this.questions.map(q => ({
                text: q.text,
                text_ar: q.text_ar,
                description: q.description,
                description_ar: q.description_ar,
                type: q.type,
                is_required: q.is_required,
                order_index: q.order_index,
                options: q.options,
                validation_rules: q.validation_rules,
                display_logic: q.display_logic
            }))
        };
    }
}

// Global functions
function previewSurvey() {
    const surveyData = surveyBuilder.getSurveyData();
    const previewContent = document.getElementById('previewContent');
    
    let previewHtml = `
        <div class="survey-preview-content">
            <h3 class="text-center mb-4">${surveyData.title_ar || surveyData.title}</h3>
            ${surveyData.description_ar || surveyData.description ? 
                `<p class="text-center text-muted mb-4">${surveyData.description_ar || surveyData.description}</p>` : 
                ''}
    `;
    
    surveyData.questions.forEach((question, index) => {
        previewHtml += `
            <div class="preview-question">
                <h6>
                    ${index + 1}. ${question.text_ar || question.text}
                    ${question.is_required ? '<span class="text-danger">*</span>' : ''}
                </h6>
                ${question.description_ar || question.description ? 
                    `<p class="text-muted small">${question.description_ar || question.description}</p>` : 
                    ''}
                <div class="mt-2">
                    ${surveyBuilder.renderQuestionPreview(question)}
                </div>
            </div>
        `;
    });
    
    previewHtml += '</div>';
    previewContent.innerHTML = previewHtml;
    
    // Show modal
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
        // For demonstration, we'll show a success message and redirect to surveys page
        // In production, this would call the API with proper authentication
        
        console.log('Survey data to save:', surveyData);
        
        // Simulate API call
        const mockResponse = {
            id: Math.floor(Math.random() * 1000),
            title: surveyData.title_ar || surveyData.title,
            status: 'draft'
        };
        
        alert('تم حفظ الاستطلاع بنجاح كمسودة');
        
        // Show save confirmation and option to return to surveys
        if (confirm('هل تريد العودة إلى صفحة الاستطلاعات؟')) {
            window.location.href = '/surveys';
        }
        
    } catch (error) {
        console.error('Error saving survey:', error);
        alert('خطأ في حفظ الاستطلاع: ' + error.message);
    }
}

async function publishSurvey() {
    if (confirm('هل أنت متأكد من نشر الاستطلاع؟ سيصبح متاحاً للجمهور.')) {
        try {
            await saveSurvey();
            // Additional publish logic would go here
            alert('تم نشر الاستطلاع بنجاح');
        } catch (error) {
            console.error('Error publishing survey:', error);
            alert('خطأ في نشر الاستطلاع');
        }
    }
}

// Initialize survey builder
let surveyBuilder;
document.addEventListener('DOMContentLoaded', () => {
    surveyBuilder = new SurveyBuilder();
});
