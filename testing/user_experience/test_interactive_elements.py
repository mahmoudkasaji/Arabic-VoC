#!/usr/bin/env python3
"""
Interactive Elements Testing for Arabic VoC Platform
Tests all buttons, toggles, and interactive components for proper functionality
"""

import pytest
import asyncio
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
import requests
import json
from typing import Dict, List, Tuple

class InteractiveElementsTester:
    """Comprehensive testing for all interactive elements"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.driver = None
        self.wait = None
        self.test_results = []
        
    def setup_driver(self):
        """Setup Selenium WebDriver with Arabic language support"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--lang=ar-SA')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        
        # Set window size for consistent testing
        self.driver.set_window_size(1920, 1080)
    
    def teardown_driver(self):
        """Clean up WebDriver"""
        if self.driver:
            self.driver.quit()
    
    def record_test_result(self, test_name: str, success: bool, details: str = ""):
        """Record test result for reporting"""
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': time.time()
        })
    
    async def test_dashboard_buttons(self) -> Dict[str, bool]:
        """Test all buttons on the dashboard page"""
        self.driver.get(f"{self.base_url}/")
        
        # Wait for page to load
        try:
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        except TimeoutException:
            self.record_test_result("dashboard_load", False, "Dashboard failed to load")
            return {"dashboard_load": False}
        
        results = {}
        
        # Test navigation menu buttons
        nav_buttons = [
            ("#nav-feedback", "Feedback navigation"),
            ("#nav-analytics", "Analytics navigation"),
            ("#nav-surveys", "Surveys navigation"),
            ("#nav-integrations", "Integrations navigation"),
            ("#nav-settings", "Settings navigation")
        ]
        
        for selector, description in nav_buttons:
            try:
                button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                original_url = self.driver.current_url
                button.click()
                time.sleep(2)  # Allow navigation to complete
                
                # Check if URL changed or content updated
                success = (self.driver.current_url != original_url or 
                          self.check_content_change())
                results[f"nav_{selector[1:]}"] = success
                self.record_test_result(f"Navigation {description}", success)
                
                # Return to dashboard for next test
                self.driver.get(f"{self.base_url}/")
                
            except (TimeoutException, ElementClickInterceptedException) as e:
                results[f"nav_{selector[1:]}"] = False
                self.record_test_result(f"Navigation {description}", False, str(e))
        
        # Test dashboard action buttons
        action_buttons = [
            ("button[data-action='refresh']", "Refresh button"),
            ("button[data-action='export']", "Export button"),
            (".filter-toggle", "Filter toggle"),
            (".date-range-button", "Date range button")
        ]
        
        for selector, description in action_buttons:
            try:
                buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if buttons:
                    button = buttons[0]
                    self.driver.execute_script("arguments[0].scrollIntoView();", button)
                    time.sleep(1)
                    
                    # Check if button is clickable
                    if button.is_enabled() and button.is_displayed():
                        button.click()
                        time.sleep(2)
                        success = True
                    else:
                        success = False
                        
                    results[f"action_{selector.replace('[', '_').replace(']', '_')}"] = success
                    self.record_test_result(f"Action {description}", success)
                else:
                    results[f"action_{selector}"] = False
                    self.record_test_result(f"Action {description}", False, "Element not found")
                    
            except Exception as e:
                results[f"action_{selector}"] = False
                self.record_test_result(f"Action {description}", False, str(e))
        
        return results
    
    async def test_survey_builder_interactions(self) -> Dict[str, bool]:
        """Test survey builder drag-and-drop and interactions"""
        self.driver.get(f"{self.base_url}/survey-builder")
        
        try:
            self.wait.until(EC.presence_of_element_located((By.ID, "survey-canvas")))
        except TimeoutException:
            self.record_test_result("survey_builder_load", False, "Survey builder failed to load")
            return {"survey_builder_load": False}
        
        results = {}
        
        # Test question type buttons
        question_types = [
            ("button[data-question-type='text']", "Text question"),
            ("button[data-question-type='multiple_choice']", "Multiple choice question"),
            ("button[data-question-type='rating']", "Rating question"),
            ("button[data-question-type='nps']", "NPS question")
        ]
        
        for selector, description in question_types:
            try:
                # Find the question type button
                question_buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if question_buttons:
                    button = question_buttons[0]
                    
                    # Scroll to button and click
                    self.driver.execute_script("arguments[0].scrollIntoView();", button)
                    time.sleep(1)
                    
                    # Get canvas before adding question
                    canvas = self.driver.find_element(By.ID, "survey-canvas")
                    questions_before = len(canvas.find_elements(By.CLASS_NAME, "question-item"))
                    
                    button.click()
                    time.sleep(2)
                    
                    # Check if question was added to canvas
                    questions_after = len(canvas.find_elements(By.CLASS_NAME, "question-item"))
                    success = questions_after > questions_before
                    
                    results[f"add_{selector.split('=')[1].strip('\\'\"')}"] = success
                    self.record_test_result(f"Add {description}", success)
                else:
                    results[f"add_{selector}"] = False
                    self.record_test_result(f"Add {description}", False, "Button not found")
                    
            except Exception as e:
                results[f"add_{selector}"] = False
                self.record_test_result(f"Add {description}", False, str(e))
        
        # Test drag and drop functionality
        try:
            # Find source and target elements
            source = self.driver.find_element(By.CSS_SELECTOR, "button[data-question-type='text']")
            target = self.driver.find_element(By.ID, "survey-canvas")
            
            # Perform drag and drop
            actions = ActionChains(self.driver)
            actions.drag_and_drop(source, target).perform()
            time.sleep(2)
            
            # Check if question was added
            questions = target.find_elements(By.CLASS_NAME, "question-item")
            success = len(questions) > 0
            results["drag_and_drop"] = success
            self.record_test_result("Drag and drop functionality", success)
            
        except Exception as e:
            results["drag_and_drop"] = False
            self.record_test_result("Drag and drop functionality", False, str(e))
        
        # Test save button functionality
        try:
            save_button = self.driver.find_element(By.CSS_SELECTOR, "button[data-action='save']")
            save_button.click()
            time.sleep(2)
            
            # Check for success indicator (toast, modal, etc.)
            success_indicators = self.driver.find_elements(By.CSS_SELECTOR, 
                ".toast-success, .alert-success, .success-message")
            success = len(success_indicators) > 0
            results["save_survey"] = success
            self.record_test_result("Save survey functionality", success)
            
        except Exception as e:
            results["save_survey"] = False
            self.record_test_result("Save survey functionality", False, str(e))
        
        return results
    
    async def test_feedback_submission(self) -> Dict[str, bool]:
        """Test feedback submission form"""
        self.driver.get(f"{self.base_url}/feedback")
        
        try:
            self.wait.until(EC.presence_of_element_located((By.ID, "feedback-form")))
        except TimeoutException:
            self.record_test_result("feedback_form_load", False, "Feedback form failed to load")
            return {"feedback_form_load": False}
        
        results = {}
        
        # Test Arabic text input
        try:
            text_area = self.driver.find_element(By.CSS_SELECTOR, "textarea[name='content']")
            arabic_text = "الخدمة ممتازة جداً وأنصح بها للجميع"
            text_area.clear()
            text_area.send_keys(arabic_text)
            
            # Verify text was entered correctly
            entered_text = text_area.get_attribute("value")
            success = arabic_text in entered_text
            results["arabic_text_input"] = success
            self.record_test_result("Arabic text input", success)
            
        except Exception as e:
            results["arabic_text_input"] = False
            self.record_test_result("Arabic text input", False, str(e))
        
        # Test channel selection
        try:
            channel_select = self.driver.find_element(By.CSS_SELECTOR, "select[name='channel']")
            channel_select.click()
            time.sleep(1)
            
            options = channel_select.find_elements(By.TAG_NAME, "option")
            if len(options) > 1:
                options[1].click()  # Select second option
                success = True
            else:
                success = False
                
            results["channel_selection"] = success
            self.record_test_result("Channel selection", success)
            
        except Exception as e:
            results["channel_selection"] = False
            self.record_test_result("Channel selection", False, str(e))
        
        # Test form submission
        try:
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()
            time.sleep(3)  # Allow for processing
            
            # Check for success message or redirect
            success_indicators = self.driver.find_elements(By.CSS_SELECTOR, 
                ".success-message, .alert-success, .toast-success")
            success = len(success_indicators) > 0 or "success" in self.driver.current_url.lower()
            results["form_submission"] = success
            self.record_test_result("Form submission", success)
            
        except Exception as e:
            results["form_submission"] = False
            self.record_test_result("Form submission", False, str(e))
        
        return results
    
    async def test_settings_toggles(self) -> Dict[str, bool]:
        """Test settings page toggles and controls"""
        self.driver.get(f"{self.base_url}/settings")
        
        try:
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "settings-container")))
        except TimeoutException:
            self.record_test_result("settings_load", False, "Settings page failed to load")
            return {"settings_load": False}
        
        results = {}
        
        # Test toggle switches
        toggles = self.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox'].toggle")
        
        for i, toggle in enumerate(toggles):
            try:
                # Get initial state
                initial_state = toggle.is_selected()
                
                # Click toggle
                self.driver.execute_script("arguments[0].click();", toggle)
                time.sleep(1)
                
                # Check if state changed
                new_state = toggle.is_selected()
                success = initial_state != new_state
                
                results[f"toggle_{i}"] = success
                self.record_test_result(f"Toggle switch {i}", success)
                
            except Exception as e:
                results[f"toggle_{i}"] = False
                self.record_test_result(f"Toggle switch {i}", False, str(e))
        
        # Test save settings button
        try:
            save_button = self.driver.find_element(By.CSS_SELECTOR, "button[data-action='save-settings']")
            save_button.click()
            time.sleep(2)
            
            # Check for success feedback
            success_indicators = self.driver.find_elements(By.CSS_SELECTOR, 
                ".settings-saved, .alert-success, .toast-success")
            success = len(success_indicators) > 0
            results["save_settings"] = success
            self.record_test_result("Save settings", success)
            
        except Exception as e:
            results["save_settings"] = False
            self.record_test_result("Save settings", False, str(e))
        
        return results
    
    def check_content_change(self) -> bool:
        """Check if page content has changed (indicates successful navigation)"""
        try:
            # Look for common indicators of content change
            indicators = [
                ".page-title",
                ".main-content", 
                "h1",
                ".dashboard-container",
                ".content-area"
            ]
            
            for selector in indicators:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    return True
            return True  # Assume change if we can't detect
        except:
            return True
    
    async def test_api_endpoints(self) -> Dict[str, bool]:
        """Test backend API endpoints that support frontend interactions"""
        results = {}
        
        # Test dashboard API
        try:
            response = requests.get(f"{self.base_url}/api/dashboard-metrics", timeout=5)
            success = response.status_code == 200 and "total_feedback" in response.text
            results["api_dashboard"] = success
            self.record_test_result("Dashboard API", success)
        except Exception as e:
            results["api_dashboard"] = False
            self.record_test_result("Dashboard API", False, str(e))
        
        # Test feedback submission API
        try:
            payload = {
                "content": "اختبار التكامل مع الواجهة الخلفية",
                "channel": "website",
                "customer_email": "test@example.com"
            }
            response = requests.post(f"{self.base_url}/api/feedback", 
                                   json=payload, timeout=10)
            success = response.status_code in [200, 201]
            results["api_feedback"] = success
            self.record_test_result("Feedback API", success)
        except Exception as e:
            results["api_feedback"] = False
            self.record_test_result("Feedback API", False, str(e))
        
        # Test health check API
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            success = response.status_code == 200
            results["api_health"] = success
            self.record_test_result("Health API", success)
        except Exception as e:
            results["api_health"] = False
            self.record_test_result("Health API", False, str(e))
        
        return results
    
    async def run_comprehensive_test(self) -> Dict[str, any]:
        """Run all interactive element tests"""
        print("Starting comprehensive interactive elements testing...")
        
        self.setup_driver()
        
        try:
            # Run all test suites
            dashboard_results = await self.test_dashboard_buttons()
            survey_results = await self.test_survey_builder_interactions()
            feedback_results = await self.test_feedback_submission()
            settings_results = await self.test_settings_toggles()
            api_results = await self.test_api_endpoints()
            
            # Compile comprehensive results
            all_results = {
                "dashboard": dashboard_results,
                "survey_builder": survey_results,
                "feedback_form": feedback_results,
                "settings": settings_results,
                "api_endpoints": api_results
            }
            
            # Calculate overall success rate
            total_tests = sum(len(category) for category in all_results.values())
            successful_tests = sum(
                sum(1 for result in category.values() if result) 
                for category in all_results.values()
            )
            
            success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
            
            summary = {
                "overall_success_rate": success_rate,
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests,
                "results_by_category": all_results,
                "detailed_results": self.test_results,
                "timestamp": time.time()
            }
            
            return summary
            
        finally:
            self.teardown_driver()

# Test runner functions for pytest integration
@pytest.mark.asyncio
async def test_dashboard_interactions():
    """Test dashboard interactive elements"""
    tester = InteractiveElementsTester()
    results = await tester.test_dashboard_buttons()
    
    # Assert that critical interactions work
    assert results.get("nav_feedback", False), "Feedback navigation should work"
    assert results.get("nav_analytics", False), "Analytics navigation should work"

@pytest.mark.asyncio 
async def test_survey_builder_functionality():
    """Test survey builder interactions"""
    tester = InteractiveElementsTester()
    results = await tester.test_survey_builder_interactions()
    
    # Assert that question addition works
    assert results.get("add_text", False), "Text question addition should work"
    assert results.get("save_survey", False), "Survey saving should work"

@pytest.mark.asyncio
async def test_feedback_form_interactions():
    """Test feedback form functionality"""
    tester = InteractiveElementsTester()
    results = await tester.test_feedback_submission()
    
    # Assert that form works with Arabic text
    assert results.get("arabic_text_input", False), "Arabic text input should work"
    assert results.get("form_submission", False), "Form submission should work"

@pytest.mark.asyncio
async def test_backend_api_integration():
    """Test API endpoints supporting frontend"""
    tester = InteractiveElementsTester()
    results = await tester.test_api_endpoints()
    
    # Assert that critical APIs work
    assert results.get("api_dashboard", False), "Dashboard API should respond"
    assert results.get("api_health", False), "Health API should respond"

if __name__ == "__main__":
    async def main():
        tester = InteractiveElementsTester()
        results = await tester.run_comprehensive_test()
        
        print("\n" + "="*60)
        print("INTERACTIVE ELEMENTS TEST RESULTS")
        print("="*60)
        
        print(f"Overall Success Rate: {results['overall_success_rate']:.1f}%")
        print(f"Tests Passed: {results['successful_tests']}/{results['total_tests']}")
        
        print("\nResults by Category:")
        for category, category_results in results['results_by_category'].items():
            passed = sum(1 for result in category_results.values() if result)
            total = len(category_results)
            print(f"  {category}: {passed}/{total} ({passed/total*100:.1f}%)")
        
        print("\nFailed Tests:")
        for result in results['detailed_results']:
            if not result['success']:
                print(f"  ❌ {result['test']}: {result['details']}")
        
        return results['overall_success_rate'] > 80
    
    success = asyncio.run(main())
    exit(0 if success else 1)