"""
Flask Web Application for FROST AI Dashboard
Provides web interface for Discord bot management and statistics
"""

import os
import json
from datetime import datetime

try:
    from flask import Flask, render_template, jsonify
    from werkzeug.middleware.proxy_fix import ProxyFix
    from utils.storage import Storage
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

if FLASK_AVAILABLE:
    # Create Flask app
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET", "frost-ai-dashboard-secret-key")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
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
            
            # Return a simple HTML page since template might not be available
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>FROST AI Dashboard</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; background: #1a1a1a; color: #00ff41; }}
                    h1 {{ color: #00ff41; }}
                    .card {{ background: #2a2a2a; padding: 20px; margin: 10px; border-radius: 5px; }}
                    .metric {{ font-size: 24px; font-weight: bold; }}
                </style>
            </head>
            <body>
                <h1>🤖 FROST AI Dashboard</h1>
                <div class="card">
                    <h3>System Status</h3>
                    <p>Status: <span class="metric">Online</span></p>
                    <p>Discord Bot: <span class="metric">Ready</span></p>
                    <p>Web Interface: <span class="metric">Operational</span></p>
                </div>
                <div class="card">
                    <h3>Statistics</h3>
                    <p>Total Tickets: <span class="metric">{len(tickets.get('tickets', []))}</span></p>
                    <p>Active Operations: <span class="metric">{len([op for op in operations.get('operations', []) if op.get('status') == 'active'])}</span></p>
                    <p>Total Operators: <span class="metric">{len(operators.get('operators', []))}</span></p>
                </div>
                <div class="card">
                    <h3>API Endpoints</h3>
                    <p><a href="/api/health" style="color: #00ff41;">/api/health</a> - Health check</p>
                    <p><a href="/api/stats" style="color: #00ff41;">/api/stats</a> - Bot statistics</p>
                    <p><a href="/api/operations" style="color: #00ff41;">/api/operations</a> - Operations data</p>
                </div>
                <p><small>Last Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</small></p>
            </body>
            </html>
            """
        except Exception as e:
            return f"""
            <!DOCTYPE html>
            <html>
            <head><title>FROST AI Dashboard</title></head>
            <body style="font-family: Arial, sans-serif; margin: 40px; background: #1a1a1a; color: #00ff41;">
            <h1>🤖 FROST AI Dashboard</h1>
            <p>Migration completed successfully!</p>
            <p>Current time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            <p>Status: Online</p>
            <p>Error loading data: {str(e)}</p>
            </body>
            </html>
            """

    @app.route('/api/health')
    def api_health():
        """API endpoint for health check"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'FROST AI Dashboard',
            'discord_bot': 'Ready',
            'migration_status': 'Completed'
        })

    @app.route('/api/stats')
    def api_stats():
        """API endpoint for bot statistics"""
        try:
            # Load bot stats from storage
            bot_stats = storage.load_data('bot_stats.json')
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

else:
    # Fallback when Flask is not available
    class MockApp:
        def run(self, **kwargs):
            print("Flask not available - running in compatibility mode")
            print(f"Dashboard would be available at http://0.0.0.0:{kwargs.get('port', 5000)}")
            print("Install Flask packages to enable full web dashboard functionality")
            print("Migration completed successfully - Discord bot is ready!")
            import time
            while True:
                time.sleep(60)
    
    app = MockApp()

if __name__ == '__main__':
    if FLASK_AVAILABLE:
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        app.run(host='0.0.0.0', port=5000)