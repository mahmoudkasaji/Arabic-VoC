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
        console.log('SurveyBuilder initialized');
    }

    setupDragAndDrop() {
        const questionTypes = document.getElementById('questionTypes');
        const questionsArea = document.getElementById('questionsArea');
        
        if (!questionTypes || !questionsArea) {
            console.error('Required elements not found for drag and drop');
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

        console.log('Drag and drop initialized');
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
                    mobileAddBtn.innerHTML = '<i class="fas fa-plus"></i> إضافة السؤال';
                    
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
        
        questionElement.innerHTML = `
            <div class="question-header">
                <div class="d-flex align-items-center">
                    <i class="fas fa-grip-vertical drag-handle me-3" title="اسحب لإعادة الترتيب"></i>
                    <span class="badge bg-primary me-2">${this.getQuestionTypeLabel(question.type)}</span>
                    <span class="question-number">السؤال ${question.order_index + 1}</span>
                </div>
                <div class="question-actions">
                    <button class="btn btn-sm btn-outline-primary" onclick="surveyBuilder.duplicateQuestion(${question.id})" title="نسخ السؤال">
                        <i class="fas fa-copy"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="surveyBuilder.deleteQuestion(${question.id})" title="حذف السؤال">
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
                
                <div class="form-check mb-3">
                    <input class="form-check-input" type="checkbox" id="isRequired" 
                           ${question.is_required ? 'checked' : ''}>
                    <label class="form-check-label" for="isRequired">
                        سؤال إجباري
                    </label>
                </div>
            </div>
        `;

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
                <div class="mt-2">
                    ${surveyBuilder.renderQuestionPreview(question)}
                </div>
            </div>
        `;
    });
    
    previewHtml += '</div>';
    previewContent.innerHTML = previewHtml;
    
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
        alert('تم حفظ الاستطلاع بنجاح كمسودة');
        
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
            alert('تم نشر الاستطلاع بنجاح');
        } catch (error) {
            console.error('Error publishing survey:', error);
            alert('خطأ في نشر الاستطلاع');
        }
    }
}