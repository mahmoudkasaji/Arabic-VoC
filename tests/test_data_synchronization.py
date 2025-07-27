"""
Data Synchronization Testing Framework
Tests database consistency, route responses, and UI data binding
"""

import json
from datetime import datetime, timedelta
from flask import url_for
from app import app, db
from models_unified import Feedback, FeedbackChannel, FeedbackStatus

class TestDataSynchronization:
    """Test suite for data synchronization across database, routes, and UI"""
    
    def test_database_channel_consistency(self):
        """Test that database channels match enum definitions"""
        with app.app_context():
            # Get all unique channels from database
            db_channels = db.session.query(Feedback.channel).distinct().all()
            db_channel_values = [channel[0] for channel in db_channels]
            
            # Verify all database channels are valid enum values
            valid_channels = [channel.value for channel in FeedbackChannel]
            
            for db_channel in db_channel_values:
                assert db_channel in valid_channels, f"Database channel '{db_channel}' not in enum"
    
    def test_route_response_structure(self):
        """Test that survey responses route returns properly structured data"""
        with app.test_client() as client:
            with app.app_context():
                response = client.get('/surveys/responses')
                assert response.status_code == 200
                
                response_data = response.get_data(as_text=True)
                
                # Check essential UI elements are present
                required_elements = [
                    'توزيع المصادر النشطة',  # Channel breakdown title
                    'جميع المصادر',  # All sources filter
                    'من تاريخ',  # Date from label
                    'إلى تاريخ',  # Date to label
                    'تطبيق الفلتر',  # Apply filter button
                    'مسح الفلاتر'  # Clear filters button
                ]
                
                for element in required_elements:
                    assert element in response_data, f"Required UI element '{element}' missing"
    
    def test_metadata_json_integrity(self):
        """Test channel metadata JSON structure integrity"""
        with app.app_context():
            # Get all feedback with metadata
            feedback_with_metadata = db.session.query(Feedback).filter(
                Feedback.channel_metadata.isnot(None)
            ).all()
            
            for feedback in feedback_with_metadata:
                # Verify metadata is valid JSON
                assert isinstance(feedback.channel_metadata, dict), "Metadata should be dict"
                
                # Verify required metadata fields based on channel
                if feedback.channel == FeedbackChannel.EMAIL:
                    assert 'source_type' in feedback.channel_metadata
                    assert feedback.channel_metadata['source_type'] in ['GMAIL_DELIVERY']
                
                elif feedback.channel == FeedbackChannel.WIDGET:
                    assert 'source_type' in feedback.channel_metadata
                    assert feedback.channel_metadata['source_type'] in [
                        'SIDEBAR_WIDGET', 'FOOTER_WIDGET'
                    ]
                    assert 'widget_version' in feedback.channel_metadata
    
    def test_channel_filter_parameter_handling(self):
        """Test that route properly handles channel filter parameters"""
        with app.test_client() as client:
            with app.app_context():
                # Test valid channel filters
                valid_filters = ['all', 'email', 'widget']
                
                for filter_value in valid_filters:
                    response = client.get(f'/surveys/responses?channel={filter_value}')
                    assert response.status_code == 200, f"Filter '{filter_value}' failed"
                
                # Test invalid channel filter (should not crash)
                response = client.get('/surveys/responses?channel=invalid')
                assert response.status_code == 200, "Invalid filter should not crash"
    
    def test_date_filter_parameter_handling(self):
        """Test that route properly handles date filter parameters"""
        with app.test_client() as client:
            with app.app_context():
                today = datetime.utcnow().date()
                yesterday = today - timedelta(days=1)
                
                # Test valid date ranges
                response = client.get(f'/surveys/responses?date_from={yesterday}&date_to={today}')
                assert response.status_code == 200
                
                # Test invalid date formats (should not crash)
                response = client.get('/surveys/responses?date_from=invalid&date_to=also-invalid')
                assert response.status_code == 200
    
    def test_analytics_data_consistency(self):
        """Test that analytics calculations match actual data"""
        with app.app_context():
            from sqlalchemy import func, desc
            
            # Get actual feedback counts
            total_feedback = db.session.query(Feedback).filter(
                Feedback.channel.in_([FeedbackChannel.EMAIL, FeedbackChannel.WIDGET])
            ).count()
            
            # Get today's feedback
            today = datetime.now().date()
            today_start = datetime.combine(today, datetime.min.time())
            today_feedback = db.session.query(Feedback).filter(
                Feedback.created_at >= today_start,
                Feedback.channel.in_([FeedbackChannel.EMAIL, FeedbackChannel.WIDGET])
            ).count()
            
            # Test route analytics match actual counts
            with app.test_client() as client:
                response = client.get('/surveys/responses')
                response_data = response.get_data(as_text=True)
                
                # Analytics should reflect actual data
                assert str(total_feedback) in response_data or total_feedback == 0
                assert str(today_feedback) in response_data or today_feedback == 0
    
    def test_channel_tag_display_consistency(self):
        """Test that channel tags display correct information"""
        with app.app_context():
            # Create test feedback to verify display
            test_feedback = Feedback(
                content="Test feedback for display",
                channel=FeedbackChannel.WIDGET,
                channel_metadata={
                    'source_type': 'SIDEBAR_WIDGET',
                    'widget_version': '2.0'
                },
                status=FeedbackStatus.PROCESSED
            )
            
            db.session.add(test_feedback)
            db.session.commit()
            
            try:
                with app.test_client() as client:
                    response = client.get('/surveys/responses')
                    response_data = response.get_data(as_text=True)
                    
                    # Verify channel tag appears with correct styling
                    assert 'badge bg-warning' in response_data  # Widget color
                    assert 'الويدجت' in response_data  # Arabic name
                    
            finally:
                # Cleanup
                db.session.delete(test_feedback)
                db.session.commit()
    
    def test_javascript_filter_integration(self):
        """Test that JavaScript filter functionality is properly integrated"""
        with app.test_client() as client:
            with app.app_context():
                response = client.get('/surveys/responses')
                response_data = response.get_data(as_text=True)
                
                # Check JavaScript elements are present
                js_elements = [
                    'handleChannelFilter',  # Function name
                    'channelFilter',  # Radio button name
                    'hiddenChannelFilter',  # Hidden input ID
                    'addEventListener',  # Event handling
                    'window.location.href'  # URL update
                ]
                
                for element in js_elements:
                    assert element in response_data, f"JavaScript element '{element}' missing"

def run_data_sync_tests():
    """Run all data synchronization tests and return results"""
    results = {
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'test_results': []
    }
    
    test_instance = TestDataSynchronization()
    
    # Get all test methods
    test_methods = [method for method in dir(test_instance) 
                   if method.startswith('test_') and callable(getattr(test_instance, method))]
    
    results['total_tests'] = len(test_methods)
    
    for test_method in test_methods:
        try:
            method = getattr(test_instance, test_method)
            method()
            results['passed_tests'] += 1
            results['test_results'].append({
                'test': test_method,
                'status': 'PASSED',
                'message': 'Test completed successfully'
            })
        except Exception as e:
            results['failed_tests'] += 1
            results['test_results'].append({
                'test': test_method,
                'status': 'FAILED',
                'message': str(e)
            })
    
    return results

if __name__ == "__main__":
    # Run tests when script is executed directly
    test_results = run_data_sync_tests()
    
    print(f"\n=== Data Synchronization Test Results ===")
    print(f"Total Tests: {test_results['total_tests']}")
    print(f"Passed: {test_results['passed_tests']}")
    print(f"Failed: {test_results['failed_tests']}")
    print(f"Success Rate: {(test_results['passed_tests']/test_results['total_tests']*100):.1f}%")
    
    print(f"\n=== Individual Test Results ===")
    for result in test_results['test_results']:
        status_icon = "✅" if result['status'] == 'PASSED' else "❌"
        print(f"{status_icon} {result['test']}: {result['status']}")
        if result['status'] == 'FAILED':
            print(f"   Error: {result['message']}")