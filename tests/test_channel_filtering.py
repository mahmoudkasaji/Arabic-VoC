"""
Channel Filtering and Metadata Testing Framework
Tests channel tagging, filtering, and data synchronization
"""

import json
from datetime import datetime, timedelta
from flask import url_for
from app import app, db
from models_unified import Feedback, FeedbackChannel, FeedbackStatus
from flask_login import login_user

class TestChannelFilteringSystem:
    """Test suite for channel filtering and metadata system"""
    
    def setup_test_data(self):
        """Create test feedback data with different channels and metadata"""
        # Clear existing feedback for clean tests
        db.session.query(Feedback).delete()
        
        # Create test feedback with different channels
        test_feedback = [
                # Gmail responses
                Feedback(
                    content="Great service via email!",
                    channel=FeedbackChannel.EMAIL,
                    rating=5,
                    status=FeedbackStatus.PROCESSED,
                    channel_metadata={
                        'source_type': 'GMAIL_DELIVERY',
                        'delivery_method': 'survey_link',
                        'email_campaign': 'customer_satisfaction'
                    },
                    created_at=datetime.utcnow() - timedelta(hours=2)
                ),
                Feedback(
                    content="Email survey was easy to complete",
                    channel=FeedbackChannel.EMAIL,
                    rating=4,
                    status=FeedbackStatus.PROCESSED,
                    channel_metadata={
                        'source_type': 'GMAIL_DELIVERY',
                        'delivery_method': 'survey_link',
                        'email_campaign': 'product_feedback'
                    },
                    created_at=datetime.utcnow() - timedelta(hours=1)
                ),
                
                # Sidebar widget responses
                Feedback(
                    content="Sidebar widget works great!",
                    channel=FeedbackChannel.WIDGET,
                    rating=5,
                    status=FeedbackStatus.PROCESSED,
                    channel_metadata={
                        'source_type': 'SIDEBAR_WIDGET',
                        'widget_version': '2.0',
                        'page_url': '/dashboard',
                        'widget_position': 'bottom-left'
                    },
                    created_at=datetime.utcnow() - timedelta(minutes=30)
                ),
                Feedback(
                    content="Widget could be improved",
                    channel=FeedbackChannel.WIDGET,
                    rating=3,
                    status=FeedbackStatus.PENDING,
                    channel_metadata={
                        'source_type': 'SIDEBAR_WIDGET',
                        'widget_version': '2.0',
                        'page_url': '/surveys',
                        'widget_position': 'bottom-left'
                    },
                    created_at=datetime.utcnow() - timedelta(minutes=15)
                ),
                
                # Footer widget responses
                Feedback(
                    content="Footer feedback is convenient",
                    channel=FeedbackChannel.WIDGET,
                    rating=4,
                    status=FeedbackStatus.PROCESSED,
                    channel_metadata={
                        'source_type': 'FOOTER_WIDGET',
                        'widget_version': '2.0',
                        'page_url': '/analytics',
                        'category': 'سهولة الاستخدام'
                    },
                    created_at=datetime.utcnow() - timedelta(minutes=5)
                )
            ]
            
        for feedback in test_feedback:
            db.session.add(feedback)
        
        db.session.commit()
    
    def cleanup_test_data(self):
        """Clean up test data after tests"""
        db.session.query(Feedback).delete()
        db.session.commit()
    
    def test_channel_enum_methods(self):
        """Test FeedbackChannel enum helper methods"""
        # Test Arabic name mapping
        if FeedbackChannel.get_arabic_name(FeedbackChannel.EMAIL) != "Gmail":
            raise AssertionError("EMAIL channel should map to 'Gmail'")
        if FeedbackChannel.get_arabic_name(FeedbackChannel.WIDGET) != "الويدجت":
            raise AssertionError("WIDGET channel should map to 'الويدجت'")
        
        # Test tag color mapping
        if FeedbackChannel.get_tag_color(FeedbackChannel.EMAIL) != "success":
            raise AssertionError("EMAIL channel should have 'success' color")
        if FeedbackChannel.get_tag_color(FeedbackChannel.WIDGET) != "warning":
            raise AssertionError("WIDGET channel should have 'warning' color")
    
    def test_channel_filtering_route_all_channels(self):
        """Test survey responses route with no filter (all channels)"""
        with app.test_client() as client:
            response = client.get('/surveys/responses')
            if response.status_code != 200:
                raise AssertionError(f"Expected 200, got {response.status_code}")
            
            # Should include all feedback from active channels
            response_data = response.get_data(as_text=True)
            if "Gmail" not in response_data:
                raise AssertionError("Gmail channel not found in response")
            if "الويدجت" not in response_data:
                raise AssertionError("Widget channel not found in response")
    
    def test_channel_filtering_route_email_only(self):
        """Test survey responses route filtering EMAIL channel only"""
        with app.test_client() as client:
            with app.app_context():
                response = client.get('/surveys/responses?channel=email')
                assert response.status_code == 200
                
                response_data = response.get_data(as_text=True)
                # Should only include email feedback
                assert "Great service via email!" in response_data
                assert "Email survey was easy" in response_data
                # Should not include widget feedback
                assert "Sidebar widget works great!" not in response_data
    
    def test_channel_filtering_route_widget_only(self):
        """Test survey responses route filtering WIDGET channel only"""
        with app.test_client() as client:
            with app.app_context():
                response = client.get('/surveys/responses?channel=widget')
                assert response.status_code == 200
                
                response_data = response.get_data(as_text=True)
                # Should only include widget feedback
                assert "Sidebar widget works great!" in response_data
                assert "Footer feedback is convenient" in response_data
                # Should not include email feedback
                assert "Great service via email!" not in response_data
    
    def test_date_range_filtering(self):
        """Test date range filtering functionality"""
        with app.test_client() as client:
            with app.app_context():
                today = datetime.utcnow().date()
                response = client.get(f'/surveys/responses?date_from={today}&date_to={today}')
                assert response.status_code == 200
                
                # Should only include today's feedback
                response_data = response.get_data(as_text=True)
                assert "Footer feedback is convenient" in response_data  # Recent
                # Older feedback should be filtered out
                assert "Great service via email!" not in response_data  # 2 hours ago
    
    def test_channel_metadata_structure(self):
        """Test channel metadata JSON structure and content"""
        with app.app_context():
            # Test EMAIL channel metadata
            email_feedback = db.session.query(Feedback).filter_by(
                channel=FeedbackChannel.EMAIL
            ).first()
            
            assert email_feedback.channel_metadata is not None
            assert email_feedback.channel_metadata['source_type'] == 'GMAIL_DELIVERY'
            assert 'delivery_method' in email_feedback.channel_metadata
            
            # Test WIDGET channel metadata
            widget_feedback = db.session.query(Feedback).filter(
                Feedback.channel == FeedbackChannel.WIDGET,
                Feedback.channel_metadata['source_type'].astext == 'SIDEBAR_WIDGET'
            ).first()
            
            assert widget_feedback.channel_metadata is not None
            assert widget_feedback.channel_metadata['source_type'] == 'SIDEBAR_WIDGET'
            assert 'widget_version' in widget_feedback.channel_metadata
            assert 'page_url' in widget_feedback.channel_metadata
    
    def test_analytics_channel_breakdown(self):
        """Test channel analytics calculations"""
        with app.app_context():
            from sqlalchemy import func
            
            # Test channel distribution query
            channel_stats = db.session.query(
                Feedback.channel,
                func.count(Feedback.id).label('count')
            ).filter(
                Feedback.channel.in_([FeedbackChannel.EMAIL, FeedbackChannel.WIDGET])
            ).group_by(Feedback.channel).all()
            
            channel_counts = {stat.channel: stat.count for stat in channel_stats}
            
            assert channel_counts[FeedbackChannel.EMAIL] == 2  # 2 email responses
            assert channel_counts[FeedbackChannel.WIDGET] == 3  # 3 widget responses
    
    def test_channel_filter_options_generation(self):
        """Test available channel options for UI filters"""
        with app.test_client() as client:
            with app.app_context():
                response = client.get('/surveys/responses')
                response_data = response.get_data(as_text=True)
                
                # Check filter options are present
                assert 'جميع المصادر' in response_data  # All sources
                assert 'Gmail' in response_data  # Email filter
                assert 'الويدجت' in response_data  # Widget filter
                
                # Check filter counts (should show numbers)
                assert '(2)' in response_data  # Email count
                assert '(3)' in response_data  # Widget count

def run_channel_filtering_tests():
    """Run all channel filtering tests and return results"""
    results = {
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'test_results': []
    }
    
    test_instance = TestChannelFilteringSystem()
    
    # Get all test methods
    test_methods = [method for method in dir(test_instance) 
                   if method.startswith('test_') and callable(getattr(test_instance, method))]
    
    results['total_tests'] = len(test_methods)
    
    with app.app_context():
        # Setup test data
        test_instance.setup_test_data()
        
        try:
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
        finally:
            # Always cleanup
            test_instance.cleanup_test_data()
    
    return results

if __name__ == "__main__":
    # Run tests when script is executed directly
    test_results = run_channel_filtering_tests()
    
    print(f"\n=== Channel Filtering Test Results ===")
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