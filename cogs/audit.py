"""
Audit and Security Monitoring System for Merrywinter Security Consulting
Comprehensive logging, security alerts, and audit trail management
"""

import discord
from discord.ext import commands
from discord import app_commands
import json
import asyncio
from datetime import datetime, timedelta
from config.settings import Config
from utils.helpers import get_user_clearance
from utils.storage import Storage

class AuditSystem(commands.Cog):
    """Audit logging and security monitoring system"""

    def __init__(self, bot):
        self.bot = bot
        self.storage = Storage()
        self.security_events = []
        self.audit_log = []
        self.suspicious_activity = {}

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check if interaction is in authorized guild"""
        return Config.check_guild_authorization(interaction.guild.id)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Log message deletions"""
        if not Config.check_guild_authorization(message.guild.id):
            return
        
        await self._log_audit_event(
            event_type="message_delete",
            user=message.author,
            details={
                "channel": message.channel.name,
                "content": message.content[:500] if message.content else "[No content]",
                "attachments": len(message.attachments)
            }
        )

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """Log message edits"""
        if not Config.check_guild_authorization(before.guild.id):
            return
        
        await self._log_audit_event(
            event_type="message_edit",
            user=before.author,
            details={
                "channel": before.channel.name,
                "before": before.content[:200] if before.content else "[No content]",
                "after": after.content[:200] if after.content else "[No content]"
            }
        )

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        """Log member bans"""
        if not Config.check_guild_authorization(guild.id):
            return
        
        await self._log_security_event(
            event_type="member_ban",
            severity="high",
            user=user,
            details={"action": "banned", "guild": guild.name}
        )

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        """Log member unbans"""
        if not Config.check_guild_authorization(guild.id):
            return
        
        await self._log_security_event(
            event_type="member_unban",
            severity="medium",
            user=user,
            details={"action": "unbanned", "guild": guild.name}
        )

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Log role changes and nickname changes"""
        if not Config.check_guild_authorization(before.guild.id):
            return
        
        # Log role changes
        if before.roles != after.roles:
            added_roles = [role.name for role in after.roles if role not in before.roles]
            removed_roles = [role.name for role in before.roles if role not in after.roles]
            
            if added_roles or removed_roles:
                await self._log_audit_event(
                    event_type="role_change",
                    user=after,
                    details={
                        "added_roles": added_roles,
                        "removed_roles": removed_roles
                    }
                )
        
        # Log nickname changes
        if before.nick != after.nick:
            await self._log_audit_event(
                event_type="nickname_change",
                user=after,
                details={
                    "old_nick": before.nick,
                    "new_nick": after.nick
                }
            )

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Log voice channel activities"""
        if not Config.check_guild_authorization(member.guild.id):
            return
        
        # Log voice channel joins/leaves
        if before.channel != after.channel:
            if after.channel:  # Joined a channel
                await self._log_audit_event(
                    event_type="voice_join",
                    user=member,
                    details={"channel": after.channel.name}
                )
            elif before.channel:  # Left a channel
                await self._log_audit_event(
                    event_type="voice_leave",
                    user=member,
                    details={"channel": before.channel.name}
                )

    @commands.Cog.listener()
    async def on_app_command_completion(self, interaction, command):
        """Log slash command usage"""
        if not Config.check_guild_authorization(interaction.guild.id):
            return
        
        await self._log_audit_event(
            event_type="command_use",
            user=interaction.user,
            details={
                "command": command.name,
                "channel": interaction.channel.name if interaction.channel else "DM",
                "parameters": str(interaction.data.get('options', []))[:200]
            }
        )

    @app_commands.command(name="audit_log", description="View audit log (Admin only)")
    @app_commands.describe(
        event_type="Filter by event type",
        hours="Hours to look back (default: 24)"
    )
    @app_commands.choices(
        event_type=[
            app_commands.Choice(name="All Events", value="all"),
            app_commands.Choice(name="Message Events", value="message"),
            app_commands.Choice(name="Role Changes", value="role_change"),
            app_commands.Choice(name="Voice Activity", value="voice"),
            app_commands.Choice(name="Command Usage", value="command_use"),
            app_commands.Choice(name="Security Events", value="security")
        ]
    )
    async def audit_log(self, interaction: discord.Interaction, event_type: str = "all", hours: int = 24):
        """View audit log"""
        user_roles = [role.name for role in interaction.user.roles]
        
        # Only admins can view audit logs
        if not Config.is_admin(user_roles):
            await interaction.response.send_message("❌ You need administrator permissions to view audit logs.", ephemeral=True)
            return

        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Filter audit log
        filtered_events = []
        for event in self.audit_log:
            event_time = datetime.fromisoformat(event['timestamp'])
            if event_time >= cutoff_time:
                if event_type == "all" or event['type'].startswith(event_type.replace("_", "")):
                    filtered_events.append(event)

        if not filtered_events:
            await interaction.response.send_message(f"No audit events found in the last {hours} hours.", ephemeral=True)
            return

        # Create audit log embed
        embed = discord.Embed(
            title="🔍 Audit Log",
            description=f"Events from the last {hours} hours\nFilter: {event_type.title()}",
            color=Config.COLORS['info'],
            timestamp=datetime.utcnow()
        )

        # Show latest 10 events
        for event in filtered_events[-10:]:
            event_time = datetime.fromisoformat(event['timestamp'])
            time_str = event_time.strftime('%H:%M:%S')
            
            embed.add_field(
                name=f"[{time_str}] {event['type'].replace('_', ' ').title()}",
                value=f"**User:** {event['user']}\n"
                      f"**Details:** {str(event['details'])[:100]}...",
                inline=False
            )

        embed.set_footer(text=f"Total events: {len(filtered_events)} | F.R.O.S.T AI Audit System")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="security_report", description="Generate security report (Admin only)")
    @app_commands.describe(hours="Hours to analyze (default: 24)")
    async def security_report(self, interaction: discord.Interaction, hours: int = 24):
        """Generate security report"""
        user_roles = [role.name for role in interaction.user.roles]
        
        # Only admins can view security reports
        if not Config.is_admin(user_roles):
            await interaction.response.send_message("❌ You need administrator permissions to view security reports.", ephemeral=True)
            return

        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Analyze security events
        recent_security_events = [
            event for event in self.security_events 
            if datetime.fromisoformat(event['timestamp']) >= cutoff_time
        ]

        # Count event types
        event_counts = {}
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        for event in recent_security_events:
            event_type = event['type']
            severity = event['severity']
            
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
            severity_counts[severity] += 1

        # Create security report embed
        embed = discord.Embed(
            title="🛡️ Security Report",
            description=f"Security analysis for the last {hours} hours",
            color=Config.COLORS['warning'] if severity_counts['critical'] > 0 else Config.COLORS['success'],
            timestamp=datetime.utcnow()
        )

        # Overall status
        total_events = len(recent_security_events)
        threat_level = "HIGH" if severity_counts['critical'] > 0 else "MEDIUM" if severity_counts['high'] > 3 else "LOW"
        
        embed.add_field(
            name="📊 Overview",
            value=f"**Total Events:** {total_events}\n"
                  f"**Threat Level:** {threat_level}\n"
                  f"**Critical:** {severity_counts['critical']}\n"
                  f"**High:** {severity_counts['high']}\n"
                  f"**Medium:** {severity_counts['medium']}\n"
                  f"**Low:** {severity_counts['low']}",
            inline=True
        )

        # Event breakdown
        if event_counts:
            event_breakdown = "\n".join([f"**{event.replace('_', ' ').title()}:** {count}" 
                                       for event, count in event_counts.items()])
            embed.add_field(
                name="📋 Event Types",
                value=event_breakdown,
                inline=True
            )

        # Suspicious activity
        suspicious_count = len([user for user, data in self.suspicious_activity.items() 
                              if data.get('last_flagged', datetime.min.replace(tzinfo=None)) >= cutoff_time.replace(tzinfo=None)])
        
        embed.add_field(
            name="⚠️ Suspicious Activity",
            value=f"**Flagged Users:** {suspicious_count}\n"
                  f"**Active Monitoring:** {len(self.suspicious_activity)} users",
            inline=True
        )

        embed.set_footer(text="F.R.O.S.T AI Security Monitoring System")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="flag_user", description="Flag user for monitoring (Admin only)")
    @app_commands.describe(
        user="User to flag for monitoring",
        reason="Reason for flagging",
        severity="Monitoring severity level"
    )
    @app_commands.choices(
        severity=[
            app_commands.Choice(name="High", value="high"),
            app_commands.Choice(name="Medium", value="medium"),
            app_commands.Choice(name="Low", value="low")
        ]
    )
    async def flag_user(self, interaction: discord.Interaction, user: discord.Member, reason: str, severity: str = "medium"):
        """Flag user for monitoring"""
        user_roles = [role.name for role in interaction.user.roles]
        
        # Only admins can flag users
        if not Config.is_admin(user_roles):
            await interaction.response.send_message("❌ You need administrator permissions to flag users.", ephemeral=True)
            return

        # Add to suspicious activity monitoring
        self.suspicious_activity[str(user.id)] = {
            'user': str(user),
            'reason': reason,
            'severity': severity,
            'flagged_by': str(interaction.user),
            'flagged_at': datetime.utcnow().isoformat(),
            'last_flagged': datetime.utcnow(),
            'event_count': 0
        }

        # Log security event
        await self._log_security_event(
            event_type="user_flagged",
            severity=severity,
            user=user,
            details={
                "reason": reason,
                "flagged_by": str(interaction.user)
            }
        )

        await interaction.response.send_message(f"✅ User {user.mention} flagged for {severity} priority monitoring.", ephemeral=True)

    async def _log_audit_event(self, event_type: str, user: discord.Member, details: dict):
        """Log audit event"""
        event = {
            'type': event_type,
            'user': str(user),
            'user_id': user.id,
            'timestamp': datetime.utcnow().isoformat(),
            'details': details
        }
        
        self.audit_log.append(event)
        
        # Keep only last 1000 events to prevent memory issues
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]

    async def _log_security_event(self, event_type: str, severity: str, user: discord.Member, details: dict):
        """Log security event"""
        event = {
            'type': event_type,
            'severity': severity,
            'user': str(user),
            'user_id': user.id,
            'timestamp': datetime.utcnow().isoformat(),
            'details': details
        }
        
        self.security_events.append(event)
        
        # Check if user is flagged for monitoring
        if str(user.id) in self.suspicious_activity:
            self.suspicious_activity[str(user.id)]['event_count'] += 1
            self.suspicious_activity[str(user.id)]['last_flagged'] = datetime.utcnow()

        # Auto-alert on critical events
        if severity == "critical":
            await self._send_security_alert(event)

    async def _send_security_alert(self, event):
        """Send automated security alert"""
        for guild in self.bot.guilds:
            if Config.check_guild_authorization(guild.id):
                security_channel = discord.utils.get(guild.channels, id=Config.LOG_CHANNEL)
                if security_channel:
                    embed = discord.Embed(
                        title="🚨 CRITICAL SECURITY EVENT",
                        description=f"**Event:** {event['type'].replace('_', ' ').title()}\n"
                                   f"**User:** {event['user']}\n"
                                   f"**Time:** {event['timestamp']}\n"
                                   f"**Details:** {event['details']}",
                        color=0xFF0000,
                        timestamp=datetime.utcnow()
                    )
                    
                    await security_channel.send("@here", embed=embed)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(AuditSystem(bot))