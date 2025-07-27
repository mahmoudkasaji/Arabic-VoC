"""
Comprehensive Channel System Validation
Complete end-to-end testing of channel filtering and data synchronization
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models_unified import Feedback, FeedbackChannel, FeedbackStatus

def validate_database_structure():
    """Validate database structure and channel metadata consistency"""
    with app.app_context():
        results = {
            'total_feedback': 0,
            'email_feedback': 0,
            'widget_feedback': 0,
            'with_metadata': 0,
            'metadata_complete': 0,
            'source_types': {},
            'issues': []
        }
        
        # Get all feedback from active channels
        feedback_items = db.session.query(Feedback).filter(
            Feedback.channel.in_([FeedbackChannel.EMAIL, FeedbackChannel.WIDGET])
        ).all()
        
        results['total_feedback'] = len(feedback_items)
        
        for feedback in feedback_items:
            # Count by channel
            if feedback.channel == FeedbackChannel.EMAIL:
                results['email_feedback'] += 1
            elif feedback.channel == FeedbackChannel.WIDGET:
                results['widget_feedback'] += 1
            
            # Check metadata
            if feedback.channel_metadata:
                results['with_metadata'] += 1
                
                if isinstance(feedback.channel_metadata, dict) and 'source_type' in feedback.channel_metadata:
                    results['metadata_complete'] += 1
                    source_type = feedback.channel_metadata['source_type']
                    results['source_types'][source_type] = results['source_types'].get(source_type, 0) + 1
                else:
                    results['issues'].append(f"Feedback {feedback.id}: incomplete metadata structure")
            else:
                results['issues'].append(f"Feedback {feedback.id}: missing metadata")
        
        return results

def validate_route_functionality():
    """Test route functionality with different filter parameters"""
    with app.test_client() as client:
        results = {
            'routes_tested': 0,
            'routes_passed': 0,
            'filter_tests': {},
            'issues': []
        }
        
        # Test main route
        response = client.get('/surveys/responses')
        results['routes_tested'] += 1
        if response.status_code == 200:
            results['routes_passed'] += 1
            results['filter_tests']['main_route'] = 'PASSED'
        else:
            results['filter_tests']['main_route'] = f'FAILED - {response.status_code}'
            results['issues'].append(f"Main route failed with {response.status_code}")
        
        # Test channel filters
        for filter_value in ['all', 'email', 'widget', 'invalid']:
            response = client.get(f'/surveys/responses?channel={filter_value}')
            results['routes_tested'] += 1
            if response.status_code == 200:
                results['routes_passed'] += 1
                results['filter_tests'][f'channel_{filter_value}'] = 'PASSED'
            else:
                results['filter_tests'][f'channel_{filter_value}'] = f'FAILED - {response.status_code}'
                results['issues'].append(f"Channel filter '{filter_value}' failed with {response.status_code}")
        
        # Test date filters
        from datetime import datetime, timedelta
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        
        response = client.get(f'/surveys/responses?date_from={yesterday}&date_to={today}')
        results['routes_tested'] += 1
        if response.status_code == 200:
            results['routes_passed'] += 1
            results['filter_tests']['date_filter'] = 'PASSED'
        else:
            results['filter_tests']['date_filter'] = f'FAILED - {response.status_code}'
            results['issues'].append(f"Date filter failed with {response.status_code}")
        
        return results

def validate_ui_elements():
    """Validate UI elements and JavaScript integration"""
    with app.test_client() as client:
        response = client.get('/surveys/responses')
        
        if response.status_code != 200:
            return {
                'ui_valid': False,
                'issues': [f"Route failed with {response.status_code}"]
            }
        
        response_data = response.get_data(as_text=True)
        
        results = {
            'ui_valid': True,
            'elements_found': {},
            'issues': []
        }
        
        # Check essential UI elements
        ui_elements = {
            'arabic_title': 'توزيع المصادر النشطة',
            'all_sources_filter': 'جميع المصادر',
            'date_from_label': 'من تاريخ',
            'date_to_label': 'إلى تاريخ',
            'apply_filter_button': 'تطبيق الفلتر',
            'clear_filters_button': 'مسح الفلاتر',
            'gmail_channel': 'Gmail',
            'widget_channel': 'الويدجت'
        }
        
        for element_name, element_text in ui_elements.items():
            if element_text in response_data:
                results['elements_found'][element_name] = 'FOUND'
            else:
                results['elements_found'][element_name] = 'MISSING'
                results['issues'].append(f"UI element missing: {element_text}")
                results['ui_valid'] = False
        
        # Check JavaScript elements
        js_elements = {
            'channel_filter_function': 'handleChannelFilter',
            'radio_button_handling': 'channelFilter',
            'event_listeners': 'addEventListener',
            'url_updates': 'window.location.href'
        }
        
        for js_name, js_code in js_elements.items():
            if js_code in response_data:
                results['elements_found'][js_name] = 'FOUND'
            else:
                results['elements_found'][js_name] = 'MISSING'
                results['issues'].append(f"JavaScript element missing: {js_code}")
                results['ui_valid'] = False
        
        return results

def generate_comprehensive_report():
    """Generate comprehensive validation report"""
    print("🔍 COMPREHENSIVE CHANNEL SYSTEM VALIDATION")
    print("=" * 60)
    
    # Database validation
    print("\n📊 DATABASE STRUCTURE VALIDATION")
    print("-" * 40)
    db_results = validate_database_structure()
    
    print(f"Total Feedback: {db_results['total_feedback']}")
    print(f"Email Feedback: {db_results['email_feedback']}")
    print(f"Widget Feedback: {db_results['widget_feedback']}")
    print(f"With Metadata: {db_results['with_metadata']}")
    print(f"Complete Metadata: {db_results['metadata_complete']}")
    
    if db_results['source_types']:
        print("\nSource Type Distribution:")
        for source_type, count in db_results['source_types'].items():
            print(f"  {source_type}: {count}")
    
    if db_results['issues']:
        print("\n⚠️  Database Issues:")
        for issue in db_results['issues'][:5]:  # Show first 5 issues
            print(f"  - {issue}")
        if len(db_results['issues']) > 5:
            print(f"  ... and {len(db_results['issues']) - 5} more issues")
    
    # Route validation
    print("\n🛣️  ROUTE FUNCTIONALITY VALIDATION")
    print("-" * 40)
    route_results = validate_route_functionality()
    
    print(f"Routes Tested: {route_results['routes_tested']}")
    print(f"Routes Passed: {route_results['routes_passed']}")
    print(f"Success Rate: {(route_results['routes_passed']/route_results['routes_tested']*100):.1f}%")
    
    print("\nFilter Test Results:")
    for test_name, result in route_results['filter_tests'].items():
        status_icon = "✅" if result == 'PASSED' else "❌"
        print(f"  {status_icon} {test_name}: {result}")
    
    if route_results['issues']:
        print("\n⚠️  Route Issues:")
        for issue in route_results['issues']:
            print(f"  - {issue}")
    
    # UI validation
    print("\n🎨 USER INTERFACE VALIDATION")
    print("-" * 40)
    ui_results = validate_ui_elements()
    
    print(f"UI Valid: {'✅ YES' if ui_results['ui_valid'] else '❌ NO'}")
    
    print("\nUI Elements Status:")
    for element_name, status in ui_results['elements_found'].items():
        status_icon = "✅" if status == 'FOUND' else "❌"
        print(f"  {status_icon} {element_name}: {status}")
    
    if ui_results['issues']:
        print("\n⚠️  UI Issues:")
        for issue in ui_results['issues']:
            print(f"  - {issue}")
    
    # Overall assessment
    print("\n🎯 OVERALL SYSTEM ASSESSMENT")
    print("-" * 40)
    
    # Calculate overall scores
    db_score = (db_results['metadata_complete'] / max(db_results['total_feedback'], 1)) * 100
    route_score = (route_results['routes_passed'] / max(route_results['routes_tested'], 1)) * 100
    ui_score = 100 if ui_results['ui_valid'] else 0
    
    overall_score = (db_score + route_score + ui_score) / 3
    
    print(f"Database Score: {db_score:.1f}%")
    print(f"Route Score: {route_score:.1f}%")
    print(f"UI Score: {ui_score:.1f}%")
    print(f"Overall Score: {overall_score:.1f}%")
    
    if overall_score >= 90:
        print("🏆 EXCELLENT - System fully operational")
    elif overall_score >= 75:
        print("✅ GOOD - System working with minor issues")
    elif overall_score >= 60:
        print("⚠️  FAIR - System needs attention")
    else:
        print("❌ POOR - System requires immediate fixes")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS")
    print("-" * 40)
    
    if overall_score >= 90:
        print("✅ System is production-ready")
        print("✅ All channel filtering functionality working correctly")
        print("✅ Data synchronization between database, routes, and UI is solid")
    else:
        print("🔧 Priority fixes needed:")
        if db_score < 90:
            print("  - Update remaining feedback entries with proper channel metadata")
        if route_score < 90:
            print("  - Fix failing route tests and parameter handling")
        if ui_score < 90:
            print("  - Ensure all UI elements and JavaScript functions are present")
    
    return {
        'database': db_results,
        'routes': route_results,
        'ui': ui_results,
        'scores': {
            'database': db_score,
            'routes': route_score,
            'ui': ui_score,
            'overall': overall_score
        }
    }

if __name__ == "__main__":
    comprehensive_results = generate_comprehensive_report()