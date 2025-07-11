"""
Merrywinter Security Consulting Discord Bot
A comprehensive Discord bot for Roblox PMC operations management
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

from config.settings import Config
from utils.logger import setup_logger
from utils.storage import Storage

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger()

class MerrywinterBot(commands.Bot):
    """Main bot class for Merrywinter Security Consulting"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        
        super().__init__(
            command_prefix=Config.COMMAND_PREFIX,
            intents=intents,
            help_command=None,
            description=f"{Config.AI_FULL_NAME} - Advanced AI Command System"
        )
        
        self.config = Config()
        self.storage = Storage()
        self.start_time = datetime.utcnow()
        
        # Anti-raid system
        self.recent_joins = []
        self.lockdown_mode = False
        
        # AI System status
        self.ai_status_index = 0
        self.uptime_start = datetime.utcnow()
        
        # Enhanced logging
        self.moderation_log_channel = None
        
    async def setup_hook(self):
        """Load all cogs and setup the bot"""
        try:
            # Add global slash commands first
            self.tree.add_command(discord.app_commands.Command(name='help', description='Display comprehensive help information', callback=help_command))
            self.tree.add_command(discord.app_commands.Command(name='info', description='Display bot information', callback=info_command))
            self.tree.add_command(discord.app_commands.Command(name='ping', description='Check bot latency', callback=ping_command))
            
            # Load all cogs
            cogs = [
                'cogs.tickets',
                'cogs.security',
                'cogs.operations',
                'cogs.moderation',
                'cogs.admin',
                'cogs.high_command'
            ]
            
            for cog in cogs:
                try:
                    await self.load_extension(cog)
                    logger.info(f"Loaded cog: {cog}")
                except Exception as e:
                    logger.error(f"Failed to load cog {cog}: {e}")
            
            # Sync slash commands to the authorized guild only
            try:
                guild = discord.Object(id=Config.AUTHORIZED_GUILD_ID)
                synced = await self.tree.sync(guild=guild)
                logger.info(f"Synced {len(synced)} slash commands to guild {Config.AUTHORIZED_GUILD_ID}")
                
                # Also try global sync as fallback
                global_synced = await self.tree.sync()
                logger.info(f"Synced {len(global_synced)} slash commands globally")
                
            except Exception as e:
                logger.error(f"Failed to sync slash commands: {e}")
                # Try global sync as fallback
                try:
                    global_synced = await self.tree.sync()
                    logger.info(f"Fallback: Synced {len(global_synced)} slash commands globally")
                except Exception as e2:
                    logger.error(f"Failed to sync slash commands globally: {e2}")
            
            # Start background tasks
            self.status_update.start()
            self.health_check.start()
            
            # Start keepalive for 24/7 uptime
            if Config.ENABLE_KEEPALIVE:
                self.keepalive.start()
            
            logger.info("Bot setup completed successfully")
            
        except Exception as e:
            logger.error(f"Error during setup: {e}")
    
    async def on_ready(self):
        """Event triggered when bot is ready"""
        # Frost AI startup sequence
        logger.info("=" * 60)
        logger.info(f"🤖 {Config.AI_NAME} {Config.AI_VERSION} - INITIALIZING")
        logger.info(f"System Name: {Config.AI_FULL_NAME}")
        logger.info(f"Connected as: {self.user}")
        logger.info(f"Serving {len(self.guilds)} combat zones")
        logger.info(f"Network latency: {round(self.latency * 1000)}ms")
        logger.info(f"Mission: {Config.COMPANY_MOTTO}")
        logger.info(f"Established: {Config.COMPANY_ESTABLISHED}")
        logger.info("=" * 60)
        
        # Get moderation log channel
        try:
            self.moderation_log_channel = self.get_channel(Config.MODERATION_LOG_CHANNEL_ID)
            if self.moderation_log_channel:
                logger.info(f"📋 Moderation logging channel acquired: {self.moderation_log_channel.name}")
        except Exception as e:
            logger.error(f"Failed to get moderation log channel: {e}")
        
        # Set AI status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{Config.AI_STATUS_MESSAGES[2]} | /help"
            ),
            status=discord.Status.online
        )
        
        # Send startup message to moderation log
        if self.moderation_log_channel:
            embed = discord.Embed(
                title="🤖 F.R.O.S.T AI SYSTEM ONLINE",
                description=f"```\n{Config.AI_STATUS_MESSAGES[0]}\n{Config.AI_STATUS_MESSAGES[1]}\n\n{Config.AI_STATUS_MESSAGES[2]}\n{Config.AI_STATUS_MESSAGES[3]}\n```",
                color=0x00ff41,
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="🌐 Network Status", value=f"Latency: {round(self.latency * 1000)}ms", inline=True)
            embed.add_field(name="🏢 Combat Zones", value=f"{len(self.guilds)} active", inline=True)
            embed.add_field(name="⏰ Boot Time", value=f"<t:{int(self.uptime_start.timestamp())}:R>", inline=True)
            embed.set_footer(text=f"{Config.AI_FULL_NAME} • {Config.AI_VERSION}")
            
            try:
                await self.moderation_log_channel.send(embed=embed)
            except Exception as e:
                logger.error(f"Failed to send startup message: {e}")
    
    async def on_member_join(self, member):
        """Handle member joins with anti-raid protection and logging"""
        if not Config.check_guild_authorization(member.guild.id):
            return
        
        # Log member join
        await self.log_member_action(member, "JOIN", f"New member joined the server")
        
        if Config.ANTI_RAID_ENABLED:
            current_time = datetime.utcnow()
            
            # Add to recent joins
            self.recent_joins.append({
                'user_id': member.id,
                'timestamp': current_time,
                'guild_id': member.guild.id
            })
            
            # Clean old entries
            cutoff_time = current_time - timedelta(seconds=Config.RAID_DETECTION_TIMEFRAME)
            self.recent_joins = [
                join for join in self.recent_joins 
                if join['timestamp'] > cutoff_time and join['guild_id'] == member.guild.id
            ]
            
            # Check for raid
            if len(self.recent_joins) >= Config.RAID_DETECTION_THRESHOLD:
                await self.handle_raid_detection(member.guild)
    
    async def handle_raid_detection(self, guild):
        """Handle raid detection"""
        logger.warning(f"Raid detected in guild {guild.name} ({guild.id})")
        
        if Config.RAID_ACTION == 'lockdown':
            self.lockdown_mode = True
            # Lock down the server
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel):
                    try:
                        await channel.set_permissions(
                            guild.default_role,
                            send_messages=False,
                            reason="Anti-raid lockdown"
                        )
                    except discord.Forbidden:
                        pass
        
        # Log to admin channel
        log_channel = discord.utils.get(guild.channels, name=Config.LOG_CHANNEL)
        if log_channel:
            embed = discord.Embed(
                title="🚨 RAID DETECTED",
                description=f"**Action Taken:** {Config.RAID_ACTION.title()}\n"
                           f"**Detection Time:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
                           f"**Threshold:** {Config.RAID_DETECTION_THRESHOLD} users in {Config.RAID_DETECTION_TIMEFRAME} seconds",
                color=0xFF0000
            )
            await log_channel.send(embed=embed)
    
    async def on_guild_join(self, guild):
        """Event triggered when bot joins a guild"""
        logger.info(f"Joined guild: {guild.name} (ID: {guild.id})")
        
        # Check if authorized to work in this guild
        if not Config.check_guild_authorization(guild.id):
            embed = discord.Embed(
                title="⚠️ Unauthorized Guild",
                description=f"This bot is configured to work only in authorized guilds.\n"
                           f"Guild ID: {guild.id}\n"
                           f"Please contact the bot administrators if you believe this is an error.",
                color=0xFF0000
            )
            
            if guild.system_channel:
                try:
                    await guild.system_channel.send(embed=embed)
                except discord.Forbidden:
                    pass
            
            logger.warning(f"Left unauthorized guild: {guild.name} ({guild.id})")
            await guild.leave()
            return
        
        # Send welcome message to system channel
        if guild.system_channel:
            embed = discord.Embed(
                title=f"🚁 {Config.COMPANY_NAME}",
                description=f"**{Config.COMPANY_MOTTO}**\n"
                           f"*{Config.COMPANY_ESTABLISHED}*\n\n"
                           f"Founded by: {', '.join(Config.COMPANY_FOUNDERS)}\n\n"
                           "**Getting Started:**\n"
                           f"• Use `/help` to see all commands\n"
                           f"• Use `/setup` to configure the bot\n"
                           f"• Use `/info` for more information\n\n"
                           "**Key Features:**\n"
                           "• Advanced Ticket System\n"
                           "• Military Chain of Command\n"
                           "• PMC Operations Management\n"
                           "• Anti-Raid Protection\n"
                           "• High Command Operations",
                color=0x2F3136
            )
            embed.set_footer(text=f"{Config.COMPANY_NAME} - Professional PMC Operations")
            await guild.system_channel.send(embed=embed)
    
    async def on_member_remove(self, member):
        """Handle member leaves"""
        if not Config.check_guild_authorization(member.guild.id):
            return
        
        # Log member leave
        await self.log_member_action(member, "LEAVE", f"Member left the server")
    
    async def on_message_delete(self, message):
        """Handle message deletions"""
        if not Config.check_guild_authorization(message.guild.id):
            return
        
        if message.author.bot:
            return
            
        # Log message deletion
        await self.log_message_action(message, "DELETE", f"Message deleted")
    
    async def on_message_edit(self, before, after):
        """Handle message edits"""
        if not Config.check_guild_authorization(before.guild.id):
            return
        
        if before.author.bot or before.content == after.content:
            return
            
        # Log message edit
        await self.log_message_edit(before, after)
    
    async def on_member_ban(self, guild, user):
        """Handle member bans"""
        if not Config.check_guild_authorization(guild.id):
            return
        
        await self.log_moderation_action(user, "BAN", "Member was banned", guild)
    
    async def on_member_unban(self, guild, user):
        """Handle member unbans"""
        if not Config.check_guild_authorization(guild.id):
            return
        
        await self.log_moderation_action(user, "UNBAN", "Member was unbanned", guild)
    
    @tasks.loop(minutes=5)
    async def status_update(self):
        """Update bot status periodically with FROST AI messages"""
        try:
            statuses = Config.AI_STATUS_MESSAGES + [
                f"Monitoring {len(self.guilds)} Combat Zones",
                "Threat Assessment: ACTIVE",
                "Personnel Tracking: ONLINE",
                "Security Protocols: ENGAGED"
            ]
            
            import random
            status = random.choice(statuses)
            
            await self.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name=f"{status} | /help"
                ),
                status=discord.Status.online
            )
            
        except Exception as e:
            logger.error(f"Error updating status: {e}")
    
    async def log_member_action(self, member, action_type, description):
        """Log member actions to moderation channel"""
        if not self.moderation_log_channel:
            return
        
        embed = discord.Embed(
            title=f"👤 MEMBER {action_type}",
            color=0x00ff41 if action_type == "JOIN" else 0xff4444,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="👤 Member", value=f"{member.mention} ({member})", inline=False)
        embed.add_field(name="🆔 User ID", value=f"`{member.id}`", inline=True)
        embed.add_field(name="📅 Account Created", value=f"<t:{int(member.created_at.timestamp())}:R>", inline=True)
        
        if action_type == "JOIN":
            embed.add_field(name="📊 Member Count", value=f"{member.guild.member_count}", inline=True)
        
        embed.set_footer(text=f"F.R.O.S.T AI • {Config.AI_VERSION}")
        
        try:
            await self.moderation_log_channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Failed to log member action: {e}")
    
    async def log_message_action(self, message, action_type, description):
        """Log message actions to moderation channel"""
        if not self.moderation_log_channel:
            return
        
        embed = discord.Embed(
            title=f"💬 MESSAGE {action_type}",
            color=0xff4444,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="👤 Author", value=f"{message.author.mention} ({message.author})", inline=False)
        embed.add_field(name="📍 Channel", value=f"{message.channel.mention}", inline=True)
        embed.add_field(name="🆔 Message ID", value=f"`{message.id}`", inline=True)
        
        # Truncate long messages
        content = message.content[:1000] + "..." if len(message.content) > 1000 else message.content
        if content:
            embed.add_field(name="📝 Content", value=f"```{content}```", inline=False)
        
        embed.set_footer(text=f"F.R.O.S.T AI • {Config.AI_VERSION}")
        
        try:
            await self.moderation_log_channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Failed to log message action: {e}")
    
    async def log_message_edit(self, before, after):
        """Log message edits to moderation channel"""
        if not self.moderation_log_channel:
            return
        
        embed = discord.Embed(
            title="✏️ MESSAGE EDITED",
            color=0xffa500,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="👤 Author", value=f"{before.author.mention} ({before.author})", inline=False)
        embed.add_field(name="📍 Channel", value=f"{before.channel.mention}", inline=True)
        embed.add_field(name="🆔 Message ID", value=f"`{before.id}`", inline=True)
        
        # Truncate long messages
        before_content = before.content[:500] + "..." if len(before.content) > 500 else before.content
        after_content = after.content[:500] + "..." if len(after.content) > 500 else after.content
        
        if before_content:
            embed.add_field(name="📝 Before", value=f"```{before_content}```", inline=False)
        if after_content:
            embed.add_field(name="📝 After", value=f"```{after_content}```", inline=False)
        
        embed.set_footer(text=f"F.R.O.S.T AI • {Config.AI_VERSION}")
        
        try:
            await self.moderation_log_channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Failed to log message edit: {e}")
    
    async def log_moderation_action(self, user, action_type, reason, guild):
        """Log moderation actions to moderation channel"""
        if not self.moderation_log_channel:
            return
        
        embed = discord.Embed(
            title=f"🔨 MODERATION - {action_type}",
            color=0xff0000,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="👤 User", value=f"{user.mention} ({user})", inline=False)
        embed.add_field(name="🆔 User ID", value=f"`{user.id}`", inline=True)
        embed.add_field(name="⚖️ Action", value=f"{action_type}", inline=True)
        embed.add_field(name="📝 Reason", value=reason, inline=False)
        
        embed.set_footer(text=f"F.R.O.S.T AI • {Config.AI_VERSION}")
        
        try:
            await self.moderation_log_channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Failed to log moderation action: {e}")
    
    @tasks.loop(minutes=Config.HEALTH_CHECK_INTERVAL)
    async def health_check(self):
        """Enhanced health check with 24/7 monitoring"""
        try:
            uptime = datetime.utcnow() - self.start_time
            
            logger.info(f"🤖 FROST AI Health Check - Uptime: {uptime}, Guilds: {len(self.guilds)}, "
                       f"Latency: {round(self.latency * 1000)}ms")
            
            # Clean up old data if needed
            await self.storage.cleanup_old_data()
            
            # Log detailed health status to moderation channel every hour
            if uptime.total_seconds() % 3600 < Config.HEALTH_CHECK_INTERVAL * 60:
                await self.log_health_status(uptime)
            
        except Exception as e:
            logger.error(f"Error during health check: {e}")
            if Config.AUTO_RESTART_ON_ERROR:
                logger.info("Attempting to recover from error...")
                await self.recover_from_error()
    
    async def log_health_status(self, uptime):
        """Log detailed health status to moderation channel"""
        if not self.moderation_log_channel:
            return
        
        embed = discord.Embed(
            title="🤖 F.R.O.S.T AI HEALTH STATUS",
            color=Config.COLORS['frost'],
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="⏱️ Uptime", value=f"{uptime.days}d {uptime.seconds//3600}h {(uptime.seconds%3600)//60}m", inline=True)
        embed.add_field(name="🌐 Latency", value=f"{round(self.latency * 1000)}ms", inline=True)
        embed.add_field(name="🏢 Combat Zones", value=f"{len(self.guilds)}", inline=True)
        embed.add_field(name="📊 Status", value="OPERATIONAL", inline=True)
        embed.add_field(name="🛡️ Security", value="ACTIVE", inline=True)
        embed.add_field(name="📡 Network", value="CONNECTED", inline=True)
        
        embed.set_footer(text=f"F.R.O.S.T AI • {Config.AI_VERSION} • Auto-monitoring active")
        
        try:
            await self.moderation_log_channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Failed to log health status: {e}")
    
    async def recover_from_error(self):
        """Attempt to recover from errors"""
        try:
            # Try to reconnect
            if self.is_closed():
                logger.info("Attempting to reconnect...")
                await self.connect()
            
            # Reset status
            await self.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name=f"FROST AI RECOVERY MODE | /help"
                ),
                status=discord.Status.online
            )
            
            logger.info("Recovery attempt completed")
        except Exception as e:
            logger.error(f"Recovery failed: {e}")
    
    @tasks.loop(minutes=Config.KEEPALIVE_INTERVAL)
    async def keepalive(self):
        """Keep the bot alive for 24/7 uptime on Render"""
        try:
            # Send a minimal request to keep the service alive
            if self.guilds:
                guild = self.guilds[0]
                # Just check if we can access the guild
                await guild.fetch_member(self.user.id)
                
            logger.debug("Keepalive ping successful")
        except Exception as e:
            logger.error(f"Keepalive failed: {e}")
    
    @status_update.before_loop
    @health_check.before_loop
    @keepalive.before_loop
    async def before_loops(self):
        """Wait until bot is ready before starting loops"""
        await self.wait_until_ready()

# Slash commands
async def help_command(interaction: discord.Interaction):
    """Display comprehensive help information"""
    embed = discord.Embed(
        title=f"🚁 {Config.COMPANY_NAME} - Command Center",
        description="**Professional PMC Operations Management**\n"
                   f"*{Config.COMPANY_MOTTO}* - {Config.COMPANY_ESTABLISHED}\n"
                   "Use these slash commands to manage operations and maintain security protocols.",
        color=Config.COLORS['primary']
    )
    
    # Ticket System Commands
    embed.add_field(
        name="🎫 Ticket System",
        value="`/report-operator` - Report operator misconduct\n"
              "`/commission` - Commission PMC services\n"
              "`/tech-issue` - Report technical issues\n"
              "`/ticket-status` - Check ticket status\n"
              "`/close-ticket` - Close ticket (Staff only)",
        inline=False
    )
    
    # Security Clearance Commands
    embed.add_field(
        name="🛡️ Security Clearance",
        value="`/clearance` - Check security clearance\n"
              "`/roster` - View operator roster\n"
              "`/promote` - Promote operator (Admin only)\n"
              "`/demote` - Demote operator (Admin only)\n"
              "`/audit` - Security audit (Admin only)",
        inline=False
    )
    
    # PMC Operations Commands
    embed.add_field(
        name="⚔️ PMC Operations",
        value="`/mission` - Get mission briefing\n"
              "`/status` - Check operator status\n"
              "`/deploy` - Deploy to sector\n"
              "`/intel` - Access intelligence reports\n"
              "`/sitrep` - Current situation report",
        inline=False
    )
    
    # High Command Operations
    embed.add_field(
        name="🎯 High Command",
        value="`/deployment` - Authorize deployments (Director+ only)\n"
              "`/operation-start` - Start operations (Chief+ only)\n"
              "`/operation-log` - Log operation activities (Director+ only)",
        inline=False
    )
    
    # Moderation Commands
    embed.add_field(
        name="🛡️ Moderation",
        value="`/purge` - Delete multiple messages (Moderator+ only)\n"
              "`/warn` - Issue warning (Moderator+ only)\n"
              "`/warnings` - Check warnings\n"
              "`/mute` - Mute user (Moderator+ only)\n"
              "`/unmute` - Unmute user (Moderator+ only)",
        inline=False
    )
    
    # Administrative Commands
    embed.add_field(
        name="🔧 Administrative",
        value="`/setup` - Initial bot setup (Admin only)\n"
              "`/verify` - Verify bot configuration\n"
              "`/stats` - Bot statistics\n"
              "`/backup` - Create data backup (Admin only)\n"
              "`/maintenance` - Toggle maintenance mode",
        inline=False
    )
    
    embed.add_field(
        name="📊 Bot Information",
        value="`/info` - Bot information\n"
              "`/ping` - Check bot latency",
        inline=False
    )
    
    embed.set_footer(text=f"{Config.COMPANY_NAME} - Professional PMC Operations | Founded by: {', '.join(Config.COMPANY_FOUNDERS)}")
    await interaction.response.send_message(embed=embed)

async def info_command(interaction: discord.Interaction):
    """Display bot information"""
    bot = interaction.client
    uptime = datetime.utcnow() - bot.start_time
    
    embed = discord.Embed(
        title=f"🚁 {Config.COMPANY_NAME}",
        description="**Professional PMC Operations Management Bot**\n"
                   f"*{Config.COMPANY_MOTTO}* (Under the shadow, we conquer)",
        color=Config.COLORS['primary']
    )
    
    embed.add_field(
        name="📋 Company Information",
        value=f"**Founded:** {Config.COMPANY_ESTABLISHED}\n"
              f"**Founders:** {', '.join(Config.COMPANY_FOUNDERS)}\n"
              f"**Motto:** {Config.COMPANY_MOTTO}\n"
              f"**Operations:** 24/7 Global Coverage",
        inline=False
    )
    
    embed.add_field(
        name="🎯 Mission Statement",
        value="Providing professional military contracting services with "
              "uncompromising standards of excellence, operational security, "
              "and tactical superiority in all operational theaters.",
        inline=False
    )
    
    embed.add_field(
        name="🛡️ Security Clearance Levels",
        value="**BOARD/CHIEF** - Executive Leadership\n"
              "**DIRECTOR** - Department Leadership\n"
              "**SPECIALIZED** - Operational Specialists\n"
              "**OMEGA** - Supreme Command Authority\n"
              "**BETA** - Field Command & Operations\n"
              "**ALPHA** - Ground Operations & Reconnaissance",
        inline=False
    )
    
    embed.add_field(
        name="👥 Moderation Structure",
        value="**Community Managers** - Ultimate Authority\n"
              "**Administrators** - Server Management\n"
              "**Moderators** - Community Oversight\n"
              "**Helpers** - Community Support",
        inline=False
    )
    
    embed.add_field(
        name="📊 Bot Statistics",
        value=f"**Uptime:** {str(uptime).split('.')[0]}\n"
              f"**Guilds:** {len(bot.guilds)}\n"
              f"**Latency:** {round(bot.latency * 1000)}ms\n"
              f"**Version:** 3.0.0",
        inline=False
    )
    
    embed.set_footer(text=f"{Config.COMPANY_NAME} - Professional PMC Operations")
    await interaction.response.send_message(embed=embed)

async def ping_command(interaction: discord.Interaction):
    """Check bot latency"""
    bot = interaction.client
    latency = round(bot.latency * 1000)
    
    if latency < 100:
        status = "🟢 Excellent"
    elif latency < 200:
        status = "🟡 Good"
    else:
        status = "🔴 Poor"
    
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"**Latency:** {latency}ms\n"
                   f"**Status:** {status}\n"
                   f"**Guild:** {interaction.guild.name if interaction.guild else 'DM'}",
        color=Config.COLORS['success']
    )
    embed.set_footer(text=f"{Config.COMPANY_NAME} - Network Diagnostics")
    await interaction.response.send_message(embed=embed)

async def main():
    """Main function to run the bot"""
    bot = MerrywinterBot()
    
    # Get bot token from environment
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        logger.error("DISCORD_TOKEN environment variable not found!")
        return
    
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
