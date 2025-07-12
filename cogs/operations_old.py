"""
PMC Operations management for Merrywinter Security Consulting
Handles missions, deployments, and operational status
"""

import discord
from discord.ext import commands
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
    
    @commands.command(name='mission')
    async def mission_briefing(self, ctx, mission_type: str = None, classified: bool = False):
        """Get mission briefing or create new mission"""
        user_clearance = get_user_clearance(ctx.author.roles)
        
        if user_clearance == 'CIVILIAN':
            await ctx.send("❌ You need military clearance to access mission briefings.")
            return
        
        if not mission_type:
            # Show available missions
            embed = discord.Embed(
                title="🎯 Available Mission Types",
                description="**Merrywinter Security Consulting - Mission Command**\n\n"
                           "Select a mission type to receive your briefing:",
                color=Config.COLORS['primary']
            )
            
            missions = Config.MISSION_TYPES
            for i, mission in enumerate(missions, 1):
                embed.add_field(
                    name=f"{i}. {mission}",
                    value=f"Use: `!mission {mission.lower().replace(' ', '-')}`",
                    inline=True
                )
            
            embed.set_footer(text="Merrywinter Security Consulting - Mission Command")
            await ctx.send(embed=embed)
            return
        
        # Generate mission briefing
        mission_name = mission_type.replace('-', ' ').title()
        
        if mission_name not in Config.MISSION_TYPES:
            await ctx.send("❌ Invalid mission type. Use `!mission` to see available types.")
            return
        
        # Check if classified mission requires higher clearance
        if classified and not Config.has_permission(user_clearance, 'BETA'):
            await ctx.send("❌ You need BETA+ clearance to access classified missions.")
            return
        
        # Generate mission details
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
            operator_info = f"**Operator:** {ctx.author.mention}"
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
                  f"• Call Sign: {ctx.author.display_name[:3].upper()}-{random.randint(10, 99)}",
            inline=False
        )
        
        embed.set_footer(text="Merrywinter Security Consulting - Mission Command")
        
        await ctx.send(embed=embed)
        
        # Save mission data
        mission_data = {
            'mission_id': mission_id,
            'operator_id': ctx.author.id,
            'mission_type': mission_name,
            'sector': sector,
            'objectives': objectives,
            'classified': classified,
            'status': 'briefed',
            'created_at': datetime.utcnow().isoformat(),
            'guild_id': ctx.guild.id
        }
        
        await self.storage.save_mission(mission_data)
    
    def generate_mission_objectives(self, mission_type: str) -> str:
        """Generate mission objectives based on mission type"""
        objectives = {
            'Reconnaissance': [
                "• Conduct surveillance of target area",
                "• Identify enemy positions and movements",
                "• Report intelligence findings",
                "• Avoid detection at all costs"
            ],
            'Direct Action': [
                "• Eliminate high-value targets",
                "• Secure the objective area",
                "• Neutralize enemy resistance",
                "• Exfiltrate to extraction point"
            ],
            'Special Operations': [
                "• Classified mission parameters",
                "• Execute with extreme precision",
                "• Maintain total operational security",
                "• Report to command only"
            ],
            'Security Detail': [
                "• Protect designated personnel",
                "• Secure perimeter and access points",
                "• Maintain vigilant watch",
                "• Respond to threats immediately"
            ],
            'Convoy Escort': [
                "• Escort convoy through hostile territory",
                "• Maintain formation and communication",
                "• Neutralize threats to convoy",
                "• Ensure safe arrival at destination"
            ],
            'Base Defense': [
                "• Defend base from enemy assault",
                "• Maintain defensive positions",
                "• Coordinate with other defenders",
                "• Prevent enemy infiltration"
            ],
            'Intelligence Gathering': [
                "• Infiltrate enemy communications",
                "• Gather strategic intelligence",
                "• Document enemy capabilities",
                "• Exfiltrate without detection"
            ],
            'Counter-Intelligence': [
                "• Identify enemy intelligence assets",
                "• Disrupt enemy operations",
                "• Protect friendly intelligence",
                "• Eliminate security threats"
            ],
            'Training Exercise': [
                "• Execute training scenarios",
                "• Demonstrate tactical proficiency",
                "• Coordinate with training team",
                "• Complete all training objectives"
            ],
            'Joint Operations': [
                "• Coordinate with allied forces",
                "• Execute combined operations",
                "• Maintain inter-unit communication",
                "• Achieve joint mission objectives"
            ]
        }
        
        return '\n'.join(objectives.get(mission_type, [
            "• Complete assigned objectives",
            "• Maintain operational security",
            "• Report status to command",
            "• Return to base safely"
        ]))
    
    @commands.command(name='status')
    async def operator_status(self, ctx, user: discord.Member = None):
        """Check operator status and active missions"""
        target_user = user or ctx.author
        user_clearance = get_user_clearance(target_user.roles)
        
        if user_clearance == 'CIVILIAN':
            await ctx.send("❌ No military status available for civilian personnel.")
            return
        
        # Get operator's active missions
        active_missions = await self.storage.get_active_missions(target_user.id)
        
        embed = discord.Embed(
            title=f"📊 Operator Status - {target_user.display_name}",
            description=f"**Clearance Level:** {user_clearance}\n"
                       f"**Status:** {'🟢 Active' if active_missions else '🟡 Standby'}\n"
                       f"**Active Missions:** {len(active_missions)}",
            color=Config.COLORS.get(user_clearance.lower(), Config.COLORS['primary'])
        )
        
        if active_missions:
            mission_list = []
            for mission in active_missions[:5]:  # Show max 5 missions
                mission_list.append(f"• {mission['mission_id']} - {mission['mission_type']}")
            
            embed.add_field(
                name="🎯 Active Missions",
                value='\n'.join(mission_list),
                inline=False
            )
        
        # Add operational statistics
        total_missions = await self.storage.get_mission_count(target_user.id)
        embed.add_field(
            name="📈 Statistics",
            value=f"**Total Missions:** {total_missions}\n"
                  f"**Success Rate:** {random.randint(85, 99)}%\n"
                  f"**Commendations:** {random.randint(0, 10)}",
            inline=True
        )
        
        embed.add_field(
            name="🏆 Specializations",
            value="• Urban Warfare\n• Reconnaissance\n• Counter-Intelligence",
            inline=True
        )
        
        embed.set_footer(text="Merrywinter Security Consulting - Personnel Status")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='deploy')
    async def deploy_to_sector(self, ctx, *, sector: str = None):
        """Deploy operator to a specific sector"""
        user_clearance = get_user_clearance(ctx.author.roles)
        
        if user_clearance == 'CIVILIAN':
            await ctx.send("❌ You need military clearance to deploy to operational sectors.")
            return
        
        if not sector:
            # Show available sectors
            embed = discord.Embed(
                title="🗺️ Available Deployment Sectors",
                description="**Merrywinter Security Consulting - Deployment Command**\n\n"
                           "Select a sector for deployment:",
                color=Config.COLORS['primary']
            )
            
            for i, sector_name in enumerate(Config.OPERATION_SECTORS, 1):
                embed.add_field(
                    name=f"{i}. {sector_name}",
                    value=f"Use: `!deploy {sector_name.split(' - ')[0]}`",
                    inline=True
                )
            
            embed.set_footer(text="Merrywinter Security Consulting - Deployment Command")
            await ctx.send(embed=embed)
            return
        
        # Find matching sector
        matching_sector = None
        for sector_name in Config.OPERATION_SECTORS:
            if sector.lower() in sector_name.lower():
                matching_sector = sector_name
                break
        
        if not matching_sector:
            await ctx.send("❌ Invalid sector. Use `!deploy` to see available sectors.")
            return
        
        # Create deployment
        deployment_id = f"DEP-{random.randint(1000, 9999)}"
        
        embed = discord.Embed(
            title="🚁 DEPLOYMENT ORDERS",
            description=f"**Deployment ID:** {deployment_id}\n"
                       f"**Operator:** {ctx.author.mention}\n"
                       f"**Clearance Level:** {user_clearance}\n"
                       f"**Destination:** {matching_sector}\n"
                       f"**Deployment Time:** {datetime.utcnow().strftime('%H:%M:%S')} UTC",
            color=Config.COLORS['warning']
        )
        
        embed.add_field(
            name="📋 Pre-Deployment Checklist",
            value="✅ Equipment Check\n"
                  "✅ Communication Systems\n"
                  "✅ Mission Briefing\n"
                  "✅ Authorization Confirmed",
            inline=False
        )
        
        embed.add_field(
            name="⚠️ Deployment Guidelines",
            value="• Maintain radio contact\n"
                  "• Follow established protocols\n"
                  "• Report any anomalies\n"
                  "• Await further orders",
            inline=False
        )
        
        embed.set_footer(text="Merrywinter Security Consulting - Deployment Command")
        
        await ctx.send(embed=embed)
        
        # Save deployment data
        deployment_data = {
            'deployment_id': deployment_id,
            'operator_id': ctx.author.id,
            'sector': matching_sector,
            'status': 'deployed',
            'deployed_at': datetime.utcnow().isoformat(),
            'guild_id': ctx.guild.id
        }
        
        await self.storage.save_deployment(deployment_data)
    
    @commands.command(name='intel')
    async def intelligence_report(self, ctx, report_type: str = None):
        """Access intelligence reports"""
        user_clearance = get_user_clearance(ctx.author.roles)
        
        if user_clearance == 'CIVILIAN':
            await ctx.send("❌ You need military clearance to access intelligence reports.")
            return
        
        if not report_type:
            embed = discord.Embed(
                title="🔍 Intelligence Report Types",
                description="**Available Intelligence Categories:**",
                color=Config.COLORS['info']
            )
            
            embed.add_field(
                name="📊 Threat Assessment",
                value="`!intel threat` - Current threat levels",
                inline=False
            )
            
            embed.add_field(
                name="🗺️ Sector Analysis",
                value="`!intel sector` - Sector-specific intelligence",
                inline=False
            )
            
            embed.add_field(
                name="👥 Enemy Activity",
                value="`!intel enemy` - Enemy movement reports",
                inline=False
            )
            
            if user_clearance in ['BETA', 'OMEGA']:
                embed.add_field(
                    name="🔒 Classified (BETA+)",
                    value="`!intel classified` - High-clearance intelligence",
                    inline=False
                )
            
            await ctx.send(embed=embed)
            return
        
        # Generate intelligence report
        report_type = report_type.lower()
        
        if report_type == 'threat':
            embed = discord.Embed(
                title="⚠️ THREAT ASSESSMENT REPORT",
                description="**Current Operational Threat Level: MODERATE**",
                color=Config.COLORS['warning']
            )
            
            embed.add_field(
                name="🔴 High Priority Threats",
                value="• Increased hostile activity in Sector Beta\n"
                      "• Potential insider threat reports\n"
                      "• Communication intercepts detected",
                inline=False
            )
            
            embed.add_field(
                name="🟡 Medium Priority Threats",
                value="• Equipment malfunctions reported\n"
                      "• Weather conditions affecting operations\n"
                      "• Supply chain disruptions possible",
                inline=False
            )
            
        elif report_type == 'sector':
            embed = discord.Embed(
                title="🗺️ SECTOR ANALYSIS REPORT",
                description="**Multi-Sector Intelligence Summary**",
                color=Config.COLORS['info']
            )
            
            embed.add_field(
                name="🏙️ Urban Sectors",
                value="• High civilian density\n"
                      "• Complex building layouts\n"
                      "• Multiple entry/exit points",
                inline=True
            )
            
            embed.add_field(
                name="🏜️ Desert Sectors",
                value="• Limited cover available\n"
                      "• Extreme weather conditions\n"
                      "• Long-range visibility",
                inline=True
            )
            
            embed.add_field(
                name="🌊 Naval Sectors",
                value="• Amphibious operations required\n"
                      "• Weather-dependent missions\n"
                      "• Specialized equipment needed",
                inline=True
            )
            
        elif report_type == 'enemy':
            embed = discord.Embed(
                title="👥 ENEMY ACTIVITY REPORT",
                description="**Recent Hostile Movement Intelligence**",
                color=Config.COLORS['error']
            )
            
            embed.add_field(
                name="📍 Confirmed Contacts",
                value="• Squad-sized element in Sector Alpha\n"
                      "• Patrol activity increased 40%\n"
                      "• New defensive positions established",
                inline=False
            )
            
            embed.add_field(
                name="🎯 Recommended Actions",
                value="• Increase surveillance operations\n"
                      "• Prepare counter-reconnaissance\n"
                      "• Brief all operators on new threats",
                inline=False
            )
            
        elif report_type == 'classified' and user_clearance in ['BETA', 'OMEGA']:
            embed = discord.Embed(
                title="🔒 CLASSIFIED INTELLIGENCE REPORT",
                description="**CLEARANCE LEVEL: BETA+ REQUIRED**",
                color=Config.COLORS['error']
            )
            
            embed.add_field(
                name="🎯 High-Value Intelligence",
                value="• [REDACTED] facility compromised\n"
                      "• Asset extraction pending\n"
                      "• Counter-intelligence operation active",
                inline=False
            )
            
            embed.add_field(
                name="⚠️ Critical Alert",
                value="• Operation security potentially compromised\n"
                      "• All personnel advised to maintain OPSEC\n"
                      "• Report any suspicious activity immediately",
                inline=False
            )
            
        else:
            await ctx.send("❌ Invalid intelligence report type or insufficient clearance.")
            return
        
        embed.set_footer(text="Merrywinter Security Consulting - Intelligence Division")
        await ctx.send(embed=embed)
    
    @commands.command(name='sitrep')
    async def situation_report(self, ctx):
        """Generate situation report for current operations"""
        user_clearance = get_user_clearance(ctx.author.roles)
        
        if user_clearance == 'CIVILIAN':
            await ctx.send("❌ You need military clearance to access situation reports.")
            return
        
        # Get operational statistics
        guild_missions = await self.storage.get_guild_missions(ctx.guild.id)
        active_missions = len([m for m in guild_missions if m.get('status') == 'active'])
        
        embed = discord.Embed(
            title="📊 SITUATION REPORT (SITREP)",
            description=f"**Report Time:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
                       f"**Reporting Officer:** {ctx.author.mention}\n"
                       f"**Clearance Level:** {user_clearance}",
            color=Config.COLORS['info']
        )
        
        embed.add_field(
            name="🎯 Current Operations",
            value=f"**Active Missions:** {active_missions}\n"
                  f"**Deployed Operators:** {random.randint(5, 25)}\n"
                  f"**Sectors Under Surveillance:** {random.randint(3, 8)}",
            inline=False
        )
        
        embed.add_field(
            name="📈 Operational Status",
            value=f"**Success Rate:** {random.randint(85, 99)}%\n"
                  f"**Equipment Readiness:** {random.randint(90, 100)}%\n"
                  f"**Personnel Readiness:** {random.randint(85, 95)}%",
            inline=True
        )
        
        embed.add_field(
            name="⚠️ Current Alerts",
            value="• Weather conditions affecting Sector Beta\n"
                  "• Equipment maintenance scheduled\n"
                  "• New intelligence received",
            inline=True
        )
        
        embed.set_footer(text="Merrywinter Security Consulting - Operations Center")
        
        await ctx.send(embed=embed)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(PMCOperations(bot))
