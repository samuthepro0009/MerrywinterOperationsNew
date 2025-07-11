"""
Configuration settings for Merrywinter Security Consulting Bot
"""

import os
from typing import Dict, List

class Config:
    """Configuration class for bot settings"""
    
    # Bot Configuration
    COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '!')
    
    # Guild Restriction - Only works in this guild
    AUTHORIZED_GUILD_ID = 1114936846124843008
    
    # Company Information
    COMPANY_NAME = "Merrywinter Security Consulting"
    COMPANY_MOTTO = "Sub umbra, vincimus"
    COMPANY_ESTABLISHED = "Est. 2025"
    COMPANY_FOUNDERS = ["Rev", "Samu", "Fraa", "Luca"]
    
    # AI System Information (FROST AI)
    AI_NAME = "F.R.O.S.T"
    AI_FULL_NAME = "Fully Responsive Operational Support Technician"
    AI_VERSION = "v2.5.7"
    AI_STATUS_MESSAGES = [
        "█▀▀ ▀█▀ ▄▀█ ▀█▀ █░█ █▀   █▀█ █▄░█ █░░ █ █▄░█ █▀▀",
        "▄▄▄ ░█░ █▀█ ░█░ █▄█ ▄█   █▄█ █░▀█ █▄▄ █ █░▀█ ██▄",
        "FROST AI v2.5.7 - OPERATIONAL",
        "All systems nominal • Threat level: GREEN",
        "Monitoring personnel • Scanning for anomalies"
    ]
    
    # Security Clearance Levels (Based on organizational sections)
    SECURITY_LEVELS = {
        'EXECUTIVE_COMMAND': 10,        # Executive Command
        'BOARD_OF_DIRECTORS': 9,        # Board of Directors
        'DEPARTMENT_DIRECTORS': 8,      # Department Directors
        'COMMAND_LEVEL': 7,             # Command positions
        'SPECIALIZED_UNITS': 6,         # Specialized unit roles
        'OMEGA': 5,                     # Senior Veteran Field Operatives
        'BETA': 4,                      # Senior Field Operatives
        'ALPHA': 3,                     # Field Operatives
        'ENLISTED': 2,                  # Regular enlisted
        'CIVILIAN': 1                   # Guests/Clients
    }
    
    # Role Configuration - COMPLETE role names from the guild
    BOARD_OF_DIRECTORS_ROLES = ["Board of Directors"]
    
    # Executive Level Roles
    CHIEF_EXECUTIVE_ROLES = ["Executive Director", "Executive Command"]
    
    # Director Level Roles - Complete list
    DIRECTOR_SECURITY_ROLES = ["Director of Strategic Operations", "Director of Security Architecture", "Compliance & Oversight Director", "Director of Security Operations", "Director of Cybersecurity Operations", "Director of Personnel and Clearance", "Director of Innovation and Technology", "Department Directors", "Director of Tactical Operations", "Director of Intelligence and Security", "Escort Security Units Director"]
    
    # Command Level Roles - All command positions
    COMMAND_ROLES = ["Tactical Operations Section Command", "Tactical Deployment Command", "Convoy & Armored Escort Division Command", "Recon & Surveillance Command", "Training & Combat Readiness Department Command", "Executive Protection Unit Command", "Intelligence and Security Section Command", "Human Intelligence Detachment Command", "Psychological Operations Detachment Command", "Open Source Intelligence Command", "Tactical Operations Sub Unit Command", "Blue Team Command", "Red Team Command", "Convoy & Control Commander", "Undercover Units Command", "Long Range Recon Team Command", "Advanced Tactical Training Teams Command", "Close Protection Teams Command", "Emergency Evacuation & Extraction Unit Command"]
    
    # Specialized Unit Roles - Complete structure
    CONVOY_ESCORT_ROLES = ["Convoy & Armored Escort Division Command", "Convoy & Control Commander", "Convoy & Control Team"]
    RECON_SURVEILLANCE_ROLES = ["Recon & Surveillance Command", "Long Range Recon Team Command", "Long Range Recon Team"]
    TRAINING_COMBAT_ROLES = ["Training & Combat Readiness Department Command", "Advanced Tactical Training Teams Command", "Advanced Tactical Training Teams"]
    EXECUTIVE_PROTECTION_ROLES = ["Executive Protection Unit Command", "Close Protection Teams Command", "Close Protection Teams"]
    TACTICAL_DEPLOYMENT_ROLES = ["Tactical Deployment Command", "Tactical Operations Sub Unit Command", "Tactical Operations Sub Units"]
    INTELLIGENCE_ROLES = ["Intelligence and Security Section Command", "Human Intelligence Detachment Command", "Psychological Operations Detachment Command", "Open Source Intelligence Command"]
    
    # Field Operative Roles - Complete hierarchy
    OMEGA_ROLES = ["Senior Veteran Field Operative", "Veteran Field Operative", "Candidate Veteran Field Operative"]
    BETA_ROLES = ["Senior Field Operative III", "Senior Field Operative II", "Senior Field Operative I"]
    ALPHA_ROLES = ["Field Operative III", "Field Operative II", "Field Operative I", "Junior Field Operative", "Trainee Operative"]
    
    # Additional roles
    VERIFICATION_ROLES = ["Verified", "Unverified"]
    CLIENT_ROLES = ["Client", "Guest"]
    ENTRANT_ROLES = ["Entrant"]
    
    # Permission Structure - Based on organizational hierarchy
    # Executive Command - Highest authority
    EXECUTIVE_COMMAND_ROLES = ["Executive Command"]
    
    # Board of Directors - Strategic oversight
    BOARD_OF_DIRECTORS_ROLES = ["Board of Directors", "CEO"]
    
    # Department Directors - Departmental leadership
    DEPARTMENT_DIRECTORS_ROLES = ["Department Directors"] + DIRECTOR_SECURITY_ROLES
    
    # Enlisted - Regular operators (all field operatives)
    ENLISTED_ROLES = OMEGA_ROLES + BETA_ROLES + ALPHA_ROLES + ["Entrant"]
    
    # Moderation Configuration
    COMMUNITY_MANAGERS = [618708505393889300, 700659364574396438, 972959357971103834, 488052909867532288]
    ADMIN_ROLES = EXECUTIVE_COMMAND_ROLES + BOARD_OF_DIRECTORS_ROLES
    MODERATOR_ROLES = DEPARTMENT_DIRECTORS_ROLES[:5]  # First 5 department directors
    HELPER_ROLES = DEPARTMENT_DIRECTORS_ROLES[5:] + COMMAND_ROLES[:10]  # Other directors + command roles
    
    # Channel Configuration
    TICKET_CATEGORY = "TICKET SYSTEM"
    LOG_CHANNEL = "bot-logs"
    
    # Channel IDs from the guild
    TICKET_CATEGORY_ID = 1393249646192754698
    LOG_CHANNEL_ID = 1393249520388935793
    
    # Moderation Logging Channel (for comprehensive logs)
    MODERATION_LOG_CHANNEL_ID = 1393349090431205456
    
    # Colors for embeds (FROST AI theme)
    COLORS = {
        'primary': 0x00ff41,        # Matrix green
        'secondary': 0x0099ff,      # Blue
        'success': 0x00ff00,        # Green
        'warning': 0xffa500,        # Orange
        'error': 0xff0000,          # Red
        'info': 0x00ffff,           # Cyan
        'frost': 0x00ff41           # FROST signature color
    }
    
    # 24/7 Uptime Configuration
    ENABLE_KEEPALIVE = True
    KEEPALIVE_INTERVAL = 30  # minutes
    HEALTH_CHECK_INTERVAL = 15  # minutes
    AUTO_RESTART_ON_ERROR = True
    
    # Advanced Moderation Settings
    ANTI_SPAM_ESCALATION = {
        'first_offense': 'warn',
        'second_offense': 'timeout_5min',
        'third_offense': 'timeout_1hour',
        'fourth_offense': 'timeout_1day',
        'fifth_offense': 'ban'
    }
    
    WARNING_POINT_SYSTEM = {
        'spam': 2,
        'inappropriate_content': 3,
        'harassment': 5,
        'raid_participation': 10,
        'point_decay_days': 30  # Points decay after 30 days
    }
    
    PHISHING_DOMAINS = [
        'discord-nitro.com', 'discordapp.info', 'discord-gift.com',
        'steamcommunity.ru', 'steampowered.org', 'discord.com.ru'
    ]
    
    # Performance Metrics Tracking
    PERFORMANCE_CATEGORIES = {
        'operations': ['deployments', 'missions_completed', 'objectives_met'],
        'training': ['sessions_attended', 'certifications_earned', 'skill_assessments'],
        'leadership': ['commands_given', 'team_coordination', 'decision_making'],
        'reliability': ['attendance_rate', 'response_time', 'availability']
    }
    
    # Training Schedule Types
    TRAINING_TYPES = {
        'basic': {'duration': 60, 'requirements': ['ALPHA'], 'max_participants': 20},
        'advanced': {'duration': 90, 'requirements': ['BETA'], 'max_participants': 15},
        'specialized': {'duration': 120, 'requirements': ['OMEGA'], 'max_participants': 10},
        'command': {'duration': 45, 'requirements': ['DEPARTMENT_DIRECTORS'], 'max_participants': 8}
    }
    
    # Smart Notifications Settings
    NOTIFICATION_PRIORITIES = {
        'critical': {'color': 0xff0000, 'ping_roles': True, 'urgent': True},
        'high': {'color': 0xff8800, 'ping_roles': True, 'urgent': False},
        'medium': {'color': 0xffff00, 'ping_roles': False, 'urgent': False},
        'low': {'color': 0x00ff00, 'ping_roles': False, 'urgent': False}
    }
    
    # Roblox Integration Settings
    ROBLOX_GAME_ID = None  # To be configured
    ROBLOX_UNIVERSE_ID = None  # To be configured
    ROBLOX_API_KEY = None  # To be configured via secrets
    ROBLOX_GROUP_ID = None  # PMC group ID
    ROBLOX_PLACE_ID = None  # Main game place ID
    
    # Roblox API Configuration
    ROBLOX_API_BASE = "https://api.roblox.com"
    ROBLOX_GAMES_API = "https://games.roblox.com"
    ROBLOX_USERS_API = "https://users.roblox.com"
    ROBLOX_GROUPS_API = "https://groups.roblox.com"
    
    # Roblox Integration Features
    ROBLOX_FEATURES = {
        'player_verification': True,
        'game_status_monitoring': True,
        'performance_tracking': True,
        'rank_synchronization': True,
        'event_logging': True
    }
    
    # API Endpoints Configuration
    API_ENDPOINTS = {
        'stats': '/api/stats',
        'users': '/api/users',
        'operations': '/api/operations',
        'training': '/api/training',
        'moderation': '/api/moderation'
    }
    
    # Guild authorization check
    @staticmethod
    def check_guild_authorization(guild_id):
        """Check if guild is authorized to use the bot"""
        return guild_id == Config.AUTHORIZED_GUILD_ID
    
    @staticmethod
    def is_moderator(user_roles, user_id):
        """Check if user has moderator permissions"""
        return (any(role in Config.MODERATOR_ROLES for role in user_roles) or
                any(role in Config.ADMIN_ROLES for role in user_roles) or
                user_id in Config.COMMUNITY_MANAGERS)
    

    
    # High Command Operations Channels
    DEPLOYMENT_CHANNEL_ID = 1393246091289559172  # Canale annunci operazioni
    OPERATION_START_CHANNEL_ID = 1393246091289559172  # Stesso canale per start operazioni
    OPERATION_LOG_CHANNEL_ID = 1393340130177191956  # Canale log operazioni
    
    # Anti-Raid Configuration
    ANTI_RAID_ENABLED = os.getenv('ANTI_RAID_ENABLED', 'true').lower() == 'true'
    RAID_DETECTION_THRESHOLD = int(os.getenv('RAID_DETECTION_THRESHOLD', '10'))  # Users joining in timeframe
    RAID_DETECTION_TIMEFRAME = int(os.getenv('RAID_DETECTION_TIMEFRAME', '30'))  # Seconds
    RAID_ACTION = os.getenv('RAID_ACTION', 'lockdown')  # lockdown, kick, ban
    
    # Ticket Configuration
    TICKET_TYPES = {
        'report-operator': {
            'name': 'Report an Operator',
            'emoji': '⚠️',
            'description': 'Report misconduct or issues with an operator'
        },
        'commission': {
            'name': 'Commission a Service',
            'emoji': '💼',
            'description': 'Request PMC services or operations'
        },
        'tech-issue': {
            'name': 'Report Technical Issue',
            'emoji': '🔧',
            'description': 'Report map bugs or technical problems'
        }
    }
    
    # Ticket Status Options
    TICKET_STATUSES = {
        'open': {'name': 'Open', 'emoji': '🟢', 'color': 0x00FF00},
        'taken': {'name': 'Taken', 'emoji': '🟡', 'color': 0xFFFF00},
        'in_progress': {'name': 'In Progress', 'emoji': '🔵', 'color': 0x0000FF},
        'pending_review': {'name': 'Pending Review', 'emoji': '🟠', 'color': 0xFFA500},
        'closed': {'name': 'Closed', 'emoji': '🔴', 'color': 0xFF0000},
        'auto_closed': {'name': 'Auto Closed', 'emoji': '⚫', 'color': 0x808080}
    }
    
    # PMC Chain of Command
    CHAIN_OF_COMMAND = {
        'OMEGA': {
            'title': 'Commander',
            'permissions': ['all'],
            'description': 'Supreme command authority'
        },
        'BETA': {
            'title': 'Lieutenant',
            'permissions': ['moderate', 'mission_planning', 'operator_management'],
            'description': 'Field command and operations'
        },
        'ALPHA': {
            'title': 'Operator',
            'permissions': ['basic_operations'],
            'description': 'Ground operations and reconnaissance'
        }
    }
    
    # Operation Sectors
    OPERATION_SECTORS = [
        'Sector Alpha - Urban Operations',
        'Sector Beta - Desert Warfare',
        'Sector Gamma - Naval Operations',
        'Sector Delta - Mountain Warfare',
        'Sector Epsilon - Jungle Operations',
        'Sector Zeta - Arctic Operations'
    ]
    
    # Mission Types
    MISSION_TYPES = [
        'Reconnaissance',
        'Direct Action',
        'Special Operations',
        'Security Detail',
        'Convoy Escort',
        'Base Defense',
        'Intelligence Gathering',
        'Counter-Intelligence',
        'Training Exercise',
        'Joint Operations'
    ]
    
    # Colors
    COLORS = {
        'primary': 0x2F3136,
        'success': 0x57F287,
        'warning': 0xFEE75C,
        'error': 0xED4245,
        'info': 0x5865F2,
        'omega': 0xFF6B6B,
        'beta': 0x4ECDC4,
        'alpha': 0x45B7D1
    }
    
    # File Paths
    DATA_DIR = 'data'
    TICKETS_FILE = f'{DATA_DIR}/tickets.json'
    OPERATORS_FILE = f'{DATA_DIR}/operators.json'
    MISSIONS_FILE = f'{DATA_DIR}/missions.json'
    
    @classmethod
    def get_security_level(cls, roles: List[str]) -> str:
        """Get security clearance level based on roles"""
        role_names = [role.lower() for role in roles]
        
        # Check all clearance levels from highest to lowest
        clearance_checks = [
            ('EXECUTIVE_COMMAND', cls.EXECUTIVE_COMMAND_ROLES),
            ('BOARD_OF_DIRECTORS', cls.BOARD_OF_DIRECTORS_ROLES),
            ('DEPARTMENT_DIRECTORS', cls.DEPARTMENT_DIRECTORS_ROLES),
            ('COMMAND_LEVEL', cls.COMMAND_ROLES),
            ('SPECIALIZED_UNITS', cls.CONVOY_ESCORT_ROLES + cls.RECON_SURVEILLANCE_ROLES + cls.TRAINING_COMBAT_ROLES + cls.EXECUTIVE_PROTECTION_ROLES + cls.TACTICAL_DEPLOYMENT_ROLES + cls.INTELLIGENCE_ROLES),
            ('OMEGA', cls.OMEGA_ROLES),
            ('BETA', cls.BETA_ROLES),
            ('ALPHA', cls.ALPHA_ROLES),
            ('ENLISTED', cls.ENLISTED_ROLES),
            ('CIVILIAN', cls.CLIENT_ROLES + cls.VERIFICATION_ROLES)
        ]
        
        for level, role_list in clearance_checks:
            for role in role_list:
                if role and role.lower() in role_names:
                    return level
        
        return 'CIVILIAN'
    
    @classmethod
    def has_permission(cls, user_level: str, required_level: str) -> bool:
        """Check if user has required permission level"""
        user_clearance = cls.SECURITY_LEVELS.get(user_level, 0)
        required_clearance = cls.SECURITY_LEVELS.get(required_level, 0)
        
        return user_clearance >= required_clearance
    
    @classmethod
    def is_community_manager(cls, user_id: int) -> bool:
        """Check if user is a community manager"""
        return user_id in cls.COMMUNITY_MANAGERS
    
    @classmethod
    def is_executive_command(cls, roles: List[str]) -> bool:
        """Check if user has Executive Command clearance"""
        role_names = [role.lower() for role in roles]
        return any(role.lower() in role_names for role in cls.EXECUTIVE_COMMAND_ROLES if role)
    
    @classmethod
    def is_board_of_directors(cls, roles: List[str]) -> bool:
        """Check if user has Board of Directors clearance"""
        role_names = [role.lower() for role in roles]
        return any(role.lower() in role_names for role in cls.BOARD_OF_DIRECTORS_ROLES if role)
    
    @classmethod
    def is_department_director(cls, roles: List[str]) -> bool:
        """Check if user has Department Director clearance"""
        role_names = [role.lower() for role in roles]
        return any(role.lower() in role_names for role in cls.DEPARTMENT_DIRECTORS_ROLES if role)
    
    @classmethod
    def is_enlisted(cls, roles: List[str]) -> bool:
        """Check if user has Enlisted clearance"""
        role_names = [role.lower() for role in roles]
        return any(role.lower() in role_names for role in cls.ENLISTED_ROLES if role)
    
    @classmethod
    def is_admin(cls, roles: List[str], user_id: int = None) -> bool:
        """Check if user has admin permissions"""
        # Community managers are always admins
        if user_id and cls.is_community_manager(user_id):
            return True
        
        # Executive Command and Board of Directors have admin permissions
        return cls.is_executive_command(roles) or cls.is_board_of_directors(roles)
    
    @classmethod
    def is_moderator(cls, roles: List[str], user_id: int = None) -> bool:
        """Check if user has moderator permissions"""
        # Community managers and admins have moderator permissions
        if user_id and cls.is_community_manager(user_id):
            return True
        if cls.is_admin(roles, user_id):
            return True
        
        # Department Directors have moderator permissions
        return cls.is_department_director(roles)
    
    @classmethod
    def is_helper(cls, roles: List[str], user_id: int = None) -> bool:
        """Check if user has helper permissions"""
        # Higher roles have helper permissions
        if cls.is_moderator(roles, user_id):
            return True
        
        # Command roles have helper permissions
        role_names = [role.lower() for role in roles]
        return any(role.lower() in role_names for role in cls.COMMAND_ROLES if role)
    
    @classmethod
    def check_guild_authorization(cls, guild_id: int) -> bool:
        """Check if the bot is authorized to work in this guild"""
        return guild_id == cls.AUTHORIZED_GUILD_ID
