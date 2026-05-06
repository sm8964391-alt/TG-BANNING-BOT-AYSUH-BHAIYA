#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Telegram Super-Manager App - Configuration Checker
Utility to validate and fix configuration issues.
"""

import os
import sys
import configparser
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_config():
    """
    Check if config.ini exists and has valid values.
    Creates a default config if not found.
    """
    config_path = Path(__file__).parent / "config.ini"
    
    if not config_path.exists():
        print("[WARNING] config.ini not found. Creating default configuration...")
        create_default_config(config_path)
        return False
    
    config = configparser.ConfigParser()
    config.read(config_path)
    
    # Check required sections
    required_sections = ["telegram", "database", "app"]
    missing_sections = [s for s in required_sections if s not in config.sections()]
    
    if missing_sections:
        print(f"[WARNING] Missing sections in config.ini: {', '.join(missing_sections)}")
        for section in missing_sections:
            config.add_section(section)
    
    # Check telegram section
    if "telegram" in config.sections():
        telegram_keys = ["api_id", "api_hash", "bot_token"]
        missing_keys = [k for k in telegram_keys if k not in config["telegram"] or config["telegram"][k] in ["YOUR_API_ID", "YOUR_API_HASH", "YOUR_BOT_TOKEN", ""]]
        
        if missing_keys:
            print(f"[WARNING] Missing or default values in [telegram] section: {', '.join(missing_keys)}")
            print("Please update these values with your Telegram API credentials from https://my.telegram.org/apps")
            return False
    
    # Check database section
    if "database" in config.sections():
        if "type" not in config["database"] or config["database"]["type"] not in ["sqlite", "postgresql"]:
            print("[WARNING] Invalid database type. Setting to default (sqlite)")
            config["database"]["type"] = "sqlite"
        
        if config["database"]["type"] == "sqlite" and ("path" not in config["database"] or not config["database"]["path"]):
            print("[WARNING] Missing database path for SQLite. Setting to default")
            config["database"]["path"] = "../database/tg_manager.db"
        
        if config["database"]["type"] == "postgresql":
            pg_keys = ["host", "port", "user", "password", "database"]
            missing_pg_keys = [k for k in pg_keys if k not in config["database"] or not config["database"][k]]
            
            if missing_pg_keys:
                print(f"[WARNING] Missing PostgreSQL configuration: {', '.join(missing_pg_keys)}")
                print("Please update these values or switch to SQLite")
    
    # Check app section
    if "app" in config.sections():
        if "theme" not in config["app"] or config["app"]["theme"] not in ["dark", "light"]:
            print("[WARNING] Invalid theme setting. Setting to default (dark)")
            config["app"]["theme"] = "dark"
        
        if "log_level" not in config["app"] or config["app"]["log_level"] not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            print("[WARNING] Invalid log_level. Setting to default (INFO)")
            config["app"]["log_level"] = "INFO"
    
    # Save any changes made
    with open(config_path, "w") as f:
        config.write(f)
    
    return True

def create_default_config(config_path):
    """
    Create a default config.ini file
    """
    config = configparser.ConfigParser()
    
    config.add_section("telegram")
    config["telegram"]["api_id"] = "YOUR_API_ID"
    config["telegram"]["api_hash"] = "YOUR_API_HASH"
    config["telegram"]["bot_token"] = "YOUR_BOT_TOKEN"
    
    config.add_section("database")
    config["database"]["type"] = "sqlite"
    config["database"]["path"] = "../database/tg_manager.db"
    config["database"]["# For PostgreSQL, uncomment and fill these"] = ""
    config["database"]["# host"] = "localhost"
    config["database"]["# port"] = "5432"
    config["database"]["# user"] = "username"
    config["database"]["# password"] = "password"
    config["database"]["# database"] = "tg_manager"
    
    config.add_section("app")
    config["app"]["debug"] = "true"
    config["app"]["log_level"] = "INFO"
    config["app"]["theme"] = "dark"
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    with open(config_path, "w") as f:
        config.write(f)
    
    print(f"Default configuration created at {config_path}")
    print("Please update the Telegram API credentials before running the application")

if __name__ == "__main__":
    check_config()