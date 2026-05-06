#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Telegram Super-Manager App - Settings Screen
Screen for app settings, including theme selection, notification preferences, and account management.
"""

import os
import sys
import json
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.switch import Switch
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, ListProperty

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import styles
from frontend.styles.theme import ButtonStyles, InputStyles, FontSizes, Spacing, apply_theme


class SettingsScreen(Screen):
    """
    Screen for app settings and preferences.
    """
    theme_mode = StringProperty("light")
    
    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        
        # Main layout
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Top bar with title and back button
        top_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        back_button = Button(
            text="Back",
            size_hint_x=0.2
        )
        back_button.bind(on_press=self.go_back)
        top_bar.add_widget(back_button)
        
        title = Label(
            text="Settings",
            font_size=dp(20),
            size_hint_x=0.8
        )
        top_bar.add_widget(title)
        
        layout.add_widget(top_bar)
        
        # Settings content
        settings_layout = GridLayout(cols=1, spacing=dp(15), size_hint_y=None)
        settings_layout.bind(minimum_height=settings_layout.setter('height'))
        
        # Theme settings
        theme_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120))
        theme_layout.add_widget(Label(
            text="Appearance",
            font_size=dp(18),
            size_hint_y=None,
            height=dp(40),
            halign='left'
        ))
        
        # Dark/Light mode toggle
        theme_toggle_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        theme_toggle_layout.add_widget(Label(
            text="Dark Mode",
            size_hint_x=0.7,
            halign='left'
        ))
        
        self.theme_switch = Switch(
            active=False,  # Default to light mode
            size_hint_x=0.3
        )
        self.theme_switch.bind(active=self.on_theme_switch)
        theme_toggle_layout.add_widget(self.theme_switch)
        
        theme_layout.add_widget(theme_toggle_layout)
        
        settings_layout.add_widget(theme_layout)
        
        # Notification settings
        notification_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(200))
        notification_layout.add_widget(Label(
            text="Notifications",
            font_size=dp(18),
            size_hint_y=None,
            height=dp(40),
            halign='left'
        ))
        
        # Group notifications
        group_notif_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        group_notif_layout.add_widget(Label(
            text="Group Activity",
            size_hint_x=0.7,
            halign='left'
        ))
        
        self.group_notif_switch = Switch(
            active=True,
            size_hint_x=0.3
        )
        group_notif_layout.add_widget(self.group_notif_switch)
        notification_layout.add_widget(group_notif_layout)
        
        # Report notifications
        report_notif_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        report_notif_layout.add_widget(Label(
            text="Report Status",
            size_hint_x=0.7,
            halign='left'
        ))
        
        self.report_notif_switch = Switch(
            active=True,
            size_hint_x=0.3
        )
        report_notif_layout.add_widget(self.report_notif_switch)
        notification_layout.add_widget(report_notif_layout)
        
        # Direct message notifications
        dm_notif_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        dm_notif_layout.add_widget(Label(
            text="Direct Messages",
            size_hint_x=0.7,
            halign='left'
        ))
        
        self.dm_notif_switch = Switch(
            active=True,
            size_hint_x=0.3
        )
        dm_notif_layout.add_widget(self.dm_notif_switch)
        notification_layout.add_widget(dm_notif_layout)
        
        settings_layout.add_widget(notification_layout)
        
        # API settings
        api_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(200))
        api_layout.add_widget(Label(
            text="API Settings",
            font_size=dp(18),
            size_hint_y=None,
            height=dp(40),
            halign='left'
        ))
        
        # API ID input
        api_id_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        api_id_layout.add_widget(Label(
            text="API ID",
            size_hint_x=0.3,
            halign='left'
        ))
        
        self.api_id_input = TextInput(
            hint_text="Enter API ID",
            multiline=False,
            input_filter="int",
            size_hint_x=0.7
        )
        api_id_layout.add_widget(self.api_id_input)
        api_layout.add_widget(api_id_layout)
        
        # API Hash input
        api_hash_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        api_hash_layout.add_widget(Label(
            text="API Hash",
            size_hint_x=0.3,
            halign='left'
        ))
        
        self.api_hash_input = TextInput(
            hint_text="Enter API Hash",
            multiline=False,
            password=True,
            size_hint_x=0.7
        )
        api_hash_layout.add_widget(self.api_hash_input)
        api_layout.add_widget(api_hash_layout)
        
        # Bot Token input
        bot_token_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        bot_token_layout.add_widget(Label(
            text="Bot Token",
            size_hint_x=0.3,
            halign='left'
        ))
        
        self.bot_token_input = TextInput(
            hint_text="Enter Bot Token",
            multiline=False,
            password=True,
            size_hint_x=0.7
        )
        bot_token_layout.add_widget(self.bot_token_input)
        api_layout.add_widget(bot_token_layout)
        
        settings_layout.add_widget(api_layout)
        
        # Database settings
        db_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(150))
        db_layout.add_widget(Label(
            text="Database Settings",
            font_size=dp(18),
            size_hint_y=None,
            height=dp(40),
            halign='left'
        ))
        
        # Database type selection
        db_type_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        db_type_layout.add_widget(Label(
            text="Database Type",
            size_hint_x=0.3,
            halign='left'
        ))
        
        db_buttons = BoxLayout(orientation='horizontal', size_hint_x=0.7)
        
        self.sqlite_btn = ToggleButton(
            text="SQLite",
            group="db_type",
            state="down",
            size_hint_x=0.5
        )
        self.sqlite_btn.bind(on_press=lambda x: self.on_db_type_change("sqlite"))
        db_buttons.add_widget(self.sqlite_btn)
        
        self.postgres_btn = ToggleButton(
            text="PostgreSQL",
            group="db_type",
            size_hint_x=0.5
        )
        self.postgres_btn.bind(on_press=lambda x: self.on_db_type_change("postgres"))
        db_buttons.add_widget(self.postgres_btn)
        
        db_type_layout.add_widget(db_buttons)
        db_layout.add_widget(db_type_layout)
        
        # PostgreSQL connection string (hidden by default)
        self.postgres_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        self.postgres_layout.add_widget(Label(
            text="Connection",
            size_hint_x=0.3,
            halign='left'
        ))
        
        self.postgres_input = TextInput(
            hint_text="postgresql://user:pass@localhost/dbname",
            multiline=False,
            size_hint_x=0.7
        )
        self.postgres_layout.add_widget(self.postgres_input)
        
        # Don't add postgres layout by default (will be added when PostgreSQL is selected)
        
        settings_layout.add_widget(db_layout)
        
        # Advanced settings
        advanced_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(150))
        advanced_layout.add_widget(Label(
            text="Advanced Settings",
            font_size=dp(18),
            size_hint_y=None,
            height=dp(40),
            halign='left'
        ))
        
        # Debug mode
        debug_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        debug_layout.add_widget(Label(
            text="Debug Mode",
            size_hint_x=0.7,
            halign='left'
        ))
        
        self.debug_switch = Switch(
            active=False,
            size_hint_x=0.3
        )
        debug_layout.add_widget(self.debug_switch)
        advanced_layout.add_widget(debug_layout)
        
        # Log level
        log_level_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        log_level_layout.add_widget(Label(
            text="Log Level",
            size_hint_x=0.3,
            halign='left'
        ))
        
        self.log_level_spinner = TextInput(
            text="INFO",
            hint_text="DEBUG, INFO, WARNING, ERROR, CRITICAL",
            multiline=False,
            size_hint_x=0.7
        )
        log_level_layout.add_widget(self.log_level_spinner)
        advanced_layout.add_widget(log_level_layout)
        
        settings_layout.add_widget(advanced_layout)
        
        # Save button
        save_button = Button(
            text="Save Settings",
            size_hint_y=None,
            height=dp(50),
            background_color=ButtonStyles.PRIMARY['background_color']
        )
        save_button.bind(on_press=self.save_settings)
        settings_layout.add_widget(save_button)
        
        # Status label
        self.status_label = Label(
            text="",
            size_hint_y=None,
            height=dp(30)
        )
        settings_layout.add_widget(self.status_label)
        
        # Wrap in scroll view
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(settings_layout)
        layout.add_widget(scroll_view)
        
        self.add_widget(layout)
        
        # Load settings
        self.load_settings()
    
    def on_theme_switch(self, instance, value):
        """
        Handle theme switch toggle.
        """
        self.theme_mode = "dark" if value else "light"
        # In a real app, you would apply the theme immediately
        # For now, we'll just update the status label
        self.status_label.text = f"Theme set to {self.theme_mode} mode (will apply after save)"
    
    def on_db_type_change(self, db_type):
        """
        Handle database type change.
        """
        if db_type == "postgres":
            # Add PostgreSQL connection string input if not already added
            if self.postgres_layout not in self.children[0].children[0].children[0].children[0].children[3].children:
                self.children[0].children[0].children[0].children[0].children[3].add_widget(self.postgres_layout)
        else:
            # Remove PostgreSQL connection string input if added
            if self.postgres_layout in self.children[0].children[0].children[0].children[0].children[3].children:
                self.children[0].children[0].children[0].children[0].children[3].remove_widget(self.postgres_layout)
    
    def load_settings(self):
        """
        Load settings from config file.
        """
        try:
            # In a real app, you would load settings from a config file or database
            # For now, we'll use dummy settings
            settings = {
                "theme": "light",
                "notifications": {
                    "group": True,
                    "report": True,
                    "dm": True
                },
                "api": {
                    "api_id": "",
                    "api_hash": "",
                    "bot_token": ""
                },
                "database": {
                    "type": "sqlite",
                    "connection": ""
                },
                "advanced": {
                    "debug": False,
                    "log_level": "INFO"
                }
            }
            
            # Apply settings to UI
            self.theme_switch.active = settings["theme"] == "dark"
            self.group_notif_switch.active = settings["notifications"]["group"]
            self.report_notif_switch.active = settings["notifications"]["report"]
            self.dm_notif_switch.active = settings["notifications"]["dm"]
            
            self.api_id_input.text = settings["api"]["api_id"]
            self.api_hash_input.text = settings["api"]["api_hash"]
            self.bot_token_input.text = settings["api"]["bot_token"]
            
            if settings["database"]["type"] == "postgres":
                self.postgres_btn.state = "down"
                self.sqlite_btn.state = "normal"
                self.on_db_type_change("postgres")
                self.postgres_input.text = settings["database"]["connection"]
            else:
                self.sqlite_btn.state = "down"
                self.postgres_btn.state = "normal"
                self.on_db_type_change("sqlite")
            
            self.debug_switch.active = settings["advanced"]["debug"]
            self.log_level_spinner.text = settings["advanced"]["log_level"]
            
        except Exception as e:
            self.status_label.text = f"Error loading settings: {str(e)}"
    
    def save_settings(self, instance):
        """
        Save settings to config file.
        """
        try:
            # Collect settings from UI
            settings = {
                "theme": "dark" if self.theme_switch.active else "light",
                "notifications": {
                    "group": self.group_notif_switch.active,
                    "report": self.report_notif_switch.active,
                    "dm": self.dm_notif_switch.active
                },
                "api": {
                    "api_id": self.api_id_input.text,
                    "api_hash": self.api_hash_input.text,
                    "bot_token": self.bot_token_input.text
                },
                "database": {
                    "type": "postgres" if self.postgres_btn.state == "down" else "sqlite",
                    "connection": self.postgres_input.text if self.postgres_btn.state == "down" else ""
                },
                "advanced": {
                    "debug": self.debug_switch.active,
                    "log_level": self.log_level_spinner.text
                }
            }
            
            # In a real app, you would save settings to a config file or database
            # For now, we'll just show a success message
            self.status_label.text = "Settings saved successfully"
            
            # Update config.ini file
            self.update_config_file(settings)
            
        except Exception as e:
            self.status_label.text = f"Error saving settings: {str(e)}"
    
    def update_config_file(self, settings):
        """
        Update config.ini file with new settings.
        """
        try:
            import configparser
            config = configparser.ConfigParser()
            
            # Try to read existing config file
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config', 'config.ini')
            config.read(config_path)
            
            # Update sections
            if 'Telegram' not in config:
                config.add_section('Telegram')
            config['Telegram']['api_id'] = settings['api']['api_id']
            config['Telegram']['api_hash'] = settings['api']['api_hash']
            config['Telegram']['bot_token'] = settings['api']['bot_token']
            
            if 'Database' not in config:
                config.add_section('Database')
            config['Database']['type'] = settings['database']['type']
            if settings['database']['type'] == 'postgres':
                config['Database']['postgres_connection'] = settings['database']['connection']
            
            if 'App' not in config:
                config.add_section('App')
            config['App']['debug'] = str(settings['advanced']['debug']).lower()
            config['App']['log_level'] = settings['advanced']['log_level']
            config['App']['theme'] = settings['theme']
            
            # Write to file
            with open(config_path, 'w') as configfile:
                config.write(configfile)
            
            self.status_label.text = "Settings saved to config.ini"
            
        except Exception as e:
            self.status_label.text = f"Error updating config file: {str(e)}"
    
    def go_back(self, instance):
        """
        Go back to dashboard screen.
        """
        self.manager.transition.direction = "right"
        self.manager.current = "dashboard"