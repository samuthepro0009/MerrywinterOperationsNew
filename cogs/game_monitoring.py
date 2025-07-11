"""
Automated Roblox Game Server Status Notifications for FROST AI
Real-time monitoring and notification system for PMC game servers
"""

import discord
from discord.ext import commands, tasks
from discord import app_commands
import aiohttp
import asyncio
import json
from datetime import datetime, timedelta
from config.settings import Config
from utils.helpers import create_embed
from utils.storage import Storage

class GameMonitoring(commands.Cog):
    """Automated game server monitoring and notification system"""
    
    def __init__(self, bot):
        self.bot = bot
        self.storage = Storage()
        self.session = None
        self.previous_status = {}
        self.monitoring_enabled = False
        self.notification_channel = None
        self.alert_thresholds = {
            'low_players': 5,      # Alert when players drop below this
            'high_players': 50,    # Alert when players exceed this
            'server_down': 0,      # Alert when no players (server down)
            'rapid_change': 20     # Alert on rapid player count changes
        }
        
    async def cog_load(self):
        """Initialize monitoring system"""
        self.session = aiohttp.ClientSession()
        await self._load_monitoring_config()
        if self.monitoring_enabled:
            self.game_monitor.start()
    
    async def cog_unload(self):
        """Cleanup monitoring system"""
        if self.session:
            await self.session.close()
        if self.game_monitor.is_running():
            self.game_monitor.cancel()
    
    def cog_check(self, ctx):
        """Check if command is used in authorized guild"""
        return Config.check_guild_authorization(ctx.guild.id)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check if interaction is in authorized guild"""
        return Config.check_guild_authorization(interaction.guild.id)
    
    async def _load_monitoring_config(self):
        """Load monitoring configuration from storage"""
        try:
            config = await self.storage.load_game_monitoring_config()
            self.monitoring_enabled = config.get('enabled', False)
            self.alert_thresholds = config.get('thresholds', self.alert_thresholds)
            
            # Get notification channel
            if config.get('notification_channel_id'):
                self.notification_channel = self.bot.get_channel(config['notification_channel_id'])
        except Exception as e:
            print(f"Error loading monitoring config: {e}")
    
    async def _save_monitoring_config(self):
        """Save monitoring configuration to storage"""
        config = {
            'enabled': self.monitoring_enabled,
            'thresholds': self.alert_thresholds,
            'notification_channel_id': self.notification_channel.id if self.notification_channel else None,
            'last_updated': datetime.utcnow().isoformat()
        }
        await self.storage.save_game_monitoring_config(config)
    
    async def _get_game_status(self):
        """Get current game server status"""
        if not Config.ROBLOX_UNIVERSE_ID or not self.session:
            return None
        
        try:
            # Get game activity
            url = f"{Config.ROBLOX_GAMES_API}/v1/games/{Config.ROBLOX_UNIVERSE_ID}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'data' in data and len(data['data']) > 0:
                        game_data = data['data'][0]
                        
                        # Get server list
                        servers_url = f"{Config.ROBLOX_GAMES_API}/v1/games/{Config.ROBLOX_UNIVERSE_ID}/servers/Public"
                        async with self.session.get(servers_url) as servers_response:
                            servers_data = []
                            if servers_response.status == 200:
                                servers_json = await servers_response.json()
                                servers_data = servers_json.get('data', [])
                        
                        return {
                            'name': game_data.get('name', 'Unknown Game'),
                            'playing': game_data.get('playing', 0),
                            'visits': game_data.get('visits', 0),
                            'max_players': game_data.get('maxPlayers', 0),
                            'active_servers': len(servers_data),
                            'servers': servers_data,
                            'timestamp': datetime.utcnow()
                        }
        except Exception as e:
            print(f"Error getting game status: {e}")
        
        return None
    
    @tasks.loop(minutes=2)  # Check every 2 minutes
    async def game_monitor(self):
        """Main monitoring loop"""
        if not self.monitoring_enabled or not self.notification_channel:
            return
        
        current_status = await self._get_game_status()
        if not current_status:
            return
        
        # Check for significant changes
        if self.previous_status:
            await self._check_for_alerts(current_status, self.previous_status)
        
        # Update previous status
        self.previous_status = current_status
        
        # Log status for tracking
        await self._log_server_status(current_status)
    
    async def _check_for_alerts(self, current, previous):
        """Check for conditions that should trigger alerts"""
        alerts = []
        
        # Server down alert
        if current['playing'] == 0 and previous['playing'] > 0:
            alerts.append({
                'type': 'server_down',
                'title': '🔴 Game Server Alert - Server Down',
                'description': f"**{current['name']}** appears to be offline",
                'color': Config.COLORS['error'],
                'priority': 'critical'
            })
        
        # Server back online
        elif current['playing'] > 0 and previous['playing'] == 0:
            alerts.append({
                'type': 'server_up',
                'title': '🟢 Game Server Alert - Server Online',
                'description': f"**{current['name']}** is back online with {current['playing']} players",
                'color': Config.COLORS['success'],
                'priority': 'high'
            })
        
        # Low player count
        elif current['playing'] <= self.alert_thresholds['low_players'] and previous['playing'] > self.alert_thresholds['low_players']:
            alerts.append({
                'type': 'low_players',
                'title': '🟡 Game Server Alert - Low Player Count',
                'description': f"**{current['name']}** player count dropped to {current['playing']}",
                'color': Config.COLORS['warning'],
                'priority': 'medium'
            })
        
        # High player count
        elif current['playing'] >= self.alert_thresholds['high_players'] and previous['playing'] < self.alert_thresholds['high_players']:
            alerts.append({
                'type': 'high_players',
                'title': '🔥 Game Server Alert - High Activity',
                'description': f"**{current['name']}** reached {current['playing']} players!",
                'color': Config.COLORS['success'],
                'priority': 'medium'
            })
        
        # Rapid change detection
        player_change = abs(current['playing'] - previous['playing'])
        if player_change >= self.alert_thresholds['rapid_change']:
            change_type = "increased" if current['playing'] > previous['playing'] else "decreased"
            alerts.append({
                'type': 'rapid_change',
                'title': f'⚡ Game Server Alert - Rapid Activity Change',
                'description': f"**{current['name']}** player count {change_type} by {player_change} ({previous['playing']} → {current['playing']})",
                'color': Config.COLORS['info'],
                'priority': 'low'
            })
        
        # Send alerts
        for alert in alerts:
            await self._send_alert(alert, current, previous)
    
    async def _send_alert(self, alert, current_status, previous_status):
        """Send alert notification to Discord"""
        embed = create_embed(
            title=alert['title'],
            description=alert['description'],
            color=alert['color']
        )
        
        # Add detailed information
        embed.add_field(name="Current Players", value=f"{current_status['playing']:,}", inline=True)
        embed.add_field(name="Previous Players", value=f"{previous_status['playing']:,}", inline=True)
        embed.add_field(name="Active Servers", value=f"{current_status['active_servers']}", inline=True)
        
        embed.add_field(name="Total Visits", value=f"{current_status['visits']:,}", inline=True)
        embed.add_field(name="Max Capacity", value=f"{current_status['max_players']:,}", inline=True)
        embed.add_field(name="Time", value=f"<t:{int(current_status['timestamp'].timestamp())}:R>", inline=True)
        
        # Add server details if available
        if current_status['servers']:
            server_info = []
            for i, server in enumerate(current_status['servers'][:3], 1):  # Show top 3 servers
                server_info.append(f"Server {i}: {server.get('playing', 0)}/{server.get('maxPlayers', 0)} players")
            
            if server_info:
                embed.add_field(name="Top Servers", value="\n".join(server_info), inline=False)
        
        embed.set_footer(text=f"F.R.O.S.T AI Game Monitor • Priority: {alert['priority'].upper()}")
        
        try:
            await self.notification_channel.send(embed=embed)
        except Exception as e:
            print(f"Error sending alert: {e}")
    
    async def _log_server_status(self, status):
        """Log server status for historical tracking"""
        log_entry = {
            'timestamp': status['timestamp'].isoformat(),
            'players': status['playing'],
            'active_servers': status['active_servers'],
            'total_visits': status['visits']
        }
        await self.storage.append_game_status_log(log_entry)
    
    @app_commands.command(name="setup-game-monitoring", description="Configure automated game server monitoring (Admin only)")
    @app_commands.describe(
        enable="Enable or disable monitoring",
        channel="Channel for notifications",
        low_threshold="Alert when players drop below this number",
        high_threshold="Alert when players exceed this number"
    )
    async def setup_game_monitoring(
        self, 
        interaction: discord.Interaction,
        enable: bool,
        channel: discord.TextChannel = None,
        low_threshold: int = 5,
        high_threshold: int = 50
    ):
        """Configure game server monitoring"""
        # Check permissions
        if not Config.is_moderator([role.name for role in interaction.user.roles], interaction.user.id):
            await interaction.response.send_message(
                "❌ Access denied. Administrator permissions required.",
                ephemeral=True
            )
            return
        
        # Update configuration
        self.monitoring_enabled = enable
        if channel:
            self.notification_channel = channel
        
        self.alert_thresholds['low_players'] = max(0, low_threshold)
        self.alert_thresholds['high_players'] = max(1, high_threshold)
        
        # Save configuration
        await self._save_monitoring_config()
        
        # Start/stop monitoring
        if enable and not self.game_monitor.is_running():
            self.game_monitor.start()
        elif not enable and self.game_monitor.is_running():
            self.game_monitor.cancel()
        
        # Create response embed
        embed = create_embed(
            title="🎮 Game Server Monitoring Configured",
            description=f"Monitoring has been {'enabled' if enable else 'disabled'}",
            color=Config.COLORS['success'] if enable else Config.COLORS['warning']
        )
        
        if enable:
            embed.add_field(name="Notification Channel", value=channel.mention if channel else "Not set", inline=True)
            embed.add_field(name="Low Player Alert", value=f"{low_threshold} players", inline=True)
            embed.add_field(name="High Player Alert", value=f"{high_threshold} players", inline=True)
            embed.add_field(name="Check Interval", value="Every 2 minutes", inline=True)
            embed.add_field(name="Game", value=Config.ROBLOX_UNIVERSE_ID or "Not configured", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="monitoring-status", description="Check game monitoring status")
    async def monitoring_status(self, interaction: discord.Interaction):
        """Check current monitoring status"""
        embed = create_embed(
            title="🎮 Game Server Monitoring Status",
            description="Current monitoring configuration and status",
            color=Config.COLORS['info']
        )
        
        embed.add_field(name="Monitoring", value="🟢 Enabled" if self.monitoring_enabled else "🔴 Disabled", inline=True)
        embed.add_field(name="Channel", value=self.notification_channel.mention if self.notification_channel else "Not set", inline=True)
        embed.add_field(name="Game ID", value=Config.ROBLOX_UNIVERSE_ID or "Not configured", inline=True)
        
        embed.add_field(name="Low Player Alert", value=f"{self.alert_thresholds['low_players']} players", inline=True)
        embed.add_field(name="High Player Alert", value=f"{self.alert_thresholds['high_players']} players", inline=True)
        embed.add_field(name="Rapid Change Alert", value=f"{self.alert_thresholds['rapid_change']} players", inline=True)
        
        if self.previous_status:
            embed.add_field(name="Last Check", value=f"<t:{int(self.previous_status['timestamp'].timestamp())}:R>", inline=True)
            embed.add_field(name="Current Players", value=f"{self.previous_status['playing']:,}", inline=True)
            embed.add_field(name="Active Servers", value=f"{self.previous_status['active_servers']}", inline=True)
        
        embed.add_field(name="Monitor Loop", value="🟢 Running" if self.game_monitor.is_running() else "🔴 Stopped", inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="force-status-check", description="Force an immediate server status check (Admin only)")
    async def force_status_check(self, interaction: discord.Interaction):
        """Force immediate status check"""
        # Check permissions
        if not Config.is_moderator([role.name for role in interaction.user.roles], interaction.user.id):
            await interaction.response.send_message(
                "❌ Access denied. Administrator permissions required.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        # Get current status
        current_status = await self._get_game_status()
        
        if not current_status:
            await interaction.followup.send(
                "❌ Unable to fetch game server status. Check game configuration.",
                ephemeral=True
            )
            return
        
        # Create status embed
        embed = create_embed(
            title=f"🎮 Current Server Status - {current_status['name']}",
            description="Real-time server information",
            color=Config.COLORS['frost']
        )
        
        embed.add_field(name="Players Online", value=f"{current_status['playing']:,}", inline=True)
        embed.add_field(name="Active Servers", value=f"{current_status['active_servers']}", inline=True)
        embed.add_field(name="Total Visits", value=f"{current_status['visits']:,}", inline=True)
        
        embed.add_field(name="Max Capacity", value=f"{current_status['max_players']:,}", inline=True)
        embed.add_field(name="Last Updated", value=f"<t:{int(current_status['timestamp'].timestamp())}:T>", inline=True)
        
        # Server status indicator
        if current_status['playing'] == 0:
            embed.add_field(name="Status", value="🔴 Offline/Empty", inline=True)
        elif current_status['playing'] <= self.alert_thresholds['low_players']:
            embed.add_field(name="Status", value="🟡 Low Activity", inline=True)
        elif current_status['playing'] >= self.alert_thresholds['high_players']:
            embed.add_field(name="Status", value="🔥 High Activity", inline=True)
        else:
            embed.add_field(name="Status", value="🟢 Normal", inline=True)
        
        # Add server details
        if current_status['servers']:
            server_list = []
            for i, server in enumerate(current_status['servers'][:5], 1):
                server_list.append(f"**Server {i}:** {server.get('playing', 0)}/{server.get('maxPlayers', 0)} players")
            
            if server_list:
                embed.add_field(name="Server Details", value="\n".join(server_list), inline=False)
        
        # Update previous status for monitoring
        if self.monitoring_enabled:
            old_status = self.previous_status
            self.previous_status = current_status
            
            # Check for alerts if we have previous data
            if old_status:
                await self._check_for_alerts(current_status, old_status)
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(GameMonitoring(bot))