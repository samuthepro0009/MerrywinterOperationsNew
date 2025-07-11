"""
Smart Notifications System for FROST AI
Context-aware notification system with priority levels
"""

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import json
import asyncio
from enum import Enum

from config.settings import Config
from utils.helpers import get_user_clearance, create_embed
from utils.storage import Storage

class NotificationPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class SmartNotifications(commands.Cog):
    """Smart notification system with context awareness"""
    
    def __init__(self, bot):
        self.bot = bot
        self.storage = Storage()
        self.notification_queue = []
        self.user_preferences = {}
        self.notification_history = {}
    
    def cog_check(self, ctx):
        """Check if command is used in authorized guild"""
        return Config.check_guild_authorization(ctx.guild.id)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check if interaction is in authorized guild"""
        return Config.check_guild_authorization(interaction.guild.id)
    
    async def send_smart_notification(self, title, message, priority, target_users=None, target_roles=None, channel=None):
        """Send a smart notification with priority handling"""
        notification = {
            'id': f"notif_{int(datetime.utcnow().timestamp())}",
            'title': title,
            'message': message,
            'priority': priority.value,
            'target_users': target_users or [],
            'target_roles': target_roles or [],
            'channel': channel,
            'timestamp': datetime.utcnow().isoformat(),
            'sent': False
        }
        
        # Get priority configuration
        priority_config = Config.NOTIFICATION_PRIORITIES[priority.value]
        
        # Create embed
        embed = discord.Embed(
            title=f"🔔 {title}",
            description=message,
            color=priority_config['color'],
            timestamp=datetime.utcnow()
        )
        
        # Add priority indicator
        priority_emoji = {
            'critical': '🚨',
            'high': '⚠️',
            'medium': '🔵',
            'low': '🟢'
        }
        
        embed.add_field(
            name="📊 Priority",
            value=f"{priority_emoji[priority.value]} {priority.value.upper()}",
            inline=True
        )
        
        if priority_config['urgent']:
            embed.add_field(
                name="⚡ Status",
                value="URGENT",
                inline=True
            )
        
        embed.set_footer(text=f"F.R.O.S.T AI • {Config.AI_VERSION}")
        
        # Determine where to send
        if channel:
            target_channel = channel
        elif hasattr(self.bot, 'moderation_log_channel') and self.bot.moderation_log_channel:
            target_channel = self.bot.moderation_log_channel
        else:
            target_channel = None
        
        # Send to channel
        if target_channel:
            content = ""
            if priority_config['ping_roles'] and target_roles:
                for role_name in target_roles:
                    role = discord.utils.get(target_channel.guild.roles, name=role_name)
                    if role:
                        content += f"{role.mention} "
            
            try:
                await target_channel.send(content=content, embed=embed)
                notification['sent'] = True
            except Exception as e:
                print(f"Failed to send notification: {e}")
        
        # Send DMs to specific users
        if target_users:
            for user_id in target_users:
                try:
                    user = self.bot.get_user(user_id)
                    if user:
                        await user.send(embed=embed)
                except:
                    pass  # Ignore if can't send DM
        
        # Store notification
        self.notification_queue.append(notification)
        await self.storage.save_notifications(self.notification_queue)
        
        return notification['id']
    
    @app_commands.command(name="send-notification", description="Send a notification (Admin only)")
    @app_commands.describe(
        title="Notification title",
        message="Notification message",
        priority="Priority level (critical, high, medium, low)",
        target_roles="Target roles (comma-separated)",
        target_channel="Target channel"
    )
    async def send_notification(self, interaction: discord.Interaction, title: str, message: str, priority: str, target_roles: str = None, target_channel: discord.TextChannel = None):
        """Send a notification"""
        # Check permissions
        if not Config.is_moderator([role.name for role in interaction.user.roles], interaction.user.id):
            await interaction.response.send_message("❌ You don't have permission to send notifications.", ephemeral=True)
            return
        
        # Validate priority
        try:
            priority_enum = NotificationPriority(priority.lower())
        except ValueError:
            await interaction.response.send_message(
                "❌ Invalid priority. Valid priorities: critical, high, medium, low",
                ephemeral=True
            )
            return
        
        # Parse target roles
        target_roles_list = None
        if target_roles:
            target_roles_list = [role.strip() for role in target_roles.split(',')]
        
        # Send notification
        notification_id = await self.send_smart_notification(
            title=title,
            message=message,
            priority=priority_enum,
            target_roles=target_roles_list,
            channel=target_channel
        )
        
        await interaction.response.send_message(
            f"✅ Notification sent successfully. ID: `{notification_id}`",
            ephemeral=True
        )
    
    @app_commands.command(name="notification-settings", description="Configure notification preferences")
    @app_commands.describe(
        priority_filter="Minimum priority level to receive (critical, high, medium, low)",
        enable_dms="Enable direct message notifications"
    )
    async def notification_settings(self, interaction: discord.Interaction, priority_filter: str = None, enable_dms: bool = None):
        """Configure notification preferences"""
        user_id = interaction.user.id
        
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {
                'priority_filter': 'medium',
                'enable_dms': True,
                'quiet_hours': None
            }
        
        settings = self.user_preferences[user_id]
        
        # Update settings
        if priority_filter:
            if priority_filter.lower() in ['critical', 'high', 'medium', 'low']:
                settings['priority_filter'] = priority_filter.lower()
            else:
                await interaction.response.send_message(
                    "❌ Invalid priority filter. Valid options: critical, high, medium, low",
                    ephemeral=True
                )
                return
        
        if enable_dms is not None:
            settings['enable_dms'] = enable_dms
        
        # Save settings
        await self.storage.save_user_preferences(self.user_preferences)
        
        # Show current settings
        embed = discord.Embed(
            title="🔔 Notification Settings",
            description="**Your notification preferences**",
            color=Config.COLORS['info'],
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="📊 Priority Filter", value=settings['priority_filter'].title(), inline=True)
        embed.add_field(name="📧 Direct Messages", value="Enabled" if settings['enable_dms'] else "Disabled", inline=True)
        
        if settings['quiet_hours']:
            embed.add_field(name="🌙 Quiet Hours", value=f"{settings['quiet_hours']['start']} - {settings['quiet_hours']['end']}", inline=True)
        
        embed.set_footer(text=f"F.R.O.S.T AI • {Config.AI_VERSION}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="notification-history", description="View recent notifications")
    async def notification_history(self, interaction: discord.Interaction):
        """View notification history"""
        if not self.notification_queue:
            await interaction.response.send_message("📋 No notifications in history.", ephemeral=True)
            return
        
        # Get recent notifications
        recent_notifications = sorted(
            self.notification_queue,
            key=lambda x: x['timestamp'],
            reverse=True
        )[:10]
        
        embed = discord.Embed(
            title="📋 Recent Notifications",
            description="**Notification History**",
            color=Config.COLORS['info'],
            timestamp=datetime.utcnow()
        )
        
        for notif in recent_notifications:
            timestamp = datetime.fromisoformat(notif['timestamp'])
            priority_emoji = {
                'critical': '🚨',
                'high': '⚠️',
                'medium': '🔵',
                'low': '🟢'
            }
            
            embed.add_field(
                name=f"{priority_emoji[notif['priority']]} {notif['title']}",
                value=f"**Message:** {notif['message'][:100]}{'...' if len(notif['message']) > 100 else ''}\n"
                      f"**Priority:** {notif['priority'].title()}\n"
                      f"**Time:** <t:{int(timestamp.timestamp())}:R>",
                inline=False
            )
        
        embed.set_footer(text=f"F.R.O.S.T AI • {Config.AI_VERSION}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def detect_context_notifications(self, guild):
        """Detect context-based notifications"""
        current_time = datetime.utcnow()
        
        # Check for low activity (no messages in 2 hours)
        if hasattr(self.bot, 'last_message_time'):
            if current_time - self.bot.last_message_time > timedelta(hours=2):
                await self.send_smart_notification(
                    title="Low Activity Detected",
                    message="Server activity has been low for the past 2 hours. Consider checking if everything is operational.",
                    priority=NotificationPriority.MEDIUM,
                    target_roles=["Administrator", "Moderator"]
                )
        
        # Check for high voice channel activity
        total_voice_members = sum(len(channel.members) for channel in guild.voice_channels)
        if total_voice_members > 20:  # Threshold for high activity
            await self.send_smart_notification(
                title="High Voice Activity",
                message=f"High voice channel activity detected: {total_voice_members} members in voice channels.",
                priority=NotificationPriority.LOW,
                target_roles=["Administrator"]
            )
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Track message activity for context awareness"""
        if message.author.bot or not Config.check_guild_authorization(message.guild.id):
            return
        
        # Update last message time
        self.bot.last_message_time = datetime.utcnow()
        
        # Check for emergency keywords
        emergency_keywords = ['emergency', 'urgent', 'help needed', 'mayday', 'crisis']
        
        if any(keyword in message.content.lower() for keyword in emergency_keywords):
            await self.send_smart_notification(
                title="Emergency Alert",
                message=f"Emergency keyword detected in message from {message.author.mention} in {message.channel.mention}",
                priority=NotificationPriority.CRITICAL,
                target_roles=["Administrator", "Moderator"]
            )
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Send notifications for new members"""
        if not Config.check_guild_authorization(member.guild.id):
            return
        
        # Check account age
        account_age = datetime.utcnow() - member.created_at
        
        if account_age.days < 7:  # New account
            await self.send_smart_notification(
                title="New Account Alert",
                message=f"New member {member.mention} has a very recent account (created {account_age.days} days ago).",
                priority=NotificationPriority.HIGH,
                target_roles=["Moderator"]
            )
        
        # Welcome notification
        await self.send_smart_notification(
            title="New Member",
            message=f"Welcome {member.mention} to {member.guild.name}!",
            priority=NotificationPriority.LOW,
            target_roles=["Moderator"]
        )

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(SmartNotifications(bot))