#!/usr/bin/env python3
"""
Test script to verify installation
"""

import sys
import os

print("====================================")
print("Telegram Super-Manager Setup Test")
print("====================================")
print("\nPython version:", sys.version)

# Fix asyncio event loop issue first
import asyncio
try:
    asyncio.get_event_loop()
except RuntimeError:
    # Fix the event loop error
    asyncio.set_event_loop(asyncio.new_event_loop())

# Test critical dependencies
dependencies = [
    ("pyrogram", "Pyrogram"),
    ("tgcrypto", "TgCrypto"),
    ("kivy", "Kivy"),
    ("kivymd", "KivyMD"),
    ("sqlite3", "SQLite3"),
    ("requests", "Requests"),
    ("dotenv", "Python-dotenv"),
    ("loguru", "Loguru")
]

all_passed = True

print("\nChecking dependencies...")
for module_name, display_name in dependencies:
    try:
        if module_name == "dotenv":
            module = __import__("dotenv")
        elif module_name == "pyrogram":
            # Special handling for pyrogram to avoid asyncio issues
            try:
                import pyrogram
                module = pyrogram
            except Exception as e:
                print(f"❌ {display_name} import error: {e}")
                all_passed = False
                continue
        else:
            module = __import__(module_name)
        
        version = getattr(module, "__version__", "Unknown")
        print(f"✅ {display_name} installed: {version}")
    except ImportError:
        print(f"❌ {display_name} not installed")
        all_passed = False

# Test asyncio event loop
print("\nChecking asyncio event loop...")
try:
    # We already set up the event loop at the beginning
    loop = asyncio.get_event_loop()
    print("✅ Asyncio event loop works correctly")
except Exception as e:
    print(f"❌ Asyncio event loop error: {e}")
    print("\nTrying to fix asyncio event loop...")
    try:
        import asyncio
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        print("✅ Asyncio event loop fixed successfully")
    except Exception as e:
        print(f"❌ Could not fix asyncio event loop: {e}")
        all_passed = False

# Check project structure
print("\nChecking project structure...")
required_dirs = [
    "backend",
    "frontend",
    "config",
    "database"
]

for directory in required_dirs:
    if os.path.isdir(directory):
        print(f"✅ {directory}/ directory exists")
    else:
        print(f"❌ {directory}/ directory missing")
        all_passed = False

# Check config file
config_path = os.path.join("config", "config.ini")
if os.path.isfile(config_path):
    print(f"✅ {config_path} exists")
else:
    print(f"⚠️ {config_path} missing - will be created when you run the app")

# Final result
print("\n====================================")
if all_passed:
    print("✅ All tests passed! Your setup is complete.")
    print("\nYou can now run the application:")
    print("  python frontend/main.py")
else:
    print("⚠️ Some tests failed. Please fix the issues above.")
    print("\nRun the setup script again to fix issues:")
    print("  python setup.py")
print("====================================")