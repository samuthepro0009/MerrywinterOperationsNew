"""
Helper utilities for Merrywinter Security Consulting Bot
"""

import discord
from config.settings import Config

def get_user_clearance(roles):
    """Get user's security clearance level based on roles"""
    role_names = [role.name for role in roles]
    return Config.get_security_level(role_names)

def create_embed(title, description, color=None):
    """Create a standardized embed"""
    if color is None:
        color = Config.COLORS['primary']
    
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    return embed

def check_permissions(user_roles, required_level):
    """Check if user has required permission level"""
    user_level = get_user_clearance(user_roles)
    return Config.has_permission(user_level, required_level)

def format_timestamp(timestamp):
    """Format timestamp for display"""
    return timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')

def get_role_color(clearance_level):
    """Get color based on clearance level"""
    color_map = {
        'BOARD_OF_DIRECTORS': Config.COLORS['error'],
        'CHIEF_EXECUTIVE': Config.COLORS['error'],
        'CHIEF_OPERATIONS': Config.COLORS['warning'],
        'CHIEF_CYBERSECURITY': Config.COLORS['warning'],
        'CHIEF_COMPLIANCE': Config.COLORS['warning'],
        'DIRECTOR_SECURITY': Config.COLORS['info'],
        'DIRECTOR_CYBERSECURITY': Config.COLORS['info'],
        'DIRECTOR_PERSONNEL': Config.COLORS['info'],
        'DIRECTOR_INNOVATION': Config.COLORS['info'],
        'DIRECTOR_TACTICAL': Config.COLORS['info'],
        'DIRECTOR_INTELLIGENCE': Config.COLORS['info'],
        'OMEGA': Config.COLORS['omega'],
        'BETA': Config.COLORS['beta'],
        'ALPHA': Config.COLORS['alpha']
    }
    return color_map.get(clearance_level, Config.COLORS['primary'])