#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Database initialization and connection management.
"""

import os
import sqlite3
import asyncio
from loguru import logger

# Database connection
db_connection = None


async def init_db(config):
    """
    Initialize the database connection based on configuration.
    """
    global db_connection
    
    db_type = config.get("database", "type", fallback="sqlite")
    
    if db_type.lower() == "sqlite":
        db_path = config.get("database", "path", fallback="../database/tg_manager.db")
        # Convert relative path to absolute
        if not os.path.isabs(db_path):
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, db_path)
            
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Connect to SQLite database
        try:
            db_connection = sqlite3.connect(db_path)
            logger.info(f"Connected to SQLite database at {db_path}")
            await create_tables_sqlite(db_connection)
            return db_connection
        except sqlite3.Error as e:
            logger.error(f"SQLite error: {e}")
            raise
    
    elif db_type.lower() == "postgresql":
        # For future implementation
        try:
            import psycopg2
            host = config.get("database", "host")
            port = config.getint("database", "port")
            user = config.get("database", "user")
            password = config.get("database", "password")
            database = config.get("database", "database")
            
            # Connect to PostgreSQL
            db_connection = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database
            )
            logger.info(f"Connected to PostgreSQL database at {host}:{port}/{database}")
            await create_tables_postgres(db_connection)
            return db_connection
        except ImportError:
            logger.error("psycopg2 not installed. Please install it for PostgreSQL support.")
            raise
        except Exception as e:
            logger.error(f"PostgreSQL error: {e}")
            raise
    else:
        logger.error(f"Unsupported database type: {db_type}")
        raise ValueError(f"Unsupported database type: {db_type}")


async def create_tables_sqlite(conn):
    """
    Create necessary tables in SQLite database.
    """
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        user_id INTEGER UNIQUE NOT NULL,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        is_admin BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create groups table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY,
        group_id INTEGER UNIQUE NOT NULL,
        title TEXT,
        username TEXT,
        member_count INTEGER DEFAULT 0,
        is_managed BOOLEAN DEFAULT TRUE,
        welcome_message TEXT,
        rules TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create channels table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS channels (
        id INTEGER PRIMARY KEY,
        channel_id INTEGER UNIQUE NOT NULL,
        title TEXT,
        username TEXT,
        subscriber_count INTEGER DEFAULT 0,
        is_managed BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create logs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY,
        entity_id INTEGER NOT NULL,  -- group_id or channel_id
        entity_type TEXT NOT NULL,   -- 'group' or 'channel'
        action TEXT NOT NULL,        -- 'kick', 'ban', 'delete', etc.
        user_id INTEGER,             -- target user if applicable
        admin_id INTEGER,            -- admin who performed action
        reason TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create sessions table for multi-account reporting
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY,
        session_name TEXT UNIQUE NOT NULL,
        session_string TEXT NOT NULL,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create reports table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY,
        target_id INTEGER NOT NULL,   -- user_id, group_id, or message_id
        target_type TEXT NOT NULL,    -- 'user', 'group', 'message'
        report_type TEXT NOT NULL,    -- 'spam', 'fake', 'porn', 'violence', etc.
        reporter_id INTEGER NOT NULL,  -- session_id that reported
        status TEXT DEFAULT 'pending', -- 'pending', 'sent', 'failed'
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Commit changes
    conn.commit()
    logger.info("SQLite tables created successfully")


async def create_tables_postgres(conn):
    """
    Create necessary tables in PostgreSQL database.
    For future implementation.
    """
    # Similar to SQLite but with PostgreSQL syntax
    # This is a placeholder for future implementation
    pass


async def get_db():
    """
    Get database connection. Initialize if not already done.
    """
    global db_connection
    if db_connection is None:
        raise RuntimeError("Database not initialized. Call init_db first.")
    return db_connection