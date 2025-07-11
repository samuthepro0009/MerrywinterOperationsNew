"""
Simple Web Dashboard for FROST AI
Uses Python's built-in HTTP server to provide a web interface
"""

import json
import os
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import threading
import time

# Import storage system
from utils.storage import Storage

class FROSTDashboardHandler(BaseHTTPRequestHandler):
    """HTTP handler for FROST AI dashboard"""
    
    def __init__(self, *args, **kwargs):
        self.storage = Storage()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/' or path == '/dashboard':
            self.serve_dashboard()
        elif path == '/api/stats':
            self.serve_api_stats()
        elif path == '/api/commands':
            self.serve_api_commands()
        elif path == '/api/health':
            self.serve_api_health()
        elif path.startswith('/static/'):
            self.serve_static_file(path)
        else:
            self.send_error(404, "Not Found")
    
    def serve_dashboard(self):
        """Serve the main dashboard page"""
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>F.R.O.S.T AI Dashboard</title>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                body {
                    font-family: 'Consolas', 'Monaco', monospace;
                    background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
                    color: #00ff41;
                    min-height: 100vh;
                    padding: 20px;
                }
                
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                }
                
                .header {
                    text-align: center;
                    margin-bottom: 40px;
                    border-bottom: 2px solid #00ff41;
                    padding-bottom: 20px;
                }
                
                .header h1 {
                    font-size: 3rem;
                    text-shadow: 0 0 20px #00ff41;
                    margin-bottom: 10px;
                    animation: glow 2s ease-in-out infinite alternate;
                }
                
                @keyframes glow {
                    from { text-shadow: 0 0 20px #00ff41; }
                    to { text-shadow: 0 0 30px #00ff41, 0 0 40px #00ff41; }
                }
                
                .subtitle {
                    font-size: 1.2rem;
                    color: #66ff99;
                    margin-bottom: 5px;
                }
                
                .stats-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 40px;
                }
                
                .stat-card {
                    background: rgba(0, 255, 65, 0.1);
                    border: 1px solid #00ff41;
                    border-radius: 10px;
                    padding: 20px;
                    text-align: center;
                    transition: all 0.3s ease;
                }
                
                .stat-card:hover {
                    background: rgba(0, 255, 65, 0.2);
                    transform: translateY(-5px);
                    box-shadow: 0 5px 20px rgba(0, 255, 65, 0.3);
                }
                
                .stat-value {
                    font-size: 2rem;
                    font-weight: bold;
                    color: #00ff41;
                    margin-bottom: 10px;
                }
                
                .stat-label {
                    font-size: 0.9rem;
                    color: #66ff99;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }
                
                .features {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-bottom: 40px;
                }
                
                .feature-card {
                    background: rgba(0, 255, 65, 0.05);
                    border: 1px solid #00ff41;
                    border-radius: 10px;
                    padding: 20px;
                }
                
                .feature-title {
                    font-size: 1.2rem;
                    color: #00ff41;
                    margin-bottom: 10px;
                    text-transform: uppercase;
                }
                
                .feature-list {
                    list-style: none;
                    padding: 0;
                }
                
                .feature-list li {
                    color: #66ff99;
                    margin-bottom: 5px;
                    padding-left: 20px;
                    position: relative;
                }
                
                .feature-list li::before {
                    content: "▶";
                    position: absolute;
                    left: 0;
                    color: #00ff41;
                }
                
                .footer {
                    text-align: center;
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #00ff41;
                    color: #66ff99;
                }
                
                .loading {
                    color: #00ff41;
                    text-align: center;
                }
                
                .error {
                    color: #ff4444;
                    text-align: center;
                }
                
                .status-indicator {
                    display: inline-block;
                    width: 10px;
                    height: 10px;
                    border-radius: 50%;
                    background-color: #00ff41;
                    box-shadow: 0 0 10px #00ff41;
                    animation: pulse 2s infinite;
                    margin-right: 8px;
                }
                
                @keyframes pulse {
                    0% { opacity: 1; }
                    50% { opacity: 0.5; }
                    100% { opacity: 1; }
                }
                
                .sound-control {
                    position: absolute;
                    top: 20px;
                    right: 20px;
                    background: rgba(0, 255, 65, 0.1);
                    border: 1px solid #00ff41;
                    color: #00ff41;
                    padding: 10px;
                    border-radius: 5px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }
                
                .sound-control:hover {
                    background: rgba(0, 255, 65, 0.2);
                    transform: scale(1.05);
                }
                
                .sound-control.muted {
                    opacity: 0.5;
                    color: #666;
                    border-color: #666;
                }</old_str>
            </style>
        </head>
        <body>
            <button class="sound-control" id="soundToggle" onclick="toggleSound()">🔊 Sound: ON</button>
            <div class="container">
                <div class="header">
                    <h1>🤖 F.R.O.S.T AI</h1>
                    <div class="subtitle">Fully Responsive Operational Support Technician</div>
                    <div class="subtitle">Merrywinter Security Consulting</div>
                    <div class="subtitle"><span class="status-indicator"></span>System Status: OPERATIONAL</div>
                </div></div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value" id="uptime">Loading...</div>
                        <div class="stat-label">System Uptime</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="latency">Loading...</div>
                        <div class="stat-label">Network Latency</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="guilds">Loading...</div>
                        <div class="stat-label">Combat Zones</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="commands">Loading...</div>
                        <div class="stat-label">Commands Executed</div>
                    </div>
                </div>
                
                <div class="features">
                    <div class="feature-card">
                        <div class="feature-title">Advanced Logging</div>
                        <ul class="feature-list">
                            <li>Voice channel monitoring</li>
                            <li>Message reaction tracking</li>
                            <li>Nickname change history</li>
                            <li>Role change monitoring</li>
                            <li>Channel activity logging</li>
                            <li>Invite tracking system</li>
                            <li>Server boost notifications</li>
                            <li>Mass action detection</li>
                        </ul>
                    </div>
                    
                    <div class="feature-card">
                        <div class="feature-title">Enhanced Moderation</div>
                        <ul class="feature-list">
                            <li>Smart spam detection</li>
                            <li>Phishing link protection</li>
                            <li>Auto-escalation system</li>
                            <li>Warning points tracking</li>
                            <li>Temporary ban system</li>
                            <li>Suspicious content detection</li>
                            <li>Context-aware monitoring</li>
                        </ul>
                    </div>
                    
                    <div class="feature-card">
                        <div class="feature-title">Performance Metrics</div>
                        <ul class="feature-list">
                            <li>Operator performance tracking</li>
                            <li>Achievement system</li>
                            <li>Attendance monitoring</li>
                            <li>Performance leaderboards</li>
                            <li>Historical data analysis</li>
                            <li>Attendance rate calculations</li>
                        </ul>
                    </div>
                    
                    <div class="feature-card">
                        <div class="feature-title">Training Management</div>
                        <ul class="feature-list">
                            <li>Automated scheduling</li>
                            <li>Multi-tier training types</li>
                            <li>Participant registration</li>
                            <li>Instructor assignments</li>
                            <li>Automated reminders</li>
                            <li>Training history tracking</li>
                        </ul>
                    </div>
                    
                    <div class="feature-card">
                        <div class="feature-title">Smart Notifications</div>
                        <ul class="feature-list">
                            <li>Priority-based routing</li>
                            <li>Emergency detection</li>
                            <li>User preferences</li>
                            <li>Context-aware alerts</li>
                            <li>Notification history</li>
                            <li>Role-based targeting</li>
                        </ul>
                    </div>
                    
                    <div class="feature-card">
                        <div class="feature-title">Roblox Integration</div>
                        <ul class="feature-list">
                            <li>Account linking system</li>
                            <li>Game server monitoring</li>
                            <li>Player activity tracking</li>
                            <li>Account verification</li>
                            <li>Game statistics</li>
                            <li>Performance correlation</li>
                        </ul>
                    </div>
                </div>
                
                <div class="footer">
                    <p>F.R.O.S.T AI v2.5.7 • Sub umbra, vincimus • Est. 2025</p>
                    <p>24/7 Operational Support • Professional PMC Operations Management</p>
                </div>
            </div>
            
            <script>
                // Enhanced Retro Terminal Audio System
                class TerminalAudio {
                    constructor() {
                        this.audioContext = null;
                        this.isPlaying = false;
                        this.enabled = true;
                        this.initAudio();
                    }
                    
                    initAudio() {
                        try {
                            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
                        } catch (e) {
                            console.log('Audio context not supported');
                        }
                    }
                    
                    playBeep(duration = 0.05, frequency = 1200, volume = 0.05) {
                        if (!this.audioContext || !this.enabled) return;
                        
                        const oscillator = this.audioContext.createOscillator();
                        const gainNode = this.audioContext.createGain();
                        
                        oscillator.connect(gainNode);
                        gainNode.connect(this.audioContext.destination);
                        
                        oscillator.frequency.value = frequency;
                        oscillator.type = 'square'; // Square wave for retro computer sound
                        
                        gainNode.gain.setValueAtTime(volume, this.audioContext.currentTime);
                        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration);
                        
                        oscillator.start(this.audioContext.currentTime);
                        oscillator.stop(this.audioContext.currentTime + duration);
                    }
                    
                    playSystemBeep() {
                        // Classic system beep
                        this.playBeep(0.1, 800, 0.03);
                    }
                    
                    playKeyClick() {
                        // Short keyboard click sound
                        this.playBeep(0.02, 2000, 0.02);
                    }
                    
                    playDataBeep() {
                        // Data processing beep
                        this.playBeep(0.08, 1500, 0.04);
                    }
                    
                    playErrorBeep() {
                        // Error/warning beep
                        this.playBeep(0.15, 400, 0.05);
                    }
                    
                    async playStartupSequence() {
                        if (this.isPlaying) return;
                        this.isPlaying = true;
                        
                        // Retro computer startup sequence
                        this.playBeep(0.08, 600, 0.04);  // Low tone
                        await this.sleep(120);
                        this.playBeep(0.08, 800, 0.04);  // Mid tone  
                        await this.sleep(120);
                        this.playBeep(0.12, 1200, 0.05); // High tone
                        await this.sleep(200);
                        this.playBeep(0.15, 1600, 0.06); // Success tone
                        
                        this.isPlaying = false;
                    }
                    
                    async playProcessingSequence() {
                        if (this.isPlaying) return;
                        this.isPlaying = true;
                        
                        // Data processing sequence: rapid beeps
                        for (let i = 0; i < 4; i++) {
                            this.playBeep(0.03, 1400 + (i * 100), 0.025);
                            await this.sleep(60);
                        }
                        
                        this.isPlaying = false;
                    }
                    
                    async playStatusUpdate() {
                        // Single status update beep
                        this.playBeep(0.06, 1000, 0.03);
                    }
                    
                    async playNetworkActivity() {
                        // Network activity sound
                        this.playBeep(0.04, 1800, 0.02);
                        await this.sleep(50);
                        this.playBeep(0.04, 1600, 0.02);
                    }
                    
                    toggleSound() {
                        this.enabled = !this.enabled;
                        return this.enabled;
                    }
                    
                    sleep(ms) {
                        return new Promise(resolve => setTimeout(resolve, ms));
                    }
                }</old_str>
                
                // Initialize terminal audio
                const terminalAudio = new TerminalAudio();
                
                // Add click listener to enable audio context
                document.addEventListener('click', () => {
                    if (terminalAudio.audioContext && terminalAudio.audioContext.state === 'suspended') {
                        terminalAudio.audioContext.resume();
                    }
                }, { once: true });
                
                // Load dashboard data
                async function loadDashboardData() {
                    try {
                        const response = await fetch('/api/stats');
                        const data = await response.json();
                        
                        // Format uptime nicely
                        const uptime = data.uptime || 'Unknown';
                        document.getElementById('uptime').textContent = uptime;
                        document.getElementById('latency').textContent = (data.latency || 0) + 'ms';
                        document.getElementById('guilds').textContent = data.guilds || 0;
                        document.getElementById('commands').textContent = data.commands_executed || 0;
                        
                        // Update status indicator
                        const statusIndicator = document.querySelector('.status-indicator');
                        if (statusIndicator) {
                            statusIndicator.style.backgroundColor = '#00ff41';
                            statusIndicator.style.boxShadow = '0 0 10px #00ff41';
                        }
                        
                        // Play network activity sound
                        if (Math.random() < 0.3) {
                            terminalAudio.playNetworkActivity();
                        }
                        
                    } catch (error) {
                        console.error('Error loading dashboard data:', error);
                        document.getElementById('uptime').textContent = 'Connection Error';
                        document.getElementById('latency').textContent = 'N/A';
                        document.getElementById('guilds').textContent = 'N/A';
                        document.getElementById('commands').textContent = 'N/A';
                        
                        // Update status indicator to error state
                        const statusIndicator = document.querySelector('.status-indicator');
                        if (statusIndicator) {
                            statusIndicator.style.backgroundColor = '#ff4444';
                            statusIndicator.style.boxShadow = '0 0 10px #ff4444';
                        }
                        
                        terminalAudio.playErrorBeep();
                    }
                }</old_str>
                
                // Add ambient terminal sounds
                function startAmbientSounds() {
                    setInterval(() => {
                        const rand = Math.random();
                        if (rand < 0.15) { // 15% chance for processing sequence
                            terminalAudio.playProcessingSequence();
                        } else if (rand < 0.25) { // 10% chance for single beep
                            terminalAudio.playDataBeep();
                        }
                    }, 8000); // Every 8 seconds
                }
                
                // Load data on page load
                loadDashboardData();
                
                // Play startup sequence after delay
                setTimeout(() => {
                    terminalAudio.playStartupSequence();
                }, 2000);
                
                // Start enhanced ambient sounds after a delay
                setTimeout(startEnhancedAmbientSounds, 5000);</old_str>
                
                // Refresh data every 30 seconds
                setInterval(loadDashboardData, 30000);
                
                // Add click sound effects
                document.addEventListener('click', () => {
                    terminalAudio.playKeyClick();
                });
                
                // Sound control function
                function toggleSound() {
                    const isEnabled = terminalAudio.toggleSound();
                    const button = document.getElementById('soundToggle');
                    
                    if (isEnabled) {
                        button.textContent = '🔊 Sound: ON';
                        button.classList.remove('muted');
                        terminalAudio.playSystemBeep();
                    } else {
                        button.textContent = '🔇 Sound: OFF';
                        button.classList.add('muted');
                    }
                }
                
                // Add hover sound effects for cards
                document.querySelectorAll('.stat-card, .feature-card').forEach(card => {
                    card.addEventListener('mouseenter', () => {
                        if (Math.random() < 0.6) { // 60% chance for hover sound
                            terminalAudio.playKeyClick();
                        }
                    });
                });
                
                // Enhanced ambient sounds with variety
                function startEnhancedAmbientSounds() {
                    setInterval(() => {
                        const rand = Math.random();
                        if (rand < 0.1) { // 10% chance for processing sequence
                            terminalAudio.playProcessingSequence();
                        } else if (rand < 0.18) { // 8% chance for data beep
                            terminalAudio.playDataBeep();
                        } else if (rand < 0.23) { // 5% chance for system beep
                            terminalAudio.playSystemBeep();
                        }
                    }, 12000); // Every 12 seconds
                }</old_str>
            </script>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def serve_api_stats(self):
        """Serve API statistics"""
        try:
            # Try to load bot stats from storage
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                stats = loop.run_until_complete(self.storage.load_bot_stats())
                if not stats:
                    stats = {
                        'uptime': 'Unknown',
                        'latency': 0,
                        'guilds': 0,
                        'commands_executed': 0,
                        'status': 'Unknown'
                    }
            except Exception as e:
                stats = {
                    'uptime': 'Error loading',
                    'latency': 0,
                    'guilds': 0,
                    'commands_executed': 0,
                    'status': 'Error',
                    'error': str(e)
                }
            finally:
                loop.close()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(stats).encode())
            
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def serve_api_commands(self):
        """Serve API command statistics"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                commands = loop.run_until_complete(self.storage.load_command_stats())
                if not commands:
                    commands = {}
            except Exception as e:
                commands = {'error': str(e)}
            finally:
                loop.close()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(commands).encode())
            
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def serve_api_health(self):
        """Serve API health check"""
        health_data = {
            'status': 'operational',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '2.5.7',
            'system': 'FROST AI'
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(health_data).encode())
    
    def serve_static_file(self, path):
        """Serve static files"""
        self.send_error(404, "Static files not implemented")
    
    def log_message(self, format, *args):
        """Override to reduce logging noise"""
        return

def run_dashboard_server():
    """Run the dashboard server"""
    server_address = ('0.0.0.0', 5000)
    httpd = HTTPServer(server_address, FROSTDashboardHandler)
    print(f"🌐 FROST AI Dashboard starting on http://0.0.0.0:5000")
    print("🤖 Web interface ready for monitoring")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Dashboard server shutting down...")
        httpd.shutdown()

if __name__ == "__main__":
    run_dashboard_server()