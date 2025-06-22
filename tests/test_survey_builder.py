"""
Comprehensive tests for Survey Builder functionality
Tests drag-and-drop, Arabic content, and UX features
"""

import pytest
from app import app

class TestSurveyBuilderCore:
    """Test core survey builder functionality"""
    
    def setup_method(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        self.app_context.pop()
    
    @pytest.mark.ui
    def test_survey_builder_page_loads(self):
        """Test survey builder page renders correctly"""
        response = self.client.get('/surveys/builder')
        assert response.status_code == 200
        
        content = response.data.decode('utf-8')
        assert 'منشئ الاستطلاعات' in content  # Survey Builder
        assert 'drag' in content.lower() or 'سحب' in content
        assert 'question' in content.lower() or 'سؤال' in content
    
    @pytest.mark.ui
    def test_drag_drop_interface_elements(self):
        """Test drag-and-drop interface elements are present"""
        response = self.client.get('/surveys/builder')
        content = response.data.decode('utf-8')
        
        # Check for drag-and-drop related elements
        assert 'draggable' in content or 'sortable' in content
        assert 'question-types' in content or 'أنواع الأسئلة' in content
        assert 'canvas' in content or 'منطقة العمل' in content
    
    @pytest.mark.arabic
    def test_arabic_question_types(self):
        """Test Arabic question type support"""
        response = self.client.get('/surveys/builder')
        content = response.data.decode('utf-8')
        
        # Check for Arabic question types
        arabic_question_types = [
            'اختيار متعدد',    # Multiple Choice
            'نص قصير',        # Short Text
            'نص طويل',        # Long Text
            'تقييم',          # Rating
            'نعم/لا'          # Yes/No
        ]
        
        for question_type in arabic_question_types:
            assert question_type in content
    
    @pytest.mark.ui
    def test_responsive_design_elements(self):
        """Test responsive design for survey builder"""
        response = self.client.get('/surveys/builder')
        content = response.data.decode('utf-8')
        
        # Check responsive Bootstrap classes
        assert 'col-lg-' in content
        assert 'col-md-' in content
        assert 'd-none d-md-block' in content or 'responsive' in content.lower()


class TestSurveyBuilderAPI:
    """Test survey builder API endpoints"""
    
    def setup_method(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        self.app_context.pop()
    
    @pytest.mark.api
    def test_create_arabic_survey(self):
        """Test creating survey with Arabic content"""
        survey_data = {
            'title': 'استطلاع رضا العملاء',
            'description': 'استطلاع لقياس مستوى رضا العملاء عن خدماتنا',
            'questions': [
                {
                    'type': 'multiple_choice',
                    'text': 'كيف تقيم خدماتنا؟',
                    'options': ['ممتاز', 'جيد جداً', 'جيد', 'مقبول', 'ضعيف']
                },
                {
                    'type': 'text',
                    'text': 'ما هي اقتراحاتك لتحسين خدماتنا؟'
                }
            ]
        }
        
        response = self.client.post('/api/surveys/create', json=survey_data)
        assert response.status_code in [200, 201]
        
        if response.status_code in [200, 201]:
            data = response.get_json()
            assert 'id' in data or 'survey_id' in data
    
    @pytest.mark.api  
    def test_survey_validation(self):
        """Test survey data validation"""
        # Test missing title
        invalid_survey = {
            'description': 'وصف بدون عنوان',
            'questions': []
        }
        
        response = self.client.post('/api/surveys/create', json=invalid_survey)
        assert response.status_code in [400, 422]
        
        # Test empty questions
        invalid_survey2 = {
            'title': 'استطلاع بدون أسئلة',
            'description': 'وصف',
            'questions': []
        }
        
        response = self.client.post('/api/surveys/create', json=invalid_survey2)
        assert response.status_code in [400, 422]


class TestSurveyBuilderPerformance:
    """Performance tests for survey builder"""
    
    def setup_method(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        self.app_context.pop()
    
    @pytest.mark.performance
    def test_survey_builder_load_time(self):
        """Test survey builder loads within performance targets"""
        import time
        
        start_time = time.time()
        response = self.client.get('/surveys/builder')
        load_time = time.time() - start_time
        
        assert response.status_code == 200
        assert load_time < 2.0, f"Survey builder load time {load_time:.2f}s too slow"
    
    @pytest.mark.performance
    def test_large_survey_creation(self):
        """Test creating survey with many questions"""
        import time
        
        # Create survey with 20 questions
        questions = []
        for i in range(20):
            questions.append({
                'type': 'multiple_choice',
                'text': f'سؤال رقم {i+1}',
                'options': ['خيار 1', 'خيار 2', 'خيار 3', 'خيار 4']
            })
        
        survey_data = {
            'title': 'استطلاع كبير',
            'description': 'استطلاع يحتوي على عدد كبير من الأسئلة',
            'questions': questions
        }
        
        start_time = time.time()
        response = self.client.post('/api/surveys/create', json=survey_data)
        creation_time = time.time() - start_time
        
        assert creation_time < 3.0, f"Large survey creation took {creation_time:.2f}s"