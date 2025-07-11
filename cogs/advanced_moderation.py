"""
Advanced Moderation Features for FROST AI
Enhanced spam detection, phishing protection, and warning system
"""

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import asyncio
import re
import urllib.parse

from config.settings import Config
from utils.helpers import get_user_clearance, create_embed
from utils.storage import Storage
from utils.logger import logger

class AdvancedModeration(commands.Cog):
    """Advanced moderation system with escalation and smart detection"""
    
    def __init__(self, bot):
        self.bot = bot
        self.storage = Storage()
        self.warning_points = {}
        self.escalation_tracking = {}
        self.suspicious_patterns = [
            r'nitro.*free',
            r'discord.*gift',
            r'free.*robux',
            r'hack.*account',
            r'generator.*discord',
            r'steam.*free.*game'
        ]
    
    def cog_check(self, ctx):
        """Check if command is used in authorized guild"""
        return Config.check_guild_authorization(ctx.guild.id)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check if interaction is in authorized guild"""
        return Config.check_guild_authorization(interaction.guild.id)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Enhanced message monitoring"""
        if message.author.bot or not Config.check_guild_authorization(message.guild.id):
            return
        
        # Check for phishing links
        await self.check_phishing_links(message)
        
        # Check for suspicious patterns
        await self.check_suspicious_patterns(message)
        
        # Enhanced spam detection
        await self.enhanced_spam_detection(message)
    
    async def check_phishing_links(self, message):
        """Check for phishing domains and suspicious links"""
        # Extract URLs from message
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', 
                         message.content)
        
        for url in urls:
            parsed_url = urllib.parse.urlparse(url)
            domain = parsed_url.netloc.lower()
            
            # Check against known phishing domains
            if any(phishing_domain in domain for phishing_domain in Config.PHISHING_DOMAINS):
                await self.handle_phishing_detection(message, url, domain)
                return
            
            # Check for suspicious URL patterns
            if self.is_suspicious_url(url):
                await self.handle_suspicious_link(message, url)
    
    def is_suspicious_url(self, url):
        """Check if URL matches suspicious patterns"""
        suspicious_indicators = [
            'bit.ly', 'tinyurl.com', 'short.link',  # URL shorteners
            'discord.com.', 'discordapp.com.',      # Typosquatting
            'steam.com.', 'steampowered.com.',      # Steam typosquatting
        ]
        
        return any(indicator in url.lower() for indicator in suspicious_indicators)
    
    async def check_suspicious_patterns(self, message):
        """Check for suspicious content patterns"""
        content = message.content.lower()
        
        for pattern in self.suspicious_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                await self.handle_suspicious_content(message, pattern)
                break
    
    async def enhanced_spam_detection(self, message):
        """Enhanced spam detection with escalation"""
        user_id = message.author.id
        current_time = datetime.utcnow()
        
        # Initialize tracking
        if user_id not in self.escalation_tracking:
            self.escalation_tracking[user_id] = {
                'messages': [],
                'offenses': 0,
                'last_offense': None
            }
        
        user_data = self.escalation_tracking[user_id]
        user_data['messages'].append({
            'timestamp': current_time,
            'content': message.content,
            'channel': message.channel.id
        })
        
        # Clean old messages (last 60 seconds)
        cutoff_time = current_time - timedelta(seconds=60)
        user_data['messages'] = [
            msg for msg in user_data['messages'] 
            if msg['timestamp'] > cutoff_time
        ]
        
        # Check for various spam patterns
        if await self.detect_spam_patterns(user_data, message):
            await self.escalate_spam_action(message.author, user_data)
    
    async def detect_spam_patterns(self, user_data, message):
        """Detect various spam patterns"""
        messages = user_data['messages']
        
        # Pattern 1: Too many messages in short time
        if len(messages) >= 8:  # 8 messages in 60 seconds
            return True
        
        # Pattern 2: Repeated content
        recent_content = [msg['content'] for msg in messages[-5:]]
        if len(set(recent_content)) <= 2 and len(recent_content) >= 4:
            return True
        
        # Pattern 3: Mass mentions
        if len(message.mentions) >= 5:
            return True
        
        # Pattern 4: Excessive caps
        if len(message.content) > 20 and sum(c.isupper() for c in message.content) / len(message.content) > 0.7:
            return True
        
        return False
    
    async def escalate_spam_action(self, user, user_data):
        """Escalate spam action based on offense count"""
        user_data['offenses'] += 1
        user_data['last_offense'] = datetime.utcnow()
        
        offense_count = user_data['offenses']
        
        # Get escalation action
        if offense_count == 1:
            action = Config.ANTI_SPAM_ESCALATION['first_offense']
        elif offense_count == 2:
            action = Config.ANTI_SPAM_ESCALATION['second_offense']
        elif offense_count == 3:
            action = Config.ANTI_SPAM_ESCALATION['third_offense']
        elif offense_count == 4:
            action = Config.ANTI_SPAM_ESCALATION['fourth_offense']
        else:
            action = Config.ANTI_SPAM_ESCALATION['fifth_offense']
        
        await self.execute_escalation_action(user, action, f"Spam offense #{offense_count}")
    
    async def execute_escalation_action(self, user, action, reason):
        """Execute the escalation action"""
        if action == 'warn':
            await self.issue_warning(user, reason)
        elif action == 'timeout_5min':
            await self.timeout_user(user, 5, reason)
        elif action == 'timeout_1hour':
            await self.timeout_user(user, 60, reason)
        elif action == 'timeout_1day':
            await self.timeout_user(user, 1440, reason)
        elif action == 'ban':
            await self.ban_user(user, reason)
    
    async def issue_warning(self, user, reason):
        """Issue a warning to the user"""
        # Add warning points
        if user.id not in self.warning_points:
            self.warning_points[user.id] = {'points': 0, 'warnings': []}
        
        self.warning_points[user.id]['points'] += Config.WARNING_POINT_SYSTEM.get('spam', 2)
        self.warning_points[user.id]['warnings'].append({
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat(),
            'points': Config.WARNING_POINT_SYSTEM.get('spam', 2)
        })
        
        # Save to storage
        await self.storage.save_warning_points(self.warning_points)
        
        # Send warning message
        embed = discord.Embed(
            title="⚠️ FROST AI WARNING",
            description=f"**{user.mention}**, you have received a warning for: {reason}",
            color=Config.COLORS['warning'],
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="📊 Warning Points", value=f"{self.warning_points[user.id]['points']}", inline=True)
        embed.add_field(name="🔍 Reason", value=reason, inline=True)
        embed.set_footer(text=f"F.R.O.S.T AI • {Config.AI_VERSION}")
        
        # Send to user's current channel
        try:
            await user.send(embed=embed)
        except:
            # If can't DM, send to a general channel
            for channel in user.guild.channels:
                if channel.name in ['general', 'main', 'chat']:
                    await channel.send(embed=embed)
                    break
    
    async def timeout_user(self, user, minutes, reason):
        """Timeout a user for specified minutes"""
        try:
            timeout_until = datetime.utcnow() + timedelta(minutes=minutes)
            await user.timeout(timeout_until, reason=reason)
            
            # Log the action
            if hasattr(self.bot, 'log_moderation_action'):
                await self.bot.log_moderation_action(user, f"TIMEOUT ({minutes}min)", reason, user.guild)
            
        except discord.Forbidden:
            logger.error(f"No permission to timeout {user}")
        except Exception as e:
            logger.error(f"Failed to timeout user: {e}")
    
    async def ban_user(self, user, reason):
        """Ban a user"""
        try:
            await user.ban(reason=reason)
            
            # Log the action
            if hasattr(self.bot, 'log_moderation_action'):
                await self.bot.log_moderation_action(user, "BAN", reason, user.guild)
            
        except discord.Forbidden:
            logger.error(f"No permission to ban {user}")
        except Exception as e:
            logger.error(f"Failed to ban user: {e}")
    
    async def handle_phishing_detection(self, message, url, domain):
        """Handle phishing link detection"""
        # Delete the message
        try:
            await message.delete()
        except:
            pass
        
        # Issue warning
        await self.issue_warning(message.author, f"Phishing link detected: {domain}")
        
        # Alert to moderation channel
        if hasattr(self.bot, 'moderation_log_channel') and self.bot.moderation_log_channel:
            embed = discord.Embed(
                title="🎣 PHISHING DETECTED",
                description=f"**Phishing link detected and removed**",
                color=Config.COLORS['error'],
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(name="👤 User", value=f"{message.author.mention}", inline=True)
            embed.add_field(name="📍 Channel", value=f"{message.channel.mention}", inline=True)
            embed.add_field(name="🔗 Domain", value=f"`{domain}`", inline=True)
            embed.add_field(name="🔗 Full URL", value=f"`{url}`", inline=False)
            embed.set_footer(text=f"F.R.O.S.T AI • {Config.AI_VERSION}")
            
            await self.bot.moderation_log_channel.send(embed=embed)
    
    async def handle_suspicious_link(self, message, url):
        """Handle suspicious link detection"""
        # Alert to moderation channel
        if hasattr(self.bot, 'moderation_log_channel') and self.bot.moderation_log_channel:
            embed = discord.Embed(
                title="🔍 SUSPICIOUS LINK DETECTED",
                description=f"**Suspicious link pattern detected**",
                color=Config.COLORS['warning'],
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(name="👤 User", value=f"{message.author.mention}", inline=True)
            embed.add_field(name="📍 Channel", value=f"{message.channel.mention}", inline=True)
            embed.add_field(name="🔗 URL", value=f"`{url}`", inline=False)
            embed.set_footer(text=f"F.R.O.S.T AI • {Config.AI_VERSION}")
            
            await self.bot.moderation_log_channel.send(embed=embed)
    
    async def handle_suspicious_content(self, message, pattern):
        """Handle suspicious content detection"""
        # Alert to moderation channel
        if hasattr(self.bot, 'moderation_log_channel') and self.bot.moderation_log_channel:
            embed = discord.Embed(
                title="🚨 SUSPICIOUS CONTENT",
                description=f"**Suspicious content pattern detected**",
                color=Config.COLORS['warning'],
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(name="👤 User", value=f"{message.author.mention}", inline=True)
            embed.add_field(name="📍 Channel", value=f"{message.channel.mention}", inline=True)
            embed.add_field(name="🔍 Pattern", value=f"`{pattern}`", inline=True)
            embed.add_field(name="📝 Content", value=f"```{message.content[:500]}```", inline=False)
            embed.set_footer(text=f"F.R.O.S.T AI • {Config.AI_VERSION}")
            
            await self.bot.moderation_log_channel.send(embed=embed)
    
    @app_commands.command(name="warning-points", description="Check warning points for a user")
    async def check_warning_points(self, interaction: discord.Interaction, user: discord.Member = None):
        """Check warning points for a user"""
        target_user = user or interaction.user
        
        if target_user.id not in self.warning_points:
            await interaction.response.send_message(
                f"📊 {target_user.mention} has no warning points.", 
                ephemeral=True
            )
            return
        
        user_data = self.warning_points[target_user.id]
        
        embed = discord.Embed(
            title=f"📊 Warning Points - {target_user.display_name}",
            description=f"**Total Points:** {user_data['points']}",
            color=Config.COLORS['warning'],
            timestamp=datetime.utcnow()
        )
        
        # Show recent warnings
        recent_warnings = user_data['warnings'][-5:]  # Last 5 warnings
        
        for i, warning in enumerate(recent_warnings, 1):
            embed.add_field(
                name=f"Warning #{i}",
                value=f"**Reason:** {warning['reason']}\n"
                      f"**Points:** {warning['points']}\n"
                      f"**Date:** <t:{int(datetime.fromisoformat(warning['timestamp']).timestamp())}:R>",
                inline=False
            )
        
        embed.set_footer(text=f"F.R.O.S.T AI • {Config.AI_VERSION}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="clear-warnings", description="Clear warning points for a user (Admin only)")
    async def clear_warnings(self, interaction: discord.Interaction, user: discord.Member):
        """Clear warning points for a user"""
        # Check permissions
        if not Config.is_moderator([role.name for role in interaction.user.roles], interaction.user.id):
            await interaction.response.send_message("❌ You don't have permission to clear warnings.", ephemeral=True)
            return
        
        if user.id in self.warning_points:
            del self.warning_points[user.id]
            await self.storage.save_warning_points(self.warning_points)
            
            await interaction.response.send_message(
                f"✅ Warning points cleared for {user.mention}",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"📊 {user.mention} has no warning points to clear.",
                ephemeral=True
            )

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(AdvancedModeration(bot))