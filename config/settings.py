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
    
    # Security Clearance Levels (Based on org chart)
    SECURITY_LEVELS = {
        'BOARD_OF_DIRECTORS': 10,
        'CHIEF_EXECUTIVE': 9,
        'CHIEF_OPERATIONS': 8,
        'CHIEF_CYBERSECURITY': 8,
        'CHIEF_COMPLIANCE': 8,
        'DIRECTOR_SECURITY': 7,
        'DIRECTOR_CYBERSECURITY': 7,
        'DIRECTOR_PERSONNEL': 7,
        'DIRECTOR_INNOVATION': 7,
        'DIRECTOR_TACTICAL': 6,
        'DIRECTOR_INTELLIGENCE': 6,
        'CONVOY_ESCORT': 5,
        'RECON_SURVEILLANCE': 5,
        'TRAINING_COMBAT': 5,
        'EXECUTIVE_PROTECTION': 5,
        'TACTICAL_DEPLOYMENT': 4,
        'OMEGA': 3,
        'BETA': 2,
        'ALPHA': 1
    }
    
    # Role Configuration - COMPLETE role names from the guild
    BOARD_OF_DIRECTORS_ROLES = ["Board of Directors", "Merrywinter Security Consulting"]
    
    # Executive Level Roles
    CHIEF_EXECUTIVE_ROLES = ["CEO", "Executive Command"]
    
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
    
    # Moderation Configuration
    COMMUNITY_MANAGERS = [618708505393889300, 700659364574396438, 972959357971103834, 488052909867532288]
    ADMIN_ROLES = ["Board of Directors", "CEO", "Executive Command"] + DIRECTOR_SECURITY_ROLES
    MODERATOR_ROLES = COMMAND_ROLES[:10]  # First 10 command roles as moderators
    HELPER_ROLES = COMMAND_ROLES[10:] + ["Verified"]  # Remaining command roles + verified users
    
    # Channel Configuration
    TICKET_CATEGORY = "TICKET SYSTEM"
    LOG_CHANNEL = "bot-logs"
    
    # Channel IDs from the guild
    TICKET_CATEGORY_ID = 1393249646192754698
    LOG_CHANNEL_ID = 1393249520388935793
    

    
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
            ('BOARD_OF_DIRECTORS', cls.BOARD_OF_DIRECTORS_ROLES),
            ('CHIEF_EXECUTIVE', cls.CHIEF_EXECUTIVE_ROLES),
            ('DIRECTOR_SECURITY', cls.DIRECTOR_SECURITY_ROLES),
            ('CONVOY_ESCORT', cls.CONVOY_ESCORT_ROLES),
            ('RECON_SURVEILLANCE', cls.RECON_SURVEILLANCE_ROLES),
            ('TRAINING_COMBAT', cls.TRAINING_COMBAT_ROLES),
            ('EXECUTIVE_PROTECTION', cls.EXECUTIVE_PROTECTION_ROLES),
            ('TACTICAL_DEPLOYMENT', cls.TACTICAL_DEPLOYMENT_ROLES),
            ('INTELLIGENCE', cls.INTELLIGENCE_ROLES),
            ('OMEGA', cls.OMEGA_ROLES),
            ('BETA', cls.BETA_ROLES),
            ('ALPHA', cls.ALPHA_ROLES)
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
    def is_admin(cls, roles: List[str], user_id: int = None) -> bool:
        """Check if user has admin permissions"""
        # Community managers are always admins
        if user_id and cls.is_community_manager(user_id):
            return True
            
        role_names = [role.lower() for role in roles]
        
        for role in cls.ADMIN_ROLES:
            if role and role.lower() in role_names:
                return True
        
        return False
    
    @classmethod
    def is_moderator(cls, roles: List[str], user_id: int = None) -> bool:
        """Check if user has moderator permissions"""
        # Community managers and admins have moderator permissions
        if user_id and cls.is_community_manager(user_id):
            return True
        if cls.is_admin(roles, user_id):
            return True
            
        role_names = [role.lower() for role in roles]
        
        for role in cls.MODERATOR_ROLES:
            if role and role.lower() in role_names:
                return True
        
        return False
    
    @classmethod
    def is_helper(cls, roles: List[str], user_id: int = None) -> bool:
        """Check if user has helper permissions"""
        # Higher roles have helper permissions
        if cls.is_moderator(roles, user_id):
            return True
            
        role_names = [role.lower() for role in roles]
        
        for role in cls.HELPER_ROLES:
            if role and role.lower() in role_names:
                return True
        
        return False
    
    @classmethod
    def check_guild_authorization(cls, guild_id: int) -> bool:
        """Check if the bot is authorized to work in this guild"""
        return guild_id == cls.AUTHORIZED_GUILD_ID
