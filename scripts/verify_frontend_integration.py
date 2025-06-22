#!/usr/bin/env python3
"""
Frontend Integration Verification Script
Automatically checks if CSS and JS changes are properly integrated
"""

import requests
import re
import sys
import time
from urllib.parse import urljoin

class FrontendVerifier:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.results = []
        
    def log_result(self, test_name, passed, details=""):
        status = "✓ PASS" if passed else "✗ FAIL"
        self.results.append({
            'test': test_name,
            'passed': passed,
            'details': details
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   {details}")
    
    def test_server_response(self):
        """Test if server is responding"""
        try:
            response = requests.get(self.base_url, timeout=5)
            self.log_result("Server Response", response.status_code == 200, 
                          f"Status: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            self.log_result("Server Response", False, f"Error: {str(e)}")
            return False
    
    def test_survey_builder_page(self):
        """Test survey builder page loads"""
        try:
            url = urljoin(self.base_url, '/survey-builder')
            response = requests.get(url, timeout=10)
            content = response.text
            
            # Check for key elements
            has_builder_container = 'builder-container' in content
            has_question_types = 'question-types-grid' in content
            has_canvas = 'main-canvas' in content
            
            self.log_result("Survey Builder Page", response.status_code == 200 and has_builder_container,
                          f"Container: {has_builder_container}, Types: {has_question_types}, Canvas: {has_canvas}")
            
            return response.status_code == 200 and has_builder_container
            
        except Exception as e:
            self.log_result("Survey Builder Page", False, f"Error: {str(e)}")
            return False
    
    def test_css_integration(self):
        """Test if CSS changes are properly integrated"""
        try:
            url = urljoin(self.base_url, '/survey-builder')
            response = requests.get(url, timeout=10)
            content = response.text
            
            # Check for specific CSS rules we implemented
            css_checks = {
                'Grid Layout': 'grid-template-columns: 280px 1fr 320px',
                'Canvas Padding': 'padding: 25px 35px',
                'Question Type Grid': 'question-types-grid',
                'Empty State Icon': 'empty-state-icon',
                'Canvas Header': 'canvas-header'
            }
            
            results = {}
            for check_name, css_rule in css_checks.items():
                found = css_rule in content
                results[check_name] = found
                self.log_result(f"CSS: {check_name}", found)
            
            total_passed = sum(results.values())
            total_tests = len(results)
            
            overall_pass = total_passed >= (total_tests * 0.8)  # 80% pass rate
            self.log_result("CSS Integration Overall", overall_pass, 
                          f"{total_passed}/{total_tests} checks passed")
            
            return overall_pass
            
        except Exception as e:
            self.log_result("CSS Integration", False, f"Error: {str(e)}")
            return False
    
    def test_javascript_integration(self):
        """Test if JavaScript is loading and working"""
        try:
            url = urljoin(self.base_url, '/static/js/survey_builder.js')
            response = requests.get(url, timeout=5)
            
            if response.status_code != 200:
                self.log_result("JavaScript File", False, f"Status: {response.status_code}")
                return False
            
            content = response.text
            
            # Check for key JavaScript functions
            js_checks = {
                'SurveyBuilder Class': 'class SurveyBuilder',
                'Drag and Drop Setup': 'setupDragAndDrop',
                'Question Rendering': 'renderQuestion',
                'Arabic Support': 'text_ar'
            }
            
            results = {}
            for check_name, js_pattern in js_checks.items():
                found = js_pattern in content
                results[check_name] = found
                self.log_result(f"JS: {check_name}", found)
            
            total_passed = sum(results.values())
            total_tests = len(results)
            
            overall_pass = total_passed == total_tests
            self.log_result("JavaScript Integration Overall", overall_pass,
                          f"{total_passed}/{total_tests} checks passed")
            
            return overall_pass
            
        except Exception as e:
            self.log_result("JavaScript Integration", False, f"Error: {str(e)}")
            return False
    
    def test_drag_drop_elements(self):
        """Test if drag and drop elements are present"""
        try:
            url = urljoin(self.base_url, '/survey-builder')
            response = requests.get(url, timeout=10)
            content = response.text
            
            # Check for drag and drop related elements
            elements = {
                'Question Types Container': 'id="questionTypes"',
                'Questions Area': 'id="questionsArea"',
                'SortableJS Library': 'sortablejs',
                'Drag Handle': 'drag-handle',
                'Question Type Items': 'data-type='
            }
            
            results = {}
            for element_name, element_pattern in elements.items():
                found = element_pattern in content
                results[element_name] = found
                self.log_result(f"Element: {element_name}", found)
            
            total_passed = sum(results.values())
            total_tests = len(results)
            
            overall_pass = total_passed >= (total_tests * 0.8)
            self.log_result("Drag Drop Elements Overall", overall_pass,
                          f"{total_passed}/{total_tests} elements found")
            
            return overall_pass
            
        except Exception as e:
            self.log_result("Drag Drop Elements", False, f"Error: {str(e)}")
            return False
    
    def test_responsive_design(self):
        """Test if responsive design CSS is present"""
        try:
            url = urljoin(self.base_url, '/survey-builder')
            response = requests.get(url, timeout=10)
            content = response.text
            
            responsive_checks = {
                'Mobile Breakpoint': '@media (max-width: 992px)',
                'Tablet Breakpoint': '@media (max-width: 1200px)',
                'Grid Reflow': 'grid-template-rows: auto 1fr auto'
            }
            
            results = {}
            for check_name, pattern in responsive_checks.items():
                found = pattern in content
                results[check_name] = found
                self.log_result(f"Responsive: {check_name}", found)
            
            total_passed = sum(results.values())
            overall_pass = total_passed >= 2  # At least 2 responsive features
            
            self.log_result("Responsive Design Overall", overall_pass,
                          f"{total_passed}/{len(results)} responsive features found")
            
            return overall_pass
            
        except Exception as e:
            self.log_result("Responsive Design", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("=" * 60)
        print("Frontend Integration Verification")
        print("=" * 60)
        
        tests = [
            self.test_server_response,
            self.test_survey_builder_page,
            self.test_css_integration,
            self.test_javascript_integration,
            self.test_drag_drop_elements,
            self.test_responsive_design
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            print("-" * 40)
            if test():
                passed_tests += 1
            time.sleep(0.5)  # Brief pause between tests
        
        print("=" * 60)
        print(f"SUMMARY: {passed_tests}/{total_tests} test categories passed")
        
        # Detailed results
        print("\nDetailed Results:")
        for result in self.results:
            status = "✓" if result['passed'] else "✗"
            print(f"{status} {result['test']}")
            if result['details']:
                print(f"    {result['details']}")
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"\nOverall Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("✅ INTEGRATION VERIFICATION PASSED")
            return True
        else:
            print("❌ INTEGRATION VERIFICATION FAILED")
            return False

def main():
    verifier = FrontendVerifier()
    success = verifier.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()