"""
Main bot client implementation
"""

import discord
from discord.ext import commands
import logging
import os
from .commands.character import CharacterCog
from .commands.crew import CrewCog
from .commands.combat import CombatCog
from .commands.ship import ShipCog
from .commands.quest import QuestCog
from .commands.ally import AllyCog
from .commands.reputation import ReputationCog
from .utils.system_manager import SystemManager
from config import Config

logger = logging.getLogger(__name__)

class OnePieceRPGBot(commands.Bot):
    """Main bot class for One Piece RPG"""
    
    def __init__(self):
        # Set up bot intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        super().__init__(
            command_prefix=Config.COMMAND_PREFIX,
            description=Config.BOT_DESCRIPTION,
            intents=intents
        )
        
        # Initialize system manager
        self.data_manager = SystemManager()
        
        # Track if bot is ready
        self.is_ready_flag = False
    
    async def setup_hook(self):
        """Called when bot is starting up"""
        logger.info("Setting up bot...")
        
        # Ensure data directory exists
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        
        # Load all cogs
        await self.add_cog(CharacterCog(self))
        await self.add_cog(CrewCog(self))
        await self.add_cog(CombatCog(self))
        await self.add_cog(ShipCog(self))
        await self.add_cog(QuestCog(self))
        await self.add_cog(AllyCog(self))
        await self.add_cog(ReputationCog(self))
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} slash commands")
        except Exception as e:
            logger.error(f"Failed to sync slash commands: {e}")
    
    async def on_ready(self):
        """Called when bot is ready"""
        if not self.is_ready_flag:
            logger.info(f"🌊 {self.user} has awakened and is ready to sail the Grand Line!")
            logger.info(f"Connected to {len(self.guilds)} servers")
            logger.info(f"Serving {len(set(self.get_all_members()))} pirates, marines, and revolutionaries")
            
            # Set bot status
            activity = discord.Activity(
                type=discord.ActivityType.watching,
                name="the Grand Line for adventures"
            )
            await self.change_presence(activity=activity)
            
            self.is_ready_flag = True
    
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore unknown commands
        
        logger.error(f"Command error in {ctx.command}: {error}")
        
        if hasattr(ctx, 'respond'):
            await ctx.respond("❌ An error occurred while processing your command.", ephemeral=True)
        else:
            await ctx.send("❌ An error occurred while processing your command.")
    
    async def on_application_command_error(self, ctx, error):
        """Handle slash command errors"""
        logger.error(f"Slash command error in {ctx.command}: {error}")
        
        error_message = "❌ An unexpected error occurred."
        
        if isinstance(error, commands.MissingRequiredArgument):
            error_message = f"❌ Missing required argument: {error.param.name}"
        elif isinstance(error, commands.BadArgument):
            error_message = "❌ Invalid argument provided."
        
        try:
            if ctx.response.is_done():
                await ctx.followup.send(error_message, ephemeral=True)
            else:
                await ctx.response.send_message(error_message, ephemeral=True)
        except:
            pass  # Ignore if we can't send error message
