"""
Flask Web Application for FROST AI Dashboard
Provides web interface for Discord bot management and statistics
"""

import os
import json
import asyncio
from datetime import datetime
from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from utils.storage import Storage

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "frost-ai-dashboard-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Enable CORS for API endpoints
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize storage
storage = Storage()

@app.route('/')
def dashboard():
    """Main dashboard page"""
    try:
        # Load bot stats from storage
        bot_stats = storage.load_data('bot_stats.json')
        tickets = storage.load_data('tickets.json')
        operations = storage.load_data('operations.json')
        operators = storage.load_data('operators.json')
        
        # Prepare context data for template
        context = {
            'bot_stats': bot_stats,
            'total_tickets': len(tickets.get('tickets', [])),
            'active_operations': len([op for op in operations.get('operations', []) if op.get('status') == 'active']),
            'total_operators': len(operators.get('operators', [])),
            'current_time': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        }
        
        return render_template('dashboard.html', **context)
    except Exception as e:
        # Return a simple HTML page if template fails
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>FROST AI Dashboard</title></head>
        <body>
        <h1>FROST AI Dashboard</h1>
        <p>Dashboard is running successfully!</p>
        <p>Current time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        <p>Status: Online</p>
        </body>
        </html>
        """

@app.route('/api/stats')
def api_stats():
    """API endpoint for bot statistics"""
    try:
        # Load bot stats from storage
        bot_stats = storage.load_data('bot_stats.json')
        
        # Load other relevant data
        tickets = storage.load_data('tickets.json')
        operations = storage.load_data('operations.json')
        operators = storage.load_data('operators.json')
        
        stats = {
            'total_tickets': len(tickets.get('tickets', [])),
            'active_operations': len([op for op in operations.get('operations', []) if op.get('status') == 'active']),
            'total_operators': len(operators.get('operators', [])),
            'bot_uptime': bot_stats.get('uptime', 0),
            'commands_processed': bot_stats.get('commands_processed', 0),
            'last_updated': datetime.utcnow().isoformat()
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/commands')
def api_commands():
    """API endpoint for command statistics"""
    try:
        bot_stats = storage.load_data('bot_stats.json')
        command_stats = bot_stats.get('command_usage', {})
        
        return jsonify(command_stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def api_health():
    """API endpoint for health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'FROST AI Dashboard'
    })

@app.route('/api/performance')
def api_performance():
    """API endpoint for performance metrics"""
    try:
        # Load performance data
        performance_data = storage.load_data('performance_metrics.json')
        
        return jsonify(performance_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/training')
def api_training():
    """API endpoint for training schedules"""
    try:
        training_data = storage.load_data('training_schedules.json')
        
        return jsonify(training_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/moderation')
def api_moderation():
    """API endpoint for moderation statistics"""
    try:
        # Load moderation data
        moderation_data = storage.load_data('moderation_stats.json')
        
        return jsonify(moderation_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/operations')
def api_operations():
    """API endpoint for operations data"""
    try:
        operations = storage.load_data('operations.json')
        
        return jsonify(operations)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)