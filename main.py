#!/usr/bin/env python3
"""
One Piece RPG Discord Bot
Main entry point for the bot application
"""

import asyncio
import logging
import os
from bot.client import OnePieceRPGBot
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Main function to start the bot"""
    try:
        # Get bot token from environment
        token = os.getenv('DISCORD_BOT_TOKEN')
        if not token:
            logger.error("DISCORD_BOT_TOKEN environment variable not set!")
            return
        
        # Create and start the bot
        bot = OnePieceRPGBot()
        
        logger.info("Starting One Piece RPG Bot...")
        await bot.start(token)
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
