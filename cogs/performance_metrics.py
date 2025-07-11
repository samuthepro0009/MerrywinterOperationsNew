"""
Performance Metrics Tracking for PMC Operations
Track operator performance, attendance, and achievements
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

class PerformanceMetrics(commands.Cog):
    """Performance metrics and tracking system"""
    
    def __init__(self, bot):
        self.bot = bot
        self.storage = Storage()
        self.performance_data = {}
        self.attendance_tracking = {}
        self.achievements = {}
    
    def cog_check(self, ctx):
        """Check if command is used in authorized guild"""
        return Config.check_guild_authorization(ctx.guild.id)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check if interaction is in authorized guild"""
        return Config.check_guild_authorization(interaction.guild.id)
    
    async def track_performance(self, user_id, category, metric, value=1):
        """Track performance metric for a user"""
        if user_id not in self.performance_data:
            self.performance_data[user_id] = {}
        
        if category not in self.performance_data[user_id]:
            self.performance_data[user_id][category] = {}
        
        if metric not in self.performance_data[user_id][category]:
            self.performance_data[user_id][category][metric] = 0
        
        self.performance_data[user_id][category][metric] += value
        
        # Save to storage
        await self.storage.save_performance_data(self.performance_data)
    
    async def record_attendance(self, user_id, event_type, event_name):
        """Record attendance for events"""
        if user_id not in self.attendance_tracking:
            self.attendance_tracking[user_id] = []
        
        self.attendance_tracking[user_id].append({
            'event_type': event_type,
            'event_name': event_name,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Track attendance metric
        await self.track_performance(user_id, 'reliability', 'events_attended')
        
        # Save to storage
        await self.storage.save_attendance_data(self.attendance_tracking)
    
    @app_commands.command(name="performance", description="View performance metrics")
    async def view_performance(self, interaction: discord.Interaction, user: discord.Member = None):
        """View performance metrics for a user"""
        target_user = user or interaction.user
        
        if target_user.id not in self.performance_data:
            await interaction.response.send_message(
                f"📊 No performance data found for {target_user.mention}",
                ephemeral=True
            )
            return
        
        user_data = self.performance_data[target_user.id]
        
        embed = discord.Embed(
            title=f"📊 Performance Metrics - {target_user.display_name}",
            description="**Operator Performance Analysis**",
            color=Config.COLORS['frost'],
            timestamp=datetime.utcnow()
        )
        
        # Display performance categories
        for category, metrics in user_data.items():
            if category in Config.PERFORMANCE_CATEGORIES:
                metric_text = ""
                for metric, value in metrics.items():
                    metric_text += f"• {metric.replace('_', ' ').title()}: {value}\n"
                
                embed.add_field(
                    name=f"🎯 {category.title()}",
                    value=metric_text or "No data",
                    inline=True
                )
        
        # Calculate overall performance score
        total_score = sum(sum(metrics.values()) for metrics in user_data.values())
        embed.add_field(
            name="🏆 Overall Score",
            value=f"{total_score}",
            inline=True
        )
        
        # Show recent achievements
        if target_user.id in self.achievements:
            recent_achievements = self.achievements[target_user.id][-3:]  # Last 3 achievements
            achievement_text = ""
            for achievement in recent_achievements:
                achievement_text += f"🏅 {achievement['name']}\n"
            
            if achievement_text:
                embed.add_field(
                    name="🏅 Recent Achievements",
                    value=achievement_text,
                    inline=False
                )
        
        embed.set_footer(text=f"F.R.O.S.T AI • {Config.AI_VERSION}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="leaderboard", description="View performance leaderboard")
    async def performance_leaderboard(self, interaction: discord.Interaction, category: str = None):
        """View performance leaderboard"""
        if not self.performance_data:
            await interaction.response.send_message("📊 No performance data available yet.", ephemeral=True)
            return
        
        # Calculate scores for each user
        user_scores = {}
        for user_id, data in self.performance_data.items():
            if category and category in data:
                # Category-specific leaderboard
                user_scores[user_id] = sum(data[category].values())
            else:
                # Overall leaderboard
                user_scores[user_id] = sum(sum(metrics.values()) for metrics in data.values())
        
        # Sort by score
        sorted_users = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)[:10]
        
        embed = discord.Embed(
            title=f"🏆 Performance Leaderboard{f' - {category.title()}' if category else ''}",
            description="**Top Performing Operators**",
            color=Config.COLORS['frost'],
            timestamp=datetime.utcnow()
        )
        
        leaderboard_text = ""
        for i, (user_id, score) in enumerate(sorted_users, 1):
            user = interaction.guild.get_member(user_id)
            if user:
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                leaderboard_text += f"{medal} {user.display_name}: {score}\n"
        
        embed.add_field(
            name="📊 Rankings",
            value=leaderboard_text or "No data available",
            inline=False
        )
        
        embed.set_footer(text=f"F.R.O.S.T AI • {Config.AI_VERSION}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="record-achievement", description="Record an achievement (Admin only)")
    @app_commands.describe(
        user="The user to award the achievement to",
        achievement="Name of the achievement",
        description="Description of the achievement"
    )
    async def record_achievement(self, interaction: discord.Interaction, user: discord.Member, achievement: str, description: str):
        """Record an achievement for a user"""
        # Check permissions
        if not Config.is_moderator([role.name for role in interaction.user.roles], interaction.user.id):
            await interaction.response.send_message("❌ You don't have permission to record achievements.", ephemeral=True)
            return
        
        if user.id not in self.achievements:
            self.achievements[user.id] = []
        
        self.achievements[user.id].append({
            'name': achievement,
            'description': description,
            'timestamp': datetime.utcnow().isoformat(),
            'awarded_by': interaction.user.id
        })
        
        # Track achievement metric
        await self.track_performance(user.id, 'training', 'achievements_earned')
        
        # Save to storage
        await self.storage.save_achievements(self.achievements)
        
        # Send notification
        embed = discord.Embed(
            title="🏅 Achievement Unlocked!",
            description=f"**{user.mention}** has earned a new achievement!",
            color=Config.COLORS['success'],
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="🏆 Achievement", value=achievement, inline=False)
        embed.add_field(name="📝 Description", value=description, inline=False)
        embed.add_field(name="👨‍💼 Awarded By", value=interaction.user.mention, inline=True)
        embed.set_footer(text=f"F.R.O.S.T AI • {Config.AI_VERSION}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="attendance", description="View attendance record")
    async def view_attendance(self, interaction: discord.Interaction, user: discord.Member = None):
        """View attendance record for a user"""
        target_user = user or interaction.user
        
        if target_user.id not in self.attendance_tracking:
            await interaction.response.send_message(
                f"📅 No attendance data found for {target_user.mention}",
                ephemeral=True
            )
            return
        
        attendance_data = self.attendance_tracking[target_user.id]
        
        embed = discord.Embed(
            title=f"📅 Attendance Record - {target_user.display_name}",
            description="**Event Attendance History**",
            color=Config.COLORS['info'],
            timestamp=datetime.utcnow()
        )
        
        # Show recent events
        recent_events = attendance_data[-10:]  # Last 10 events
        
        event_text = ""
        for event in recent_events:
            timestamp = datetime.fromisoformat(event['timestamp'])
            event_text += f"• {event['event_name']} ({event['event_type']}) - <t:{int(timestamp.timestamp())}:R>\n"
        
        embed.add_field(
            name="📋 Recent Events",
            value=event_text or "No events recorded",
            inline=False
        )
        
        # Calculate attendance rate
        total_events = len(attendance_data)
        embed.add_field(
            name="📊 Total Events",
            value=f"{total_events}",
            inline=True
        )
        
        embed.set_footer(text=f"F.R.O.S.T AI • {Config.AI_VERSION}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="record-event", description="Record event attendance (Admin only)")
    @app_commands.describe(
        event_type="Type of event (training, operation, meeting)",
        event_name="Name of the event",
        participants="Mention all participants"
    )
    async def record_event(self, interaction: discord.Interaction, event_type: str, event_name: str, participants: str):
        """Record event attendance"""
        # Check permissions
        if not Config.is_moderator([role.name for role in interaction.user.roles], interaction.user.id):
            await interaction.response.send_message("❌ You don't have permission to record events.", ephemeral=True)
            return
        
        # Extract user mentions
        mentioned_users = interaction.message.mentions if hasattr(interaction, 'message') else []
        
        if not mentioned_users:
            await interaction.response.send_message("❌ Please mention the participants in the event.", ephemeral=True)
            return
        
        # Record attendance for each participant
        for user in mentioned_users:
            await self.record_attendance(user.id, event_type, event_name)
        
        # Send confirmation
        embed = discord.Embed(
            title="📅 Event Recorded",
            description=f"**{event_name}** attendance has been recorded",
            color=Config.COLORS['success'],
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="📋 Event Type", value=event_type.title(), inline=True)
        embed.add_field(name="👥 Participants", value=f"{len(mentioned_users)}", inline=True)
        embed.add_field(name="📝 Recorded By", value=interaction.user.mention, inline=True)
        
        participant_list = ", ".join([user.display_name for user in mentioned_users])
        embed.add_field(name="👤 Participants", value=participant_list, inline=False)
        
        embed.set_footer(text=f"F.R.O.S.T AI • {Config.AI_VERSION}")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(PerformanceMetrics(bot))