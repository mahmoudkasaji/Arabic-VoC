#!/usr/bin/env python3
"""
Comprehensive Test Execution for Arabic Voice of Customer Platform
Executes tests in logical sequence with proper error handling and reporting
"""

import subprocess
import sys
import time
import json
from datetime import datetime

class TestExecutor:
    def __init__(self):
        self.start_time = datetime.now()
        self.results = {
            'summary': {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0},
            'phases': {},
            'critical_failures': []
        }
    
    def execute_test_group(self, group_name, test_commands, critical=False):
        """Execute a group of related tests"""
        print(f"\n{'='*60}")
        print(f"EXECUTING: {group_name}")
        print(f"{'='*60}")
        
        group_start = time.time()
        group_results = {'passed': 0, 'failed': 0, 'errors': []}
        
        for test_cmd in test_commands:
            print(f"\nRunning: {test_cmd}")
            try:
                result = subprocess.run(
                    ['python', '-m', 'pytest'] + test_cmd.split(),
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode == 0:
                    print("✓ PASSED")
                    group_results['passed'] += 1
                    self.results['summary']['passed'] += 1
                else:
                    print("✗ FAILED")
                    group_results['failed'] += 1
                    self.results['summary']['failed'] += 1
                    
                    error_info = {
                        'test': test_cmd,
                        'output': result.stdout + result.stderr,
                        'critical': critical
                    }
                    group_results['errors'].append(error_info)
                    
                    if critical:
                        self.results['critical_failures'].append(error_info)
                
                self.results['summary']['total'] += 1
                
            except subprocess.TimeoutExpired:
                print("⏰ TIMEOUT")
                group_results['failed'] += 1
                self.results['summary']['failed'] += 1
                self.results['summary']['total'] += 1
                
            except Exception as e:
                print(f"🚨 ERROR: {str(e)}")
                group_results['failed'] += 1
                self.results['summary']['failed'] += 1
                self.results['summary']['total'] += 1
        
        group_duration = time.time() - group_start
        self.results['phases'][group_name] = {
            'duration': group_duration,
            'passed': group_results['passed'],
            'failed': group_results['failed'],
            'errors': group_results['errors']
        }
        
        print(f"\n{group_name} Summary: {group_results['passed']} passed, {group_results['failed']} failed ({group_duration:.2f}s)")
    
    def run_comprehensive_test_suite(self):
        """Execute comprehensive test suite in logical order"""
        
        # Phase 1: Core Arabic Processing (Critical)
        arabic_processing_tests = [
            "tests/test_arabic_processing.py::TestArabicTextProcessor::test_arabic_detection",
            "tests/test_arabic_processing.py::TestArabicTextProcessor::test_arabic_normalization", 
            "tests/test_arabic_processing.py::TestArabicTextProcessor::test_reshaping_for_display",
            "tests/test_arabic_dialects.py::TestArabicDialects::test_gulf_dialect_processing",
            "tests/test_arabic_dialects.py::TestArabicDialects::test_egyptian_dialect_processing"
        ]
        self.execute_test_group("Arabic Processing", arabic_processing_tests, critical=True)
        
        # Phase 2: Database Operations (Critical)
        database_tests = [
            "tests/test_database_arabic.py::TestArabicDatabaseConfiguration::test_database_connection",
            "tests/test_database_arabic.py::TestArabicDatabaseConfiguration::test_utf8_encoding",
            "tests/test_database_arabic.py::TestArabicUserModel::test_create_user_with_arabic_names",
            "tests/test_database_arabic.py::TestArabicSurveyModel::test_create_bilingual_survey"
        ]
        self.execute_test_group("Database Operations", database_tests, critical=True)
        
        # Phase 3: Authentication System (Critical)
        auth_tests = [
            "tests/test_auth_integration.py::TestUsernameValidation::test_valid_usernames",
            "tests/test_auth_integration.py::TestPasswordSecurity::test_password_hashing",
            "tests/test_auth_integration.py::TestJWTTokens::test_access_token_creation",
            "tests/test_auth_api.py::TestArabicNameValidation::test_arabic_name_normalization"
        ]
        self.execute_test_group("Authentication System", auth_tests, critical=True)
        
        # Phase 4: API Endpoints (Critical)
        api_tests = [
            "tests/test_api_endpoints.py::TestArabicSpecificAPI::test_arabic_content_processing",
            "tests/test_api_endpoints.py::TestArabicSpecificAPI::test_arabic_character_encoding",
            "tests/test_api_comprehensive.py::TestFeedbackAPI",
        ]
        self.execute_test_group("API Endpoints", api_tests, critical=True)
        
        # Phase 5: Security Validation (Important)
        security_tests = [
            "tests/test_security.py::TestSecurityIntegration::test_arabic_text_with_security_patterns",
            "tests/test_arabic_processing.py::TestArabicSecurity::test_malicious_input_handling",
            "tests/test_arabic_processing.py::TestArabicSecurity::test_unicode_safety"
        ]
        self.execute_test_group("Security Validation", security_tests, critical=False)
        
        # Phase 6: Performance Testing (Important)
        performance_tests = [
            "tests/test_performance.py::TestPerformanceBenchmarks::test_arabic_processing_performance",
            "tests/test_dashboard_performance.py::TestDashboardPerformance::test_arabic_processing_rate_target",
            "tests/test_load_performance.py::TestLoadPerformance::test_arabic_processing_throughput"
        ]
        self.execute_test_group("Performance Testing", performance_tests, critical=False)
        
        # Phase 7: Integration Testing (Important) 
        integration_tests = [
            "tests/test_openai_integration.py::TestOpenAIConnection",
            "tests/test_english_support.py::TestEnglishLanguageSupport::test_language_toggle_button_presence"
        ]
        self.execute_test_group("Integration Testing", integration_tests, critical=False)
    
    def generate_final_report(self):
        """Generate comprehensive test execution report"""
        total_duration = (datetime.now() - self.start_time).total_seconds()
        
        print(f"\n{'='*80}")
        print("COMPREHENSIVE TEST SUITE EXECUTION REPORT")
        print(f"{'='*80}")
        print(f"Execution Time: {total_duration:.2f} seconds")
        print(f"Start: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"End: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Summary
        summary = self.results['summary']
        success_rate = (summary['passed'] / summary['total'] * 100) if summary['total'] > 0 else 0
        
        print(f"\nOVERALL SUMMARY:")
        print(f"  Total Tests: {summary['total']}")
        print(f"  Passed: {summary['passed']}")
        print(f"  Failed: {summary['failed']}")
        print(f"  Success Rate: {success_rate:.1f}%")
        
        # Phase breakdown
        print(f"\nPHASE BREAKDOWN:")
        for phase_name, phase_data in self.results['phases'].items():
            phase_success = (phase_data['passed'] / (phase_data['passed'] + phase_data['failed']) * 100) if (phase_data['passed'] + phase_data['failed']) > 0 else 0
            print(f"  {phase_name:<25} {phase_data['passed']:>3}/{phase_data['passed'] + phase_data['failed']:<3} ({phase_success:>5.1f}%) - {phase_data['duration']:.2f}s")
        
        # Critical failures
        if self.results['critical_failures']:
            print(f"\nCRITICAL FAILURES ({len(self.results['critical_failures'])}):")
            for failure in self.results['critical_failures']:
                print(f"  ✗ {failure['test']}")
                
        # Production readiness assessment
        critical_success = len(self.results['critical_failures']) == 0
        overall_success = success_rate >= 85
        
        print(f"\nPRODUCTION READINESS ASSESSMENT:")
        print(f"  Critical Systems: {'✓ PASS' if critical_success else '✗ FAIL'}")
        print(f"  Overall Quality: {'✓ PASS' if overall_success else '✗ FAIL'}")
        print(f"  Recommendation: {'READY FOR DEPLOYMENT' if (critical_success and overall_success) else 'REQUIRES ATTENTION'}")
        
        # Save detailed report
        report_file = f"comprehensive_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"\nDetailed report saved: {report_file}")
        
        return critical_success and overall_success

def main():
    executor = TestExecutor()
    executor.run_comprehensive_test_suite()
    success = executor.generate_final_report()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()