"""
Script to get ALL roles and channels from the guild and update settings.py
"""

import discord
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

class GuildRolesBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.members = True
        super().__init__(intents=intents)
        
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        
        # Get the guild
        guild_id = 1114936846124843008
        guild = self.get_guild(guild_id)
        
        if not guild:
            print(f"Guild {guild_id} not found!")
            await self.close()
            return
            
        print(f'\nGuild: {guild.name} (ID: {guild.id})')
        print(f'Members: {guild.member_count}')
        
        # Get all roles
        print(f'\n=== ALL ROLES ({len(guild.roles)} total) ===')
        roles_by_category = {}
        
        for role in sorted(guild.roles, key=lambda r: r.position, reverse=True):
            if role.name == "@everyone":
                continue
                
            print(f'Role: "{role.name}" (ID: {role.id}, Position: {role.position})')
            
            # Categorize roles
            if "board" in role.name.lower() or "merrywinter security consulting" in role.name.lower():
                category = "BOARD_DIRECTORS"
            elif "chief" in role.name.lower():
                category = "CHIEF_LEVEL"
            elif "director" in role.name.lower():
                category = "DIRECTOR_LEVEL"
            elif "command" in role.name.lower():
                category = "COMMAND_LEVEL"
            elif "senior veteran" in role.name.lower():
                category = "SENIOR_VETERAN"
            elif "veteran" in role.name.lower():
                category = "VETERAN"
            elif "senior field" in role.name.lower():
                category = "SENIOR_FIELD"
            elif "field operative" in role.name.lower():
                category = "FIELD_OPERATIVE"
            elif "trainee" in role.name.lower() or "junior" in role.name.lower():
                category = "TRAINEE"
            else:
                category = "OTHER"
                
            if category not in roles_by_category:
                roles_by_category[category] = []
            roles_by_category[category].append(role.name)
        
        # Print categorized roles
        print(f'\n=== ROLES BY CATEGORY ===')
        for category, role_list in roles_by_category.items():
            print(f'\n{category}:')
            for role_name in role_list:
                print(f'  - "{role_name}"')
        
        # Get all channels
        print(f'\n=== ALL CHANNELS ({len(guild.channels)} total) ===')
        channels_by_category = {}
        
        for channel in guild.channels:
            if isinstance(channel, discord.CategoryChannel):
                print(f'CATEGORY: "{channel.name}" (ID: {channel.id})')
                channels_by_category[channel.name] = []
            elif isinstance(channel, discord.TextChannel):
                category_name = channel.category.name if channel.category else "NO_CATEGORY"
                print(f'  TEXT: "{channel.name}" (ID: {channel.id}) - Category: {category_name}')
                if category_name not in channels_by_category:
                    channels_by_category[category_name] = []
                channels_by_category[category_name].append((channel.name, channel.id))
            elif isinstance(channel, discord.VoiceChannel):
                category_name = channel.category.name if channel.category else "NO_CATEGORY"
                print(f'  VOICE: "{channel.name}" (ID: {channel.id}) - Category: {category_name}')
        
        # Print channels by category
        print(f'\n=== CHANNELS BY CATEGORY ===')
        for category, channel_list in channels_by_category.items():
            print(f'\n{category}:')
            for channel_info in channel_list:
                if isinstance(channel_info, tuple):
                    print(f'  - "{channel_info[0]}" (ID: {channel_info[1]})')
        
        # Generate updated settings.py content
        print(f'\n=== GENERATING UPDATED SETTINGS.PY ===')
        
        # Board/Executive roles
        board_roles = roles_by_category.get("BOARD_DIRECTORS", [])
        chief_roles = roles_by_category.get("CHIEF_LEVEL", [])
        director_roles = roles_by_category.get("DIRECTOR_LEVEL", [])
        command_roles = roles_by_category.get("COMMAND_LEVEL", [])
        
        # Field operative roles
        senior_veteran_roles = roles_by_category.get("SENIOR_VETERAN", [])
        veteran_roles = roles_by_category.get("VETERAN", [])
        senior_field_roles = roles_by_category.get("SENIOR_FIELD", [])
        field_operative_roles = roles_by_category.get("FIELD_OPERATIVE", [])
        trainee_roles = roles_by_category.get("TRAINEE", [])
        
        print("\n# Updated role configuration:")
        print(f"BOARD_OF_DIRECTORS_ROLES = {board_roles}")
        print(f"CHIEF_EXECUTIVE_ROLES = {chief_roles}")
        print(f"DIRECTOR_ROLES = {director_roles}")
        print(f"COMMAND_ROLES = {command_roles}")
        print(f"OMEGA_ROLES = {senior_veteran_roles + veteran_roles}")
        print(f"BETA_ROLES = {senior_field_roles}")
        print(f"ALPHA_ROLES = {field_operative_roles + trainee_roles}")
        
        await self.close()

async def main():
    bot = GuildRolesBot()
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        print("DISCORD_TOKEN not found!")
        return
    
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())