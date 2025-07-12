"""
High Command Operations for Merrywinter Security Consulting
Special operations commands for leadership
"""

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import random

from config.settings import Config
from utils.helpers import get_user_clearance, create_embed
from utils.storage import Storage

class HighCommand(commands.Cog):
    """High Command operations management system"""
    
    def __init__(self, bot):
        self.bot = bot
        self.storage = Storage()
    
    def cog_check(self, ctx):
        """Check if command is used in authorized guild"""
        return Config.check_guild_authorization(ctx.guild.id)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check if interaction is in authorized guild"""
        return Config.check_guild_authorization(interaction.guild.id)
    
    @app_commands.command(name="deployment", description="Deploy units to operational sectors (Director+ only)")
    @app_commands.describe(
        sector="Operation sector for deployment",
        units="Number of units to deploy",
        mission_type="Type of mission for deployment",
        priority="Priority level of deployment",
        classified="Mark as classified operation (Executive Command only)"
    )
    @app_commands.choices(
        sector=[
            app_commands.Choice(name="Sector Alpha - Urban Operations", value="alpha"),
            app_commands.Choice(name="Sector Beta - Desert Warfare", value="beta"),
            app_commands.Choice(name="Sector Gamma - Naval Operations", value="gamma"),
            app_commands.Choice(name="Sector Delta - Mountain Warfare", value="delta"),
            app_commands.Choice(name="Sector Epsilon - Jungle Operations", value="epsilon"),
            app_commands.Choice(name="Sector Zeta - Arctic Operations", value="zeta")
        ],
        mission_type=[
            app_commands.Choice(name="Reconnaissance", value="recon"),
            app_commands.Choice(name="Direct Action", value="direct_action"),
            app_commands.Choice(name="Security Detail", value="security"),
            app_commands.Choice(name="Convoy Escort", value="convoy"),
            app_commands.Choice(name="Base Defense", value="defense"),
            app_commands.Choice(name="Intelligence Gathering", value="intelligence")
        ],
        priority=[
            app_commands.Choice(name="Critical", value="critical"),
            app_commands.Choice(name="High", value="high"),
            app_commands.Choice(name="Medium", value="medium"),
            app_commands.Choice(name="Low", value="low")
        ]
    )
    async def deployment(self, interaction: discord.Interaction, sector: str, units: int, mission_type: str, priority: str, classified: bool = False):
        """Deploy units to operational sectors"""
        user_clearance = get_user_clearance(interaction.user.roles)
        
        # Check if user has Director+ clearance
        if not Config.has_permission(user_clearance, 'DIRECTOR_SECURITY'):
            await interaction.response.send_message("❌ You need Director+ clearance to authorize deployments.", ephemeral=True)
            return
        
        # Check if classified operation requires Executive Command clearance
        if classified and not Config.has_permission(user_clearance, 'EXECUTIVE_COMMAND'):
            await interaction.response.send_message("❌ Only Executive Command can authorize classified operations.", ephemeral=True)
            return
        
        # Check if deployment channel is configured
        if not Config.DEPLOYMENT_CHANNEL_ID:
            await interaction.response.send_message("❌ Deployment channel not configured.", ephemeral=True)
            return
        
        deployment_channel = self.bot.get_channel(Config.DEPLOYMENT_CHANNEL_ID)
        if not deployment_channel:
            await interaction.response.send_message("❌ Deployment channel not found.", ephemeral=True)
            return
        
        # Generate deployment ID
        deployment_id = f"DEP-{random.randint(10000, 99999)}"
        
        # Create deployment embed
        sector_names = {
            "alpha": "Sector Alpha - Urban Operations",
            "beta": "Sector Beta - Desert Warfare", 
            "gamma": "Sector Gamma - Naval Operations",
            "delta": "Sector Delta - Mountain Warfare",
            "epsilon": "Sector Epsilon - Jungle Operations",
            "zeta": "Sector Zeta - Arctic Operations"
        }
        
        mission_names = {
            "recon": "Reconnaissance",
            "direct_action": "Direct Action",
            "security": "Security Detail",
            "convoy": "Convoy Escort",
            "defense": "Base Defense",
            "intelligence": "Intelligence Gathering"
        }
        
        priority_colors = {
            "critical": 0xFF0000,
            "high": 0xFF8C00,
            "medium": 0xFFFF00,
            "low": 0x00FF00
        }
        
        # Handle classified operations
        if classified:
            title = "🚁 [CLASSIFIED] DEPLOYMENT AUTHORIZATION"
            authorized_by = "authorized by: **[RESTRICTED]**"
            classification_note = "\n🔒 **CLASSIFIED OPERATION**\n*Access restricted to Executive Command personnel only*"
        else:
            title = "🚁 DEPLOYMENT AUTHORIZATION"
            authorized_by = f"**Authorized By:** {interaction.user.mention}"
            classification_note = ""
        
        embed = discord.Embed(
            title=title,
            description=f"**Deployment ID:** {deployment_id}\n"
                       f"{authorized_by}\n"
                       f"**Clearance Level:** {user_clearance}\n"
                       f"**Timestamp:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
                       f"{classification_note}",
            color=priority_colors.get(priority, 0xFFFF00)
        )
        
        embed.add_field(
            name="📋 Deployment Details",
            value=f"**Sector:** {sector_names.get(sector, sector)}\n"
                  f"**Units:** {units}\n"
                  f"**Mission Type:** {mission_names.get(mission_type, mission_type)}\n"
                  f"**Priority:** {priority.upper()}",
            inline=False
        )
        
        embed.add_field(
            name="⚠️ Deployment Guidelines",
            value="• Maintain radio contact at all times\n"
                  "• Follow established ROE protocols\n"
                  "• Report status every 30 minutes\n"
                  "• Await extraction orders from command",
            inline=False
        )
        
        embed.add_field(
            name="🔗 Chain of Command",
            value=f"**Deployment Officer:** {interaction.user.display_name}\n"
                  f"**Sector Command:** Operational\n"
                  f"**Mission Control:** Active",
            inline=False
        )
        
        embed.set_footer(text=f"{Config.COMPANY_NAME} - High Command Operations")
        
        # Send to deployment channel
        await deployment_channel.send(embed=embed)
        
        # Save deployment data
        deployment_data = {
            'deployment_id': deployment_id,
            'authorized_by': interaction.user.id,
            'sector': sector,
            'units': units,
            'mission_type': mission_type,
            'priority': priority,
            'classified': classified,
            'status': 'deployed',
            'timestamp': datetime.utcnow().isoformat(),
            'guild_id': interaction.guild.id
        }
        
        await self.storage.save_deployment(deployment_data)
        
        # Send DM notifications to selected roles
        await self._send_dm_notifications(interaction.guild, deployment_data, 'deployment')
        
        await interaction.response.send_message(f"✅ Deployment {deployment_id} authorized successfully!", ephemeral=True)
    
    @app_commands.command(name="operation_start", description="Start a new operation (Chief+ only)")
    @app_commands.describe(
        operation_name="Name of the operation",
        objective="Primary objective of the operation",
        participants="Number of participants",
        duration="Expected duration in hours",
        classified="Mark as classified operation (Executive Command only)"
    )
    async def operation_start(self, interaction: discord.Interaction, operation_name: str, objective: str, participants: int, duration: int, classified: bool = False):
        """Start a new operation"""
        user_clearance = get_user_clearance(interaction.user.roles)
        
        # Check if user has Chief+ clearance
        if not Config.has_permission(user_clearance, 'CHIEF_OPERATIONS'):
            await interaction.response.send_message("❌ You need Chief+ clearance to start operations.", ephemeral=True)
            return
        
        # Check if classified operation requires Executive Command clearance
        if classified and not Config.has_permission(user_clearance, 'EXECUTIVE_COMMAND'):
            await interaction.response.send_message("❌ Only Executive Command can authorize classified operations.", ephemeral=True)
            return
        
        # Check if operation start channel is configured
        if not Config.OPERATION_START_CHANNEL_ID:
            await interaction.response.send_message("❌ Operation start channel not configured.", ephemeral=True)
            return
        
        operation_channel = self.bot.get_channel(Config.OPERATION_START_CHANNEL_ID)
        if not operation_channel:
            await interaction.response.send_message("❌ Operation start channel not found.", ephemeral=True)
            return
        
        # Generate operation ID
        operation_id = f"OP-{random.randint(1000, 9999)}"
        
        # Handle classified operations
        if classified:
            title = "🎯 [CLASSIFIED] OPERATION COMMENCED"
            commanding_officer = "**Commanding Officer:** authorized by: **[RESTRICTED]**"
            classification_note = "\n🔒 **CLASSIFIED OPERATION**\n*Access restricted to Executive Command personnel only*"
        else:
            title = "🎯 OPERATION COMMENCED"
            commanding_officer = f"**Commanding Officer:** {interaction.user.mention}"
            classification_note = ""
        
        # Create operation embed
        embed = discord.Embed(
            title=title,
            description=f"**Operation Name:** {operation_name}\n"
                       f"**Operation ID:** {operation_id}\n"
                       f"{commanding_officer}\n"
                       f"**Clearance Level:** {user_clearance}"
                       f"{classification_note}",
            color=0x00FF00
        )
        
        embed.add_field(
            name="🎯 Mission Parameters",
            value=f"**Primary Objective:** {objective}\n"
                  f"**Personnel:** {participants} operators\n"
                  f"**Duration:** {duration} hours\n"
                  f"**Status:** ACTIVE",
            inline=False
        )
        
        embed.add_field(
            name="📡 Command Structure",
            value=f"**Operation Commander:** {interaction.user.display_name}\n"
                  f"**Mission Control:** {Config.COMPANY_NAME}\n"
                  f"**Start Time:** {datetime.utcnow().strftime('%H:%M:%S')} UTC",
            inline=False
        )
        
        embed.add_field(
            name="⚠️ Operation Protocols",
            value="• All participants report to designated channels\n"
                  "• Maintain operational security at all times\n"
                  "• Follow established chain of command\n"
                  "• Regular status updates required",
            inline=False
        )
        
        embed.set_footer(text=f"{Config.COMPANY_NAME} - Operation Command")
        
        # Send to operation channel
        await operation_channel.send(embed=embed)
        
        # Save operation data
        operation_data = {
            'operation_id': operation_id,
            'operation_name': operation_name,
            'commander': interaction.user.id,
            'objective': objective,
            'participants': participants,
            'duration': duration,
            'classified': classified,
            'status': 'active',
            'start_time': datetime.utcnow().isoformat(),
            'guild_id': interaction.guild.id
        }
        
        await self.storage.save_operation(operation_data)
        
        # Send DM notifications to selected roles
        await self._send_dm_notifications(interaction.guild, operation_data, 'operation')
        
        await interaction.response.send_message(f"✅ Operation {operation_name} ({operation_id}) has been started!", ephemeral=True)
    
    @app_commands.command(name="operation_log", description="Log operation activities (Director+ only)")
    @app_commands.describe(
        operation_id="ID of the operation to log",
        activity="Activity or event to log",
        status="Current status of the operation"
    )
    @app_commands.choices(
        status=[
            app_commands.Choice(name="In Progress", value="in_progress"),
            app_commands.Choice(name="Completed", value="completed"),
            app_commands.Choice(name="On Hold", value="on_hold"),
            app_commands.Choice(name="Cancelled", value="cancelled")
        ]
    )
    async def operation_log(self, interaction: discord.Interaction, operation_id: str, activity: str, status: str):
        """Log operation activities"""
        user_clearance = get_user_clearance(interaction.user.roles)
        
        # Check if user has Director+ clearance
        if not Config.has_permission(user_clearance, 'DIRECTOR_SECURITY'):
            await interaction.response.send_message("❌ You need Director+ clearance to log operations.", ephemeral=True)
            return
        
        # Check if operation log channel is configured
        if not Config.OPERATION_LOG_CHANNEL_ID:
            await interaction.response.send_message("❌ Operation log channel not configured.", ephemeral=True)
            return
        
        log_channel = self.bot.get_channel(Config.OPERATION_LOG_CHANNEL_ID)
        if not log_channel:
            await interaction.response.send_message("❌ Operation log channel not found.", ephemeral=True)
            return
        
        # Create log embed
        status_colors = {
            "in_progress": 0xFFFF00,
            "completed": 0x00FF00,
            "on_hold": 0xFFA500,
            "cancelled": 0xFF0000
        }
        
        status_emojis = {
            "in_progress": "🔄",
            "completed": "✅",
            "on_hold": "⏸️",
            "cancelled": "❌"
        }
        
        embed = discord.Embed(
            title=f"📝 OPERATION LOG - {operation_id}",
            description=f"**Logged By:** {interaction.user.mention}\n"
                       f"**Clearance Level:** {user_clearance}\n"
                       f"**Timestamp:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
            color=status_colors.get(status, 0xFFFF00)
        )
        
        embed.add_field(
            name="📋 Activity Log",
            value=f"**Activity:** {activity}\n"
                  f"**Status:** {status_emojis.get(status, '🔄')} {status.replace('_', ' ').title()}",
            inline=False
        )
        
        embed.set_footer(text=f"{Config.COMPANY_NAME} - Operation Logs")
        
        # Send to log channel
        await log_channel.send(embed=embed)
        
        # Save log data
        log_data = {
            'operation_id': operation_id,
            'logged_by': interaction.user.id,
            'activity': activity,
            'status': status,
            'timestamp': datetime.utcnow().isoformat(),
            'guild_id': interaction.guild.id
        }
        
        await self.storage.save_operation_log(log_data)
        
        await interaction.response.send_message(f"✅ Activity logged for operation {operation_id}!", ephemeral=True)
    
    async def _send_dm_notifications(self, guild, data, notification_type):
        """Send enhanced DM notifications to specific roles for deployments and operations"""
        if notification_type == 'deployment':
            target_roles = Config.DEPLOYMENT_NOTIFICATION_ROLES
            # Map sector codes to full names
            sector_names = {
                "alpha": "Sector Alpha - Urban Operations",
                "beta": "Sector Beta - Desert Warfare", 
                "gamma": "Sector Gamma - Naval Operations",
                "delta": "Sector Delta - Mountain Warfare",
                "epsilon": "Sector Epsilon - Jungle Operations",
                "zeta": "Sector Zeta - Arctic Operations"
            }
            mission_names = {
                "recon": "Reconnaissance",
                "direct_action": "Direct Action",
                "security": "Security Detail",
                "convoy": "Convoy Escort",
                "defense": "Base Defense",
                "intelligence": "Intelligence Gathering"
            }
            
            title = f"🚁 DEPLOYMENT AUTHORIZATION ISSUED"
            description = f"**Deployment ID:** `{data['deployment_id']}`\n**Status:** `ACTIVE DEPLOYMENT`"
            
        elif notification_type == 'operation':
            target_roles = Config.OPERATION_NOTIFICATION_ROLES
            title = f"🎯 OPERATION COMMENCED"
            description = f"**Operation:** `{data['operation_name']}`\n**Operation ID:** `{data['operation_id']}`\n**Status:** `ACTIVE OPERATION`"
        else:
            return
        
        # Create enhanced DM embed
        if data.get('classified'):
            embed = discord.Embed(
                title=f"🔒 [CLASSIFIED] {title}",
                description=f"{description}\n\n⚠️ **CLASSIFIED OPERATION**\n*Executive Command Authorization Required*",
                color=0xFF0000,  # Red for classified
                timestamp=datetime.utcnow()
            )
        else:
            embed = discord.Embed(
                title=title,
                description=description,
                color=0xFF8C00,  # Orange for high priority
                timestamp=datetime.utcnow()
            )
        
        # Add detailed information based on type
        if notification_type == 'deployment':
            embed.add_field(
                name="📋 Deployment Details",
                value=f"**Sector:** {sector_names.get(data.get('sector', ''), data.get('sector', 'Unknown'))}\n"
                      f"**Units Deployed:** {data.get('units', 'Unknown')}\n"
                      f"**Mission Type:** {mission_names.get(data.get('mission_type', ''), data.get('mission_type', 'Unknown'))}\n"
                      f"**Priority Level:** {data.get('priority', 'Unknown').upper()}",
                inline=False
            )
            embed.add_field(
                name="⚡ Command Response Required",
                value="• Review deployment parameters\n• Coordinate sector resources\n• Monitor unit status\n• Report to High Command",
                inline=False
            )
            
        elif notification_type == 'operation':
            embed.add_field(
                name="🎯 Operation Parameters",
                value=f"**Primary Objective:** {data.get('objective', 'Unknown')}\n"
                      f"**Participants:** {data.get('participants', 'Unknown')} personnel\n"
                      f"**Duration:** {data.get('duration', 'Unknown')} hours\n"
                      f"**Start Time:** {datetime.utcnow().strftime('%H:%M:%S')} UTC",
                inline=False
            )
            embed.add_field(
                name="⚡ Command Response Required",
                value="• Coordinate operational assets\n• Monitor mission progress\n• Maintain communication\n• Prepare contingency plans",
                inline=False
            )
        
        # Add authorization info
        authorizing_member = guild.get_member(data.get('authorized_by') or data.get('commander'))
        if authorizing_member and not data.get('classified'):
            embed.add_field(
                name="🔐 Authorization",
                value=f"**Authorized By:** {authorizing_member.display_name}\n"
                      f"**Command Level:** High Command\n"
                      f"**Clearance:** Verified",
                inline=True
            )
        elif data.get('classified'):
            embed.add_field(
                name="🔐 Authorization",
                value="**Authorized By:** [RESTRICTED]\n"
                      f"**Command Level:** Executive Command\n"
                      f"**Clearance:** CLASSIFIED",
                inline=True
            )
        
        # Add timestamp and company info
        embed.add_field(
            name="🕐 Timestamp",
            value=f"**Issued:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
                  f"**Mission:** {Config.COMPANY_MOTTO}\n"
                  f"**Status:** Active",
            inline=True
        )
        
        embed.set_footer(
            text=f"F.R.O.S.T AI v{Config.AI_VERSION} • {Config.COMPANY_NAME}",
            icon_url=None
        )
        
        # Send notifications to members with target roles
        notified_count = 0
        failed_count = 0
        
        for member in guild.members:
            if member.bot:
                continue
                
            member_role_names = [role.name for role in member.roles]
            if any(role_name in member_role_names for role_name in target_roles):
                try:
                    await member.send(embed=embed)
                    notified_count += 1
                except discord.Forbidden:
                    failed_count += 1
                except Exception as e:
                    failed_count += 1
                    print(f"Failed to send DM to {member}: {e}")
        
        print(f"✅ Sent {notification_type} DM notifications to {notified_count} commanders ({failed_count} failed - DMs disabled)")

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(HighCommand(bot))