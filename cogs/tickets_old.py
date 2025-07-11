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
                if role.name.lower() in [r.lower() for r in Config.OMEGA_ROLES + Config.BETA_ROLES + Config.ADMIN_ROLES]:
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
    
    @commands.command(name='report-operator')
    async def report_operator(self, ctx, operator: discord.Member = None, *, reason: str = None):
        """Report an operator for misconduct"""
        if not operator:
            await ctx.send("❌ Please specify an operator to report.")
            return
        
        if not reason:
            await ctx.send("❌ Please provide a reason for the report.")
            return
        
        # Generate ticket ID
        ticket_id = str(uuid.uuid4())
        
        # Create ticket data
        ticket_data = {
            'id': ticket_id,
            'type': 'report-operator',
            'reporter': ctx.author.id,
            'reported_user': operator.id,
            'reason': reason,
            'status': 'open',
            'created_at': datetime.utcnow().isoformat(),
            'guild_id': ctx.guild.id,
            'channel_id': None
        }
        
        # Create ticket channel
        channel = await self.create_ticket_channel(ctx.guild, 'report-operator', ctx.author, ticket_id)
        
        if channel:
            ticket_data['channel_id'] = channel.id
            
            # Create embed for ticket
            embed = discord.Embed(
                title="⚠️ Operator Report Filed",
                description=f"**Ticket ID:** `{ticket_id}`\n"
                           f"**Reporter:** {ctx.author.mention}\n"
                           f"**Reported Operator:** {operator.mention}\n"
                           f"**Reason:** {reason}\n\n"
                           "**Status:** Under Review\n"
                           "A staff member will review this report shortly.",
                color=Config.COLORS['warning']
            )
            embed.set_footer(text="Merrywinter Security Consulting - Internal Affairs")
            
            await channel.send(embed=embed)
            
            # Send confirmation to user
            confirm_embed = discord.Embed(
                title="✅ Report Submitted",
                description=f"Your report has been submitted and assigned ticket ID: `{ticket_id}`\n"
                           f"Please check {channel.mention} for updates.",
                color=Config.COLORS['success']
            )
            await ctx.send(embed=confirm_embed)
        
        # Save ticket data
        await self.storage.save_ticket(ticket_data)
    
    @commands.command(name='commission')
    async def commission_service(self, ctx, *, service_details: str = None):
        """Commission a PMC service"""
        if not service_details:
            await ctx.send("❌ Please provide details about the service you wish to commission.")
            return
        
        # Generate ticket ID
        ticket_id = str(uuid.uuid4())
        
        # Create ticket data
        ticket_data = {
            'id': ticket_id,
            'type': 'commission',
            'client': ctx.author.id,
            'service_details': service_details,
            'status': 'open',
            'created_at': datetime.utcnow().isoformat(),
            'guild_id': ctx.guild.id,
            'channel_id': None
        }
        
        # Create ticket channel
        channel = await self.create_ticket_channel(ctx.guild, 'commission', ctx.author, ticket_id)
        
        if channel:
            ticket_data['channel_id'] = channel.id
            
            # Create embed for ticket
            embed = discord.Embed(
                title="💼 Service Commission Request",
                description=f"**Ticket ID:** `{ticket_id}`\n"
                           f"**Client:** {ctx.author.mention}\n"
                           f"**Service Details:** {service_details}\n\n"
                           "**Status:** Pending Review\n"
                           "Our operations team will review your request and provide a quote.",
                color=Config.COLORS['info']
            )
            embed.add_field(
                name="🎯 Available Services",
                value="• Security Details\n• Convoy Escorts\n• Base Defense\n• Training Operations\n• Intelligence Gathering\n• Special Operations",
                inline=False
            )
            embed.set_footer(text="Merrywinter Security Consulting - Contract Operations")
            
            await channel.send(embed=embed)
            
            # Send confirmation to user
            confirm_embed = discord.Embed(
                title="✅ Commission Request Submitted",
                description=f"Your service request has been submitted with ticket ID: `{ticket_id}`\n"
                           f"Please check {channel.mention} for updates and quotes.",
                color=Config.COLORS['success']
            )
            await ctx.send(embed=confirm_embed)
        
        # Save ticket data
        await self.storage.save_ticket(ticket_data)
    
    @commands.command(name='tech-issue')
    async def tech_issue(self, ctx, *, issue_description: str = None):
        """Report a technical issue or map bug"""
        if not issue_description:
            await ctx.send("❌ Please provide a description of the technical issue.")
            return
        
        # Generate ticket ID
        ticket_id = str(uuid.uuid4())
        
        # Create ticket data
        ticket_data = {
            'id': ticket_id,
            'type': 'tech-issue',
            'reporter': ctx.author.id,
            'issue_description': issue_description,
            'status': 'open',
            'created_at': datetime.utcnow().isoformat(),
            'guild_id': ctx.guild.id,
            'channel_id': None
        }
        
        # Create ticket channel
        channel = await self.create_ticket_channel(ctx.guild, 'tech-issue', ctx.author, ticket_id)
        
        if channel:
            ticket_data['channel_id'] = channel.id
            
            # Create embed for ticket
            embed = discord.Embed(
                title="🔧 Technical Issue Report",
                description=f"**Ticket ID:** `{ticket_id}`\n"
                           f"**Reporter:** {ctx.author.mention}\n"
                           f"**Issue Description:** {issue_description}\n\n"
                           "**Status:** Under Investigation\n"
                           "Our technical team will investigate this issue.",
                color=Config.COLORS['warning']
            )
            embed.add_field(
                name="📋 Common Issues",
                value="• Map Bugs\n• Script Errors\n• Performance Issues\n• Asset Problems\n• Gameplay Mechanics\n• UI/UX Issues",
                inline=False
            )
            embed.set_footer(text="Merrywinter Security Consulting - Technical Support")
            
            await channel.send(embed=embed)
            
            # Send confirmation to user
            confirm_embed = discord.Embed(
                title="✅ Technical Issue Reported",
                description=f"Your technical issue has been reported with ticket ID: `{ticket_id}`\n"
                           f"Please check {channel.mention} for updates.",
                color=Config.COLORS['success']
            )
            await ctx.send(embed=confirm_embed)
        
        # Save ticket data
        await self.storage.save_ticket(ticket_data)
    
    @commands.command(name='ticket-status')
    async def ticket_status(self, ctx, ticket_id: str = None):
        """Check the status of a ticket"""
        if not ticket_id:
            # Show user's tickets
            tickets = await self.storage.get_user_tickets(ctx.author.id)
            
            if not tickets:
                await ctx.send("❌ You have no tickets.")
                return
            
            embed = discord.Embed(
                title="🎫 Your Tickets",
                description="Here are your active tickets:",
                color=Config.COLORS['info']
            )
            
            for ticket in tickets[:10]:  # Show max 10 tickets
                status_emoji = "🟢" if ticket['status'] == 'open' else "🔴" if ticket['status'] == 'closed' else "🟡"
                embed.add_field(
                    name=f"{status_emoji} {ticket['type'].title()} - {ticket['id'][:8]}",
                    value=f"Status: {ticket['status'].title()}\nCreated: {ticket['created_at'][:10]}",
                    inline=True
                )
            
            await ctx.send(embed=embed)
        else:
            # Show specific ticket
            ticket = await self.storage.get_ticket(ticket_id)
            
            if not ticket:
                await ctx.send("❌ Ticket not found.")
                return
            
            # Check if user has permission to view this ticket
            user_clearance = get_user_clearance(ctx.author.roles)
            if (ticket.get('reporter') != ctx.author.id and 
                ticket.get('client') != ctx.author.id and
                not Config.has_permission(user_clearance, 'BETA')):
                await ctx.send("❌ You don't have permission to view this ticket.")
                return
            
            embed = discord.Embed(
                title=f"🎫 Ticket Status - {ticket['id'][:8]}",
                description=f"**Type:** {ticket['type'].title()}\n"
                           f"**Status:** {ticket['status'].title()}\n"
                           f"**Created:** {ticket['created_at'][:10]}",
                color=Config.COLORS['info']
            )
            
            if ticket['type'] == 'report-operator':
                embed.add_field(name="Reporter", value=f"<@{ticket['reporter']}>", inline=True)
                embed.add_field(name="Reported User", value=f"<@{ticket['reported_user']}>", inline=True)
                embed.add_field(name="Reason", value=ticket['reason'], inline=False)
            elif ticket['type'] == 'commission':
                embed.add_field(name="Client", value=f"<@{ticket['client']}>", inline=True)
                embed.add_field(name="Service Details", value=ticket['service_details'], inline=False)
            elif ticket['type'] == 'tech-issue':
                embed.add_field(name="Reporter", value=f"<@{ticket['reporter']}>", inline=True)
                embed.add_field(name="Issue Description", value=ticket['issue_description'], inline=False)
            
            await ctx.send(embed=embed)
    
    @commands.command(name='close-ticket')
    @commands.has_permissions(manage_channels=True)
    async def close_ticket(self, ctx, ticket_id: str = None):
        """Close a ticket (Staff only)"""
        if not ticket_id:
            await ctx.send("❌ Please provide a ticket ID to close.")
            return
        
        ticket = await self.storage.get_ticket(ticket_id)
        
        if not ticket:
            await ctx.send("❌ Ticket not found.")
            return
        
        # Update ticket status
        ticket['status'] = 'closed'
        ticket['closed_at'] = datetime.utcnow().isoformat()
        ticket['closed_by'] = ctx.author.id
        
        await self.storage.save_ticket(ticket)
        
        # Close channel if it exists
        if ticket.get('channel_id'):
            channel = self.bot.get_channel(ticket['channel_id'])
            if channel:
                embed = discord.Embed(
                    title="🔒 Ticket Closed",
                    description=f"This ticket has been closed by {ctx.author.mention}.\n"
                               "This channel will be deleted in 30 seconds.",
                    color=Config.COLORS['error']
                )
                await channel.send(embed=embed)
                
                # Delete channel after 30 seconds
                await asyncio.sleep(30)
                await channel.delete()
        
        await ctx.send(f"✅ Ticket `{ticket_id}` has been closed.")

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(TicketSystem(bot))
