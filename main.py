
"""
Merrywinter Security Consulting Discord Bot
Complete 24/7 PMC operations management system with integrated web dashboard
"""

import os
import asyncio
import logging
import threading
import time
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional

import discord
from discord.ext import commands, tasks
from discord import app_commands
from dotenv import load_dotenv

# Flask imports for web dashboard
try:
    from flask import Flask, render_template, jsonify, request
    from werkzeug.middleware.proxy_fix import ProxyFix
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

# Load environment variables
load_dotenv()

# Configuration
class Config:
    """Configuration settings for Merrywinter Security Consulting Bot"""
    
    # Bot Configuration
    COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '!')
    AUTHORIZED_GUILD_ID = 1114936846124843008
    
    # Company Information
    COMPANY_NAME = "Merrywinter Security Consulting"
    COMPANY_MOTTO = "Sub umbra, vincimus"
    
    # AI System Information
    AI_NAME = "F.R.O.S.T"
    AI_FULL_NAME = "Fully Responsive Operational Support Technician"
    AI_VERSION = "v2.5.7"
    
    # 24/7 Uptime Configuration
    ENABLE_KEEPALIVE = True
    KEEPALIVE_INTERVAL = 15
    HEALTH_CHECK_INTERVAL = 10
    AUTO_RESTART_ON_ERROR = True
    KEEPALIVE_PORT = 8080
    WEB_PORT = 5000
    
    # Colors
    COLORS = {
        'primary': 0x00ff41,
        'secondary': 0x0099ff,
        'success': 0x00ff00,
        'warning': 0xffa500,
        'error': 0xff0000,
        'info': 0x00ffff,
        'frost': 0x00ff41
    }
    
    # Security Clearance Levels
    SECURITY_LEVELS = {
        'EXECUTIVE_COMMAND': 10,
        'BOARD_OF_DIRECTORS': 9,
        'DEPARTMENT_DIRECTORS': 8,
        'COMMAND_LEVEL': 7,
        'SPECIALIZED_UNITS': 6,
        'OMEGA': 5,
        'BETA': 4,
        'ALPHA': 3,
        'ENLISTED': 2,
        'CIVILIAN': 1
    }
    
    # Role Configuration
    ADMIN_ROLES = ["Executive Command", "Board of Directors", "Executive Director"]
    MODERATOR_ROLES = ["Department Directors", "Director of Security Operations"]
    COMMAND_ROLES = ["Tactical Operations Section Command", "Intelligence and Security Section Command"]
    
    # Channel Configuration
    TICKET_CATEGORY_ID = 1393249646192754698
    LOG_CHANNEL_ID = 1393249520388935793
    DEPLOYMENT_CHANNEL_ID = 1393246091289559172
    OPERATION_LOG_CHANNEL_ID = 1393340130177191956
    
    @classmethod
    def check_guild_authorization(cls, guild_id: int) -> bool:
        return guild_id == cls.AUTHORIZED_GUILD_ID

# Storage System
class Storage:
    """Simple file-based storage system"""
    
    def __init__(self):
        self.data_dir = 'data'
        os.makedirs(self.data_dir, exist_ok=True)
    
    def load_data(self, filename: str) -> Dict:
        """Load data from JSON file"""
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}
    
    def save_data(self, filename: str, data: Dict):
        """Save data to JSON file"""
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

# Logger Setup
def setup_logger():
    """Setup logging configuration"""
    logger = logging.getLogger('MerrywinterBot')
    logger.setLevel(logging.INFO)
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # File handler
    file_handler = logging.FileHandler(
        f'logs/bot_{datetime.now().strftime("%Y%m%d")}.log',
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Global variables
logger = setup_logger()
storage = Storage()

# Keep-Alive Server
class KeepAliveServer:
    """Web server for 24/7 uptime monitoring"""
    
    def __init__(self, bot_instance, port=8080):
        self.bot = bot_instance
        self.port = port
        self.start_time = datetime.now(timezone.utc)
        
        if FLASK_AVAILABLE:
            self.app = Flask(__name__)
            self.app.secret_key = os.environ.get("SESSION_SECRET", "frost-ai-secret")
            self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask routes"""
        if not FLASK_AVAILABLE:
            return
        
        @self.app.route('/')
        def home():
            uptime = datetime.now(timezone.utc) - self.start_time
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>FROST AI - Keep Alive</title>
                <meta http-equiv="refresh" content="30">
                <style>
                    body {{ font-family: Arial, sans-serif; background: #1a1a1a; color: #00ff41; padding: 20px; }}
                    .card {{ background: #2a2a2a; padding: 20px; margin: 10px 0; border-radius: 5px; }}
                    .metric {{ font-size: 18px; font-weight: bold; color: #00ff41; }}
                </style>
            </head>
            <body>
                <h1>🤖 FROST AI Keep-Alive Service</h1>
                <div class="card">
                    <h3>Service Status</h3>
                    <p>✅ Status: <span class="metric">ONLINE</span></p>
                    <p>⏰ Uptime: <span class="metric">{str(uptime).split('.')[0]}</span></p>
                    <p>🔄 Auto-refresh: <span class="metric">30 seconds</span></p>
                </div>
                <div class="card">
                    <h3>Discord Bot Status</h3>
                    <p>📡 Connection: <span class="metric">{"ONLINE" if self.bot.is_ready() else "OFFLINE"}</span></p>
                    <p>🏓 Latency: <span class="metric">{round(self.bot.latency * 1000) if self.bot.latency else 0}ms</span></p>
                    <p>🔗 Guilds: <span class="metric">{len(self.bot.guilds)}</span></p>
                </div>
                <div class="card">
                    <h3>API Endpoints</h3>
                    <p><a href="/ping" style="color: #00ff41;">/ping</a> - Basic ping</p>
                    <p><a href="/health" style="color: #00ff41;">/health</a> - Health check</p>
                    <p><a href="/stats" style="color: #00ff41;">/stats</a> - Bot statistics</p>
                </div>
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
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "discord_bot": {
                    "ready": self.bot.is_ready(),
                    "latency": round(self.bot.latency * 1000) if self.bot.latency else 0,
                    "guilds": len(self.bot.guilds)
                }
            })
        
        @self.app.route('/stats')
        def stats():
            bot_stats = storage.load_data('bot_stats.json')
            return jsonify({
                "uptime_seconds": (datetime.now(timezone.utc) - self.start_time).total_seconds(),
                "discord_ready": self.bot.is_ready(),
                "guilds": len(self.bot.guilds),
                "latency": round(self.bot.latency * 1000) if self.bot.latency else 0,
                "commands_processed": bot_stats.get('commands_processed', 0),
                "last_updated": datetime.now(timezone.utc).isoformat()
            })
    
    def run(self):
        """Run the keep-alive server"""
        if not FLASK_AVAILABLE:
            logger.warning("Flask not available - running basic HTTP server")
            self.run_basic_server()
            return
        
        try:
            self.app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)
        except Exception as e:
            logger.error(f"Keep-alive server error: {e}")
            self.run_basic_server()
    
    def run_basic_server(self):
        """Fallback HTTP server when Flask is not available"""
        import http.server
        import socketserver
        
        class Handler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                uptime = datetime.now(timezone.utc) - self.server.start_time
                html = f"""
                <!DOCTYPE html>
                <html>
                <head><title>FROST AI Keep-Alive</title></head>
                <body style="font-family: Arial; background: #1a1a1a; color: #00ff41; padding: 20px;">
                <h1>🤖 FROST AI Keep-Alive Service</h1>
                <p>✅ Status: ONLINE</p>
                <p>⏰ Uptime: {str(uptime).split('.')[0]}</p>
                <p>📡 Discord Bot: {"ONLINE" if self.server.bot.is_ready() else "OFFLINE"}</p>
                <p>🔄 Auto-refresh: 30 seconds</p>
                <meta http-equiv="refresh" content="30">
                </body>
                </html>
                """
                self.wfile.write(html.encode())
        
        with socketserver.TCPServer(("0.0.0.0", self.port), Handler) as httpd:
            httpd.start_time = self.start_time
            httpd.bot = self.bot
            logger.info(f"✅ Basic keep-alive server running on port {self.port}")
            httpd.serve_forever()

# Main Bot Class
class MerrywinterBot(commands.Bot):
    """Main Discord bot for Merrywinter Security Consulting"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        
        super().__init__(
            command_prefix=Config.COMMAND_PREFIX,
            intents=intents,
            help_command=None,
            description="F.R.O.S.T AI - PMC Operations Management System"
        )
        
        self.config = Config()
        self.storage = storage
        self.start_time = datetime.now(timezone.utc)
        self.last_heartbeat = datetime.now(timezone.utc)
        
        # Stats tracking
        self.command_usage_stats = {}
        self.bot_stats = {}
        
        # Keep-alive server
        self.keep_alive_server = None
        self.keep_alive_thread = None
    
    async def setup_hook(self):
        """Setup the bot"""
        try:
            # Add essential slash commands - create them properly
            @app_commands.command(name='help', description='Display help information')
            async def help_cmd(interaction: discord.Interaction):
                await self.help_command(interaction)
            
            @app_commands.command(name='info', description='Display bot information')
            async def info_cmd(interaction: discord.Interaction):
                await self.info_command(interaction)
            
            @app_commands.command(name='ping', description='Check bot latency')
            async def ping_cmd(interaction: discord.Interaction):
                await self.ping_command(interaction)
            
            @app_commands.command(name='clearance', description='Check security clearance level')
            async def clearance_cmd(interaction: discord.Interaction):
                await self.clearance_command(interaction)
            
            @app_commands.command(name='status', description='Check bot system status')
            async def status_cmd(interaction: discord.Interaction):
                await self.status_command(interaction)
            
            # Add commands to tree
            self.tree.add_command(help_cmd)
            self.tree.add_command(info_cmd)
            self.tree.add_command(ping_cmd)
            self.tree.add_command(clearance_cmd)
            self.tree.add_command(status_cmd)
            
            # Load available cogs
            available_cogs = [
                'cogs.tickets',
                'cogs.security', 
                'cogs.operations',
                'cogs.moderation',
                'cogs.admin',
                'cogs.high_command',
                'cogs.communications',
                'cogs.alerts',
                'cogs.audit',
                'cogs.intelligence'
            ]
            
            for cog in available_cogs:
                try:
                    # Check if cog file exists
                    cog_path = cog.replace('.', '/') + '.py'
                    if os.path.exists(cog_path):
                        await self.load_extension(cog)
                        logger.info(f"✅ Loaded cog: {cog}")
                    else:
                        logger.warning(f"⚠️ Cog file not found: {cog_path}")
                except Exception as e:
                    logger.error(f"❌ Failed to load cog {cog}: {e}")
                    # Continue loading other cogs even if one fails
            
            # Sync slash commands
            try:
                synced = await self.tree.sync()
                logger.info(f"Synced {len(synced)} slash commands globally")
            except Exception as e:
                logger.error(f"Failed to sync slash commands: {e}")
            
            # Start background tasks
            self.status_update.start()
            
            if Config.ENABLE_KEEPALIVE:
                self.keep_alive_task.start()
                self.health_monitor.start()
            
        except Exception as e:
            logger.error(f"Error in setup_hook: {e}")
    
    async def on_ready(self):
        """Bot ready event"""
        logger.info(f"Bot logged in as {self.user}")
        logger.info(f"Bot is ready in {len(self.guilds)} guilds")
        
        # Start keep-alive server
        if Config.ENABLE_KEEPALIVE:
            self.start_keep_alive_server()
        
        # Set status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="PMC Operations | /help"
            ),
            status=discord.Status.online
        )
    
    def start_keep_alive_server(self):
        """Start the keep-alive server in a separate thread"""
        if self.keep_alive_server is None:
            self.keep_alive_server = KeepAliveServer(self, Config.KEEPALIVE_PORT)
            self.keep_alive_thread = threading.Thread(
                target=self.keep_alive_server.run,
                daemon=True
            )
            self.keep_alive_thread.start()
            logger.info(f"✅ Keep-alive server started on port {Config.KEEPALIVE_PORT}")
    
    async def on_guild_join(self, guild):
        """Handle guild join"""
        logger.info(f"Joined guild: {guild.name} (ID: {guild.id})")
        
        if not Config.check_guild_authorization(guild.id):
            logger.warning(f"Unauthorized guild - leaving: {guild.name}")
            await guild.leave()
            return
        
        # Send welcome message
        if guild.system_channel:
            embed = discord.Embed(
                title=f"🚁 {Config.COMPANY_NAME}",
                description=f"**{Config.COMPANY_MOTTO}**\n\n"
                           "**Getting Started:**\n"
                           "• Use `/help` to see all commands\n"
                           "• Use `/info` for bot information\n"
                           "• Use `/ping` to check latency\n\n"
                           "**Key Features:**\n"
                           "• Ticket System\n"
                           "• Security Clearance\n"
                           "• Operations Management\n"
                           "• Moderation Tools",
                color=Config.COLORS['primary']
            )
            embed.set_footer(text=f"{Config.COMPANY_NAME} - Professional PMC Operations")
            await guild.system_channel.send(embed=embed)
    
    @tasks.loop(minutes=30)
    async def status_update(self):
        """Update bot status periodically"""
        try:
            await self.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name=f"PMC Operations | {len(self.guilds)} guilds"
                ),
                status=discord.Status.online
            )
        except Exception as e:
            logger.error(f"Error updating status: {e}")
    
    @tasks.loop(minutes=Config.KEEPALIVE_INTERVAL)
    async def keep_alive_task(self):
        """Keep-alive ping task"""
        try:
            self.last_heartbeat = datetime.now(timezone.utc)
            
            # Update bot stats
            self.bot_stats.update({
                'last_heartbeat': self.last_heartbeat.isoformat(),
                'uptime_hours': round((datetime.now(timezone.utc) - self.start_time).total_seconds() / 3600, 2),
                'guilds': len(self.guilds),
                'latency': round(self.latency * 1000) if self.latency else 0
            })
            
            # Save stats
            storage.save_data('bot_stats.json', self.bot_stats)
            
            logger.info("✅ Keep-alive ping successful")
            
        except Exception as e:
            logger.error(f"Keep-alive error: {e}")
    
    @tasks.loop(minutes=Config.HEALTH_CHECK_INTERVAL)
    async def health_monitor(self):
        """Health monitoring task"""
        try:
            uptime = datetime.now(timezone.utc) - self.start_time
            uptime_hours = round(uptime.total_seconds() / 3600, 2)
            
            logger.info(f"🤖 FROST AI Health Check - Uptime: {uptime_hours}h | Guilds: {len(self.guilds)} | Latency: {round(self.latency * 1000)}ms")
            
            # Check for connection issues
            if (datetime.now(timezone.utc) - self.last_heartbeat).total_seconds() > 3600:
                logger.warning("⚠️ Bot heartbeat delayed - potential connection issues")
                
                if Config.AUTO_RESTART_ON_ERROR:
                    logger.info("🔄 Attempting to refresh connection...")
                    await self.change_presence(
                        activity=discord.Activity(
                            type=discord.ActivityType.watching,
                            name="Systems Recovering..."
                        ),
                        status=discord.Status.idle
                    )
                    await asyncio.sleep(5)
                    await self.change_presence(
                        activity=discord.Activity(
                            type=discord.ActivityType.watching,
                            name="PMC Operations | /help"
                        ),
                        status=discord.Status.online
                    )
            
        except Exception as e:
            logger.error(f"Health monitor error: {e}")
    
    @status_update.before_loop
    async def before_status_update(self):
        await self.wait_until_ready()
    
    @keep_alive_task.before_loop
    async def before_keep_alive_task(self):
        await self.wait_until_ready()
    
    @health_monitor.before_loop
    async def before_health_monitor(self):
        await self.wait_until_ready()
    
    # Slash Commands
    async def help_command(self, interaction: discord.Interaction):
        """Display help information"""
        embed = discord.Embed(
            title="🚁 F.R.O.S.T AI Command Center",
            description=f"**{Config.COMPANY_NAME}** - {Config.COMPANY_MOTTO}",
            color=Config.COLORS['primary']
        )
        
        embed.add_field(
            name="📋 **Essential Commands**",
            value="• `/help` - Show this help menu\n"
                  "• `/info` - Bot information\n"
                  "• `/ping` - Check bot latency\n"
                  "• `/status` - System status\n"
                  "• `/clearance` - Check security clearance",
            inline=False
        )
        
        embed.add_field(
            name="🎫 **Available Systems**",
            value="• Ticket System\n"
                  "• Security Clearance\n"
                  "• Operations Management\n"
                  "• Moderation Tools\n"
                  "• Administrative Commands",
            inline=False
        )
        
        embed.set_footer(text=f"{Config.COMPANY_NAME} - Professional PMC Operations")
        await interaction.response.send_message(embed=embed)
    
    async def info_command(self, interaction: discord.Interaction):
        """Display bot information"""
        uptime = datetime.now(timezone.utc) - self.start_time
        
        embed = discord.Embed(
            title="🤖 F.R.O.S.T AI Information",
            description=f"**{Config.COMPANY_NAME}**\n{Config.COMPANY_MOTTO}",
            color=Config.COLORS['primary']
        )
        
        embed.add_field(
            name="📊 **Statistics**",
            value=f"**Uptime:** {str(uptime).split('.')[0]}\n"
                  f"**Guilds:** {len(self.guilds)}\n"
                  f"**Latency:** {round(self.latency * 1000)}ms\n"
                  f"**Version:** {Config.AI_VERSION}",
            inline=False
        )
        
        embed.add_field(
            name="🔧 **System Features**",
            value="**24/7 Uptime:** ✅ Enabled\n"
                  "**Keep-Alive Server:** ✅ Running\n"
                  "**Health Monitor:** ✅ Active\n"
                  "**Auto-Recovery:** ✅ Enabled",
            inline=False
        )
        
        embed.set_footer(text=f"{Config.COMPANY_NAME} - Professional PMC Operations")
        await interaction.response.send_message(embed=embed)
    
    async def ping_command(self, interaction: discord.Interaction):
        """Check bot latency"""
        latency = round(self.latency * 1000)
        
        if latency < 100:
            status = "🟢 Excellent"
        elif latency < 200:
            status = "🟡 Good"
        else:
            status = "🔴 Poor"
        
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"**Latency:** {latency}ms\n"
                       f"**Status:** {status}",
            color=Config.COLORS['primary']
        )
        embed.set_footer(text=f"{Config.COMPANY_NAME} - Network Diagnostics")
        await interaction.response.send_message(embed=embed)
    
    async def clearance_command(self, interaction: discord.Interaction):
        """Check security clearance level"""
        user_roles = [role.name for role in interaction.user.roles]
        
        # Determine clearance level
        clearance_level = "CIVILIAN"
        for role in user_roles:
            if role in Config.ADMIN_ROLES:
                clearance_level = "EXECUTIVE_COMMAND"
                break
            elif role in Config.MODERATOR_ROLES:
                clearance_level = "DEPARTMENT_DIRECTORS"
                break
            elif role in Config.COMMAND_ROLES:
                clearance_level = "COMMAND_LEVEL"
                break
        
        embed = discord.Embed(
            title="🔒 Security Clearance Check",
            description=f"**Operator:** {interaction.user.mention}\n"
                       f"**Clearance Level:** {clearance_level}\n"
                       f"**Access Level:** {Config.SECURITY_LEVELS.get(clearance_level, 1)}",
            color=Config.COLORS['primary']
        )
        
        embed.set_footer(text=f"{Config.COMPANY_NAME} - Security Division")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def status_command(self, interaction: discord.Interaction):
        """Check bot system status"""
        uptime = datetime.now(timezone.utc) - self.start_time
        
        embed = discord.Embed(
            title="📊 System Status Report",
            description=f"**{Config.AI_FULL_NAME}** - {Config.AI_VERSION}",
            color=Config.COLORS['success']
        )
        
        embed.add_field(
            name="🤖 Bot Status",
            value=f"**Status:** 🟢 Online\n"
                  f"**Uptime:** {str(uptime).split('.')[0]}\n"
                  f"**Latency:** {round(self.latency * 1000)}ms\n"
                  f"**Guilds:** {len(self.guilds)}",
            inline=True
        )
        
        embed.add_field(
            name="🔧 System Health",
            value=f"**Keep-Alive:** ✅ Active\n"
                  f"**Health Monitor:** ✅ Running\n"
                  f"**Auto-Recovery:** ✅ Enabled\n"
                  f"**Web Dashboard:** ✅ Online",
            inline=True
        )
        
        embed.set_footer(text=f"{Config.COMPANY_NAME} - Systems Monitoring")
        await interaction.response.send_message(embed=embed)
    
    async def close(self):
        """Clean shutdown"""
        try:
            # Cancel tasks
            if hasattr(self, 'status_update'):
                self.status_update.cancel()
            if hasattr(self, 'keep_alive_task'):
                self.keep_alive_task.cancel()
            if hasattr(self, 'health_monitor'):
                self.health_monitor.cancel()
            
            logger.info("🔄 FROST AI shutting down gracefully...")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        finally:
            await super().close()

# Main function
async def main():
    """Main function to run the bot"""
    bot = MerrywinterBot()
    
    # Get bot token
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        logger.error("❌ DISCORD_TOKEN environment variable not found!")
        logger.error("Please set your Discord bot token in the Secrets tab or .env file")
        return
    
    try:
        logger.info("🚀 Starting FROST AI Discord Bot...")
        await bot.start(token)
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        await bot.close()

# Entry point
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
    except Exception as e:
        logger.error(f"Critical error: {e}")
