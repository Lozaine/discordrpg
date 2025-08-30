"""
Configuration settings for the One Piece RPG Bot
"""

import os

class Config:
    """Bot configuration class"""
    
    # Bot settings
    COMMAND_PREFIX = "!"
    BOT_DESCRIPTION = "A One Piece RPG Discord Bot where players create their destiny across the seas"
    
    # Data paths
    DATA_DIR = "data"
    CHARACTERS_FILE = "data/characters.json"
    
    # Bot permissions
    REQUIRED_PERMISSIONS = [
        "send_messages",
        "use_slash_commands",
        "embed_links",
        "read_message_history"
    ]
    
    # Character limits
    MAX_CHARACTERS_PER_USER = 3
    
    # XP and progression settings
    BASE_XP_MULTIPLIER = 1.0
    HUMAN_XP_BONUS = 0.1  # +10% for humans
    
    # Embed colors
    EMBED_COLORS = {
        "default": 0x3498db,
        "success": 0x2ecc71,
        "error": 0xe74c3c,
        "warning": 0xf39c12,
        "info": 0x3498db
    }
