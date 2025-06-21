"""
Load testing script for Arabic VoC platform using Locust
Tests API endpoints under realistic load conditions
"""

from locust import HttpUser, task, between
import random
import json

class ArabicVoCUser(HttpUser):
    """Simulated user for Arabic VoC platform load testing"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Setup test data"""
        self.arabic_feedback_samples = [
            "الخدمة ممتازة جداً وأنصح بها بشدة",
            "المنتج سيء ولا أنصح بشرائه", 
            "التطبيق جيد لكن يحتاج تحسينات",
            "فريق الدعم سريع ومفيد جداً",
            "التسليم متأخر والجودة متوسطة",
            "أحب هذا المتجر وأتسوق منه دائماً",
            "الموقع الإلكتروني لا يعمل بشكل صحيح",
            "منتج رائع بسعر معقول جداً",
            "الخدمة بطيئة والموظفون غير مهتمين",
            "تجربة تسوق رائعة وسريعة",
        ]
        
        self.channels = [
            "website", "mobile_app", "email", "phone", 
            "social_media", "whatsapp", "sms", "survey"
        ]
        
        self.submitted_feedback_ids = []
    
    @task(10)
    def submit_feedback(self):
        """Submit Arabic feedback (most common operation)"""
        feedback_data = {
            "content": random.choice(self.arabic_feedback_samples),
            "channel": random.choice(self.channels),
            "rating": random.randint(1, 5),
            "customer_email": f"user{random.randint(1, 1000)}@example.com" if random.random() > 0.5 else None
        }
        
        with self.client.post(
            "/api/feedback/submit",
            json=feedback_data,
            headers={"Content-Type": "application/json"},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "id" in data:
                        self.submitted_feedback_ids.append(data["id"])
                        response.success()
                    else:
                        response.failure("No feedback ID in response")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(5)
    def list_feedback(self):
        """List feedback with various filters"""
        params = {}
        
        # Random filter combinations
        if random.random() > 0.7:
            params["channel"] = random.choice(self.channels)
        
        if random.random() > 0.8:
            params["limit"] = random.randint(5, 20)
        
        if random.random() > 0.9:
            params["min_sentiment"] = random.uniform(-1, 0)
        
        with self.client.get("/api/feedback/list", params=params, catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        response.success()
                    else:
                        response.failure("Response is not a list")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(3)
    def get_dashboard_metrics(self):
        """Get dashboard analytics metrics"""
        with self.client.get("/api/analytics/dashboard", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    required_fields = ["total_feedback", "processed_feedback", "average_sentiment"]
                    if all(field in data for field in required_fields):
                        response.success()
                    else:
                        response.failure("Missing required dashboard fields")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(2)
    def get_sentiment_metrics(self):
        """Get sentiment analysis metrics"""
        with self.client.get("/api/analytics/sentiment", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "average_sentiment" in data and "confidence_score" in data:
                        response.success()
                    else:
                        response.failure("Missing sentiment metrics")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def get_specific_feedback(self):
        """Get specific feedback by ID"""
        if self.submitted_feedback_ids:
            feedback_id = random.choice(self.submitted_feedback_ids)
            
            with self.client.get(f"/api/feedback/{feedback_id}", catch_response=True) as response:
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if "id" in data and "content" in data:
                            response.success()
                        else:
                            response.failure("Missing feedback fields")
                    except json.JSONDecodeError:
                        response.failure("Invalid JSON response")
                elif response.status_code == 404:
                    # Remove invalid ID
                    self.submitted_feedback_ids.remove(feedback_id)
                    response.success()  # 404 is acceptable
                else:
                    response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def health_check(self):
        """Health check endpoint"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("status") == "healthy":
                        response.success()
                    else:
                        response.failure("Unhealthy status")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def homepage(self):
        """Access homepage"""
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                if "منصة صوت العميل العربية" in response.text:
                    response.success()
                else:
                    response.failure("Arabic title not found")
            else:
                response.failure(f"Status code: {response.status_code}")

class HeavyLoadUser(HttpUser):
    """Heavy load user for stress testing"""
    
    wait_time = between(0.1, 0.5)  # Very short wait times
    
    def on_start(self):
        """Setup for heavy load testing"""
        self.arabic_texts = [
            "نص قصير",
            "نص متوسط الطول يحتوي على محتوى عربي",
            "نص طويل جداً يحتوي على محتوى عربي مفصل ومعقد " * 10,
            "🤔 نص مع إيموجي وأرقام ١٢٣٤٥",
            "Mixed Arabic والإنجليزية والأرقام 123",
        ]
    
    @task
    def rapid_feedback_submission(self):
        """Rapid feedback submission for stress testing"""
        feedback_data = {
            "content": random.choice(self.arabic_texts),
            "channel": random.choice(["website", "mobile_app", "email"]),
            "rating": random.randint(1, 5)
        }
        
        self.client.post("/api/feedback/submit", json=feedback_data)

class SecurityTestUser(HttpUser):
    """User for security testing scenarios"""
    
    wait_time = between(2, 5)
    
    def on_start(self):
        """Setup security test data"""
        self.malicious_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE feedback; --",
            "../../../etc/passwd",
            "{{7*7}}",
            "\x00\x01\x02",
            "A" * 10000,  # Very long input
        ]
    
    @task
    def test_malicious_input_handling(self):
        """Test handling of malicious inputs"""
        malicious_content = random.choice(self.malicious_inputs)
        
        feedback_data = {
            "content": malicious_content,
            "channel": "website"
        }
        
        with self.client.post(
            "/api/feedback/submit",
            json=feedback_data,
            catch_response=True
        ) as response:
            # Should either reject (422) or sanitize (200)
            if response.status_code in [200, 422]:
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")
    
    @task
    def test_rate_limiting(self):
        """Test rate limiting behavior"""
        # Make rapid requests to test rate limiting
        for i in range(5):
            self.client.post("/api/feedback/submit", json={
                "content": f"اختبار {i}",
                "channel": "website"
            })

if __name__ == "__main__":
    # Run locust programmatically for automated testing
    import subprocess
    import sys
    
    print("Starting Arabic VoC Platform Load Test...")
    print("Make sure the application is running on http://localhost:5000")
    
    # Basic load test
    cmd = [
        sys.executable, "-m", "locust",
        "-f", __file__,
        "--host", "http://localhost:5000",
        "--users", "10",
        "--spawn-rate", "2",
        "--run-time", "60s",
        "--headless",
        "--print-stats"
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Load test failed: {e}")
        sys.exit(1)
    
    print("Load test completed successfully!")