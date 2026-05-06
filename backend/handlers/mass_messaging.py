#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mass messaging handlers for Telegram Super-Manager App.
Implements features for mass DM to subscribers, mass forwarding to groups,
filtering subscribers, and handling flood wait limits.
"""

import os
import sys
import time
import asyncio

# Fix asyncio event loop error
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())
    
from typing import List, Dict, Union, Optional
from pyrogram import Client, filters
from pyrogram.types import Message, User, Chat
from pyrogram.errors import FloodWait, UserIsBlocked, PeerIdInvalid, UserPrivacyRestricted
from loguru import logger

# Import database functions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.database import get_db

# Constants for rate limiting
MAX_MESSAGES_PER_MINUTE = 20
MAX_FORWARDS_PER_MINUTE = 15
DELAY_BETWEEN_MESSAGES = 3  # seconds


def setup_messaging_handlers(bot: Client):
    """
    Set up all mass messaging handlers for the bot.
    """
    
    @bot.on_message(filters.command(["massdm"]) & filters.private)
    async def mass_dm_command(client: Client, message: Message):
        """
        Handle the mass DM command.
        Usage: /massdm -c <channel_id> -m <message> [-f active|all]
        """
        user_id = message.from_user.id
        
        try:
            # Check if user is authorized (admin)
            conn = await get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT is_admin FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            
            if not result or not result[0]:
                await message.reply_text("You are not authorized to use this command.")
                return
            
            # Parse command arguments
            args = message.text.split(" ")
            if len(args) < 5:
                await message.reply_text(
                    "Invalid command format.\n"
                    "Usage: /massdm -c <channel_id> -m <message> [-f active|all]\n"
                    "Example: /massdm -c -1001234567890 -m Hello subscribers! -f active"
                )
                return
            
            # Extract channel ID and message
            channel_id = None
            dm_message = ""
            filter_type = "all"  # Default filter
            
            i = 1
            while i < len(args):
                if args[i] == "-c" and i + 1 < len(args):
                    try:
                        channel_id = int(args[i + 1])
                        i += 2
                    except ValueError:
                        await message.reply_text("Invalid channel ID. Please provide a numeric ID.")
                        return
                elif args[i] == "-m" and i + 1 < len(args):
                    # Collect all text after -m until next flag or end
                    j = i + 1
                    while j < len(args) and not args[j].startswith("-"):
                        dm_message += args[j] + " "
                        j += 1
                    dm_message = dm_message.strip()
                    i = j
                elif args[i] == "-f" and i + 1 < len(args):
                    filter_type = args[i + 1].lower()
                    if filter_type not in ["active", "all"]:
                        await message.reply_text("Invalid filter type. Use 'active' or 'all'.")
                        return
                    i += 2
                else:
                    i += 1
            
            if not channel_id:
                await message.reply_text("Channel ID is required.")
                return
            
            if not dm_message:
                await message.reply_text("Message content is required.")
                return
            
            # Start the mass DM process
            status_message = await message.reply_text("Starting mass DM process...")
            
            # Get subscribers
            subscribers = await get_channel_subscribers(client, channel_id, filter_type)
            
            if not subscribers:
                await status_message.edit_text("No subscribers found or you don't have access to this channel.")
                return
            
            await status_message.edit_text(f"Sending message to {len(subscribers)} subscribers...")
            
            # Send messages with rate limiting
            success_count = 0
            fail_count = 0
            
            for i, user in enumerate(subscribers):
                try:
                    # Rate limiting
                    if i > 0 and i % MAX_MESSAGES_PER_MINUTE == 0:
                        await status_message.edit_text(
                            f"Sent to {success_count}/{len(subscribers)} subscribers. "
                            f"Failed: {fail_count}. Waiting to avoid rate limits..."
                        )
                        await asyncio.sleep(60)  # Wait a minute after every MAX_MESSAGES_PER_MINUTE messages
                    
                    # Send message
                    await client.send_message(user.id, dm_message)
                    success_count += 1
                    
                    # Small delay between messages
                    await asyncio.sleep(DELAY_BETWEEN_MESSAGES)
                    
                    # Update status every 10 messages
                    if i % 10 == 0:
                        await status_message.edit_text(
                            f"Progress: {i+1}/{len(subscribers)} subscribers. "
                            f"Success: {success_count}, Failed: {fail_count}"
                        )
                    
                except FloodWait as e:
                    await status_message.edit_text(f"Rate limited. Waiting for {e.x} seconds...")
                    await asyncio.sleep(e.x)
                    # Try again
                    try:
                        await client.send_message(user.id, dm_message)
                        success_count += 1
                    except Exception:
                        fail_count += 1
                except (UserIsBlocked, PeerIdInvalid, UserPrivacyRestricted):
                    # User has blocked the bot or has privacy settings
                    fail_count += 1
                except Exception as e:
                    logger.error(f"Error sending message to user {user.id}: {e}")
                    fail_count += 1
            
            # Final status update
            await status_message.edit_text(
                f"Mass DM completed.\n"
                f"Total subscribers: {len(subscribers)}\n"
                f"Successfully sent: {success_count}\n"
                f"Failed: {fail_count}"
            )
            
            # Log the action
            cursor.execute(
                "INSERT INTO logs (entity_id, entity_type, action, user_id, admin_id, reason) VALUES (?, ?, ?, ?, ?, ?)",
                (channel_id, "channel", "mass_dm", None, user_id, f"Mass DM to {len(subscribers)} subscribers")
            )
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error in mass_dm_command: {e}")
            await message.reply_text(f"Error: {str(e)}")
    
    @bot.on_message(filters.command(["massforward"]) & filters.private)
    async def mass_forward_command(client: Client, message: Message):
        """
        Handle the mass forward command.
        Usage: /massforward -s <source_chat_id> -t <target_chat_ids> -m <message_id>
        """
        user_id = message.from_user.id
        
        try:
            # Check if user is authorized (admin)
            conn = await get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT is_admin FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            
            if not result or not result[0]:
                await message.reply_text("You are not authorized to use this command.")
                return
            
            # Parse command arguments
            args = message.text.split(" ")
            if len(args) < 7:
                await message.reply_text(
                    "Invalid command format.\n"
                    "Usage: /massforward -s <source_chat_id> -t <target_chat_ids> -m <message_id>\n"
                    "Example: /massforward -s -1001234567890 -t -1001234567891,-1001234567892 -m 123"
                )
                return
            
            # Extract parameters
            source_chat_id = None
            target_chat_ids = []
            message_id = None
            
            i = 1
            while i < len(args):
                if args[i] == "-s" and i + 1 < len(args):
                    try:
                        source_chat_id = int(args[i + 1])
                        i += 2
                    except ValueError:
                        await message.reply_text("Invalid source chat ID. Please provide a numeric ID.")
                        return
                elif args[i] == "-t" and i + 1 < len(args):
                    try:
                        # Split by comma for multiple target chats
                        target_ids = args[i + 1].split(",")
                        target_chat_ids = [int(chat_id.strip()) for chat_id in target_ids]
                        i += 2
                    except ValueError:
                        await message.reply_text("Invalid target chat IDs. Please provide numeric IDs separated by commas.")
                        return
                elif args[i] == "-m" and i + 1 < len(args):
                    try:
                        message_id = int(args[i + 1])
                        i += 2
                    except ValueError:
                        await message.reply_text("Invalid message ID. Please provide a numeric ID.")
                        return
                else:
                    i += 1
            
            if not source_chat_id:
                await message.reply_text("Source chat ID is required.")
                return
            
            if not target_chat_ids:
                await message.reply_text("Target chat IDs are required.")
                return
            
            if not message_id:
                await message.reply_text("Message ID is required.")
                return
            
            # Start the mass forward process
            status_message = await message.reply_text("Starting mass forward process...")
            
            # Forward the message to all target chats
            success_count = 0
            fail_count = 0
            
            for i, chat_id in enumerate(target_chat_ids):
                try:
                    # Rate limiting
                    if i > 0 and i % MAX_FORWARDS_PER_MINUTE == 0:
                        await status_message.edit_text(
                            f"Forwarded to {success_count}/{len(target_chat_ids)} chats. "
                            f"Failed: {fail_count}. Waiting to avoid rate limits..."
                        )
                        await asyncio.sleep(60)  # Wait a minute after every MAX_FORWARDS_PER_MINUTE forwards
                    
                    # Forward message
                    await client.forward_messages(chat_id, source_chat_id, message_id)
                    success_count += 1
                    
                    # Small delay between forwards
                    await asyncio.sleep(DELAY_BETWEEN_MESSAGES)
                    
                except FloodWait as e:
                    await status_message.edit_text(f"Rate limited. Waiting for {e.x} seconds...")
                    await asyncio.sleep(e.x)
                    # Try again
                    try:
                        await client.forward_messages(chat_id, source_chat_id, message_id)
                        success_count += 1
                    except Exception:
                        fail_count += 1
                except Exception as e:
                    logger.error(f"Error forwarding message to chat {chat_id}: {e}")
                    fail_count += 1
            
            # Final status update
            await status_message.edit_text(
                f"Mass forward completed.\n"
                f"Total target chats: {len(target_chat_ids)}\n"
                f"Successfully forwarded: {success_count}\n"
                f"Failed: {fail_count}"
            )
            
            # Log the action
            cursor.execute(
                "INSERT INTO logs (entity_id, entity_type, action, user_id, admin_id, reason) VALUES (?, ?, ?, ?, ?, ?)",
                (source_chat_id, "channel", "mass_forward", None, user_id, f"Mass forward to {len(target_chat_ids)} chats")
            )
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error in mass_forward_command: {e}")
            await message.reply_text(f"Error: {str(e)}")


async def get_channel_subscribers(client: Client, channel_id: int, filter_type: str = "all") -> List[User]:
    """
    Get subscribers of a channel with optional filtering.
    
    Args:
        client: The Pyrogram client
        channel_id: The channel ID
        filter_type: 'all' for all subscribers, 'active' for active subscribers only
        
    Returns:
        List of User objects
    """
    try:
        # Check if the bot has access to the channel
        try:
            chat = await client.get_chat(channel_id)
            if chat.type not in ["channel", "supergroup"]:
                logger.warning(f"Chat {channel_id} is not a channel or supergroup")
                return []
        except Exception as e:
            logger.error(f"Error accessing channel {channel_id}: {e}")
            return []
        
        # Get all subscribers
        # Note: This is a simplified implementation
        # In a real app, you would need to use Telethon or other methods to get all subscribers
        # as Pyrogram doesn't provide direct access to all subscribers
        
        # For demonstration purposes, we'll use a mock implementation
        subscribers = []
        
        # In a real implementation, you would get actual subscribers
        # For now, we'll just return an empty list with a note
        logger.info("Note: Getting actual subscribers requires Telethon or admin access to the channel")
        
        # Filter subscribers if needed
        if filter_type == "active" and subscribers:
            # In a real implementation, you would filter based on activity
            # For now, we'll just return all subscribers
            pass
        
        return subscribers
        
    except Exception as e:
        logger.error(f"Error getting channel subscribers: {e}")
        return []