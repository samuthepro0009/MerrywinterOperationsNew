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
            description="Merrywinter Security Consulting - Professional PMC Operations Bot"
        )
        
        self.config = Config()
        self.storage = Storage()
        self.start_time = datetime.utcnow()
        
        # Anti-raid system
        self.recent_joins = []
        self.lockdown_mode = False
        
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
                await self.tree.sync(guild=guild)
                logger.info(f"Synced slash commands to guild {Config.AUTHORIZED_GUILD_ID}")
            except Exception as e:
                logger.error(f"Failed to sync slash commands: {e}")
            
            # Start background tasks
            self.status_update.start()
            self.health_check.start()
            
            logger.info("Bot setup completed successfully")
            
        except Exception as e:
            logger.error(f"Error during setup: {e}")
    
    async def on_ready(self):
        """Event triggered when bot is ready"""
        logger.info(f"🚁 {self.user} has landed! {Config.COMPANY_NAME} is operational.")
        logger.info(f"Bot is serving {len(self.guilds)} guilds")
        logger.info(f"Latency: {round(self.latency * 1000)}ms")
        logger.info(f"Motto: {Config.COMPANY_MOTTO}")
        logger.info(f"Established: {Config.COMPANY_ESTABLISHED}")
        
        # Set initial status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{Config.COMPANY_MOTTO} | /help"
            ),
            status=discord.Status.online
        )
    
    async def on_member_join(self, member):
        """Handle member joins with anti-raid protection"""
        if not Config.check_guild_authorization(member.guild.id):
            return
            
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
    
    @tasks.loop(minutes=5)
    async def status_update(self):
        """Update bot status periodically"""
        try:
            statuses = [
                "Roblox PMC Operations",
                f"{len(self.guilds)} Military Installations",
                "Security Clearance Alpha-Omega",
                "Operator Status: ACTIVE",
                "Mission Briefings Available"
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
    
    @tasks.loop(minutes=30)
    async def health_check(self):
        """Perform health check and log statistics"""
        try:
            uptime = datetime.utcnow() - self.start_time
            
            logger.info(f"Health Check - Uptime: {uptime}, Guilds: {len(self.guilds)}, "
                       f"Latency: {round(self.latency * 1000)}ms")
            
            # Clean up old data if needed
            await self.storage.cleanup_old_data()
            
        except Exception as e:
            logger.error(f"Error during health check: {e}")
    
    @status_update.before_loop
    @health_check.before_loop
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
