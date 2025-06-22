"""
Quick dashboard demo data generator for immediate testing
Creates focused data for specific dashboard scenarios
"""

from datetime import datetime, timedelta
import random
from models_unified import Feedback, FeedbackChannel, FeedbackStatus
from app import app, db
import logging

logger = logging.getLogger(__name__)

def create_demo_scenarios():
    """Create specific scenarios for dashboard demonstration"""
    
    scenarios = [
        create_improvement_trend(),
        create_channel_performance_comparison(),
        create_sentiment_variations(),
        create_recent_activity_spike()
    ]
    
    with app.app_context():
        try:
            # Clear existing data
            db.session.query(Feedback).delete()
            
            total_created = 0
            for scenario_data in scenarios:
                for feedback in scenario_data:
                    db.session.add(feedback)
                    total_created += 1
            
            db.session.commit()
            logger.info(f"Created {total_created} demo feedback records")
            return total_created
            
        except Exception as e:
            logger.error(f"Error creating demo data: {e}")
            db.session.rollback()
            raise

def create_improvement_trend():
    """Create data showing improvement over time"""
    feedbacks = []
    base_date = datetime.utcnow() - timedelta(days=30)
    
    for day in range(30):
        current_date = base_date + timedelta(days=day)
        
        # Gradually improving sentiment
        sentiment_trend = -0.3 + (day * 0.025)  # From -0.3 to 0.45
        
        daily_count = random.randint(8, 15)
        for _ in range(daily_count):
            sentiment = sentiment_trend + random.uniform(-0.15, 0.15)
            sentiment = max(-1.0, min(1.0, sentiment))
            
            feedback = create_feedback_entry(
                date=current_date,
                sentiment=sentiment,
                channel=random.choice(list(FeedbackChannel)),
                content=select_content_by_sentiment(sentiment)
            )
            feedbacks.append(feedback)
    
    return feedbacks

def create_channel_performance_comparison():
    """Create data highlighting channel performance differences"""
    feedbacks = []
    base_date = datetime.utcnow() - timedelta(days=7)
    
    channel_performance = {
        FeedbackChannel.WHATSAPP: 0.65,      # Best performing
        FeedbackChannel.PHONE: 0.45,         # Good
        FeedbackChannel.EMAIL: 0.25,         # Average  
        FeedbackChannel.WEBSITE: 0.05,       # Needs improvement
        FeedbackChannel.SOCIAL_MEDIA: -0.15  # Poor performing
    }
    
    for channel, avg_sentiment in channel_performance.items():
        # Create 40-60 feedback entries per channel
        count = random.randint(40, 60)
        for _ in range(count):
            sentiment = avg_sentiment + random.uniform(-0.25, 0.25)
            sentiment = max(-1.0, min(1.0, sentiment))
            
            # Distribute across last 7 days
            day_offset = random.randint(0, 6)
            feedback_date = base_date + timedelta(days=day_offset)
            
            feedback = create_feedback_entry(
                date=feedback_date,
                sentiment=sentiment,
                channel=channel,
                content=select_content_by_sentiment(sentiment)
            )
            feedbacks.append(feedback)
    
    return feedbacks

def create_sentiment_variations():
    """Create varied sentiment data for comprehensive analysis"""
    feedbacks = []
    base_date = datetime.utcnow() - timedelta(days=14)
    
    sentiment_patterns = [
        (0.8, 50),   # Highly positive
        (0.4, 80),   # Positive
        (0.0, 60),   # Neutral
        (-0.4, 40),  # Negative
        (-0.8, 20)   # Highly negative
    ]
    
    for base_sentiment, count in sentiment_patterns:
        for _ in range(count):
            sentiment = base_sentiment + random.uniform(-0.15, 0.15)
            sentiment = max(-1.0, min(1.0, sentiment))
            
            # Random date in last 14 days
            day_offset = random.randint(0, 13)
            feedback_date = base_date + timedelta(days=day_offset)
            
            feedback = create_feedback_entry(
                date=feedback_date,
                sentiment=sentiment,
                channel=random.choice(list(FeedbackChannel)),
                content=select_content_by_sentiment(sentiment)
            )
            feedbacks.append(feedback)
    
    return feedbacks

def create_recent_activity_spike():
    """Create recent high-volume activity for real-time testing"""
    feedbacks = []
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Heavy activity in last 24 hours
    for hour in range(24):
        feedback_time = today + timedelta(hours=hour)
        
        # Vary hourly volume (business hours higher)
        if 9 <= hour <= 17:
            hourly_count = random.randint(8, 15)
        elif 19 <= hour <= 22:
            hourly_count = random.randint(5, 10)
        else:
            hourly_count = random.randint(1, 4)
        
        for _ in range(hourly_count):
            minute_offset = random.randint(0, 59)
            exact_time = feedback_time + timedelta(minutes=minute_offset)
            
            sentiment = random.uniform(-0.6, 0.8)
            
            feedback = create_feedback_entry(
                date=exact_time,
                sentiment=sentiment,
                channel=random.choice(list(FeedbackChannel)),
                content=select_content_by_sentiment(sentiment)
            )
            feedbacks.append(feedback)
    
    return feedbacks

def create_feedback_entry(date, sentiment, channel, content):
    """Create a single feedback entry with realistic data"""
    
    confidence = random.uniform(0.75, 0.95)
    rating = convert_sentiment_to_rating(sentiment)
    
    # Processing time varies by channel
    processing_hours = {
        FeedbackChannel.PHONE: 0.5,
        FeedbackChannel.CHATBOT: 0.1,
        FeedbackChannel.WHATSAPP: 1,
        FeedbackChannel.SMS: 2,
        FeedbackChannel.EMAIL: 12,
        FeedbackChannel.WEBSITE: 8,
        FeedbackChannel.MOBILE_APP: 6,
        FeedbackChannel.SOCIAL_MEDIA: 4,
        FeedbackChannel.SURVEY: 24,
        FeedbackChannel.IN_PERSON: 1
    }.get(channel, 8)
    
    processed_at = date + timedelta(hours=processing_hours + random.uniform(-0.5, 0.5))
    
    return Feedback(
        content=content,
        processed_content=content,
        channel=channel,
        status=FeedbackStatus.PROCESSED,
        customer_email=f"demo{random.randint(1000, 9999)}@example.com" if random.random() < 0.7 else None,
        customer_phone=f"+966{random.randint(500000000, 599999999)}" if random.random() < 0.5 else None,
        customer_id=f"DEMO_{random.randint(10000, 99999)}",
        rating=rating,
        sentiment_score=sentiment,
        confidence_score=confidence,
        ai_summary=generate_summary_for_sentiment(sentiment),
        ai_categories=["خدمة العملاء", "جودة المنتج"],
        ai_action_items=generate_actions_for_sentiment(sentiment),
        channel_metadata={"demo": True, "source": channel.value},
        created_at=date,
        updated_at=processed_at,
        processed_at=processed_at,
        language_detected="ar",
        region=random.choice(["SA", "AE", "EG", "JO", "KW"])
    )

def select_content_by_sentiment(sentiment):
    """Select appropriate Arabic content based on sentiment score"""
    
    if sentiment > 0.6:
        options = [
            "خدمة ممتازة وفريق رائع، شكراً لكم",
            "تجربة استثنائية تفوق التوقعات",
            "منتج عالي الجودة وخدمة مميزة",
            "أفضل خدمة حصلت عليها، أنصح بها بشدة"
        ]
    elif sentiment > 0.2:
        options = [
            "خدمة جيدة بشكل عام مع إمكانية التحسين",
            "تجربة إيجابية، أتطلع للمزيد من التطوير",
            "منتج مفيد، يحتاج بعض التحسينات",
            "راضي عن الخدمة مع ملاحظات للتطوير"
        ]
    elif sentiment > -0.2:
        options = [
            "خدمة عادية، لا سيء ولا ممتاز",
            "تجربة متوسطة، يمكن أن تكون أفضل",
            "المنتج يؤدي الغرض المطلوب فقط",
            "لا يوجد شيء مميز أو سيء بشكل خاص"
        ]
    elif sentiment > -0.6:
        options = [
            "خدمة مخيبة للآمال، يجب التحسين",
            "مشاكل في الجودة والاستجابة",
            "لم تلبي الخدمة توقعاتي",
            "صعوبات في الاستخدام والدعم الفني"
        ]
    else:
        options = [
            "خدمة سيئة جداً، أسوأ تجربة",
            "منتج لا يعمل وخدمة عملاء فظيعة",
            "أريد استرداد أموالي، خدمة غير مقبولة",
            "لا أنصح أحد بالتعامل معكم"
        ]
    
    return random.choice(options)

def convert_sentiment_to_rating(sentiment):
    """Convert sentiment score to 1-5 rating"""
    if sentiment > 0.6:
        return random.choice([5, 5, 4])
    elif sentiment > 0.2:
        return random.choice([4, 4, 3])
    elif sentiment > -0.2:
        return random.choice([3, 3, 2, 4])
    elif sentiment > -0.6:
        return random.choice([2, 2, 1])
    else:
        return random.choice([1, 1, 2])

def generate_summary_for_sentiment(sentiment):
    """Generate AI summary based on sentiment"""
    if sentiment > 0.4:
        return "ملخص: تقييم إيجابي مع تقدير للخدمة المقدمة"
    elif sentiment > 0:
        return "ملخص: تجربة مرضية مع اقتراحات للتحسين"
    elif sentiment > -0.4:
        return "ملخص: تجربة متوسطة تحتاج متابعة"
    else:
        return "ملخص: شكوى تتطلب إجراء فوري"

def generate_actions_for_sentiment(sentiment):
    """Generate action items based on sentiment"""
    if sentiment > 0.4:
        return ["متابعة مع العميل", "استخدام كمثال إيجابي"]
    elif sentiment > 0:
        return ["مراجعة الاقتراحات", "تحسين النقاط المذكورة"]
    elif sentiment > -0.4:
        return ["متابعة حالة العميل", "تحليل المشكلة"]
    else:
        return ["اتصال فوري بالعميل", "حل المشكلة بأولوية عالية"]

if __name__ == "__main__":
    total = create_demo_scenarios()
    print(f"Demo data created: {total} feedback entries")
    print("Dashboard is now populated with realistic test data!")