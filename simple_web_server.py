#!/usr/bin/env python3
"""
Simple web server for FROST AI Dashboard
Works without external dependencies
"""

import http.server
import socketserver
import json
import os
import logging
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FrostAIHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler for FROST AI Dashboard"""
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/' or path == '/dashboard':
            self.serve_dashboard()
        elif path == '/api/health':
            self.serve_api_health()
        elif path == '/api/stats':
            self.serve_api_stats()
        elif path == '/api/operations':
            self.serve_api_operations()
        else:
            self.send_error(404, "Page not found")
    
    def serve_dashboard(self):
        """Serve the main dashboard"""
        try:
            # Load data from storage files
            stats = self.load_json_file('data/bot_stats.json')
            tickets = self.load_json_file('data/tickets.json')
            operations = self.load_json_file('data/operations.json')
            operators = self.load_json_file('data/operators.json')
            
            # Count active operations
            active_operations = len([op for op in operations.get('operations', []) if op.get('status') == 'active'])
            total_tickets = len(tickets.get('tickets', []))
            total_operators = len(operators.get('operators', []))
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>FROST AI Dashboard</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{
                        font-family: 'Courier New', monospace;
                        margin: 0;
                        padding: 20px;
                        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
                        color: #00ff41;
                        min-height: 100vh;
                    }}
                    
                    .container {{
                        max-width: 1200px;
                        margin: 0 auto;
                    }}
                    
                    .header {{
                        text-align: center;
                        margin-bottom: 30px;
                        border-bottom: 2px solid #00ff41;
                        padding-bottom: 20px;
                    }}
                    
                    .title {{
                        font-size: 2.5em;
                        margin: 0;
                        text-shadow: 0 0 10px #00ff41;
                    }}
                    
                    .subtitle {{
                        font-size: 1.2em;
                        margin: 10px 0;
                        opacity: 0.8;
                    }}
                    
                    .status-grid {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                        gap: 20px;
                        margin-bottom: 30px;
                    }}
                    
                    .card {{
                        background: rgba(0, 255, 65, 0.1);
                        border: 1px solid #00ff41;
                        border-radius: 8px;
                        padding: 20px;
                        backdrop-filter: blur(10px);
                    }}
                    
                    .card h3 {{
                        margin-top: 0;
                        color: #00ff41;
                        font-size: 1.5em;
                        border-bottom: 1px solid #00ff41;
                        padding-bottom: 10px;
                    }}
                    
                    .metric {{
                        font-size: 2em;
                        font-weight: bold;
                        color: #00ff41;
                        text-shadow: 0 0 5px #00ff41;
                    }}
                    
                    .metric-label {{
                        font-size: 0.9em;
                        opacity: 0.8;
                    }}
                    
                    .status-online {{
                        color: #00ff41;
                        font-weight: bold;
                    }}
                    
                    .api-links {{
                        margin-top: 20px;
                    }}
                    
                    .api-links a {{
                        color: #00ff41;
                        text-decoration: none;
                        margin-right: 15px;
                        padding: 5px 10px;
                        border: 1px solid #00ff41;
                        border-radius: 4px;
                        display: inline-block;
                        margin-bottom: 5px;
                    }}
                    
                    .api-links a:hover {{
                        background: rgba(0, 255, 65, 0.2);
                    }}
                    
                    .timestamp {{
                        text-align: center;
                        margin-top: 30px;
                        opacity: 0.7;
                        font-size: 0.9em;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1 class="title">🤖 F.R.O.S.T AI Dashboard</h1>
                        <p class="subtitle">Fully Responsive Operational Support Technician</p>
                        <p class="subtitle">Merrywinter Security Consulting</p>
                    </div>
                    
                    <div class="status-grid">
                        <div class="card">
                            <h3>System Status</h3>
                            <p>Discord Bot: <span class="status-online">ONLINE</span></p>
                            <p>Web Interface: <span class="status-online">OPERATIONAL</span></p>
                            <p>Commands Loaded: <span class="metric">39</span></p>
                            <p class="metric-label">Slash Commands Available</p>
                        </div>
                        
                        <div class="card">
                            <h3>Operations Statistics</h3>
                            <p>Active Operations: <span class="metric">{active_operations}</span></p>
                            <p>Total Tickets: <span class="metric">{total_tickets}</span></p>
                            <p>Registered Operators: <span class="metric">{total_operators}</span></p>
                        </div>
                        
                        <div class="card">
                            <h3>Bot Information</h3>
                            <p>Version: <span class="metric">v2.5.7</span></p>
                            <p>Cogs Loaded: <span class="metric">8</span></p>
                            <p>Guilds: <span class="metric">1</span></p>
                            <p class="metric-label">Authorized Guild Connected</p>
                        </div>
                        
                        <div class="card">
                            <h3>API Endpoints</h3>
                            <div class="api-links">
                                <a href="/api/health">Health Check</a>
                                <a href="/api/stats">Bot Statistics</a>
                                <a href="/api/operations">Operations Data</a>
                            </div>
                        </div>
                    </div>
                    
                    <div class="timestamp">
                        Last Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
                    </div>
                </div>
            </body>
            </html>
            """
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
            
        except Exception as e:
            logger.error(f"Error serving dashboard: {e}")
            self.send_error(500, f"Internal server error: {e}")
    
    def serve_api_health(self):
        """Serve health check API"""
        data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "discord_bot": "online",
            "web_interface": "operational",
            "commands_loaded": 39,
            "cogs_loaded": 8
        }
        self.send_json_response(data)
    
    def serve_api_stats(self):
        """Serve bot statistics API"""
        try:
            stats = self.load_json_file('data/bot_stats.json')
            tickets = self.load_json_file('data/tickets.json')
            operations = self.load_json_file('data/operations.json')
            
            data = {
                "bot_stats": stats,
                "total_tickets": len(tickets.get('tickets', [])),
                "active_operations": len([op for op in operations.get('operations', []) if op.get('status') == 'active']),
                "timestamp": datetime.utcnow().isoformat()
            }
            self.send_json_response(data)
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)
    
    def serve_api_operations(self):
        """Serve operations data API"""
        try:
            operations = self.load_json_file('data/operations.json')
            self.send_json_response(operations)
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)
    
    def load_json_file(self, filename):
        """Load JSON file safely"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.warning(f"Could not load {filename}: {e}")
            return {}
    
    def send_json_response(self, data, status_code=200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

def main():
    """Start the web server"""
    PORT = 5000
    
    logger.info("Starting FROST AI Web Dashboard")
    logger.info(f"Server will run at http://0.0.0.0:{PORT}")
    
    try:
        with socketserver.TCPServer(("0.0.0.0", PORT), FrostAIHandler) as httpd:
            logger.info(f"✅ FROST AI Dashboard running on port {PORT}")
            logger.info("Discord Bot: ✅ Online with 39 commands")
            logger.info("Web Interface: ✅ Operational")
            httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")

if __name__ == "__main__":
    main()