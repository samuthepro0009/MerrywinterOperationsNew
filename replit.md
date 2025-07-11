# Merrywinter Security Consulting Discord Bot

## Overview

This is a comprehensive Discord bot designed for Roblox PMC (Private Military Company) operations management. The bot features a military-inspired hierarchy system, ticket management, mission operations, and moderation tools. It's built with Python using discord.py and implements a file-based storage system for simplicity and deployment flexibility.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes (December 2024)

✓ Implemented strict guild restriction (1114936846124843008)
✓ Enhanced security clearance system with comprehensive organizational hierarchy
✓ Converted ALL commands to modern slash commands
✓ Added high command operations functionality
✓ Implemented comprehensive automod system with anti-raid protection
✓ Added specialized Community Manager hardcoded permissions
✓ Created complete moderation tier system (Helper, Moderator, Admin, Community Managers)
✓ Added purge command with advanced filtering capabilities
✓ Configured deployment-ready workflow for Render hosting

## System Architecture

The bot follows a modular architecture using Discord.py's cog system, with clear separation of concerns:

### Core Architecture
- **Main Bot Class**: `MerrywinterBot` - Central bot instance that manages all operations
- **Cog-based Modules**: Each major feature is implemented as a separate cog for modularity
- **File-based Storage**: Uses JSON files for data persistence instead of a database
- **Configuration Management**: Centralized settings through environment variables and config class

### Key Design Decisions
- **No Database Dependency**: Uses file-based JSON storage to simplify deployment and reduce infrastructure requirements
- **Military Hierarchy**: Implements OMEGA > BETA > ALPHA clearance levels with role-based permissions
- **Async Operations**: Fully async implementation for better performance with Discord API
- **Modular Design**: Each feature isolated in separate cogs for maintainability

## Key Components

### 1. Ticket System (`cogs/tickets.py`)
- **Purpose**: Handles three types of tickets - operator reports, service commissions, and technical issues
- **Features**: Private channel creation, role-based access, automatic cleanup
- **Architecture**: Uses UUID for unique ticket IDs, creates temporary channels with specific permissions

### 2. Security Clearance System (`cogs/security.py`)
- **Purpose**: Manages military hierarchy and permissions
- **Levels**: OMEGA (Supreme), BETA (Field Command), ALPHA (Ground Operations)
- **Features**: Clearance checking, promotion tracking, permission enforcement

### 3. PMC Operations (`cogs/operations.py`)
- **Purpose**: Mission management and deployment systems
- **Features**: Mission briefings, deployment tracking, intelligence reports
- **Architecture**: Supports multiple mission types with randomized objectives

### 4. Moderation System (`cogs/moderation.py`)
- **Purpose**: Automated moderation and logging
- **Features**: Spam detection, content filtering, warning system
- **Architecture**: Real-time message monitoring with configurable thresholds

### 5. Admin Tools (`cogs/admin.py`)
- **Purpose**: Bot configuration and management
- **Features**: Setup commands, configuration management, system health checks
- **Architecture**: Administrator-only commands with comprehensive setup guidance

## Data Flow

### Storage Pattern
1. **JSON Files**: All data stored in `/data/` directory as JSON files
2. **File Locking**: Async locks prevent concurrent write conflicts
3. **Backup Strategy**: Data files include metadata and version information
4. **Structure**: Each data file has an `_info` section documenting its structure

### Ticket Workflow
1. User creates ticket → Bot generates unique ID
2. Private channel created with appropriate permissions
3. Staff notified based on clearance level
4. Ticket tracked in `tickets.json` with status updates
5. Channel automatically cleaned up when ticket closes

### Security Clearance Flow
1. User roles checked against configured clearance levels
2. Permissions granted based on hierarchy (OMEGA > BETA > ALPHA)
3. Actions logged for audit trail
4. Promotion/demotion tracked in `operators.json`

## External Dependencies

### Required Packages
- `discord.py`: Main Discord API wrapper
- `python-dotenv`: Environment variable management
- `aiofiles`: Async file operations
- `asyncio`: Async operations support

### Environment Variables
- `DISCORD_TOKEN`: Bot token for Discord API
- `COMMAND_PREFIX`: Bot command prefix (default: '!')
- `OMEGA_ROLES`, `BETA_ROLES`, `ALPHA_ROLES`: Role names for clearance levels
- `ADMIN_ROLES`, `MODERATOR_ROLES`: Administrative role names
- `TICKET_CATEGORY`, `LOG_CHANNEL`: Channel configuration

### Discord Permissions Required
- Read Messages
- Send Messages
- Manage Messages
- Manage Channels
- Manage Roles
- View Audit Log
- Embed Links
- Attach Files

## Deployment Strategy

### Platform Compatibility
- **Primary**: Designed for Render.com deployment
- **Alternative**: Can run on any Python-supporting platform
- **Local Development**: Full support for local testing

### File Structure
- `/data/`: JSON storage files
- `/logs/`: Application logs (local only)
- `/config/`: Configuration files
- `/utils/`: Helper utilities
- `/cogs/`: Feature modules

### Deployment Requirements
1. Python 3.9+ runtime
2. Environment variables configured
3. Discord bot token with appropriate permissions
4. Server roles and channels setup matching configuration

### Scaling Considerations
- File-based storage suitable for small to medium Discord servers
- Consider database migration for high-volume operations
- Automatic backup system recommended for production use
- Health monitoring and uptime tracking built-in

The bot is designed to be deployment-ready with minimal configuration, using file-based storage to avoid database setup complexity while maintaining full functionality for PMC operations management.