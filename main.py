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
from flask import Flask

from config.settings import Config
from utils.logger import setup_logger
from utils.storage import Storage

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger()

# Create Flask app instance for the web dashboard
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "frost-ai-secret-key")

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
                'cogs.communications'
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

# Export the Flask app for gunicorn
from app import app

if __name__ == "__main__":
    asyncio.run(main())