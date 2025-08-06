"""
Integration Management Routes
Handles integration testing, status monitoring, and catalog display
"""

from flask import render_template, jsonify, request
from core.app import app
from auth.replit_auth import require_login
from utils.integration_registry import integration_registry
import logging

logger = logging.getLogger(__name__)


@app.route('/integrations/catalog')
@app.route('/integrations/technical')
@require_login
def integrations_catalog():
    """API-focused integration catalog for developers with technical details"""
    return render_template('integrations_technical_catalog.html')


@app.route('/integrations/test/<integration_id>', methods=['POST'])
@require_login
def test_integration(integration_id):
    """Test specific integration and return results"""
    try:
        if integration_id not in integration_registry.integrations:
            return jsonify({
                'success': False,
                'error': 'Integration not found'
            }), 404
        
        # Perform integration test
        test_result = integration_registry.test_integration(integration_id)
        
        return jsonify({
            'success': test_result.get('success', False),
            'message': test_result.get('message', 'Test completed'),
            'details': test_result.get('details', {}),
            'response_time': test_result.get('response_time'),
            'timestamp': test_result.get('timestamp')
        })
        
    except Exception as e:
        logger.error(f"Integration test failed for {integration_id}: {e}")
        return jsonify({
            'success': False,
            'error': f'Test failed: {str(e)}'
        }), 500


@app.route('/integrations/status')
@require_login
def integrations_status():
    """Get status of all integrations"""
    try:
        integrations_data = []
        
        for integration_id, integration in integration_registry.integrations.items():
            integrations_data.append({
                'id': integration.id,
                'name': integration.name,
                'status': integration.status.value,
                'category': integration.category.value,
                'description': integration.description,
                'test_endpoint': integration.test_endpoint
            })
        
        return jsonify({
            'success': True,
            'integrations': integrations_data
        })
        
    except Exception as e:
        logger.error(f"Error getting integrations status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500