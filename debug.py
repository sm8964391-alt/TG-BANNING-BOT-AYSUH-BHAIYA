#!/usr/bin/env python3
"""
Debug script for Telegram Super-Manager

This script checks for common errors and fixes them automatically.
"""

import os
import sys
import re
import subprocess
from pathlib import Path

# ANSI colors for better output
COLORS = {
    "reset": "\033[0m",
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "magenta": "\033[95m",
    "cyan": "\033[96m",
}

def colored(text, color):
    """Return colored text if terminal supports it"""
    if sys.platform == "win32" and "ANSICON" not in os.environ:
        return text
    return f"{COLORS.get(color.lower(), '')}{text}{COLORS['reset']}"

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 50)
    print(colored(text, "cyan"))
    print("=" * 50)

def print_success(text):
    """Print a success message"""
    print(colored(f"✅ {text}", "green"))

def print_error(text):
    """Print an error message"""
    print(colored(f"❌ {text}", "red"))

def print_warning(text):
    """Print a warning message"""
    print(colored(f"⚠️ {text}", "yellow"))

def print_info(text):
    """Print an info message"""
    print(colored(f"ℹ️ {text}", "blue"))

def check_python_version():
    """Check if Python version is compatible"""
    print_header("Checking Python Version")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print_error(f"Python {version.major}.{version.minor}.{version.micro} detected")
        print_error("Python 3.7 or higher is required")
        return False
    
    print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def check_dependencies():
    """Check if all required dependencies are installed"""
    print_header("Checking Dependencies")
    
    dependencies = [
        "pyrogram",
        "tgcrypto",
        "kivy",
        "kivymd",
        "sqlite3",
        "requests",
        "python-dotenv",
        "loguru"
    ]
    
    missing = []
    for dep in dependencies:
        try:
            if dep == "python-dotenv":
                __import__("dotenv")
            else:
                __import__(dep.split("==")[0])
            print_success(f"{dep} is installed")
        except ImportError:
            print_error(f"{dep} is not installed")
            missing.append(dep)
    
    if missing:
        print_warning("\nInstalling missing dependencies...")
        for dep in missing:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                print_success(f"Installed {dep}")
            except subprocess.CalledProcessError:
                print_error(f"Failed to install {dep}")
                return False
    
    return True

def fix_asyncio_in_file(file_path):
    """Fix asyncio event loop error in a file"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check if asyncio fix is already present
    if "asyncio.set_event_loop(asyncio.new_event_loop())" in content:
        print_info(f"Asyncio fix already present in {file_path}")
        return True
    
    # Find import section
    import_pattern = r"import\s+asyncio"
    if not re.search(import_pattern, content):
        print_error(f"Could not find asyncio import in {file_path}")
        return False
    
    # Add the fix after asyncio import
    fixed_content = re.sub(
        import_pattern,
        "import asyncio\n\n# Fix asyncio event loop error\ntry:\n    asyncio.get_event_loop()\nexcept RuntimeError:\n    asyncio.set_event_loop(asyncio.new_event_loop())",
        content
    )
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(fixed_content)
    
    print_success(f"Added asyncio fix to {file_path}")
    return True

def check_asyncio_errors():
    """Check and fix asyncio event loop errors"""
    print_header("Checking Asyncio Event Loop Errors")
    
    # Files that might need the asyncio fix
    backend_files = [
        os.path.join("backend", "handlers", "group_management.py"),
        os.path.join("backend", "handlers", "mass_messaging.py"),
        os.path.join("backend", "handlers", "reporting.py"),
        os.path.join("backend", "main.py")
    ]
    
    for file_path in backend_files:
        if os.path.exists(file_path):
            fix_asyncio_in_file(file_path)
        else:
            print_warning(f"File not found: {file_path}")
    
    return True

def check_kivy_config():
    """Check Kivy configuration"""
    print_header("Checking Kivy Configuration")
    
    # Create .kivy directory if it doesn't exist
    kivy_dir = os.path.join(os.path.expanduser("~"), ".kivy")
    os.makedirs(kivy_dir, exist_ok=True)
    
    # Create config.ini if it doesn't exist
    kivy_config = os.path.join(kivy_dir, "config.ini")
    if not os.path.exists(kivy_config):
        with open(kivy_config, "w") as f:
            f.write("[kivy]\nlog_level = info\n")
        print_success(f"Created Kivy config at {kivy_config}")
    else:
        print_info(f"Kivy config already exists at {kivy_config}")
    
    return True

def check_project_structure():
    """Check if project structure is correct"""
    print_header("Checking Project Structure")
    
    required_dirs = [
        "backend",
        "frontend",
        "config",
        "database"
    ]
    
    for directory in required_dirs:
        if os.path.isdir(directory):
            print_success(f"{directory}/ directory exists")
        else:
            print_warning(f"{directory}/ directory missing, creating it")
            os.makedirs(directory, exist_ok=True)
    
    # Check if config.ini exists
    config_path = os.path.join("config", "config.ini")
    if not os.path.exists(config_path):
        print_warning(f"{config_path} missing, creating a template")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w") as f:
            f.write("""[telegram]
# Get these from https://my.telegram.org/apps
api_id = 
api_hash = 
bot_token = 

[database]
type = sqlite
sqlite_db = database/telegram_manager.db
# If using PostgreSQL, uncomment and fill:
# postgres_uri = postgresql://username:password@localhost/dbname

[app]
theme = dark
notifications = true
debug_mode = false
log_level = INFO
""")
        print_success(f"Created template {config_path}")
    else:
        print_success(f"{config_path} exists")
    
    return True

def check_frontend_imports():
    """Check frontend imports and fix them if needed"""
    print_header("Checking Frontend Imports")
    
    frontend_main = os.path.join("frontend", "main.py")
    if not os.path.exists(frontend_main):
        print_warning(f"File not found: {frontend_main}")
        return False
    
    with open(frontend_main, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check for common import errors
    missing_imports = []
    
    if "from kivy.app import App" not in content:
        missing_imports.append("from kivy.app import App")
    
    if "from kivy.uix.screenmanager import ScreenManager, Screen" not in content:
        missing_imports.append("from kivy.uix.screenmanager import ScreenManager, Screen")
    
    if missing_imports:
        print_warning(f"Missing imports in {frontend_main}:")
        for imp in missing_imports:
            print_warning(f"  - {imp}")
        
        # Add missing imports at the top of the file
        import_section_end = content.find("\n\n", content.find("import"))
        if import_section_end == -1:
            import_section_end = content.find("\n", content.find("import"))
        
        new_content = content[:import_section_end] + "\n" + "\n".join(missing_imports) + content[import_section_end:]
        
        with open(frontend_main, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        print_success(f"Added missing imports to {frontend_main}")
    else:
        print_success(f"No missing imports in {frontend_main}")
    
    return True

def run_tests():
    """Run tests to verify everything is working"""
    print_header("Running Tests")
    
    test_script = "test_setup.py"
    if os.path.exists(test_script):
        print_info(f"Running {test_script}...")
        try:
            subprocess.check_call([sys.executable, test_script])
            print_success("Tests completed successfully")
        except subprocess.CalledProcessError:
            print_error("Tests failed")
            return False
    else:
        print_warning(f"Test script not found: {test_script}")
    
    return True

def main():
    """Main function"""
    print_header("Telegram Super-Manager Debug Tool")
    print("This tool will check for common errors and fix them automatically.")
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Asyncio Errors", check_asyncio_errors),
        ("Kivy Configuration", check_kivy_config),
        ("Project Structure", check_project_structure),
        ("Frontend Imports", check_frontend_imports),
        ("Tests", run_tests)
    ]
    
    results = {}
    for name, check_func in checks:
        print(f"\nRunning check: {name}")
        try:
            result = check_func()
            results[name] = result
        except Exception as e:
            print_error(f"Error during {name} check: {e}")
            results[name] = False
    
    # Print summary
    print_header("Debug Summary")
    all_passed = True
    for name, result in results.items():
        if result:
            print_success(f"{name}: Passed")
        else:
            print_error(f"{name}: Failed")
            all_passed = False
    
    if all_passed:
        print_header("All checks passed! Your setup is ready.")
        print("You can now run the application:")
        print(colored("  python frontend/main.py", "green"))
    else:
        print_header("Some checks failed. Please fix the issues above.")
        print("Run this debug tool again after fixing the issues:")
        print(colored("  python debug.py", "yellow"))

if __name__ == "__main__":
    main()