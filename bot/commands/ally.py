"""
Ally recruitment and management commands
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import logging

from ..models.ally import AVAILABLE_ALLIES, get_available_allies_for_player, calculate_ally_recruitment_cost
from ..utils.embeds import create_embed
from config import Config

logger = logging.getLogger(__name__)

class AllyCog(commands.Cog):
    """Ally system commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="allies", description="View your recruited allies")
    async def view_allies(self, interaction: discord.Interaction):
        """View recruited allies"""
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
            
            # Get player's allies
            player_allies = self.bot.data_manager.get_player_allies(user_id)
            
            if not player_allies:
                embed = create_embed(
                    "No Allies",
                    "❌ You haven't recruited any allies yet. Use `/ally_recruit` to find companions!",
                    "warning"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Create allies embed
            embed = discord.Embed(
                title="👥 Your Allies",
                description=f"Companions fighting alongside **{character.name}**",
                color=Config.EMBED_COLORS["info"]
            )
            
            total_bonuses = {"strength": 0, "agility": 0, "intelligence": 0, "durability": 0}
            
            for player_ally in player_allies:
                ally_data = AVAILABLE_ALLIES.get(player_ally.ally_id)
                if not ally_data:
                    continue
                
                # Calculate total bonuses
                for stat in total_bonuses:
                    total_bonuses[stat] += ally_data.get_total_stat_bonus(stat)
                
                # Create ally field
                embed.add_field(
                    name=f"{ally_data.emoji} {ally_data.name}",
                    value=f"**{ally_data.title}**\n"
                          f"**Rarity:** {ally_data.rarity.value.title()}\n"
                          f"**Level:** {ally_data.level}/{ally_data.max_level}\n"
                          f"**Bond:** {ally_data.bond_level}/{ally_data.max_bond}\n"
                          f"**Faction:** {ally_data.faction}",
                    inline=True
                )
            
            # Show total stat bonuses
            bonus_text = []
            for stat, bonus in total_bonuses.items():
                if bonus > 0:
                    bonus_text.append(f"**{stat.title()}:** +{bonus}")
            
            if bonus_text:
                embed.add_field(
                    name="⭐ Total Stat Bonuses",
                    value="\n".join(bonus_text),
                    inline=False
                )
            
            embed.set_footer(text="Use /ally_info to see detailed ally information")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error viewing allies: {e}")
            embed = create_embed(
                "Error",
                "❌ An error occurred while loading allies.",
                "error"
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="ally_recruit", description="Browse and recruit available allies")
    async def recruit_ally(self, interaction: discord.Interaction):
        """Browse available allies for recruitment"""
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
            
            # Get available allies
            completed_quests = character.quests_completed
            available_allies = get_available_allies_for_player(character, completed_quests, character.level)
            
            # Filter out already recruited allies
            player_allies = self.bot.data_manager.get_player_allies(user_id)
            recruited_ally_ids = [pa.ally_id for pa in player_allies]
            available_allies = [ally for ally in available_allies if ally.ally_id not in recruited_ally_ids]
            
            if not available_allies:
                embed = create_embed(
                    "No Available Allies",
                    "❌ No allies are currently available for recruitment. Complete more quests to unlock new companions!",
                    "warning"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Create recruitment embed
            embed = discord.Embed(
                title="🤝 Available Allies",
                description="Choose an ally to recruit to your cause:",
                color=Config.EMBED_COLORS["info"]
            )
            
            # Get player's reputation for cost calculation
            faction_reputation = self.bot.data_manager.get_faction_reputation(user_id, character.name)
            reputation_values = {faction: rep.reputation for faction, rep in faction_reputation.items()}
            
            # Show available allies
            for ally in available_allies[:5]:  # Limit to 5 for space
                recruitment_cost = calculate_ally_recruitment_cost(ally, reputation_values)
                
                cost_text = []
                for resource, amount in recruitment_cost.items():
                    cost_text.append(f"{resource}: {amount}")
                
                embed.add_field(
                    name=f"{ally.emoji} {ally.name}",
                    value=f"**{ally.title}**\n"
                          f"**Rarity:** {ally.rarity.value.title()}\n"
                          f"**Faction:** {ally.faction}\n"
                          f"**Cost:** {', '.join(cost_text) if cost_text else 'Free'}",
                    inline=True
                )
            
            # Create recruitment view
            view = AllyRecruitmentView(user_id, available_allies[:5], self.bot)
            
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"Error showing ally recruitment: {e}")
            embed = create_embed(
                "Error",
                "❌ An error occurred while loading available allies.",
                "error"
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="ally_info", description="Get detailed information about an ally")
    @app_commands.describe(ally_name="Name of the ally to view")
    async def ally_info(self, interaction: discord.Interaction, ally_name: str):
        """Get detailed ally information"""
        await interaction.response.defer()
        
        user_id = str(interaction.user.id)
        
        try:
            # Find ally by name
            ally = None
            for ally_data in AVAILABLE_ALLIES.values():
                if ally_name.lower() in ally_data.name.lower():
                    ally = ally_data
                    break
            
            if not ally:
                embed = create_embed(
                    "Ally Not Found",
                    f"❌ No ally found matching '{ally_name}'.",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Create detailed ally embed
            rarity_colors = {
                "common": 0x808080,
                "uncommon": 0x00ff00,
                "rare": 0x0080ff,
                "epic": 0x8000ff,
                "legendary": 0xff8000
            }
            
            embed = discord.Embed(
                title=f"{ally.emoji} {ally.name}",
                description=f"**{ally.title}**\n\n{ally.description}",
                color=rarity_colors.get(ally.rarity.value, Config.EMBED_COLORS["info"])
            )
            
            # Basic info
            embed.add_field(
                name="📊 Basic Info",
                value=f"**Rarity:** {ally.rarity.value.title()}\n"
                      f"**Faction:** {ally.faction}\n"
                      f"**Origin:** {ally.origin or 'Unknown'}\n"
                      f"**Max Level:** {ally.max_level}\n"
                      f"**Max Bond:** {ally.max_bond}",
                inline=True
            )
            
            # Stat bonuses
            if ally.stat_bonuses:
                bonus_text = []
                for stat, bonus in ally.stat_bonuses.items():
                    total_bonus = ally.get_total_stat_bonus(stat)
                    bonus_text.append(f"**{stat.title()}:** +{total_bonus}")
                
                embed.add_field(
                    name="⭐ Stat Bonuses",
                    value="\n".join(bonus_text),
                    inline=True
                )
            
            # Passive effects
            if ally.passive_effects:
                effect_text = []
                for effect, value in ally.passive_effects.items():
                    total_effect = ally.get_passive_effect(effect)
                    effect_text.append(f"**{effect.replace('_', ' ').title()}:** +{total_effect:.1%}")
                
                embed.add_field(
                    name="🌟 Passive Effects",
                    value="\n".join(effect_text),
                    inline=True
                )
            
            # Abilities
            if ally.abilities:
                ability_text = []
                for ability in ally.abilities:
                    cooldown_text = f" (Cooldown: {ability.cooldown}s)" if ability.cooldown > 0 else ""
                    ability_text.append(f"**{ability.name}**{cooldown_text}\n{ability.description}")
                
                embed.add_field(
                    name="⚡ Abilities",
                    value="\n\n".join(ability_text),
                    inline=False
                )
            
            # Recruitment requirements
            if ally.unlock_requirements:
                requirements = []
                for req in ally.unlock_requirements:
                    if req.startswith("complete_quest:"):
                        quest_name = req.split(":", 1)[1].replace("_", " ").title()
                        requirements.append(f"Complete {quest_name}")
                    elif req.startswith("level:"):
                        level = req.split(":")[1]
                        requirements.append(f"Level {level}+")
                    elif req.startswith("faction:"):
                        faction = req.split(":")[1]
                        requirements.append(f"Faction: {faction}")
                    else:
                        requirements.append(req.replace("_", " ").title())
                
                embed.add_field(
                    name="📋 Recruitment Requirements",
                    value="\n".join(requirements),
                    inline=False
                )
            
            # Recruitment cost
            if ally.recruitment_cost:
                cost_text = []
                for resource, amount in ally.recruitment_cost.items():
                    cost_text.append(f"**{resource}:** {amount}")
                
                embed.add_field(
                    name="💰 Recruitment Cost",
                    value="\n".join(cost_text),
                    inline=False
                )
            
            embed.set_footer(text=f"Ally ID: {ally.ally_id}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error showing ally info: {e}")
            embed = create_embed(
                "Error",
                "❌ An error occurred while loading ally information.",
                "error"
            )
            await interaction.followup.send(embed=embed)

class AllyRecruitmentView(discord.ui.View):
    """View for ally recruitment selection"""
    
    def __init__(self, user_id: str, available_allies: list, bot):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.available_allies = available_allies
        self.bot = bot
        
        # Add recruit buttons
        for i, ally in enumerate(available_allies):
            button = discord.ui.Button(
                label=f"{ally.name}",
                style=discord.ButtonStyle.blurple,
                emoji=ally.emoji,
                custom_id=f"recruit_{ally.ally_id}"
            )
            button.callback = self.create_recruit_callback(ally)
            self.add_item(button)
    
    def create_recruit_callback(self, ally):
        """Create callback for recruit button"""
        async def recruit_callback(interaction: discord.Interaction):
            if str(interaction.user.id) != self.user_id:
                await interaction.response.send_message("❌ This is not your ally recruitment menu!", ephemeral=True)
                return
            
            try:
                # Get current character
                character = self.bot.data_manager.get_user_characters(self.user_id)[0]
                
                # Get player's reputation for cost calculation
                faction_reputation = self.bot.data_manager.get_faction_reputation(self.user_id, character.name)
                reputation_values = {faction: rep.reputation for faction, rep in faction_reputation.items()}
                
                # Calculate recruitment cost
                recruitment_cost = calculate_ally_recruitment_cost(ally, reputation_values)
                
                # Check if player can afford the ally
                can_afford = True
                missing_resources = []
                
                for resource, cost in recruitment_cost.items():
                    if resource.lower() == "berry":
                        player_amount = character.inventory.get("Berry", 0)
                    else:
                        player_amount = character.inventory.get(resource, 0)
                    
                    if player_amount < cost:
                        can_afford = False
                        missing_resources.append(f"{resource}: {cost - player_amount} more needed")
                
                if not can_afford:
                    await interaction.response.send_message(
                        f"❌ You cannot afford to recruit {ally.name}.\nMissing: {', '.join(missing_resources)}",
                        ephemeral=True
                    )
                    return
                
                # Recruit the ally
                success = self.bot.data_manager.recruit_ally(self.user_id, character.name, ally.ally_id)
                
                if success:
                    # Deduct costs
                    for resource, cost in recruitment_cost.items():
                        character.remove_item(resource, cost)
                    
                    # Save character
                    self.bot.data_manager.save_character(character)
                    
                    # Create success embed
                    embed = discord.Embed(
                        title="🤝 Ally Recruited!",
                        description=f"**{ally.name}** has joined your cause!",
                        color=Config.EMBED_COLORS["success"]
                    )
                    
                    embed.add_field(
                        name=f"{ally.emoji} {ally.name}",
                        value=f"**{ally.title}**\n"
                              f"**Rarity:** {ally.rarity.value.title()}\n"
                              f"**Faction:** {ally.faction}",
                        inline=False
                    )
                    
                    # Show stat bonuses
                    if ally.stat_bonuses:
                        bonus_text = []
                        for stat, bonus in ally.stat_bonuses.items():
                            total_bonus = ally.get_total_stat_bonus(stat)
                            bonus_text.append(f"**{stat.title()}:** +{total_bonus}")
                        
                        embed.add_field(
                            name="⭐ Stat Bonuses",
                            value="\n".join(bonus_text),
                            inline=True
                        )
                    
                    # Disable all buttons
                    for item in self.children:
                        item.disabled = True
                    
                    await interaction.response.edit_message(embed=embed, view=self)
                    
                    logger.info(f"Ally {ally.ally_id} recruited by {character.name}")
                else:
                    await interaction.response.send_message(
                        "❌ Failed to recruit ally. You may have already recruited them.",
                        ephemeral=True
                    )
                
            except Exception as e:
                logger.error(f"Error recruiting ally: {e}")
                await interaction.response.send_message(
                    "❌ An error occurred while recruiting the ally.",
                    ephemeral=True
                )
        
        return recruit_callback

# Auto-complete for ally names
async def ally_name_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    """Autocomplete for ally names"""
    choices = []
    
    for ally in AVAILABLE_ALLIES.values():
        if current.lower() in ally.name.lower():
            choices.append(app_commands.Choice(name=ally.name, value=ally.name))
        
        if len(choices) >= 25:  # Discord limit
            break
    
    return choices

# Add autocomplete to commands
AllyCog.ally_info.autocomplete('ally_name')(ally_name_autocomplete)