# Merrywinter Security Consulting Discord Bot

A comprehensive Discord bot designed for Roblox PMC (Private Military Company) operations management. This bot features a military-inspired hierarchy system, ticket management, mission operations, moderation tools, and anti-raid protection - all restricted to authorized Discord servers.

## Features

### 🎫 Advanced Ticket System
- **Report Operator**: Report misconduct or issues with operators
- **Commission Services**: Request PMC services and operations
- **Technical Issues**: Report map bugs and technical problems
- Private ticket channels with role-based access
- Automated ticket management and cleanup
- **All slash commands** - Modern Discord integration

### 🛡️ Comprehensive Security Clearance System
Based on organizational hierarchy with multiple levels:
- **Board of Directors**: Supreme executive authority
- **Chief Executive/Operations/Cybersecurity/Compliance**: Executive leadership
- **Director-Level Positions**: Department leadership across Security, Cybersecurity, Personnel, Innovation, Tactical, and Intelligence
- **Specialized Roles**: Convoy Escort, Recon & Surveillance, Training & Combat, Executive Protection, Tactical Deployment
- **Traditional PMC Ranks**: OMEGA (Supreme Command), BETA (Field Command), ALPHA (Ground Operations)

### 👥 Moderation Hierarchy
- **Community Managers**: Ultimate authority (hardcoded user IDs)
- **Administrators**: Server management
- **Moderators**: Community oversight
- **Helpers**: Community support

### ⚔️ PMC Operations
- Mission briefings with randomized objectives
- Operator status tracking and deployment
- Intelligence reports and situation updates
- Sector-based deployment system (6 operational sectors)
- Mission type classification (10 different types)

### 🎯 High Command Operations
- **Deployment Authorization**: Director+ can authorize unit deployments
- **Operation Management**: Chief+ can start major operations
- **Operation Logging**: Director+ can log operation activities
- Dedicated channels for each command type

### 🔧 Administrative Tools
- Bot setup and configuration management
- Data backup and restoration
- Health monitoring and statistics
- Maintenance mode controls
- Comprehensive logging system

### 🛡️ Advanced Moderation Features
- **Anti-Raid System**: Automatic detection and lockdown
- **Purge Command**: Bulk message deletion with filtering
- Warning system with tracking
- Mute/unmute functionality
- Moderation action logging
- Content filtering and monitoring

### 🔒 Guild Restriction
- **Authorized Guild Only**: Bot only functions in guild ID `1114936846124843008`
- Automatic departure from unauthorized servers
- Complete command restriction outside authorized guild

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install discord.py python-dotenv aiofiles
   ```
3. Configure environment variables (see `.env.example`)
4. Run the bot:
   ```bash
   python main.py
   ```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure the following:

```env
# Bot Configuration
DISCORD_TOKEN=your_discord_bot_token_here
COMMAND_PREFIX=!

# All Security Clearance Roles (comma-separated)
BOARD_OF_DIRECTORS_ROLES=Board of Directors,Chairman,CEO
CHIEF_EXECUTIVE_ROLES=Chief Executive,CEO,Executive Director
CHIEF_OPERATIONS_ROLES=Chief Operations,COO,Operations Director
# ... (see .env.example for complete list)

# Moderation Roles
ADMIN_ROLES=Admin,Administrator,Management
MODERATOR_ROLES=Moderator,Mod,Staff
HELPER_ROLES=Helper,Support,Assistant

# High Command Channels
DEPLOYMENT_CHANNEL_ID=your_deployment_channel_id
OPERATION_START_CHANNEL_ID=your_operation_start_channel_id
OPERATION_LOG_CHANNEL_ID=your_operation_log_channel_id

# Anti-Raid Configuration
ANTI_RAID_ENABLED=true
RAID_DETECTION_THRESHOLD=10
RAID_DETECTION_TIMEFRAME=30
RAID_ACTION=lockdown

# Channel Configuration
TICKET_CATEGORY=Support Tickets
LOG_CHANNEL=bot-logs
```

### Role Setup

1. Create Discord roles matching your configuration
2. Assign roles to users based on their clearance level
3. Ensure bot has appropriate permissions
4. Configure Community Manager user IDs in config/settings.py

## Commands (All Slash Commands)

### Ticket System
- `/report-operator` - Report operator misconduct
- `/commission` - Commission PMC services
- `/tech-issue` - Report technical issues
- `/ticket-status` - Check ticket status
- `/close-ticket` - Close ticket (Staff only)

### Security Clearance
- `/clearance` - Check security clearance level
- `/roster` - View operator roster by clearance
- `/promote` - Promote operator (Admin only)
- `/demote` - Demote operator (Admin only)
- `/audit` - Perform security audit (Admin only)

### PMC Operations
- `/mission` - Get mission briefing
- `/status` - Check operator status
- `/deploy` - Deploy to operational sector
- `/intel` - Access intelligence reports
- `/sitrep` - Generate situation report

### High Command Operations
- `/deployment` - Authorize unit deployments (Director+ only)
- `/operation-start` - Start major operations (Chief+ only)
- `/operation-log` - Log operation activities (Director+ only)

### Advanced Moderation
- `/purge` - Delete multiple messages with filtering (Moderator+ only)
- `/warn` - Issue warning (Moderator+ only)
- `/warnings` - Check user warnings
- `/mute` - Mute user (Moderator+ only)
- `/unmute` - Unmute user (Moderator+ only)

### Administrative
- `/setup` - Initial bot setup (Admin only)
- `/verify` - Verify bot configuration
- `/stats` - Display bot statistics
- `/backup` - Create data backup (Admin only)
- `/maintenance` - Toggle maintenance mode

### General
- `/help` - Display help information
- `/info` - Display bot information
- `/ping` - Check bot latency

## Company Information

- **Company Name**: Merrywinter Security Consulting
- **Motto**: "Sub umbra, vincimus" (Under the shadow, we conquer)
- **Established**: 2025
- **Founders**: Rev, Samu, Fraa, Luca
- **Operations**: 24/7 Global Coverage
- **Authorized Guild**: 1114936846124843008

## Permissions

The bot requires the following Discord permissions:
- Read Messages
- Send Messages
- Manage Messages
- Manage Channels
- Manage Roles
- View Audit Log
- Embed Links
- Attach Files
- Use Slash Commands

## Deployment

### Render.com Deployment (Recommended)

1. Connect your GitHub repository to Render
2. Set up environment variables in Render dashboard
3. Deploy as a Background Worker service
4. Monitor logs for successful startup

### Local Development

1. Create a `.env` file with your configuration
2. Run `python main.py` to start the bot
3. Check logs for any configuration issues

## Architecture

The bot uses a modular architecture with separate cogs for different features:

- **main.py**: Bot initialization and core functionality
- **cogs/tickets.py**: Advanced ticket system management
- **cogs/security.py**: Security clearance system
- **cogs/operations.py**: PMC operations management
- **cogs/moderation.py**: Advanced moderation and anti-raid
- **cogs/admin.py**: Administrative tools
- **cogs/high_command.py**: High command operations
- **config/settings.py**: Comprehensive configuration management
- **utils/**: Utility functions and helpers

## Data Storage

The bot uses JSON files for data persistence:
- `data/tickets.json`: Ticket information
- `data/operators.json`: Operator data
- `data/missions.json`: Mission records
- `data/warnings.json`: Warning records
- `data/deployments.json`: Deployment records
- `data/operations.json`: Operation records
- `data/operation_logs.json`: Operation log records

## Anti-Raid Protection

The bot includes comprehensive anti-raid protection:
- Monitors user join patterns
- Configurable detection thresholds
- Automatic server lockdown on raid detection
- Logging and alerting to admin channels

## Security Features

- Guild restriction ensures bot only works in authorized server
- Hierarchical permission system
- Community Manager override permissions
- Comprehensive audit logging
- Automatic data cleanup and backups

## Support

For support or questions, please contact the Community Managers or open an issue on the GitHub repository.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Merrywinter Security Consulting** - *Sub umbra, vincimus* (Under the shadow, we conquer)
*Est. 2025 - Founded by Rev, Samu, Fraa, Luca*