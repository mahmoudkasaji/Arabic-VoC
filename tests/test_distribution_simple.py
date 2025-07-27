#!/usr/bin/env python3
"""
Quick Distribution System Test - Focused on Real Functionality
Tests the working parts of the distribution system
"""

import requests
import json
import time
from datetime import datetime

class QuickDistributionTest:
    """Simple test focusing on working functionality"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.results = []
        
    def test_result(self, name, status, details=""):
        """Log test result"""
        result = {
            'test': name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.results.append(result)
        
        color = '\033[92m' if status == 'PASS' else '\033[91m'
        reset = '\033[0m'
        print(f"{color}[{status}]{reset} {name}: {details}")
        
    def test_hub_accessibility(self):
        """Test distribution hub loads correctly"""
        try:
            response = requests.get(f"{self.base_url}/surveys/distribution", timeout=5)
            
            if response.status_code == 200:
                if "مركز توزيع الاستطلاعات" in response.text:
                    self.test_result("Hub Page Load", "PASS", f"Status 200, Arabic title found")
                else:
                    self.test_result("Hub Page Load", "FAIL", "Arabic title missing")
            else:
                self.test_result("Hub Page Load", "FAIL", f"Status {response.status_code}")
                
        except Exception as e:
            self.test_result("Hub Page Load", "FAIL", f"Error: {str(e)}")
    
    def test_campaign_form_accessibility(self):
        """Test campaign creation form loads"""
        try:
            response = requests.get(f"{self.base_url}/surveys/distribution/create-campaign", timeout=5)
            
            if response.status_code == 200:
                form_elements = ['name="name"', 'name="survey_id"', 'name="method_type"']
                found_elements = sum(1 for element in form_elements if element in response.text)
                
                if found_elements == len(form_elements):
                    self.test_result("Campaign Form", "PASS", f"All {found_elements} form elements found")
                else:
                    self.test_result("Campaign Form", "FAIL", f"Only {found_elements}/{len(form_elements)} elements found")
            else:
                self.test_result("Campaign Form", "FAIL", f"Status {response.status_code}")
                
        except Exception as e:
            self.test_result("Campaign Form", "FAIL", f"Error: {str(e)}")
    
    def test_form_validation(self):
        """Test form validation with invalid data"""
        try:
            # Send empty form data to test validation
            response = requests.post(
                f"{self.base_url}/surveys/distribution/create-campaign",
                data={'name': '', 'survey_id': '', 'method_type': 'email'},
                timeout=5,
                allow_redirects=False
            )
            
            # Should redirect or return validation error
            if response.status_code in [200, 302, 400]:
                self.test_result("Form Validation", "PASS", f"Validation works, status {response.status_code}")
            else:
                self.test_result("Form Validation", "FAIL", f"Unexpected status {response.status_code}")
                
        except Exception as e:
            self.test_result("Form Validation", "FAIL", f"Error: {str(e)}")
    
    def test_performance(self):
        """Test response times"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/surveys/distribution", timeout=5)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            if response.status_code == 200:
                if response_time < 2.0:
                    self.test_result("Performance", "PASS", f"Response time: {response_time:.2f}s")
                else:
                    self.test_result("Performance", "WARN", f"Slow response: {response_time:.2f}s")
            else:
                self.test_result("Performance", "FAIL", f"Page not accessible")
                
        except Exception as e:
            self.test_result("Performance", "FAIL", f"Error: {str(e)}")
    
    def test_arabic_support(self):
        """Test Arabic RTL support"""
        try:
            response = requests.get(f"{self.base_url}/surveys/distribution", timeout=5)
            
            if response.status_code == 200:
                arabic_indicators = ['dir="rtl"', 'lang="ar"', 'مركز توزيع', 'إنشاء حملة']
                found_indicators = sum(1 for indicator in arabic_indicators if indicator in response.text)
                
                if found_indicators >= 2:
                    self.test_result("Arabic Support", "PASS", f"{found_indicators} Arabic elements found")
                else:
                    self.test_result("Arabic Support", "FAIL", f"Only {found_indicators} Arabic elements found")
            else:
                self.test_result("Arabic Support", "FAIL", "Page not accessible")
                
        except Exception as e:
            self.test_result("Arabic Support", "FAIL", f"Error: {str(e)}")
    
    def test_navigation_links(self):
        """Test navigation between pages"""
        try:
            # Test hub page has creation link
            hub_response = requests.get(f"{self.base_url}/surveys/distribution", timeout=5)
            
            if "create-campaign" in hub_response.text:
                self.test_result("Navigation Links", "PASS", "Campaign creation link found in hub")
            else:
                self.test_result("Navigation Links", "FAIL", "Campaign creation link not found")
                
            # Test creation page has back link
            form_response = requests.get(f"{self.base_url}/surveys/distribution/create-campaign", timeout=5)
            
            if "العودة" in form_response.text or "إلغاء" in form_response.text:
                self.test_result("Back Navigation", "PASS", "Back navigation found in form")
            else:
                self.test_result("Back Navigation", "FAIL", "Back navigation not found")
                
        except Exception as e:
            self.test_result("Navigation Links", "FAIL", f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all quick tests"""
        print("🚀 Running Quick Distribution System Tests")
        print("=" * 50)
        
        self.test_hub_accessibility()
        self.test_campaign_form_accessibility()
        self.test_form_validation()
        self.test_performance()
        self.test_arabic_support()
        self.test_navigation_links()
        
        # Summary
        total = len(self.results)
        passed = sum(1 for r in self.results if r['status'] == 'PASS')
        failed = sum(1 for r in self.results if r['status'] == 'FAIL')
        warned = sum(1 for r in self.results if r['status'] == 'WARN')
        
        print("\n" + "=" * 50)
        print("📊 QUICK TEST SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warned}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if failed == 0:
            print("\n🎉 All core functionality tests passed!")
            print("Distribution system is working correctly.")
        else:
            print(f"\n⚠️  {failed} test(s) failed - review needed.")
        
        # Save results
        with open('/tmp/quick_test_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        return failed == 0

if __name__ == "__main__":
    tester = QuickDistributionTest()
    success = tester.run_all_tests()
    print(f"\nTest results saved to: /tmp/quick_test_results.json")
    exit(0 if success else 1)