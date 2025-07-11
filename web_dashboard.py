"""
Web Dashboard for FROST AI
External web interface for bot management and statistics
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta
import asyncio
import threading
import requests

from config.settings import Config
from utils.storage import Storage

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# Initialize storage
storage = Storage()

# Global variables for bot data
bot_stats = {}
command_stats = {}
performance_data = {}
training_schedules = {}
warning_points = {}

async def load_bot_data():
    """Load bot data from storage"""
    global bot_stats, command_stats, performance_data, training_schedules, warning_points
    
    try:
        # Load various data files
        bot_stats = await storage.load_bot_stats() or {}
        command_stats = await storage.load_command_stats() or {}
        performance_data = await storage.load_performance_data() or {}
        training_schedules = await storage.load_training_schedule() or {}
        warning_points = await storage.load_warning_points() or {}
    except Exception as e:
        print(f"Error loading bot data: {e}")

def run_async_task(coro):
    """Run async task in a thread"""
    def run_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(coro)
        loop.close()
    
    threading.Thread(target=run_in_thread).start()

# Load data on startup
run_async_task(load_bot_data())

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html', 
                         bot_stats=bot_stats,
                         command_stats=command_stats,
                         performance_data=performance_data)

@app.route('/api/stats')
def api_stats():
    """API endpoint for bot statistics"""
    return jsonify({
        'uptime': bot_stats.get('uptime', 0),
        'guilds': bot_stats.get('guilds', 0),
        'users': bot_stats.get('users', 0),
        'commands_executed': bot_stats.get('commands_executed', 0),
        'latency': bot_stats.get('latency', 0),
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/commands')
def api_commands():
    """API endpoint for command statistics"""
    return jsonify({
        'total_commands': sum(cmd_data.get('count', 0) for cmd_data in command_stats.values()),
        'commands': command_stats,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/performance')
def api_performance():
    """API endpoint for performance metrics"""
    return jsonify({
        'metrics': performance_data,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/training')
def api_training():
    """API endpoint for training schedules"""
    # Filter upcoming training sessions
    upcoming_training = {}
    current_time = datetime.utcnow()
    
    for training_id, training in training_schedules.items():
        training_datetime = datetime.fromisoformat(training['datetime'])
        if training_datetime > current_time and training.get('status') == 'scheduled':
            upcoming_training[training_id] = training
    
    return jsonify({
        'upcoming_training': upcoming_training,
        'total_scheduled': len(upcoming_training),
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/moderation')
def api_moderation():
    """API endpoint for moderation statistics"""
    return jsonify({
        'warning_points': warning_points,
        'total_warnings': sum(len(user_data.get('warnings', [])) for user_data in warning_points.values()),
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/users')
def api_users():
    """API endpoint for user information"""
    return jsonify({
        'total_users': len(performance_data),
        'active_users': len([user for user, data in performance_data.items() if data]),
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/operations')
def api_operations():
    """API endpoint for operations data"""
    # This would integrate with operations data
    return jsonify({
        'active_operations': 0,
        'completed_operations': 0,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/admin')
def admin_panel():
    """Admin panel for bot management"""
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    
    return render_template('admin.html',
                         bot_stats=bot_stats,
                         warning_points=warning_points,
                         training_schedules=training_schedules)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple authentication (in production, use proper authentication)
        if username == 'admin' and password == os.getenv('ADMIN_PASSWORD', 'frost2025'):
            session['authenticated'] = True
            return redirect(url_for('admin_panel'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Admin logout"""
    session.pop('authenticated', None)
    return redirect(url_for('dashboard'))

@app.route('/api/send-notification', methods=['POST'])
def api_send_notification():
    """API endpoint to send notifications"""
    if not session.get('authenticated'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    title = data.get('title')
    message = data.get('message')
    priority = data.get('priority', 'medium')
    
    if not title or not message:
        return jsonify({'error': 'Title and message are required'}), 400
    
    # This would integrate with the bot's notification system
    notification_id = f"web_{int(datetime.utcnow().timestamp())}"
    
    return jsonify({
        'success': True,
        'notification_id': notification_id,
        'message': 'Notification sent successfully'
    })

@app.route('/api/update-config', methods=['POST'])
def api_update_config():
    """API endpoint to update bot configuration"""
    if not session.get('authenticated'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    config_key = data.get('key')
    config_value = data.get('value')
    
    if not config_key:
        return jsonify({'error': 'Configuration key is required'}), 400
    
    # This would update the bot's configuration
    return jsonify({
        'success': True,
        'message': f'Configuration {config_key} updated successfully'
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': Config.AI_VERSION
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)