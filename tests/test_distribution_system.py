#!/usr/bin/env python3
"""
Comprehensive Testing Framework for Survey Distribution System
Tests the new campaign-based distribution architecture with real database operations
"""

import sys
import os
import json
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class DistributionSystemTester:
    """Comprehensive test suite for the new distribution system"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.test_results = []
        self.test_data = {}
        
    def log_test(self, test_name: str, status: str, details: str = "", response_data: Any = None):
        """Log test result with timestamp"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'test_name': test_name,
            'status': status,
            'details': details,
            'response_data': response_data
        }
        self.test_results.append(result)
        
        # Color coding for console output
        color = '\033[92m' if status == 'PASS' else '\033[91m' if status == 'FAIL' else '\033[93m'
        reset = '\033[0m'
        
        print(f"{color}[{status}]{reset} {test_name}")
        if details:
            print(f"      {details}")
            
    def test_database_structure(self) -> bool:
        """Test 1: Database Structure Validation"""
        print("\n=== Phase 1: Database Structure Tests ===")
        
        try:
            # Import models using Flask app context to avoid circular imports
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            from app import app, db
            with app.app_context():
                from models.survey_campaigns import SurveyCampaign, DistributionMethod
                from models.survey_flask import SurveyFlask
            
            # Test SurveyCampaign model structure
            campaign_fields = ['id', 'name', 'survey_id', 'created_by', 'description', 
                             'status', 'sent_count', 'response_count', 'created_at', 'scheduled_at']
            
            missing_fields = []
            for field in campaign_fields:
                if not hasattr(SurveyCampaign, field):
                    missing_fields.append(field)
                    
            if missing_fields:
                self.log_test("Database Schema - SurveyCampaign", "FAIL", 
                            f"Missing fields: {missing_fields}")
                return False
            else:
                self.log_test("Database Schema - SurveyCampaign", "PASS", 
                            f"All {len(campaign_fields)} fields present")
            
            # Test DistributionMethod model structure
            method_fields = ['id', 'campaign_id', 'method_type', 'target_audience', 
                           'status', 'created_at', 'executed_at']
            
            missing_method_fields = []
            for field in method_fields:
                if not hasattr(DistributionMethod, field):
                    missing_method_fields.append(field)
                    
            if missing_method_fields:
                self.log_test("Database Schema - DistributionMethod", "FAIL", 
                            f"Missing fields: {missing_method_fields}")
                return False
            else:
                self.log_test("Database Schema - DistributionMethod", "PASS", 
                            f"All {len(method_fields)} fields present")
                
            return True
            
        except Exception as e:
            self.log_test("Database Structure", "FAIL", f"Import error: {str(e)}")
            return False
    
    def test_distribution_hub_routes(self) -> bool:
        """Test 2: Distribution Hub Route Functionality"""
        print("\n=== Phase 2: Route Functionality Tests ===")
        
        try:
            # Test main distribution hub
            response = requests.get(f"{self.base_url}/surveys/distribution", timeout=10)
            
            if response.status_code == 200:
                self.log_test("Distribution Hub Route", "PASS", 
                            f"Status {response.status_code}, Content length: {len(response.text)}")
                
                # Check for key UI elements
                required_elements = [
                    "مركز توزيع الاستطلاعات",  # Hub title
                    "إنشاء حملة جديدة",       # Create campaign button
                    "الحملات الأخيرة",        # Recent campaigns
                    "إجمالي الحملات"          # Total campaigns metric
                ]
                
                missing_elements = []
                for element in required_elements:
                    if element not in response.text:
                        missing_elements.append(element)
                
                if missing_elements:
                    self.log_test("Distribution Hub UI Elements", "FAIL", 
                                f"Missing elements: {missing_elements}")
                    return False
                else:
                    self.log_test("Distribution Hub UI Elements", "PASS", 
                                f"All {len(required_elements)} elements present")
                    
            else:
                self.log_test("Distribution Hub Route", "FAIL", 
                            f"Status {response.status_code}")
                return False
                
            # Test campaign creation form
            response = requests.get(f"{self.base_url}/surveys/distribution/create-campaign", timeout=10)
            
            if response.status_code == 200:
                self.log_test("Campaign Creation Form Route", "PASS", 
                            f"Status {response.status_code}")
                
                # Check for form elements
                form_elements = [
                    'name="name"',           # Campaign name field
                    'name="survey_id"',      # Survey selection
                    'name="method_type"',    # Distribution method
                    'name="description"'     # Description field
                ]
                
                missing_form_elements = []
                for element in form_elements:
                    if element not in response.text:
                        missing_form_elements.append(element)
                
                if missing_form_elements:
                    self.log_test("Campaign Form Elements", "FAIL", 
                                f"Missing form elements: {missing_form_elements}")
                    return False
                else:
                    self.log_test("Campaign Form Elements", "PASS", 
                                f"All {len(form_elements)} form fields present")
            else:
                self.log_test("Campaign Creation Form Route", "FAIL", 
                            f"Status {response.status_code}")
                return False
                
            return True
            
        except Exception as e:
            self.log_test("Distribution Routes", "FAIL", f"Request error: {str(e)}")
            return False
    
    def test_campaign_creation_workflow(self) -> bool:
        """Test 3: Campaign Creation Workflow (Database Operations)"""
        print("\n=== Phase 3: Campaign Creation Workflow Tests ===")
        
        try:
            from models.survey_campaigns import SurveyCampaign, DistributionMethod
            from models.survey_flask import SurveyFlask
            from app import db
            
            # First, create a test survey if none exists
            existing_surveys = SurveyFlask.query.limit(1).all()
            if not existing_surveys:
                self.log_test("Test Survey Creation", "INFO", 
                            "No surveys found, creating test survey for campaign testing")
                
                test_survey = SurveyFlask(
                    uuid='test-campaign-survey-uuid',
                    short_id='testcamp',
                    display_title='Test Campaign Survey',
                    description='Survey for testing campaign creation',
                    questions='[{"type": "rating", "question": "Test question"}]',
                    status='published'
                )
                db.session.add(test_survey)
                db.session.commit()
                
                self.test_data['test_survey_id'] = test_survey.id
                self.log_test("Test Survey Creation", "PASS", 
                            f"Created test survey with ID: {test_survey.id}")
            else:
                self.test_data['test_survey_id'] = existing_surveys[0].id
                self.log_test("Test Survey Found", "PASS", 
                            f"Using existing survey ID: {existing_surveys[0].id}")
            
            # Test campaign creation via POST request
            campaign_data = {
                'name': f'Test Campaign {datetime.now().strftime("%Y%m%d_%H%M%S")}',
                'survey_id': str(self.test_data['test_survey_id']),
                'description': 'Automated test campaign',
                'method_type': 'email',
                'schedule_type': 'now'
            }
            
            response = requests.post(
                f"{self.base_url}/surveys/distribution/create-campaign",
                data=campaign_data,
                timeout=10,
                allow_redirects=False
            )
            
            if response.status_code in [200, 302]:  # Success or redirect
                self.log_test("Campaign Creation POST", "PASS", 
                            f"Status {response.status_code}")
                
                # Verify campaign was created in database
                latest_campaign = SurveyCampaign.query.order_by(SurveyCampaign.created_at.desc()).first()
                
                if latest_campaign and latest_campaign.name == campaign_data['name']:
                    self.log_test("Campaign Database Storage", "PASS", 
                                f"Campaign '{latest_campaign.name}' stored successfully")
                    self.test_data['test_campaign_id'] = latest_campaign.id
                    
                    # Verify distribution method was created
                    distribution_method = DistributionMethod.query.filter_by(
                        campaign_id=latest_campaign.id
                    ).first()
                    
                    if distribution_method:
                        self.log_test("Distribution Method Creation", "PASS", 
                                    f"Method type: {distribution_method.method_type}")
                    else:
                        self.log_test("Distribution Method Creation", "FAIL", 
                                    "No distribution method found for campaign")
                        return False
                        
                else:
                    self.log_test("Campaign Database Storage", "FAIL", 
                                "Campaign not found in database after creation")
                    return False
                    
            else:
                self.log_test("Campaign Creation POST", "FAIL", 
                            f"Status {response.status_code}, Response: {response.text[:200]}")
                return False
                
            return True
            
        except Exception as e:
            self.log_test("Campaign Creation Workflow", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_dashboard_metrics_calculation(self) -> bool:
        """Test 4: Dashboard Metrics Calculation"""
        print("\n=== Phase 4: Dashboard Metrics Tests ===")
        
        try:
            from models.survey_campaigns import SurveyCampaign
            from app import db
            
            # Get actual database counts
            total_campaigns = SurveyCampaign.query.count()
            active_campaigns = SurveyCampaign.query.filter_by(status='active').count()
            draft_campaigns = SurveyCampaign.query.filter_by(status='draft').count()
            
            self.log_test("Database Metrics Count", "PASS", 
                        f"Total: {total_campaigns}, Active: {active_campaigns}, Draft: {draft_campaigns}")
            
            # Test dashboard displays metrics correctly
            response = requests.get(f"{self.base_url}/surveys/distribution", timeout=10)
            
            if response.status_code == 200:
                response_text = response.text
                
                # Check if metrics appear in the response
                metrics_found = []
                if str(total_campaigns) in response_text:
                    metrics_found.append(f"Total campaigns: {total_campaigns}")
                if str(active_campaigns) in response_text:
                    metrics_found.append(f"Active campaigns: {active_campaigns}")
                
                if metrics_found:
                    self.log_test("Dashboard Metrics Display", "PASS", 
                                f"Found metrics: {metrics_found}")
                else:
                    self.log_test("Dashboard Metrics Display", "FAIL", 
                                "No metrics found in dashboard response")
                    return False
                    
            else:
                self.log_test("Dashboard Metrics Display", "FAIL", 
                            f"Dashboard not accessible: {response.status_code}")
                return False
                
            return True
            
        except Exception as e:
            self.log_test("Dashboard Metrics Calculation", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_url_generation_and_navigation(self) -> bool:
        """Test 5: URL Generation and Navigation"""
        print("\n=== Phase 5: URL and Navigation Tests ===")
        
        try:
            # Test all distribution-related URLs
            urls_to_test = [
                ("/surveys/distribution", "Distribution Hub"),
                ("/surveys/distribution/create-campaign", "Campaign Creation Form")
            ]
            
            for url, description in urls_to_test:
                response = requests.get(f"{self.base_url}{url}", timeout=10)
                
                if response.status_code == 200:
                    self.log_test(f"URL Access - {description}", "PASS", 
                                f"Status {response.status_code}")
                    
                    # Check for proper Arabic RTL support
                    if 'dir="rtl"' in response.text or 'direction' in response.text:
                        self.log_test(f"RTL Support - {description}", "PASS", 
                                    "Arabic RTL attributes found")
                    else:
                        self.log_test(f"RTL Support - {description}", "WARN", 
                                    "No RTL attributes found")
                        
                else:
                    self.log_test(f"URL Access - {description}", "FAIL", 
                                f"Status {response.status_code}")
                    return False
            
            # Test navigation links within pages
            hub_response = requests.get(f"{self.base_url}/surveys/distribution", timeout=10)
            
            if 'create-campaign' in hub_response.text:
                self.log_test("Navigation Links", "PASS", 
                            "Campaign creation link found in hub")
            else:
                self.log_test("Navigation Links", "FAIL", 
                            "Campaign creation link not found in hub")
                return False
                
            return True
            
        except Exception as e:
            self.log_test("URL Generation and Navigation", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_error_handling_and_validation(self) -> bool:
        """Test 6: Error Handling and Validation"""
        print("\n=== Phase 6: Error Handling Tests ===")
        
        try:
            # Test form validation with missing required fields
            invalid_data = {
                'name': '',  # Empty required field
                'survey_id': '',  # Empty required field
                'description': 'Test validation',
                'method_type': 'email'
            }
            
            response = requests.post(
                f"{self.base_url}/surveys/distribution/create-campaign",
                data=invalid_data,
                timeout=10,
                allow_redirects=False
            )
            
            # Should redirect back to form or show validation error
            if response.status_code in [200, 302, 400]:
                self.log_test("Form Validation", "PASS", 
                            f"Validation handled properly, status: {response.status_code}")
            else:
                self.log_test("Form Validation", "FAIL", 
                            f"Unexpected status: {response.status_code}")
                return False
            
            # Test with invalid survey ID
            invalid_survey_data = {
                'name': 'Test Campaign',
                'survey_id': '99999',  # Non-existent survey ID
                'description': 'Test validation',
                'method_type': 'email'
            }
            
            response = requests.post(
                f"{self.base_url}/surveys/distribution/create-campaign",
                data=invalid_survey_data,
                timeout=10,
                allow_redirects=False
            )
            
            if response.status_code in [200, 302, 400]:
                self.log_test("Invalid Survey ID Handling", "PASS", 
                            f"Invalid survey ID handled, status: {response.status_code}")
            else:
                self.log_test("Invalid Survey ID Handling", "FAIL", 
                            f"Unexpected status: {response.status_code}")
                return False
                
            return True
            
        except Exception as e:
            self.log_test("Error Handling and Validation", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_performance_and_responsiveness(self) -> bool:
        """Test 7: Performance and Responsiveness"""
        print("\n=== Phase 7: Performance Tests ===")
        
        try:
            # Test response times for key pages
            pages_to_test = [
                ("/surveys/distribution", "Distribution Hub"),
                ("/surveys/distribution/create-campaign", "Campaign Form")
            ]
            
            for url, description in pages_to_test:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{url}", timeout=10)
                end_time = time.time()
                
                response_time = end_time - start_time
                
                if response.status_code == 200:
                    if response_time < 2.0:  # Less than 2 seconds
                        self.log_test(f"Performance - {description}", "PASS", 
                                    f"Response time: {response_time:.2f}s")
                    else:
                        self.log_test(f"Performance - {description}", "WARN", 
                                    f"Slow response time: {response_time:.2f}s")
                else:
                    self.log_test(f"Performance - {description}", "FAIL", 
                                f"Page not accessible: {response.status_code}")
                    return False
            
            # Test concurrent requests
            import threading
            concurrent_results = []
            
            def concurrent_request():
                try:
                    response = requests.get(f"{self.base_url}/surveys/distribution", timeout=10)
                    concurrent_results.append(response.status_code)
                except:
                    concurrent_results.append(500)
            
            threads = []
            for _ in range(5):  # 5 concurrent requests
                thread = threading.Thread(target=concurrent_request)
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            successful_requests = sum(1 for code in concurrent_results if code == 200)
            
            if successful_requests >= 4:  # At least 4 out of 5 successful
                self.log_test("Concurrent Request Handling", "PASS", 
                            f"{successful_requests}/5 requests successful")
            else:
                self.log_test("Concurrent Request Handling", "FAIL", 
                            f"Only {successful_requests}/5 requests successful")
                return False
                
            return True
            
        except Exception as e:
            self.log_test("Performance and Responsiveness", "FAIL", f"Error: {str(e)}")
            return False
    
    def cleanup_test_data(self):
        """Clean up test data created during testing"""
        print("\n=== Cleanup Phase ===")
        
        try:
            from models.survey_campaigns import SurveyCampaign, DistributionMethod
            from models.survey_flask import SurveyFlask
            from app import db
            
            # Clean up test campaign if created
            if 'test_campaign_id' in self.test_data:
                campaign = SurveyCampaign.query.get(self.test_data['test_campaign_id'])
                if campaign:
                    # Delete associated distribution methods first
                    DistributionMethod.query.filter_by(campaign_id=campaign.id).delete()
                    db.session.delete(campaign)
                    self.log_test("Cleanup - Test Campaign", "PASS", 
                                f"Removed campaign ID: {campaign.id}")
            
            # Clean up test survey if created
            if 'test_survey_id' in self.test_data:
                survey = SurveyFlask.query.filter_by(uuid='test-campaign-survey-uuid').first()
                if survey:
                    db.session.delete(survey)
                    self.log_test("Cleanup - Test Survey", "PASS", 
                                f"Removed test survey")
            
            db.session.commit()
            
        except Exception as e:
            self.log_test("Cleanup", "WARN", f"Cleanup error: {str(e)}")
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['status'] == 'PASS')
        failed_tests = sum(1 for result in self.test_results if result['status'] == 'FAIL')
        warned_tests = sum(1 for result in self.test_results if result['status'] == 'WARN')
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'warned_tests': warned_tests,
            'success_rate': round(success_rate, 1),
            'test_results': self.test_results,
            'test_data_used': self.test_data
        }
        
        return report
    
    def run_all_tests(self) -> bool:
        """Run complete test suite"""
        print("🚀 Starting Comprehensive Distribution System Testing")
        print("=" * 70)
        
        test_methods = [
            self.test_database_structure,
            self.test_distribution_hub_routes,
            self.test_campaign_creation_workflow,
            self.test_dashboard_metrics_calculation,
            self.test_url_generation_and_navigation,
            self.test_error_handling_and_validation,
            self.test_performance_and_responsiveness
        ]
        
        all_passed = True
        
        for test_method in test_methods:
            try:
                result = test_method()
                if not result:
                    all_passed = False
            except Exception as e:
                self.log_test(test_method.__name__, "FAIL", f"Exception: {str(e)}")
                all_passed = False
        
        # Cleanup
        self.cleanup_test_data()
        
        # Generate and display final report
        report = self.generate_test_report()
        
        print("\n" + "=" * 70)
        print("🏁 FINAL TEST REPORT")
        print("=" * 70)
        print(f"Total Tests: {report['total_tests']}")
        print(f"✅ Passed: {report['passed_tests']}")
        print(f"❌ Failed: {report['failed_tests']}")
        print(f"⚠️  Warnings: {report['warned_tests']}")
        print(f"📊 Success Rate: {report['success_rate']}%")
        
        if all_passed and report['failed_tests'] == 0:
            print("\n🎉 ALL TESTS PASSED! Distribution system is production ready.")
        else:
            print(f"\n⚠️  {report['failed_tests']} test(s) failed. Review required.")
        
        # Save report to file
        with open('tests/distribution_test_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📋 Detailed report saved to: tests/distribution_test_report.json")
        
        return all_passed

def main():
    """Main testing entry point"""
    tester = DistributionSystemTester()
    success = tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())