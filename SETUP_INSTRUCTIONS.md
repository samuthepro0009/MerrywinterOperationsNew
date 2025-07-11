# Discord Bot Setup Instructions

## Current Status
✅ **Bot is running and operational**
✅ **20 slash commands synced globally**
✅ **All cogs loaded successfully**

## If Commands Still Not Showing

The bot is properly configured and syncing commands. If you still can't see the slash commands in Discord, please check:

### 1. Discord Developer Portal Settings
Go to https://discord.com/developers/applications/1393253884176236746/bot

**Required Bot Permissions:**
- ✅ Send Messages
- ✅ Use Slash Commands  
- ✅ Embed Links
- ✅ Manage Messages
- ✅ Manage Channels
- ✅ Manage Roles
- ✅ Read Message History

**Required Privileged Gateway Intents:**
- ✅ Server Members Intent (REQUIRED)
- ✅ Message Content Intent (REQUIRED)
- ✅ Presence Intent (Optional)

### 2. Server Integration
Make sure the bot was invited with proper scopes:
- `bot` scope
- `applications.commands` scope

### 3. Testing Commands
Try these commands in Discord:
- `/help` - Should show comprehensive help
- `/info` - Should show bot information
- `/ping` - Should show latency
- `/setup` - Admin setup (requires admin role)

### 4. Troubleshooting
If commands still don't appear:
1. Try kicking and re-inviting the bot
2. Check that you have the proper roles configured
3. Wait 1-2 minutes for Discord to propagate the commands
4. Try refreshing Discord (Ctrl+R or Cmd+R)

## Bot Application Details
- **Application ID**: 1393253884176236746
- **Bot ID**: 1393253884176236746
- **Authorized Guild**: 1114936846124843008 (Merrywinter Security Consulting)

## Available Commands
The bot has successfully registered these 20 slash commands:
- `/help` - Comprehensive help
- `/info` - Bot information  
- `/ping` - Latency check
- `/setup` - Bot setup (Admin)
- `/verify` - Verify configuration (Admin)
- `/stats` - Bot statistics (Admin)
- `/backup` - Create backup (Admin)
- `/maintenance` - Toggle maintenance mode (Admin)
- `/reload` - Reload cogs (Admin)
- `/shutdown` - Shutdown bot (Admin)
- `/report-operator` - Report misconduct
- `/commission` - Commission services
- `/tech-issue` - Report technical issues
- `/ticket-status` - Check ticket status
- `/close-ticket` - Close ticket (Staff)
- `/clearance` - Check security clearance
- `/roster` - View operator roster
- `/mission` - Get mission briefing
- `/deploy` - Deploy to sector
- Plus additional specialized commands

## Next Steps
The bot is fully operational. If you're still having issues seeing the commands, the problem is likely with Discord's permissions or the bot invitation settings rather than the code itself.