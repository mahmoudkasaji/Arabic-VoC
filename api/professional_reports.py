"""
Professional Reports API - Phase 3B
API endpoints for PDF report generation and enhanced data export
"""

from flask import Blueprint, jsonify, request, send_file, make_response
from typing import Dict, Any, List
import logging
import json
import io
from datetime import datetime, timedelta
from sqlalchemy import text
from app import db

logger = logging.getLogger(__name__)

# Create blueprint
professional_reports_bp = Blueprint('professional_reports', __name__, url_prefix='/api/reports')

@professional_reports_bp.route('/executive-pdf', methods=['GET'])
def generate_executive_pdf():
    """
    Generate executive PDF report
    
    Query parameters:
    - time_range: "1d", "7d", "30d", "all" (default: "30d")
    - survey_id: specific survey ID (optional)
    """
    try:
        time_range = request.args.get('time_range', '30d')
        survey_id = request.args.get('survey_id')
        
        # For now, create a simplified PDF without complex dependencies
        # This can be enhanced with full reportlab implementation later
        pdf_content = _generate_simple_executive_report(time_range, survey_id)
        
        # Create response
        response = make_response(pdf_content)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=executive_report_{datetime.now().strftime("%Y%m%d")}.pdf'
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating PDF report: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate PDF report'
        }), 500

@professional_reports_bp.route('/export-excel', methods=['GET'])
def export_to_excel():
    """
    Export survey data to Excel format
    
    Query parameters:
    - time_range: "1d", "7d", "30d", "all" (default: "30d")
    - survey_id: specific survey ID (optional)
    - include_analytics: include enhanced analytics (default: true)
    """
    try:
        time_range = request.args.get('time_range', '30d')
        survey_id = request.args.get('survey_id')
        include_analytics = request.args.get('include_analytics', 'true').lower() == 'true'
        
        # Get survey data
        export_data = _get_export_data(time_range, survey_id, include_analytics)
        
        # For now, return JSON data that can be converted to Excel on frontend
        # This avoids complex Excel library dependencies
        response_data = {
            'success': True,
            'data': export_data,
            'metadata': {
                'export_date': datetime.now().isoformat(),
                'time_range': time_range,
                'total_responses': len(export_data.get('responses', [])),
                'include_analytics': include_analytics
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error exporting to Excel: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to export data'
        }), 500

@professional_reports_bp.route('/export-csv', methods=['GET'])
def export_to_csv():
    """
    Export survey data to CSV format
    
    Query parameters:
    - time_range: "1d", "7d", "30d", "all" (default: "30d")
    - survey_id: specific survey ID (optional)
    """
    try:
        time_range = request.args.get('time_range', '30d')
        survey_id = request.args.get('survey_id')
        
        # Get data and convert to CSV
        export_data = _get_export_data(time_range, survey_id, include_analytics=True)
        csv_content = _convert_to_csv(export_data)
        
        # Create CSV response with proper encoding for Arabic
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=survey_data_{datetime.now().strftime("%Y%m%d")}.csv'
        
        return response
        
    except Exception as e:
        logger.error(f"Error exporting to CSV: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to export CSV'
        }), 500

@professional_reports_bp.route('/analytics-summary', methods=['GET'])
def get_analytics_summary():
    """
    Get comprehensive analytics summary for reporting
    
    Query parameters:
    - time_range: "1d", "7d", "30d", "all" (default: "30d")
    - survey_id: specific survey ID (optional)
    """
    try:
        time_range = request.args.get('time_range', '30d')
        survey_id = request.args.get('survey_id')
        
        # Get comprehensive analytics data
        summary = _generate_analytics_summary(time_range, survey_id)
        
        return jsonify({
            'success': True,
            'data': summary,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating analytics summary: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate analytics summary'
        }), 500

@professional_reports_bp.route('/report-templates', methods=['GET'])
def get_report_templates():
    """
    Get available report templates and formats
    """
    try:
        templates = {
            'executive_summary': {
                'name': 'Executive Summary Report',
                'description': 'High-level overview with key metrics and trends',
                'formats': ['pdf', 'excel'],
                'sections': ['summary', 'sentiment_analysis', 'topic_insights', 'recommendations']
            },
            'detailed_analytics': {
                'name': 'Detailed Analytics Report',
                'description': 'Comprehensive analysis with emotion detection and topic categorization',
                'formats': ['excel', 'csv'],
                'sections': ['responses', 'emotions', 'topics', 'sentiment_trends', 'insights']
            },
            'trend_analysis': {
                'name': 'Trend Analysis Report',
                'description': 'Time-based analysis showing changes and patterns',
                'formats': ['pdf', 'excel'],
                'sections': ['time_series', 'comparative_analysis', 'predictions', 'alerts']
            }
        }
        
        return jsonify({
            'success': True,
            'templates': templates
        })
        
    except Exception as e:
        logger.error(f"Error getting report templates: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get report templates'
        }), 500

def _generate_simple_executive_report(time_range: str, survey_id: str = None) -> bytes:
    """Generate a simple text-based executive report"""
    
    # Get analytics data
    summary = _generate_analytics_summary(time_range, survey_id)
    
    # Create simple text report
    report_lines = [
        "CUSTOMER EXPERIENCE EXECUTIVE REPORT",
        "=" * 50,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Time Range: {time_range}",
        "",
        "EXECUTIVE SUMMARY",
        "-" * 20,
        f"Total Responses: {summary['total_responses']}",
        f"Average CSAT: {summary['avg_csat']:.1f}/5.0",
        f"Completion Rate: {summary['completion_rate']:.1f}%",
        f"Primary Emotion: {summary['dominant_emotion']}",
        "",
        "SENTIMENT BREAKDOWN",
        "-" * 20,
        f"Positive: {summary['sentiment_breakdown']['positive']:.1f}%",
        f"Neutral: {summary['sentiment_breakdown']['neutral']:.1f}%", 
        f"Negative: {summary['sentiment_breakdown']['negative']:.1f}%",
        "",
        "TOP TOPICS",
        "-" * 20
    ]
    
    # Add top topics
    for topic, data in list(summary['topic_analysis'].items())[:5]:
        report_lines.append(f"{topic.title()}: {data['mentions']} mentions")
    
    report_lines.extend([
        "",
        "RECOMMENDATIONS",
        "-" * 20,
        "1. Focus on maintaining service quality as it drives positive emotions",
        "2. Investigate neutral responses for improvement opportunities", 
        "3. Implement proactive support for identified frustration areas",
        "4. Continue monitoring emotion trends for early warning indicators",
        "",
        "Report generated by Voice of Customer Platform"
    ])
    
    # Convert to bytes (simple text format)
    report_content = "\n".join(report_lines)
    return report_content.encode('utf-8')

def _get_export_data(time_range: str, survey_id: str = None, include_analytics: bool = True) -> Dict[str, Any]:
    """Get survey data formatted for export"""
    
    # Build query for survey responses
    query = """
        SELECT r.id, r.survey_id, r.answers, r.created_at, r.completion_percentage,
               r.language_used, r.device_type, r.sentiment_score, r.keywords,
               s.title as survey_title, r.respondent_email, r.duration_minutes
        FROM responses_flask r 
        JOIN surveys_flask s ON r.survey_id = s.id 
    """
    
    conditions = []
    params = {}
    
    # Add time filter
    if time_range != 'all':
        if time_range == '1d':
            start_date = datetime.now() - timedelta(days=1)
        elif time_range == '7d':
            start_date = datetime.now() - timedelta(days=7)
        elif time_range == '30d':
            start_date = datetime.now() - timedelta(days=30)
        else:
            start_date = datetime.now() - timedelta(days=7)
        
        conditions.append("r.created_at >= :start_date")
        params['start_date'] = start_date
    
    # Add survey filter
    if survey_id:
        conditions.append("r.survey_id = :survey_id")
        params['survey_id'] = survey_id
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY r.created_at DESC"
    
    # Execute query
    result = db.session.execute(text(query), params)
    
    responses = []
    for row in result:
        # Extract text from answers
        response_text = ""
        questions_data = {}
        
        try:
            if row[2]:  # answers column
                answers_data = json.loads(row[2]) if isinstance(row[2], str) else row[2]
                text_responses = []
                for question_id, answer in answers_data.items():
                    questions_data[question_id] = answer
                    if isinstance(answer, str) and len(answer.strip()) > 0 and not answer.isdigit():
                        text_responses.append(answer.strip())
                response_text = " | ".join(text_responses)
        except Exception as e:
            logger.warning(f"Could not parse answers for response {row[0]}: {e}")
        
        response_data = {
            'response_id': row[0],
            'survey_id': row[1],
            'survey_title': row[9] or 'Unknown Survey',
            'created_at': row[3].strftime('%Y-%m-%d %H:%M') if row[3] else '',
            'completion_percentage': row[4] or 0,
            'language_used': row[5] or 'unknown',
            'device_type': row[6] or 'unknown',
            'sentiment_score': row[7] or 0,
            'keywords': row[8] or '',
            'respondent_email': row[10] or '',
            'duration_minutes': row[11] or 0,
            'response_text': response_text,
            'questions': questions_data
        }
        
        responses.append(response_data)
    
    return {
        'responses': responses,
        'summary': _generate_analytics_summary(time_range, survey_id),
        'export_metadata': {
            'time_range': time_range,
            'survey_id': survey_id,
            'include_analytics': include_analytics,
            'total_responses': len(responses)
        }
    }

def _convert_to_csv(export_data: Dict[str, Any]) -> str:
    """Convert export data to CSV format with Arabic support"""
    
    responses = export_data.get('responses', [])
    
    # CSV headers
    headers = [
        'Response ID', 'Survey Title', 'Created Date', 'Completion Rate (%)',
        'Language', 'Device Type', 'Duration (min)', 'Sentiment Score',
        'Response Text', 'Keywords', 'Respondent Email'
    ]
    
    # Build CSV content with UTF-8 BOM for Arabic support
    csv_lines = [','.join(f'"{header}"' for header in headers)]
    
    for response in responses:
        row = [
            str(response.get('response_id', '')),
            response.get('survey_title', '').replace('"', '""'),
            response.get('created_at', ''),
            str(response.get('completion_percentage', 0)),
            response.get('language_used', ''),
            response.get('device_type', ''),
            str(response.get('duration_minutes', 0)),
            str(response.get('sentiment_score', 0)),
            response.get('response_text', '').replace('"', '""'),
            str(response.get('keywords', '')).replace('"', '""'),
            response.get('respondent_email', '')
        ]
        
        csv_lines.append(','.join(f'"{field}"' for field in row))
    
    # Add UTF-8 BOM for proper Arabic display
    csv_content = '\ufeff' + '\n'.join(csv_lines)
    return csv_content

def _generate_analytics_summary(time_range: str, survey_id: str = None) -> Dict[str, Any]:
    """Generate comprehensive analytics summary"""
    
    # Get export data
    export_data = _get_export_data(time_range, survey_id, include_analytics=False)
    responses = export_data.get('responses', [])
    
    if not responses:
        return {
            'total_responses': 0,
            'avg_csat': 0,
            'completion_rate': 0,
            'dominant_emotion': 'neutral',
            'sentiment_breakdown': {'positive': 0, 'negative': 0, 'neutral': 0},
            'topic_analysis': {}
        }
    
    # Calculate basic metrics
    total_responses = len(responses)
    avg_sentiment = sum(r.get('sentiment_score', 0) for r in responses) / total_responses
    avg_completion = sum(r.get('completion_percentage', 0) for r in responses) / total_responses
    
    # Sentiment breakdown
    sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
    topic_keywords = {}
    
    for response in responses:
        score = response.get('sentiment_score', 0)
        if score > 0.3:
            sentiment_counts['positive'] += 1
        elif score < -0.3:
            sentiment_counts['negative'] += 1
        else:
            sentiment_counts['neutral'] += 1
        
        # Process keywords for topic analysis
        keywords_str = response.get('keywords', '')
        if keywords_str:
            try:
                if keywords_str.startswith('['):
                    keywords = json.loads(keywords_str)
                else:
                    keywords = [k.strip() for k in keywords_str.split(',')]
                
                for keyword in keywords:
                    if keyword:
                        topic_keywords[keyword] = topic_keywords.get(keyword, 0) + 1
            except:
                pass
    
    # Calculate percentages
    sentiment_breakdown = {
        'positive': (sentiment_counts['positive'] / total_responses) * 100,
        'negative': (sentiment_counts['negative'] / total_responses) * 100,
        'neutral': (sentiment_counts['neutral'] / total_responses) * 100
    }
    
    # Topic analysis from keywords
    topic_analysis = {}
    for keyword, count in topic_keywords.items():
        topic_analysis[keyword] = {
            'mentions': count,
            'relevance': count / total_responses,
            'keywords': [keyword]
        }
    
    # Determine dominant emotion based on sentiment
    if sentiment_counts['positive'] > sentiment_counts['negative']:
        dominant_emotion = 'satisfaction' if sentiment_counts['positive'] > sentiment_counts['neutral'] else 'neutral'
    else:
        dominant_emotion = 'frustration' if sentiment_counts['negative'] > sentiment_counts['neutral'] else 'neutral'
    
    return {
        'total_responses': total_responses,
        'avg_csat': (avg_sentiment + 1) * 2.5,  # Convert to 5-point scale
        'completion_rate': avg_completion,
        'dominant_emotion': dominant_emotion,
        'sentiment_breakdown': sentiment_breakdown,
        'topic_analysis': topic_analysis,
        'time_range': time_range,
        'survey_id': survey_id
    }