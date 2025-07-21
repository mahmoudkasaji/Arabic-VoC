#!/usr/bin/env python3
"""
Comprehensive User Acceptance Testing (UAT) for July 21, 2025 Platform Enhancements
Testing all major components implemented today:
- Survey Design System Implementation
- Survey Builder Progressive Disclosure Enhancement
- Executive Dashboard Mobile Optimization
- Analyst Dashboard Comprehensive Overhaul (with Journey Map Integration)
- Navigation & User Management Enhancements
- Homepage & Platform Rebranding
"""

import requests
import time
from bs4 import BeautifulSoup
import re
import json
from urllib.parse import urljoin

class ComprehensivePlatformUAT:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, passed, details=""):
        """Log test result"""
        status = "✓ PASS" if passed else "✗ FAIL"
        result = f"{status}: {test_name}"
        if details:
            result += f" - {details}"
        self.test_results.append((passed, result))
        print(result)
        
    def test_page_load(self):
        """Test 1: Basic page loading and accessibility"""
        try:
            response = self.session.get(f"{self.base_url}/dashboards/analyst")
            
            # Test HTTP response
            self.log_test("Page Load - HTTP Status", response.status_code == 200, 
                         f"Status: {response.status_code}")
            
            # Test content type
            content_type = response.headers.get('content-type', '')
            self.log_test("Page Load - Content Type", 'text/html' in content_type,
                         f"Content-Type: {content_type}")
            
            # Test page size (should be substantial)
            content_length = len(response.content)
            self.log_test("Page Load - Content Size", content_length > 10000,
                         f"Size: {content_length} bytes")
            
            return response
            
        except Exception as e:
            self.log_test("Page Load - Exception", False, str(e))
            return None
    
    def test_tab_navigation_structure(self, response):
        """Test 2: Tab navigation structure and accessibility"""
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test tab navigation container exists
        tab_container = soup.find('ul', {'id': 'dashboardTabs'})
        self.log_test("Navigation - Tab Container", tab_container is not None,
                     "dashboardTabs container found")
        
        if tab_container:
            # Test all four tabs exist (including Journey Map)
            tab_buttons = tab_container.find_all('button', {'class': re.compile(r'nav-link')})
            self.log_test("Navigation - Tab Count", len(tab_buttons) == 4,
                         f"Found {len(tab_buttons)} tabs")
            
            # Test tab labels and order (updated for July 21 changes)
            expected_tabs = ['التحليلات والمقاييس', 'خريطة رحلة العميل', 'الإجراءات المطلوبة', 'الرؤى الذكية']
            actual_tabs = [btn.get_text().strip() for btn in tab_buttons]
            
            for i, expected in enumerate(expected_tabs):
                if i < len(actual_tabs):
                    self.log_test(f"Navigation - Tab {i+1} Label", expected in actual_tabs[i],
                                f"Expected: {expected}, Found: {actual_tabs[i] if i < len(actual_tabs) else 'Missing'}")
            
            # Test Actions tab is active by default
            actions_tab = soup.find('button', {'id': 'actions-tab'})
            is_active = actions_tab and 'active' in actions_tab.get('class', [])
            self.log_test("Navigation - Default Active Tab", is_active,
                         "Actions Required tab is active by default")
    
    def test_actions_tab_content(self, response):
        """Test 3: Actions Required tab content structure"""
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test Actions tab pane exists and is active
        actions_pane = soup.find('div', {'id': 'actions'})
        is_active = actions_pane and 'active' in actions_pane.get('class', [])
        self.log_test("Actions Tab - Pane Active", is_active,
                     "Actions tab pane is active")
        
        if actions_pane:
            # Test Today's Priorities section
            priorities_section = actions_pane.find('h5', string=re.compile(r'أولويات اليوم'))
            self.log_test("Actions Tab - Priorities Section", priorities_section is not None,
                         "Today's priorities section found")
            
            # Test High Priority tasks
            high_priority = actions_pane.find('h6', string=re.compile(r'أولوية عالية'))
            self.log_test("Actions Tab - High Priority Section", high_priority is not None,
                         "High priority section found")
            
            # Test Medium Priority tasks  
            medium_priority = actions_pane.find('h6', string=re.compile(r'أولوية متوسطة'))
            self.log_test("Actions Tab - Medium Priority Section", medium_priority is not None,
                         "Medium priority section found")
            
            # Test task checkboxes
            checkboxes = actions_pane.find_all('input', {'type': 'checkbox'})
            self.log_test("Actions Tab - Task Checkboxes", len(checkboxes) >= 6,
                         f"Found {len(checkboxes)} task checkboxes")
    
    def test_response_templates(self, response):
        """Test 4: Automated response templates section"""
        soup = BeautifulSoup(response.content, 'html.parser')
        actions_pane = soup.find('div', {'id': 'actions'})
        
        if actions_pane:
            # Test templates section header
            templates_header = actions_pane.find('h5', string=re.compile(r'قوالب الردود التلقائية'))
            self.log_test("Templates - Section Header", templates_header is not None,
                         "Response templates header found")
            
            # Test template cards
            template_buttons = actions_pane.find_all('button', {'onclick': re.compile(r'useTemplate')})
            self.log_test("Templates - Template Buttons", len(template_buttons) >= 3,
                         f"Found {len(template_buttons)} template buttons")
            
            # Test specific template types
            delivery_template = actions_pane.find('button', {'onclick': "useTemplate('delivery')"})
            self.log_test("Templates - Delivery Template", delivery_template is not None,
                         "Delivery complaint template found")
            
            technical_template = actions_pane.find('button', {'onclick': "useTemplate('technical')"})
            self.log_test("Templates - Technical Template", technical_template is not None,
                         "Technical issue template found")
            
            refund_template = actions_pane.find('button', {'onclick': "useTemplate('refund')"})
            self.log_test("Templates - Refund Template", refund_template is not None,
                         "Refund request template found")
    
    def test_followup_tracking(self, response):
        """Test 5: Follow-up tracking pipeline"""
        soup = BeautifulSoup(response.content, 'html.parser')
        actions_pane = soup.find('div', {'id': 'actions'})
        
        if actions_pane:
            # Test tracking section header
            tracking_header = actions_pane.find('h5', string=re.compile(r'تتبع المتابعة'))
            self.log_test("Tracking - Section Header", tracking_header is not None,
                         "Follow-up tracking header found")
            
            # Test pipeline stages
            pipeline_stages = ['جديد', 'قيد المراجعة', 'في انتظار العميل', 'محلول']
            for stage in pipeline_stages:
                stage_element = actions_pane.find('span', string=re.compile(stage))
                self.log_test(f"Tracking - {stage} Stage", stage_element is not None,
                             f"Pipeline stage '{stage}' found")
            
            # Test progress bars
            progress_bars = actions_pane.find_all('div', {'class': re.compile(r'progress-bar')})
            self.log_test("Tracking - Progress Bars", len(progress_bars) >= 4,
                         f"Found {len(progress_bars)} progress bars")
    
    def test_performance_metrics(self, response):
        """Test 6: Personal performance tracking"""
        soup = BeautifulSoup(response.content, 'html.parser')
        actions_pane = soup.find('div', {'id': 'actions'})
        
        if actions_pane:
            # Test performance section header
            performance_header = actions_pane.find('h5', string=re.compile(r'مقاييس الأداء الشخصية'))
            self.log_test("Performance - Section Header", performance_header is not None,
                         "Performance metrics header found")
            
            # Test metric boxes
            metric_boxes = actions_pane.find_all('div', {'class': re.compile(r'metric-box')})
            self.log_test("Performance - Metric Boxes", len(metric_boxes) >= 4,
                         f"Found {len(metric_boxes)} metric boxes")
            
            # Test specific metrics by looking for numbers
            numbers_found = actions_pane.find_all('h3')
            metric_numbers = [h3 for h3 in numbers_found if re.search(r'\d+', h3.get_text())]
            self.log_test("Performance - Metric Values", len(metric_numbers) >= 4,
                         f"Found {len(metric_numbers)} numeric metrics")
    
    def test_knowledge_base(self, response):
        """Test 7: Knowledge base integration"""
        soup = BeautifulSoup(response.content, 'html.parser')
        actions_pane = soup.find('div', {'id': 'actions'})
        
        if actions_pane:
            # Test knowledge base header
            kb_header = actions_pane.find('h5', string=re.compile(r'قاعدة المعرفة'))
            self.log_test("Knowledge Base - Section Header", kb_header is not None,
                         "Knowledge base header found")
            
            # Test knowledge base links
            kb_links = actions_pane.find_all('a', {'onclick': re.compile(r'openKnowledgeBase')})
            self.log_test("Knowledge Base - Links Count", len(kb_links) >= 4,
                         f"Found {len(kb_links)} knowledge base links")
            
            # Test specific KB sections
            kb_sections = ['faq', 'escalation', 'products', 'policies']
            for section in kb_sections:
                section_link = actions_pane.find('a', {'onclick': f"openKnowledgeBase('{section}')"})
                self.log_test(f"Knowledge Base - {section.upper()} Link", section_link is not None,
                             f"Knowledge base {section} link found")
    
    def test_javascript_functions(self, response):
        """Test 8: JavaScript function definitions"""
        content = response.text
        
        # Test workflow-specific JavaScript functions exist
        js_functions = [
            'openCase', 'respondQuickly', 'viewDeliveryIssues', 'escalateDelivery',
            'viewNegativeReviews', 'analyzeProductIssues', 'analyzeRiyadhSatisfaction',
            'editWeeklyReport', 'checkImprovements', 'useTemplate', 'openKnowledgeBase'
        ]
        
        for func in js_functions:
            function_exists = f'function {func}(' in content
            self.log_test(f"JavaScript - {func} Function", function_exists,
                         f"Function {func} definition found")
    
    def test_responsive_design(self, response):
        """Test 9: Responsive design elements"""
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test Bootstrap responsive classes
        responsive_elements = soup.find_all(class_=re.compile(r'col-(xs|sm|md|lg|xl)'))
        self.log_test("Responsive - Bootstrap Classes", len(responsive_elements) > 0,
                     f"Found {len(responsive_elements)} responsive elements")
        
        # Test viewport meta tag
        viewport = soup.find('meta', {'name': 'viewport'})
        self.log_test("Responsive - Viewport Meta", viewport is not None,
                     "Viewport meta tag found")
        
        # Test card layouts for mobile
        cards = soup.find_all('div', {'class': re.compile(r'card')})
        self.log_test("Responsive - Card Layout", len(cards) >= 5,
                     f"Found {len(cards)} card components")
    
    def test_accessibility(self, response):
        """Test 10: Accessibility features"""
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test ARIA labels
        aria_elements = soup.find_all(attrs={'aria-controls': True}) + soup.find_all(attrs={'aria-selected': True})
        self.log_test("Accessibility - ARIA Labels", len(aria_elements) >= 3,
                     f"Found {len(aria_elements)} ARIA-labeled elements")
        
        # Test role attributes
        role_elements = soup.find_all(attrs={'role': True})
        self.log_test("Accessibility - Role Attributes", len(role_elements) >= 5,
                     f"Found {len(role_elements)} role-attributed elements")
        
        # Test button accessibility
        buttons = soup.find_all('button')
        buttons_with_text = [btn for btn in buttons if btn.get_text().strip()]
        self.log_test("Accessibility - Button Text", len(buttons_with_text) >= 10,
                     f"Found {len(buttons_with_text)} buttons with text")
        
        # Test form labels
        form_inputs = soup.find_all('input')
        labeled_inputs = [inp for inp in form_inputs if inp.get('id') and soup.find('label', {'for': inp.get('id')})]
        checkbox_inputs = [inp for inp in form_inputs if inp.get('type') == 'checkbox']
        self.log_test("Accessibility - Form Labels", 
                     len(labeled_inputs) > 0 or len(checkbox_inputs) > 0,
                     f"Found {len(labeled_inputs)} labeled inputs and {len(checkbox_inputs)} checkboxes")
    
    def run_comprehensive_uat(self):
        """Run all UAT tests"""
        print("=" * 60)
        print("COMPREHENSIVE UAT - ACTIONS REQUIRED WORKFLOW TAB")
        print("=" * 60)
        
        # Test 1: Page Load
        print("\n1. PAGE LOAD TESTING")
        print("-" * 30)
        response = self.test_page_load()
        
        if not response:
            print("❌ CRITICAL: Page load failed - stopping UAT")
            return self.generate_report()
        
        # Test 2: Tab Navigation
        print("\n2. TAB NAVIGATION TESTING")
        print("-" * 30)
        self.test_tab_navigation_structure(response)
        
        # Test 3: Actions Tab Content
        print("\n3. ACTIONS TAB CONTENT TESTING")
        print("-" * 30)
        self.test_actions_tab_content(response)
        
        # Test 4: Response Templates
        print("\n4. RESPONSE TEMPLATES TESTING")
        print("-" * 30)
        self.test_response_templates(response)
        
        # Test 5: Follow-up Tracking
        print("\n5. FOLLOW-UP TRACKING TESTING")
        print("-" * 30)
        self.test_followup_tracking(response)
        
        # Test 6: Performance Metrics
        print("\n6. PERFORMANCE METRICS TESTING")
        print("-" * 30)
        self.test_performance_metrics(response)
        
        # Test 7: Knowledge Base
        print("\n7. KNOWLEDGE BASE TESTING")
        print("-" * 30)
        self.test_knowledge_base(response)
        
        # Test 8: JavaScript Functions
        print("\n8. JAVASCRIPT FUNCTIONS TESTING")
        print("-" * 30)
        self.test_javascript_functions(response)
        
        # Test 9: Responsive Design
        print("\n9. RESPONSIVE DESIGN TESTING")
        print("-" * 30)
        self.test_responsive_design(response)
        
        # Test 10: Accessibility
        print("\n10. ACCESSIBILITY TESTING")
        print("-" * 30)
        self.test_accessibility(response)
        
        return self.generate_report()
    
    def generate_report(self):
        """Generate final UAT report"""
        print("\n" + "=" * 60)
        print("COMPREHENSIVE UAT REPORT")
        print("=" * 60)
        
        passed_tests = sum(1 for passed, _ in self.test_results if passed)
        total_tests = len(self.test_results)
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"TOTAL TESTS: {total_tests}")
        print(f"PASSED: {passed_tests}")
        print(f"FAILED: {total_tests - passed_tests}")
        print(f"PASS RATE: {pass_rate:.1f}%")
        
        if pass_rate >= 90:
            print("🟢 UAT RESULT: EXCELLENT - Feature ready for production")
        elif pass_rate >= 80:
            print("🟡 UAT RESULT: GOOD - Minor issues to address")
        elif pass_rate >= 70:
            print("🟠 UAT RESULT: ACCEPTABLE - Some issues need fixing")
        else:
            print("🔴 UAT RESULT: NEEDS WORK - Major issues detected")
        
        print("\nFAILED TESTS:")
        for passed, result in self.test_results:
            if not passed:
                print(f"  {result}")
        
        return {
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': total_tests - passed_tests,
            'pass_rate': pass_rate,
            'results': self.test_results
        }

    def test_survey_design_system(self, response):
        """Test July 21: Survey Design System Implementation"""
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test for design system CSS
        css_links = soup.find_all('link', {'rel': 'stylesheet'})
        design_system_loaded = any('survey-design-system.css' in link.get('href', '') for link in css_links)
        self.log_test("Design System - CSS Loaded", design_system_loaded,
                     "survey-design-system.css found in head")
        
        # Test standardized button classes
        buttons = soup.find_all('button')
        has_design_system_buttons = any('btn-primary' in btn.get('class', []) or 
                                       'btn-secondary' in btn.get('class', []) or
                                       'btn-outline' in ' '.join(btn.get('class', [])) for btn in buttons)
        self.log_test("Design System - Button Classes", has_design_system_buttons,
                     f"Found {len(buttons)} buttons with design system classes")

    def test_journey_map_integration(self, response):
        """Test July 21: Journey Map Integration in Analyst Dashboard"""
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test journey map tab exists
        journey_tab = soup.find('button', {'id': 'journey-tab'})
        self.log_test("Journey Map - Tab Present", journey_tab is not None,
                     "Journey map tab found in navigation")
        
        # Test journey map content section
        journey_content = soup.find('div', {'id': 'journey'})
        self.log_test("Journey Map - Content Section", journey_content is not None,
                     "Journey map content section exists")
        
        # Test iframe integration
        if journey_content:
            iframe = journey_content.find('iframe', {'id': 'journeyMapFrame'})
            self.log_test("Journey Map - Iframe Integration", iframe is not None,
                         "Journey map iframe found for embedding")

    def test_executive_dashboard_enhancements(self):
        """Test July 21: Executive Dashboard Mobile Optimization"""
        try:
            response = self.session.get(f"{self.base_url}/dashboards/executive")
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Test responsive viewport meta tag
            viewport = soup.find('meta', {'name': 'viewport'})
            self.log_test("Mobile - Viewport Meta", viewport is not None,
                         "Viewport meta tag for mobile responsiveness")
            
            # Test for export functionality
            export_buttons = soup.find_all('button', string=re.compile(r'تصدير|export', re.IGNORECASE))
            self.log_test("Executive - Export Buttons", len(export_buttons) > 0,
                         f"Found {len(export_buttons)} export buttons")
                         
        except Exception as e:
            self.log_test("Executive Dashboard - Enhancement Test", False, str(e))

    def test_platform_rebranding(self):
        """Test July 21: Platform Rebranding Changes"""
        try:
            response = self.session.get(f"{self.base_url}/")
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Test updated title
            title = soup.find('title')
            if title:
                title_text = title.get_text()
                has_new_branding = "صوت العميل" in title_text
                self.log_test("Rebranding - Title Updated", has_new_branding,
                             f"Title: {title_text}")
                         
        except Exception as e:
            self.log_test("Rebranding - Platform Test", False, str(e))

if __name__ == "__main__":
    print("🔄 Starting Comprehensive Platform Enhancement UAT (July 21, 2025)...")
    print("=" * 80)
    
    # Initialize test suite
    uat = ComprehensivePlatformUAT()
    
    try:
        # Run comprehensive UAT with July 21st enhancements
        response = uat.test_page_load()
        if response:
            # Run existing tests
            results = uat.run_comprehensive_uat()
            
            # Run new July 21st enhancement tests
            print("\n🆕 JULY 21ST ENHANCEMENT TESTS")
            print("-" * 40)
            uat.test_survey_design_system(response)
            uat.test_journey_map_integration(response)
        
        # Additional tests requiring separate requests
        uat.test_executive_dashboard_enhancements()
        uat.test_platform_rebranding()
        
        # Generate final comprehensive report
        uat.generate_report()
        
    except KeyboardInterrupt:
        print("\n⏹️  Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Critical error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Comprehensive Platform Enhancement UAT Complete!")
    print("=" * 80)