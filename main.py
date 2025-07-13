"""
Merrywinter Security Consulting Discord Bot
A streamlined Discord bot for PMC operations management
"""

import os
import asyncio
import logging
from datetime import datetime
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from config.settings import Config
from utils.logger import setup_logger
from utils.storage import Storage
import aiohttp
import threading
import time

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
            description="F.R.O.S.T AI - PMC Operations Management System"
        )

        self.config = Config()
        self.storage = Storage()
        self.start_time = datetime.utcnow()
        
        # Essential tracking
        self.command_usage_stats = {}
        self.bot_stats = {}
        
        # 24/7 Uptime features
        self.last_heartbeat = datetime.utcnow()
        self.health_check_url = None
        self.session = None

    async def setup_hook(self):
        """Load all cogs and setup the bot"""
        try:
            # Add global slash commands
            self.tree.add_command(discord.app_commands.Command(name='help', description='Display help information', callback=help_command))
            self.tree.add_command(discord.app_commands.Command(name='info', description='Display bot information', callback=info_command))
            self.tree.add_command(discord.app_commands.Command(name='ping', description='Check bot latency', callback=ping_command))

            # Load essential cogs only
            cogs = [
                'cogs.tickets',
                'cogs.security',
                'cogs.operations',
                'cogs.moderation',
                'cogs.admin',
                'cogs.high_command',
                'cogs.intelligence',
                'cogs.communications',
                'cogs.alerts',
                'cogs.audit'
            ]

            for cog in cogs:
                try:
                    await self.load_extension(cog)
                    logger.info(f"Loaded cog: {cog}")
                except Exception as e:
                    logger.error(f"Failed to load cog {cog}: {e}")

            # Sync slash commands globally
            try:
                synced = await self.tree.sync()
                logger.info(f"Synced {len(synced)} slash commands globally")
            except Exception as e:
                logger.error(f"Failed to sync slash commands: {e}")

            # Start background tasks
            self.status_update.start()
            
            # Start 24/7 uptime features
            if Config.ENABLE_KEEPALIVE:
                self.keep_alive.start()
                self.health_monitor.start()

        except Exception as e:
            logger.error(f"Error in setup_hook: {e}")

    async def on_ready(self):
        """Event triggered when bot is ready"""
        logger.info(f"Bot logged in as {self.user}")
        logger.info(f"Bot is ready in {len(self.guilds)} guilds")
        
        # Set status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="PMC Operations | /help"
            ),
            status=discord.Status.online
        )

    async def on_member_join(self, member):
        """Handle member joins"""
        if not Config.check_guild_authorization(member.guild.id):
            return
        
        logger.info(f"Member {member.name} joined {member.guild.name}")

    async def on_member_remove(self, member):
        """Handle member leaves"""
        if not Config.check_guild_authorization(member.guild.id):
            return
        
        logger.info(f"Member {member.name} left {member.guild.name}")

    async def on_guild_join(self, guild):
        """Event triggered when bot joins a guild"""
        logger.info(f"Joined guild: {guild.name} (ID: {guild.id})")

        # Check if authorized to work in this guild
        if not Config.check_guild_authorization(guild.id):
            logger.warning(f"Unauthorized guild - leaving: {guild.name} ({guild.id})")
            await guild.leave()
            return

        # Send welcome message
        if guild.system_channel:
            embed = discord.Embed(
                title=f"🚁 {Config.COMPANY_NAME}",
                description=f"**{Config.COMPANY_MOTTO}**\n\n"
                           "**Getting Started:**\n"
                           "• Use `/help` to see all commands\n"
                           "• Use `/setup` to configure the bot\n"
                           "• Use `/info` for more information\n\n"
                           "**Key Features:**\n"
                           "• Ticket System\n"
                           "• Security Clearance\n"
                           "• Operations Management\n"
                           "• Moderation Tools",
                color=0x2F3136
            )
            embed.set_footer(text=f"{Config.COMPANY_NAME} - Professional PMC Operations")
            await guild.system_channel.send(embed=embed)

    @tasks.loop(minutes=30)
    async def status_update(self):
        """Update bot status periodically"""
        try:
            await self.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name=f"PMC Operations | {len(self.guilds)} guilds"
                ),
                status=discord.Status.online
            )
        except Exception as e:
            logger.error(f"Error updating status: {e}")

    @status_update.before_loop
    async def before_status_update(self):
        """Wait until bot is ready before starting loops"""
        await self.wait_until_ready()

    @tasks.loop(minutes=Config.KEEPALIVE_INTERVAL)
    async def keep_alive(self):
        """Keep the bot alive by pinging itself"""
        try:
            self.last_heartbeat = datetime.utcnow()
            
            # Create session if not exists
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Try to ping the web dashboard if available
            try:
                async with self.session.get('http://0.0.0.0:5000/api/health', timeout=10) as response:
                    if response.status == 200:
                        logger.info("✅ Keep-alive ping successful")
                    else:
                        logger.warning(f"⚠️ Keep-alive ping returned status {response.status}")
            except Exception as ping_error:
                logger.debug(f"Keep-alive ping failed (normal if web dashboard not running): {ping_error}")
            
            # Update bot stats
            self.bot_stats.update({
                'last_heartbeat': self.last_heartbeat.isoformat(),
                'uptime_hours': round((datetime.utcnow() - self.start_time).total_seconds() / 3600, 2),
                'guilds': len(self.guilds),
                'latency': round(self.latency * 1000)
            })
            
        except Exception as e:
            logger.error(f"Keep-alive error: {e}")

    @tasks.loop(minutes=Config.HEALTH_CHECK_INTERVAL)
    async def health_monitor(self):
        """Monitor bot health and log status"""
        try:
            uptime = datetime.utcnow() - self.start_time
            uptime_hours = round(uptime.total_seconds() / 3600, 2)
            
            # Log health status
            logger.info(f"🤖 FROST AI Health Check - Uptime: {uptime_hours}h | Guilds: {len(self.guilds)} | Latency: {round(self.latency * 1000)}ms")
            
            # Check if bot is responding
            if (datetime.utcnow() - self.last_heartbeat).total_seconds() > 3600:  # 1 hour
                logger.warning("⚠️ Bot heartbeat delayed - potential connection issues")
                
                # Attempt to reconnect if auto-restart enabled
                if Config.AUTO_RESTART_ON_ERROR:
                    logger.info("🔄 Attempting to refresh connection...")
                    await self.change_presence(
                        activity=discord.Activity(
                            type=discord.ActivityType.watching,
                            name="Systems Recovering..."
                        ),
                        status=discord.Status.idle
                    )
                    await asyncio.sleep(5)
                    await self.change_presence(
                        activity=discord.Activity(
                            type=discord.ActivityType.watching,
                            name="PMC Operations | /help"
                        ),
                        status=discord.Status.online
                    )
            
        except Exception as e:
            logger.error(f"Health monitor error: {e}")

    @keep_alive.before_loop
    async def before_keep_alive(self):
        """Wait until bot is ready before starting keep-alive"""
        await self.wait_until_ready()

    @health_monitor.before_loop
    async def before_health_monitor(self):
        """Wait until bot is ready before starting health monitor"""
        await self.wait_until_ready()

    async def close(self):
        """Clean shutdown"""
        try:
            # Stop all tasks
            if hasattr(self, 'keep_alive'):
                self.keep_alive.cancel()
            if hasattr(self, 'health_monitor'):
                self.health_monitor.cancel()
            if hasattr(self, 'status_update'):
                self.status_update.cancel()
            
            # Close aiohttp session
            if self.session:
                await self.session.close()
                
            logger.info("🔄 FROST AI shutting down gracefully...")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        finally:
            await super().close()

async def help_command(interaction: discord.Interaction):
    """Display help information"""
    embed = discord.Embed(
        title="🚁 F.R.O.S.T AI Command Center",
        description=f"**{Config.COMPANY_NAME}** - {Config.COMPANY_MOTTO}",
        color=0x00ff41
    )
    
    embed.add_field(
        name="📋 **Essential Commands**",
        value="• `/help` - Show this help menu\n"
              "• `/info` - Bot information\n"
              "• `/ping` - Check bot latency\n"
              "• `/setup` - Configure bot (Admin only)",
        inline=False
    )
    
    embed.add_field(
        name="🎫 **Ticket System**",
        value="• `/create-ticket` - Create support ticket\n"
              "• `/close-ticket` - Close current ticket\n"
              "• `/ticket-info` - Get ticket information",
        inline=False
    )
    
    embed.add_field(
        name="🔒 **Security & Operations**",
        value="• `/clearance` - Check security clearance\n"
              "• `/mission-brief` - Get mission briefing\n"
              "• `/deployment` - Deployment commands",
        inline=False
    )
    
    embed.set_footer(text=f"{Config.COMPANY_NAME} - Professional PMC Operations")
    await interaction.response.send_message(embed=embed)

async def info_command(interaction: discord.Interaction):
    """Display bot information"""
    bot = interaction.client
    uptime = datetime.utcnow() - bot.start_time
    
    embed = discord.Embed(
        title="🤖 F.R.O.S.T AI Information",
        description=f"**{Config.COMPANY_NAME}**\n{Config.COMPANY_MOTTO}",
        color=0x00ff41
    )
    
    embed.add_field(
        name="📊 **Statistics**",
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
                   f"**Status:** {status}",
        color=0x00ff41
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

# Main entry point for Discord bot only

if __name__ == "__main__":
    asyncio.run(main())