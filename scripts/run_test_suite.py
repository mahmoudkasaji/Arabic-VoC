#!/usr/bin/env python3
"""
Comprehensive Test Suite Runner for Arabic Voice of Customer Platform
Orchestrates testing phases with proper sequencing and reporting
"""

import subprocess
import time
import sys
import json
from datetime import datetime
from pathlib import Path

class TestSuiteRunner:
    def __init__(self):
        self.start_time = datetime.now()
        self.results = {
            'phases': {},
            'summary': {},
            'errors': []
        }
        
    def run_phase(self, phase_name, test_patterns, timeout=300):
        """Run a specific test phase with timeout"""
        print(f"\n{'='*60}")
        print(f"Phase: {phase_name}")
        print(f"{'='*60}")
        
        phase_start = time.time()
        
        for pattern in test_patterns:
            print(f"\nRunning: {pattern}")
            try:
                cmd = [
                    'python', '-m', 'pytest', 
                    pattern,
                    '--tb=short',
                    '--timeout=60',
                    '-v'
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                
                if result.returncode == 0:
                    print(f"✓ PASSED: {pattern}")
                else:
                    print(f"✗ FAILED: {pattern}")
                    self.results['errors'].append({
                        'phase': phase_name,
                        'pattern': pattern,
                        'stderr': result.stderr,
                        'stdout': result.stdout
                    })
                    
            except subprocess.TimeoutExpired:
                print(f"⏰ TIMEOUT: {pattern}")
                self.results['errors'].append({
                    'phase': phase_name,
                    'pattern': pattern,
                    'error': 'Test timeout'
                })
            except Exception as e:
                print(f"🚨 ERROR: {pattern} - {str(e)}")
                self.results['errors'].append({
                    'phase': phase_name,
                    'pattern': pattern,
                    'error': str(e)
                })
        
        phase_duration = time.time() - phase_start
        self.results['phases'][phase_name] = {
            'duration': phase_duration,
            'status': 'completed'
        }
        
        print(f"\nPhase '{phase_name}' completed in {phase_duration:.2f}s")
    
    def run_infrastructure_tests(self):
        """Phase 1: Infrastructure and setup validation"""
        patterns = [
            'tests/conftest.py::*',
            'tests/test_database_arabic.py::TestDatabaseConnection',
            'tests/test_auth_integration.py::TestAuthSetup'
        ]
        self.run_phase("Infrastructure Validation", patterns, timeout=180)
    
    def run_unit_tests(self):
        """Phase 2: Core unit tests"""
        patterns = [
            'tests/test_arabic_processing.py',
            'tests/test_arabic_dialects.py',
            'tests/test_auth_api.py::TestUserValidation',
            'tests/test_auth_integration.py::TestPasswordValidation'
        ]
        self.run_phase("Unit Tests", patterns, timeout=300)
    
    def run_api_tests(self):
        """Phase 3: API integration tests"""
        patterns = [
            'tests/test_api_endpoints.py',
            'tests/test_api_comprehensive.py::TestFeedbackAPI',
            'tests/test_auth_api.py::TestAuthAPI'
        ]
        self.run_phase("API Integration Tests", patterns, timeout=400)
    
    def run_security_tests(self):
        """Phase 4: Security validation"""
        patterns = [
            'tests/test_security.py',
            'tests/test_auth_api.py::TestAuthSecurity'
        ]
        self.run_phase("Security Tests", patterns, timeout=300)
    
    def run_performance_tests(self):
        """Phase 5: Performance validation"""
        patterns = [
            'tests/test_performance.py',
            'tests/test_dashboard_performance.py::TestDashboardLoad',
            'tests/test_load_performance.py::TestBasicLoad'
        ]
        self.run_phase("Performance Tests", patterns, timeout=600)
    
    def run_integration_tests(self):
        """Phase 6: External service integration"""
        patterns = [
            'tests/test_openai_integration.py::TestOpenAIConnection',
            'tests/test_database_arabic.py::TestArabicOperations'
        ]
        self.run_phase("Integration Tests", patterns, timeout=400)
    
    def run_ui_tests(self):
        """Phase 7: UI and bilingual functionality"""
        patterns = [
            'tests/test_english_support.py::TestEnglishLanguageSupport::test_language_toggle_button_presence'
        ]
        self.run_phase("UI/Bilingual Tests", patterns, timeout=500)
    
    def generate_report(self):
        """Generate comprehensive test report"""
        total_duration = (datetime.now() - self.start_time).total_seconds()
        
        print(f"\n{'='*80}")
        print("COMPREHENSIVE TEST SUITE REPORT")
        print(f"{'='*80}")
        print(f"Total Execution Time: {total_duration:.2f}s")
        print(f"Start Time: {self.start_time}")
        print(f"End Time: {datetime.now()}")
        
        print(f"\nPHASE SUMMARY:")
        for phase, details in self.results['phases'].items():
            status = "✓ COMPLETED" if details['status'] == 'completed' else "✗ FAILED"
            print(f"  {phase:<25} {status} ({details['duration']:.2f}s)")
        
        if self.results['errors']:
            print(f"\nERRORS AND FAILURES ({len(self.results['errors'])}):")
            for i, error in enumerate(self.results['errors'], 1):
                print(f"\n{i}. {error['phase']} - {error['pattern']}")
                if 'error' in error:
                    print(f"   Error: {error['error']}")
                if 'stderr' in error and error['stderr']:
                    print(f"   Details: {error['stderr'][:200]}...")
        else:
            print(f"\n🎉 ALL TESTS PASSED! No errors detected.")
        
        # Save detailed report
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\nDetailed report saved to: {report_file}")
        
        return len(self.results['errors']) == 0
    
    def run_critical_path_only(self):
        """Run only critical P0/P1 tests for quick validation"""
        print("Running CRITICAL PATH tests only...")
        self.run_infrastructure_tests()
        self.run_unit_tests()
        self.run_api_tests()
        self.run_security_tests()
        return self.generate_report()
    
    def run_comprehensive_suite(self):
        """Run full comprehensive test suite"""
        print("Running COMPREHENSIVE test suite...")
        self.run_infrastructure_tests()
        self.run_unit_tests()
        self.run_api_tests()
        self.run_security_tests()
        self.run_performance_tests()
        self.run_integration_tests()
        self.run_ui_tests()
        return self.generate_report()

def main():
    runner = TestSuiteRunner()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--critical':
        success = runner.run_critical_path_only()
    else:
        success = runner.run_comprehensive_suite()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()