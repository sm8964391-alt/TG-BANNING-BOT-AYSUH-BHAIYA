#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Telegram Super-Manager App - Frontend
Main entry point for the Kivy-based mobile UI.
"""

import os
import sys
import json
import configparser

# Add better error handling for Kivy imports
try:
    from kivy.app import App
    from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.button import Button
    from kivy.uix.label import Label
    from kivy.uix.textinput import TextInput
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.gridlayout import GridLayout
    from kivy.core.window import Window
    from kivy.metrics import dp
    from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, ListProperty
    from kivy.clock import Clock
except ImportError as e:
    print(f"Error importing Kivy modules: {e}")
    print("Please make sure Kivy is installed correctly. Run 'pip install kivy kivymd' or use the setup.py script.")
    sys.exit(1)

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import backend modules
try:
    from backend.db.database import init_db, get_db
except ImportError:
    print("Backend modules not found. Running in standalone mode.")

# Import frontend screens
try:
    from frontend.screens.group_management import GroupManagementScreen
    from frontend.screens.mass_messaging import MassMessagingScreen
    from frontend.screens.reporting import ReportingScreen
    from frontend.screens.settings import SettingsScreen
except ImportError as e:
    print(f"Error importing frontend screens: {e}")
    print("Please make sure the project structure is correct and all dependencies are installed.")
    sys.exit(1)

# Import styles
try:
    from frontend.styles.theme import apply_theme, ButtonStyles, FontSizes
except ImportError as e:
    print(f"Error importing theme styles: {e}")
    print("Please make sure the frontend/styles directory exists and contains theme.py.")
    sys.exit(1)

# Set default window size for desktop testing
Window.size = (400, 700)  # Simulate phone dimensions


class LoginScreen(Screen):
    """
    Login screen for connecting to Telegram API and bot.
    """
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        
        # Main layout
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # App title
        title = Label(
            text="Telegram Super-Manager",
            font_size=dp(24),
            size_hint_y=None,
            height=dp(50)
        )
        layout.add_widget(title)
        
        # Form layout
        form_layout = GridLayout(cols=1, spacing=dp(10), size_hint_y=None)
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        # API ID input
        form_layout.add_widget(Label(text="API ID:", size_hint_y=None, height=dp(30), halign='left'))
        self.api_id_input = TextInput(hint_text="Enter API ID", multiline=False, size_hint_y=None, height=dp(40))
        form_layout.add_widget(self.api_id_input)
        
        # API Hash input
        form_layout.add_widget(Label(text="API Hash:", size_hint_y=None, height=dp(30), halign='left'))
        self.api_hash_input = TextInput(hint_text="Enter API Hash", multiline=False, size_hint_y=None, height=dp(40))
        form_layout.add_widget(self.api_hash_input)
        
        # Bot Token input
        form_layout.add_widget(Label(text="Bot Token:", size_hint_y=None, height=dp(30), halign='left'))
        self.bot_token_input = TextInput(hint_text="Enter Bot Token", multiline=False, size_hint_y=None, height=dp(40))
        form_layout.add_widget(self.bot_token_input)
        
        # Add form to a scroll view
        scroll_view = ScrollView(size_hint=(1, 0.7))
        scroll_view.add_widget(form_layout)
        layout.add_widget(scroll_view)
        
        # Login button
        login_button = Button(
            text="Login",
            size_hint_y=None,
            height=dp(50),
            background_color=ButtonStyles.PRIMARY['background_color']
        )
        login_button.bind(on_press=self.login)
        layout.add_widget(login_button)
        
        # Load credentials button
        load_button = Button(
            text="Load Saved Credentials",
            size_hint_y=None,
            height=dp(50),
            background_color=ButtonStyles.SECONDARY['background_color']
        )
        load_button.bind(on_press=self.load_credentials)
        layout.add_widget(load_button)
        
        # Status label
        self.status_label = Label(
            text="",
            size_hint_y=None,
            height=dp(30)
        )
        layout.add_widget(self.status_label)
        
        self.add_widget(layout)
    
    def login(self, instance):
        """
        Handle login button press.
        """
        # Validate inputs
        api_id = self.api_id_input.text.strip()
        api_hash = self.api_hash_input.text.strip()
        bot_token = self.bot_token_input.text.strip()
        
        if not api_id or not api_hash or not bot_token:
            self.status_label.text = "Please fill in all fields"
            return
        
        # Save credentials to config
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'config.ini')
        
        if os.path.exists(config_path):
            config.read(config_path)
        
        if not config.has_section('telegram'):
            config.add_section('telegram')
        
        config.set('telegram', 'api_id', api_id)
        config.set('telegram', 'api_hash', api_hash)
        config.set('telegram', 'bot_token', bot_token)
        
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            config.write(f)
        
        self.status_label.text = "Connecting to Telegram..."
        
        # Simulate connection (in a real app, you would connect to Telegram API here)
        Clock.schedule_once(self.connect_to_telegram, 2)
    
    def load_credentials(self, instance):
        """
        Load saved credentials from config file.
        """
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'config.ini')
        
        if not os.path.exists(config_path):
            self.status_label.text = "No saved credentials found"
            return
        
        config.read(config_path)
        
        if not config.has_section('telegram'):
            self.status_label.text = "No Telegram credentials found"
            return
        
        try:
            self.api_id_input.text = config.get('telegram', 'api_id')
            self.api_hash_input.text = config.get('telegram', 'api_hash')
            self.bot_token_input.text = config.get('telegram', 'bot_token')
            self.status_label.text = "Credentials loaded"
        except configparser.NoOptionError:
            self.status_label.text = "Incomplete credentials found"
    
    def connect_to_telegram(self, dt):
        """
        Connect to Telegram API and transition to dashboard.
        """
        # In a real app, you would verify the connection here
        self.status_label.text = "Connected successfully!"
        
        # Transition to dashboard
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "dashboard"


class DashboardScreen(Screen):
    """
    Main dashboard screen showing groups/channels and quick actions.
    """
    def __init__(self, **kwargs):
        super(DashboardScreen, self).__init__(**kwargs)
        
        # Main layout
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Top bar with title and settings button
        top_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        title = Label(
            text="Dashboard",
            font_size=dp(20),
            size_hint_x=0.8
        )
        top_bar.add_widget(title)
        
        settings_button = Button(
            text="Settings",
            size_hint_x=0.2
        )
        settings_button.bind(on_press=self.go_to_settings)
        top_bar.add_widget(settings_button)
        
        layout.add_widget(top_bar)
        
        # Groups and channels section
        groups_layout = BoxLayout(orientation='vertical', size_hint_y=0.4)
        groups_layout.add_widget(Label(text="Your Groups & Channels", size_hint_y=None, height=dp(30)))
        
        # Scrollable list of groups and channels
        groups_grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None)
        groups_grid.bind(minimum_height=groups_grid.setter('height'))
        
        # Add some dummy groups/channels
        for i in range(5):
            group_item = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
            group_item.add_widget(Label(text=f"Group {i+1}", size_hint_x=0.7))
            manage_btn = Button(text="Manage", size_hint_x=0.3)
            manage_btn.bind(on_press=lambda x, i=i: self.manage_group(i))
            group_item.add_widget(manage_btn)
            groups_grid.add_widget(group_item)
        
        groups_scroll = ScrollView(size_hint=(1, 1))
        groups_scroll.add_widget(groups_grid)
        groups_layout.add_widget(groups_scroll)
        
        layout.add_widget(groups_layout)
        
        # Quick actions section
        actions_layout = BoxLayout(orientation='vertical', size_hint_y=0.6)
        actions_layout.add_widget(Label(text="Quick Actions", size_hint_y=None, height=dp(30)))
        
        # Grid of action buttons
        actions_grid = GridLayout(cols=2, spacing=dp(10))
        
        # Group Management button
        group_mgmt_btn = Button(
            text="Group Management",
            background_color=ButtonStyles.PRIMARY['background_color']
        )
        group_mgmt_btn.bind(on_press=self.go_to_group_management)
        actions_grid.add_widget(group_mgmt_btn)
        
        # Mass Messaging button
        mass_msg_btn = Button(
            text="Mass Messaging",
            background_color=ButtonStyles.PRIMARY['background_color']
        )
        mass_msg_btn.bind(on_press=self.go_to_mass_messaging)
        actions_grid.add_widget(mass_msg_btn)
        
        # Reporting button
        reporting_btn = Button(
            text="Reporting & Security",
            background_color=ButtonStyles.PRIMARY['background_color']
        )
        reporting_btn.bind(on_press=self.go_to_reporting)
        actions_grid.add_widget(reporting_btn)
        
        # Logs button
        logs_btn = Button(
            text="View Logs",
            background_color=ButtonStyles.PRIMARY['background_color']
        )
        logs_btn.bind(on_press=self.view_logs)
        actions_grid.add_widget(logs_btn)
        
        actions_layout.add_widget(actions_grid)
        
        layout.add_widget(actions_layout)
        
        # Status label
        self.status_label = Label(
            text="",
            size_hint_y=None,
            height=dp(30)
        )
        layout.add_widget(self.status_label)
        
        self.add_widget(layout)
    
    def manage_group(self, group_index):
        """
        Handle manage button press for a group.
        """
        self.status_label.text = f"Managing Group {group_index+1}"
        # In a real app, you would navigate to a group management screen for this specific group
    
    def go_to_group_management(self, instance):
        """
        Navigate to group management screen.
        """
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "group_management"
    
    def go_to_mass_messaging(self, instance):
        """
        Navigate to mass messaging screen.
        """
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "mass_messaging"
    
    def go_to_reporting(self, instance):
        """
        Navigate to reporting screen.
        """
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "reporting"
    
    def go_to_settings(self, instance):
        """
        Navigate to settings screen.
        """
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "settings"
    
    def view_logs(self, instance):
        """
        View logs.
        """
        self.status_label.text = "Viewing logs..."
        # In a real app, you would navigate to a logs screen


class TelegramSuperManagerApp(App):
    """
    Main application class.
    """
    def build(self):
        # Create screen manager
        sm = ScreenManager(transition=SlideTransition())
        
        # Add screens
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(GroupManagementScreen(name="group_management"))
        sm.add_widget(MassMessagingScreen(name="mass_messaging"))
        sm.add_widget(ReportingScreen(name="reporting"))
        sm.add_widget(SettingsScreen(name="settings"))
        
        return sm


if __name__ == "__main__":
    TelegramSuperManagerApp().run()