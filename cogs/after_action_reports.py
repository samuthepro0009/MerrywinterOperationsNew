"""
After Action Reports (AAR) System for FROST AI
Structured mission debriefings with lessons learned and performance analysis
"""

import discord
from discord.ext import commands
from discord import app_commands
import json
from datetime import datetime, timedelta
from config.settings import Config
from utils.helpers import create_embed
from utils.storage import Storage

class AfterActionReports(commands.Cog):
    """After Action Reports system for mission debriefings"""
    
    def __init__(self, bot):
        self.bot = bot
        self.storage = Storage()
        
        # AAR categories and templates
        self.aar_templates = {
            'combat_mission': {
                'name': 'Combat Operation',
                'sections': [
                    'mission_summary',
                    'objectives_assessment', 
                    'tactical_analysis',
                    'casualties_damage',
                    'equipment_performance',
                    'lessons_learned',
                    'recommendations'
                ]
            },
            'training_exercise': {
                'name': 'Training Exercise',
                'sections': [
                    'exercise_summary',
                    'learning_objectives',
                    'participant_performance',
                    'scenarios_tested',
                    'skill_gaps_identified',
                    'training_effectiveness',
                    'future_improvements'
                ]
            },
            'recon_mission': {
                'name': 'Reconnaissance Mission',
                'sections': [
                    'mission_summary',
                    'intelligence_gathered',
                    'route_analysis',
                    'threats_encountered',
                    'equipment_effectiveness',
                    'stealth_assessment',
                    'recommendations'
                ]
            },
            'defensive_operation': {
                'name': 'Defensive Operation',
                'sections': [
                    'situation_summary',
                    'defensive_positions',
                    'threat_assessment',
                    'resource_utilization',
                    'coordination_effectiveness',
                    'casualties_damage',
                    'lessons_learned'
                ]
            }
        }
        
    def cog_check(self, ctx):
        """Check if command is used in authorized guild"""
        return Config.check_guild_authorization(ctx.guild.id)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check if interaction is in authorized guild"""
        return Config.check_guild_authorization(interaction.guild.id)
    
    @app_commands.command(name="aar-create", description="Create a new After Action Report")
    @app_commands.describe(
        mission_name="Name of the mission/operation",
        mission_type="Type of mission",
        operation_date="Date of operation (YYYY-MM-DD)",
        commander="Mission commander",
        participants="Number of participants"
    )
    async def create_aar(
        self,
        interaction: discord.Interaction,
        mission_name: str,
        mission_type: str,
        operation_date: str,
        commander: discord.Member,
        participants: int = 1
    ):
        """Create a new After Action Report"""
        # Check permissions - only moderators and above can create AARs
        if not Config.is_moderator([role.name for role in interaction.user.roles], interaction.user.id):
            await interaction.response.send_message(
                "❌ Access denied. Commander permissions required to create AARs.",
                ephemeral=True
            )
            return
        
        # Validate mission type
        if mission_type not in self.aar_templates:
            valid_types = ", ".join(self.aar_templates.keys())
            await interaction.response.send_message(
                f"❌ Invalid mission type. Valid types: {valid_types}",
                ephemeral=True
            )
            return
        
        # Validate date format
        try:
            operation_datetime = datetime.strptime(operation_date, "%Y-%m-%d")
        except ValueError:
            await interaction.response.send_message(
                "❌ Invalid date format. Use YYYY-MM-DD (e.g., 2025-07-12)",
                ephemeral=True
            )
            return
        
        # Load AAR data
        aar_data = await self.storage.load_after_action_reports()
        
        # Generate AAR ID
        aar_id = f"AAR-{len(aar_data) + 1:04d}"
        
        # Create AAR entry
        aar_entry = {
            'aar_id': aar_id,
            'mission_name': mission_name,
            'mission_type': mission_type,
            'operation_date': operation_date,
            'commander_id': commander.id,
            'commander_name': commander.display_name,
            'participants': participants,
            'created_by': interaction.user.id,
            'created_date': datetime.utcnow().isoformat(),
            'status': 'draft',
            'sections': {},
            'overall_rating': None,
            'classification': 'unclassified',
            'lessons_learned': [],
            'recommendations': [],
            'attachments': []
        }
        
        # Initialize sections based on template
        template = self.aar_templates[mission_type]
        for section in template['sections']:
            aar_entry['sections'][section] = {
                'content': '',
                'completed': False,
                'last_updated': None,
                'updated_by': None
            }
        
        aar_data[aar_id] = aar_entry
        await self.storage.save_after_action_reports(aar_data)
        
        # Create response embed
        embed = create_embed(
            title="📋 After Action Report Created",
            description=f"AAR **{aar_id}** has been created for mission: **{mission_name}**",
            color=Config.COLORS['success']
        )
        
        embed.add_field(name="AAR ID", value=f"`{aar_id}`", inline=True)
        embed.add_field(name="Mission Type", value=template['name'], inline=True)
        embed.add_field(name="Operation Date", value=operation_date, inline=True)
        embed.add_field(name="Commander", value=commander.mention, inline=True)
        embed.add_field(name="Participants", value=str(participants), inline=True)
        embed.add_field(name="Status", value="Draft", inline=True)
        
        # Show required sections
        sections_text = "\n".join(f"• {section.replace('_', ' ').title()}" for section in template['sections'])
        embed.add_field(name="Required Sections", value=sections_text, inline=False)
        
        embed.add_field(
            name="Next Steps", 
            value=f"Use `/aar-edit {aar_id} <section>` to fill out each section.\nUse `/aar-finalize {aar_id}` when complete.",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="aar-edit", description="Edit a section of an After Action Report")
    @app_commands.describe(
        aar_id="AAR ID to edit",
        section="Section to edit",
        content="Content for the section"
    )
    async def edit_aar(
        self,
        interaction: discord.Interaction,
        aar_id: str,
        section: str,
        content: str
    ):
        """Edit an AAR section"""
        # Load AAR data
        aar_data = await self.storage.load_after_action_reports()
        
        if aar_id not in aar_data:
            await interaction.response.send_message(
                f"❌ AAR ID `{aar_id}` not found.",
                ephemeral=True
            )
            return
        
        aar = aar_data[aar_id]
        
        # Check permissions - commander, creator, or moderator can edit
        can_edit = (
            interaction.user.id == aar['commander_id'] or
            interaction.user.id == aar['created_by'] or
            Config.is_moderator([role.name for role in interaction.user.roles], interaction.user.id)
        )
        
        if not can_edit:
            await interaction.response.send_message(
                "❌ You can only edit AARs you created or commanded.",
                ephemeral=True
            )
            return
        
        # Check if AAR is finalized
        if aar['status'] == 'finalized':
            await interaction.response.send_message(
                "❌ Cannot edit a finalized AAR. Create an addendum if needed.",
                ephemeral=True
            )
            return
        
        # Validate section
        if section not in aar['sections']:
            valid_sections = ", ".join(aar['sections'].keys())
            await interaction.response.send_message(
                f"❌ Invalid section. Valid sections: {valid_sections}",
                ephemeral=True
            )
            return
        
        # Update section
        aar['sections'][section]['content'] = content
        aar['sections'][section]['completed'] = True
        aar['sections'][section]['last_updated'] = datetime.utcnow().isoformat()
        aar['sections'][section]['updated_by'] = interaction.user.id
        
        await self.storage.save_after_action_reports(aar_data)
        
        # Create response embed
        embed = create_embed(
            title="📝 AAR Section Updated",
            description=f"Section **{section.replace('_', ' ').title()}** has been updated",
            color=Config.COLORS['success']
        )
        
        embed.add_field(name="AAR ID", value=f"`{aar_id}`", inline=True)
        embed.add_field(name="Mission", value=aar['mission_name'], inline=True)
        embed.add_field(name="Section", value=section.replace('_', ' ').title(), inline=True)
        
        # Show completion status
        completed_sections = sum(1 for s in aar['sections'].values() if s['completed'])
        total_sections = len(aar['sections'])
        completion_rate = (completed_sections / total_sections * 100)
        
        embed.add_field(name="Progress", value=f"{completion_rate:.0f}% ({completed_sections}/{total_sections} sections)", inline=False)
        
        if content:
            preview = content[:200] + "..." if len(content) > 200 else content
            embed.add_field(name="Content Preview", value=f"```{preview}```", inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="aar-view", description="View an After Action Report")
    @app_commands.describe(
        aar_id="AAR ID to view",
        section="Specific section to view (optional)"
    )
    async def view_aar(
        self,
        interaction: discord.Interaction,
        aar_id: str,
        section: str = None
    ):
        """View an AAR"""
        # Load AAR data
        aar_data = await self.storage.load_after_action_reports()
        
        if aar_id not in aar_data:
            await interaction.response.send_message(
                f"❌ AAR ID `{aar_id}` not found.",
                ephemeral=True
            )
            return
        
        aar = aar_data[aar_id]
        
        # Check classification access
        if aar.get('classification') == 'classified':
            if not Config.is_omega_clearance([role.name for role in interaction.user.roles]):
                await interaction.response.send_message(
                    "❌ This AAR is classified. OMEGA clearance required.",
                    ephemeral=True
                )
                return
        
        # If specific section requested
        if section:
            if section not in aar['sections']:
                valid_sections = ", ".join(aar['sections'].keys())
                await interaction.response.send_message(
                    f"❌ Invalid section. Valid sections: {valid_sections}",
                    ephemeral=True
                )
                return
            
            section_data = aar['sections'][section]
            
            embed = create_embed(
                title=f"📋 AAR {aar_id} - {section.replace('_', ' ').title()}",
                description=f"**{aar['mission_name']}** ({aar['operation_date']})",
                color=Config.COLORS['info']
            )
            
            if section_data['content']:
                # Split content if too long for Discord
                content = section_data['content']
                if len(content) > 1024:
                    embed.add_field(name="Content (Part 1)", value=content[:1024], inline=False)
                    if len(content) > 1024:
                        embed.add_field(name="Content (Part 2)", value=content[1024:2048], inline=False)
                else:
                    embed.add_field(name="Content", value=content, inline=False)
                
                if section_data['last_updated']:
                    updated_date = datetime.fromisoformat(section_data['last_updated'])
                    embed.add_field(name="Last Updated", value=f"<t:{int(updated_date.timestamp())}:R>", inline=True)
            else:
                embed.add_field(name="Status", value="Not completed", inline=False)
            
            await interaction.response.send_message(embed=embed)
            return
        
        # Show full AAR overview
        embed = create_embed(
            title=f"📋 After Action Report - {aar_id}",
            description=f"**{aar['mission_name']}**",
            color=Config.COLORS['info']
        )
        
        # Basic info
        commander = interaction.guild.get_member(aar['commander_id'])
        embed.add_field(name="Mission Type", value=self.aar_templates[aar['mission_type']]['name'], inline=True)
        embed.add_field(name="Operation Date", value=aar['operation_date'], inline=True)
        embed.add_field(name="Commander", value=commander.mention if commander else "Unknown", inline=True)
        embed.add_field(name="Participants", value=str(aar['participants']), inline=True)
        embed.add_field(name="Status", value=aar['status'].title(), inline=True)
        embed.add_field(name="Classification", value=aar['classification'].title(), inline=True)
        
        # Section completion
        completed_sections = sum(1 for s in aar['sections'].values() if s['completed'])
        total_sections = len(aar['sections'])
        completion_rate = (completed_sections / total_sections * 100)
        
        embed.add_field(name="Completion", value=f"{completion_rate:.0f}% ({completed_sections}/{total_sections})", inline=True)
        
        # Show section status
        sections_text = ""
        for section_name, section_data in aar['sections'].items():
            status_icon = "✅" if section_data['completed'] else "❌"
            sections_text += f"{status_icon} {section_name.replace('_', ' ').title()}\n"
        
        embed.add_field(name="Sections", value=sections_text, inline=False)
        
        # Overall rating if available
        if aar['overall_rating']:
            rating_stars = "⭐" * aar['overall_rating']
            embed.add_field(name="Overall Rating", value=f"{rating_stars} ({aar['overall_rating']}/5)", inline=True)
        
        # Created info
        created_date = datetime.fromisoformat(aar['created_date'])
        embed.add_field(name="Created", value=f"<t:{int(created_date.timestamp())}:f>", inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="aar-finalize", description="Finalize an After Action Report")
    @app_commands.describe(
        aar_id="AAR ID to finalize",
        overall_rating="Overall mission rating (1-5)",
        classification="Classification level"
    )
    async def finalize_aar(
        self,
        interaction: discord.Interaction,
        aar_id: str,
        overall_rating: int = None,
        classification: str = "unclassified"
    ):
        """Finalize an AAR"""
        # Load AAR data
        aar_data = await self.storage.load_after_action_reports()
        
        if aar_id not in aar_data:
            await interaction.response.send_message(
                f"❌ AAR ID `{aar_id}` not found.",
                ephemeral=True
            )
            return
        
        aar = aar_data[aar_id]
        
        # Check permissions
        can_finalize = (
            interaction.user.id == aar['commander_id'] or
            interaction.user.id == aar['created_by'] or
            Config.is_moderator([role.name for role in interaction.user.roles], interaction.user.id)
        )
        
        if not can_finalize:
            await interaction.response.send_message(
                "❌ You can only finalize AARs you created or commanded.",
                ephemeral=True
            )
            return
        
        # Check if all sections are completed
        incomplete_sections = [name for name, data in aar['sections'].items() if not data['completed']]
        if incomplete_sections:
            sections_text = ", ".join(incomplete_sections)
            await interaction.response.send_message(
                f"❌ Cannot finalize AAR. Incomplete sections: {sections_text}",
                ephemeral=True
            )
            return
        
        # Validate rating
        if overall_rating and not 1 <= overall_rating <= 5:
            await interaction.response.send_message(
                "❌ Overall rating must be between 1 and 5.",
                ephemeral=True
            )
            return
        
        # Validate classification
        valid_classifications = ["unclassified", "restricted", "classified"]
        if classification not in valid_classifications:
            await interaction.response.send_message(
                f"❌ Invalid classification. Valid levels: {', '.join(valid_classifications)}",
                ephemeral=True
            )
            return
        
        # Finalize AAR
        aar['status'] = 'finalized'
        aar['finalized_date'] = datetime.utcnow().isoformat()
        aar['finalized_by'] = interaction.user.id
        
        if overall_rating:
            aar['overall_rating'] = overall_rating
        
        aar['classification'] = classification
        
        await self.storage.save_after_action_reports(aar_data)
        
        # Create response embed
        embed = create_embed(
            title="✅ After Action Report Finalized",
            description=f"AAR **{aar_id}** for **{aar['mission_name']}** has been finalized",
            color=Config.COLORS['success']
        )
        
        embed.add_field(name="AAR ID", value=f"`{aar_id}`", inline=True)
        embed.add_field(name="Classification", value=classification.title(), inline=True)
        
        if overall_rating:
            rating_stars = "⭐" * overall_rating
            embed.add_field(name="Overall Rating", value=f"{rating_stars} ({overall_rating}/5)", inline=True)
        
        embed.add_field(name="Finalized By", value=interaction.user.mention, inline=True)
        embed.add_field(name="Finalized Date", value=f"<t:{int(datetime.utcnow().timestamp())}:f>", inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="aar-list", description="List After Action Reports")
    @app_commands.describe(
        mission_type="Filter by mission type (optional)",
        status="Filter by status (optional)",
        limit="Number of AARs to show (default: 10)"
    )
    async def list_aars(
        self,
        interaction: discord.Interaction,
        mission_type: str = None,
        status: str = None,
        limit: int = 10
    ):
        """List AARs"""
        # Load AAR data
        aar_data = await self.storage.load_after_action_reports()
        
        if not aar_data:
            await interaction.response.send_message(
                "📋 No After Action Reports found.",
                ephemeral=True
            )
            return
        
        # Filter AARs
        filtered_aars = []
        for aar_id, aar in aar_data.items():
            # Check classification access
            if aar.get('classification') == 'classified':
                if not Config.is_omega_clearance([role.name for role in interaction.user.roles]):
                    continue
            
            if mission_type and aar['mission_type'] != mission_type:
                continue
            if status and aar['status'] != status:
                continue
            
            filtered_aars.append((aar_id, aar))
        
        # Sort by creation date (most recent first)
        filtered_aars.sort(key=lambda x: x[1]['created_date'], reverse=True)
        
        # Limit results
        filtered_aars = filtered_aars[:limit]
        
        embed = create_embed(
            title="📋 After Action Reports",
            description="Recent mission debriefings and analysis",
            color=Config.COLORS['info']
        )
        
        if not filtered_aars:
            embed.add_field(name="No Results", value="No AARs match the specified criteria.", inline=False)
        else:
            aar_list = ""
            for aar_id, aar in filtered_aars:
                status_icon = "✅" if aar['status'] == 'finalized' else "📝"
                classification_icon = "🔒" if aar.get('classification') == 'classified' else ""
                
                operation_date = aar['operation_date']
                aar_list += f"{status_icon}{classification_icon} **{aar_id}** - {aar['mission_name']} ({operation_date})\n"
                aar_list += f"   Type: {self.aar_templates[aar['mission_type']]['name']} | Status: {aar['status'].title()}\n\n"
            
            embed.add_field(name="Recent AARs", value=aar_list, inline=False)
        
        embed.add_field(name="Legend", value="✅ Finalized | 📝 Draft | 🔒 Classified", inline=False)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(AfterActionReports(bot))