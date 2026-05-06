# Telegram Super-Manager App

A comprehensive Telegram management application with bot backend and mobile UI for controlling and automating Telegram group/channel management.

## Features

### Group/Channel Management
- Auto-kick spammers
- Auto-delete NSFW links, phishing, or flood messages
- Custom welcome & rules messages
- Logs system for all actions

### Mass Messaging Tools
- Mass DM subscribers of a channel
- Mass forward messages to multiple groups
- Option to filter subscribers before sending (e.g., active users only)
- Speed control & flood-wait handling

### Reporting & Security
- Automated reporting system (spam, fake, porn, violence, etc.)
- Multi-account reporting (via session strings)
- Dashboard to view logs of reports sent

### Mobile App Interface
- Built with Kivy (Python) for APK conversion or React Native for cross-platform
- Clean UI with login, dashboard, quick actions, and logs viewer
- Dark/light mode toggle

## Project Structure

```
├── backend/               # Python backend using Pyrogram/Telethon
│   ├── bot/               # Telegram bot implementation
│   ├── db/                # Database models and connections
│   ├── handlers/          # Message and command handlers
│   └── utils/             # Utility functions
├── frontend/              # Mobile UI (Kivy or React Native)
│   ├── assets/            # Images, icons, and other static assets
│   ├── components/        # Reusable UI components
│   ├── screens/           # App screens/pages
│   └── styles/            # UI styling
├── database/              # Database migrations and schema
└── config/                # Configuration files
```

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- Telegram API credentials (API ID, API Hash, Bot Token)
- For Android APK building: Buildozer

### Installation

#### Automatic Setup (Recommended)

Run the setup script to install dependencies and fix common issues:

```
python setup.py
```

This script will:
- Install all required dependencies
- Fix the asyncio event loop error in backend handlers
- Create a test script to verify your installation

#### Manual Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure your Telegram API credentials:
   - Create a `config.ini` file in the `config` directory (or use the app to create it)
   - Add your Telegram API credentials (API ID, API Hash, Bot Token)

#### Troubleshooting Common Issues

1. **Missing Dependencies**
   - If you encounter `ModuleNotFoundError`, install the specific module:
     ```
     pip install pyrogram tgcrypto kivy kivymd
     ```

2. **Asyncio Event Loop Error**
   - If you see `RuntimeError: There is no current event loop in thread 'MainThread'`, add this code at the top of your script:
     ```python
     import asyncio
     try:
         asyncio.get_event_loop()
     except RuntimeError:
         asyncio.set_event_loop(asyncio.new_event_loop())
     ```

3. **Kivy Installation Issues**
   - On Windows, you might need to install additional dependencies:
     ```
     pip install docutils pygments pypiwin32 kivy.deps.sdl2 kivy.deps.glew
     ```

### Running the Application

#### Running the Backend (Telegram Bot)

```
python backend/main.py
```

#### Running the Frontend (Kivy UI)

```
python frontend/main.py
```

### Building for Android

1. Install Buildozer: `pip install buildozer`
2. Initialize Buildozer in the project directory: `buildozer init`
3. Edit the `buildozer.spec` file to configure your app settings
4. Build the APK: `buildozer android debug`

## Configuration

The application uses a `config.ini` file for configuration. You can edit this file directly or use the Settings screen in the app.

### Sample Configuration

```ini
[telegram]
api_id = YOUR_API_ID
api_hash = YOUR_API_HASH
bot_token = YOUR_BOT_TOKEN

[database]
type = sqlite
sqlite_db = database/telegram_manager.db

[app]
theme = dark
debug = false
log_level = INFO
```

## Usage

1. Start the application and log in with your Telegram API credentials
2. Navigate to the dashboard to see your groups and channels
3. Use the quick action buttons to access different features:
   - Group Management: Configure auto-moderation, welcome messages, etc.
   - Mass Messaging: Send mass DMs or forward messages
   - Reporting & Security: Report users, groups, or messages
   - View Logs: Check logs of actions taken

## License

MIT