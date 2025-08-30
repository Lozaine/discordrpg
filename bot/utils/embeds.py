"""
Discord embed utilities
"""

import discord
from datetime import datetime
from config import Config

def create_embed(title: str, description: str, color_type: str = "default") -> discord.Embed:
    """Create a basic embed with consistent formatting"""
    
    color = Config.EMBED_COLORS.get(color_type, Config.EMBED_COLORS["default"])
    
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.now()
    )
    
    return embed

def create_character_profile_embed(character, races_data, origins_data, dreams_data) -> discord.Embed:
    """Create a detailed character profile embed"""
    
    race_info = races_data[character.race]
    origin_info = origins_data[character.origin]
    dream_info = dreams_data[character.dream]
    
    # Create main embed
    embed = discord.Embed(
        title=f"⚓ {character.name}",
        description=f"*{dream_info['description']}*",
        color=Config.EMBED_COLORS["info"],
        timestamp=datetime.now()
    )
    
    # Add character image/thumbnail (using race emoji as placeholder)
    embed.set_thumbnail(url="https://i.imgur.com/placeholder.png")  # Placeholder for future character avatars
    
    # Basic info field
    basic_info = (
        f"**Race:** {race_info['emoji']} {character.race}\n"
        f"**Origin:** {origin_info['emoji']} {character.origin}\n"
        f"**Faction:** {origin_info['faction']}\n"
        f"**Dream:** {dream_info['emoji']} {character.dream}"
    )
    embed.add_field(name="📝 Basic Info", value=basic_info, inline=True)
    
    # Stats field
    stats_info = []
    base_stats = character.stats
    race_bonuses = race_info['stats']
    
    for stat_name, base_value in base_stats.items():
        bonus = race_bonuses.get(stat_name, 0)
        total = base_value + bonus
        
        if bonus > 0:
            stats_info.append(f"**{stat_name.title()}:** {base_value} + {bonus} = {total}")
        else:
            stats_info.append(f"**{stat_name.title()}:** {total}")
    
    embed.add_field(name="💪 Stats", value="\n".join(stats_info), inline=True)
    
    # Level and experience
    level_info = (
        f"**Level:** {character.level}\n"
        f"**Experience:** {character.experience:,} XP\n"
        f"**Next Level:** {character.get_xp_for_next_level():,} XP"
    )
    embed.add_field(name="⭐ Progression", value=level_info, inline=True)
    
    # Race abilities
    race_abilities = f"**{race_info['ability']}**\n{race_info.get('extra', 'No additional effects.')}"
    embed.add_field(name="🌟 Racial Abilities", value=race_abilities, inline=False)
    
    # Dream benefits
    dream_benefits = (
        f"**Starting Bonus:** {dream_info['bonus']}\n"
        f"**Unlocks:** {dream_info['unlocks']}"
    )
    embed.add_field(name="💭 Dream Benefits", value=dream_benefits, inline=False)
    
    # Origin story
    embed.add_field(
        name=f"🏝️ Origin Story - {character.origin}",
        value=f"**{origin_info['story']}**\n{origin_info['description']}",
        inline=False
    )
    
    # Footer with creation date and other info
    embed.set_footer(
        text=f"Character created on {character.created_at.strftime('%B %d, %Y')} • Bounty: ฿{character.bounty:,}",
        icon_url="https://i.imgur.com/onepiece_logo.png"  # Placeholder for One Piece logo
    )
    
    return embed

def create_error_embed(title: str, message: str) -> discord.Embed:
    """Create an error embed"""
    return create_embed(title, f"❌ {message}", "error")

def create_success_embed(title: str, message: str) -> discord.Embed:
    """Create a success embed"""
    return create_embed(title, f"✅ {message}", "success")

def create_warning_embed(title: str, message: str) -> discord.Embed:
    """Create a warning embed"""
    return create_embed(title, f"⚠️ {message}", "warning")

def create_info_embed(title: str, message: str) -> discord.Embed:
    """Create an info embed"""
    return create_embed(title, f"ℹ️ {message}", "info")
