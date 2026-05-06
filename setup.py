#!/usr/bin/env python3
"""
Setup script for Telegram Super-Manager

This script helps install dependencies and fix common issues.
"""

import os
import sys
import subprocess
import asyncio

def install_dependencies():
    """Install required dependencies from requirements.txt"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        print("\nTrying to install critical dependencies individually...")
        
        critical_deps = ["pyrogram", "tgcrypto", "kivy", "kivymd"]
        for dep in critical_deps:
            try:
                print(f"Installing {dep}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                print(f"✅ {dep} installed successfully!")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {dep}")

def create_asyncio_patch():
    """Create a patch for the asyncio event loop error"""
    print("\nCreating asyncio patch for backend handlers...")
    
    handlers_dir = os.path.join("backend", "handlers")
    patch_content = """
# Add this at the top of your file to fix asyncio event loop error
import asyncio
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())
"""
    
    # List of handler files to patch
    handler_files = [
        os.path.join(handlers_dir, "group_management.py"),
        os.path.join(handlers_dir, "mass_messaging.py"),
        os.path.join(handlers_dir, "reporting.py")
    ]
    
    for file_path in handler_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    content = f.read()
                
                if "asyncio.set_event_loop(asyncio.new_event_loop())" not in content:
                    with open(file_path, "r") as f:
                        lines = f.readlines()
                    
                    # Find where to insert the patch (after imports)
                    insert_index = 0
                    for i, line in enumerate(lines):
                        if line.startswith("import ") or line.startswith("from "):
                            insert_index = i + 1
                    
                    # Insert the patch
                    lines.insert(insert_index, patch_content)
                    
                    with open(file_path, "w") as f:
                        f.writelines(lines)
                    
                    print(f"✅ Added asyncio patch to {file_path}")
                else:
                    print(f"ℹ️ {file_path} already has asyncio patch")
            except Exception as e:
                print(f"❌ Error patching {file_path}: {e}")
        else:
            print(f"⚠️ File not found: {file_path}")

def create_test_script():
    """Create a test script to verify installation"""
    print("\nCreating test script...")
    
    test_script_path = "test_setup.py"
    test_script_content = """
#!/usr/bin/env python3
"""
"""Test script to verify installation"""
"""

import sys

print("Python version:", sys.version)

try:
    import pyrogram
    print("✅ Pyrogram installed:", pyrogram.__version__)
except ImportError:
    print("❌ Pyrogram not installed")

try:
    import tgcrypto
    print("✅ TgCrypto installed:", tgcrypto.__version__)
except ImportError:
    print("❌ TgCrypto not installed")

try:
    import kivy
    print("✅ Kivy installed:", kivy.__version__)
except ImportError:
    print("❌ Kivy not installed")

try:
    import kivymd
    print("✅ KivyMD installed:", kivymd.__version__)
except ImportError:
    print("❌ KivyMD not installed")

try:
    import asyncio
    loop = asyncio.get_event_loop()
    print("✅ Asyncio event loop works correctly")
except Exception as e:
    print(f"❌ Asyncio event loop error: {e}")

print("\nSetup test complete!")
"""

# Test script already exists, no need to create it
test_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_setup.py")

def main():
    """Main function"""
    print("=== Telegram Super-Manager Setup ===")
    print("This script will help you set up the project.\n")
    
    install_dependencies()
    create_asyncio_patch()
    create_test_script()
    
    print("\n=== Setup Complete ===")
    print("To test your installation, run: python test_setup.py")
    print("To start the application, run: python frontend/main.py")

if __name__ == "__main__":
    main()