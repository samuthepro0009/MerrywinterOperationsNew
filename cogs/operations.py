"""
PMC Operations management for Merrywinter Security Consulting
Handles missions, deployments, and operational status - SLASH COMMANDS ONLY
"""

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import random

from config.settings import Config
from utils.helpers import get_user_clearance, create_embed
from utils.storage import Storage

class PMCOperations(commands.Cog):
    """PMC Operations management system"""
    
    def __init__(self, bot):
        self.bot = bot
        self.storage = Storage()
    
    @app_commands.command(name="mission", description="Get mission briefing")
    @app_commands.describe(
        mission_type="Type of mission to request",
        classified="Make this a classified mission (requires BETA+ clearance)"
    )
    @app_commands.choices(mission_type=[
        app_commands.Choice(name="Reconnaissance", value="reconnaissance"),
        app_commands.Choice(name="Security Detail", value="security-detail"),
        app_commands.Choice(name="Convoy Escort", value="convoy-escort"),
        app_commands.Choice(name="Base Defense", value="base-defense"),
        app_commands.Choice(name="Direct Action", value="direct-action"),
        app_commands.Choice(name="Intelligence Gathering", value="intelligence-gathering")
    ])
    async def mission_briefing(self, interaction: discord.Interaction, mission_type: str, classified: bool = False):
        """Get mission briefing"""
        user_clearance = get_user_clearance(interaction.user.roles)
        
        if user_clearance == 'CIVILIAN':
            await interaction.response.send_message("❌ You need military clearance to access mission briefings.", ephemeral=True)
            return
        
        # Check if classified mission requires higher clearance
        if classified and not Config.has_permission(user_clearance, 'BETA'):
            await interaction.response.send_message("❌ You need BETA+ clearance to access classified missions.", ephemeral=True)
            return
        
        # Generate mission details
        mission_name = mission_type.replace('-', ' ').title()
        sector = random.choice(Config.OPERATION_SECTORS)
        mission_id = f"MSC-{random.randint(1000, 9999)}"
        objectives = self.generate_mission_objectives(mission_name)
        
        # Handle classified missions
        if classified:
            title = f"🎯 [CLASSIFIED] MISSION BRIEFING - {mission_name.upper()}"
            operator_info = f"**Operator:** authorized by: **[RESTRICTED]**"
            classification_note = f"\n🔒 **CLASSIFIED MISSION**\n*Access restricted to BETA+ clearance only*"
        else:
            title = f"🎯 MISSION BRIEFING - {mission_name.upper()}"
            operator_info = f"**Operator:** {interaction.user.mention}"
            classification_note = ""
        
        embed = discord.Embed(
            title=title,
            description=f"**Mission ID:** {mission_id}\n"
                       f"{operator_info}\n"
                       f"**Clearance Level:** {user_clearance}\n"
                       f"**Deployment Sector:** {sector}"
                       f"{classification_note}",
            color=Config.COLORS['info']
        )
        
        embed.add_field(
            name="📋 Mission Objectives",
            value=objectives,
            inline=False
        )
        
        embed.add_field(
            name="⚠️ Rules of Engagement",
            value="• Maintain operational security\n"
                  "• Follow chain of command\n"
                  "• Report status regularly\n"
                  "• Minimize civilian casualties\n"
                  "• Extraction on command",
            inline=False
        )
        
        embed.add_field(
            name="📡 Communication",
            value=f"• Primary Channel: Command\n"
                  f"• Backup Channel: Emergency\n"
                  f"• Call Sign: {interaction.user.display_name[:3].upper()}-{random.randint(10, 99)}",
            inline=False
        )
        
        embed.set_footer(text="Merrywinter Security Consulting - Mission Command")
        
        await interaction.response.send_message(embed=embed)
        
        # Save mission data
        mission_data = {
            'mission_id': mission_id,
            'operator_id': interaction.user.id,
            'mission_type': mission_name,
            'sector': sector,
            'objectives': objectives,
            'classified': classified,
            'status': 'briefed',
            'created_at': datetime.utcnow().isoformat(),
            'guild_id': interaction.guild.id
        }
        
        # Save to storage
        missions = self.storage.load_data('missions.json')
        missions[mission_id] = mission_data
        self.storage.save_data('missions.json', missions)
    
    def generate_mission_objectives(self, mission_type):
        """Generate mission objectives based on type"""
        objectives_map = {
            'Reconnaissance': [
                "• Conduct surveillance of target area",
                "• Identify enemy positions and movements",
                "• Gather intelligence on local conditions",
                "• Report findings to command"
            ],
            'Security Detail': [
                "• Protect assigned VIP or asset",
                "• Maintain security perimeter",
                "• Coordinate with local security forces",
                "• Respond to security threats"
            ],
            'Convoy Escort': [
                "• Provide security for supply convoy",
                "• Maintain formation and communication",
                "• Respond to ambush or attack",
                "• Ensure safe delivery of cargo"
            ],
            'Base Defense': [
                "• Secure defensive positions",
                "• Monitor perimeter sensors",
                "• Coordinate with other units",
                "• Repel enemy attacks"
            ],
            'Direct Action': [
                "• Neutralize specified targets",
                "• Secure designated objectives",
                "• Minimize collateral damage",
                "• Extract upon mission completion"
            ],
            'Intelligence Gathering': [
                "• Collect actionable intelligence",
                "• Establish surveillance network",
                "• Document enemy activities",
                "• Transmit findings to command"
            ]
        }
        
        return '\n'.join(objectives_map.get(mission_type, [
            "• Complete assigned objectives",
            "• Maintain operational security",
            "• Report status to command",
            "• Return to base safely"
        ]))
    
    @app_commands.command(name="operation-status", description="Check current operational status")
    async def operation_status(self, interaction: discord.Interaction):
        """Check current operational status"""
        user_clearance = get_user_clearance(interaction.user.roles)
        
        if user_clearance == 'CIVILIAN':
            await interaction.response.send_message("❌ You need military clearance to access operational status.", ephemeral=True)
            return
        
        # Load operations data
        operations = self.storage.load_data('operations.json')
        
        active_ops = []
        completed_ops = []
        
        for op_id, op_data in operations.items():
            if op_data.get('status') == 'active':
                active_ops.append(op_data)
            elif op_data.get('status') == 'completed':
                completed_ops.append(op_data)
        
        embed = discord.Embed(
            title="📊 Operational Status Report",
            description=f"**Current Operations Status**\n"
                       f"**Requesting Officer:** {interaction.user.mention}\n"
                       f"**Clearance Level:** {user_clearance}",
            color=Config.COLORS['info']
        )
        
        if active_ops:
            active_list = []
            for op in active_ops[:5]:  # Show max 5 active ops
                active_list.append(f"• **{op.get('operation_id', 'N/A')}** - {op.get('operation_name', 'Unknown')}")
            
            embed.add_field(
                name="🔥 Active Operations",
                value='\n'.join(active_list),
                inline=False
            )
        else:
            embed.add_field(
                name="🔥 Active Operations",
                value="No active operations",
                inline=False
            )
        
        embed.add_field(
            name="📈 Statistics",
            value=f"**Active Operations:** {len(active_ops)}\n"
                  f"**Completed Operations:** {len(completed_ops)}\n"
                  f"**Total Operations:** {len(operations)}",
            inline=False
        )
        
        embed.set_footer(text="Merrywinter Security Consulting - Operations Command")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="deploy", description="Deploy to operational sectors")
    @app_commands.describe(
        sector="Deployment sector",
        duration="Deployment duration in hours"
    )
    @app_commands.choices(sector=[
        app_commands.Choice(name="Sector Alpha - Urban Operations", value="alpha"),
        app_commands.Choice(name="Sector Beta - Desert Warfare", value="beta"),
        app_commands.Choice(name="Sector Gamma - Naval Operations", value="gamma"),
        app_commands.Choice(name="Sector Delta - Mountain Warfare", value="delta")
    ])
    async def deploy_operator(self, interaction: discord.Interaction, sector: str, duration: int = 8):
        """Deploy to operational sectors"""
        user_clearance = get_user_clearance(interaction.user.roles)
        
        if user_clearance == 'CIVILIAN':
            await interaction.response.send_message("❌ You need military clearance to deploy.", ephemeral=True)
            return
        
        if duration < 1 or duration > 24:
            await interaction.response.send_message("❌ Deployment duration must be between 1 and 24 hours.", ephemeral=True)
            return
        
        sector_names = {
            'alpha': 'Alpha - Urban Operations',
            'beta': 'Beta - Desert Warfare',
            'gamma': 'Gamma - Naval Operations',
            'delta': 'Delta - Mountain Warfare'
        }
        
        deployment_id = f"DEP-{random.randint(1000, 9999)}"
        
        embed = discord.Embed(
            title="🚁 Deployment Authorized",
            description=f"**Deployment ID:** {deployment_id}\n"
                       f"**Operator:** {interaction.user.mention}\n"
                       f"**Clearance Level:** {user_clearance}\n"
                       f"**Deployment Sector:** {sector_names.get(sector, sector)}\n"
                       f"**Duration:** {duration} hours",
            color=Config.COLORS['success']
        )
        
        embed.add_field(
            name="📋 Deployment Orders",
            value=f"• Report to sector commander upon arrival\n"
                  f"• Maintain communication protocols\n"
                  f"• Follow all ROE guidelines\n"
                  f"• Expected return: <t:{int((datetime.utcnow() + timedelta(hours=duration)).timestamp())}:R>",
            inline=False
        )
        
        embed.set_footer(text="Merrywinter Security Consulting - Deployment Command")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(PMCOperations(bot))