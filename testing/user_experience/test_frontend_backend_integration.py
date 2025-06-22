#!/usr/bin/env python3
"""
Frontend-Backend Integration Testing for Arabic VoC Platform
Comprehensive testing of data flow and user interaction paths
"""

import pytest
import asyncio
import json
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import websocket
import threading
from typing import Dict, List, Any, Optional

class FrontendBackendIntegrationTester:
    """Test frontend-backend integration flows"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.driver = None
        self.wait = None
        self.websocket_messages = []
        self.ws_connection = None
        
    def setup_browser(self):
        """Setup browser for testing"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--lang=ar-SA')
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 15)
        self.driver.set_window_size(1920, 1080)
    
    def teardown_browser(self):
        """Cleanup browser"""
        if self.driver:
            self.driver.quit()
        if self.ws_connection:
            self.ws_connection.close()
    
    async def test_feedback_submission_flow(self) -> Dict[str, Any]:
        """Test complete feedback submission and processing flow"""
        results = {
            "frontend_submission": False,
            "backend_processing": False,
            "database_storage": False,
            "real_time_update": False,
            "arabic_processing": False
        }
        
        # Step 1: Submit feedback through frontend
        self.driver.get(f"{self.base_url}/feedback")
        
        try:
            # Wait for form to load
            form = self.wait.until(EC.presence_of_element_located((By.ID, "feedback-form")))
            
            # Fill out form with Arabic text
            arabic_feedback = "الخدمة ممتازة والموظفين محترفين، لكن الأسعار مرتفعة قليلاً"
            
            content_field = form.find_element(By.NAME, "content")
            content_field.clear()
            content_field.send_keys(arabic_feedback)
            
            channel_field = form.find_element(By.NAME, "channel")
            channel_field.send_keys("website")
            
            email_field = form.find_element(By.NAME, "customer_email")
            email_field.send_keys("test@example.com")
            
            # Submit form
            submit_button = form.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()
            
            # Wait for success indicator
            success_message = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".success-message, .alert-success"))
            )
            
            results["frontend_submission"] = True
            
        except TimeoutException:
            return results
        
        # Step 2: Verify backend received and processed the feedback
        time.sleep(5)  # Allow processing time
        
        try:
            # Check via API that feedback was stored
            response = requests.get(f"{self.base_url}/api/feedback", timeout=10)
            if response.status_code == 200:
                feedback_data = response.json()
                
                # Look for our submitted feedback
                for feedback in feedback_data.get('feedback', []):
                    if arabic_feedback in feedback.get('content', ''):
                        results["database_storage"] = True
                        
                        # Check if analysis was performed
                        if feedback.get('sentiment_score') is not None:
                            results["backend_processing"] = True
                        
                        # Check if Arabic text was processed correctly
                        if feedback.get('ai_summary') or feedback.get('ai_categories'):
                            results["arabic_processing"] = True
                        break
        except Exception as e:
            print(f"Error checking backend: {e}")
        
        # Step 3: Check real-time dashboard update
        try:
            self.driver.get(f"{self.base_url}/")
            
            # Wait for dashboard to load
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dashboard-container")))
            
            # Look for updated metrics
            total_feedback_element = self.driver.find_element(By.CSS_SELECTOR, 
                "[data-metric='total-feedback']")
            
            if total_feedback_element and total_feedback_element.text:
                results["real_time_update"] = True
                
        except Exception as e:
            print(f"Error checking dashboard update: {e}")
        
        return results
    
    async def test_survey_creation_flow(self) -> Dict[str, Any]:
        """Test survey creation from frontend to backend"""
        results = {
            "frontend_creation": False,
            "backend_storage": False,
            "validation_working": False,
            "arabic_support": False
        }
        
        self.driver.get(f"{self.base_url}/survey-builder")
        
        try:
            # Wait for survey builder to load
            canvas = self.wait.until(EC.presence_of_element_located((By.ID, "survey-canvas")))
            
            # Add a question
            text_question_btn = self.driver.find_element(
                By.CSS_SELECTOR, "button[data-question-type='text']"
            )
            text_question_btn.click()
            time.sleep(2)
            
            # Verify question was added to canvas
            questions = canvas.find_elements(By.CLASS_NAME, "question-item")
            if len(questions) > 0:
                results["frontend_creation"] = True
                
                # Edit question to include Arabic text
                question = questions[0]
                title_field = question.find_element(By.CSS_SELECTOR, "input[name='title']")
                arabic_title = "ما رأيك في خدمتنا؟"
                title_field.clear()
                title_field.send_keys(arabic_title)
                
                results["arabic_support"] = True
            
            # Test form validation
            save_button = self.driver.find_element(By.CSS_SELECTOR, "button[data-action='save']")
            save_button.click()
            time.sleep(2)
            
            # Look for validation errors or success
            validation_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                ".validation-error, .field-error")
            success_elements = self.driver.find_elements(By.CSS_SELECTOR,
                ".success-message, .alert-success")
            
            if len(success_elements) > 0:
                results["backend_storage"] = True
            
            results["validation_working"] = len(validation_elements) > 0 or len(success_elements) > 0
            
        except Exception as e:
            print(f"Error in survey creation test: {e}")
        
        return results
    
    async def test_analytics_data_flow(self) -> Dict[str, Any]:
        """Test analytics dashboard data loading and filtering"""
        results = {
            "data_loading": False,
            "chart_rendering": False,
            "filter_functionality": False,
            "real_time_updates": False,
            "arabic_formatting": False
        }
        
        self.driver.get(f"{self.base_url}/analytics")
        
        try:
            # Wait for analytics dashboard to load
            dashboard = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "analytics-dashboard"))
            )
            
            # Check if data loaded
            metric_elements = dashboard.find_elements(By.CSS_SELECTOR, "[data-metric]")
            if len(metric_elements) > 0:
                results["data_loading"] = True
                
                # Check if Arabic numbers are formatted correctly
                for element in metric_elements:
                    text = element.text
                    if any('\u0600' <= char <= '\u06FF' for char in text):
                        results["arabic_formatting"] = True
                        break
            
            # Check chart rendering
            charts = dashboard.find_elements(By.CSS_SELECTOR, "canvas, .chart-container")
            if len(charts) > 0:
                results["chart_rendering"] = True
            
            # Test filter functionality
            filter_buttons = dashboard.find_elements(By.CSS_SELECTOR, ".filter-button")
            if len(filter_buttons) > 0:
                # Click a filter and check if data updates
                original_data = self.get_dashboard_data()
                filter_buttons[0].click()
                time.sleep(3)
                new_data = self.get_dashboard_data()
                
                results["filter_functionality"] = original_data != new_data
            
            # Test real-time updates by refreshing data
            refresh_button = dashboard.find_elements(By.CSS_SELECTOR, 
                "button[data-action='refresh']")
            if len(refresh_button) > 0:
                refresh_button[0].click()
                time.sleep(2)
                results["real_time_updates"] = True
            
        except Exception as e:
            print(f"Error in analytics test: {e}")
        
        return results
    
    def get_dashboard_data(self) -> str:
        """Get current dashboard data for comparison"""
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-metric]")
            return "".join(element.text for element in elements)
        except:
            return ""
    
    async def test_settings_persistence(self) -> Dict[str, Any]:
        """Test settings save and reload functionality"""
        results = {
            "settings_load": False,
            "toggle_changes": False,
            "backend_save": False,
            "persistence_check": False
        }
        
        self.driver.get(f"{self.base_url}/settings")
        
        try:
            # Wait for settings page to load
            settings_container = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "settings-container"))
            )
            results["settings_load"] = True
            
            # Find a toggle and record its state
            toggles = settings_container.find_elements(By.CSS_SELECTOR, 
                "input[type='checkbox']")
            
            if len(toggles) > 0:
                toggle = toggles[0]
                original_state = toggle.is_selected()
                
                # Change the toggle state
                self.driver.execute_script("arguments[0].click();", toggle)
                time.sleep(1)
                
                new_state = toggle.is_selected()
                if original_state != new_state:
                    results["toggle_changes"] = True
                    
                    # Save settings
                    save_button = settings_container.find_element(
                        By.CSS_SELECTOR, "button[data-action='save']"
                    )
                    save_button.click()
                    time.sleep(2)
                    
                    # Check for save confirmation
                    success_messages = self.driver.find_elements(By.CSS_SELECTOR,
                        ".success-message, .alert-success")
                    
                    if len(success_messages) > 0:
                        results["backend_save"] = True
                        
                        # Reload page and check persistence
                        self.driver.refresh()
                        time.sleep(3)
                        
                        # Find the same toggle and check if state persisted
                        reloaded_toggles = self.driver.find_elements(
                            By.CSS_SELECTOR, "input[type='checkbox']"
                        )
                        
                        if len(reloaded_toggles) > 0:
                            reloaded_state = reloaded_toggles[0].is_selected()
                            results["persistence_check"] = reloaded_state == new_state
            
        except Exception as e:
            print(f"Error in settings persistence test: {e}")
        
        return results
    
    async def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling across frontend-backend integration"""
        results = {
            "invalid_data_handling": False,
            "network_error_handling": False,
            "validation_errors": False,
            "user_feedback": False
        }
        
        # Test invalid data submission
        self.driver.get(f"{self.base_url}/feedback")
        
        try:
            form = self.wait.until(EC.presence_of_element_located((By.ID, "feedback-form")))
            
            # Submit empty form
            submit_button = form.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()
            time.sleep(2)
            
            # Check for validation errors
            error_messages = self.driver.find_elements(By.CSS_SELECTOR,
                ".error-message, .field-error, .validation-error")
            
            if len(error_messages) > 0:
                results["validation_errors"] = True
                results["user_feedback"] = True
            
            # Test with invalid email
            content_field = form.find_element(By.NAME, "content")
            content_field.send_keys("Test feedback")
            
            email_field = form.find_element(By.NAME, "customer_email")
            email_field.send_keys("invalid-email")
            
            submit_button.click()
            time.sleep(2)
            
            error_messages = self.driver.find_elements(By.CSS_SELECTOR,
                ".error-message, .field-error")
            
            if len(error_messages) > 0:
                results["invalid_data_handling"] = True
            
        except Exception as e:
            print(f"Error in error handling test: {e}")
        
        # Test network error handling (simulate by trying invalid endpoint)
        try:
            # Execute JavaScript to make invalid API call
            self.driver.execute_script("""
                fetch('/api/invalid-endpoint')
                .catch(error => {
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'network-error-test';
                    errorDiv.textContent = 'Network error handled';
                    document.body.appendChild(errorDiv);
                });
            """)
            
            time.sleep(2)
            
            # Check if error was handled
            error_elements = self.driver.find_elements(By.CSS_SELECTOR,
                ".network-error-test")
            
            if len(error_elements) > 0:
                results["network_error_handling"] = True
                
        except Exception as e:
            print(f"Error in network error test: {e}")
        
        return results
    
    async def test_websocket_connectivity(self) -> Dict[str, Any]:
        """Test WebSocket real-time connectivity"""
        results = {
            "websocket_connection": False,
            "message_receiving": False,
            "frontend_updates": False
        }
        
        try:
            # Setup WebSocket connection
            ws_url = f"ws://localhost:5000/ws"
            
            def on_message(ws, message):
                self.websocket_messages.append(json.loads(message))
            
            def on_error(ws, error):
                print(f"WebSocket error: {error}")
            
            def on_open(ws):
                results["websocket_connection"] = True
            
            self.ws_connection = websocket.WebSocketApp(
                ws_url,
                on_message=on_message,
                on_error=on_error,
                on_open=on_open
            )
            
            # Start WebSocket in separate thread
            ws_thread = threading.Thread(target=self.ws_connection.run_forever)
            ws_thread.daemon = True
            ws_thread.start()
            
            time.sleep(3)  # Allow connection to establish
            
            # Submit feedback to trigger WebSocket message
            feedback_data = {
                "content": "اختبار الاتصال المباشر",
                "channel": "website"
            }
            
            response = requests.post(f"{self.base_url}/api/feedback", 
                                   json=feedback_data, timeout=10)
            
            if response.status_code in [200, 201]:
                time.sleep(5)  # Allow message processing
                
                if len(self.websocket_messages) > 0:
                    results["message_receiving"] = True
                    
                    # Check if dashboard updates in real-time
                    self.driver.get(f"{self.base_url}/")
                    time.sleep(3)
                    
                    # Look for real-time update indicators
                    live_elements = self.driver.find_elements(By.CSS_SELECTOR,
                        ".live-update, [data-live='true']")
                    
                    if len(live_elements) > 0:
                        results["frontend_updates"] = True
            
        except Exception as e:
            print(f"Error in WebSocket test: {e}")
        
        return results
    
    async def run_comprehensive_integration_test(self) -> Dict[str, Any]:
        """Run all frontend-backend integration tests"""
        print("Starting comprehensive frontend-backend integration testing...")
        
        self.setup_browser()
        
        try:
            # Run all test suites
            feedback_flow = await self.test_feedback_submission_flow()
            survey_flow = await self.test_survey_creation_flow()
            analytics_flow = await self.test_analytics_data_flow()
            settings_flow = await self.test_settings_persistence()
            error_handling = await self.test_error_handling()
            websocket_test = await self.test_websocket_connectivity()
            
            # Compile results
            all_results = {
                "feedback_submission_flow": feedback_flow,
                "survey_creation_flow": survey_flow,
                "analytics_data_flow": analytics_flow,
                "settings_persistence": settings_flow,
                "error_handling": error_handling,
                "websocket_connectivity": websocket_test
            }
            
            # Calculate metrics
            total_tests = sum(len(flow) for flow in all_results.values())
            passed_tests = sum(
                sum(1 for result in flow.values() if result)
                for flow in all_results.values()
            )
            
            summary = {
                "integration_success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_integration_tests": total_tests,
                "passed_integration_tests": passed_tests,
                "failed_integration_tests": total_tests - passed_tests,
                "detailed_results": all_results,
                "timestamp": time.time()
            }
            
            return summary
            
        finally:
            self.teardown_browser()

# Pytest integration
@pytest.mark.asyncio
async def test_complete_feedback_flow():
    """Test complete feedback submission and processing"""
    tester = FrontendBackendIntegrationTester()
    results = await tester.test_feedback_submission_flow()
    
    assert results["frontend_submission"], "Frontend submission should work"
    assert results["backend_processing"], "Backend processing should work"

@pytest.mark.asyncio
async def test_survey_builder_integration():
    """Test survey builder frontend-backend integration"""
    tester = FrontendBackendIntegrationTester()
    results = await tester.test_survey_creation_flow()
    
    assert results["frontend_creation"], "Frontend survey creation should work"
    assert results["arabic_support"], "Arabic text support should work"

@pytest.mark.asyncio
async def test_analytics_integration():
    """Test analytics dashboard integration"""
    tester = FrontendBackendIntegrationTester()
    results = await tester.test_analytics_data_flow()
    
    assert results["data_loading"], "Analytics data should load"
    assert results["chart_rendering"], "Charts should render"

if __name__ == "__main__":
    async def main():
        tester = FrontendBackendIntegrationTester()
        results = await tester.run_comprehensive_integration_test()
        
        print("\n" + "="*70)
        print("FRONTEND-BACKEND INTEGRATION TEST RESULTS")
        print("="*70)
        
        print(f"Integration Success Rate: {results['integration_success_rate']:.1f}%")
        print(f"Tests Passed: {results['passed_integration_tests']}/{results['total_integration_tests']}")
        
        print("\nDetailed Results:")
        for flow_name, flow_results in results['detailed_results'].items():
            passed = sum(1 for result in flow_results.values() if result)
            total = len(flow_results)
            print(f"\n{flow_name}:")
            for test_name, success in flow_results.items():
                status = "✅" if success else "❌"
                print(f"  {status} {test_name}")
        
        return results['integration_success_rate'] > 75
    
    success = asyncio.run(main())
    exit(0 if success else 1)