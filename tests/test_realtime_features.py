"""
Tests for real-time features and WebSocket functionality
Validates real-time updates and performance targets
"""

import pytest
import time
import json
from app import app

class TestRealTimeUpdates:
    """Test real-time data updates"""
    
    def setup_method(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        self.app_context.pop()
    
    @pytest.mark.performance
    def test_real_time_dashboard_refresh(self):
        """Test dashboard real-time refresh capability"""
        # Get initial metrics
        response1 = self.client.get('/api/executive-dashboard/metrics')
        assert response1.status_code == 200
        data1 = response1.get_json()
        initial_timestamp = data1.get('timestamp')
        
        # Wait a moment and get updated metrics
        time.sleep(0.1)
        response2 = self.client.get('/api/executive-dashboard/metrics')
        assert response2.status_code == 200
        data2 = response2.get_json()
        updated_timestamp = data2.get('timestamp')
        
        # Timestamps should be different (real-time updates)
        assert initial_timestamp != updated_timestamp
    
    @pytest.mark.performance
    def test_feedback_to_dashboard_latency(self):
        """Test latency from feedback submission to dashboard update"""
        # Submit feedback
        start_time = time.time()
        feedback_response = self.client.post('/api/feedback/submit', 
                                           json={
                                               'content': 'اختبار التحديث الفوري',
                                               'channel': 'realtime_test',
                                               'rating': 5
                                           })
        submit_time = time.time() - start_time
        assert feedback_response.status_code == 200
        
        # Check dashboard reflects the change
        dashboard_start = time.time()
        dashboard_response = self.client.get('/api/executive-dashboard/metrics')
        dashboard_time = time.time() - dashboard_start
        assert dashboard_response.status_code == 200
        
        total_latency = submit_time + dashboard_time
        assert total_latency < 0.2, f"Real-time latency {total_latency:.3f}s exceeds 200ms target"
    
    def test_concurrent_real_time_updates(self):
        """Test real-time updates with concurrent users"""
        from concurrent.futures import ThreadPoolExecutor
        import threading
        
        def submit_and_check():
            # Submit feedback
            response = self.client.post('/api/feedback/submit', 
                                      json={
                                          'content': f'تحديث متزامن {threading.current_thread().ident}',
                                          'channel': 'concurrent_test',
                                          'rating': 4
                                      })
            return response.status_code == 200
        
        # Test with 5 concurrent submissions
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(submit_and_check) for _ in range(5)]
            results = [future.result() for future in futures]
        
        # All submissions should succeed
        success_rate = sum(results) / len(results)
        assert success_rate >= 0.8, f"Concurrent submission success rate {success_rate:.2f} too low"


class TestAutoRefreshMechanism:
    """Test automatic refresh mechanism"""
    
    def setup_method(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        self.app_context.pop()
    
    def test_dashboard_auto_refresh_javascript(self):
        """Test dashboard auto-refresh JavaScript is present"""
        response = self.client.get('/analytics/executive')
        content = response.data.decode('utf-8')
        
        # Check for auto-refresh related JavaScript
        assert 'setInterval' in content or 'refresh' in content.lower()
        assert '30000' in content or '30 seconds' in content.lower()  # 30 second refresh
    
    @pytest.mark.performance
    def test_auto_refresh_performance(self):
        """Test auto-refresh mechanism performance"""
        refresh_times = []
        
        # Simulate multiple auto-refreshes
        for _ in range(5):
            start_time = time.time()
            response = self.client.get('/api/executive-dashboard/metrics')
            refresh_time = time.time() - start_time
            refresh_times.append(refresh_time)
            
            assert response.status_code == 200
            time.sleep(0.1)  # Small delay between refreshes
        
        avg_refresh_time = sum(refresh_times) / len(refresh_times)
        max_refresh_time = max(refresh_times)
        
        assert avg_refresh_time < 0.3, f"Average auto-refresh time {avg_refresh_time:.3f}s too slow"
        assert max_refresh_time < 0.5, f"Maximum auto-refresh time {max_refresh_time:.3f}s too slow"


class TestDataStreamingPerformance:
    """Test data streaming and update performance"""
    
    def setup_method(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        self.app_context.pop()
    
    @pytest.mark.performance
    def test_high_frequency_updates(self):
        """Test system performance with high frequency updates"""
        update_times = []
        
        # Submit feedback rapidly and measure update times
        for i in range(10):
            start_time = time.time()
            
            # Submit feedback
            self.client.post('/api/feedback/submit', 
                           json={
                               'content': f'تحديث سريع {i}',
                               'channel': 'high_frequency_test',
                               'rating': (i % 5) + 1
                           })
            
            # Get updated metrics
            self.client.get('/api/executive-dashboard/metrics')
            
            update_time = time.time() - start_time
            update_times.append(update_time)
        
        avg_update_time = sum(update_times) / len(update_times)
        assert avg_update_time < 0.5, f"High frequency update time {avg_update_time:.3f}s too slow"
    
    @pytest.mark.performance
    def test_data_consistency_under_load(self):
        """Test data consistency during high load"""
        from concurrent.futures import ThreadPoolExecutor
        
        def submit_feedback_batch(batch_id):
            """Submit a batch of feedback"""
            success_count = 0
            for i in range(5):
                response = self.client.post('/api/feedback/submit', 
                                          json={
                                              'content': f'تحديث مجمع {batch_id}-{i}',
                                              'channel': 'batch_test',
                                              'rating': 4
                                          })
                if response.status_code == 200:
                    success_count += 1
            return success_count
        
        # Submit multiple batches concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(submit_feedback_batch, i) for i in range(3)]
            results = [future.result() for future in futures]
        
        total_successful = sum(results)
        total_expected = 3 * 5  # 3 batches * 5 feedbacks each
        
        success_rate = total_successful / total_expected
        assert success_rate >= 0.9, f"Data consistency under load: {success_rate:.2f} success rate"
        
        # Verify dashboard still responds correctly after load
        response = self.client.get('/api/executive-dashboard/metrics')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['volume']['total'] >= total_successful


class TestMemoryEfficiencyRealTime:
    """Test memory efficiency for real-time operations"""
    
    def setup_method(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        self.app_context.pop()
    
    @pytest.mark.performance
    def test_memory_usage_during_streaming(self):
        """Test memory usage remains stable during real-time streaming"""
        import psutil
        import gc
        
        # Get baseline memory
        gc.collect()
        process = psutil.Process()
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Simulate continuous real-time updates
        for i in range(50):
            # Submit feedback
            self.client.post('/api/feedback/submit', 
                           json={
                               'content': f'اختبار الذاكرة المستمر {i}',
                               'channel': 'memory_test',
                               'rating': (i % 5) + 1
                           })
            
            # Get dashboard update
            self.client.get('/api/executive-dashboard/metrics')
            
            # Check memory every 10 iterations
            if i % 10 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_increase = current_memory - baseline_memory
                assert memory_increase < 50, f"Memory increase {memory_increase:.1f}MB too high at iteration {i}"
        
        # Final memory check
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024
        total_increase = final_memory - baseline_memory
        assert total_increase < 30, f"Total memory increase {total_increase:.1f}MB too high"