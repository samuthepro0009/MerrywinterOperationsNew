# 🚁 Merrywinter Security Consulting - Discord Bot

A comprehensive Discord bot for Roblox PMC (Private Military Company) operations management, featuring advanced ticket systems, security clearance management, and 24/7 hosting compatibility.

*Inspired by Merriweather Security from GTA V*

## 🌟 Features

### 🎫 Ticket System
- **Report an Operator**: Report misconduct or issues with team members
- **Commission a Service**: Request PMC services and operations
- **Report Technical Issue**: Report map bugs, script errors, or technical problems
- Private ticket channels with automatic cleanup
- Role-based access control for ticket management

### 🔒 Security Clearance System
- **OMEGA Command**: Supreme authority with full access
- **BETA Command**: Field operations and management
- **ALPHA Operators**: Ground operations and basic access
- Automatic role-based permission management
- Promotion/demotion tracking and logging

### ⚔️ PMC Operations
- **Mission Briefings**: Detailed mission assignments with objectives
- **Deployment System**: Deploy operators to various sectors
- **Intelligence Reports**: Access classified operational intelligence
- **Situation Reports**: Real-time operational status updates
- **Operator Status**: Track individual operator performance

### 🛡️ Moderation & Administration
- **Automated Moderation**: Spam detection and content filtering
- **Warning System**: Official warning management with logging
- **Timeout/Mute System**: Temporary user restrictions
- **Comprehensive Logging**: All actions tracked and logged
- **Admin Tools**: Bot management and configuration

### 📊 Advanced Features
- **Chain of Command**: Military hierarchy enforcement
- **File-based Storage**: No database required
- **Health Monitoring**: Automatic health checks and uptime tracking
- **Backup System**: Data backup and recovery capabilities
- **Statistics Dashboard**: Comprehensive operational statistics

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- Discord Bot Token
- Render account (for hosting)

### Installation

1. **Clone or download the bot files**
2. **Install dependencies**:
   ```bash
   pip install discord.py python-dotenv aiofiles
   ```

3. **Configure Environment Variables**:
   Create a `.env` file based on `.env.example`:
   ```env
   DISCORD_TOKEN=your_bot_token_here
   COMMAND_PREFIX=!
   OMEGA_ROLES=OMEGA Command,Supreme Commander
   BETA_ROLES=BETA Command,Field Commander
   ALPHA_ROLES=ALPHA Operator,Ground Operator
   ADMIN_ROLES=Admin,Administrator
   MODERATOR_ROLES=Moderator,Staff
   TICKET_CATEGORY=Support Tickets
   LOG_CHANNEL=bot-logs
   ```

4. **Run the bot**:
   ```bash
   python main.py
   ```

### Discord Server Setup

1. **Create Required Roles**:
   - `OMEGA Command` - Supreme authority
   - `BETA Command` - Field operations
   - `ALPHA Operator` - Ground operations
   - `Admin` - Bot administration
   - `Moderator` - Moderation permissions

2. **Create Required Channels**:
   - `#bot-logs` - For moderation and system logs
   - `#general` - General communications
   - `#operations` - Mission briefings and operations

3. **Create Categories**:
   - `Support Tickets` - For the ticket system

4. **Configure Bot Permissions**:
   - Manage Channels
   - Manage Roles
   - Manage Messages
   - Read Messages
   - Send Messages
   - Embed Links
   - Add Reactions

## 🔧 Commands Reference

### 📋 General Commands
- `!help` - Display comprehensive help information
- `!info` - Bot information and statistics
- `!ping` - Check bot latency and response time

### 🎫 Ticket System
- `!report-operator @user reason` - Report an operator for misconduct
- `!commission service_details` - Commission PMC services
- `!tech-issue description` - Report technical issues
- `!ticket-status [ticket_id]` - Check ticket status
- `!close-ticket ticket_id` - Close a ticket (Staff only)

### 🔒 Security Clearance
- `!clearance [@user]` - Check security clearance level
- `!promote @user LEVEL` - Promote operator (Admin only)
- `!demote @user LEVEL` - Demote operator (Admin only)
- `!roster` - View operator roster by clearance
- `!security-audit` - Perform security audit (Admin only)

### ⚔️ Operations
- `!mission [type]` - Get mission briefing
- `!status [@user]` - Check operator status
- `!deploy [sector]` - Deploy to operational sector
- `!intel [type]` - Access intelligence reports
- `!sitrep` - Generate situation report

### 🛡️ Moderation
- `!warn @user reason` - Issue official warning (Mod only)
- `!warnings [@user]` - Check warning history
- `!mute @user duration reason` - Mute user (Mod only)
- `!unmute @user` - Unmute user (Mod only)
- `!modlogs [@user]` - View moderation logs (Admin only)

### ⚙️ Administration
- `!setup` - Initial bot setup guide (Admin only)
- `!verify-setup` - Verify bot configuration (Admin only)
- `!stats` - Display bot statistics (Admin only)
- `!backup` - Create data backup (Admin only)
- `!maintenance [on/off]` - Toggle maintenance mode (Admin only)
- `!reload [cog]` - Reload bot components (Admin only)

## 🌐 Render Hosting Setup

### Deployment Configuration

1. **Connect Repository**: Link your GitHub repository to Render
2. **Service Settings**:
   - **Name**: `merrywinter-security-bot`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`

3. **Environment Variables**:
   Set all required environment variables in Render dashboard:
   ```
   DISCORD_TOKEN=your_bot_token
   COMMAND_PREFIX=!
   OMEGA_ROLES=OMEGA Command
   BETA_ROLES=BETA Command
   ALPHA_ROLES=ALPHA Operator
   ADMIN_ROLES=Admin
   MODERATOR_ROLES=Moderator
   TICKET_CATEGORY=Support Tickets
   LOG_CHANNEL=bot-logs
   ```

### Requirements File
Create `requirements.txt`:
