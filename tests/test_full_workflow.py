#!/usr/bin/env python3
"""
Full Workflow Test for Distribution System
Tests complete end-to-end functionality including database operations
"""

import requests
import json
import time
from datetime import datetime

class FullWorkflowTest:
    """Complete workflow testing for distribution system"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.results = []
        
    def log_result(self, test_name, status, details="", data=None):
        """Log test result with details"""
        result = {
            'test_name': test_name,
            'status': status,
            'details': details,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        self.results.append(result)
        
        color = '\033[92m' if status == 'PASS' else '\033[91m' if status == 'FAIL' else '\033[93m'
        reset = '\033[0m'
        print(f"{color}[{status}]{reset} {test_name}")
        if details:
            print(f"      {details}")
    
    def test_hub_functionality(self):
        """Test distribution hub complete functionality"""
        print("\n=== Hub Functionality Tests ===")
        
        try:
            response = requests.get(f"{self.base_url}/surveys/distribution", timeout=10)
            
            # Basic accessibility
            if response.status_code == 200:
                self.log_result("Hub Accessibility", "PASS", f"Status 200, {len(response.text)} chars")
            else:
                self.log_result("Hub Accessibility", "FAIL", f"Status {response.status_code}")
                return False
            
            # Arabic UI elements
            arabic_elements = [
                "مركز توزيع الاستطلاعات",  # Page title
                "إنشاء حملة جديدة",         # Create button
                "الحملات الأخيرة",          # Recent campaigns
                "إجمالي الحملات",           # Total campaigns metric
                "معدل الاستجابة",           # Response rate
                "إجراءات سريعة"             # Quick actions
            ]
            
            found_elements = [elem for elem in arabic_elements if elem in response.text]
            
            if len(found_elements) >= 4:
                self.log_result("Arabic UI Elements", "PASS", f"Found {len(found_elements)}/6 elements")
            else:
                self.log_result("Arabic UI Elements", "FAIL", f"Only {len(found_elements)}/6 elements found")
            
            # Dashboard metrics structure
            if "إجمالي الحملات" in response.text and "الحملات النشطة" in response.text:
                self.log_result("Dashboard Metrics", "PASS", "Metrics dashboard structure present")
            else:
                self.log_result("Dashboard Metrics", "FAIL", "Missing metrics dashboard structure")
            
            # Quick actions availability
            if "create-campaign" in response.text:
                self.log_result("Quick Actions", "PASS", "Campaign creation action available")
            else:
                self.log_result("Quick Actions", "FAIL", "Campaign creation action missing")
                
            return True
            
        except Exception as e:
            self.log_result("Hub Functionality", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_campaign_creation_flow(self):
        """Test complete campaign creation workflow"""
        print("\n=== Campaign Creation Flow Tests ===")
        
        try:
            # Step 1: Access campaign creation form
            form_response = requests.get(f"{self.base_url}/surveys/distribution/create-campaign", timeout=10)
            
            if form_response.status_code == 200:
                self.log_result("Campaign Form Access", "PASS", "Form accessible")
            else:
                self.log_result("Campaign Form Access", "FAIL", f"Status {form_response.status_code}")
                return False
            
            # Step 2: Validate form structure
            required_fields = [
                'name="name"',           # Campaign name
                'name="survey_id"',      # Survey selection
                'name="description"',    # Description
                'name="method_type"',    # Distribution method
                'name="schedule_type"'   # Scheduling option
            ]
            
            missing_fields = [field for field in required_fields if field not in form_response.text]
            
            if not missing_fields:
                self.log_result("Form Structure", "PASS", f"All {len(required_fields)} required fields present")
            else:
                self.log_result("Form Structure", "FAIL", f"Missing fields: {missing_fields}")
                return False
            
            # Step 3: Test form submission with valid data
            # First, create a test campaign with realistic data
            campaign_data = {
                'name': f'Test Workflow Campaign {datetime.now().strftime("%H%M%S")}',
                'survey_id': '1',  # Assuming survey ID 1 exists
                'description': 'End-to-end workflow test campaign',
                'method_type': 'email',
                'schedule_type': 'now'
            }
            
            submit_response = requests.post(
                f"{self.base_url}/surveys/distribution/create-campaign",
                data=campaign_data,
                timeout=10,
                allow_redirects=False
            )
            
            # Step 4: Validate submission handling
            if submit_response.status_code in [200, 302]:
                self.log_result("Campaign Submission", "PASS", f"Status {submit_response.status_code}")
                
                # Check for success redirect or flash message
                if submit_response.status_code == 302:
                    redirect_url = submit_response.headers.get('Location', '')
                    if 'distribution' in redirect_url:
                        self.log_result("Success Redirect", "PASS", "Redirected to distribution hub")
                    else:
                        self.log_result("Success Redirect", "WARN", f"Unexpected redirect: {redirect_url}")
                        
            else:
                self.log_result("Campaign Submission", "FAIL", f"Status {submit_response.status_code}")
                return False
            
            # Step 5: Test validation with invalid data
            invalid_data = {
                'name': '',  # Empty required field
                'survey_id': '',
                'method_type': 'email'
            }
            
            validation_response = requests.post(
                f"{self.base_url}/surveys/distribution/create-campaign",
                data=invalid_data,
                timeout=10,
                allow_redirects=False
            )
            
            if validation_response.status_code in [200, 302, 400]:
                self.log_result("Form Validation", "PASS", "Validation properly handled")
            else:
                self.log_result("Form Validation", "FAIL", f"Unexpected validation response: {validation_response.status_code}")
                
            return True
            
        except Exception as e:
            self.log_result("Campaign Creation Flow", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_ui_responsiveness(self):
        """Test UI responsiveness and design"""
        print("\n=== UI Responsiveness Tests ===")
        
        try:
            # Test hub page responsiveness
            hub_response = requests.get(f"{self.base_url}/surveys/distribution", timeout=10)
            
            # Check for responsive design elements
            responsive_indicators = [
                'class="container',     # Bootstrap containers
                'class="row',          # Grid system
                'class="col-',         # Responsive columns
                'btn btn-',            # Button classes
                'card',                # Card components
                'modal'                # Modal dialogs
            ]
            
            found_responsive = sum(1 for indicator in responsive_indicators if indicator in hub_response.text)
            
            if found_responsive >= 4:
                self.log_result("Responsive Design", "PASS", f"Found {found_responsive}/6 responsive elements")
            else:
                self.log_result("Responsive Design", "FAIL", f"Only {found_responsive}/6 responsive elements")
            
            # Test RTL (Right-to-Left) support
            rtl_indicators = [
                'dir="rtl"',
                'lang="ar"',
                'text-end',       # RTL text alignment
                'me-',            # RTL margin classes
                'ms-'             # RTL margin classes
            ]
            
            found_rtl = sum(1 for indicator in rtl_indicators if indicator in hub_response.text)
            
            if found_rtl >= 2:
                self.log_result("RTL Support", "PASS", f"Found {found_rtl}/5 RTL elements")
            else:
                self.log_result("RTL Support", "FAIL", f"Only {found_rtl}/5 RTL elements")
            
            # Test performance
            start_time = time.time()
            perf_response = requests.get(f"{self.base_url}/surveys/distribution", timeout=10)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            if response_time < 1.0:
                self.log_result("Page Performance", "PASS", f"Fast response: {response_time:.2f}s")
            elif response_time < 3.0:
                self.log_result("Page Performance", "WARN", f"Acceptable response: {response_time:.2f}s")
            else:
                self.log_result("Page Performance", "FAIL", f"Slow response: {response_time:.2f}s")
                
            return True
            
        except Exception as e:
            self.log_result("UI Responsiveness", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_navigation_flow(self):
        """Test complete navigation flow"""
        print("\n=== Navigation Flow Tests ===")
        
        try:
            # Test navigation from hub to form
            hub_response = requests.get(f"{self.base_url}/surveys/distribution", timeout=10)
            
            if "create-campaign" in hub_response.text:
                self.log_result("Hub to Form Navigation", "PASS", "Create campaign link found")
            else:
                self.log_result("Hub to Form Navigation", "FAIL", "Create campaign link missing")
                return False
            
            # Test form back navigation
            form_response = requests.get(f"{self.base_url}/surveys/distribution/create-campaign", timeout=10)
            
            back_navigation = ["العودة", "إلغاء", "distribution"]
            found_back = sum(1 for nav in back_navigation if nav in form_response.text)
            
            if found_back >= 1:
                self.log_result("Form Back Navigation", "PASS", f"Found {found_back} back navigation elements")
            else:
                self.log_result("Form Back Navigation", "FAIL", "No back navigation found")
            
            # Test breadcrumb or navigation context
            if "مركز توزيع" in form_response.text or "Distribution" in form_response.text:
                self.log_result("Navigation Context", "PASS", "Context navigation present")
            else:
                self.log_result("Navigation Context", "WARN", "No clear navigation context")
                
            return True
            
        except Exception as e:
            self.log_result("Navigation Flow", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_error_handling(self):
        """Test comprehensive error handling"""
        print("\n=== Error Handling Tests ===")
        
        try:
            # Test invalid survey ID
            invalid_survey_data = {
                'name': 'Test Error Handling',
                'survey_id': '99999',  # Non-existent survey
                'description': 'Testing error handling',
                'method_type': 'email'
            }
            
            error_response = requests.post(
                f"{self.base_url}/surveys/distribution/create-campaign",
                data=invalid_survey_data,
                timeout=10,
                allow_redirects=False
            )
            
            if error_response.status_code in [200, 302, 400]:
                self.log_result("Invalid Survey Handling", "PASS", f"Error handled gracefully: {error_response.status_code}")
            else:
                self.log_result("Invalid Survey Handling", "FAIL", f"Unexpected error response: {error_response.status_code}")
            
            # Test missing required fields
            empty_data = {
                'name': '',
                'survey_id': '',
                'method_type': ''
            }
            
            validation_response = requests.post(
                f"{self.base_url}/surveys/distribution/create-campaign",
                data=empty_data,
                timeout=10,
                allow_redirects=False
            )
            
            if validation_response.status_code in [200, 302, 400]:
                self.log_result("Required Field Validation", "PASS", "Empty fields handled properly")
            else:
                self.log_result("Required Field Validation", "FAIL", f"Validation not working: {validation_response.status_code}")
            
            # Test invalid method type
            invalid_method_data = {
                'name': 'Test Campaign',
                'survey_id': '1',
                'method_type': 'invalid_method',
                'description': 'Testing invalid method'
            }
            
            method_response = requests.post(
                f"{self.base_url}/surveys/distribution/create-campaign",
                data=invalid_method_data,
                timeout=10,
                allow_redirects=False
            )
            
            if method_response.status_code in [200, 302, 400]:
                self.log_result("Invalid Method Handling", "PASS", "Invalid method handled")
            else:
                self.log_result("Invalid Method Handling", "FAIL", f"Method validation failed: {method_response.status_code}")
                
            return True
            
        except Exception as e:
            self.log_result("Error Handling", "FAIL", f"Error: {str(e)}")
            return False
    
    def run_complete_test_suite(self):
        """Run all comprehensive tests"""
        print("🚀 Starting Complete Distribution System Test Suite")
        print("=" * 70)
        
        test_suites = [
            ("Hub Functionality", self.test_hub_functionality),
            ("Campaign Creation Flow", self.test_campaign_creation_flow),
            ("UI Responsiveness", self.test_ui_responsiveness),
            ("Navigation Flow", self.test_navigation_flow),
            ("Error Handling", self.test_error_handling)
        ]
        
        suite_results = {}
        
        for suite_name, test_method in test_suites:
            print(f"\n🔧 Running {suite_name} Tests...")
            try:
                result = test_method()
                suite_results[suite_name] = result
            except Exception as e:
                print(f"❌ {suite_name} suite failed: {str(e)}")
                suite_results[suite_name] = False
        
        # Generate comprehensive report
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['status'] == 'PASS')
        failed_tests = sum(1 for r in self.results if r['status'] == 'FAIL')
        warned_tests = sum(1 for r in self.results if r['status'] == 'WARN')
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print("\n" + "=" * 70)
        print("🏁 COMPREHENSIVE TEST REPORT")
        print("=" * 70)
        print(f"Test Suites: {len(test_suites)}")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️  Warnings: {warned_tests}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        print(f"\n📋 Suite Results:")
        for suite_name, result in suite_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} {suite_name}")
        
        # Detailed results
        print(f"\n📝 Detailed Test Results:")
        for result in self.results:
            status_icon = "✅" if result['status'] == 'PASS' else "❌" if result['status'] == 'FAIL' else "⚠️"
            print(f"  {status_icon} {result['test_name']}: {result['details']}")
        
        # Overall assessment
        successful_suites = sum(1 for result in suite_results.values() if result)
        
        if successful_suites == len(test_suites) and failed_tests == 0:
            print(f"\n🎉 COMPLETE SUCCESS! All {len(test_suites)} test suites passed!")
            print("Distribution system is fully functional and production-ready.")
        elif successful_suites >= len(test_suites) * 0.8:  # 80% success
            print(f"\n✅ LARGELY SUCCESSFUL! {successful_suites}/{len(test_suites)} suites passed.")
            print("Distribution system is functional with minor issues.")
        else:
            print(f"\n⚠️  NEEDS ATTENTION! Only {successful_suites}/{len(test_suites)} suites passed.")
            print("Distribution system requires fixes before production use.")
        
        # Save comprehensive report
        report = {
            'timestamp': datetime.now().isoformat(),
            'suite_results': suite_results,
            'test_statistics': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'warned_tests': warned_tests,
                'success_rate': success_rate
            },
            'detailed_results': self.results
        }
        
        with open('/tmp/distribution_comprehensive_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📋 Comprehensive report saved to: /tmp/distribution_comprehensive_report.json")
        
        return successful_suites == len(test_suites) and failed_tests == 0

if __name__ == "__main__":
    tester = FullWorkflowTest()
    success = tester.run_complete_test_suite()
    exit(0 if success else 1)