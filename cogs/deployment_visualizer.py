"""
Animated Deployment Status Visualizer for Merrywinter Security Consulting
Real-time deployment tracking with animated status updates
"""

import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
import json
from datetime import datetime, timedelta
from config.settings import Config
from utils.storage import Storage
import random

class DeploymentVisualizer(commands.Cog):
    """Animated deployment status visualization system"""
    
    def __init__(self, bot):
        self.bot = bot
        self.storage = Storage()
        self.active_visualizers = {}  # Track active animated status messages
        self.animation_frames = {
            'deploying': [
                "🟢⚪⚪⚪⚪ Initiating deployment...",
                "⚪🟢⚪⚪⚪ Mobilizing units...",
                "⚪⚪🟢⚪⚪ En route to sector...",
                "⚪⚪⚪🟢⚪ Arriving at destination...",
                "⚪⚪⚪⚪🟢 Deployment complete!"
            ],
            'active': [
                "🔴⚪⚪⚪ Mission in progress...",
                "⚪🔴⚪⚪ Objectives advancing...",
                "⚪⚪🔴⚪ Status monitoring...",
                "⚪⚪⚪🔴 Operations continuing..."
            ],
            'extraction': [
                "🟡⚪⚪⚪ Preparing extraction...",
                "⚪🟡⚪⚪ Withdrawing units...",
                "⚪⚪🟡⚪ Returning to base...",
                "⚪⚪⚪🟡 Extraction complete!"
            ]
        }
        
    async def cog_load(self):
        """Start the visualizer update task"""
        self.update_visualizers.start()
        
    def cog_unload(self):
        """Stop the visualizer update task"""
        self.update_visualizers.cancel()
    
    @app_commands.command(name="deployment-visualizer", description="Create animated deployment status tracker")
    @app_commands.describe(
        deployment_id="ID of deployment to visualize",
        duration="Duration in minutes for visualization"
    )
    async def create_visualizer(self, interaction: discord.Interaction, deployment_id: str, duration: int = 30):
        """Create an animated deployment status visualizer"""
        
        # Check permissions
        user_roles = [role.name for role in interaction.user.roles]
        if not Config.is_moderator(user_roles, interaction.user.id):
            await interaction.response.send_message("❌ You need moderator permissions to create deployment visualizers.", ephemeral=True)
            return
        
        # Validate deployment exists
        deployments = await self.storage.load_deployments()
        deployment = None
        for dep in deployments:
            if dep.get('deployment_id') == deployment_id:
                deployment = dep
                break
                
        if not deployment:
            await interaction.response.send_message(f"❌ Deployment {deployment_id} not found.", ephemeral=True)
            return
        
        # Create initial visualizer embed
        embed = await self.create_deployment_embed(deployment, 'deploying', 0)
        
        await interaction.response.send_message(embed=embed)
        
        # Get the message for animation
        message = await interaction.original_response()
        
        # Store visualizer data
        visualizer_data = {
            'message': message,
            'deployment': deployment,
            'phase': 'deploying',
            'frame': 0,
            'start_time': datetime.utcnow(),
            'duration': duration,
            'channel_id': interaction.channel.id
        }
        
        self.active_visualizers[deployment_id] = visualizer_data
        
        await interaction.followup.send(f"✅ Deployment visualizer activated for {deployment_id} (Duration: {duration} minutes)", ephemeral=True)
    
    @app_commands.command(name="deployment-status", description="View current deployment statuses")
    async def deployment_status(self, interaction: discord.Interaction):
        """Display current deployment statuses"""
        
        deployments = await self.storage.load_deployments()
        active_deployments = [d for d in deployments if d.get('status') == 'deployed']
        
        if not active_deployments:
            await interaction.response.send_message("📊 No active deployments currently.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📊 ACTIVE DEPLOYMENT STATUS",
            description="Current operational deployments across all sectors",
            color=Config.COLORS['primary'],
            timestamp=datetime.utcnow()
        )
        
        for deployment in active_deployments[:10]:  # Show max 10
            deployment_id = deployment.get('deployment_id', 'Unknown')
            sector = deployment.get('sector', 'Unknown')
            units = deployment.get('units', 'Unknown')
            priority = deployment.get('priority', 'Unknown')
            timestamp = deployment.get('timestamp', '')
            
            # Calculate deployment duration
            if timestamp:
                try:
                    start_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    duration = datetime.utcnow() - start_time.replace(tzinfo=None)
                    duration_str = f"{duration.total_seconds() // 3600:.0f}h {(duration.total_seconds() % 3600) // 60:.0f}m"
                except:
                    duration_str = "Unknown"
            else:
                duration_str = "Unknown"
            
            # Status indicator based on priority
            status_emoji = {
                'critical': '🔴',
                'high': '🟠', 
                'medium': '🟡',
                'low': '🟢'
            }.get(priority.lower(), '⚪')
            
            embed.add_field(
                name=f"{status_emoji} {deployment_id}",
                value=f"**Sector:** {sector}\n**Units:** {units}\n**Duration:** {duration_str}\n**Priority:** {priority.upper()}",
                inline=True
            )
        
        embed.set_footer(text=f"F.R.O.S.T AI • {len(active_deployments)} active deployments")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="stop-visualizer", description="Stop deployment visualizer")
    @app_commands.describe(deployment_id="ID of deployment visualizer to stop")
    async def stop_visualizer(self, interaction: discord.Interaction, deployment_id: str):
        """Stop an active deployment visualizer"""
        
        user_roles = [role.name for role in interaction.user.roles]
        if not Config.is_moderator(user_roles, interaction.user.id):
            await interaction.response.send_message("❌ You need moderator permissions to stop visualizers.", ephemeral=True)
            return
        
        if deployment_id in self.active_visualizers:
            del self.active_visualizers[deployment_id]
            await interaction.response.send_message(f"✅ Stopped visualizer for deployment {deployment_id}", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ No active visualizer found for deployment {deployment_id}", ephemeral=True)
    
    async def create_deployment_embed(self, deployment, phase, frame):
        """Create animated deployment embed"""
        deployment_id = deployment.get('deployment_id', 'Unknown')
        sector = deployment.get('sector', 'Unknown')
        units = deployment.get('units', 'Unknown')
        mission_type = deployment.get('mission_type', 'Unknown')
        priority = deployment.get('priority', 'Unknown')
        
        # Phase-specific colors and titles
        phase_config = {
            'deploying': {'color': 0x00FF00, 'title': '🚁 DEPLOYMENT IN PROGRESS'},
            'active': {'color': 0xFF8C00, 'title': '⚔️ ACTIVE DEPLOYMENT'},
            'extraction': {'color': 0xFFFF00, 'title': '🔄 EXTRACTION IN PROGRESS'},
            'completed': {'color': 0x808080, 'title': '✅ DEPLOYMENT COMPLETED'}
        }
        
        config = phase_config.get(phase, phase_config['active'])
        
        embed = discord.Embed(
            title=config['title'],
            description=f"**Deployment ID:** `{deployment_id}`\n**Real-time Status Tracking**",
            color=config['color'],
            timestamp=datetime.utcnow()
        )
        
        # Add animated progress bar
        if phase in self.animation_frames and frame < len(self.animation_frames[phase]):
            progress_text = self.animation_frames[phase][frame]
        else:
            progress_text = "⚪⚪⚪⚪ Standby..."
        
        embed.add_field(
            name="📊 Progress Status",
            value=progress_text,
            inline=False
        )
        
        # Sector mapping for display
        sector_names = {
            "alpha": "Sector Alpha - Urban Operations",
            "beta": "Sector Beta - Desert Warfare", 
            "gamma": "Sector Gamma - Naval Operations",
            "delta": "Sector Delta - Mountain Warfare",
            "epsilon": "Sector Epsilon - Jungle Operations",
            "zeta": "Sector Zeta - Arctic Operations"
        }
        
        mission_names = {
            "recon": "Reconnaissance",
            "direct_action": "Direct Action",
            "security": "Security Detail",
            "convoy": "Convoy Escort",
            "defense": "Base Defense",
            "intelligence": "Intelligence Gathering"
        }
        
        embed.add_field(
            name="📋 Deployment Details",
            value=f"**Sector:** {sector_names.get(sector, sector)}\n"
                  f"**Units:** {units} personnel\n"
                  f"**Mission:** {mission_names.get(mission_type, mission_type)}\n"
                  f"**Priority:** {priority.upper()}",
            inline=True
        )
        
        # Add live metrics (simulated for realism)
        embed.add_field(
            name="📡 Live Metrics",
            value=f"**Comms Status:** {'🟢 Online' if random.random() > 0.1 else '🟡 Intermittent'}\n"
                  f"**Unit Health:** {random.randint(85, 100)}%\n"
                  f"**Objective Progress:** {min(frame * 20, 100)}%\n"
                  f"**Last Update:** {datetime.utcnow().strftime('%H:%M:%S')} UTC",
            inline=True
        )
        
        embed.set_footer(text=f"F.R.O.S.T AI Live Tracker • Auto-updating every 5 seconds")
        
        return embed
    
    @tasks.loop(seconds=5)
    async def update_visualizers(self):
        """Update all active deployment visualizers"""
        if not self.active_visualizers:
            return
        
        to_remove = []
        
        for deployment_id, visualizer in self.active_visualizers.items():
            try:
                # Check if visualizer has expired
                elapsed = datetime.utcnow() - visualizer['start_time']
                if elapsed.total_seconds() > visualizer['duration'] * 60:
                    to_remove.append(deployment_id)
                    continue
                
                # Determine current phase based on elapsed time
                total_duration = visualizer['duration'] * 60
                elapsed_seconds = elapsed.total_seconds()
                
                if elapsed_seconds < total_duration * 0.2:
                    phase = 'deploying'
                elif elapsed_seconds < total_duration * 0.8:
                    phase = 'active'
                else:
                    phase = 'extraction'
                
                # Update frame
                if phase != visualizer['phase']:
                    visualizer['phase'] = phase
                    visualizer['frame'] = 0
                else:
                    max_frames = len(self.animation_frames.get(phase, []))
                    if max_frames > 0:
                        visualizer['frame'] = (visualizer['frame'] + 1) % max_frames
                
                # Update embed
                new_embed = await self.create_deployment_embed(
                    visualizer['deployment'], 
                    visualizer['phase'], 
                    visualizer['frame']
                )
                
                # Update message
                await visualizer['message'].edit(embed=new_embed)
                
            except Exception as e:
                print(f"Error updating visualizer {deployment_id}: {e}")
                to_remove.append(deployment_id)
        
        # Remove expired or errored visualizers
        for deployment_id in to_remove:
            if deployment_id in self.active_visualizers:
                del self.active_visualizers[deployment_id]
    
    @update_visualizers.before_loop
    async def before_update_visualizers(self):
        """Wait for bot to be ready before starting updates"""
        await self.bot.wait_until_ready()

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(DeploymentVisualizer(bot))