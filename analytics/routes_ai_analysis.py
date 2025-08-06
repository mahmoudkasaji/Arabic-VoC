"""
AI Text Analysis Routes
Provides real OpenAI-powered text analysis for customer feedback
"""

import json
import logging
from flask import request, jsonify
from openai import OpenAI
import os
from core.app import app

logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route('/api/analyze-text', methods=['POST'])
def analyze_text():
    """
    Analyze customer feedback text using OpenAI GPT-4o
    
    Request body:
    {
        "text": "النص المراد تحليله"
    }
    
    Response:
    {
        "success": true,
        "analysis": {
            "sentiment": "positive|negative|neutral",
            "confidence": 85,
            "emotions": ["joy", "satisfaction"],
            "topics": ["product_quality", "customer_service"],
            "key_phrases": ["المنتج رائع", "خدمة ممتازة"],
            "summary": "ملخص التحليل بالعربية"
        }
    }
    """
    try:
        # Get request data
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'يرجى إرسال النص المراد تحليله'
            }), 400
        
        text_to_analyze = data['text'].strip()
        if not text_to_analyze:
            return jsonify({
                'success': False,
                'error': 'النص فارغ'
            }), 400
        
        # Create AI analysis prompt
        prompt = f"""You are an expert Arabic text analyst specializing in customer feedback analysis. Analyze the following customer text and provide a structured response.

Text to analyze: "{text_to_analyze}"

Please provide your analysis in the following JSON format:

{{
  "sentiment": "positive" | "negative" | "neutral",
  "confidence": <number between 0-100>,
  "emotions": ["joy", "frustration", "satisfaction", "disappointment", etc.],
  "topics": ["product_quality", "customer_service", "pricing", "delivery", etc.],
  "key_phrases": ["<important phrases from the text>"],
  "summary": "<brief Arabic summary of the main feedback points>"
}}

Guidelines:
- Focus on clear sentiment identification
- Extract business-relevant topics
- Provide confidence based on text clarity and sentiment strength
- Identify both explicit and implied sentiments
- Respond only with valid JSON, no additional text"""

        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert text analyst. Always respond with valid JSON only."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=1000
        )
        
        # Parse AI response
        ai_response = response.choices[0].message.content
        analysis_result = json.loads(ai_response)
        
        # Validate and clean the response
        validated_result = {
            'sentiment': analysis_result.get('sentiment', 'neutral'),
            'confidence': min(100, max(0, analysis_result.get('confidence', 0))),
            'emotions': analysis_result.get('emotions', []),
            'topics': analysis_result.get('topics', []),
            'key_phrases': analysis_result.get('key_phrases', []),
            'summary': analysis_result.get('summary', 'لا يوجد ملخص متاح')
        }
        
        logger.info(f"Successfully analyzed text with sentiment: {validated_result['sentiment']}")
        
        return jsonify({
            'success': True,
            'analysis': validated_result,
            'message': 'تم تحليل النص بنجاح'
        })
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        return jsonify({
            'success': False,
            'error': 'خطأ في تحليل النتائج من الذكاء الاصطناعي'
        }), 500
        
    except Exception as e:
        logger.error(f"Error in AI text analysis: {e}")
        return jsonify({
            'success': False,
            'error': 'حدث خطأ في تحليل النص'
        }), 500

@app.route('/api/analyze-text/health', methods=['GET'])
def analyze_text_health():
    """Health check for AI analysis service"""
    try:
        # Test OpenAI connection
        if not os.environ.get("OPENAI_API_KEY"):
            return jsonify({
                'success': False,
                'status': 'no_api_key',
                'message': 'OpenAI API key not configured'
            }), 500
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'service': 'ai-text-analysis',
            'message': 'AI analysis service is ready'
        })
        
    except Exception as e:
        logger.error(f"AI analysis health check failed: {e}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 500