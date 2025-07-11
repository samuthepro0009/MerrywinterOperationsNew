"""
Security clearance management for Merrywinter Security Consulting
Handles Omega, Beta, and Alpha clearance levels
"""

import discord
from discord.ext import commands
from datetime import datetime

from config.settings import Config
from utils.helpers import get_user_clearance, create_embed
from utils.storage import Storage

class SecurityClearance(commands.Cog):
    """Security clearance management system"""
    
    def __init__(self, bot):
        self.bot = bot
        self.storage = Storage()
    
    @commands.command(name='clearance')
    async def check_clearance(self, ctx, user: discord.Member = None):
        """Check security clearance level"""
        target_user = user or ctx.author
        
        clearance_level = get_user_clearance(target_user.roles)
        chain_info = Config.CHAIN_OF_COMMAND.get(clearance_level, {
            'title': 'Civilian',
            'description': 'No military clearance',
            'permissions': []
        })
        
        # Choose color based on clearance level
        color = Config.COLORS.get(clearance_level.lower(), Config.COLORS['primary'])
        
        embed = discord.Embed(
            title=f"🔒 Security Clearance - {clearance_level}",
            description=f"**Operator:** {target_user.mention}\n"
                       f"**Rank:** {chain_info['title']}\n"
                       f"**Clearance Level:** {clearance_level}\n"
                       f"**Description:** {chain_info['description']}",
            color=color
        )
        
        # Add clearance level indicator
        if clearance_level == 'OMEGA':
            embed.add_field(name="🌟 Supreme Authority", value="Full command access", inline=False)
        elif clearance_level == 'BETA':
            embed.add_field(name="⚡ Field Command", value="Operations and management", inline=False)
        elif clearance_level == 'ALPHA':
            embed.add_field(name="🎯 Ground Operations", value="Basic operations access", inline=False)
        else:
            embed.add_field(name="🚫 Restricted", value="No military access", inline=False)
        
        # Add permissions
        permissions = chain_info.get('permissions', [])
        if permissions and permissions != ['all']:
            embed.add_field(
                name="📋 Authorized Operations",
                value='\n'.join([f"• {perm.replace('_', ' ').title()}" for perm in permissions]),
                inline=False
            )
        elif permissions == ['all']:
            embed.add_field(
                name="📋 Authorized Operations",
                value="• All Operations Authorized",
                inline=False
            )
        
        embed.set_footer(text="Merrywinter Security Consulting - Security Clearance Division")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='roster')
    async def operator_roster(self, ctx):
        """Display operator roster by clearance level"""
        guild = ctx.guild
        
        # Organize members by clearance level
        omega_ops = []
        beta_ops = []
        alpha_ops = []
        
        for member in guild.members:
            if member.bot:
                continue
            
            clearance = get_user_clearance(member.roles)
            
            if clearance == 'OMEGA':
                omega_ops.append(member)
            elif clearance == 'BETA':
                beta_ops.append(member)
            elif clearance == 'ALPHA':
                alpha_ops.append(member)
        
        embed = discord.Embed(
            title="🎖️ Merrywinter Security Consulting - Operator Roster",
            description="**Current Active Personnel**",
            color=Config.COLORS['primary']
        )
        
        if omega_ops:
            omega_list = '\n'.join([f"• {op.display_name}" for op in omega_ops[:10]])
            embed.add_field(
                name="🌟 OMEGA Command (Supreme Authority)",
                value=omega_list,
                inline=False
            )
        
        if beta_ops:
            beta_list = '\n'.join([f"• {op.display_name}" for op in beta_ops[:15]])
            embed.add_field(
                name="⚡ BETA Command (Field Operations)",
                value=beta_list,
                inline=False
            )
        
        if alpha_ops:
            alpha_list = '\n'.join([f"• {op.display_name}" for op in alpha_ops[:20]])
            embed.add_field(
                name="🎯 ALPHA Operators (Ground Operations)",
                value=alpha_list,
                inline=False
            )
        
        total_ops = len(omega_ops) + len(beta_ops) + len(alpha_ops)
        embed.add_field(
            name="📊 Personnel Statistics",
            value=f"**Total Active Operators:** {total_ops}\n"
                  f"**OMEGA:** {len(omega_ops)}\n"
                  f"**BETA:** {len(beta_ops)}\n"
                  f"**ALPHA:** {len(alpha_ops)}",
            inline=False
        )
        
        embed.set_footer(text="Merrywinter Security Consulting - Personnel Division")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='promote')
    @commands.has_permissions(manage_roles=True)
    async def promote_operator(self, ctx, user: discord.Member, level: str):
        """Promote an operator to a higher clearance level (Admin only)"""
        if not Config.is_admin([role.name for role in ctx.author.roles]):
            await ctx.send("❌ You don't have permission to promote operators.")
            return
        
        level = level.upper()
        
        if level not in Config.SECURITY_LEVELS:
            await ctx.send("❌ Invalid clearance level. Use: OMEGA, BETA, or ALPHA")
            return
        
        # Get current clearance
        current_clearance = get_user_clearance(user.roles)
        
        if current_clearance == level:
            await ctx.send(f"❌ {user.mention} already has {level} clearance.")
            return
        
        # Remove old clearance roles
        old_roles = []
        for role in user.roles:
            if (role.name in Config.OMEGA_ROLES + Config.BETA_ROLES + Config.ALPHA_ROLES):
                old_roles.append(role)
        
        try:
            # Remove old roles
            if old_roles:
                await user.remove_roles(*old_roles, reason=f"Clearance update by {ctx.author}")
            
            # Add new role
            new_role_names = {
                'OMEGA': Config.OMEGA_ROLES,
                'BETA': Config.BETA_ROLES,
                'ALPHA': Config.ALPHA_ROLES
            }
            
            new_roles = []
            for role_name in new_role_names[level]:
                role = discord.utils.get(ctx.guild.roles, name=role_name)
                if role:
                    new_roles.append(role)
            
            if new_roles:
                await user.add_roles(*new_roles, reason=f"Promoted to {level} by {ctx.author}")
            
            # Log the promotion
            await self.storage.log_promotion(user.id, current_clearance, level, ctx.author.id)
            
            # Send confirmation
            embed = discord.Embed(
                title="🎖️ Operator Promoted",
                description=f"**Operator:** {user.mention}\n"
                           f"**Previous Clearance:** {current_clearance}\n"
                           f"**New Clearance:** {level}\n"
                           f"**Authorized By:** {ctx.author.mention}",
                color=Config.COLORS['success']
            )
            embed.set_footer(text="Merrywinter Security Consulting - Personnel Division")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error promoting operator: {str(e)}")
    
    @commands.command(name='demote')
    @commands.has_permissions(manage_roles=True)
    async def demote_operator(self, ctx, user: discord.Member, level: str):
        """Demote an operator to a lower clearance level (Admin only)"""
        if not Config.is_admin([role.name for role in ctx.author.roles]):
            await ctx.send("❌ You don't have permission to demote operators.")
            return
        
        level = level.upper()
        
        if level not in Config.SECURITY_LEVELS:
            await ctx.send("❌ Invalid clearance level. Use: OMEGA, BETA, or ALPHA")
            return
        
        # Get current clearance
        current_clearance = get_user_clearance(user.roles)
        
        if current_clearance == level:
            await ctx.send(f"❌ {user.mention} already has {level} clearance.")
            return
        
        # Check if this is actually a demotion
        if Config.SECURITY_LEVELS[current_clearance] <= Config.SECURITY_LEVELS[level]:
            await ctx.send("❌ This would be a promotion, not a demotion. Use !promote instead.")
            return
        
        # Remove old clearance roles
        old_roles = []
        for role in user.roles:
            if (role.name in Config.OMEGA_ROLES + Config.BETA_ROLES + Config.ALPHA_ROLES):
                old_roles.append(role)
        
        try:
            # Remove old roles
            if old_roles:
                await user.remove_roles(*old_roles, reason=f"Clearance update by {ctx.author}")
            
            # Add new role
            new_role_names = {
                'OMEGA': Config.OMEGA_ROLES,
                'BETA': Config.BETA_ROLES,
                'ALPHA': Config.ALPHA_ROLES
            }
            
            new_roles = []
            for role_name in new_role_names[level]:
                role = discord.utils.get(ctx.guild.roles, name=role_name)
                if role:
                    new_roles.append(role)
            
            if new_roles:
                await user.add_roles(*new_roles, reason=f"Demoted to {level} by {ctx.author}")
            
            # Log the demotion
            await self.storage.log_promotion(user.id, current_clearance, level, ctx.author.id)
            
            # Send confirmation
            embed = discord.Embed(
                title="⬇️ Operator Demoted",
                description=f"**Operator:** {user.mention}\n"
                           f"**Previous Clearance:** {current_clearance}\n"
                           f"**New Clearance:** {level}\n"
                           f"**Authorized By:** {ctx.author.mention}",
                color=Config.COLORS['warning']
            )
            embed.set_footer(text="Merrywinter Security Consulting - Personnel Division")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error demoting operator: {str(e)}")
    
    @commands.command(name='security-audit')
    @commands.has_permissions(administrator=True)
    async def security_audit(self, ctx):
        """Perform security audit of all operators (Admin only)"""
        if not Config.is_admin([role.name for role in ctx.author.roles]):
            await ctx.send("❌ You don't have permission to perform security audits.")
            return
        
        guild = ctx.guild
        issues = []
        
        # Check for role configuration issues
        for member in guild.members:
            if member.bot:
                continue
            
            member_roles = [role.name for role in member.roles]
            
            # Check for conflicting clearance levels
            clearance_roles = []
            for role_name in member_roles:
                if role_name in Config.OMEGA_ROLES:
                    clearance_roles.append('OMEGA')
                elif role_name in Config.BETA_ROLES:
                    clearance_roles.append('BETA')
                elif role_name in Config.ALPHA_ROLES:
                    clearance_roles.append('ALPHA')
            
            if len(set(clearance_roles)) > 1:
                issues.append(f"🔴 {member.display_name} has conflicting clearance levels: {', '.join(set(clearance_roles))}")
        
        embed = discord.Embed(
            title="🔍 Security Audit Report",
            description=f"**Guild:** {guild.name}\n**Audit Date:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
            color=Config.COLORS['info']
        )
        
        if issues:
            embed.add_field(
                name="⚠️ Issues Found",
                value='\n'.join(issues[:10]),  # Show max 10 issues
                inline=False
            )
        else:
            embed.add_field(
                name="✅ Audit Results",
                value="No security issues found. All operators have proper clearance levels.",
                inline=False
            )
        
        embed.set_footer(text="Merrywinter Security Consulting - Security Audit Division")
        
        await ctx.send(embed=embed)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(SecurityClearance(bot))
