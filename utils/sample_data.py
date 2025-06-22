"""
Sample data generator for Executive Dashboard development and testing
Creates realistic Arabic feedback data for demonstration purposes
"""

from datetime import datetime, timedelta
import random
from models_unified import Feedback, FeedbackChannel, FeedbackStatus
from utils.database import get_db_session
import logging

logger = logging.getLogger(__name__)

# Sample Arabic feedback texts with sentiment indicators
SAMPLE_FEEDBACK = [
    # Positive feedback
    ("الخدمة ممتازة والموظفون متعاونون جداً، أنصح بالتعامل معكم", 0.8, 0.9),
    ("تجربة رائعة ومنتجات عالية الجودة، شكراً لكم", 0.7, 0.85),
    ("خدمة العملاء مميزة والاستجابة سريعة", 0.75, 0.88),
    ("راضي جداً عن المنتج والخدمة المقدمة", 0.6, 0.82),
    ("تطبيق سهل الاستخدام وفعال", 0.65, 0.8),
    
    # Neutral feedback
    ("الخدمة عادية ولكن يمكن تحسينها", 0.1, 0.7),
    ("المنتج جيد ولكن السعر مرتفع قليلاً", 0.05, 0.75),
    ("الخدمة مقبولة ولكن الانتظار طويل", -0.05, 0.72),
    ("التطبيق يعمل بشكل طبيعي", 0.0, 0.8),
    
    # Negative feedback
    ("الخدمة بطيئة جداً وغير مرضية", -0.6, 0.85),
    ("المنتج لا يلبي التوقعات والجودة ضعيفة", -0.7, 0.9),
    ("صعوبة في التواصل مع خدمة العملاء", -0.5, 0.8),
    ("التطبيق يواجه مشاكل تقنية كثيرة", -0.65, 0.88),
    ("السعر لا يتناسب مع الجودة المقدمة", -0.4, 0.75)
]

def generate_sample_feedback(days_back=30, count_per_day=10):
    """
    Generate sample feedback data for testing the executive dashboard
    """
    from app import app, db
    try:
        with app.app_context():
            end_date = datetime.utcnow()
            
            for day in range(days_back):
                current_date = end_date - timedelta(days=day)
                
                # Vary the count per day to simulate realistic patterns
                daily_count = random.randint(max(1, count_per_day - 5), count_per_day + 5)
                
                for _ in range(daily_count):
                    # Select random feedback
                    content, sentiment, confidence = random.choice(SAMPLE_FEEDBACK)
                    
                    # Add some variation to sentiment and confidence
                    sentiment += random.uniform(-0.1, 0.1)
                    confidence += random.uniform(-0.05, 0.05)
                    
                    # Ensure bounds
                    sentiment = max(-1.0, min(1.0, sentiment))
                    confidence = max(0.0, min(1.0, confidence))
                    
                    # Random channel
                    channel = random.choice(list(FeedbackChannel))
                    
                    # Create timestamp within the day
                    hour = random.randint(8, 20)  # Business hours
                    minute = random.randint(0, 59)
                    timestamp = current_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    
                    # Create feedback record
                    feedback = Feedback(
                        content=content,
                        processed_content=content,  # In real system, this would be processed
                        channel=channel,
                        status=FeedbackStatus.PROCESSED,
                        customer_email=f"customer{random.randint(1000, 9999)}@example.com",
                        sentiment_score=sentiment,
                        confidence_score=confidence,
                        ai_summary=f"ملخص: {content[:50]}...",
                        ai_categories=["خدمة العملاء", "جودة المنتج"],
                        created_at=timestamp,
                        processed_at=timestamp + timedelta(minutes=random.randint(1, 30)),
                        language_detected="ar",
                        region="SA"
                    )
                    
                    db.session.add(feedback)
            
            db.session.commit()
            logger.info(f"Generated {days_back * count_per_day} sample feedback records")
            
    except Exception as e:
        logger.error(f"Error generating sample data: {e}")
        raise

def clear_sample_data():
    """
    Clear all feedback data (use with caution!)
    """
    from app import app, db
    try:
        with app.app_context():
            db.session.query(Feedback).delete()
            db.session.commit()
            logger.info("Cleared all feedback data")
            
    except Exception as e:
        logger.error(f"Error clearing sample data: {e}")
        raise

if __name__ == "__main__":
    # Generate sample data for testing
    generate_sample_feedback(days_back=30, count_per_day=15)
    print("Sample data generated successfully!")