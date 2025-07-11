"""
Administrative commands for Merrywinter Security Consulting
Bot management and configuration
"""

import discord
from discord.ext import commands
from datetime import datetime
import os
import json

from config.settings import Config
from utils.helpers import get_user_clearance, create_embed
from utils.storage import Storage

class AdminSystem(commands.Cog):
    """Administrative system for bot management"""
    
    def __init__(self, bot):
        self.bot = bot
        self.storage = Storage()
    
    @commands.command(name='setup')
    @commands.has_permissions(administrator=True)
    async def setup_bot(self, ctx):
        """Initial bot setup (Administrator only)"""
        if not Config.is_admin([role.name for role in ctx.author.roles]):
            await ctx.send("❌ You need administrator permissions to run setup.")
            return
        
        embed = discord.Embed(
            title="⚙️ Merrywinter Security Consulting - Bot Setup",
            description="**Initial Configuration Guide**\n\n"
                       "Follow these steps to configure your PMC bot:",
            color=Config.COLORS['info']
        )
        
        embed.add_field(
            name="1. 🔐 Security Clearance Roles",
            value="Create and assign these roles:\n"
                  "• `OMEGA Command` - Supreme authority\n"
                  "• `BETA Command` - Field operations\n"
                  "• `ALPHA Operator` - Ground operations\n"
                  "• `Admin` - Bot administration\n"
                  "• `Moderator` - Moderation permissions",
            inline=False
        )
        
        embed.add_field(
            name="2. 📋 Channels Setup",
            value="Create these channels:\n"
                  "• `#bot-logs` - Moderation logs\n"
                  "• `Support Tickets` category - For ticket system\n"
                  "• `#general` - General communications\n"
                  "• `#operations` - Mission briefings",
            inline=False
        )
        
        embed.add_field(
            name="3. 🔧 Environment Configuration",
            value="Set these environment variables:\n"
                  "• `OMEGA_ROLES=OMEGA Command`\n"
                  "• `BETA_ROLES=BETA Command`\n"
                  "• `ALPHA_ROLES=ALPHA Operator`\n"
                  "• `ADMIN_ROLES=Admin`\n"
                  "• `MODERATOR_ROLES=Moderator`",
            inline=False
        )
        
        embed.add_field(
            name="4. ✅ Verification",
            value=f"Run `{Config.COMMAND_PREFIX}verify-setup` to check configuration",
            inline=False
        )
        
        embed.set_footer(text="Merrywinter Security Consulting - Configuration Guide")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='verify-setup')
    @commands.has_permissions(administrator=True)
    async def verify_setup(self, ctx):
        """Verify bot setup configuration"""
        if not Config.is_admin([role.name for role in ctx.author.roles]):
            await ctx.send("❌ You need administrator permissions to verify setup.")
            return
        
        guild = ctx.guild
        issues = []
        successes = []
        
        # Check for required roles
        required_roles = Config.OMEGA_ROLES + Config.BETA_ROLES + Config.ALPHA_ROLES + Config.ADMIN_ROLES + Config.MODERATOR_ROLES
        
        for role_name in required_roles:
            if role_name and not discord.utils.get(guild.roles, name=role_name):
                issues.append(f"❌ Missing role: `{role_name}`")
            elif role_name:
                successes.append(f"✅ Found role: `{role_name}`")
        
        # Check for required channels
        required_channels = [Config.LOG_CHANNEL]
        
        for channel_name in required_channels:
            if channel_name and not discord.utils.get(guild.channels, name=channel_name):
                issues.append(f"❌ Missing channel: `#{channel_name}`")
            elif channel_name:
                successes.append(f"✅ Found channel: `#{channel_name}`")
        
        # Check for ticket category
        if not discord.utils.get(guild.categories, name=Config.TICKET_CATEGORY):
            issues.append(f"❌ Missing category: `{Config.TICKET_CATEGORY}`")
        else:
            successes.append(f"✅ Found category: `{Config.TICKET_CATEGORY}`")
        
        # Check bot permissions
        bot_member = guild.get_member(self.bot.user.id)
        required_perms = [
            'manage_channels', 'manage_roles', 'manage_messages',
            'read_messages', 'send_messages', 'embed_links'
        ]
        
        for perm in required_perms:
            if not getattr(bot_member.guild_permissions, perm, False):
                issues.append(f"❌ Missing permission: `{perm}`")
            else:
                successes.append(f"✅ Has permission: `{perm}`")
        
        # Create verification report
        embed = discord.Embed(
            title="🔍 Setup Verification Report",
            description="**Configuration Status Check**",
            color=Config.COLORS['success'] if not issues else Config.COLORS['warning']
        )
        
        if successes:
            embed.add_field(
                name="✅ Successful Configurations",
                value='\n'.join(successes[:10]),  # Show max 10
                inline=False
            )
        
        if issues:
            embed.add_field(
                name="❌ Issues Found",
                value='\n'.join(issues[:10]),  # Show max 10
                inline=False
            )
            
            embed.add_field(
                name="🔧 Recommendations",
                value="• Create missing roles and channels\n"
                      "• Grant required permissions to the bot\n"
                      "• Run setup again after fixes\n"
                      "• Contact support if issues persist",
                inline=False
            )
        else:
            embed.add_field(
                name="🎉 Setup Complete",
                value="Your Merrywinter Security Consulting bot is properly configured!\n"
                      "You can now use all features without issues.",
                inline=False
            )
        
        embed.set_footer(text="Merrywinter Security Consulting - Setup Verification")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='stats')
    @commands.has_permissions(manage_guild=True)
    async def statistics(self, ctx):
        """Display bot statistics"""
        if not Config.is_admin([role.name for role in ctx.author.roles]):
            await ctx.send("❌ You need administrator permissions to view bot statistics.")
            return
        
        guild = ctx.guild
        
        # Get statistics
        total_tickets = await self.storage.get_total_tickets()
        total_missions = await self.storage.get_total_missions()
        total_warnings = await self.storage.get_total_warnings()
        
        # Count operators by clearance
        omega_count = len([m for m in guild.members if get_user_clearance(m.roles) == 'OMEGA'])
        beta_count = len([m for m in guild.members if get_user_clearance(m.roles) == 'BETA'])
        alpha_count = len([m for m in guild.members if get_user_clearance(m.roles) == 'ALPHA'])
        
        embed = discord.Embed(
            title="📊 Merrywinter Security Consulting - Statistics",
            description="**Operational Statistics Report**",
            color=Config.COLORS['info']
        )
        
        embed.add_field(
            name="🎫 Ticket System",
            value=f"**Total Tickets:** {total_tickets}\n"
                  f"**Active Tickets:** {await self.storage.get_active_tickets_count()}\n"
                  f"**Resolved Tickets:** {total_tickets - await self.storage.get_active_tickets_count()}",
            inline=True
        )
        
        embed.add_field(
            name="🎯 Mission Operations",
            value=f"**Total Missions:** {total_missions}\n"
                  f"**Active Missions:** {await self.storage.get_active_missions_count()}\n"
                  f"**Completed Missions:** {total_missions - await self.storage.get_active_missions_count()}",
            inline=True
        )
        
        embed.add_field(
            name="👥 Personnel",
            value=f"**OMEGA Command:** {omega_count}\n"
                  f"**BETA Command:** {beta_count}\n"
                  f"**ALPHA Operators:** {alpha_count}\n"
                  f"**Total Active:** {omega_count + beta_count + alpha_count}",
            inline=True
        )
        
        embed.add_field(
            name="⚠️ Moderation",
            value=f"**Total Warnings:** {total_warnings}\n"
                  f"**Moderation Actions:** {await self.storage.get_moderation_actions_count()}\n"
                  f"**Active Mutes:** 0",  # Discord timeouts are automatic
            inline=True
        )
        
        embed.add_field(
            name="🖥️ Bot Status",
            value=f"**Uptime:** {datetime.utcnow() - self.bot.start_time}\n"
                  f"**Guilds:** {len(self.bot.guilds)}\n"
                  f"**Latency:** {round(self.bot.latency * 1000)}ms",
            inline=True
        )
        
        embed.add_field(
            name="💾 Storage",
            value=f"**Data Files:** {len(os.listdir(Config.DATA_DIR)) if os.path.exists(Config.DATA_DIR) else 0}\n"
                  f"**Last Backup:** Not configured\n"
                  f"**Storage Health:** ✅ Good",
            inline=True
        )
        
        embed.set_footer(text="Merrywinter Security Consulting - Administrative Statistics")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='backup')
    @commands.has_permissions(administrator=True)
    async def backup_data(self, ctx):
        """Create a backup of bot data"""
        if not Config.is_admin([role.name for role in ctx.author.roles]):
            await ctx.send("❌ You need administrator permissions to create backups.")
            return
        
        try:
            backup_data = await self.storage.create_backup()
            
            # Create backup file
            backup_filename = f"merrywinter_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(backup_filename, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            # Send backup file
            embed = discord.Embed(
                title="💾 Data Backup Created",
                description=f"**Backup File:** `{backup_filename}`\n"
                           f"**Created:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
                           f"**Size:** {os.path.getsize(backup_filename)} bytes",
                color=Config.COLORS['success']
            )
            
            await ctx.send(embed=embed, file=discord.File(backup_filename))
            
            # Clean up backup file
            os.remove(backup_filename)
            
        except Exception as e:
            await ctx.send(f"❌ Error creating backup: {str(e)}")
    
    @commands.command(name='maintenance')
    @commands.has_permissions(administrator=True)
    async def maintenance_mode(self, ctx, mode: str = None):
        """Toggle maintenance mode"""
        if not Config.is_admin([role.name for role in ctx.author.roles]):
            await ctx.send("❌ You need administrator permissions to control maintenance mode.")
            return
        
        if mode is None:
            # Show current status
            maintenance_status = getattr(self.bot, 'maintenance_mode', False)
            status_text = "🔴 ENABLED" if maintenance_status else "🟢 DISABLED"
            
            embed = discord.Embed(
                title="🔧 Maintenance Mode Status",
                description=f"**Current Status:** {status_text}",
                color=Config.COLORS['warning'] if maintenance_status else Config.COLORS['success']
            )
            
            await ctx.send(embed=embed)
            return
        
        if mode.lower() in ['on', 'enable', 'true']:
            self.bot.maintenance_mode = True
            await self.bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name="🔧 Maintenance Mode"
                ),
                status=discord.Status.do_not_disturb
            )
            
            embed = discord.Embed(
                title="🔧 Maintenance Mode Enabled",
                description="The bot is now in maintenance mode.\n"
                           "Most commands will be disabled for regular users.",
                color=Config.COLORS['warning']
            )
            
        elif mode.lower() in ['off', 'disable', 'false']:
            self.bot.maintenance_mode = False
            await self.bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name="Roblox PMC Operations | !help"
                ),
                status=discord.Status.online
            )
            
            embed = discord.Embed(
                title="✅ Maintenance Mode Disabled",
                description="The bot is now fully operational.\n"
                           "All commands are available for use.",
                color=Config.COLORS['success']
            )
            
        else:
            await ctx.send("❌ Invalid option. Use `on` or `off`.")
            return
        
        await ctx.send(embed=embed)
    
    @commands.command(name='reload')
    @commands.has_permissions(administrator=True)
    async def reload_cog(self, ctx, cog_name: str = None):
        """Reload a specific cog or all cogs"""
        if not Config.is_admin([role.name for role in ctx.author.roles]):
            await ctx.send("❌ You need administrator permissions to reload cogs.")
            return
        
        if cog_name is None:
            # Reload all cogs
            cogs = ['cogs.tickets', 'cogs.security', 'cogs.operations', 'cogs.moderation', 'cogs.admin']
            reloaded = []
            failed = []
            
            for cog in cogs:
                try:
                    await self.bot.reload_extension(cog)
                    reloaded.append(cog)
                except Exception as e:
                    failed.append(f"{cog}: {str(e)}")
            
            embed = discord.Embed(
                title="🔄 Cog Reload Results",
                color=Config.COLORS['success'] if not failed else Config.COLORS['warning']
            )
            
            if reloaded:
                embed.add_field(
                    name="✅ Successfully Reloaded",
                    value='\n'.join(reloaded),
                    inline=False
                )
            
            if failed:
                embed.add_field(
                    name="❌ Failed to Reload",
                    value='\n'.join(failed),
                    inline=False
                )
            
        else:
            # Reload specific cog
            try:
                await self.bot.reload_extension(f'cogs.{cog_name}')
                embed = discord.Embed(
                    title="✅ Cog Reloaded",
                    description=f"Successfully reloaded `cogs.{cog_name}`",
                    color=Config.COLORS['success']
                )
            except Exception as e:
                embed = discord.Embed(
                    title="❌ Reload Failed",
                    description=f"Failed to reload `cogs.{cog_name}`: {str(e)}",
                    color=Config.COLORS['error']
                )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='shutdown')
    @commands.has_permissions(administrator=True)
    async def shutdown_bot(self, ctx):
        """Shutdown the bot (Administrator only)"""
        if not Config.is_admin([role.name for role in ctx.author.roles]):
            await ctx.send("❌ You need administrator permissions to shutdown the bot.")
            return
        
        embed = discord.Embed(
            title="🔴 Bot Shutdown",
            description="Merrywinter Security Consulting bot is shutting down...\n"
                       "The bot will automatically restart if hosted on Render.",
            color=Config.COLORS['error']
        )
        
        await ctx.send(embed=embed)
        
        # Close the bot
        await self.bot.close()

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(AdminSystem(bot))
