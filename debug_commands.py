"""
Debug script to check bot commands
"""

import discord
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

class DebugBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.members = True
        super().__init__(intents=intents)
        
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        print(f'Bot ID: {self.user.id}')
        
        # Check application info
        app_info = await self.application_info()
        print(f'Application ID: {app_info.id}')
        print(f'Application Name: {app_info.name}')
        
        # Check guild commands
        guild_id = 1114936846124843008
        guild = self.get_guild(guild_id)
        
        if guild:
            print(f'Guild: {guild.name}')
            print(f'Guild ID: {guild.id}')
            print(f'Bot member in guild: {guild.get_member(self.user.id) is not None}')
            
            # Check bot permissions
            bot_member = guild.get_member(self.user.id)
            if bot_member:
                perms = bot_member.guild_permissions
                print(f'Bot permissions:')
                print(f'  - Use Slash Commands: {perms.use_slash_commands}')
                print(f'  - Send Messages: {perms.send_messages}')
                print(f'  - Manage Messages: {perms.manage_messages}')
                print(f'  - Embed Links: {perms.embed_links}')
            
            # Try to get guild commands
            try:
                commands = await guild.fetch_commands()
                print(f'Guild commands found: {len(commands)}')
                for cmd in commands:
                    print(f'  - {cmd.name}: {cmd.description}')
            except Exception as e:
                print(f'Error fetching guild commands: {e}')
                
        # Try to get global commands
        try:
            global_commands = await self.fetch_global_commands()
            print(f'Global commands found: {len(global_commands)}')
            for cmd in global_commands:
                print(f'  - {cmd.name}: {cmd.description}')
        except Exception as e:
            print(f'Error fetching global commands: {e}')
            
        await self.close()

async def main():
    bot = DebugBot()
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        print("DISCORD_TOKEN not found!")
        return
    
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())