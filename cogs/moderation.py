"""
Moderation features for Merrywinter Security Consulting
Handles automated moderation and logging
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
    """Moderation and logging system"""
    
    def __init__(self, bot):
        self.bot = bot
        self.storage = Storage()
        self.warning_counts = {}
    
    def cog_check(self, ctx):
        """Check if command is used in authorized guild"""
        return Config.check_guild_authorization(ctx.guild.id)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check if interaction is in authorized guild"""
        return Config.check_guild_authorization(interaction.guild.id)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Monitor messages for moderation"""
        if message.author.bot:
            return
        
        # Check for spam
        await self.check_spam(message)
        
        # Check for inappropriate content
        await self.check_content(message)
    
    async def check_spam(self, message):
        """Check for spam messages"""
        user_id = message.author.id
        current_time = datetime.utcnow()
        
        # Initialize user tracking
        if user_id not in self.warning_counts:
            self.warning_counts[user_id] = {
                'messages': [],
                'warnings': 0,
                'last_warning': None
            }
        
        user_data = self.warning_counts[user_id]
        
        # Add current message to tracking
        user_data['messages'].append(current_time)
        
        # Remove old messages (older than 10 seconds)
        user_data['messages'] = [
            msg_time for msg_time in user_data['messages']
            if (current_time - msg_time).total_seconds() < 10
        ]
        
        # Check for spam (5+ messages in 10 seconds)
        if len(user_data['messages']) >= 5:
            await self.handle_spam(message)
    
    async def check_content(self, message):
        """Check message content for inappropriate material"""
        content = message.content.lower()
        
        # Basic content filters
        inappropriate_words = [
            'spam', 'scam', 'hack', 'cheat', 'exploit'
        ]
        
        for word in inappropriate_words:
            if word in content:
                await self.handle_inappropriate_content(message, word)
                break
    
    async def handle_spam(self, message):
        """Handle spam detection"""
        user_clearance = get_user_clearance(message.author.roles)
        
        # Don't moderate high-clearance users
        if user_clearance in ['OMEGA', 'BETA']:
            return
        
        # Delete the message
        try:
            await message.delete()
        except discord.NotFound:
            pass
        
        # Send warning
        embed = discord.Embed(
            title="⚠️ Spam Detected",
            description=f"{message.author.mention}, please avoid sending messages too quickly.\n"
                       "Continued spam will result in temporary restrictions.",
            color=Config.COLORS['warning']
        )
        
        warning_msg = await message.channel.send(embed=embed)
        
        # Delete warning after 10 seconds
        await asyncio.sleep(10)
        try:
            await warning_msg.delete()
        except discord.NotFound:
            pass
        
        # Log the incident
        await self.log_moderation_action(
            message.author,
            "Spam Detection",
            "Automatic spam detection triggered",
            message.channel
        )
    
    async def handle_inappropriate_content(self, message, trigger_word):
        """Handle inappropriate content detection"""
        user_clearance = get_user_clearance(message.author.roles)
        
        # Don't moderate high-clearance users
        if user_clearance in ['OMEGA', 'BETA']:
            return
        
        # Delete the message
        try:
            await message.delete()
        except discord.NotFound:
            pass
        
        # Send warning
        embed = discord.Embed(
            title="⚠️ Content Filter Triggered",
            description=f"{message.author.mention}, your message was removed for containing inappropriate content.\n"
                       "Please follow our community guidelines.",
            color=Config.COLORS['warning']
        )
        
        warning_msg = await message.channel.send(embed=embed)
        
        # Delete warning after 15 seconds
        await asyncio.sleep(15)
        try:
            await warning_msg.delete()
        except discord.NotFound:
            pass
        
        # Log the incident
        await self.log_moderation_action(
            message.author,
            "Content Filter",
            f"Triggered by word: {trigger_word}",
            message.channel
        )
    
    async def log_moderation_action(self, user, action_type, reason, channel):
        """Log moderation actions"""
        log_data = {
            'user_id': user.id,
            'action_type': action_type,
            'reason': reason,
            'channel_id': channel.id,
            'timestamp': datetime.utcnow().isoformat(),
            'guild_id': channel.guild.id
        }
        
        await self.storage.save_moderation_log(log_data)
        
        # Send to log channel if configured
        log_channel = discord.utils.get(channel.guild.channels, name=Config.LOG_CHANNEL)
        if log_channel:
            embed = discord.Embed(
                title="📋 Moderation Action",
                description=f"**User:** {user.mention}\n"
                           f"**Action:** {action_type}\n"
                           f"**Reason:** {reason}\n"
                           f"**Channel:** {channel.mention}",
                color=Config.COLORS['info']
            )
            embed.timestamp = datetime.utcnow()
            
            try:
                await log_channel.send(embed=embed)
            except discord.Forbidden:
                pass
    
    @app_commands.command(name="purge", description="Delete multiple messages (Moderator+ only)")
    @app_commands.describe(
        amount="Number of messages to delete (1-100)",
        user="Only delete messages from this user",
        reason="Reason for purging messages"
    )
    async def purge(self, interaction: discord.Interaction, amount: int, user: discord.Member = None, reason: str = "No reason provided"):
        """Purge messages from a channel"""
        # Check permissions
        if not Config.is_moderator([role.name for role in interaction.user.roles], interaction.user.id):
            await interaction.response.send_message("❌ You don't have permission to purge messages.", ephemeral=True)
            return
        
        # Validate amount
        if amount < 1 or amount > 100:
            await interaction.response.send_message("❌ Amount must be between 1 and 100.", ephemeral=True)
            return
        
        # Check if user can purge messages from the target user
        if user:
            user_clearance = get_user_clearance(user.roles)
            issuer_clearance = get_user_clearance(interaction.user.roles)
            
            if (Config.has_permission(user_clearance, issuer_clearance) and 
                not Config.is_community_manager(interaction.user.id)):
                await interaction.response.send_message("❌ You cannot purge messages from users with equal or higher clearance.", ephemeral=True)
                return
        
        await interaction.response.defer()
        
        try:
            def check_message(message):
                if user:
                    return message.author == user
                return True
            
            deleted = await interaction.channel.purge(limit=amount, check=check_message)
            
            # Log the action
            await self.log_moderation_action(
                interaction.user,
                "Message Purge",
                f"Deleted {len(deleted)} messages" + (f" from {user.display_name}" if user else "") + f" - {reason}",
                interaction.channel
            )
            
            # Send confirmation
            embed = discord.Embed(
                title="🧹 Messages Purged",
                description=f"**Messages Deleted:** {len(deleted)}\n"
                           f"**Target User:** {user.mention if user else 'All users'}\n"
                           f"**Reason:** {reason}\n"
                           f"**Moderator:** {interaction.user.mention}",
                color=Config.COLORS['success']
            )
            embed.set_footer(text=f"{Config.COMPANY_NAME} - Moderation Action")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except discord.Forbidden:
            await interaction.followup.send("❌ I don't have permission to delete messages in this channel.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error purging messages: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="warn", description="Issue a warning to a user (Moderator+ only)")
    @app_commands.describe(
        user="User to warn",
        reason="Reason for the warning"
    )
    async def warn_user(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        """Warn a user (Moderator only)"""
        if not Config.is_moderator([role.name for role in interaction.user.roles], interaction.user.id):
            await interaction.response.send_message("❌ You don't have permission to warn users.", ephemeral=True)
            return
        
        # Don't warn high-clearance users unless issuer has higher clearance
        user_clearance = get_user_clearance(user.roles)
        issuer_clearance = get_user_clearance(interaction.user.roles)
        
        if (Config.has_permission(user_clearance, issuer_clearance) and 
            not Config.is_community_manager(interaction.user.id)):
            await interaction.response.send_message("❌ You cannot warn users with equal or higher clearance.", ephemeral=True)
            return
        
        # Issue warning
        warning_data = {
            'user_id': user.id,
            'warned_by': interaction.user.id,
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat(),
            'guild_id': interaction.guild.id
        }
        
        await self.storage.save_warning(warning_data)
        
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
    
    @commands.command(name='warnings')
    async def check_warnings(self, ctx, user: discord.Member = None):
        """Check warnings for a user"""
        target_user = user or ctx.author
        
        # Check permissions
        if (target_user != ctx.author and 
            not Config.is_moderator([role.name for role in ctx.author.roles])):
            await ctx.send("❌ You can only check your own warnings.")
            return
        
        warnings = await self.storage.get_user_warnings(target_user.id)
        
        if not warnings:
            await ctx.send(f"✅ {target_user.mention} has no warnings.")
            return
        
        embed = discord.Embed(
            title=f"⚠️ Warning History - {target_user.display_name}",
            description=f"**Total Warnings:** {len(warnings)}",
            color=Config.COLORS['warning']
        )
        
        for i, warning in enumerate(warnings[-5:], 1):  # Show last 5 warnings
            embed.add_field(
                name=f"Warning {i}",
                value=f"**Reason:** {warning['reason']}\n"
                      f"**Date:** {warning['timestamp'][:10]}\n"
                      f"**Issued By:** <@{warning['warned_by']}>",
                inline=False
            )
        
        embed.set_footer(text="Merrywinter Security Consulting - Disciplinary Records")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='mute')
    @commands.has_permissions(manage_roles=True)
    async def mute_user(self, ctx, user: discord.Member, duration: int = 10, *, reason: str = "No reason provided"):
        """Mute a user for specified minutes (Moderator only)"""
        if not Config.is_moderator([role.name for role in ctx.author.roles]):
            await ctx.send("❌ You don't have permission to mute users.")
            return
        
        # Don't mute high-clearance users unless issuer has higher clearance
        user_clearance = get_user_clearance(user.roles)
        issuer_clearance = get_user_clearance(ctx.author.roles)
        
        if (user_clearance in ['OMEGA', 'BETA'] and 
            not Config.has_permission(issuer_clearance, user_clearance)):
            await ctx.send("❌ You cannot mute users with equal or higher clearance.")
            return
        
        # Try to timeout the user (Discord's built-in timeout)
        try:
            timeout_until = datetime.utcnow() + timedelta(minutes=duration)
            await user.timeout(timeout_until, reason=reason)
            
            embed = discord.Embed(
                title="🔇 User Muted",
                description=f"**User:** {user.mention}\n"
                           f"**Duration:** {duration} minutes\n"
                           f"**Reason:** {reason}\n"
                           f"**Muted By:** {ctx.author.mention}",
                color=Config.COLORS['error']
            )
            
            await ctx.send(embed=embed)
            
            # Log the action
            await self.log_moderation_action(
                user,
                "Mute",
                f"{duration} minutes - {reason}",
                ctx.channel
            )
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to mute this user.")
        except Exception as e:
            await ctx.send(f"❌ Error muting user: {str(e)}")
    
    @commands.command(name='unmute')
    @commands.has_permissions(manage_roles=True)
    async def unmute_user(self, ctx, user: discord.Member):
        """Unmute a user (Moderator only)"""
        if not Config.is_moderator([role.name for role in ctx.author.roles]):
            await ctx.send("❌ You don't have permission to unmute users.")
            return
        
        try:
            await user.timeout(None, reason=f"Unmuted by {ctx.author}")
            
            embed = discord.Embed(
                title="🔊 User Unmuted",
                description=f"**User:** {user.mention}\n"
                           f"**Unmuted By:** {ctx.author.mention}",
                color=Config.COLORS['success']
            )
            
            await ctx.send(embed=embed)
            
            # Log the action
            await self.log_moderation_action(
                user,
                "Unmute",
                f"Unmuted by {ctx.author}",
                ctx.channel
            )
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to unmute this user.")
        except Exception as e:
            await ctx.send(f"❌ Error unmuting user: {str(e)}")
    
    @commands.command(name='modlogs')
    @commands.has_permissions(manage_guild=True)
    async def moderation_logs(self, ctx, user: discord.Member = None):
        """View moderation logs (Admin only)"""
        if not Config.is_admin([role.name for role in ctx.author.roles]):
            await ctx.send("❌ You don't have permission to view moderation logs.")
            return
        
        if user:
            logs = await self.storage.get_user_moderation_logs(user.id)
            title = f"Moderation Logs - {user.display_name}"
        else:
            logs = await self.storage.get_guild_moderation_logs(ctx.guild.id)
            title = "Server Moderation Logs"
        
        if not logs:
            await ctx.send("📋 No moderation logs found.")
            return
        
        embed = discord.Embed(
            title=f"📋 {title}",
            description=f"**Total Entries:** {len(logs)}",
            color=Config.COLORS['info']
        )
        
        for i, log in enumerate(logs[-10:], 1):  # Show last 10 logs
            embed.add_field(
                name=f"Entry {i}",
                value=f"**User:** <@{log['user_id']}>\n"
                      f"**Action:** {log['action_type']}\n"
                      f"**Reason:** {log['reason']}\n"
                      f"**Date:** {log['timestamp'][:10]}",
                inline=False
            )
        
        embed.set_footer(text="Merrywinter Security Consulting - Moderation Logs")
        
        await ctx.send(embed=embed)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(ModerationSystem(bot))
