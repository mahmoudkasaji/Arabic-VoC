"""
Consolidated Testing Utilities
Combines functionality from test_data_generator.py, sample_data.py, and dashboard_demo_data.py
"""

import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from faker import Faker
import logging

logger = logging.getLogger(__name__)

# Initialize Faker with Arabic locale
fake = Faker(['ar_SA', 'en_US'])

class TestDataGenerator:
    """Unified test data generation for all platform components"""
    
    def __init__(self):
        self.arabic_companies = [
            'شركة الابتكار التقني', 'مؤسسة الخليج للتطوير', 'شركة النور للتكنولوجيا',
            'مجموعة الشرق الأوسط', 'شركة الأمل للحلول الذكية', 'مؤسسة البحرين التجارية'
        ]
        
        self.arabic_feedback_samples = [
            'الخدمة ممتازة والفريق محترف جداً، أنصح بالتعامل معهم',
            'التطبيق سهل الاستخدام ولكن يحتاج تحسين في السرعة',
            'دعم العملاء رائع ومتجاوب، حل مشكلتي بسرعة',
            'المنتج جيد بشكل عام ولكن الواجهة معقدة قليلاً',
            'تجربة مميزة وخدمة عملاء على أعلى مستوى',
            'يحتاج المنتج إلى تطوير أكثر في الخصائص الأساسية'
        ]
        
        self.english_feedback_samples = [
            'Excellent service and very professional team',
            'Easy to use but needs improvement in speed',
            'Great customer support, very responsive',
            'Good product overall but interface is complex',
            'Outstanding experience and top-level service',
            'Product needs more development in core features'
        ]
        
        self.sentiment_labels = ['positive', 'neutral', 'negative']
        self.channels = ['website', 'email', 'sms', 'whatsapp', 'phone', 'social_media']
    
    def generate_demo_dashboard_data(self) -> Dict[str, Any]:
        """Generate comprehensive demo dashboard data"""
        return {
            "overview_metrics": self._generate_overview_metrics(),
            "sentiment_analysis": self._generate_sentiment_data(),
            "channel_performance": self._generate_channel_data(),
            "recent_feedback": self._generate_recent_feedback(),
            "trends": self._generate_trend_data(),
            "geographic_data": self._generate_geographic_data()
        }
    
    def generate_sample_contacts(self, count: int = 50) -> List[Dict[str, Any]]:
        """Generate sample contact data"""
        contacts = []
        
        for _ in range(count):
            # Mix of Arabic and English names
            use_arabic = random.choice([True, False])
            
            if use_arabic:
                name = fake.name_male() if random.choice([True, False]) else fake.name_female()
                company = random.choice(self.arabic_companies)
            else:
                name = fake.name()
                company = fake.company()
            
            contact = {
                "name": name,
                "email": fake.email(),
                "phone": fake.phone_number(),
                "company": company,
                "language_preference": "ar" if use_arabic else "en",
                "tags": random.sample(['VIP', 'New', 'Premium', 'Support', 'Sales'], 
                                    random.randint(1, 3)),
                "email_opt_in": random.choice([True, True, True, False]),  # 75% opt-in
                "sms_opt_in": random.choice([True, True, False]),  # 66% opt-in
                "whatsapp_opt_in": random.choice([True, True, True, False]),  # 75% opt-in
                "created_at": fake.date_time_between(start_date='-1y', end_date='now'),
                "is_active": random.choice([True, True, True, True, False]),  # 80% active
                "notes": fake.text(max_nb_chars=100) if random.choice([True, False]) else None
            }
            
            contacts.append(contact)
        
        return contacts
    
    def generate_sample_feedback(self, count: int = 100) -> List[Dict[str, Any]]:
        """Generate sample feedback entries"""
        feedback_entries = []
        
        for _ in range(count):
            # Choose language and corresponding feedback
            use_arabic = random.choice([True, False])
            
            if use_arabic:
                content = random.choice(self.arabic_feedback_samples)
                language = "ar"
            else:
                content = random.choice(self.english_feedback_samples)
                language = "en"
            
            # Generate sentiment based on content keywords
            sentiment_score = self._calculate_demo_sentiment(content)
            
            feedback = {
                "content": content,
                "language": language,
                "channel": random.choice(self.channels),
                "sentiment_score": sentiment_score,
                "sentiment_label": self._score_to_label(sentiment_score),
                "confidence_score": random.uniform(0.7, 0.95),
                "customer_email": fake.email() if random.choice([True, False]) else None,
                "customer_name": fake.name() if random.choice([True, False]) else None,
                "created_at": fake.date_time_between(start_date='-3m', end_date='now'),
                "status": random.choice(['new', 'reviewed', 'responded', 'closed']),
                "priority": random.choice(['low', 'medium', 'high']),
                "tags": random.sample(['bug', 'feature', 'praise', 'complaint', 'question'], 
                                    random.randint(0, 2))
            }
            
            feedback_entries.append(feedback)
        
        return feedback_entries
    
    def generate_survey_data(self, count: int = 20) -> List[Dict[str, Any]]:
        """Generate sample survey data"""
        surveys = []
        
        for i in range(count):
            survey = {
                "title": f"استبيان رضا العملاء {i+1}" if random.choice([True, False]) 
                        else f"Customer Satisfaction Survey {i+1}",
                "description": "استبيان لقياس مستوى رضا العملاء عن خدماتنا" 
                             if random.choice([True, False])
                             else "Survey to measure customer satisfaction with our services",
                "status": random.choice(['draft', 'active', 'paused', 'completed']),
                "language": random.choice(['ar', 'en', 'both']),
                "created_at": fake.date_time_between(start_date='-6m', end_date='now'),
                "response_count": random.randint(10, 500),
                "completion_rate": random.uniform(0.6, 0.95),
                "avg_completion_time": random.randint(120, 600),  # seconds
                "questions_count": random.randint(5, 15),
                "channels": random.sample(self.channels, random.randint(2, 4))
            }
            
            surveys.append(survey)
        
        return surveys
    
    def _generate_overview_metrics(self) -> Dict[str, Any]:
        """Generate overview metrics for dashboard"""
        return {
            "total_feedback": random.randint(1000, 5000),
            "total_surveys": random.randint(15, 50),
            "active_contacts": random.randint(500, 2000),
            "avg_sentiment": round(random.uniform(0.6, 0.8), 2),
            "response_rate": round(random.uniform(0.7, 0.9), 2),
            "completion_rate": round(random.uniform(0.75, 0.95), 2)
        }
    
    def _generate_sentiment_data(self) -> Dict[str, Any]:
        """Generate sentiment analysis data"""
        total = 100
        positive = random.randint(60, 80)
        negative = random.randint(5, 15)
        neutral = total - positive - negative
        
        return {
            "distribution": {
                "positive": positive,
                "neutral": neutral,
                "negative": negative
            },
            "trend": random.choice(['improving', 'stable', 'declining']),
            "average_score": round(random.uniform(0.6, 0.8), 2),
            "confidence": round(random.uniform(0.8, 0.95), 2)
        }
    
    def _generate_channel_data(self) -> Dict[str, Any]:
        """Generate channel performance data"""
        channels = {}
        
        for channel in self.channels:
            channels[channel] = {
                "volume": random.randint(50, 500),
                "sentiment": round(random.uniform(0.5, 0.8), 2),
                "response_rate": round(random.uniform(0.6, 0.9), 2),
                "avg_resolution_time": random.randint(30, 300)  # minutes
            }
        
        return channels
    
    def _generate_recent_feedback(self) -> List[Dict[str, Any]]:
        """Generate recent feedback entries for dashboard"""
        return self.generate_sample_feedback(10)
    
    def _generate_trend_data(self) -> Dict[str, Any]:
        """Generate trend data for charts"""
        days = []
        sentiment_scores = []
        volume_data = []
        
        for i in range(30):  # Last 30 days
            date = datetime.now() - timedelta(days=i)
            days.append(date.strftime('%Y-%m-%d'))
            sentiment_scores.append(round(random.uniform(0.5, 0.8), 2))
            volume_data.append(random.randint(10, 100))
        
        return {
            "sentiment_trend": {
                "dates": list(reversed(days)),
                "scores": list(reversed(sentiment_scores))
            },
            "volume_trend": {
                "dates": list(reversed(days)),
                "volumes": list(reversed(volume_data))
            }
        }
    
    def _generate_geographic_data(self) -> Dict[str, Any]:
        """Generate geographic distribution data"""
        countries = ['Saudi Arabia', 'UAE', 'Kuwait', 'Qatar', 'Bahrain', 'Jordan', 'Lebanon']
        
        geographic_data = {}
        for country in countries:
            geographic_data[country] = {
                "count": random.randint(10, 200),
                "avg_sentiment": round(random.uniform(0.5, 0.8), 2)
            }
        
        return geographic_data
    
    def _calculate_demo_sentiment(self, text: str) -> float:
        """Calculate demo sentiment based on text content"""
        positive_words = ['ممتاز', 'رائع', 'جيد', 'excellent', 'great', 'good', 'amazing']
        negative_words = ['سيء', 'صعب', 'مشكلة', 'bad', 'difficult', 'problem', 'issue']
        
        positive_count = sum(1 for word in positive_words if word.lower() in text.lower())
        negative_count = sum(1 for word in negative_words if word.lower() in text.lower())
        
        if positive_count > negative_count:
            return round(random.uniform(0.6, 0.9), 2)
        elif negative_count > positive_count:
            return round(random.uniform(-0.9, -0.3), 2)
        else:
            return round(random.uniform(-0.2, 0.2), 2)
    
    def _score_to_label(self, score: float) -> str:
        """Convert sentiment score to label"""
        if score > 0.3:
            return "positive"
        elif score < -0.3:
            return "negative"
        else:
            return "neutral"
    
    def generate_performance_test_data(self) -> Dict[str, Any]:
        """Generate data for performance testing"""
        return {
            "large_feedback_batch": self.generate_sample_feedback(1000),
            "large_contact_batch": self.generate_sample_contacts(500),
            "stress_test_surveys": self.generate_survey_data(100)
        }

# Singleton instance
test_data_generator = TestDataGenerator()