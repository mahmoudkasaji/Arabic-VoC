"""
Channel Testing Framework Runner
Comprehensive testing for channel metadata, filtering, and data synchronization
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_channel_filtering import run_channel_filtering_tests
from test_data_synchronization import run_data_sync_tests
from datetime import datetime

def run_comprehensive_channel_tests():
    """Run all channel-related tests and generate comprehensive report"""
    
    print("=" * 60)
    print("🧪 COMPREHENSIVE CHANNEL TESTING FRAMEWORK")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run Channel Filtering Tests
    print("🔍 Running Channel Filtering Tests...")
    filtering_results = run_channel_filtering_tests()
    
    print("🔄 Running Data Synchronization Tests...")
    sync_results = run_data_sync_tests()
    
    # Combine results
    total_tests = filtering_results['total_tests'] + sync_results['total_tests']
    total_passed = filtering_results['passed_tests'] + sync_results['passed_tests']
    total_failed = filtering_results['failed_tests'] + sync_results['failed_tests']
    
    # Generate comprehensive report
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 60)
    
    print(f"📈 Overall Statistics:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {total_passed}")
    print(f"   Failed: {total_failed}")
    print(f"   Success Rate: {(total_passed/total_tests*100):.1f}%")
    
    print(f"\n🔍 Channel Filtering Tests:")
    print(f"   Tests: {filtering_results['total_tests']}")
    print(f"   Passed: {filtering_results['passed_tests']}")
    print(f"   Failed: {filtering_results['failed_tests']}")
    
    print(f"\n🔄 Data Synchronization Tests:")
    print(f"   Tests: {sync_results['total_tests']}")
    print(f"   Passed: {sync_results['passed_tests']}")
    print(f"   Failed: {sync_results['failed_tests']}")
    
    # Detailed results
    print(f"\n📋 Detailed Test Results:")
    print("-" * 60)
    
    all_results = filtering_results['test_results'] + sync_results['test_results']
    
    for result in all_results:
        status_icon = "✅" if result['status'] == 'PASSED' else "❌"
        test_name = result['test'].replace('test_', '').replace('_', ' ').title()
        print(f"{status_icon} {test_name}")
        
        if result['status'] == 'FAILED':
            print(f"   💥 Error: {result['message']}")
    
    # System validation summary
    print(f"\n🏗️ SYSTEM VALIDATION SUMMARY:")
    print("-" * 60)
    
    validation_checks = [
        ("Database Channel Enum Consistency", "✅" if any("channel_consistency" in r['test'] for r in all_results if r['status'] == 'PASSED') else "❌"),
        ("Route Parameter Handling", "✅" if any("parameter_handling" in r['test'] for r in all_results if r['status'] == 'PASSED') else "❌"),
        ("Channel Metadata Structure", "✅" if any("metadata" in r['test'] for r in all_results if r['status'] == 'PASSED') else "❌"),
        ("UI Filter Integration", "✅" if any("filter" in r['test'] for r in all_results if r['status'] == 'PASSED') else "❌"),
        ("Analytics Calculations", "✅" if any("analytics" in r['test'] for r in all_results if r['status'] == 'PASSED') else "❌"),
        ("JavaScript Integration", "✅" if any("javascript" in r['test'] for r in all_results if r['status'] == 'PASSED') else "❌")
    ]
    
    for check_name, status in validation_checks:
        print(f"{status} {check_name}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    print("-" * 60)
    
    if total_failed == 0:
        print("✅ All tests passed! Channel filtering system is working correctly.")
        print("✅ Database, routes, and UI are properly synchronized.")
        print("✅ System is ready for production use.")
    else:
        print("⚠️  Some tests failed. Review the errors above.")
        print("⚠️  Focus on failed components before deploying to production.")
        
        # Specific recommendations based on failed tests
        failed_areas = []
        for result in all_results:
            if result['status'] == 'FAILED':
                if 'filter' in result['test']:
                    failed_areas.append("Channel Filtering")
                elif 'metadata' in result['test']:
                    failed_areas.append("Metadata Structure")
                elif 'sync' in result['test']:
                    failed_areas.append("Data Synchronization")
        
        if failed_areas:
            unique_areas = list(set(failed_areas))
            print(f"🎯 Priority areas to fix: {', '.join(unique_areas)}")
    
    print(f"\n🕐 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    return {
        'total_tests': total_tests,
        'passed_tests': total_passed,
        'failed_tests': total_failed,
        'success_rate': (total_passed/total_tests*100),
        'filtering_results': filtering_results,
        'sync_results': sync_results,
        'validation_checks': validation_checks
    }

if __name__ == "__main__":
    comprehensive_results = run_comprehensive_channel_tests()