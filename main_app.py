#!/usr/bin/env python3
"""
Main application entry point for FROST AI
Supports both Flask web app and Discord bot
"""

import os
import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main application entry point"""
    try:
        # Check if Flask is available and run the web application
        from app import app, FLASK_AVAILABLE
        
        if FLASK_AVAILABLE:
            logger.info("Starting FROST AI web dashboard on port 5000")
            app.run(host='0.0.0.0', port=5000, debug=False)
        else:
            logger.warning("Flask not available - running fallback server")
            # Import the fallback from start_server.py
            from start_server import main as fallback_main
            fallback_main()
            
    except ImportError as e:
        logger.error(f"Import error: {e}")
        # Last resort fallback
        import http.server
        import socketserver
        
        class Handler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                html = f"""
                <!DOCTYPE html>
                <html>
                <head><title>FROST AI Dashboard</title></head>
                <body style="font-family: Arial; margin: 40px; background: #1a1a1a; color: #00ff41;">
                <h1>🤖 FROST AI Dashboard</h1>
                <p>✅ Application is running</p>
                <p>✅ Web interface operational</p>
                <p>Status: Online | Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                </body>
                </html>
                """
                self.wfile.write(html.encode())
        
        with socketserver.TCPServer(("0.0.0.0", 5000), Handler) as httpd:
            logger.info("Serving fallback dashboard at http://0.0.0.0:5000")
            httpd.serve_forever()
    
    except Exception as e:
        logger.error(f"Application error: {e}")
        print("FROST AI Application Failed to Start")
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()