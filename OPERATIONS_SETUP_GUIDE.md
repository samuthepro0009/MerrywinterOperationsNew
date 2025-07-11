# Operations Channels Setup Guide

## Required Discord Channels

Your bot supports comprehensive PMC operations, but you need to create these channels in your Discord server first:

### 1. Operations Categories
Create these **categories** in your Discord server:

```
🎯 OPERATIONS COMMAND
├── 📋 mission-briefings
├── 🎯 active-operations  
├── 📊 situation-reports
└── 🗺️ deployment-status

🔐 TACTICAL OPERATIONS
├── 🔴 sector-alpha (Urban Operations)
├── 🟡 sector-beta (Desert Warfare)
├── 🔵 sector-gamma (Naval Operations)
├── 🟢 sector-delta (Mountain Warfare)
├── 🟣 sector-epsilon (Jungle Operations)
└── ⚪ sector-zeta (Arctic Operations)

🎫 SUPPORT OPERATIONS
├── 🎫 tickets
├── 📝 operator-reports
├── 💼 commissions
└── 🔧 tech-support

📊 INTELLIGENCE & REPORTS
├── 📊 intelligence-reports
├── 📈 operation-logs
├── 🔍 recon-data
└── 📋 after-action-reports
```

### 2. Channel Permissions Setup

**For Operation Categories:**
- **Board of Directors**: Full access
- **Chief Officers**: Full access  
- **Directors**: Read + Send messages
- **Unit Commands**: Read + Send messages
- **Field Operatives**: Read only (except assigned sectors)

**For Tactical Sectors:**
- Only operatives deployed to specific sectors can write
- Command staff can see all sectors
- Regular members can only see sectors they're assigned to

### 3. Bot Commands for Operations

Once channels are created, update the bot configuration:

1. **Run `/setup`** - This will guide you through channel configuration
2. **Use `/deploy <sector>`** - Deploy operators to specific sectors
3. **Use `/mission <type>`** - Create mission briefings
4. **Use `/roster`** - View operator deployments

### 4. Advanced Operations Setup

The bot supports these operation types:
- **Reconnaissance** - Information gathering missions
- **Direct Action** - Combat operations
- **Special Operations** - High-priority missions
- **Security Detail** - Protection assignments
- **Convoy Escort** - Transport security
- **Base Defense** - Facility protection
- **Intelligence Gathering** - Information collection
- **Counter-Intelligence** - Security operations
- **Training Exercise** - Skill development
- **Joint Operations** - Multi-unit missions

### 5. Quick Channel Creation Commands

You can use these Discord commands to quickly create channels:

**Right-click your server → Create Category:**
1. "🎯 OPERATIONS COMMAND"
2. "🔐 TACTICAL OPERATIONS"  
3. "🎫 SUPPORT OPERATIONS"
4. "📊 INTELLIGENCE & REPORTS"

**Then create channels inside each category as listed above.**

### 6. Channel IDs Configuration

After creating channels, you'll need to get their IDs:
1. Enable Developer Mode in Discord (Settings → Advanced → Developer Mode)
2. Right-click each channel → Copy ID
3. Run `/setup` and provide the channel IDs when prompted

### 7. Role-Based Access

The bot automatically manages access based on your roles:
- **Higher clearance** = access to more channels
- **Specialized roles** = access to specific operational areas
- **Field operatives** = access to assigned sectors only

## Next Steps

1. **Create the channel structure** above in your Discord server
2. **Set proper permissions** for each category
3. **Run `/setup`** to configure the bot
4. **Test with `/mission`** and `/deploy` commands
5. **Use `/help`** for full command list

The bot is already programmed to handle all these operations - you just need to create the Discord channels and configure them!