"""
Training Progress Tracker for FROST AI
Monitor individual skill development and training completion
"""

import discord
from discord.ext import commands
from discord import app_commands
import json
from datetime import datetime, timedelta
from config.settings import Config
from utils.helpers import create_embed
from utils.storage import Storage

class TrainingProgress(commands.Cog):
    """Training progress tracking and skill development system"""
    
    def __init__(self, bot):
        self.bot = bot
        self.storage = Storage()
        
        # Training categories and skills
        self.training_categories = {
            'combat': {
                'name': 'Combat Operations',
                'skills': ['marksmanship', 'cqc', 'explosives', 'tactical_movement', 'urban_warfare']
            },
            'medical': {
                'name': 'Medical Training',
                'skills': ['first_aid', 'field_medicine', 'trauma_care', 'medic_certification', 'combat_medic']
            },
            'technical': {
                'name': 'Technical Operations',
                'skills': ['electronics', 'hacking', 'demolitions', 'communications', 'engineering']
            },
            'leadership': {
                'name': 'Leadership Development',
                'skills': ['squad_leadership', 'mission_planning', 'team_coordination', 'strategic_thinking', 'command_training']
            },
            'specialized': {
                'name': 'Specialized Training',
                'skills': ['sniper_training', 'pilot_training', 'recon_ops', 'intel_analysis', 'cyber_warfare']
            }
        }
        
    def cog_check(self, ctx):
        """Check if command is used in authorized guild"""
        return Config.check_guild_authorization(ctx.guild.id)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check if interaction is in authorized guild"""
        return Config.check_guild_authorization(interaction.guild.id)
    
    @app_commands.command(name="training-record", description="Record training completion for an operator")
    @app_commands.describe(
        operator="Operator who completed training",
        category="Training category",
        skill="Specific skill trained",
        level="Skill level achieved (1-5)",
        instructor="Training instructor",
        notes="Additional notes"
    )
    async def record_training(
        self,
        interaction: discord.Interaction,
        operator: discord.Member,
        category: str,
        skill: str,
        level: int,
        instructor: discord.Member = None,
        notes: str = None
    ):
        """Record training completion"""
        # Check permissions
        if not Config.is_moderator([role.name for role in interaction.user.roles], interaction.user.id):
            await interaction.response.send_message(
                "❌ Access denied. Instructor permissions required.",
                ephemeral=True
            )
            return
        
        # Validate inputs
        if category not in self.training_categories:
            valid_categories = ", ".join(self.training_categories.keys())
            await interaction.response.send_message(
                f"❌ Invalid category. Valid categories: {valid_categories}",
                ephemeral=True
            )
            return
        
        if skill not in self.training_categories[category]['skills']:
            valid_skills = ", ".join(self.training_categories[category]['skills'])
            await interaction.response.send_message(
                f"❌ Invalid skill for {category}. Valid skills: {valid_skills}",
                ephemeral=True
            )
            return
        
        if not 1 <= level <= 5:
            await interaction.response.send_message(
                "❌ Skill level must be between 1 and 5.",
                ephemeral=True
            )
            return
        
        # Load training data
        training_data = await self.storage.load_training_progress()
        
        if str(operator.id) not in training_data:
            training_data[str(operator.id)] = {
                'operator_name': operator.display_name,
                'operator_id': operator.id,
                'training_records': {},
                'certifications': [],
                'total_training_hours': 0,
                'created_date': datetime.utcnow().isoformat()
            }
        
        operator_data = training_data[str(operator.id)]
        
        # Initialize category if needed
        if category not in operator_data['training_records']:
            operator_data['training_records'][category] = {}
        
        # Record training
        training_entry = {
            'skill': skill,
            'level': level,
            'instructor_id': instructor.id if instructor else interaction.user.id,
            'instructor_name': instructor.display_name if instructor else interaction.user.display_name,
            'recorded_by': interaction.user.id,
            'date_completed': datetime.utcnow().isoformat(),
            'notes': notes,
            'previous_level': operator_data['training_records'][category].get(skill, {}).get('level', 0)
        }
        
        operator_data['training_records'][category][skill] = training_entry
        operator_data['total_training_hours'] += 2  # Assume 2 hours per training session
        
        # Check for certifications
        await self._check_certifications(operator_data, category)
        
        await self.storage.save_training_progress(training_data)
        
        # Create response embed
        level_names = ["Untrained", "Novice", "Competent", "Proficient", "Expert", "Master"]
        improvement = level - training_entry['previous_level']
        
        embed = create_embed(
            title="🎓 Training Record Updated",
            description=f"Training completed for **{operator.display_name}**",
            color=Config.COLORS['success']
        )
        
        embed.add_field(name="Category", value=self.training_categories[category]['name'], inline=True)
        embed.add_field(name="Skill", value=skill.replace('_', ' ').title(), inline=True)
        embed.add_field(name="Level", value=f"{level}/5 ({level_names[level]})", inline=True)
        embed.add_field(name="Instructor", value=instructor.mention if instructor else interaction.user.mention, inline=True)
        
        if improvement > 0:
            embed.add_field(name="Improvement", value=f"+{improvement} level{'s' if improvement > 1 else ''}", inline=True)
        
        embed.add_field(name="Total Training Hours", value=f"{operator_data['total_training_hours']} hours", inline=True)
        
        if notes:
            embed.add_field(name="Notes", value=notes, inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    async def _check_certifications(self, operator_data, category):
        """Check if operator qualifies for new certifications"""
        category_skills = self.training_categories[category]['skills']
        category_records = operator_data['training_records'].get(category, {})
        
        # Check if all skills in category are at least level 3
        if all(category_records.get(skill, {}).get('level', 0) >= 3 for skill in category_skills):
            cert_name = f"{category}_certified"
            if cert_name not in operator_data['certifications']:
                operator_data['certifications'].append({
                    'name': cert_name,
                    'display_name': f"{self.training_categories[category]['name']} Certified",
                    'earned_date': datetime.utcnow().isoformat()
                })
        
        # Check for master certification (all skills level 5)
        if all(category_records.get(skill, {}).get('level', 0) >= 5 for skill in category_skills):
            master_cert = f"{category}_master"
            if master_cert not in [c['name'] for c in operator_data['certifications']]:
                operator_data['certifications'].append({
                    'name': master_cert,
                    'display_name': f"{self.training_categories[category]['name']} Master",
                    'earned_date': datetime.utcnow().isoformat()
                })
    
    @app_commands.command(name="training-progress", description="View training progress for an operator")
    @app_commands.describe(
        operator="Operator to view progress for (defaults to yourself)",
        category="Specific category to view (optional)"
    )
    async def view_progress(
        self,
        interaction: discord.Interaction,
        operator: discord.Member = None,
        category: str = None
    ):
        """View training progress"""
        target_operator = operator or interaction.user
        
        # Load training data
        training_data = await self.storage.load_training_progress()
        
        if str(target_operator.id) not in training_data:
            await interaction.response.send_message(
                f"📋 No training records found for {target_operator.display_name}.",
                ephemeral=True
            )
            return
        
        operator_data = training_data[str(target_operator.id)]
        
        # If specific category requested
        if category:
            if category not in self.training_categories:
                valid_categories = ", ".join(self.training_categories.keys())
                await interaction.response.send_message(
                    f"❌ Invalid category. Valid categories: {valid_categories}",
                    ephemeral=True
                )
                return
            
            embed = create_embed(
                title=f"🎓 {self.training_categories[category]['name']} Progress",
                description=f"Training progress for **{target_operator.display_name}**",
                color=Config.COLORS['info']
            )
            
            category_records = operator_data['training_records'].get(category, {})
            level_names = ["❌", "🥉", "🥈", "🥇", "⭐", "🏆"]
            
            skills_text = ""
            for skill in self.training_categories[category]['skills']:
                level = category_records.get(skill, {}).get('level', 0)
                skills_text += f"{level_names[level]} **{skill.replace('_', ' ').title()}** - Level {level}/5\n"
            
            embed.add_field(name="Skills", value=skills_text, inline=False)
            
            # Show recent training in this category
            recent_training = []
            for skill, record in category_records.items():
                recent_training.append((skill, record))
            
            recent_training.sort(key=lambda x: x[1]['date_completed'], reverse=True)
            
            if recent_training:
                recent_text = ""
                for skill, record in recent_training[:3]:
                    date = datetime.fromisoformat(record['date_completed'])
                    recent_text += f"**{skill.replace('_', ' ').title()}** - Level {record['level']} (<t:{int(date.timestamp())}:R>)\n"
                
                embed.add_field(name="Recent Training", value=recent_text, inline=False)
            
            await interaction.response.send_message(embed=embed)
            return
        
        # General progress overview
        embed = create_embed(
            title=f"🎓 Training Progress Overview",
            description=f"Complete training summary for **{target_operator.display_name}**",
            color=Config.COLORS['info']
        )
        
        # Overall stats
        total_skills = sum(len(cat['skills']) for cat in self.training_categories.values())
        trained_skills = 0
        total_level = 0
        
        for cat_name, cat_records in operator_data['training_records'].items():
            for skill, record in cat_records.items():
                if record['level'] > 0:
                    trained_skills += 1
                    total_level += record['level']
        
        avg_level = total_level / trained_skills if trained_skills > 0 else 0
        completion_rate = (trained_skills / total_skills * 100) if total_skills > 0 else 0
        
        embed.add_field(name="Overall Progress", value=f"{completion_rate:.1f}% ({trained_skills}/{total_skills} skills)", inline=True)
        embed.add_field(name="Average Level", value=f"{avg_level:.1f}/5", inline=True)
        embed.add_field(name="Training Hours", value=f"{operator_data['total_training_hours']} hours", inline=True)
        
        # Category breakdown
        category_text = ""
        for cat_name, cat_data in self.training_categories.items():
            cat_records = operator_data['training_records'].get(cat_name, {})
            cat_trained = len([s for s in cat_data['skills'] if cat_records.get(s, {}).get('level', 0) > 0])
            cat_total = len(cat_data['skills'])
            cat_percentage = (cat_trained / cat_total * 100) if cat_total > 0 else 0
            
            category_text += f"**{cat_data['name']}:** {cat_percentage:.0f}% ({cat_trained}/{cat_total})\n"
        
        embed.add_field(name="Category Progress", value=category_text, inline=False)
        
        # Certifications
        if operator_data['certifications']:
            cert_text = ""
            for cert in operator_data['certifications']:
                earned_date = datetime.fromisoformat(cert['earned_date'])
                cert_text += f"🏅 **{cert['display_name']}** - <t:{int(earned_date.timestamp())}:d>\n"
            
            embed.add_field(name="Certifications", value=cert_text, inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="training-leaderboard", description="View training leaderboard")
    @app_commands.describe(
        category="Category to rank by (optional)",
        metric="Metric to rank by (hours, skills, level)"
    )
    async def training_leaderboard(
        self,
        interaction: discord.Interaction,
        category: str = None,
        metric: str = "hours"
    ):
        """View training leaderboard"""
        training_data = await self.storage.load_training_progress()
        
        if not training_data:
            await interaction.response.send_message(
                "📋 No training data available.",
                ephemeral=True
            )
            return
        
        # Calculate rankings
        rankings = []
        
        for operator_id, operator_data in training_data.items():
            operator = interaction.guild.get_member(int(operator_id))
            if not operator:
                continue
            
            if category and category in self.training_categories:
                # Category-specific ranking
                cat_records = operator_data['training_records'].get(category, {})
                if metric == "skills":
                    score = len([s for s in cat_records.values() if s.get('level', 0) > 0])
                elif metric == "level":
                    score = sum(s.get('level', 0) for s in cat_records.values())
                else:  # hours - approximate based on completed training
                    score = len(cat_records) * 2
            else:
                # Overall ranking
                if metric == "hours":
                    score = operator_data['total_training_hours']
                elif metric == "skills":
                    score = sum(
                        len([s for s in cat_records.values() if s.get('level', 0) > 0])
                        for cat_records in operator_data['training_records'].values()
                    )
                elif metric == "level":
                    score = sum(
                        sum(s.get('level', 0) for s in cat_records.values())
                        for cat_records in operator_data['training_records'].values()
                    )
                else:
                    score = operator_data['total_training_hours']
            
            rankings.append((operator, score))
        
        # Sort by score (highest first)
        rankings.sort(key=lambda x: x[1], reverse=True)
        
        # Create leaderboard embed
        title = f"🏆 Training Leaderboard"
        if category:
            title += f" - {self.training_categories[category]['name']}"
        title += f" ({metric.title()})"
        
        embed = create_embed(
            title=title,
            description="Top performers in training and development",
            color=Config.COLORS['frost']
        )
        
        # Show top 10
        leaderboard_text = ""
        for i, (operator, score) in enumerate(rankings[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"**{i}.**"
            
            if metric == "hours":
                score_text = f"{score} hours"
            elif metric == "skills":
                score_text = f"{score} skills"
            elif metric == "level":
                score_text = f"{score} total levels"
            else:
                score_text = str(score)
            
            leaderboard_text += f"{medal} {operator.display_name} - {score_text}\n"
        
        embed.add_field(name="Rankings", value=leaderboard_text or "No data available", inline=False)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(TrainingProgress(bot))