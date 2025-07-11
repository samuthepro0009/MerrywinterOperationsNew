"""
Script to gather guild information for proper bot configuration
"""

import discord
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

class GuildInfoBot(discord.Client):
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
            print(f"Guild {guild_id} not found")
            await self.close()
            return
            
        print(f"\n=== GUILD INFO ===")
        print(f"Guild Name: {guild.name}")
        print(f"Guild ID: {guild.id}")
        print(f"Member Count: {guild.member_count}")
        print(f"Owner: {guild.owner}")
        
        print(f"\n=== ROLES ===")
        for role in guild.roles:
            if role.name != "@everyone":
                print(f"Role: {role.name} (ID: {role.id})")
        
        print(f"\n=== CHANNELS ===")
        for channel in guild.channels:
            print(f"Channel: {channel.name} (ID: {channel.id}) - Type: {type(channel).__name__}")
        
        print(f"\n=== CATEGORIES ===")
        for category in guild.categories:
            print(f"Category: {category.name} (ID: {category.id})")
        
        await self.close()

async def main():
    bot = GuildInfoBot()
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        print("DISCORD_TOKEN not found!")
        return
    
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())