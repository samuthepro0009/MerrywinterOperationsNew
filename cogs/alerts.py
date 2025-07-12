"""
Alert System for Merrywinter Security Consulting
Emergency broadcasts, priority notifications, and alert management
"""

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import json
from datetime import datetime, timedelta
from config.settings import Config
from utils.helpers import get_user_clearance
from utils.storage import Storage

class AlertSystem(commands.Cog):
    """Advanced alert and notification system"""

    def __init__(self, bot):
        self.bot = bot
        self.storage = Storage()
        self.active_alerts = {}
        self.alert_history = []

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check if interaction is in authorized guild"""
        return Config.check_guild_authorization(interaction.guild.id)

    @app_commands.command(name="emergency_alert", description="Broadcast emergency alert (Executive Command only)")
    @app_commands.describe(
        alert_type="Type of emergency alert",
        severity="Severity level of the alert",
        message="Alert message content",
        duration="Duration in minutes (max 60)"
    )
    @app_commands.choices(
        alert_type=[
            app_commands.Choice(name="Security Breach", value="security_breach"),
            app_commands.Choice(name="Base Lockdown", value="base_lockdown"),
            app_commands.Choice(name="Personnel Emergency", value="personnel_emergency"),
            app_commands.Choice(name="System Failure", value="system_failure"),
            app_commands.Choice(name="Operational Alert", value="operational_alert"),
            app_commands.Choice(name="Weather Warning", value="weather_warning")
        ],
        severity=[
            app_commands.Choice(name="Critical", value="critical"),
            app_commands.Choice(name="High", value="high"),
            app_commands.Choice(name="Medium", value="medium"),
            app_commands.Choice(name="Low", value="low")
        ]
    )
    async def emergency_alert(self, interaction: discord.Interaction, alert_type: str, severity: str, message: str, duration: int = 15):
        """Broadcast emergency alert"""
        user_roles = [role.name for role in interaction.user.roles]
        
        # Only Executive Command can send emergency alerts
        if not any(role in user_roles for role in Config.CHIEF_EXECUTIVE_ROLES):
            await interaction.response.send_message("❌ Only Executive Command can broadcast emergency alerts.", ephemeral=True)
            return

        if duration > 60:
            await interaction.response.send_message("❌ Maximum duration is 60 minutes.", ephemeral=True)
            return

        # Create alert ID
        alert_id = f"ALERT-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        
        # Create alert embed
        severity_colors = {
            'critical': 0xFF0000,  # Red
            'high': 0xFF8C00,      # Orange
            'medium': 0xFFFF00,    # Yellow
            'low': 0x00FF00        # Green
        }
        
        embed = discord.Embed(
            title=f"🚨 EMERGENCY ALERT - {alert_type.replace('_', ' ').upper()}",
            description=f"**SEVERITY:** {severity.upper()}\n"
                       f"**ALERT ID:** {alert_id}\n"
                       f"**ISSUED BY:** {interaction.user.mention}\n"
                       f"**DURATION:** {duration} minutes\n\n"
                       f"**MESSAGE:**\n{message}",
            color=severity_colors.get(severity, 0xFF0000),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="📞 Emergency Contacts",
            value="Contact your direct supervisor or Emergency Operations Center",
            inline=False
        )
        
        embed.set_footer(text=f"F.R.O.S.T AI Alert System | {Config.COMPANY_NAME}")

        # Store alert data
        alert_data = {
            'id': alert_id,
            'type': alert_type,
            'severity': severity,
            'message': message,
            'issued_by': str(interaction.user),
            'issued_at': datetime.utcnow().isoformat(),
            'duration': duration,
            'expires_at': (datetime.utcnow() + timedelta(minutes=duration)).isoformat(),
            'active': True
        }
        
        self.active_alerts[alert_id] = alert_data
        self.alert_history.append(alert_data)

        # Broadcast to all channels based on severity
        await self._broadcast_alert(interaction.guild, embed, severity)
        
        await interaction.response.send_message(f"✅ Emergency alert {alert_id} broadcast successfully.", ephemeral=True)
        
        # Auto-expire alert after duration
        await asyncio.sleep(duration * 60)
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id]['active'] = False
            del self.active_alerts[alert_id]

    @app_commands.command(name="priority_notification", description="Send priority notification (Command Level+)")
    @app_commands.describe(
        title="Notification title",
        message="Notification content",
        target_clearance="Target clearance level",
        urgent="Mark as urgent notification"
    )
    @app_commands.choices(
        target_clearance=[
            app_commands.Choice(name="All Personnel", value="all"),
            app_commands.Choice(name="Officers Only", value="officers"),
            app_commands.Choice(name="NCOs and Above", value="ncos"),
            app_commands.Choice(name="Executive Command", value="executive")
        ]
    )
    async def priority_notification(self, interaction: discord.Interaction, title: str, message: str, target_clearance: str, urgent: bool = False):
        """Send priority notification"""
        user_clearance = get_user_clearance(interaction.user.roles)
        
        # Check if user has Command Level+ clearance
        if not Config.has_permission(user_clearance, 'COMMAND_LEVEL'):
            await interaction.response.send_message("❌ You need Command Level+ clearance to send priority notifications.", ephemeral=True)
            return

        # Create notification embed
        color = 0xFF4500 if urgent else 0x4169E1
        prefix = "🔥 URGENT" if urgent else "📢 PRIORITY"
        
        embed = discord.Embed(
            title=f"{prefix} NOTIFICATION",
            description=f"**{title}**\n\n{message}",
            color=color,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="📋 Details",
            value=f"**Issued by:** {interaction.user.mention}\n"
                  f"**Target:** {target_clearance.replace('_', ' ').title()}\n"
                  f"**Priority:** {'URGENT' if urgent else 'HIGH'}",
            inline=False
        )
        
        embed.set_footer(text=f"F.R.O.S.T AI Notification System | {Config.COMPANY_NAME}")

        # Send to appropriate channels/users
        await self._send_targeted_notification(interaction.guild, embed, target_clearance)
        
        await interaction.response.send_message("✅ Priority notification sent successfully.", ephemeral=True)

    @app_commands.command(name="alert_status", description="Check active alerts")
    async def alert_status(self, interaction: discord.Interaction):
        """Check active alerts"""
        if not self.active_alerts:
            await interaction.response.send_message("✅ No active alerts at this time.", ephemeral=True)
            return

        embed = discord.Embed(
            title="🚨 Active Alerts",
            description="Current emergency alerts and notifications",
            color=Config.COLORS['warning'],
            timestamp=datetime.utcnow()
        )

        for alert_id, alert_data in self.active_alerts.items():
            expires_at = datetime.fromisoformat(alert_data['expires_at'])
            time_remaining = expires_at - datetime.utcnow()
            
            if time_remaining.total_seconds() > 0:
                minutes_left = int(time_remaining.total_seconds() / 60)
                embed.add_field(
                    name=f"Alert: {alert_data['type'].replace('_', ' ').title()}",
                    value=f"**ID:** {alert_id}\n"
                          f"**Severity:** {alert_data['severity'].upper()}\n"
                          f"**Expires:** {minutes_left} minutes\n"
                          f"**Message:** {alert_data['message'][:100]}...",
                    inline=False
                )

        embed.set_footer(text=f"F.R.O.S.T AI Alert System | {Config.COMPANY_NAME}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="cancel_alert", description="Cancel active alert (Executive Command only)")
    @app_commands.describe(alert_id="Alert ID to cancel")
    async def cancel_alert(self, interaction: discord.Interaction, alert_id: str):
        """Cancel active alert"""
        user_roles = [role.name for role in interaction.user.roles]
        
        # Only Executive Command can cancel alerts
        if not any(role in user_roles for role in Config.CHIEF_EXECUTIVE_ROLES):
            await interaction.response.send_message("❌ Only Executive Command can cancel alerts.", ephemeral=True)
            return

        if alert_id not in self.active_alerts:
            await interaction.response.send_message("❌ Alert not found or already expired.", ephemeral=True)
            return

        # Cancel alert
        alert_data = self.active_alerts[alert_id]
        alert_data['active'] = False
        alert_data['cancelled_by'] = str(interaction.user)
        alert_data['cancelled_at'] = datetime.utcnow().isoformat()
        
        del self.active_alerts[alert_id]

        # Broadcast cancellation
        embed = discord.Embed(
            title="✅ ALERT CANCELLED",
            description=f"**Alert ID:** {alert_id}\n"
                       f"**Type:** {alert_data['type'].replace('_', ' ').title()}\n"
                       f"**Cancelled by:** {interaction.user.mention}\n"
                       f"**Original Message:** {alert_data['message']}",
            color=Config.COLORS['success'],
            timestamp=datetime.utcnow()
        )

        # Send cancellation to operations channel
        operations_channel = discord.utils.get(interaction.guild.channels, id=Config.OPERATIONS_CHANNEL)
        if operations_channel:
            await operations_channel.send(embed=embed)

        await interaction.response.send_message(f"✅ Alert {alert_id} cancelled successfully.", ephemeral=True)

    async def _broadcast_alert(self, guild, embed, severity):
        """Broadcast alert to appropriate channels"""
        # Send to operations channel
        operations_channel = discord.utils.get(guild.channels, id=Config.OPERATIONS_CHANNEL)
        if operations_channel:
            await operations_channel.send("@everyone", embed=embed)

        # For critical alerts, send to all text channels
        if severity == 'critical':
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    try:
                        await channel.send(embed=embed)
                    except:
                        pass  # Skip channels where bot can't send

    async def _send_targeted_notification(self, guild, embed, target_clearance):
        """Send notification to targeted clearance levels"""
        operations_channel = discord.utils.get(guild.channels, id=Config.OPERATIONS_CHANNEL)
        
        if target_clearance == "executive":
            mention = " ".join([f"<@&{guild.get_role(role_id).id}>" for role_id in Config.CHIEF_EXECUTIVE_ROLES if guild.get_role(role_id)])
        elif target_clearance == "officers":
            mention = "@here"  # Notify online officers
        else:
            mention = "@everyone"

        if operations_channel:
            await operations_channel.send(mention, embed=embed)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(AlertSystem(bot))