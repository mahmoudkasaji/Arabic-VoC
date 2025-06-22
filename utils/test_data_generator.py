"""
Comprehensive test data generator for Arabic VoC Dashboard
Creates realistic feedback data with temporal patterns and diverse scenarios
"""

from datetime import datetime, timedelta
import random
from models_unified import Feedback, FeedbackChannel, FeedbackStatus
from app import app, db
import logging

logger = logging.getLogger(__name__)

# Expanded Arabic feedback samples with varied sentiment patterns
ARABIC_FEEDBACK_SAMPLES = [
    # Highly Positive (0.7 to 0.9 sentiment)
    ("الخدمة رائعة جداً والموظفون أكثر من رائعين، أشكركم من كل قلبي", 0.85, 0.92),
    ("تجربة استثنائية! المنتج فاق كل توقعاتي بمراحل", 0.82, 0.89),
    ("خدمة عملاء ممتازة، استجابة سريعة وحلول فعالة", 0.78, 0.91),
    ("أفضل تطبيق استخدمته، سهل وسريع ومفيد جداً", 0.75, 0.88),
    ("شكراً لكم على الاهتمام والمتابعة المستمرة", 0.73, 0.86),
    ("منتج عالي الجودة بسعر ممتاز، أنصح الجميع به", 0.79, 0.90),
    ("التسليم سريع والتعامل راقي ومهني للغاية", 0.77, 0.87),
    
    # Positive (0.3 to 0.7 sentiment)
    ("الخدمة جيدة بشكل عام، يمكن تحسين بعض الأشياء", 0.45, 0.78),
    ("منتج مفيد، لكن يحتاج تطوير في بعض المميزات", 0.38, 0.75),
    ("التطبيق سهل الاستخدام، أتمنى إضافة مميزات أكثر", 0.42, 0.80),
    ("خدمة العملاء مساعدة، لكن الرد بطيء أحياناً", 0.35, 0.73),
    ("جودة المنتج مقبولة للسعر المدفوع", 0.48, 0.77),
    ("التجربة إيجابية عموماً، مع وجود نقاط للتحسين", 0.52, 0.82),
    
    # Neutral (-0.2 to 0.3 sentiment)
    ("الخدمة عادية، لا أستطيع القول أنها سيئة أو ممتازة", 0.05, 0.70),
    ("المنتج يؤدي الغرض المطلوب منه فقط", 0.08, 0.68),
    ("لا توجد مشاكل كبيرة، لكن لا يوجد شيء مميز أيضاً", 0.02, 0.72),
    ("خدمة عادية جداً، لا أتوقع أكثر من ذلك", -0.05, 0.75),
    ("التطبيق يعمل بشكل طبيعي، لا جديد", 0.12, 0.69),
    ("السعر مناسب، الجودة عادية", 0.15, 0.71),
    
    # Negative (-0.7 to -0.2 sentiment)
    ("الخدمة محبطة، انتظرت طويلاً دون حل مناسب", -0.48, 0.83),
    ("المنتج لا يستحق السعر المدفوع إطلاقاً", -0.52, 0.86),
    ("صعوبة في الاستخدام، التطبيق معقد جداً", -0.45, 0.79),
    ("خدمة العملاء غير مفيدة، ردود آلية فقط", -0.38, 0.81),
    ("جودة ضعيفة مقارنة بالمنافسين", -0.42, 0.84),
    ("التسليم متأخر والمنتج مختلف عن الوصف", -0.55, 0.87),
    
    # Highly Negative (-0.9 to -0.7 sentiment)
    ("خدمة سيئة جداً، أسوأ تجربة مررت بها", -0.82, 0.91),
    ("المنتج معطل تماماً، أريد استرداد أموالي", -0.85, 0.89),
    ("لا أنصح أي شخص بالتعامل معكم نهائياً", -0.78, 0.93),
    ("خدمة عملاء فظيعة، تعامل غير لائق", -0.88, 0.90),
    ("ضياع للوقت والمال، منتج لا يعمل", -0.79, 0.87),
    ("أسوأ تطبيق استخدمته في حياتي", -0.83, 0.92),
]

# Channel-specific patterns and performance weights
CHANNEL_PATTERNS = {
    FeedbackChannel.EMAIL: {"weight": 0.25, "avg_sentiment": 0.15, "response_time": 24},
    FeedbackChannel.PHONE: {"weight": 0.20, "avg_sentiment": 0.25, "response_time": 2},
    FeedbackChannel.WEBSITE: {"weight": 0.18, "avg_sentiment": 0.10, "response_time": 12},
    FeedbackChannel.WHATSAPP: {"weight": 0.15, "avg_sentiment": 0.30, "response_time": 1},
    FeedbackChannel.MOBILE_APP: {"weight": 0.12, "avg_sentiment": 0.05, "response_time": 6},
    FeedbackChannel.SOCIAL_MEDIA: {"weight": 0.06, "avg_sentiment": -0.10, "response_time": 8},
    FeedbackChannel.SMS: {"weight": 0.02, "avg_sentiment": 0.20, "response_time": 4},
    FeedbackChannel.SURVEY: {"weight": 0.015, "avg_sentiment": 0.35, "response_time": 48},
    FeedbackChannel.CHATBOT: {"weight": 0.005, "avg_sentiment": -0.05, "response_time": 0.5},
}

def generate_realistic_dataset(days=45, base_daily_volume=25):
    """
    Generate realistic test data with temporal patterns and trends
    """
    with app.app_context():
        try:
            # Clear existing data
            db.session.query(Feedback).delete()
            db.session.commit()
            
            end_date = datetime.utcnow()
            total_generated = 0
            
            for day_offset in range(days):
                current_date = end_date - timedelta(days=day_offset)
                
                # Create realistic daily volume patterns
                daily_volume = calculate_daily_volume(current_date, base_daily_volume)
                
                for _ in range(daily_volume):
                    feedback = generate_single_feedback(current_date)
                    db.session.add(feedback)
                    total_generated += 1
            
            db.session.commit()
            logger.info(f"Generated {total_generated} realistic feedback records over {days} days")
            
            # Generate summary stats
            return generate_dataset_summary()
            
        except Exception as e:
            logger.error(f"Error generating realistic dataset: {e}")
            db.session.rollback()
            raise

def calculate_daily_volume(date, base_volume):
    """
    Calculate realistic daily volume with patterns
    """
    # Weekend reduction (Friday-Saturday in Arabic context)
    weekday = date.weekday()
    if weekday in [4, 5]:  # Friday, Saturday
        volume_multiplier = 0.6
    elif weekday in [6, 0]:  # Sunday, Monday (higher activity)
        volume_multiplier = 1.3
    else:
        volume_multiplier = 1.0
    
    # Monthly trends (simulate growth/decline)
    month_factor = 1.0 + (date.day - 15) * 0.02  # Slight monthly variation
    
    # Add random variation
    random_factor = random.uniform(0.7, 1.4)
    
    final_volume = int(base_volume * volume_multiplier * month_factor * random_factor)
    return max(1, final_volume)

def generate_single_feedback(base_date):
    """
    Generate a single realistic feedback entry
    """
    # Select channel based on realistic distribution
    channel = select_weighted_channel()
    
    # Select feedback content with channel-appropriate sentiment bias
    content, base_sentiment, confidence = select_content_for_channel(channel)
    
    # Generate realistic timestamp within the day
    hour = generate_realistic_hour(channel)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    
    timestamp = base_date.replace(
        hour=hour, minute=minute, second=second, microsecond=0
    )
    
    # Generate customer information
    customer_info = generate_customer_info(channel)
    
    # Create processed timestamp
    processing_delay = generate_processing_delay(channel)
    processed_at = timestamp + timedelta(hours=processing_delay)
    
    return Feedback(
        content=content,
        processed_content=content,
        channel=channel,
        status=FeedbackStatus.PROCESSED,
        customer_email=customer_info.get('email'),
        customer_phone=customer_info.get('phone'),
        customer_id=customer_info.get('customer_id'),
        rating=generate_rating_from_sentiment(base_sentiment),
        sentiment_score=base_sentiment,
        confidence_score=confidence,
        ai_summary=generate_ai_summary(content),
        ai_categories=generate_categories(content, channel),
        ai_action_items=generate_action_items(base_sentiment),
        channel_metadata=generate_channel_metadata(channel),
        created_at=timestamp,
        updated_at=processed_at,
        processed_at=processed_at,
        language_detected="ar",
        region=select_arabic_region()
    )

def select_weighted_channel():
    """Select channel based on realistic distribution weights"""
    channels = list(CHANNEL_PATTERNS.keys())
    weights = [CHANNEL_PATTERNS[ch]["weight"] for ch in channels]
    return random.choices(channels, weights=weights)[0]

def select_content_for_channel(channel):
    """Select appropriate content based on channel characteristics"""
    channel_sentiment_bias = CHANNEL_PATTERNS[channel]["avg_sentiment"]
    
    # Filter samples closer to channel's typical sentiment
    suitable_samples = []
    for content, sentiment, confidence in ARABIC_FEEDBACK_SAMPLES:
        # Allow some variation but prefer content matching channel characteristics
        if abs(sentiment - channel_sentiment_bias) < 0.6:
            suitable_samples.append((content, sentiment, confidence))
    
    if not suitable_samples:
        suitable_samples = ARABIC_FEEDBACK_SAMPLES
    
    content, sentiment, confidence = random.choice(suitable_samples)
    
    # Apply slight channel bias to sentiment
    adjusted_sentiment = sentiment + (channel_sentiment_bias * 0.2)
    adjusted_sentiment = max(-1.0, min(1.0, adjusted_sentiment))
    
    return content, adjusted_sentiment, confidence

def generate_realistic_hour(channel):
    """Generate realistic hour based on channel usage patterns"""
    if channel == FeedbackChannel.PHONE:
        # Business hours preference
        return random.choice([9, 10, 11, 14, 15, 16, 17])
    elif channel == FeedbackChannel.SOCIAL_MEDIA:
        # Evening/night activity
        return random.choice([19, 20, 21, 22, 23, 8, 12, 13])
    elif channel == FeedbackChannel.EMAIL:
        # Throughout the day
        return random.randint(8, 22)
    else:
        # General usage
        return random.randint(7, 23)

def generate_customer_info(channel):
    """Generate realistic customer information"""
    customer_id = f"CUST_{random.randint(10000, 99999)}"
    
    info = {"customer_id": customer_id}
    
    if channel in [FeedbackChannel.EMAIL, FeedbackChannel.WEBSITE]:
        info["email"] = f"customer{random.randint(1000, 9999)}@example.com"
    
    if channel in [FeedbackChannel.PHONE, FeedbackChannel.SMS, FeedbackChannel.WHATSAPP]:
        info["phone"] = f"+966{random.randint(500000000, 599999999)}"
    
    return info

def generate_processing_delay(channel):
    """Generate realistic processing delays"""
    base_delay = CHANNEL_PATTERNS[channel]["response_time"]
    variation = random.uniform(0.5, 2.0)
    return base_delay * variation

def generate_rating_from_sentiment(sentiment):
    """Convert sentiment to 1-5 rating scale"""
    if sentiment > 0.6:
        return random.choice([5, 5, 4])
    elif sentiment > 0.2:
        return random.choice([4, 4, 3])
    elif sentiment > -0.2:
        return random.choice([3, 3, 2])
    elif sentiment > -0.6:
        return random.choice([2, 2, 1])
    else:
        return random.choice([1, 1, 2])

def generate_ai_summary(content):
    """Generate AI summary based on content"""
    summaries = [
        "ملخص: تقييم إيجابي للخدمة المقدمة",
        "ملخص: ملاحظات على التحسين المطلوب",
        "ملخص: شكوى حول جودة المنتج",
        "ملخص: تقدير للدعم الفني",
        "ملخص: اقتراحات لتطوير الخدمة",
        "ملخص: تجربة عامة مرضية",
        "ملخص: مشاكل في الاستخدام",
        "ملخص: رضا عن سرعة الاستجابة"
    ]
    return random.choice(summaries)

def generate_categories(content, channel):
    """Generate relevant categories"""
    categories = [
        ["خدمة العملاء", "جودة المنتج"],
        ["التقنية", "سهولة الاستخدام"],
        ["السعر", "القيمة المقابل"],
        ["التسليم", "الشحن"],
        ["الدعم الفني", "المساعدة"],
        ["المميزات", "التطوير"],
        ["الأمان", "الخصوصية"]
    ]
    return random.choice(categories)

def generate_action_items(sentiment):
    """Generate action items based on sentiment"""
    if sentiment > 0.5:
        actions = [
            "متابعة مع العميل للحصول على مراجعة",
            "استخدام كمثال إيجابي للفريق",
            "شكر العميل على التقييم الإيجابي"
        ]
    elif sentiment < -0.3:
        actions = [
            "التواصل مع العميل لحل المشكلة",
            "مراجعة العملية التي تسببت في المشكلة",
            "تحسين الجودة في النقاط المذكورة",
            "متابعة حالة العميل بعد الحل"
        ]
    else:
        actions = [
            "مراجعة التعليقات مع الفريق المختص",
            "تحليل نقاط التحسين المقترحة"
        ]
    
    return random.sample(actions, min(2, len(actions)))

def generate_channel_metadata(channel):
    """Generate channel-specific metadata"""
    metadata = {"source": channel.value}
    
    if channel == FeedbackChannel.SOCIAL_MEDIA:
        metadata.update({
            "platform": random.choice(["twitter", "instagram", "facebook"]),
            "public": True
        })
    elif channel == FeedbackChannel.EMAIL:
        metadata.update({
            "thread_id": f"thread_{random.randint(1000, 9999)}",
            "priority": random.choice(["normal", "high", "low"])
        })
    elif channel == FeedbackChannel.PHONE:
        metadata.update({
            "call_duration": random.randint(120, 1800),
            "agent_id": f"agent_{random.randint(1, 20)}"
        })
    
    return metadata

def select_arabic_region():
    """Select Arabic region with realistic distribution"""
    regions = ["SA", "AE", "EG", "JO", "LB", "KW", "QA", "BH", "OM"]
    weights = [0.35, 0.20, 0.15, 0.08, 0.08, 0.06, 0.04, 0.02, 0.02]
    return random.choices(regions, weights=weights)[0]

def generate_dataset_summary():
    """Generate summary statistics of the created dataset"""
    with app.app_context():
        total_count = db.session.query(Feedback).count()
        
        # Sentiment distribution
        positive = db.session.query(Feedback).filter(Feedback.sentiment_score > 0.2).count()
        neutral = db.session.query(Feedback).filter(
            Feedback.sentiment_score >= -0.2, Feedback.sentiment_score <= 0.2
        ).count()
        negative = db.session.query(Feedback).filter(Feedback.sentiment_score < -0.2).count()
        
        # Channel distribution
        channel_stats = {}
        for channel in FeedbackChannel:
            count = db.session.query(Feedback).filter(Feedback.channel == channel).count()
            channel_stats[channel.value] = count
        
        return {
            "total_feedback": total_count,
            "sentiment_distribution": {
                "positive": positive,
                "neutral": neutral,
                "negative": negative
            },
            "channel_distribution": channel_stats,
            "date_range": "45 days",
            "avg_daily_volume": total_count / 45
        }

if __name__ == "__main__":
    summary = generate_realistic_dataset(days=45, base_daily_volume=30)
    print("Dataset Generation Complete!")
    print(f"Total Records: {summary['total_feedback']}")
    print(f"Average Daily Volume: {summary['avg_daily_volume']:.1f}")
    print(f"Sentiment Distribution: {summary['sentiment_distribution']}")
    print(f"Top Channels: {sorted(summary['channel_distribution'].items(), key=lambda x: x[1], reverse=True)[:3]}")