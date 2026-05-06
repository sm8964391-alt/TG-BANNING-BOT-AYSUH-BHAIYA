#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Reporting and security handlers for Telegram Super-Manager App.
Implements features for automated reporting of spam, fake accounts, NSFW content,
and violence using multiple accounts via session strings.
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
from pyrogram.errors import FloodWait, UserIsBlocked, PeerIdInvalid
from loguru import logger

# Import database functions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.database import get_db

# Constants
REPORT_TYPES = {
    "spam": "Spam",
    "fake": "Fake account",
    "porn": "Pornography",
    "violence": "Violence",
    "child_abuse": "Child abuse",
    "copyright": "Copyright infringement",
    "other": "Other"
}

# Store active reporting sessions
active_sessions = {}


def setup_reporting_handlers(bot: Client):
    """
    Set up all reporting and security handlers for the bot.
    """
    
    @bot.on_message(filters.command(["addsession"]) & filters.private)
    async def add_session_command(client: Client, message: Message):
        """
        Add a new session string for multi-account reporting.
        Usage: /addsession <session_name> <session_string>
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
            args = message.text.split(" ", 2)
            if len(args) < 3:
                await message.reply_text(
                    "Invalid command format.\n"
                    "Usage: /addsession <session_name> <session_string>\n"
                    "Example: /addsession account1 1BQANOTEuMTA4LjU2LjE5MQG7vOUveTtsEz..."
                )
                return
            
            session_name = args[1]
            session_string = args[2]
            
            # Check if session name already exists
            cursor.execute("SELECT id FROM sessions WHERE session_name = ?", (session_name,))
            if cursor.fetchone():
                await message.reply_text(f"Session name '{session_name}' already exists. Please use a different name.")
                return
            
            # Save session to database
            cursor.execute(
                "INSERT INTO sessions (session_name, session_string) VALUES (?, ?)",
                (session_name, session_string)
            )
            conn.commit()
            
            await message.reply_text(f"Session '{session_name}' has been added successfully!")
            
        except Exception as e:
            logger.error(f"Error in add_session_command: {e}")
            await message.reply_text(f"Error adding session: {str(e)}")
    
    @bot.on_message(filters.command(["listsessions"]) & filters.private)
    async def list_sessions_command(client: Client, message: Message):
        """
        List all available sessions for reporting.
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
            
            # Get all sessions
            cursor.execute("SELECT id, session_name, is_active FROM sessions")
            sessions = cursor.fetchall()
            
            if not sessions:
                await message.reply_text("No sessions found. Add a session with /addsession command.")
                return
            
            # Format sessions list
            sessions_text = "**Available Sessions:**\n\n"
            for session_id, session_name, is_active in sessions:
                status = "Active" if is_active else "Inactive"
                sessions_text += f"ID: {session_id} | Name: {session_name} | Status: {status}\n"
            
            await message.reply_text(sessions_text)
            
        except Exception as e:
            logger.error(f"Error in list_sessions_command: {e}")
            await message.reply_text(f"Error listing sessions: {str(e)}")
    
    @bot.on_message(filters.command(["removesession"]) & filters.private)
    async def remove_session_command(client: Client, message: Message):
        """
        Remove a session.
        Usage: /removesession <session_id>
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
            if len(args) < 2:
                await message.reply_text(
                    "Invalid command format.\n"
                    "Usage: /removesession <session_id>\n"
                    "Example: /removesession 1"
                )
                return
            
            try:
                session_id = int(args[1])
            except ValueError:
                await message.reply_text("Session ID must be a number.")
                return
            
            # Check if session exists
            cursor.execute("SELECT session_name FROM sessions WHERE id = ?", (session_id,))
            session = cursor.fetchone()
            
            if not session:
                await message.reply_text(f"Session with ID {session_id} not found.")
                return
            
            # Remove session from database
            cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            conn.commit()
            
            await message.reply_text(f"Session '{session[0]}' has been removed successfully!")
            
        except Exception as e:
            logger.error(f"Error in remove_session_command: {e}")
            await message.reply_text(f"Error removing session: {str(e)}")
    
    @bot.on_message(filters.command(["report"]) & filters.private)
    async def report_command(client: Client, message: Message):
        """
        Report a user, group, or message.
        Usage: /report <type> <target_id> <report_type> [session_ids]
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
            if len(args) < 4:
                await message.reply_text(
                    "Invalid command format.\n"
                    "Usage: /report <type> <target_id> <report_type> [session_ids]\n"
                    "Types: user, group, message\n"
                    "Report types: spam, fake, porn, violence, child_abuse, copyright, other\n"
                    "Example: /report user 123456789 spam 1,2,3"
                )
                return
            
            target_type = args[1].lower()
            if target_type not in ["user", "group", "message"]:
                await message.reply_text("Invalid target type. Use 'user', 'group', or 'message'.")
                return
            
            try:
                target_id = int(args[2])
            except ValueError:
                await message.reply_text("Target ID must be a number.")
                return
            
            report_type = args[3].lower()
            if report_type not in REPORT_TYPES:
                report_types_str = ", ".join(REPORT_TYPES.keys())
                await message.reply_text(f"Invalid report type. Use one of: {report_types_str}")
                return
            
            # Get session IDs (optional)
            session_ids = []
            if len(args) > 4:
                try:
                    session_ids = [int(s.strip()) for s in args[4].split(",")]
                except ValueError:
                    await message.reply_text("Session IDs must be numbers separated by commas.")
                    return
            
            # If no session IDs provided, use all active sessions
            if not session_ids:
                cursor.execute("SELECT id FROM sessions WHERE is_active = 1")
                session_ids = [row[0] for row in cursor.fetchall()]
            
            if not session_ids:
                await message.reply_text("No active sessions found. Add a session with /addsession command.")
                return
            
            # Start the reporting process
            status_message = await message.reply_text("Starting reporting process...")
            
            # Get session strings for the specified session IDs
            cursor.execute(
                "SELECT id, session_string FROM sessions WHERE id IN ({})".
                format(",".join(["?" for _ in session_ids])),
                session_ids
            )
            sessions = cursor.fetchall()
            
            if not sessions:
                await status_message.edit_text("No valid sessions found for the specified IDs.")
                return
            
            await status_message.edit_text(f"Reporting {target_type} {target_id} for {REPORT_TYPES[report_type]} using {len(sessions)} accounts...")
            
            # Report using each session
            success_count = 0
            fail_count = 0
            
            for session_id, session_string in sessions:
                try:
                    # Create a temporary client with the session string
                    async with Client(f"reporter_{session_id}", session_string=session_string, no_updates=True) as app:
                        # Report based on target type
                        if target_type == "user":
                            await app.report_user(target_id, REPORT_TYPES[report_type])
                        elif target_type == "group":
                            await app.report_chat(target_id, REPORT_TYPES[report_type])
                        elif target_type == "message":
                            # For message reporting, we need chat_id and message_id
                            # This is a simplified implementation
                            # In a real app, you would need to parse the message ID properly
                            await app.report_message(target_id, REPORT_TYPES[report_type])
                        
                        success_count += 1
                        
                        # Log the report
                        cursor.execute(
                            "INSERT INTO reports (target_id, target_type, report_type, reporter_id, status) VALUES (?, ?, ?, ?, ?)",
                            (target_id, target_type, report_type, session_id, "sent")
                        )
                        
                except Exception as e:
                    logger.error(f"Error reporting with session {session_id}: {e}")
                    fail_count += 1
                    
                    # Log the failed report
                    cursor.execute(
                        "INSERT INTO reports (target_id, target_type, report_type, reporter_id, status) VALUES (?, ?, ?, ?, ?)",
                        (target_id, target_type, report_type, session_id, "failed")
                    )
                
                # Small delay between reports
                await asyncio.sleep(2)
            
            conn.commit()
            
            # Final status update
            await status_message.edit_text(
                f"Reporting completed.\n"
                f"Target: {target_type} {target_id}\n"
                f"Report type: {REPORT_TYPES[report_type]}\n"
                f"Total sessions: {len(sessions)}\n"
                f"Successfully reported: {success_count}\n"
                f"Failed: {fail_count}"
            )
            
        except Exception as e:
            logger.error(f"Error in report_command: {e}")
            await message.reply_text(f"Error reporting: {str(e)}")
    
    @bot.on_message(filters.command(["reportlogs"]) & filters.private)
    async def report_logs_command(client: Client, message: Message):
        """
        Show logs of reports sent.
        Usage: /reportlogs [limit]
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
            limit = 10  # Default limit
            
            if len(args) > 1:
                try:
                    limit = int(args[1])
                    if limit <= 0:
                        limit = 10
                except ValueError:
                    pass
            
            # Get report logs
            cursor.execute(
                """
                SELECT r.id, r.target_id, r.target_type, r.report_type, s.session_name, r.status, r.created_at
                FROM reports r
                JOIN sessions s ON r.reporter_id = s.id
                ORDER BY r.created_at DESC
                LIMIT ?
                """,
                (limit,)
            )
            logs = cursor.fetchall()
            
            if not logs:
                await message.reply_text("No report logs found.")
                return
            
            # Format logs
            logs_text = f"**Recent Report Logs (Last {len(logs)}):**\n\n"
            for log_id, target_id, target_type, report_type, session_name, status, created_at in logs:
                report_type_name = REPORT_TYPES.get(report_type, report_type)
                logs_text += f"ID: {log_id} | Target: {target_type} {target_id} | Type: {report_type_name} | Reporter: {session_name} | Status: {status} | Date: {created_at}\n\n"
            
            await message.reply_text(logs_text)
            
        except Exception as e:
            logger.error(f"Error in report_logs_command: {e}")
            await message.reply_text(f"Error getting report logs: {str(e)}")