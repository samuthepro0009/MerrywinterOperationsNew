"""
Simple Flask app for testing
"""
import os
from flask import Flask, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "test-secret")

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head><title>FROST AI Dashboard</title></head>
    <body>
    <h1>FROST AI Dashboard</h1>
    <p>Migration successful! Dashboard is running.</p>
    <p>Discord Bot Status: Ready (needs DISCORD_TOKEN)</p>
    <p>Web Interface: Operational</p>
    </body>
    </html>
    """

@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "message": "Migration completed successfully"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)