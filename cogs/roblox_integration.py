"""
Roblox Integration for FROST AI
Connect with Roblox game servers and track player activity
"""

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import aiohttp
import json
import asyncio

from config.settings import Config
from utils.helpers import get_user_clearance, create_embed
from utils.storage import Storage

class RobloxIntegration(commands.Cog):
    """Roblox game integration system"""
    
    def __init__(self, bot):
        self.bot = bot
        self.storage = Storage()
        self.roblox_users = {}
        self.game_activity = {}
        self.session = None
    
    def cog_check(self, ctx):
        """Check if command is used in authorized guild"""
        return Config.check_guild_authorization(ctx.guild.id)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check if interaction is in authorized guild"""
        return Config.check_guild_authorization(interaction.guild.id)
    
    async def cog_load(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
    
    async def cog_unload(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def get_roblox_user_info(self, username):
        """Get Roblox user information"""
        if not self.session:
            return None
        
        try:
            # Get user by username
            async with self.session.get(f"https://api.roblox.com/users/get-by-username?username={username}") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'Id' in data:
                        user_id = data['Id']
                        
                        # Get detailed user info
                        async with self.session.get(f"https://users.roblox.com/v1/users/{user_id}") as detail_response:
                            if detail_response.status == 200:
                                detail_data = await detail_response.json()
                                return {
                                    'id': user_id,
                                    'username': detail_data.get('name', username),
                                    'display_name': detail_data.get('displayName', username),
                                    'description': detail_data.get('description', ''),
                                    'created': detail_data.get('created', ''),
                                    'is_banned': detail_data.get('isBanned', False)
                                }
        except Exception as e:
            print(f"Error getting Roblox user info: {e}")
        
        return None
    
    async def get_game_activity(self, game_id):
        """Get game activity information"""
        if not self.session:
            return None
        
        try:
            # Get game stats
            async with self.session.get(f"https://games.roblox.com/v1/games/{game_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'data' in data and len(data['data']) > 0:
                        game_data = data['data'][0]
                        return {
                            'name': game_data.get('name', 'Unknown'),
                            'description': game_data.get('description', ''),
                            'playing': game_data.get('playing', 0),
                            'visits': game_data.get('visits', 0),
                            'max_players': game_data.get('maxPlayers', 0),
                            'created': game_data.get('created', ''),
                            'updated': game_data.get('updated', '')
                        }
        except Exception as e:
            print(f"Error getting game activity: {e}")
        
        return None
    
    @app_commands.command(name="link-roblox", description="Link your Roblox account")
    @app_commands.describe(username="Your Roblox username")
    async def link_roblox(self, interaction: discord.Interaction, username: str):
        """Link a Roblox account to Discord"""
        # Get Roblox user info
        roblox_info = await self.get_roblox_user_info(username)
        
        if not roblox_info:
            await interaction.response.send_message(
                "❌ Roblox user not found. Please check the username and try again.",
                ephemeral=True
            )
            return
        
        # Store the link
        self.roblox_users[interaction.user.id] = {
            'roblox_id': roblox_info['id'],
            'roblox_username': roblox_info['username'],
            'display_name': roblox_info['display_name'],
            'linked_at': datetime.utcnow().isoformat(),
            'discord_id': interaction.user.id
        }
        
        await self.storage.save_roblox_links(self.roblox_users)
        
        # Create verification embed
        embed = discord.Embed(
            title="🔗 Roblox Account Linked",
            description=f"**{roblox_info['display_name']}** (@{roblox_info['username']}) has been linked to your Discord account.",
            color=Config.COLORS['success'],
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="🆔 Roblox ID", value=f"`{roblox_info['id']}`", inline=True)
        embed.add_field(name="📅 Account Created", value=roblox_info['created'][:10] if roblox_info['created'] else "Unknown", inline=True)
        embed.add_field(name="🚫 Banned", value="Yes" if roblox_info['is_banned'] else "No", inline=True)
        
        if roblox_info['description']:
            embed.add_field(name="📝 Description", value=roblox_info['description'][:200], inline=False)
        
        embed.set_footer(text=f"F.R.O.S.T AI • {Config.AI_VERSION}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="roblox-profile", description="View Roblox profile information")
    @app_commands.describe(user="Discord user to check (leave empty for yourself)")
    async def roblox_profile(self, interaction: discord.Interaction, user: discord.Member = None):
        """View Roblox profile information"""
        target_user = user or interaction.user
        
        if target_user.id not in self.roblox_users:
            await interaction.response.send_message(
                f"❌ No Roblox account linked for {target_user.mention}. Use `/link-roblox` to link an account.",
                ephemeral=True
            )
            return
        
        roblox_data = self.roblox_users[target_user.id]
        
        # Get fresh Roblox info
        roblox_info = await self.get_roblox_user_info(roblox_data['roblox_username'])
        
        if not roblox_info:
            await interaction.response.send_message(
                "❌ Unable to fetch Roblox profile information.",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title=f"🎮 Roblox Profile - {roblox_info['display_name']}",
            description=f"**@{roblox_info['username']}**",
            color=Config.COLORS['info'],
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="👤 Discord User", value=target_user.mention, inline=True)
        embed.add_field(name="🆔 Roblox ID", value=f"`{roblox_info['id']}`", inline=True)
        embed.add_field(name="📅 Account Created", value=roblox_info['created'][:10] if roblox_info['created'] else "Unknown", inline=True)
        
        embed.add_field(name="🔗 Linked", value=f"<t:{int(datetime.fromisoformat(roblox_data['linked_at']).timestamp())}:R>", inline=True)
        embed.add_field(name="🚫 Banned", value="Yes" if roblox_info['is_banned'] else "No", inline=True)
        embed.add_field(name="📊 Status", value="Active" if not roblox_info['is_banned'] else "Banned", inline=True)
        
        if roblox_info['description']:
            embed.add_field(name="📝 Description", value=roblox_info['description'][:200], inline=False)
        
        embed.set_footer(text=f"F.R.O.S.T AI • {Config.AI_VERSION}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="game-status", description="Check game server status")
    async def game_status(self, interaction: discord.Interaction):
        """Check game server status"""
        if not Config.ROBLOX_GAME_ID:
            await interaction.response.send_message(
                "❌ No game configured. Please contact an administrator to set up game integration.",
                ephemeral=True
            )
            return
        
        game_info = await self.get_game_activity(Config.ROBLOX_GAME_ID)
        
        if not game_info:
            await interaction.response.send_message(
                "❌ Unable to fetch game information.",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title=f"🎮 Game Status - {game_info['name']}",
            description=game_info['description'][:200] if game_info['description'] else "No description available",
            color=Config.COLORS['info'],
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="🎯 Currently Playing", value=f"{game_info['playing']:,}", inline=True)
        embed.add_field(name="👥 Max Players", value=f"{game_info['max_players']:,}", inline=True)
        embed.add_field(name="📊 Total Visits", value=f"{game_info['visits']:,}", inline=True)
        
        embed.add_field(name="📅 Created", value=game_info['created'][:10] if game_info['created'] else "Unknown", inline=True)
        embed.add_field(name="🔄 Last Updated", value=game_info['updated'][:10] if game_info['updated'] else "Unknown", inline=True)
        
        # Server status indicator
        if game_info['playing'] > 0:
            embed.add_field(name="🟢 Status", value="Online", inline=True)
        else:
            embed.add_field(name="🔴 Status", value="Offline", inline=True)
        
        embed.set_footer(text=f"F.R.O.S.T AI • {Config.AI_VERSION}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="player-activity", description="View player activity statistics")
    async def player_activity(self, interaction: discord.Interaction):
        """View player activity statistics"""
        if not self.roblox_users:
            await interaction.response.send_message(
                "📊 No linked Roblox accounts found.",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="📊 Player Activity Statistics",
            description="**Linked Roblox Accounts**",
            color=Config.COLORS['info'],
            timestamp=datetime.utcnow()
        )
        
        total_linked = len(self.roblox_users)
        active_players = 0  # This would need game API integration
        
        embed.add_field(name="🔗 Total Linked", value=f"{total_linked}", inline=True)
        embed.add_field(name="🎮 Active Players", value=f"{active_players}", inline=True)
        embed.add_field(name="📈 Activity Rate", value=f"{(active_players/total_linked*100):.1f}%" if total_linked > 0 else "0%", inline=True)
        
        # Show recent links
        recent_links = sorted(
            self.roblox_users.values(),
            key=lambda x: x['linked_at'],
            reverse=True
        )[:5]
        
        recent_text = ""
        for link in recent_links:
            discord_user = interaction.guild.get_member(link['discord_id'])
            if discord_user:
                recent_text += f"• {discord_user.display_name} → @{link['roblox_username']}\n"
        
        if recent_text:
            embed.add_field(name="🔗 Recent Links", value=recent_text, inline=False)
        
        embed.set_footer(text=f"F.R.O.S.T AI • {Config.AI_VERSION}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="unlink-roblox", description="Unlink your Roblox account")
    async def unlink_roblox(self, interaction: discord.Interaction):
        """Unlink Roblox account"""
        if interaction.user.id not in self.roblox_users:
            await interaction.response.send_message(
                "❌ No Roblox account linked to your Discord account.",
                ephemeral=True
            )
            return
        
        roblox_data = self.roblox_users[interaction.user.id]
        del self.roblox_users[interaction.user.id]
        
        await self.storage.save_roblox_links(self.roblox_users)
        
        await interaction.response.send_message(
            f"✅ Roblox account **@{roblox_data['roblox_username']}** has been unlinked from your Discord account.",
            ephemeral=True
        )
    
    @app_commands.command(name="configure-game", description="Configure game integration (Admin only)")
    @app_commands.describe(game_id="Roblox game ID")
    async def configure_game(self, interaction: discord.Interaction, game_id: str):
        """Configure game integration"""
        # Check permissions
        if not Config.is_moderator([role.name for role in interaction.user.roles], interaction.user.id):
            await interaction.response.send_message("❌ You don't have permission to configure game integration.", ephemeral=True)
            return
        
        # Validate game ID
        try:
            game_id_int = int(game_id)
        except ValueError:
            await interaction.response.send_message("❌ Invalid game ID. Please provide a valid Roblox game ID.", ephemeral=True)
            return
        
        # Test game access
        game_info = await self.get_game_activity(game_id_int)
        
        if not game_info:
            await interaction.response.send_message(
                "❌ Unable to access game information. Please check the game ID and try again.",
                ephemeral=True
            )
            return
        
        # Update configuration (this would need to be saved to a config file)
        Config.ROBLOX_GAME_ID = game_id_int
        
        embed = discord.Embed(
            title="🎮 Game Integration Configured",
            description=f"**{game_info['name']}** has been configured for integration.",
            color=Config.COLORS['success'],
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="🆔 Game ID", value=f"`{game_id_int}`", inline=True)
        embed.add_field(name="🎯 Currently Playing", value=f"{game_info['playing']:,}", inline=True)
        embed.add_field(name="👥 Max Players", value=f"{game_info['max_players']:,}", inline=True)
        
        embed.set_footer(text=f"F.R.O.S.T AI • {Config.AI_VERSION}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(RobloxIntegration(bot))