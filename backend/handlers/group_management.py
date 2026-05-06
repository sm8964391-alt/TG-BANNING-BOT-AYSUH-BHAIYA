#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Group management handlers for Telegram Super-Manager App.
Implements features like auto-kick spammers, auto-delete NSFW/phishing,
custom welcome messages, and logging.
"""

import re
import os
import sys
import time
import asyncio

# Fix asyncio event loop error
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())
    
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.errors import FloodWait, UserAdminInvalid
from loguru import logger

# Import database functions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.database import get_db

# Regex patterns for detecting spam, NSFW, and phishing
SPAM_PATTERNS = [
    r'\b(?:buy|sell|discount|offer|promo|click|earn|\$\$\$)\b.*\b(?:now|fast|quick|easy|money|cash)\b',
    r'\b(?:bitcoin|crypto|investment|forex|binary options).*\b(?:profit|earn|money|cash|income)\b',
    r'(?i)\b(?:viagra|cialis|enlargement|diet pill)\b',
]

NSFW_PATTERNS = [
    r'(?i)\b(?:porn|xxx|sex|adult|nude|naked)\b',
    r'(?i)\b(?:onlyfans|cam girl|webcam)\b',
]

PHISHING_PATTERNS = [
    r'(?:bit\.ly|goo\.gl|t\.me|tinyurl\.com|is\.gd).*(?:login|account|verify|password|bank|wallet)',
    r'(?i)\b(?:verify your account|password reset|unusual activity|login attempt)\b',
]


def setup_group_handlers(bot: Client):
    """
    Set up all group management handlers for the bot.
    """
    
    @bot.on_message(filters.group & filters.new_chat_members)
    async def welcome_new_members(client: Client, message: Message):
        """
        Send welcome message to new chat members.
        """
        chat_id = message.chat.id
        
        try:
            # Get custom welcome message from database
            conn = await get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT welcome_message FROM groups WHERE group_id = ?", (chat_id,))
            result = cursor.fetchone()
            
            if result and result[0]:
                welcome_message = result[0]
            else:
                # Default welcome message
                welcome_message = f"Welcome to {message.chat.title}! Please read the rules and enjoy your stay."
            
            # Get mentioned users
            new_members = ", ".join([f"@{u.username}" if u.username else u.first_name for u in message.new_chat_members])
            
            # Send welcome message
            await message.reply_text(f"{welcome_message}\n\nWelcome, {new_members}!")
            
            # Log the new members
            for user in message.new_chat_members:
                cursor.execute(
                    "INSERT OR IGNORE INTO users (user_id, username, first_name, last_name) VALUES (?, ?, ?, ?)",
                    (user.id, user.username, user.first_name, user.last_name)
                )
                
                cursor.execute(
                    "INSERT INTO logs (entity_id, entity_type, action, user_id, admin_id, reason) VALUES (?, ?, ?, ?, ?, ?)",
                    (chat_id, "group", "join", user.id, None, "New member joined")
                )
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error in welcome_new_members: {e}")
    
    @bot.on_message(filters.group & filters.text)
    async def filter_messages(client: Client, message: Message):
        """
        Filter messages for spam, NSFW content, and phishing links.
        """
        chat_id = message.chat.id
        user_id = message.from_user.id if message.from_user else None
        text = message.text or message.caption or ""
        
        if not user_id:
            return
        
        try:
            # Check if user is admin
            chat_member = await client.get_chat_member(chat_id, user_id)
            if chat_member.status in ["administrator", "creator"]:
                return  # Skip filtering for admins
            
            # Check for spam patterns
            for pattern in SPAM_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    await handle_violation(client, message, "spam")
                    return
            
            # Check for NSFW patterns
            for pattern in NSFW_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    await handle_violation(client, message, "nsfw")
                    return
            
            # Check for phishing patterns
            for pattern in PHISHING_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    await handle_violation(client, message, "phishing")
                    return
            
            # Check for flooding (multiple messages in short time)
            # This would require tracking message frequency per user
            # Simplified implementation for now
            
        except Exception as e:
            logger.error(f"Error in filter_messages: {e}")
    
    @bot.on_message(filters.command(["setwelcome"]) & filters.group)
    async def set_welcome_message(client: Client, message: Message):
        """
        Set custom welcome message for the group.
        """
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        try:
            # Check if user is admin
            chat_member = await client.get_chat_member(chat_id, user_id)
            if chat_member.status not in ["administrator", "creator"]:
                await message.reply_text("Only administrators can set welcome messages.")
                return
            
            # Get welcome message text
            if len(message.command) < 2:
                await message.reply_text("Please provide a welcome message.\nUsage: /setwelcome Your welcome message here")
                return
            
            welcome_text = message.text.split("/setwelcome ", 1)[1]
            
            # Save to database
            conn = await get_db()
            cursor = conn.cursor()
            
            # Check if group exists in database
            cursor.execute("SELECT id FROM groups WHERE group_id = ?", (chat_id,))
            if cursor.fetchone():
                cursor.execute("UPDATE groups SET welcome_message = ? WHERE group_id = ?", (welcome_text, chat_id))
            else:
                cursor.execute(
                    "INSERT INTO groups (group_id, title, username, welcome_message) VALUES (?, ?, ?, ?)",
                    (chat_id, message.chat.title, message.chat.username, welcome_text)
                )
            
            conn.commit()
            
            await message.reply_text("Welcome message has been set successfully!")
            
        except Exception as e:
            logger.error(f"Error in set_welcome_message: {e}")
            await message.reply_text(f"Error setting welcome message: {str(e)}")
    
    @bot.on_message(filters.command(["setrules"]) & filters.group)
    async def set_rules(client: Client, message: Message):
        """
        Set rules for the group.
        """
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        try:
            # Check if user is admin
            chat_member = await client.get_chat_member(chat_id, user_id)
            if chat_member.status not in ["administrator", "creator"]:
                await message.reply_text("Only administrators can set rules.")
                return
            
            # Get rules text
            if len(message.command) < 2:
                await message.reply_text("Please provide rules.\nUsage: /setrules Group rules here")
                return
            
            rules_text = message.text.split("/setrules ", 1)[1]
            
            # Save to database
            conn = await get_db()
            cursor = conn.cursor()
            
            # Check if group exists in database
            cursor.execute("SELECT id FROM groups WHERE group_id = ?", (chat_id,))
            if cursor.fetchone():
                cursor.execute("UPDATE groups SET rules = ? WHERE group_id = ?", (rules_text, chat_id))
            else:
                cursor.execute(
                    "INSERT INTO groups (group_id, title, username, rules) VALUES (?, ?, ?, ?)",
                    (chat_id, message.chat.title, message.chat.username, rules_text)
                )
            
            conn.commit()
            
            await message.reply_text("Rules have been set successfully!")
            
        except Exception as e:
            logger.error(f"Error in set_rules: {e}")
            await message.reply_text(f"Error setting rules: {str(e)}")
    
    @bot.on_message(filters.command(["rules"]) & filters.group)
    async def show_rules(client: Client, message: Message):
        """
        Show the group rules.
        """
        chat_id = message.chat.id
        
        try:
            # Get rules from database
            conn = await get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT rules FROM groups WHERE group_id = ?", (chat_id,))
            result = cursor.fetchone()
            
            if result and result[0]:
                await message.reply_text(f"**Group Rules:**\n\n{result[0]}")
            else:
                await message.reply_text("No rules have been set for this group yet.")
            
        except Exception as e:
            logger.error(f"Error in show_rules: {e}")
            await message.reply_text(f"Error showing rules: {str(e)}")


async def handle_violation(client: Client, message: Message, violation_type: str):
    """
    Handle message violations (spam, NSFW, phishing).
    """
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    try:
        # Delete the message
        await message.delete()
        
        # Get action based on violation type
        action = "none"  # Default action
        
        # In a real implementation, we would get the action from the database
        # based on group settings. For now, we'll use defaults.
        if violation_type == "spam":
            action = "kick"
            reason = "Sending spam messages"
        elif violation_type == "nsfw":
            action = "ban"
            reason = "Sending NSFW content"
        elif violation_type == "phishing":
            action = "ban"
            reason = "Sending phishing links"
        
        # Take action based on violation
        if action == "kick":
            await client.kick_chat_member(chat_id, user_id, until_date=int(time.time() + 60))  # Kick for 1 minute (soft ban)
            await client.send_message(chat_id, f"User kicked for {violation_type} content.")
        elif action == "ban":
            await client.kick_chat_member(chat_id, user_id)  # Permanent ban
            await client.send_message(chat_id, f"User banned for {violation_type} content.")
        elif action == "mute":
            await client.restrict_chat_member(
                chat_id, user_id,
                ChatPermissions(can_send_messages=False),
                until_date=int(time.time() + 3600)  # Mute for 1 hour
            )
            await client.send_message(chat_id, f"User muted for {violation_type} content.")
        
        # Log the action
        conn = await get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO logs (entity_id, entity_type, action, user_id, admin_id, reason) VALUES (?, ?, ?, ?, ?, ?)",
            (chat_id, "group", action, user_id, None, reason)
        )
        conn.commit()
        
    except FloodWait as e:
        logger.warning(f"FloodWait: Sleeping for {e.x} seconds")
        await asyncio.sleep(e.x)
    except UserAdminInvalid:
        logger.warning(f"Cannot restrict admin in chat {chat_id}")
    except Exception as e:
        logger.error(f"Error in handle_violation: {e}")