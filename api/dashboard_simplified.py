"""
Simplified Dashboard API
Provides KPI data for the 4-card dashboard with toggleable charts
"""

import logging
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import random
import math

logger = logging.getLogger(__name__)

# Create blueprint
dashboard_simple_bp = Blueprint('dashboard_simple', __name__)

def get_date_range(time_range):
    """Get start and end dates based on time range"""
    end_date = datetime.now()
    
    if time_range == '7d':
        start_date = end_date - timedelta(days=7)
    elif time_range == '30d':
        start_date = end_date - timedelta(days=30)
    elif time_range == '90d':
        start_date = end_date - timedelta(days=90)
    elif time_range == '1y':
        start_date = end_date - timedelta(days=365)
    else:
        start_date = end_date - timedelta(days=7)
    
    return start_date, end_date

def generate_sample_kpi_data(time_range):
    """Generate sample KPI data for demonstration"""
    # Base values for each KPI
    base_values = {
        'csat': 85,
        'nps': 42,
        'ces': 7.2,
        'completion': 78
    }
    
    # Generate some variation
    data = {}
    
    for kpi, base_value in base_values.items():
        # Add some random variation
        current_value = base_value + random.uniform(-5, 5)
        
        # Generate trend change
        change_value = random.uniform(-3, 3)
        
        # Format values based on KPI type
        if kpi == 'csat' or kpi == 'completion':
            formatted_value = f"{current_value:.1f}%"
        elif kpi == 'nps':
            formatted_value = f"{current_value:.0f}"
        else:  # CES
            formatted_value = f"{current_value:.1f}/10"
        
        data[kpi] = {
            'value': formatted_value,
            'change': {
                'value': f"{change_value:.1f}",
                'period': 'مقارنة بالفترة السابقة'
            }
        }
    
    return data

def generate_sample_chart_data(metric, time_range):
    """Generate sample chart data for the selected metric"""
    start_date, end_date = get_date_range(time_range)
    
    # Generate date labels
    days_diff = (end_date - start_date).days
    
    if days_diff <= 7:
        # Daily data for 7 days
        labels = []
        current_date = start_date
        while current_date <= end_date:
            labels.append(current_date.strftime('%m/%d'))
            current_date += timedelta(days=1)
    elif days_diff <= 30:
        # Daily data for 30 days (every 2-3 days)
        labels = []
        current_date = start_date
        step = max(1, days_diff // 10)
        while current_date <= end_date:
            labels.append(current_date.strftime('%m/%d'))
            current_date += timedelta(days=step)
    elif days_diff <= 90:
        # Weekly data for 90 days
        labels = []
        current_date = start_date
        while current_date <= end_date:
            labels.append(current_date.strftime('%m/%d'))
            current_date += timedelta(days=7)
    else:
        # Monthly data for 1 year
        labels = []
        current_date = start_date.replace(day=1)
        while current_date <= end_date:
            labels.append(current_date.strftime('%Y/%m'))
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
    
    # Generate values based on metric type
    base_values = {
        'csat': 85,
        'nps': 42,
        'ces': 7.2,
        'completion': 78
    }
    
    base_value = base_values.get(metric, 50)
    values = []
    
    for i, label in enumerate(labels):
        # Create a trend pattern with some noise
        trend = math.sin(i * 0.3) * 5  # Slight trend
        noise = random.uniform(-3, 3)  # Random variation
        value = base_value + trend + noise
        
        # Ensure values are within reasonable ranges
        if metric == 'csat' or metric == 'completion':
            value = max(0, min(100, value))
        elif metric == 'nps':
            value = max(-100, min(100, value))
        elif metric == 'ces':
            value = max(1, min(10, value))
        
        values.append(round(value, 1))
    
    return {
        'labels': labels,
        'values': values
    }

@dashboard_simple_bp.route('/api/analytics/dashboard', methods=['GET'])
def get_dashboard_data():
    """
    Get KPI data for the simplified dashboard
    
    Query parameters:
    - time_range: "7d", "30d", "90d", "1y" (default: "7d")
    """
    try:
        time_range = request.args.get('time_range', '7d')
        
        # Generate KPI data
        kpi_data = generate_sample_kpi_data(time_range)
        
        return jsonify({
            'success': True,
            'data': kpi_data,
            'time_range': time_range,
            'last_updated': datetime.now().isoformat(),
            'message': 'Dashboard data retrieved successfully'
        })
        
    except Exception as e:
        logger.error(f"Error in dashboard API: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve dashboard data',
            'message': str(e)
        }), 500

@dashboard_simple_bp.route('/api/analytics/chart-data', methods=['GET'])
def get_chart_data():
    """
    Get chart data for a specific metric
    
    Query parameters:
    - metric: "csat", "nps", "ces", "completion" (required)
    - time_range: "7d", "30d", "90d", "1y" (default: "7d")
    """
    try:
        metric = request.args.get('metric', 'csat')
        time_range = request.args.get('time_range', '7d')
        
        # Validate metric
        valid_metrics = ['csat', 'nps', 'ces', 'completion']
        if metric not in valid_metrics:
            return jsonify({
                'success': False,
                'error': 'Invalid metric specified',
                'valid_metrics': valid_metrics
            }), 400
        
        # Generate chart data
        chart_data = generate_sample_chart_data(metric, time_range)
        
        return jsonify({
            'success': True,
            'data': chart_data,
            'metric': metric,
            'time_range': time_range,
            'last_updated': datetime.now().isoformat(),
            'message': f'Chart data for {metric} retrieved successfully'
        })
        
    except Exception as e:
        logger.error(f"Error in chart data API: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve chart data',
            'message': str(e)
        }), 500

@dashboard_simple_bp.route('/api/analytics/health', methods=['GET'])
def health_check():
    """Health check for simplified dashboard API"""
    try:
        return jsonify({
            'success': True,
            'status': 'healthy',
            'service': 'dashboard-simplified',
            'timestamp': datetime.now().isoformat(),
            'message': 'Simplified dashboard API is operational'
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'service': 'dashboard-simplified',
            'error': str(e)
        }), 500