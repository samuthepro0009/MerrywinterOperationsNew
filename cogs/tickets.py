"""
Ticket system for Merrywinter Security Consulting
Handles report-operator, commission, and tech-issue tickets
"""

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import uuid
import asyncio

from config.settings import Config
from utils.helpers import get_user_clearance, create_embed
from utils.storage import Storage

class TicketSystem(commands.Cog):
    """Ticket system for PMC operations"""
    
    def __init__(self, bot):
        self.bot = bot
        self.storage = Storage()
        self.active_tickets = {}
    
    def cog_check(self, ctx):
        """Check if command is used in authorized guild"""
        return Config.check_guild_authorization(ctx.guild.id)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check if interaction is in authorized guild"""
        return Config.check_guild_authorization(interaction.guild.id)
    
    async def create_ticket_channel(self, guild, ticket_type: str, user: discord.Member, ticket_id: str):
        """Create a private ticket channel"""
        try:
            # Find or create ticket category
            category = discord.utils.get(guild.categories, name=Config.TICKET_CATEGORY)
            if not category:
                category = await guild.create_category(Config.TICKET_CATEGORY)
            
            # Create channel
            channel_name = f"ticket-{ticket_type}-{ticket_id[:8]}"
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            
            # Add permissions for staff based on clearance
            for role in guild.roles:
                role_names = [r.lower() for r in (Config.OMEGA_ROLES + Config.BETA_ROLES + Config.ADMIN_ROLES + Config.MODERATOR_ROLES)]
                if role.name.lower() in role_names:
                    overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            
            channel = await guild.create_text_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites
            )
            
            return channel
            
        except Exception as e:
            print(f"Error creating ticket channel: {e}")
            return None
    
    @app_commands.command(name="report-operator", description="Report an operator for misconduct")
    @app_commands.describe(
        operator="The operator to report",
        reason="Reason for the report"
    )
    async def report_operator(self, interaction: discord.Interaction, operator: discord.Member = None, *, reason: str = None):
        """Report an operator for misconduct"""
        if not operator:
            await interaction.response.send_message("❌ Please specify an operator to report.", ephemeral=True)
            return
        
        if not reason:
            await interaction.response.send_message("❌ Please provide a reason for the report.", ephemeral=True)
            return
        
        # Generate ticket ID
        ticket_id = str(uuid.uuid4())
        
        # Create ticket data
        ticket_data = {
            'id': ticket_id,
            'type': 'report-operator',
            'reporter': interaction.user.id,
            'reported_user': operator.id,
            'reason': reason,
            'status': 'open',
            'created_at': datetime.utcnow().isoformat(),
            'guild_id': interaction.guild.id,
            'channel_id': None
        }
        
        # Create ticket channel
        channel = await self.create_ticket_channel(interaction.guild, 'report-operator', interaction.user, ticket_id)
        
        if channel:
            ticket_data['channel_id'] = channel.id
            
            # Create embed for ticket
            embed = discord.Embed(
                title="⚠️ Operator Report Filed",
                description=f"**Ticket ID:** `{ticket_id}`\n"
                           f"**Reporter:** {interaction.user.mention}\n"
                           f"**Reported Operator:** {operator.mention}\n"
                           f"**Reason:** {reason}\n\n"
                           "**Status:** Under Review\n"
                           "A staff member will review this report shortly.",
                color=Config.COLORS['warning']
            )
            embed.set_footer(text=f"{Config.COMPANY_NAME} - Internal Affairs")
            
            await channel.send(embed=embed)
            
            # Send confirmation to user
            await interaction.response.send_message(
                f"✅ Report submitted successfully! Ticket ID: `{ticket_id}`\n"
                f"Please check {channel.mention} for updates.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message("❌ Error creating ticket channel. Please contact an administrator.", ephemeral=True)
        
        # Save ticket data
        await self.storage.save_ticket(ticket_data)
    
    @app_commands.command(name="commission", description="Commission a PMC service")
    @app_commands.describe(
        service_details="Details about the service you wish to commission"
    )
    async def commission_service(self, interaction: discord.Interaction, *, service_details: str = None):
        """Commission a PMC service"""
        if not service_details:
            await interaction.response.send_message("❌ Please provide details about the service you wish to commission.", ephemeral=True)
            return
        
        # Generate ticket ID
        ticket_id = str(uuid.uuid4())
        
        # Create ticket data
        ticket_data = {
            'id': ticket_id,
            'type': 'commission',
            'client': interaction.user.id,
            'service_details': service_details,
            'status': 'open',
            'created_at': datetime.utcnow().isoformat(),
            'guild_id': interaction.guild.id,
            'channel_id': None
        }
        
        # Create ticket channel
        channel = await self.create_ticket_channel(interaction.guild, 'commission', interaction.user, ticket_id)
        
        if channel:
            ticket_data['channel_id'] = channel.id
            
            # Create embed for ticket
            embed = discord.Embed(
                title="💼 Service Commission Request",
                description=f"**Ticket ID:** `{ticket_id}`\n"
                           f"**Client:** {interaction.user.mention}\n"
                           f"**Service Details:** {service_details}\n\n"
                           "**Status:** Pending Review\n"
                           "Our operations team will contact you shortly to discuss requirements and pricing.",
                color=Config.COLORS['info']
            )
            embed.set_footer(text=f"{Config.COMPANY_NAME} - Business Development")
            
            await channel.send(embed=embed)
            
            # Send confirmation to user
            await interaction.response.send_message(
                f"✅ Commission request submitted! Ticket ID: `{ticket_id}`\n"
                f"Please check {channel.mention} for updates.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message("❌ Error creating ticket channel. Please contact an administrator.", ephemeral=True)
        
        # Save ticket data
        await self.storage.save_ticket(ticket_data)
    
    @app_commands.command(name="tech-issue", description="Report a technical issue or map bug")
    @app_commands.describe(
        issue_description="Description of the technical issue or bug"
    )
    async def tech_issue(self, interaction: discord.Interaction, *, issue_description: str = None):
        """Report a technical issue or map bug"""
        if not issue_description:
            await interaction.response.send_message("❌ Please provide a description of the technical issue.", ephemeral=True)
            return
        
        # Generate ticket ID
        ticket_id = str(uuid.uuid4())
        
        # Create ticket data
        ticket_data = {
            'id': ticket_id,
            'type': 'tech-issue',
            'reporter': interaction.user.id,
            'issue_description': issue_description,
            'status': 'open',
            'created_at': datetime.utcnow().isoformat(),
            'guild_id': interaction.guild.id,
            'channel_id': None
        }
        
        # Create ticket channel
        channel = await self.create_ticket_channel(interaction.guild, 'tech-issue', interaction.user, ticket_id)
        
        if channel:
            ticket_data['channel_id'] = channel.id
            
            # Create embed for ticket
            embed = discord.Embed(
                title="🔧 Technical Issue Report",
                description=f"**Ticket ID:** `{ticket_id}`\n"
                           f"**Reporter:** {interaction.user.mention}\n"
                           f"**Issue Description:** {issue_description}\n\n"
                           "**Status:** Under Investigation\n"
                           "Our technical team will investigate this issue and provide updates.",
                color=Config.COLORS['warning']
            )
            embed.set_footer(text=f"{Config.COMPANY_NAME} - Technical Support")
            
            await channel.send(embed=embed)
            
            # Send confirmation to user
            await interaction.response.send_message(
                f"✅ Technical issue reported! Ticket ID: `{ticket_id}`\n"
                f"Please check {channel.mention} for updates.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message("❌ Error creating ticket channel. Please contact an administrator.", ephemeral=True)
        
        # Save ticket data
        await self.storage.save_ticket(ticket_data)
    
    @app_commands.command(name="ticket-status", description="Check the status of a ticket")
    @app_commands.describe(
        ticket_id="The ID of the ticket to check"
    )
    async def ticket_status(self, interaction: discord.Interaction, ticket_id: str = None):
        """Check the status of a ticket"""
        if not ticket_id:
            await interaction.response.send_message("❌ Please provide a ticket ID.", ephemeral=True)
            return
        
        # Get ticket data
        ticket_data = await self.storage.get_ticket(ticket_id)
        
        if not ticket_data:
            await interaction.response.send_message("❌ Ticket not found.", ephemeral=True)
            return
        
        # Create status embed
        embed = discord.Embed(
            title=f"🎫 Ticket Status - {ticket_id}",
            description=f"**Type:** {ticket_data['type'].replace('-', ' ').title()}\n"
                       f"**Status:** {ticket_data['status'].title()}\n"
                       f"**Created:** {ticket_data['created_at']}\n"
                       f"**Reporter:** <@{ticket_data.get('reporter', ticket_data.get('client', 'Unknown'))}>",
            color=Config.COLORS['info']
        )
        embed.set_footer(text=f"{Config.COMPANY_NAME} - Ticket System")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="close-ticket", description="Close a ticket (Staff only)")
    @app_commands.describe(
        ticket_id="The ID of the ticket to close"
    )
    async def close_ticket(self, interaction: discord.Interaction, ticket_id: str = None):
        """Close a ticket (Staff only)"""
        # Check if user has permission
        user_clearance = get_user_clearance(interaction.user.roles)
        if not (Config.is_moderator([role.name for role in interaction.user.roles], interaction.user.id) or 
                Config.has_permission(user_clearance, 'BETA')):
            await interaction.response.send_message("❌ You don't have permission to close tickets.", ephemeral=True)
            return
        
        if not ticket_id:
            await interaction.response.send_message("❌ Please provide a ticket ID.", ephemeral=True)
            return
        
        # Get ticket data
        ticket_data = await self.storage.get_ticket(ticket_id)
        
        if not ticket_data:
            await interaction.response.send_message("❌ Ticket not found.", ephemeral=True)
            return
        
        # Update ticket status
        ticket_data['status'] = 'closed'
        ticket_data['closed_by'] = interaction.user.id
        ticket_data['closed_at'] = datetime.utcnow().isoformat()
        
        await self.storage.save_ticket(ticket_data)
        
        # Send closure message to ticket channel
        if ticket_data.get('channel_id'):
            channel = interaction.guild.get_channel(ticket_data['channel_id'])
            if channel:
                embed = discord.Embed(
                    title="🔒 Ticket Closed",
                    description=f"**Ticket ID:** `{ticket_id}`\n"
                               f"**Closed By:** {interaction.user.mention}\n"
                               f"**Closed At:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n"
                               "This ticket has been resolved. The channel will be deleted in 5 minutes.",
                    color=Config.COLORS['success']
                )
                embed.set_footer(text=f"{Config.COMPANY_NAME} - Ticket System")
                
                await channel.send(embed=embed)
                
                # Delete channel after 5 minutes
                await asyncio.sleep(300)
                try:
                    await channel.delete()
                except:
                    pass
        
        await interaction.response.send_message(f"✅ Ticket {ticket_id} has been closed successfully.", ephemeral=True)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(TicketSystem(bot))