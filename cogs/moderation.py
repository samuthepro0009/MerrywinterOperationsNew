"""
Moderation system for Merrywinter Security Consulting
Basic moderation tools - SLASH COMMANDS ONLY
"""

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import asyncio

from config.settings import Config
from utils.helpers import get_user_clearance, create_embed
from utils.storage import Storage

class ModerationSystem(commands.Cog):
    """Moderation system for PMC operations"""
    
    def __init__(self, bot):
        self.bot = bot
        self.storage = Storage()
    
    @app_commands.command(name="purge", description="Delete multiple messages (Moderator+ only)")
    @app_commands.describe(
        amount="Number of messages to delete (1-100)",
        user="Delete messages from specific user only (optional)"
    )
    async def purge_messages(self, interaction: discord.Interaction, amount: int, user: discord.Member = None):
        """Delete multiple messages (Moderator+ only)"""
        if not Config.is_moderator([role.name for role in interaction.user.roles]):
            await interaction.response.send_message("❌ You don't have permission to purge messages.", ephemeral=True)
            return
        
        if amount < 1 or amount > 100:
            await interaction.response.send_message("❌ Amount must be between 1 and 100.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            if user:
                # Delete messages from specific user
                def check_user(message):
                    return message.author == user
                
                deleted = await interaction.channel.purge(limit=amount, check=check_user)
                
                embed = discord.Embed(
                    title="🗑️ Messages Purged",
                    description=f"**Deleted:** {len(deleted)} messages from {user.mention}\n"
                               f"**Moderator:** {interaction.user.mention}\n"
                               f"**Channel:** {interaction.channel.mention}",
                    color=Config.COLORS['success']
                )
            else:
                # Delete any messages
                deleted = await interaction.channel.purge(limit=amount)
                
                embed = discord.Embed(
                    title="🗑️ Messages Purged",
                    description=f"**Deleted:** {len(deleted)} messages\n"
                               f"**Moderator:** {interaction.user.mention}\n"
                               f"**Channel:** {interaction.channel.mention}",
                    color=Config.COLORS['success']
                )
            
            embed.set_footer(text=f"{Config.COMPANY_NAME} - Moderation Action")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error purging messages: {str(e)}")
    
    @app_commands.command(name="warn", description="Issue a warning to a user (Moderator+ only)")
    @app_commands.describe(
        user="User to warn",
        reason="Reason for the warning"
    )
    async def warn_user(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        """Issue a warning to a user (Moderator+ only)"""
        if not Config.is_moderator([role.name for role in interaction.user.roles]):
            await interaction.response.send_message("❌ You don't have permission to warn users.", ephemeral=True)
            return
        
        # Don't warn officers unless issuer has higher clearance
        user_clearance = get_user_clearance(user.roles)
        issuer_clearance = get_user_clearance(interaction.user.roles)
        
        # Officers (Command Level+) can only be warned by higher officers
        if (Config.has_permission(user_clearance, 'COMMAND_LEVEL') and 
            not Config.has_permission(issuer_clearance, user_clearance)):
            await interaction.response.send_message("❌ You cannot warn officers with equal or higher clearance.", ephemeral=True)
            return
        
        # Create warning data
        warning_data = {
            'user_id': user.id,
            'warned_by': interaction.user.id,
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat(),
            'guild_id': interaction.guild.id
        }
        
        # Save warning (you'd implement this in storage)
        warnings = self.storage.load_data('warnings.json')
        if str(user.id) not in warnings:
            warnings[str(user.id)] = []
        warnings[str(user.id)].append(warning_data)
        self.storage.save_data('warnings.json', warnings)
        
        # Send warning embed
        embed = discord.Embed(
            title="⚠️ Official Warning Issued",
            description=f"**User:** {user.mention}\n"
                       f"**Warned By:** {interaction.user.mention}\n"
                       f"**Reason:** {reason}\n"
                       f"**Date:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
            color=Config.COLORS['warning']
        )
        embed.set_footer(text=f"{Config.COMPANY_NAME} - Disciplinary Action")
        
        await interaction.response.send_message(embed=embed)
        
        # DM the user
        try:
            dm_embed = discord.Embed(
                title="⚠️ Warning Received",
                description=f"You have received an official warning in **{interaction.guild.name}**.\n\n"
                           f"**Reason:** {reason}\n"
                           f"**Issued By:** {interaction.user.display_name}\n\n"
                           "Please review our guidelines and adjust your behavior accordingly.",
                color=Config.COLORS['warning']
            )
            await user.send(embed=dm_embed)
        except discord.Forbidden:
            pass
    
    @app_commands.command(name="warnings", description="Check warnings for a user")
    @app_commands.describe(user="User to check warnings for (optional)")
    async def check_warnings(self, interaction: discord.Interaction, user: discord.Member = None):
        """Check warnings for a user"""
        target_user = user or interaction.user
        
        # Check permissions
        if (target_user != interaction.user and 
            not Config.is_moderator([role.name for role in interaction.user.roles])):
            await interaction.response.send_message("❌ You can only check your own warnings.", ephemeral=True)
            return
        
        warnings = self.storage.load_data('warnings.json')
        user_warnings = warnings.get(str(target_user.id), [])
        
        if not user_warnings:
            await interaction.response.send_message(f"✅ {target_user.mention} has no warnings.")
            return
        
        embed = discord.Embed(
            title=f"⚠️ Warning History - {target_user.display_name}",
            description=f"**Total Warnings:** {len(user_warnings)}",
            color=Config.COLORS['warning']
        )
        
        for i, warning in enumerate(user_warnings[-5:], 1):  # Show last 5 warnings
            embed.add_field(
                name=f"Warning {i}",
                value=f"**Reason:** {warning['reason']}\n"
                      f"**Date:** {warning['timestamp'][:10]}\n"
                      f"**Issued By:** <@{warning['warned_by']}>",
                inline=False
            )
        
        embed.set_footer(text="Merrywinter Security Consulting - Disciplinary Records")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="timeout", description="Timeout a user (Moderator+ only)")
    @app_commands.describe(
        user="User to timeout",
        duration="Duration in minutes (1-1440)",
        reason="Reason for the timeout"
    )
    async def timeout_user(self, interaction: discord.Interaction, user: discord.Member, duration: int, reason: str = "No reason provided"):
        """Timeout a user (Moderator+ only)"""
        if not Config.is_moderator([role.name for role in interaction.user.roles]):
            await interaction.response.send_message("❌ You don't have permission to timeout users.", ephemeral=True)
            return
        
        if duration < 1 or duration > 1440:  # Max 24 hours
            await interaction.response.send_message("❌ Duration must be between 1 and 1440 minutes (24 hours).", ephemeral=True)
            return
        
        # Don't timeout officers unless issuer has higher clearance
        user_clearance = get_user_clearance(user.roles)
        issuer_clearance = get_user_clearance(interaction.user.roles)
        
        # Officers (Command Level+) can only be timed out by higher officers
        if (Config.has_permission(user_clearance, 'COMMAND_LEVEL') and 
            not Config.has_permission(issuer_clearance, user_clearance)):
            await interaction.response.send_message("❌ You cannot timeout officers with equal or higher clearance.", ephemeral=True)
            return
        
        # Try to timeout the user
        try:
            timeout_until = datetime.utcnow() + timedelta(minutes=duration)
            await user.timeout(timeout_until, reason=reason)
            
            embed = discord.Embed(
                title="🔇 User Timed Out",
                description=f"**User:** {user.mention}\n"
                           f"**Duration:** {duration} minutes\n"
                           f"**Reason:** {reason}\n"
                           f"**Timed Out By:** {interaction.user.mention}\n"
                           f"**Expires:** <t:{int(timeout_until.timestamp())}:R>",
                color=Config.COLORS['error']
            )
            embed.set_footer(text=f"{Config.COMPANY_NAME} - Moderation Action")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error timing out user: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="untimeout", description="Remove timeout from a user (Moderator+ only)")
    @app_commands.describe(user="User to remove timeout from")
    async def untimeout_user(self, interaction: discord.Interaction, user: discord.Member):
        """Remove timeout from a user (Moderator+ only)"""
        if not Config.is_moderator([role.name for role in interaction.user.roles]):
            await interaction.response.send_message("❌ You don't have permission to remove timeouts.", ephemeral=True)
            return
        
        try:
            await user.timeout(None, reason=f"Timeout removed by {interaction.user}")
            
            embed = discord.Embed(
                title="🔊 Timeout Removed",
                description=f"**User:** {user.mention}\n"
                           f"**Removed By:** {interaction.user.mention}",
                color=Config.COLORS['success']
            )
            embed.set_footer(text=f"{Config.COMPANY_NAME} - Moderation Action")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error removing timeout: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="kick", description="Kick a user from the server (Moderator+ only)")
    @app_commands.describe(
        user="User to kick",
        reason="Reason for the kick"
    )
    async def kick_user(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        """Kick a user from the server (Moderator+ only)"""
        if not Config.is_moderator([role.name for role in interaction.user.roles]):
            await interaction.response.send_message("❌ You don't have permission to kick users.", ephemeral=True)
            return
        
        # Don't kick officers unless issuer has higher clearance
        user_clearance = get_user_clearance(user.roles)
        issuer_clearance = get_user_clearance(interaction.user.roles)
        
        # Officers (Command Level+) can only be kicked by higher officers
        if (Config.has_permission(user_clearance, 'COMMAND_LEVEL') and 
            not Config.has_permission(issuer_clearance, user_clearance)):
            await interaction.response.send_message("❌ You cannot kick officers with equal or higher clearance.", ephemeral=True)
            return
        
        try:
            await user.kick(reason=reason)
            
            embed = discord.Embed(
                title="👢 User Kicked",
                description=f"**User:** {user.mention}\n"
                           f"**Reason:** {reason}\n"
                           f"**Kicked By:** {interaction.user.mention}",
                color=Config.COLORS['error']
            )
            embed.set_footer(text=f"{Config.COMPANY_NAME} - Moderation Action")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error kicking user: {str(e)}", ephemeral=True)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(ModerationSystem(bot))