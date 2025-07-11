"""
Training Schedule System for PMC Operations
Automated training session scheduling and management
"""

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import json
import asyncio

from config.settings import Config
from utils.helpers import get_user_clearance, create_embed
from utils.storage import Storage

class TrainingSchedule(commands.Cog):
    """Training schedule management system"""
    
    def __init__(self, bot):
        self.bot = bot
        self.storage = Storage()
        self.scheduled_training = {}
        self.training_history = {}
    
    def cog_check(self, ctx):
        """Check if command is used in authorized guild"""
        return Config.check_guild_authorization(ctx.guild.id)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check if interaction is in authorized guild"""
        return Config.check_guild_authorization(interaction.guild.id)
    
    @app_commands.command(name="schedule-training", description="Schedule a training session (Admin only)")
    @app_commands.describe(
        training_type="Type of training (basic, advanced, specialized, command)",
        date="Date for training (YYYY-MM-DD)",
        time="Time for training (HH:MM)",
        instructor="Training instructor",
        description="Training description"
    )
    async def schedule_training(self, interaction: discord.Interaction, training_type: str, date: str, time: str, instructor: discord.Member, description: str):
        """Schedule a training session"""
        # Check permissions
        if not Config.is_moderator([role.name for role in interaction.user.roles], interaction.user.id):
            await interaction.response.send_message("❌ You don't have permission to schedule training.", ephemeral=True)
            return
        
        # Validate training type
        if training_type not in Config.TRAINING_TYPES:
            await interaction.response.send_message(
                f"❌ Invalid training type. Valid types: {', '.join(Config.TRAINING_TYPES.keys())}",
                ephemeral=True
            )
            return
        
        # Parse date and time
        try:
            training_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        except ValueError:
            await interaction.response.send_message(
                "❌ Invalid date/time format. Use YYYY-MM-DD for date and HH:MM for time.",
                ephemeral=True
            )
            return
        
        # Check if training is in the future
        if training_datetime <= datetime.utcnow():
            await interaction.response.send_message("❌ Training must be scheduled for a future date/time.", ephemeral=True)
            return
        
        # Generate training ID
        training_id = f"training_{int(training_datetime.timestamp())}"
        
        # Get training configuration
        training_config = Config.TRAINING_TYPES[training_type]
        
        # Create training session
        training_session = {
            'id': training_id,
            'type': training_type,
            'datetime': training_datetime.isoformat(),
            'instructor': instructor.id,
            'description': description,
            'duration': training_config['duration'],
            'max_participants': training_config['max_participants'],
            'requirements': training_config['requirements'],
            'participants': [],
            'created_by': interaction.user.id,
            'created_at': datetime.utcnow().isoformat(),
            'status': 'scheduled'
        }
        
        self.scheduled_training[training_id] = training_session
        await self.storage.save_training_schedule(self.scheduled_training)
        
        # Create announcement embed
        embed = discord.Embed(
            title="🎓 Training Session Scheduled",
            description=f"**{training_type.title()} Training**",
            color=Config.COLORS['info'],
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="📅 Date & Time", value=f"<t:{int(training_datetime.timestamp())}:F>", inline=False)
        embed.add_field(name="👨‍🏫 Instructor", value=instructor.mention, inline=True)
        embed.add_field(name="⏱️ Duration", value=f"{training_config['duration']} minutes", inline=True)
        embed.add_field(name="👥 Max Participants", value=f"{training_config['max_participants']}", inline=True)
        embed.add_field(name="📝 Description", value=description, inline=False)
        
        # Requirements
        requirements_text = ", ".join(training_config['requirements'])
        embed.add_field(name="🎯 Requirements", value=requirements_text, inline=False)
        
        embed.add_field(name="🆔 Training ID", value=f"`{training_id}`", inline=False)
        embed.add_field(name="📋 Sign Up", value="Use `/join-training` to participate", inline=False)
        
        embed.set_footer(text=f"F.R.O.S.T AI • {Config.AI_VERSION}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="join-training", description="Join a training session")
    @app_commands.describe(training_id="Training session ID")
    async def join_training(self, interaction: discord.Interaction, training_id: str):
        """Join a training session"""
        if training_id not in self.scheduled_training:
            await interaction.response.send_message("❌ Training session not found.", ephemeral=True)
            return
        
        training = self.scheduled_training[training_id]
        
        # Check if training is still open
        if training['status'] != 'scheduled':
            await interaction.response.send_message("❌ This training session is no longer available.", ephemeral=True)
            return
        
        # Check if user already joined
        if interaction.user.id in training['participants']:
            await interaction.response.send_message("❌ You are already registered for this training.", ephemeral=True)
            return
        
        # Check if training is full
        if len(training['participants']) >= training['max_participants']:
            await interaction.response.send_message("❌ This training session is full.", ephemeral=True)
            return
        
        # Check requirements
        user_clearance = get_user_clearance(interaction.user.roles)
        if not any(req in [user_clearance] + [role.name for role in interaction.user.roles] for req in training['requirements']):
            await interaction.response.send_message(
                f"❌ You don't meet the requirements for this training. Required: {', '.join(training['requirements'])}",
                ephemeral=True
            )
            return
        
        # Check if training is in the past
        training_datetime = datetime.fromisoformat(training['datetime'])
        if training_datetime <= datetime.utcnow():
            await interaction.response.send_message("❌ This training session has already passed.", ephemeral=True)
            return
        
        # Add user to training
        training['participants'].append(interaction.user.id)
        await self.storage.save_training_schedule(self.scheduled_training)
        
        # Send confirmation
        embed = discord.Embed(
            title="✅ Training Registration Confirmed",
            description=f"You have successfully registered for **{training['type'].title()} Training**",
            color=Config.COLORS['success'],
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="📅 Date & Time", value=f"<t:{int(training_datetime.timestamp())}:F>", inline=False)
        embed.add_field(name="👨‍🏫 Instructor", value=f"<@{training['instructor']}>", inline=True)
        embed.add_field(name="⏱️ Duration", value=f"{training['duration']} minutes", inline=True)
        embed.add_field(name="👥 Participants", value=f"{len(training['participants'])}/{training['max_participants']}", inline=True)
        embed.add_field(name="🆔 Training ID", value=f"`{training_id}`", inline=False)
        
        embed.set_footer(text=f"F.R.O.S.T AI • {Config.AI_VERSION}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="leave-training", description="Leave a training session")
    @app_commands.describe(training_id="Training session ID")
    async def leave_training(self, interaction: discord.Interaction, training_id: str):
        """Leave a training session"""
        if training_id not in self.scheduled_training:
            await interaction.response.send_message("❌ Training session not found.", ephemeral=True)
            return
        
        training = self.scheduled_training[training_id]
        
        # Check if user is registered
        if interaction.user.id not in training['participants']:
            await interaction.response.send_message("❌ You are not registered for this training.", ephemeral=True)
            return
        
        # Remove user from training
        training['participants'].remove(interaction.user.id)
        await self.storage.save_training_schedule(self.scheduled_training)
        
        await interaction.response.send_message(
            f"✅ You have been removed from **{training['type'].title()} Training**",
            ephemeral=True
        )
    
    @app_commands.command(name="training-schedule", description="View upcoming training sessions")
    async def view_training_schedule(self, interaction: discord.Interaction):
        """View upcoming training sessions"""
        if not self.scheduled_training:
            await interaction.response.send_message("📅 No training sessions scheduled.", ephemeral=True)
            return
        
        # Filter upcoming trainings
        current_time = datetime.utcnow()
        upcoming_trainings = []
        
        for training_id, training in self.scheduled_training.items():
            training_datetime = datetime.fromisoformat(training['datetime'])
            if training_datetime > current_time and training['status'] == 'scheduled':
                upcoming_trainings.append((training_id, training, training_datetime))
        
        # Sort by date
        upcoming_trainings.sort(key=lambda x: x[2])
        
        if not upcoming_trainings:
            await interaction.response.send_message("📅 No upcoming training sessions.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🎓 Upcoming Training Sessions",
            description="**PMC Training Schedule**",
            color=Config.COLORS['info'],
            timestamp=datetime.utcnow()
        )
        
        for training_id, training, training_datetime in upcoming_trainings[:5]:  # Show first 5
            instructor = interaction.guild.get_member(training['instructor'])
            instructor_name = instructor.display_name if instructor else "Unknown"
            
            embed.add_field(
                name=f"📋 {training['type'].title()} Training",
                value=f"**Date:** <t:{int(training_datetime.timestamp())}:F>\n"
                      f"**Instructor:** {instructor_name}\n"
                      f"**Duration:** {training['duration']} minutes\n"
                      f"**Participants:** {len(training['participants'])}/{training['max_participants']}\n"
                      f"**ID:** `{training_id}`",
                inline=False
            )
        
        embed.set_footer(text=f"F.R.O.S.T AI • {Config.AI_VERSION}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="training-details", description="View training session details")
    @app_commands.describe(training_id="Training session ID")
    async def training_details(self, interaction: discord.Interaction, training_id: str):
        """View detailed information about a training session"""
        if training_id not in self.scheduled_training:
            await interaction.response.send_message("❌ Training session not found.", ephemeral=True)
            return
        
        training = self.scheduled_training[training_id]
        training_datetime = datetime.fromisoformat(training['datetime'])
        
        embed = discord.Embed(
            title=f"🎓 {training['type'].title()} Training Details",
            description=training['description'],
            color=Config.COLORS['info'],
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="📅 Date & Time", value=f"<t:{int(training_datetime.timestamp())}:F>", inline=False)
        
        instructor = interaction.guild.get_member(training['instructor'])
        embed.add_field(name="👨‍🏫 Instructor", value=instructor.mention if instructor else "Unknown", inline=True)
        embed.add_field(name="⏱️ Duration", value=f"{training['duration']} minutes", inline=True)
        embed.add_field(name="📊 Status", value=training['status'].title(), inline=True)
        
        embed.add_field(name="👥 Participants", value=f"{len(training['participants'])}/{training['max_participants']}", inline=True)
        embed.add_field(name="🎯 Requirements", value=", ".join(training['requirements']), inline=True)
        embed.add_field(name="🆔 Training ID", value=f"`{training_id}`", inline=True)
        
        # List participants
        if training['participants']:
            participants_list = []
            for participant_id in training['participants']:
                participant = interaction.guild.get_member(participant_id)
                if participant:
                    participants_list.append(participant.display_name)
            
            if participants_list:
                embed.add_field(
                    name="📋 Registered Participants",
                    value=", ".join(participants_list),
                    inline=False
                )
        
        embed.set_footer(text=f"F.R.O.S.T AI • {Config.AI_VERSION}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="cancel-training", description="Cancel a training session (Admin only)")
    @app_commands.describe(training_id="Training session ID")
    async def cancel_training(self, interaction: discord.Interaction, training_id: str):
        """Cancel a training session"""
        # Check permissions
        if not Config.is_moderator([role.name for role in interaction.user.roles], interaction.user.id):
            await interaction.response.send_message("❌ You don't have permission to cancel training.", ephemeral=True)
            return
        
        if training_id not in self.scheduled_training:
            await interaction.response.send_message("❌ Training session not found.", ephemeral=True)
            return
        
        training = self.scheduled_training[training_id]
        training['status'] = 'cancelled'
        
        await self.storage.save_training_schedule(self.scheduled_training)
        
        # Notify participants
        if training['participants']:
            embed = discord.Embed(
                title="❌ Training Session Cancelled",
                description=f"**{training['type'].title()} Training** has been cancelled",
                color=Config.COLORS['error'],
                timestamp=datetime.utcnow()
            )
            
            training_datetime = datetime.fromisoformat(training['datetime'])
            embed.add_field(name="📅 Was Scheduled For", value=f"<t:{int(training_datetime.timestamp())}:F>", inline=False)
            embed.add_field(name="🆔 Training ID", value=f"`{training_id}`", inline=False)
            embed.set_footer(text=f"F.R.O.S.T AI • {Config.AI_VERSION}")
            
            # Send notification to participants
            for participant_id in training['participants']:
                participant = interaction.guild.get_member(participant_id)
                if participant:
                    try:
                        await participant.send(embed=embed)
                    except:
                        pass  # Ignore if can't send DM
        
        await interaction.response.send_message(
            f"✅ Training session **{training['type'].title()}** has been cancelled.",
            ephemeral=True
        )

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(TrainingSchedule(bot))