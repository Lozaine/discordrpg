"""
Quest system commands for East Blue Saga
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import logging

from ..models.quest import EAST_BLUE_QUESTS, QuestStatus, QuestType
from ..utils.embeds import create_embed
from config import Config

logger = logging.getLogger(__name__)

class QuestCog(commands.Cog):
    """Quest system commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="quests", description="View available and active quests")
    async def view_quests(self, interaction: discord.Interaction):
        """View available and active quests"""
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
            
            # Get available quests
            available_quests = self.bot.data_manager.get_available_quests(user_id, character.name)
            active_quests = self.bot.data_manager.get_player_quests(user_id)
            active_quests = [q for q in active_quests if q.status == QuestStatus.ACTIVE]
            
            # Create quest embed
            embed = discord.Embed(
                title="📜 Quest Journal",
                description=f"Adventures for **{character.name}** in the East Blue",
                color=Config.EMBED_COLORS["info"]
            )
            
            # Active quests
            if active_quests:
                active_text = []
                for player_quest in active_quests:
                    quest = EAST_BLUE_QUESTS.get(player_quest.quest_id)
                    if quest:
                        progress = quest.get_progress_percentage()
                        active_text.append(f"⚡ **{quest.title}** ({progress:.0f}% complete)")
                
                embed.add_field(
                    name="🔥 Active Quests",
                    value="\n".join(active_text) if active_text else "None",
                    inline=False
                )
            
            # Available quests by arc
            arcs = {}
            for quest in available_quests:
                if quest.arc not in arcs:
                    arcs[quest.arc] = []
                arcs[quest.arc].append(quest)
            
            for arc_name, arc_quests in arcs.items():
                quest_list = []
                for quest in arc_quests:
                    difficulty_emoji = {
                        "Easy": "🟢",
                        "Medium": "🟡", 
                        "Hard": "🟠",
                        "Legendary": "🔴"
                    }.get(quest.difficulty, "⚪")
                    
                    quest_list.append(f"{difficulty_emoji} **{quest.title}**")
                
                embed.add_field(
                    name=f"🏴‍☠️ {arc_name} Arc",
                    value="\n".join(quest_list),
                    inline=True
                )
            
            if not available_quests and not active_quests:
                embed.add_field(
                    name="🚫 No Quests",
                    value="Complete more adventures to unlock new quests!",
                    inline=False
                )
            
            embed.set_footer(text="Use /quest_start to begin a quest or /quest_info for details")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error viewing quests: {e}")
            embed = create_embed(
                "Error",
                "❌ An error occurred while loading quests.",
                "error"
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="quest_info", description="Get detailed information about a quest")
    @app_commands.describe(quest_name="Name of the quest to view")
    async def quest_info(self, interaction: discord.Interaction, quest_name: str):
        """Get detailed quest information"""
        await interaction.response.defer()
        
        user_id = str(interaction.user.id)
        
        try:
            character = self.bot.data_manager.get_user_characters(user_id)[0]
            
            # Find quest by name
            quest = None
            for q in EAST_BLUE_QUESTS.values():
                if quest_name.lower() in q.title.lower():
                    quest = q
                    break
            
            if not quest:
                embed = create_embed(
                    "Quest Not Found",
                    f"❌ No quest found matching '{quest_name}'.",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Check if quest is available
            available_quests = self.bot.data_manager.get_available_quests(user_id, character.name)
            is_available = quest in available_quests
            
            # Create detailed quest embed
            difficulty_color = {
                "Easy": 0x00ff00,
                "Medium": 0xffff00,
                "Hard": 0xff8800,
                "Legendary": 0xff0000
            }.get(quest.difficulty, Config.EMBED_COLORS["info"])
            
            embed = discord.Embed(
                title=f"📜 {quest.title}",
                description=quest.description,
                color=difficulty_color
            )
            
            # Quest details
            embed.add_field(
                name="📊 Quest Details",
                value=f"**Saga:** {quest.saga}\n"
                      f"**Arc:** {quest.arc}\n"
                      f"**Difficulty:** {quest.difficulty}\n"
                      f"**Estimated Duration:** {quest.estimated_duration} minutes\n"
                      f"**Type:** {quest.quest_type.value.replace('_', ' ').title()}",
                inline=True
            )
            
            # Requirements
            requirements = []
            if quest.level_requirement > 1:
                requirements.append(f"Level {quest.level_requirement}+")
            if quest.origin_requirement:
                requirements.append(f"Origin: {', '.join(quest.origin_requirement)}")
            if quest.dream_requirement:
                requirements.append(f"Dream: {', '.join(quest.dream_requirement)}")
            if quest.faction_requirement:
                requirements.append(f"Faction: {', '.join(quest.faction_requirement)}")
            
            if requirements:
                embed.add_field(
                    name="📋 Requirements",
                    value="\n".join(requirements),
                    inline=True
                )
            
            # Rewards
            reward_text = []
            if quest.rewards.experience:
                reward_text.append(f"**Experience:** {quest.rewards.experience} XP")
            if quest.rewards.bounty:
                reward_text.append(f"**Bounty:** ฿{quest.rewards.bounty:,}")
            if quest.rewards.berry:
                reward_text.append(f"**Berry:** ฿{quest.rewards.berry:,}")
            if quest.rewards.items:
                items = [f"{item} x{qty}" for item, qty in quest.rewards.items.items()]
                reward_text.append(f"**Items:** {', '.join(items)}")
            
            if reward_text:
                embed.add_field(
                    name="🏆 Rewards",
                    value="\n".join(reward_text),
                    inline=False
                )
            
            # Objectives
            if quest.objectives:
                objective_text = []
                for i, objective in enumerate(quest.objectives, 1):
                    objective_text.append(f"{i}. {objective.description}")
                
                embed.add_field(
                    name="🎯 Objectives",
                    value="\n".join(objective_text),
                    inline=False
                )
            
            # Availability status
            if is_available:
                embed.add_field(
                    name="✅ Status",
                    value="Available to start!",
                    inline=False
                )
            else:
                embed.add_field(
                    name="🔒 Status",
                    value="Requirements not met or already completed.",
                    inline=False
                )
            
            embed.set_footer(text=f"Quest ID: {quest.quest_id}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error showing quest info: {e}")
            embed = create_embed(
                "Error",
                "❌ An error occurred while loading quest information.",
                "error"
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="quest_start", description="Start a new quest")
    @app_commands.describe(quest_name="Name of the quest to start")
    async def start_quest(self, interaction: discord.Interaction, quest_name: str):
        """Start a new quest"""
        await interaction.response.defer()
        
        user_id = str(interaction.user.id)
        
        try:
            character = self.bot.data_manager.get_user_characters(user_id)[0]
            
            # Find quest by name
            quest = None
            quest_id = None
            for qid, q in EAST_BLUE_QUESTS.items():
                if quest_name.lower() in q.title.lower():
                    quest = q
                    quest_id = qid
                    break
            
            if not quest:
                embed = create_embed(
                    "Quest Not Found",
                    f"❌ No quest found matching '{quest_name}'.",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Check if quest is available
            available_quests = self.bot.data_manager.get_available_quests(user_id, character.name)
            if quest not in available_quests:
                embed = create_embed(
                    "Quest Unavailable",
                    f"❌ The quest '{quest.title}' is not available to you right now.",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Check if already active
            active_quests = self.bot.data_manager.get_player_quests(user_id)
            if any(q.quest_id == quest_id and q.status == QuestStatus.ACTIVE for q in active_quests):
                embed = create_embed(
                    "Quest Already Active",
                    f"❌ You are already working on '{quest.title}'.",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Start the quest
            success = self.bot.data_manager.start_quest(user_id, character.name, quest_id)
            
            if success:
                embed = discord.Embed(
                    title="🚀 Quest Started!",
                    description=f"You have begun **{quest.title}**!",
                    color=Config.EMBED_COLORS["success"]
                )
                
                embed.add_field(
                    name="📖 Description",
                    value=quest.description,
                    inline=False
                )
                
                # Show first objective
                if quest.objectives:
                    first_objective = quest.objectives[0]
                    embed.add_field(
                        name="🎯 Current Objective",
                        value=first_objective.description,
                        inline=False
                    )
                
                embed.add_field(
                    name="💡 Next Steps",
                    value="Complete objectives to progress through the quest!",
                    inline=False
                )
                
                await interaction.followup.send(embed=embed)
                logger.info(f"Quest {quest_id} started for {character.name}")
            else:
                embed = create_embed(
                    "Quest Start Failed",
                    "❌ Failed to start the quest. Please try again.",
                    "error"
                )
                await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error starting quest: {e}")
            embed = create_embed(
                "Error",
                "❌ An error occurred while starting the quest.",
                "error"
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="quest_progress", description="View progress on active quests")
    async def quest_progress(self, interaction: discord.Interaction):
        """View active quest progress"""
        await interaction.response.defer()
        
        user_id = str(interaction.user.id)
        
        try:
            character = self.bot.data_manager.get_user_characters(user_id)[0]
            
            # Get active quests
            active_quests = self.bot.data_manager.get_player_quests(user_id)
            active_quests = [q for q in active_quests if q.status == QuestStatus.ACTIVE]
            
            if not active_quests:
                embed = create_embed(
                    "No Active Quests",
                    "❌ You don't have any active quests. Use `/quests` to see available quests.",
                    "warning"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Create progress embed
            embed = discord.Embed(
                title="📊 Quest Progress",
                description=f"Active quests for **{character.name}**",
                color=Config.EMBED_COLORS["info"]
            )
            
            for player_quest in active_quests:
                quest = EAST_BLUE_QUESTS.get(player_quest.quest_id)
                if not quest:
                    continue
                
                # Calculate progress
                progress = quest.get_progress_percentage()
                progress_bar = self._create_progress_bar(progress)
                
                # Get current objective
                current_objective = quest.get_next_objective()
                objective_text = current_objective.description if current_objective else "All objectives complete!"
                
                embed.add_field(
                    name=f"⚡ {quest.title}",
                    value=f"**Progress:** {progress:.0f}% {progress_bar}\n"
                          f"**Current Objective:** {objective_text}\n"
                          f"**Arc:** {quest.arc}",
                    inline=False
                )
            
            embed.set_footer(text="Complete objectives by engaging in activities!")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error viewing quest progress: {e}")
            embed = create_embed(
                "Error",
                "❌ An error occurred while loading quest progress.",
                "error"
            )
            await interaction.followup.send(embed=embed)
    
    def _create_progress_bar(self, percentage: float) -> str:
        """Create a visual progress bar"""
        filled = int(percentage / 10)
        empty = 10 - filled
        return "▰" * filled + "▱" * empty

# Auto-complete for quest names
async def quest_name_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    """Autocomplete for quest names"""
    user_id = str(interaction.user.id)
    
    try:
        # Get user's available quests
        bot = interaction.client
        if not hasattr(bot, 'data_manager'):
            return []
        
        user_characters = bot.data_manager.get_user_characters(user_id)
        if not user_characters:
            return []
        
        character = user_characters[0]
        available_quests = bot.data_manager.get_available_quests(user_id, character.name)
        
        # Filter quests by current input
        choices = []
        for quest in available_quests:
            if current.lower() in quest.title.lower():
                choices.append(app_commands.Choice(name=quest.title, value=quest.title))
            
            if len(choices) >= 25:  # Discord limit
                break
        
        return choices
    except:
        return []

# Add autocomplete to commands
QuestCog.quest_info.autocomplete('quest_name')(quest_name_autocomplete)
QuestCog.start_quest.autocomplete('quest_name')(quest_name_autocomplete)