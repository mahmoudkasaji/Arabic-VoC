"""
Test Enhanced Text Analytics on Real Survey Data
Phase 3A - Processing actual survey responses
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import logging
from datetime import datetime
from utils.enhanced_text_analytics import EnhancedTextAnalytics
from sqlalchemy import text
from app import app, db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_real_survey_responses():
    """Get actual survey responses from database"""
    with app.app_context():
        query = text("""
            SELECT r.id, r.survey_id, r.answers, r.keywords, r.sentiment_score, 
                   r.confidence_score, r.created_at, s.title 
            FROM responses_flask r 
            JOIN surveys_flask s ON r.survey_id = s.id 
            ORDER BY r.created_at DESC
        """)
        
        result = db.session.execute(query)
        responses = []
        
        for row in result:
            responses.append({
                'id': row[0],
                'survey_id': row[1], 
                'answers': row[2],
                'keywords': row[3],
                'sentiment_score': row[4],
                'confidence_score': row[5],
                'created_at': row[6],
                'survey_title': row[7]
            })
        
        return responses

def test_enhanced_analytics():
    """Test enhanced analytics on real survey data"""
    print("🔍 Testing Enhanced Text Analytics on Real Survey Data")
    print("=" * 60)
    
    # Get real responses
    responses = get_real_survey_responses()
    print(f"📊 Found {len(responses)} real survey responses")
    
    if not responses:
        print("❌ No survey responses found in database")
        return
    
    # Initialize enhanced analytics
    analyzer = EnhancedTextAnalytics()
    
    # Process each response
    for i, response in enumerate(responses, 1):
        print(f"\n📝 Response {i}: Survey '{response['survey_title']}'")
        print(f"Response ID: {response['id']}")
        print(f"Created: {response['created_at']}")
        
        # Parse answers
        try:
            if isinstance(response['answers'], str):
                answers_data = json.loads(response['answers'])
            else:
                answers_data = response['answers']
            
            # Extract text responses
            text_responses = []
            for question_id, answer in answers_data.items():
                if isinstance(answer, str) and len(answer.strip()) > 0 and not answer.isdigit():
                    text_responses.append(f"Q{question_id}: {answer}")
            
            combined_text = " | ".join(text_responses)
            
            if combined_text:
                print(f"📄 Text: {combined_text}")
                
                # Run enhanced analysis
                print("🤖 Running enhanced analysis...")
                analysis = analyzer.analyze_with_emotions_and_topics(combined_text)
                
                # Display results
                print(f"⏱️  Processing time: {analysis.get('processing_time', 'N/A')}s")
                
                # Primary emotion
                primary_emotion = analysis.get('primary_emotion', {})
                print(f"😊 Primary emotion: {primary_emotion.get('emotion', 'N/A')} "
                      f"(confidence: {primary_emotion.get('confidence', 0):.2f})")
                
                # Topics
                topics = analysis.get('topics', [])
                if topics:
                    print(f"📚 Topics detected ({len(topics)}):")
                    for topic in topics:
                        print(f"   - {topic.get('category', 'N/A')} "
                              f"(relevance: {topic.get('relevance', 0):.2f})")
                        if topic.get('keywords'):
                            print(f"     Keywords: {', '.join(topic.get('keywords', []))}")
                
                # Sentiment
                sentiment = analysis.get('sentiment', {})
                print(f"💭 Sentiment: {sentiment.get('label', 'N/A')} "
                      f"(score: {sentiment.get('score', 0):.2f})")
                
                # Key insights
                insights = analysis.get('insights', {})
                if insights.get('key_points'):
                    print(f"💡 Key insights:")
                    for point in insights.get('key_points', [])[:3]:  # Show top 3
                        print(f"   - {point}")
                
                # Compare with existing analysis
                if response.get('sentiment_score'):
                    print(f"📊 Comparison with existing:")
                    print(f"   Old sentiment: {response['sentiment_score']:.2f}")
                    print(f"   New sentiment: {sentiment.get('score', 0):.2f}")
                    
                    if response.get('keywords'):
                        old_keywords = response['keywords']
                        new_keywords = analysis.get('keywords', [])
                        print(f"   Old keywords: {old_keywords}")
                        print(f"   New keywords: {new_keywords}")
                
            else:
                print("⚠️  No text content found (only numeric responses)")
                
        except Exception as e:
            print(f"❌ Error processing response: {e}")
        
        print("-" * 40)
    
    print(f"\n✅ Enhanced analytics testing completed on {len(responses)} responses")
    print("🎯 Ready to integrate enhanced analytics into live system!")

if __name__ == "__main__":
    test_enhanced_analytics()