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
    
    async def get_game_servers(self, universe_id):
        """Get active game servers"""
        if not self.session:
            return []
        
        try:
            url = f"{Config.ROBLOX_GAMES_API}/v1/games/{universe_id}/servers/Public"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('data', [])
        except Exception as e:
            print(f"Error getting game servers: {e}")
        
        return []
    
    async def get_group_info(self, group_id):
        """Get Roblox group information"""
        if not self.session:
            return None
        
        try:
            url = f"{Config.ROBLOX_GROUPS_API}/v1/groups/{group_id}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
        except Exception as e:
            print(f"Error getting group info: {e}")
        
        return None
    
    async def get_user_group_role(self, user_id, group_id):
        """Get user's role in a Roblox group"""
        if not self.session:
            return None
        
        try:
            url = f"{Config.ROBLOX_GROUPS_API}/v2/users/{user_id}/groups/roles"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    for group_data in data.get('data', []):
                        if group_data.get('group', {}).get('id') == group_id:
                            return group_data.get('role', {})
        except Exception as e:
            print(f"Error getting user group role: {e}")
        
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
        embed = create_embed(
            title="🎮 Roblox Account Linked Successfully",
            description=f"Successfully linked to **{roblox_info['username']}**",
            color=Config.COLORS['success']
        )
        embed.add_field(name="Roblox User ID", value=roblox_info['id'], inline=True)
        embed.add_field(name="Display Name", value=roblox_info['display_name'], inline=True)
        embed.add_field(name="Account Age", value=roblox_info['created'][:10] if roblox_info['created'] else 'Unknown', inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="roblox-profile", description="View linked Roblox profile")
    @app_commands.describe(user="User to check (optional)")
    async def roblox_profile(self, interaction: discord.Interaction, user: discord.Member = None):
        """View a user's linked Roblox profile"""
        target_user = user or interaction.user
        
        # Load saved links
        saved_links = await self.storage.load_roblox_links()
        
        if target_user.id not in saved_links:
            await interaction.response.send_message(
                f"❌ {target_user.display_name} has not linked a Roblox account.",
                ephemeral=True
            )
            return
        
        roblox_data = saved_links[target_user.id]
        
        # Get fresh Roblox data
        fresh_info = await self.get_roblox_user_info(roblox_data['roblox_username'])
        
        if not fresh_info:
            await interaction.response.send_message(
                "❌ Unable to fetch current Roblox data. Account may have been deleted or renamed.",
                ephemeral=True
            )
            return
        
        # Check group membership if configured
        group_role = None
        if Config.ROBLOX_GROUP_ID:
            group_role = await self.get_user_group_role(fresh_info['id'], Config.ROBLOX_GROUP_ID)
        
        embed = create_embed(
            title=f"🎮 Roblox Profile: {fresh_info['username']}",
            description=fresh_info.get('description', 'No description available'),
            color=Config.COLORS['info']
        )
        
        embed.add_field(name="Username", value=fresh_info['username'], inline=True)
        embed.add_field(name="Display Name", value=fresh_info['display_name'], inline=True)
        embed.add_field(name="User ID", value=fresh_info['id'], inline=True)
        
        if group_role:
            embed.add_field(name="PMC Rank", value=group_role.get('name', 'Unknown'), inline=True)
            embed.add_field(name="Group Role ID", value=group_role.get('rank', 'N/A'), inline=True)
        
        embed.add_field(name="Account Created", value=fresh_info['created'][:10] if fresh_info['created'] else 'Unknown', inline=True)
        embed.add_field(name="Linked Since", value=roblox_data['linked_at'][:10], inline=True)
        
        if fresh_info['is_banned']:
            embed.add_field(name="⚠️ Status", value="**BANNED**", inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="game-status", description="Check PMC game server status")
    async def game_status(self, interaction: discord.Interaction):
        """Check the status of PMC game servers"""
        if not Config.ROBLOX_UNIVERSE_ID:
            await interaction.response.send_message(
                "❌ Game server monitoring not configured. Contact administrators.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        # Get game activity
        game_activity = await self.get_game_activity(Config.ROBLOX_UNIVERSE_ID)
        servers = await self.get_game_servers(Config.ROBLOX_UNIVERSE_ID)
        
        if not game_activity:
            await interaction.followup.send(
                "❌ Unable to fetch game status. Service may be temporarily unavailable.",
                ephemeral=True
            )
            return
        
        embed = create_embed(
            title="🎮 PMC Game Server Status",
            description=f"**{game_activity['name']}**",
            color=Config.COLORS['frost']
        )
        
        embed.add_field(name="Players Online", value=f"{game_activity['playing']:,}", inline=True)
        embed.add_field(name="Total Visits", value=f"{game_activity['visits']:,}", inline=True)
        embed.add_field(name="Max Players", value=f"{game_activity['max_players']:,}", inline=True)
        
        if servers:
            active_servers = len(servers)
            total_players_in_servers = sum(server.get('playing', 0) for server in servers)
            embed.add_field(name="Active Servers", value=f"{active_servers}", inline=True)
            embed.add_field(name="Players in Servers", value=f"{total_players_in_servers}", inline=True)
        
        embed.add_field(name="Last Updated", value=game_activity['updated'][:16] if game_activity['updated'] else 'Unknown', inline=True)
        
        # Add server list if available
        if servers and len(servers) <= 10:  # Limit to prevent embed from being too large
            server_list = []
            for i, server in enumerate(servers[:5], 1):  # Show top 5 servers
                server_list.append(f"**Server {i}:** {server.get('playing', 0)}/{server.get('maxPlayers', 0)} players")
            
            if server_list:
                embed.add_field(name="Active Servers (Top 5)", value="\n".join(server_list), inline=False)
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="unlink-roblox", description="Unlink your Roblox account")
    async def unlink_roblox(self, interaction: discord.Interaction):
        """Unlink Roblox account from Discord"""
        saved_links = await self.storage.load_roblox_links()
        
        if interaction.user.id not in saved_links:
            await interaction.response.send_message(
                "❌ You don't have a linked Roblox account.",
                ephemeral=True
            )
            return
        
        # Remove the link
        del saved_links[interaction.user.id]
        await self.storage.save_roblox_links(saved_links)
        
        embed = create_embed(
            title="🔗 Roblox Account Unlinked",
            description="Your Roblox account has been successfully unlinked from Discord.",
            color=Config.COLORS['warning']
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="pmc-roster", description="View PMC group roster (Admin only)")
    @app_commands.describe(
        role_filter="Filter by specific role name (optional)",
        limit="Maximum number of members to show (default: 50)"
    )
    async def pmc_roster(self, interaction: discord.Interaction, role_filter: str = None, limit: int = 50):
        """View PMC group roster from Roblox"""
        # Check permissions
        user_clearance = get_user_clearance(interaction.user)
        if user_clearance not in ['OMEGA', 'BETA'] and not Config.is_moderator([role.name for role in interaction.user.roles], interaction.user.id):
            await interaction.response.send_message(
                "❌ Access denied. BETA clearance or higher required.",
                ephemeral=True
            )
            return
        
        if not Config.ROBLOX_GROUP_ID:
            await interaction.response.send_message(
                "❌ PMC group not configured. Contact administrators.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        # Get group info
        group_info = await self.get_group_info(Config.ROBLOX_GROUP_ID)
        
        if not group_info:
            await interaction.followup.send(
                "❌ Unable to fetch PMC group data.",
                ephemeral=True
            )
            return
        
        embed = create_embed(
            title=f"🏛️ {group_info.get('name', 'PMC')} Roster",
            description=f"**Members:** {group_info.get('memberCount', 0):,}",
            color=Config.COLORS['frost']
        )
        
        embed.add_field(name="Group ID", value=Config.ROBLOX_GROUP_ID, inline=True)
        embed.add_field(name="Owner", value=group_info.get('owner', {}).get('username', 'Unknown'), inline=True)
        embed.add_field(name="Public Entry", value="Yes" if group_info.get('publicEntryAllowed') else "No", inline=True)
        
        if group_info.get('description'):
            embed.add_field(name="Description", value=group_info['description'][:200] + ("..." if len(group_info['description']) > 200 else ""), inline=False)
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(RobloxIntegration(bot))