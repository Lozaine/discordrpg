"""
Character creation and management commands
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional

import asyncio
import logging

from ..models.character import Character
from ..models.races import RACES
from ..models.origins import ORIGINS
from ..models.dreams import DREAMS
from ..utils.embeds import create_embed, create_character_profile_embed

from ..utils.postgres_data_manager import PostgresDataManager
from config import Config

logger = logging.getLogger(__name__)

class CharacterCog(commands.Cog):
    """Character management commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.data_manager = PostgresDataManager()
    
    @app_commands.command(name="create_character", description="Create a new One Piece RPG character")
    @app_commands.describe(
        name="Your character's name",
        race="Choose your character's race",
        origin="Choose your character's origin island",
        dream="Choose your character's dream/goal"
    )
    async def create_character(
        self, 
        interaction: discord.Interaction,
        name: str,
        race: str,
        origin: str,
        dream: str
    ):
        """Create a new character"""
        await interaction.response.defer()
        
        user_id = str(interaction.user.id)
        
        try:
            # Check if user already has max characters
            user_characters = await self.data_manager.get_user_characters(user_id)
            if len(user_characters) >= Config.MAX_CHARACTERS_PER_USER:
                embed = create_embed(
                    "Character Creation Failed",
                    f"❌ You can only have {Config.MAX_CHARACTERS_PER_USER} characters maximum.",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Check if character name already exists for this user
            if any(char.name.lower() == name.lower() for char in user_characters):
                embed = create_embed(
                    "Character Creation Failed",
                    "❌ You already have a character with that name.",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Validate race
            if race not in RACES:
                available_races = ", ".join(RACES.keys())
                embed = create_embed(
                    "Invalid Race",
                    f"❌ Invalid race. Available races: {available_races}",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Validate origin
            if origin not in ORIGINS:
                available_origins = ", ".join(ORIGINS.keys())
                embed = create_embed(
                    "Invalid Origin",
                    f"❌ Invalid origin. Available origins: {available_origins}",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Validate dream
            if dream not in DREAMS:
                available_dreams = ", ".join(DREAMS.keys())
                embed = create_embed(
                    "Invalid Dream",
                    f"❌ Invalid dream. Available dreams: {available_dreams}",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Create the character
            character = Character(
                user_id=user_id,
                name=name,
                race=race,
                origin=origin,
                dream=dream
            )
            # Save character
            await self.data_manager.save_character(character)
            
            # Create success embed
            embed = create_character_profile_embed(character, RACES, ORIGINS, DREAMS)
            embed.title = "🎉 Character Created Successfully!"
            embed.color = Config.EMBED_COLORS["success"]
            
            await interaction.followup.send(embed=embed)
            logger.info(f"Character created: {name} by user {user_id}")
            
        except Exception as e:
            logger.error(f"Error creating character: {e}")
            embed = create_embed(
                "Error",
                "❌ An error occurred while creating your character.",
                "error"
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="character", description="View your character profile")
    @app_commands.describe(character_name="Name of the character to view (optional)")
    async def view_character(
        self,
        interaction: discord.Interaction,
        character_name: Optional[str] = None
    ):
        """View character profile"""
        await interaction.response.defer()
        
        user_id = str(interaction.user.id)
        
        try:
            user_characters = await self.data_manager.get_user_characters(user_id)
            
            if not user_characters:
                embed = create_embed(
                    "No Character Found",
                    "❌ You don't have any characters yet. Use `/create_character` to create one!",
                    "warning"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # If no character name specified, use the first one
            if character_name is None:
                character = user_characters[0]
            else:
                # Find character by name
                character = None
                for char in user_characters:
                    if char.name.lower() == character_name.lower():
                        character = char
                        break
                if character is None:
                    character_names = ", ".join(char.name for char in user_characters)
                    embed = create_embed(
                        "Character Not Found",
                        f"❌ Character '{character_name}' not found. Your characters: {character_names}",
                        "error"
                    )
                    await interaction.followup.send(embed=embed)
                    return
            
            # Create character profile embed
            embed = create_character_profile_embed(character, RACES, ORIGINS, DREAMS)
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error viewing character: {e}")
            embed = create_embed(
                "Error",
                "❌ An error occurred while retrieving your character.",
                "error"
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="characters", description="List all your characters")
    async def list_characters(self, interaction: discord.Interaction):
        """List all user's characters"""
        await interaction.response.defer()
        
        user_id = str(interaction.user.id)
        
        try:
            user_characters = await self.data_manager.get_user_characters(user_id)
            
            if not user_characters:
                embed = create_embed(
                    "No Characters",
                    "❌ You don't have any characters yet. Use `/create_character` to create one!",
                    "warning"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Create character list embed
            embed = discord.Embed(
                title=f"🏴‍☠️ {interaction.user.display_name}'s Characters",
                color=Config.EMBED_COLORS["info"]
            )
            
            for i, character in enumerate(user_characters, 1):
                race_info = RACES[character.race]
                origin_info = ORIGINS[character.origin]
                
                embed.add_field(
                    name=f"{i}. {character.name}",
                    value=f"**Race:** {character.race}\n"
                          f"**Origin:** {character.origin}\n"
                          f"**Faction:** {origin_info['faction']}\n"
                          f"**Dream:** {character.dream}",
                    inline=True
                )
            
            embed.set_footer(text=f"Total Characters: {len(user_characters)}/{Config.MAX_CHARACTERS_PER_USER}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error listing characters: {e}")
            embed = create_embed(
                "Error",
                "❌ An error occurred while retrieving your characters.",
                "error"
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="races", description="View available character races")
    async def view_races(self, interaction: discord.Interaction):
        """Display available races"""
        await interaction.response.defer()
        
        embed = discord.Embed(
            title="🧬 Available Races",
            description="Choose your character's race to determine their stats and abilities:",
            color=Config.EMBED_COLORS["info"]
        )
        
        for race_name, race_data in RACES.items():
            stats_text = ", ".join([f"{stat}: +{bonus}" for stat, bonus in race_data["stats"].items()])
            
            embed.add_field(
                name=f"{race_data['emoji']} {race_name}",
                value=f"**Stats:** {stats_text}\n"
                      f"**Ability:** {race_data['ability']}\n"
                      f"**Description:** {race_data['description']}",
                inline=False
            )
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="origins", description="View available origin islands")
    async def view_origins(self, interaction: discord.Interaction):
        """Display available origins"""
        await interaction.response.defer()
        
        embed = discord.Embed(
            title="🏝️ Origin Islands",
            description="Choose where your character begins their journey:",
            color=Config.EMBED_COLORS["info"]
        )
        
        for origin_name, origin_data in ORIGINS.items():
            embed.add_field(
                name=f"{origin_data['emoji']} {origin_name}",
                value=f"**Default Faction:** {origin_data['faction']}\n"
                      f"**Story Arc:** {origin_data['story']}\n"
                      f"**Description:** {origin_data['description']}",
                inline=False
            )
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="dreams", description="View available character dreams")
    async def view_dreams(self, interaction: discord.Interaction):
        """Display available dreams"""
        await interaction.response.defer()
        
        embed = discord.Embed(
            title="💭 Character Dreams",
            description="Choose your character's ultimate goal:",
            color=Config.EMBED_COLORS["info"]
        )
        
        for dream_name, dream_data in DREAMS.items():
            embed.add_field(
                name=f"{dream_data['emoji']} {dream_name}",
                value=f"**Starting Bonus:** {dream_data['bonus']}\n"
                      f"**Unlocks:** {dream_data['unlocks']}\n"
                      f"**Description:** {dream_data['description']}",
                inline=False
            )
        
        await interaction.followup.send(embed=embed)

    # Autocomplete functions for slash commands
    @create_character.autocomplete('race')
    async def race_autocomplete(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=f"{data['emoji']} {race}", value=race)
            for race, data in RACES.items()
            if current.lower() in race.lower()
        ][:25]
    
    @create_character.autocomplete('origin')
    async def origin_autocomplete(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=f"{data['emoji']} {origin}", value=origin)
            for origin, data in ORIGINS.items()
            if current.lower() in origin.lower()
        ][:25]
    
    @create_character.autocomplete('dream')
    async def dream_autocomplete(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=f"{data['emoji']} {dream}", value=dream)
            for dream, data in DREAMS.items()
            if current.lower() in dream.lower()
        ][:25]
    
    @view_character.autocomplete('character_name')
    async def character_autocomplete(self, interaction: discord.Interaction, current: str):
        user_id = str(interaction.user.id)
        user_characters = await self.data_manager.get_user_characters(user_id)
        return [
            app_commands.Choice(name=char.name, value=char.name)
            for char in user_characters
            if current.lower() in char.name.lower()
        ][:25]
