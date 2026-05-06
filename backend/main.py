#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Telegram Super-Manager App - Backend
Main entry point for the Telegram bot backend using Pyrogram.
"""

import os
import sys
import configparser
import asyncio

# Fix asyncio event loop error
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())
    
from pyrogram import Client, idle
from pyrogram.errors import ApiIdInvalid, ApiIdPublishedFlood, AuthKeyUnregistered
from loguru import logger

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import handlers
from handlers.group_management import setup_group_handlers
from handlers.mass_messaging import setup_messaging_handlers
from handlers.reporting import setup_reporting_handlers
from db.database import init_db

# Configure logger
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
)
logger.add("logs/bot.log", rotation="10 MB", retention="1 week", level="DEBUG")


class TelegramManager:
    def __init__(self):
        self.config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "config.ini")
        
        if not os.path.exists(config_path):
            logger.error(f"Config file not found at {config_path}")
            sys.exit(1)
            
        self.config.read(config_path)
        
        # Initialize bot client
        try:
            self.api_id = self.config.getint("telegram", "api_id")
            self.api_hash = self.config.get("telegram", "api_hash")
            self.bot_token = self.config.get("telegram", "bot_token")
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            logger.error(f"Config error: {e}. Please check your config.ini file.")
            sys.exit(1)
            
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # Initialize the bot client
        self.bot = Client(
            "tg_super_manager_bot",
            api_id=self.api_id,
            api_hash=self.api_hash,
            bot_token=self.bot_token,
            workdir=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database")
        )
        
    async def start(self):
        try:
            # Initialize database
            await init_db(self.config)
            
            # Start the bot
            await self.bot.start()
            
            # Setup handlers
            setup_group_handlers(self.bot)
            setup_messaging_handlers(self.bot)
            setup_reporting_handlers(self.bot)
            
            bot_info = await self.bot.get_me()
            logger.info(f"Bot started as @{bot_info.username} ({bot_info.id})")
            
            # Keep the bot running
            await idle()
            
        except (ApiIdInvalid, ApiIdPublishedFlood, AuthKeyUnregistered) as e:
            logger.error(f"API Error: {e}. Please check your Telegram API credentials.")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            sys.exit(1)
        finally:
            if self.bot.is_connected:
                await self.bot.stop()


if __name__ == "__main__":
    # Create and run the bot
    manager = TelegramManager()
    loop = asyncio.get_event_loop()
    
    try:
        loop.run_until_complete(manager.start())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        loop.close()