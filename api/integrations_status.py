"""
Integration Status API
Real-time status monitoring and testing for all platform integrations
"""

from flask import jsonify, request
from app import app
from utils.integration_registry import integration_registry, IntegrationStatus, IntegrationCategory
import logging

logger = logging.getLogger(__name__)

@app.route('/api/integrations/status')
def get_integrations_status():
    """Get real-time status of all integrations"""
    try:
        status_data = {}
        
        for integration_id, integration_spec in integration_registry.integrations.items():
            health_data = integration_registry.check_integration_health(integration_id)
            
            status_data[integration_id] = {
                'name': integration_spec.name,
                'category': integration_spec.category.value,
                'status': integration_spec.status.value,
                'description': integration_spec.description,
                'config_complete': health_data.get('config_complete', False),
                'missing_keys': health_data.get('missing_keys', []),
                'last_check': health_data.get('last_check'),
                'priority': integration_spec.priority,
                'health': health_data
            }
        
        return jsonify({
            'success': True,
            'integrations': status_data,
            'summary': integration_registry.get_integration_summary()
        })
        
    except Exception as e:
        logger.error(f"Error getting integration status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/integrations/status/<integration_id>')
def get_integration_status(integration_id):
    """Get detailed status of specific integration"""
    try:
        if integration_id not in integration_registry.integrations:
            return jsonify({
                'success': False,
                'error': 'Integration not found'
            }), 404
        
        integration_spec = integration_registry.integrations[integration_id]
        health_data = integration_registry.check_integration_health(integration_id)
        
        return jsonify({
            'success': True,
            'integration': {
                'id': integration_id,
                'name': integration_spec.name,
                'category': integration_spec.category.value,
                'status': integration_spec.status.value,
                'description': integration_spec.description,
                'config_keys': integration_spec.config_keys,
                'endpoints': integration_spec.endpoints,
                'auth_method': integration_spec.auth_method,
                'implementation_files': integration_spec.implementation_files,
                'dependencies': integration_spec.dependencies,
                'estimated_effort_weeks': integration_spec.estimated_effort_weeks,
                'priority': integration_spec.priority,
                'health': health_data
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting integration {integration_id} status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/integrations/test/<integration_id>', methods=['POST'])
def test_integration(integration_id):
    """Test specific integration with real API call"""
    try:
        if integration_id not in integration_registry.integrations:
            return jsonify({
                'success': False,
                'error': 'Integration not found'
            }), 404
        
        integration_spec = integration_registry.integrations[integration_id]
        
        if integration_spec.status not in [IntegrationStatus.ACTIVE, IntegrationStatus.CONFIGURED]:
            return jsonify({
                'success': False,
                'error': f'Integration {integration_id} is not configured for testing'
            }), 400
        
        # Perform integration-specific tests
        test_result = None
        
        if integration_id == 'openai':
            test_result = _test_openai_integration()
        elif integration_id == 'claude':
            test_result = _test_claude_integration()
        elif integration_id == 'gmail':
            test_result = _test_gmail_integration()
        elif integration_id == 'jais':
            test_result = _test_jais_integration()
        else:
            return jsonify({
                'success': False,
                'error': f'Testing not implemented for {integration_id}'
            }), 501
        
        return jsonify({
            'success': True,
            'integration_id': integration_id,
            'test_result': test_result
        })
        
    except Exception as e:
        logger.error(f"Error testing integration {integration_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/integrations/categories')
def get_integration_categories():
    """Get integrations grouped by category"""
    try:
        categories_data = {}
        
        for category in IntegrationCategory:
            integrations_in_category = integration_registry.get_by_category(category)
            categories_data[category.value] = {
                'name': category.value,
                'count': len(integrations_in_category),
                'integrations': [
                    {
                        'id': integration.id,
                        'name': integration.name,
                        'status': integration.status.value,
                        'priority': integration.priority
                    }
                    for integration in integrations_in_category
                ]
            }
        
        return jsonify({
            'success': True,
            'categories': categories_data
        })
        
    except Exception as e:
        logger.error(f"Error getting integration categories: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/integrations/roadmap')
def get_integration_roadmap():
    """Get roadmap integrations with implementation timeline"""
    try:
        roadmap_integrations = integration_registry.get_roadmap_integrations()
        
        roadmap_data = []
        for integration in roadmap_integrations:
            roadmap_data.append({
                'id': integration.id,
                'name': integration.name,
                'category': integration.category.value,
                'description': integration.description,
                'priority': integration.priority,
                'estimated_effort_weeks': integration.estimated_effort_weeks,
                'dependencies': integration.dependencies,
                'config_keys': integration.config_keys,
                'implementation_files': integration.implementation_files
            })
        
        return jsonify({
            'success': True,
            'roadmap': roadmap_data,
            'total_integrations': len(roadmap_data)
        })
        
    except Exception as e:
        logger.error(f"Error getting integration roadmap: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Integration-specific test functions
def _test_openai_integration():
    """Test OpenAI integration"""
    try:
        from utils.api_key_manager import APIKeyManager
        import time
        
        api_manager = APIKeyManager()
        client = api_manager.get_openai_client()
        
        start_time = time.time()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Test Arabic: مرحبا"}],
            max_tokens=10
        )
        response_time = (time.time() - start_time) * 1000
        
        return {
            'success': True,
            'response_time_ms': round(response_time, 2),
            'model': 'gpt-4o',
            'tokens_used': response.usage.total_tokens if response.usage else 0,
            'message': 'OpenAI API accessible and responding'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def _test_claude_integration():
    """Test Claude integration"""
    try:
        from utils.api_key_manager import APIKeyManager
        import time
        
        api_manager = APIKeyManager()
        client = api_manager.get_anthropic_client()
        
        start_time = time.time()
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=10,
            messages=[{"role": "user", "content": "Test Arabic: مرحبا"}]
        )
        response_time = (time.time() - start_time) * 1000
        
        return {
            'success': True,
            'response_time_ms': round(response_time, 2),
            'model': 'claude-3-sonnet-20240229',
            'tokens_used': response.usage.input_tokens + response.usage.output_tokens if response.usage else 0,
            'message': 'Claude API accessible and responding'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def _test_gmail_integration():
    """Test Gmail SMTP integration"""
    try:
        import smtplib
        import os
        from email.mime.text import MIMEText
        
        gmail_email = os.getenv('GMAIL_EMAIL')
        gmail_password = os.getenv('GMAIL_APP_PASSWORD')
        
        if not gmail_email or not gmail_password:
            return {
                'success': False,
                'error': 'Gmail credentials not configured'
            }
        
        # Test SMTP connection
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_email, gmail_password)
        server.quit()
        
        return {
            'success': True,
            'message': 'Gmail SMTP connection successful',
            'email_account': gmail_email
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def _test_jais_integration():
    """Test JAIS integration"""
    try:
        import os
        import requests
        
        jais_key = os.getenv('JAIS_API_KEY')
        jais_endpoint = os.getenv('JAIS_ENDPOINT', 'https://api.core42.ai/v1')
        
        if not jais_key:
            return {
                'success': False,
                'error': 'JAIS API key not configured'
            }
        
        # Test API endpoint
        headers = {
            'Authorization': f'Bearer {jais_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(f"{jais_endpoint}/models", headers=headers, timeout=10)
        
        return {
            'success': response.status_code == 200,
            'status_code': response.status_code,
            'message': 'JAIS API accessible' if response.status_code == 200 else f'JAIS API error: {response.status_code}'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }