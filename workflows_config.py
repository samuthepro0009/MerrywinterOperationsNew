"""
Configuration for multiple workflows
"""

# Discord Bot workflow - runs the main bot
discord_bot_config = {
    'name': 'Discord Bot',
    'command': 'python main.py',
    'wait_for_port': None
}

# Web Dashboard workflow - runs the web interface  
web_dashboard_config = {
    'name': 'Web Dashboard',
    'command': 'python web_dashboard.py',
    'wait_for_port': 5000
}

# Export configurations for easy import
WORKFLOWS = [
    discord_bot_config,
    web_dashboard_config
]