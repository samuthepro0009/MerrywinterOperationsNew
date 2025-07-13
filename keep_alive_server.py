"""
Keep-Alive Web Server for 24/7 Uptime
Runs alongside Discord bot to maintain connection
"""

import asyncio
import threading
import time
from datetime import datetime, timezone
from flask import Flask, jsonify
import logging

logger = logging.getLogger(__name__)

class KeepAliveServer:
    def __init__(self, port=8080):
        self.app = Flask(__name__)
        self.port = port
        self.start_time = datetime.now(timezone.utc)
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/')
        def home():
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>FROST AI - Keep Alive</title>
                <meta http-equiv="refresh" content="30">
            </head>
            <body style="font-family: Arial; background: #1a1a1a; color: #00ff41; padding: 20px;">
                <h1>🤖 FROST AI Keep-Alive Service</h1>
                <p>✅ Service Status: ONLINE</p>
                <p>⏰ Uptime: """ + str(datetime.now(timezone.utc) - self.start_time).split('.')[0] + """</p>
                <p>🔄 Auto-refresh every 30 seconds</p>
                <p>📡 Monitoring Discord bot connection...</p>
            </body>
            </html>
            """

        @self.app.route('/ping')
        def ping():
            return jsonify({
                "status": "alive",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "uptime": str(datetime.now(timezone.utc) - self.start_time)
            })

        @self.app.route('/health')
        def health():
            return jsonify({
                "service": "FROST AI Keep-Alive",
                "status": "healthy",
                "uptime_seconds": (datetime.now(timezone.utc) - self.start_time).total_seconds(),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

    def run(self):
        """Run the keep-alive server"""
        try:
            self.app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)
        except Exception as e:
            logger.error(f"Keep-alive server error: {e}")

def start_keep_alive_server():
    """Start keep-alive server in background thread"""
    server = KeepAliveServer()
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()
    logger.info(f"✅ Keep-alive server started on port {server.port}")
    return server_thread

if __name__ == "__main__":
    start_keep_alive_server()

    # Keep main thread alive
    try:
        while True:
            time.sleep(60)
            print(f"Keep-alive server running... {datetime.now(timezone.utc)}")
    except KeyboardInterrupt:
        print("Keep-alive server stopped")
```