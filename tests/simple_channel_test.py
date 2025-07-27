"""
Simplified Channel Testing
Direct validation of channel filtering and metadata functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models_unified import Feedback, FeedbackChannel, FeedbackStatus
from datetime import datetime, timedelta

def test_channel_enum_functionality():
    """Test that FeedbackChannel enum methods work correctly"""
    try:
        # Test Arabic name mapping
        email_name = FeedbackChannel.get_arabic_name(FeedbackChannel.EMAIL)
        widget_name = FeedbackChannel.get_arabic_name(FeedbackChannel.WIDGET)
        
        if email_name != "Gmail":
            return False, f"Expected 'Gmail', got '{email_name}'"
        if widget_name != "الويدجت":
            return False, f"Expected 'الويدجت', got '{widget_name}'"
        
        # Test tag color mapping
        email_color = FeedbackChannel.get_tag_color(FeedbackChannel.EMAIL)
        widget_color = FeedbackChannel.get_tag_color(FeedbackChannel.WIDGET)
        
        if email_color != "success":
            return False, f"Expected 'success', got '{email_color}'"
        if widget_color != "warning":
            return False, f"Expected 'warning', got '{widget_color}'"
            
        return True, "Channel enum methods working correctly"
    except Exception as e:
        return False, f"Error testing enum methods: {e}"

def test_survey_responses_route():
    """Test that survey responses route loads correctly"""
    try:
        with app.test_client() as client:
            response = client.get('/surveys/responses')
            
            if response.status_code != 200:
                return False, f"Route returned {response.status_code} instead of 200"
            
            response_data = response.get_data(as_text=True)
            
            # Check for essential UI elements
            required_elements = [
                'توزيع المصادر النشطة',  # Channel breakdown
                'جميع المصادر',  # All sources filter
                'تطبيق الفلتر'  # Apply filter button
            ]
            
            for element in required_elements:
                if element not in response_data:
                    return False, f"Missing UI element: {element}"
            
            return True, "Survey responses route working correctly"
            
    except Exception as e:
        return False, f"Error testing route: {e}"

def test_channel_filtering():
    """Test channel filtering with URL parameters"""
    try:
        with app.test_client() as client:
            # Test all channels filter
            response = client.get('/surveys/responses?channel=all')
            if response.status_code != 200:
                return False, f"All channels filter failed with {response.status_code}"
            
            # Test email filter
            response = client.get('/surveys/responses?channel=email')
            if response.status_code != 200:
                return False, f"Email filter failed with {response.status_code}"
            
            # Test widget filter
            response = client.get('/surveys/responses?channel=widget')
            if response.status_code != 200:
                return False, f"Widget filter failed with {response.status_code}"
            
            # Test invalid filter (should not crash)
            response = client.get('/surveys/responses?channel=invalid')
            if response.status_code != 200:
                return False, f"Invalid filter crashed with {response.status_code}"
            
            return True, "Channel filtering working correctly"
            
    except Exception as e:
        return False, f"Error testing filtering: {e}"

def test_database_feedback_structure():
    """Test that feedback data has proper channel metadata"""
    try:
        with app.app_context():
            # Count feedback by channel
            email_count = db.session.query(Feedback).filter_by(channel=FeedbackChannel.EMAIL).count()
            widget_count = db.session.query(Feedback).filter_by(channel=FeedbackChannel.WIDGET).count()
            
            # Check that we have some feedback data
            total_feedback = email_count + widget_count
            if total_feedback == 0:
                return False, "No feedback data found in database"
            
            # Check metadata structure on sample feedback
            sample_feedback = db.session.query(Feedback).filter(
                Feedback.channel_metadata.isnot(None)
            ).first()
            
            if sample_feedback and sample_feedback.channel_metadata:
                if not isinstance(sample_feedback.channel_metadata, dict):
                    return False, "Channel metadata is not a dict"
                if 'source_type' not in sample_feedback.channel_metadata:
                    return False, "Channel metadata missing source_type"
            
            # Count feedback with proper metadata
            metadata_count = 0
            for feedback in db.session.query(Feedback).filter(
                Feedback.channel.in_([FeedbackChannel.EMAIL, FeedbackChannel.WIDGET])
            ).all():
                if (feedback.channel_metadata and 
                    isinstance(feedback.channel_metadata, dict) and
                    'source_type' in feedback.channel_metadata):
                    metadata_count += 1
            
            if metadata_count == 0 and total_feedback > 0:
                return False, "No feedback found with proper source_type metadata"
            
            return True, f"Database structure valid - {email_count} email, {widget_count} widget responses"
            
    except Exception as e:
        return False, f"Error testing database: {e}"

def test_javascript_integration():
    """Test that JavaScript filtering code is present"""
    try:
        with app.test_client() as client:
            response = client.get('/surveys/responses')
            response_data = response.get_data(as_text=True)
            
            js_elements = [
                'handleChannelFilter',
                'channelFilter',
                'addEventListener'
            ]
            
            for element in js_elements:
                if element not in response_data:
                    return False, f"Missing JavaScript element: {element}"
            
            return True, "JavaScript integration working correctly"
            
    except Exception as e:
        return False, f"Error testing JavaScript: {e}"

def run_simple_tests():
    """Run all simplified tests and return results"""
    tests = [
        ("Channel Enum Functionality", test_channel_enum_functionality),
        ("Survey Responses Route", test_survey_responses_route),
        ("Channel Filtering", test_channel_filtering),
        ("Database Structure", test_database_feedback_structure),
        ("JavaScript Integration", test_javascript_integration)
    ]
    
    results = []
    passed = 0
    failed = 0
    
    print("🧪 SIMPLIFIED CHANNEL TESTING FRAMEWORK")
    print("=" * 50)
    
    for test_name, test_function in tests:
        try:
            success, message = test_function()
            if success:
                print(f"✅ {test_name}: {message}")
                passed += 1
            else:
                print(f"❌ {test_name}: {message}")
                failed += 1
                
            results.append({
                'test': test_name,
                'status': 'PASSED' if success else 'FAILED',
                'message': message
            })
        except Exception as e:
            print(f"💥 {test_name}: Unexpected error - {e}")
            failed += 1
            results.append({
                'test': test_name,
                'status': 'ERROR',
                'message': str(e)
            })
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTS: {passed} passed, {failed} failed")
    print(f"🎯 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("✅ All channel functionality working correctly!")
        print("✅ System ready for production use.")
    else:
        print("⚠️  Some tests failed - review the issues above")
    
    return {
        'passed': passed,
        'failed': failed,
        'results': results,
        'success_rate': (passed/(passed+failed)*100) if (passed+failed) > 0 else 0
    }

if __name__ == "__main__":
    run_simple_tests()