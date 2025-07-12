"""
Security clearance management for Merrywinter Security Consulting
Handles Omega, Beta, and Alpha clearance levels - SLASH COMMANDS ONLY
"""

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

from config.settings import Config
from utils.helpers import get_user_clearance, create_embed
from utils.storage import Storage

class SecurityClearance(commands.Cog):
    """Security clearance management system"""
    
    def __init__(self, bot):
        self.bot = bot
        self.storage = Storage()
    
    @app_commands.command(name="clearance", description="Check security clearance level")
    @app_commands.describe(user="User to check clearance for (optional)")
    async def check_clearance(self, interaction: discord.Interaction, user: discord.Member = None):
        """Check security clearance level"""
        target_user = user or interaction.user
        
        # Get clearance level from real guild roles
        role_names = [role.name for role in target_user.roles]
        clearance_level = Config.get_security_level(role_names)
        
        # Get detailed clearance information
        clearance_info = {
            'BOARD_OF_DIRECTORS': {
                'title': 'Board of Directors',
                'description': 'Highest level oversight and strategic direction',
                'permissions': ['All Operations Authorized', 'Strategic Planning', 'Executive Decisions']
            },
            'EXECUTIVE_COMMAND': {
                'title': 'Executive Command',
                'description': 'Executive leadership and operational authority',
                'permissions': ['All Operations Authorized', 'Command Authority', 'Strategic Operations']
            },
            'DEPARTMENT_DIRECTORS': {
                'title': 'Department Director',
                'description': 'Department leadership and specialized operations',
                'permissions': ['Department Operations', 'Personnel Management', 'Resource Allocation']
            },
            'COMMAND_LEVEL': {
                'title': 'Command Level',
                'description': 'Unit command and tactical operations',
                'permissions': ['Unit Command', 'Tactical Operations', 'Personnel Leadership']
            },
            'SPECIALIZED_UNITS': {
                'title': 'Specialized Unit',
                'description': 'Specialized operations and unit expertise',
                'permissions': ['Specialized Operations', 'Unit Expertise', 'Advanced Training']
            },
            'OMEGA': {
                'title': 'OMEGA Senior Enlisted',
                'description': 'Highest enlisted rank - senior NCOs and veteran operators',
                'permissions': ['Advanced Operations', 'Enlisted Supervision', 'Training Leadership', 'Field Command']
            },
            'BETA': {
                'title': 'BETA Enlisted NCO',
                'description': 'Non-commissioned officers - experienced enlisted personnel',
                'permissions': ['Standard Operations', 'Team Leadership', 'Training Support', 'Squad Command']
            },
            'ALPHA': {
                'title': 'ALPHA Junior Enlisted',
                'description': 'Junior enlisted personnel - basic field operators',
                'permissions': ['Basic Operations', 'Support Duties', 'Training Participation']
            },
            'ENLISTED': {
                'title': 'Enlisted Personnel',
                'description': 'Basic military operations',
                'permissions': ['Basic Operations', 'Support Missions']
            },
            'CIVILIAN': {
                'title': 'Civilian',
                'description': 'No military clearance',
                'permissions': ['Public Access Only']
            }
        }
        
        info = clearance_info.get(clearance_level, clearance_info['CIVILIAN'])
        
        # Choose color based on clearance level
        color_map = {
            'BOARD_OF_DIRECTORS': 0xFF0000,      # Red
            'EXECUTIVE_COMMAND': 0xFF4500,       # Orange Red
            'DEPARTMENT_DIRECTORS': 0xFF8C00,    # Dark Orange
            'COMMAND_LEVEL': 0xFFD700,           # Gold
            'SPECIALIZED_UNITS': 0x32CD32,       # Lime Green
            'OMEGA': 0x00FF00,                   # Green
            'BETA': 0x00CED1,                    # Dark Turquoise
            'ALPHA': 0x0000FF,                   # Blue
            'ENLISTED': 0x808080,                # Gray
            'CIVILIAN': 0xA0A0A0                 # Light Gray
        }
        
        color = color_map.get(clearance_level, Config.COLORS['primary'])
        
        embed = discord.Embed(
            title=f"🔒 Security Clearance - {clearance_level}",
            description=f"**Operator:** {target_user.mention}\n"
                       f"**Position:** {info['title']}\n"
                       f"**Clearance Level:** {clearance_level}\n"
                       f"**Description:** {info['description']}",
            color=color
        )
        
        # Add current roles
        if target_user.roles:
            relevant_roles = [role.name for role in target_user.roles if role.name != '@everyone']
            if relevant_roles:
                embed.add_field(
                    name="📝 Current Roles",
                    value='\n'.join([f"• {role}" for role in relevant_roles[:10]]),
                    inline=False
                )
        
        # Add permissions
        permissions = info.get('permissions', [])
        if permissions:
            embed.add_field(
                name="📋 Authorized Operations",
                value='\n'.join([f"• {perm}" for perm in permissions]),
                inline=False
            )
        
        embed.set_footer(text="Merrywinter Security Consulting - Security Clearance Division")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="roster", description="Display operator roster by clearance level")
    async def operator_roster(self, interaction: discord.Interaction):
        """Display operator roster by clearance level"""
        guild = interaction.guild
        
        # Organize members by clearance level using real guild data
        executive_command = []
        board_directors = []
        department_directors = []
        command_level = []
        specialized_units = []
        omega_ops = []
        beta_ops = []
        alpha_ops = []
        enlisted = []
        
        for member in guild.members:
            if member.bot:
                continue
            
            role_names = [role.name for role in member.roles]
            clearance = Config.get_security_level(role_names)
            
            if clearance == 'EXECUTIVE_COMMAND':
                executive_command.append(member)
            elif clearance == 'BOARD_OF_DIRECTORS':
                board_directors.append(member)
            elif clearance == 'DEPARTMENT_DIRECTORS':
                department_directors.append(member)
            elif clearance == 'COMMAND_LEVEL':
                command_level.append(member)
            elif clearance == 'SPECIALIZED_UNITS':
                specialized_units.append(member)
            elif clearance == 'OMEGA':
                omega_ops.append(member)
            elif clearance == 'BETA':
                beta_ops.append(member)
            elif clearance == 'ALPHA':
                alpha_ops.append(member)
            elif clearance == 'ENLISTED':
                enlisted.append(member)
        
        embed = discord.Embed(
            title="🎖️ Merrywinter Security Consulting - Personnel Roster",
            description="**Current Active Personnel by Clearance Level**",
            color=Config.COLORS['primary']
        )
        
        # Executive Command
        if executive_command:
            exec_list = '\n'.join([f"• {op.display_name}" for op in executive_command[:5]])
            embed.add_field(
                name="👑 Executive Command",
                value=exec_list,
                inline=False
            )
        
        # Board of Directors
        if board_directors:
            board_list = '\n'.join([f"• {op.display_name}" for op in board_directors[:5]])
            embed.add_field(
                name="🏢 Board of Directors",
                value=board_list,
                inline=False
            )
        
        # Department Directors
        if department_directors:
            dir_list = '\n'.join([f"• {op.display_name}" for op in department_directors[:10]])
            embed.add_field(
                name="📋 Department Directors",
                value=dir_list,
                inline=False
            )
        
        # Command Level
        if command_level:
            cmd_list = '\n'.join([f"• {op.display_name}" for op in command_level[:15]])
            embed.add_field(
                name="⚔️ Command Level",
                value=cmd_list,
                inline=False
            )
        
        # Specialized Units
        if specialized_units:
            spec_list = '\n'.join([f"• {op.display_name}" for op in specialized_units[:15]])
            embed.add_field(
                name="🎯 Specialized Units",
                value=spec_list,
                inline=False
            )
        
        # OMEGA Operatives
        if omega_ops:
            omega_list = '\n'.join([f"• {op.display_name}" for op in omega_ops[:10]])
            embed.add_field(
                name="🌟 OMEGA Field Operatives",
                value=omega_list,
                inline=False
            )
        
        # BETA Operatives
        if beta_ops:
            beta_list = '\n'.join([f"• {op.display_name}" for op in beta_ops[:15]])
            embed.add_field(
                name="⚡ BETA Field Operatives",
                value=beta_list,
                inline=False
            )
        
        # ALPHA Operatives
        if alpha_ops:
            alpha_list = '\n'.join([f"• {op.display_name}" for op in alpha_ops[:20]])
            embed.add_field(
                name="🎖️ ALPHA Field Operatives",
                value=alpha_list,
                inline=False
            )
        
        # Enlisted
        if enlisted:
            enlisted_list = '\n'.join([f"• {op.display_name}" for op in enlisted[:25]])
            embed.add_field(
                name="🔰 Enlisted Personnel",
                value=enlisted_list,
                inline=False
            )
        
        # Statistics
        total_ops = len(executive_command) + len(board_directors) + len(department_directors) + len(command_level) + len(specialized_units) + len(omega_ops) + len(beta_ops) + len(alpha_ops) + len(enlisted)
        embed.add_field(
            name="📊 Personnel Statistics",
            value=f"**Total Active Personnel:** {total_ops}\n"
                  f"**Executive Command:** {len(executive_command)}\n"
                  f"**Board of Directors:** {len(board_directors)}\n"
                  f"**Department Directors:** {len(department_directors)}\n"
                  f"**Command Level:** {len(command_level)}\n"
                  f"**Specialized Units:** {len(specialized_units)}\n"
                  f"**OMEGA Field Ops:** {len(omega_ops)}\n"
                  f"**BETA Field Ops:** {len(beta_ops)}\n"
                  f"**ALPHA Field Ops:** {len(alpha_ops)}\n"
                  f"**Enlisted:** {len(enlisted)}",
            inline=False
        )
        
        embed.set_footer(text="Merrywinter Security Consulting - Personnel Division")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="promote", description="Promote enlisted personnel (Admin only)")
    @app_commands.describe(user="User to promote", clearance_level="Enlisted rank (ALPHA, BETA, OMEGA)")
    @app_commands.choices(clearance_level=[
        app_commands.Choice(name="ALPHA - Junior Enlisted (Corporal level)", value="ALPHA"),
        app_commands.Choice(name="BETA - Enlisted NCO (Sergeant level)", value="BETA"),
        app_commands.Choice(name="OMEGA - Senior Enlisted (Sergeant Major level)", value="OMEGA")
    ])
    async def promote_operator(self, interaction: discord.Interaction, user: discord.Member, clearance_level: str):
        """Promote an operator (Admin only)"""
        if not Config.is_admin([role.name for role in interaction.user.roles]):
            await interaction.response.send_message("❌ You need administrator permissions to promote operators.", ephemeral=True)
            return
        
        level = clearance_level.upper()
        
        # Get current clearance
        current_clearance = get_user_clearance(user.roles)
        
        if current_clearance == level:
            await interaction.response.send_message(f"❌ {user.mention} already has {level} clearance.", ephemeral=True)
            return
        
        # Remove old clearance roles
        old_roles = []
        for role in user.roles:
            if (role.name in Config.OMEGA_ROLES + Config.BETA_ROLES + Config.ALPHA_ROLES):
                old_roles.append(role)
        
        try:
            # Remove old roles
            if old_roles:
                await user.remove_roles(*old_roles, reason=f"Clearance update by {interaction.user}")
            
            # Add new role
            new_role_names = {
                'OMEGA': Config.OMEGA_ROLES,
                'BETA': Config.BETA_ROLES,
                'ALPHA': Config.ALPHA_ROLES
            }
            
            new_roles = []
            for role_name in new_role_names[level]:
                role = discord.utils.get(interaction.guild.roles, name=role_name)
                if role:
                    new_roles.append(role)
            
            if new_roles:
                await user.add_roles(*new_roles, reason=f"Promoted to {level} by {interaction.user}")
            
            embed = discord.Embed(
                title="✅ Operator Promoted",
                description=f"**Operator:** {user.mention}\n"
                           f"**Previous Clearance:** {current_clearance}\n"
                           f"**New Clearance:** {level}\n"
                           f"**Authorized By:** {interaction.user.mention}",
                color=Config.COLORS['success']
            )
            embed.set_footer(text="Merrywinter Security Consulting - Personnel Division")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error promoting operator: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="demote", description="Demote an operator (Admin only)")
    @app_commands.describe(user="User to demote", clearance_level="New clearance level (ALPHA, BETA, CIVILIAN)")
    @app_commands.choices(clearance_level=[
        app_commands.Choice(name="ALPHA - Junior Enlisted", value="ALPHA"),
        app_commands.Choice(name="BETA - Enlisted NCO", value="BETA"),
        app_commands.Choice(name="CIVILIAN - No Clearance", value="CIVILIAN")
    ])
    async def demote_operator(self, interaction: discord.Interaction, user: discord.Member, clearance_level: str):
        """Demote an operator (Admin only)"""
        if not Config.is_admin([role.name for role in interaction.user.roles]):
            await interaction.response.send_message("❌ You need administrator permissions to demote operators.", ephemeral=True)
            return
        
        level = clearance_level.upper()
        
        # Get current clearance
        current_clearance = get_user_clearance(user.roles)
        
        if current_clearance == level:
            await interaction.response.send_message(f"❌ {user.mention} already has {level} clearance.", ephemeral=True)
            return
        
        # Remove old clearance roles
        old_roles = []
        for role in user.roles:
            if (role.name in Config.OMEGA_ROLES + Config.BETA_ROLES + Config.ALPHA_ROLES):
                old_roles.append(role)
        
        try:
            # Remove old roles
            if old_roles:
                await user.remove_roles(*old_roles, reason=f"Clearance update by {interaction.user}")
            
            # Add new role (if not civilian)
            if level != 'CIVILIAN':
                new_role_names = {
                    'BETA': Config.BETA_ROLES,
                    'ALPHA': Config.ALPHA_ROLES
                }
                
                new_roles = []
                for role_name in new_role_names[level]:
                    role = discord.utils.get(interaction.guild.roles, name=role_name)
                    if role:
                        new_roles.append(role)
                
                if new_roles:
                    await user.add_roles(*new_roles, reason=f"Demoted to {level} by {interaction.user}")
            
            embed = discord.Embed(
                title="⚠️ Operator Demoted",
                description=f"**Operator:** {user.mention}\n"
                           f"**Previous Clearance:** {current_clearance}\n"
                           f"**New Clearance:** {level}\n"
                           f"**Authorized By:** {interaction.user.mention}",
                color=Config.COLORS['warning']
            )
            embed.set_footer(text="Merrywinter Security Consulting - Personnel Division")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error demoting operator: {str(e)}", ephemeral=True)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(SecurityClearance(bot))