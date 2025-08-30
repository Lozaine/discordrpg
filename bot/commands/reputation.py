"""
Faction reputation and standing commands
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import logging

from ..models.faction import FACTIONS, FACTION_RANKS, FactionAlignment, get_faction_benefits
from ..utils.embeds import create_embed
from config import Config

logger = logging.getLogger(__name__)

class ReputationCog(commands.Cog):
    """Faction reputation system commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="reputation", description="View your reputation with all factions")
    async def view_reputation(self, interaction: discord.Interaction):
        """View faction reputation standings"""
        await interaction.response.defer()
        
        user_id = str(interaction.user.id)
        
        try:
            # Get user's character
            user_characters = self.bot.data_manager.get_user_characters(user_id)
            if not user_characters:
                embed = create_embed(
                    "No Character",
                    "❌ You need to create a character first.",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            character = user_characters[0]
            
            # Get faction reputations
            faction_reputations = self.bot.data_manager.get_faction_reputation(user_id, character.name)
            
            # Create reputation embed
            embed = discord.Embed(
                title="🏛️ Faction Reputation",
                description=f"Standing of **{character.name}** with major factions",
                color=Config.EMBED_COLORS["info"]
            )
            
            # Major factions
            major_factions = ["Pirate", "Marine", "Revolutionary", "World Government", "Neutral"]
            
            for faction_name in major_factions:
                faction_data = FACTIONS.get(faction_name, {})
                faction_emoji = faction_data.get("emoji", "⚫")
                
                if faction_name in faction_reputations:
                    rep = faction_reputations[faction_name]
                    alignment = rep.get_alignment()
                    rank_title = rep.get_rank_title()
                    
                    # Alignment emoji
                    alignment_emoji = {
                        FactionAlignment.ALLY: "💚",
                        FactionAlignment.FRIENDLY: "💙", 
                        FactionAlignment.NEUTRAL: "💛",
                        FactionAlignment.HOSTILE: "🧡",
                        FactionAlignment.ENEMY: "❤️"
                    }.get(alignment, "💛")
                    
                    embed.add_field(
                        name=f"{faction_emoji} {faction_name}",
                        value=f"**Rank:** {rank_title}\n"
                              f"**Reputation:** {rep.reputation:,}\n"
                              f"**Standing:** {alignment_emoji} {alignment.value.title()}",
                        inline=True
                    )
                else:
                    # No reputation with this faction
                    embed.add_field(
                        name=f"{faction_emoji} {faction_name}",
                        value=f"**Rank:** Unknown\n"
                              f"**Reputation:** 0\n"
                              f"**Standing:** 💛 Neutral",
                        inline=True
                    )
            
            # Calculate total benefits
            reputation_values = {name: rep.reputation for name, rep in faction_reputations.items()}
            total_benefits = get_faction_benefits(reputation_values)
            
            if total_benefits:
                benefit_text = []
                for benefit, value in total_benefits.items():
                    if isinstance(value, (int, float)) and value > 0:
                        if benefit.endswith("_bonus") or benefit.endswith("_multiplier"):
                            benefit_text.append(f"**{benefit.replace('_', ' ').title()}:** +{value:.1%}")
                        else:
                            benefit_text.append(f"**{benefit.replace('_', ' ').title()}:** +{value}")
                    elif value is True:
                        benefit_text.append(f"**{benefit.replace('_', ' ').title()}:** Enabled")
                
                if benefit_text:
                    embed.add_field(
                        name="⭐ Active Benefits",
                        value="\n".join(benefit_text),
                        inline=False
                    )
            
            embed.set_footer(text="Complete faction quests and actions to improve reputation!")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error viewing reputation: {e}")
            embed = create_embed(
                "Error",
                "❌ An error occurred while loading reputation data.",
                "error"
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="faction_info", description="Get detailed information about a faction")
    @app_commands.describe(faction="Name of the faction to learn about")
    async def faction_info(self, interaction: discord.Interaction, faction: str):
        """Get detailed faction information"""
        await interaction.response.defer()
        
        try:
            # Find faction by name
            faction_data = None
            faction_name = None
            
            for name, data in FACTIONS.items():
                if faction.lower() in name.lower():
                    faction_data = data
                    faction_name = name
                    break
            
            if not faction_data:
                embed = create_embed(
                    "Faction Not Found",
                    f"❌ No faction found matching '{faction}'.",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Create detailed faction embed
            embed = discord.Embed(
                title=f"{faction_data['emoji']} {faction_data['name']}",
                description=faction_data['description'],
                color=faction_data.get('color', Config.EMBED_COLORS["info"])
            )
            
            # Faction relationships
            relationships = []
            if faction_data.get('allied_factions'):
                allies = ', '.join(faction_data['allied_factions'])
                relationships.append(f"**Allies:** {allies}")
            
            if faction_data.get('opposing_factions'):
                enemies = ', '.join(faction_data['opposing_factions'])
                relationships.append(f"**Enemies:** {enemies}")
            
            if relationships:
                embed.add_field(
                    name="🤝 Relationships",
                    value="\n".join(relationships),
                    inline=False
                )
            
            # Faction benefits
            if faction_data.get('benefits'):
                benefit_text = []
                for benefit, value in faction_data['benefits'].items():
                    if isinstance(value, (int, float)):
                        if value < 1:
                            benefit_text.append(f"**{benefit.replace('_', ' ').title()}:** +{value:.1%}")
                        else:
                            benefit_text.append(f"**{benefit.replace('_', ' ').title()}:** +{value}")
                    else:
                        benefit_text.append(f"**{benefit.replace('_', ' ').title()}:** {value}")
                
                embed.add_field(
                    name="⭐ Faction Benefits",
                    value="\n".join(benefit_text),
                    inline=False
                )
            
            # Reputation milestones
            if faction_data.get('milestones'):
                milestone_text = []
                for rep_level, milestone in sorted(faction_data['milestones'].items()):
                    milestone_text.append(f"**{rep_level:,} Rep:** {milestone['name']}")
                
                embed.add_field(
                    name="🏆 Reputation Milestones", 
                    value="\n".join(milestone_text),
                    inline=False
                )
            
            # Rank system
            if faction_name in FACTION_RANKS:
                rank_text = []
                ranks = FACTION_RANKS[faction_name]
                sorted_ranks = sorted(ranks.items(), reverse=True)[:5]  # Show top 5 ranks
                
                for rep_req, rank_info in sorted_ranks:
                    if rep_req >= 0:  # Only show positive reputation ranks
                        rank_text.append(f"**{rep_req:,} Rep:** {rank_info['title']}")
                
                if rank_text:
                    embed.add_field(
                        name="📈 Rank System",
                        value="\n".join(rank_text),
                        inline=False
                    )
            
            embed.set_footer(text=f"Join the {faction_data['name']} to unlock these benefits!")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error showing faction info: {e}")
            embed = create_embed(
                "Error",
                "❌ An error occurred while loading faction information.",
                "error"
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="faction_ranks", description="View the rank structure of a faction")
    @app_commands.describe(faction="Faction to view ranks for")
    async def faction_ranks(self, interaction: discord.Interaction, faction: str):
        """View faction rank structure"""
        await interaction.response.defer()
        
        try:
            # Find faction
            faction_key = None
            for name in FACTION_RANKS.keys():
                if faction.lower() in name.lower():
                    faction_key = name
                    break
            
            if not faction_key:
                embed = create_embed(
                    "Faction Not Found",
                    f"❌ No rank system found for faction '{faction}'.",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            faction_data = FACTIONS.get(faction_key, {})
            ranks = FACTION_RANKS[faction_key]
            
            # Create ranks embed
            embed = discord.Embed(
                title=f"{faction_data.get('emoji', '⚫')} {faction_key} Ranks",
                description=f"Rank structure and progression for the {faction_key}",
                color=faction_data.get('color', Config.EMBED_COLORS["info"])
            )
            
            # Sort ranks by reputation requirement
            sorted_ranks = sorted(ranks.items())
            
            positive_ranks = []
            negative_ranks = []
            
            for rep_req, rank_info in sorted_ranks:
                rank_text = f"**{rank_info['title']}**\n{rank_info['description']}"
                
                if rep_req >= 0:
                    positive_ranks.append((rep_req, rank_text))
                else:
                    negative_ranks.append((rep_req, rank_text))
            
            # Show positive reputation ranks
            if positive_ranks:
                positive_text = []
                for rep_req, rank_text in positive_ranks:
                    positive_text.append(f"**{rep_req:,}+ Rep**\n{rank_text}")
                
                embed.add_field(
                    name="🌟 Positive Standing",
                    value="\n\n".join(positive_text),
                    inline=False
                )
            
            # Show negative reputation ranks
            if negative_ranks:
                negative_text = []
                for rep_req, rank_text in reversed(negative_ranks):  # Worst to least bad
                    negative_text.append(f"**{rep_req:,} Rep**\n{rank_text}")
                
                embed.add_field(
                    name="💀 Negative Standing",
                    value="\n\n".join(negative_text),
                    inline=False
                )
            
            embed.set_footer(text="Complete faction missions and make aligned choices to improve your rank!")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error showing faction ranks: {e}")
            embed = create_embed(
                "Error",
                "❌ An error occurred while loading faction ranks.",
                "error"
            )
            await interaction.followup.send(embed=embed)

# Auto-complete for faction names
async def faction_name_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    """Autocomplete for faction names"""
    choices = []
    
    for faction_name in FACTIONS.keys():
        if current.lower() in faction_name.lower():
            choices.append(app_commands.Choice(name=faction_name, value=faction_name))
        
        if len(choices) >= 25:  # Discord limit
            break
    
    return choices

# Add autocomplete to commands
ReputationCog.faction_info.autocomplete('faction')(faction_name_autocomplete)
ReputationCog.faction_ranks.autocomplete('faction')(faction_name_autocomplete)