#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Telegram Super-Manager App - Group Management Screen
Screen for managing Telegram groups, including auto-kick, auto-delete, welcome messages, and logs.
"""

import os
import sys
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.spinner import Spinner
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import styles
from frontend.styles.theme import ButtonStyles, InputStyles, FontSizes, Spacing


class GroupManagementScreen(Screen):
    """
    Screen for managing Telegram groups.
    """
    selected_group = StringProperty("")
    
    def __init__(self, **kwargs):
        super(GroupManagementScreen, self).__init__(**kwargs)
        
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
            text="Group Management",
            font_size=dp(20),
            size_hint_x=0.8
        )
        top_bar.add_widget(title)
        
        layout.add_widget(top_bar)
        
        # Group selection
        group_selection = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80))
        group_selection.add_widget(Label(text="Select Group:", size_hint_y=None, height=dp(30), halign='left'))
        
        self.group_spinner = Spinner(
            text="Select a group",
            values=self.get_groups(),
            size_hint_y=None,
            height=dp(50)
        )
        self.group_spinner.bind(text=self.on_group_select)
        group_selection.add_widget(self.group_spinner)
        
        layout.add_widget(group_selection)
        
        # Tabs for different management features
        tabs_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        self.auto_mod_btn = ToggleButton(
            text="Auto-Moderation",
            group="management_tabs",
            state="down",
            size_hint_x=0.33
        )
        self.auto_mod_btn.bind(on_press=lambda x: self.switch_tab("auto_mod"))
        tabs_layout.add_widget(self.auto_mod_btn)
        
        self.welcome_btn = ToggleButton(
            text="Welcome",
            group="management_tabs",
            size_hint_x=0.33
        )
        self.welcome_btn.bind(on_press=lambda x: self.switch_tab("welcome"))
        tabs_layout.add_widget(self.welcome_btn)
        
        self.logs_btn = ToggleButton(
            text="Logs",
            group="management_tabs",
            size_hint_x=0.33
        )
        self.logs_btn.bind(on_press=lambda x: self.switch_tab("logs"))
        tabs_layout.add_widget(self.logs_btn)
        
        layout.add_widget(tabs_layout)
        
        # Content area (will be filled with selected tab content)
        self.content_layout = BoxLayout(orientation='vertical', padding=dp(10))
        
        # Create tab content layouts
        self.auto_mod_layout = self.create_auto_mod_layout()
        self.welcome_layout = self.create_welcome_layout()
        self.logs_layout = self.create_logs_layout()
        
        # Add auto-mod layout by default
        self.content_layout.add_widget(self.auto_mod_layout)
        
        layout.add_widget(self.content_layout)
        
        # Save button
        save_button = Button(
            text="Save Settings",
            size_hint_y=None,
            height=dp(50),
            background_color=ButtonStyles.PRIMARY['background_color']
        )
        save_button.bind(on_press=self.save_settings)
        layout.add_widget(save_button)
        
        # Status label
        self.status_label = Label(
            text="",
            size_hint_y=None,
            height=dp(30)
        )
        layout.add_widget(self.status_label)
        
        self.add_widget(layout)
    
    def get_groups(self):
        """
        Get list of groups from backend.
        """
        # In a real app, you would fetch groups from the database or Telegram API
        # For now, we'll use dummy data
        return ["Group 1", "Group 2", "Group 3"]
    
    def on_group_select(self, spinner, text):
        """
        Handle group selection.
        """
        self.selected_group = text
        self.load_group_settings(text)
    
    def load_group_settings(self, group_name):
        """
        Load settings for selected group.
        """
        # In a real app, you would fetch group settings from the database or Telegram API
        # For now, we'll use dummy data
        self.status_label.text = f"Loaded settings for {group_name}"
        
        # Update auto-mod settings
        self.spam_toggle.state = "down"  # Enable spam filter
        self.nsfw_toggle.state = "down"  # Enable NSFW filter
        self.phishing_toggle.state = "down"  # Enable phishing filter
        self.flood_toggle.state = "normal"  # Disable flood filter
        
        self.spam_action.text = "Kick"  # Set spam action to kick
        self.nsfw_action.text = "Delete"  # Set NSFW action to delete
        self.phishing_action.text = "Ban"  # Set phishing action to ban
        self.flood_action.text = "Mute"  # Set flood action to mute
        
        # Update welcome settings
        self.welcome_toggle.state = "down"  # Enable welcome message
        self.welcome_text.text = f"Welcome to {group_name}! Please read the rules and enjoy your stay."
        
        # Update logs settings
        self.log_joins_toggle.state = "down"  # Enable logging joins
        self.log_leaves_toggle.state = "down"  # Enable logging leaves
        self.log_messages_toggle.state = "normal"  # Disable logging messages
        self.log_actions_toggle.state = "down"  # Enable logging actions
    
    def switch_tab(self, tab_name):
        """
        Switch between management tabs.
        """
        self.content_layout.clear_widgets()
        
        if tab_name == "auto_mod":
            self.content_layout.add_widget(self.auto_mod_layout)
        elif tab_name == "welcome":
            self.content_layout.add_widget(self.welcome_layout)
        elif tab_name == "logs":
            self.content_layout.add_widget(self.logs_layout)
    
    def create_auto_mod_layout(self):
        """
        Create layout for auto-moderation settings.
        """
        layout = GridLayout(cols=1, spacing=dp(15), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        # Spam filter
        spam_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        spam_layout.add_widget(Label(text="Anti-Spam Filter", size_hint_x=0.4))
        self.spam_toggle = ToggleButton(text="Enabled", size_hint_x=0.3)
        spam_layout.add_widget(self.spam_toggle)
        self.spam_action = Spinner(
            text="Action",
            values=["Delete", "Kick", "Ban", "Mute"],
            size_hint_x=0.3
        )
        spam_layout.add_widget(self.spam_action)
        layout.add_widget(spam_layout)
        
        # NSFW filter
        nsfw_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        nsfw_layout.add_widget(Label(text="NSFW Filter", size_hint_x=0.4))
        self.nsfw_toggle = ToggleButton(text="Enabled", size_hint_x=0.3)
        nsfw_layout.add_widget(self.nsfw_toggle)
        self.nsfw_action = Spinner(
            text="Action",
            values=["Delete", "Kick", "Ban", "Mute"],
            size_hint_x=0.3
        )
        nsfw_layout.add_widget(self.nsfw_action)
        layout.add_widget(nsfw_layout)
        
        # Phishing filter
        phishing_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        phishing_layout.add_widget(Label(text="Phishing Filter", size_hint_x=0.4))
        self.phishing_toggle = ToggleButton(text="Enabled", size_hint_x=0.3)
        phishing_layout.add_widget(self.phishing_toggle)
        self.phishing_action = Spinner(
            text="Action",
            values=["Delete", "Kick", "Ban", "Mute"],
            size_hint_x=0.3
        )
        phishing_layout.add_widget(self.phishing_action)
        layout.add_widget(phishing_layout)
        
        # Flood filter
        flood_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        flood_layout.add_widget(Label(text="Anti-Flood Filter", size_hint_x=0.4))
        self.flood_toggle = ToggleButton(text="Enabled", size_hint_x=0.3)
        flood_layout.add_widget(self.flood_toggle)
        self.flood_action = Spinner(
            text="Action",
            values=["Delete", "Kick", "Ban", "Mute"],
            size_hint_x=0.3
        )
        flood_layout.add_widget(self.flood_action)
        layout.add_widget(flood_layout)
        
        # Flood settings
        flood_settings = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        flood_settings.add_widget(Label(text="Flood Threshold", size_hint_x=0.4))
        self.flood_threshold = TextInput(
            text="5",
            input_filter="int",
            multiline=False,
            size_hint_x=0.3
        )
        flood_settings.add_widget(self.flood_threshold)
        self.flood_time = TextInput(
            text="10",
            input_filter="int",
            multiline=False,
            size_hint_x=0.3
        )
        flood_settings.add_widget(self.flood_time)
        layout.add_widget(flood_settings)
        
        # Add description label
        layout.add_widget(Label(
            text="Flood threshold: messages per time period (seconds)",
            size_hint_y=None,
            height=dp(30),
            font_size=FontSizes.SMALL
        ))
        
        # Wrap in scroll view
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(layout)
        return scroll_view
    
    def create_welcome_layout(self):
        """
        Create layout for welcome message settings.
        """
        layout = GridLayout(cols=1, spacing=dp(15), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        # Welcome message toggle
        welcome_toggle_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        welcome_toggle_layout.add_widget(Label(text="Welcome Message", size_hint_x=0.7))
        self.welcome_toggle = ToggleButton(text="Enabled", size_hint_x=0.3)
        welcome_toggle_layout.add_widget(self.welcome_toggle)
        layout.add_widget(welcome_toggle_layout)
        
        # Welcome message text
        layout.add_widget(Label(text="Welcome Message Text:", size_hint_y=None, height=dp(30), halign='left'))
        self.welcome_text = TextInput(
            text="Welcome to our group! Please read the rules and enjoy your stay.",
            multiline=True,
            size_hint_y=None,
            height=dp(150)
        )
        layout.add_widget(self.welcome_text)
        
        # Variables explanation
        layout.add_widget(Label(
            text="Available variables: {user} - username, {group} - group name, {rules} - group rules",
            size_hint_y=None,
            height=dp(40),
            font_size=FontSizes.SMALL
        ))
        
        # Rules settings
        rules_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(200))
        rules_layout.add_widget(Label(text="Group Rules:", size_hint_y=None, height=dp(30), halign='left'))
        self.rules_text = TextInput(
            text="1. Be respectful to others\n2. No spam or flooding\n3. No NSFW content\n4. No phishing or scam links",
            multiline=True,
            size_hint_y=None,
            height=dp(150)
        )
        rules_layout.add_widget(self.rules_text)
        layout.add_widget(rules_layout)
        
        # Wrap in scroll view
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(layout)
        return scroll_view
    
    def create_logs_layout(self):
        """
        Create layout for logs settings.
        """
        layout = GridLayout(cols=1, spacing=dp(15), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        # Log settings
        layout.add_widget(Label(text="Log Settings:", size_hint_y=None, height=dp(30), halign='left'))
        
        # Log joins
        log_joins_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        log_joins_layout.add_widget(Label(text="Log User Joins", size_hint_x=0.7))
        self.log_joins_toggle = ToggleButton(text="Enabled", size_hint_x=0.3)
        log_joins_layout.add_widget(self.log_joins_toggle)
        layout.add_widget(log_joins_layout)
        
        # Log leaves
        log_leaves_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        log_leaves_layout.add_widget(Label(text="Log User Leaves", size_hint_x=0.7))
        self.log_leaves_toggle = ToggleButton(text="Enabled", size_hint_x=0.3)
        log_leaves_layout.add_widget(self.log_leaves_toggle)
        layout.add_widget(log_leaves_layout)
        
        # Log messages
        log_messages_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        log_messages_layout.add_widget(Label(text="Log Messages", size_hint_x=0.7))
        self.log_messages_toggle = ToggleButton(text="Enabled", size_hint_x=0.3)
        log_messages_layout.add_widget(self.log_messages_toggle)
        layout.add_widget(log_messages_layout)
        
        # Log actions
        log_actions_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        log_actions_layout.add_widget(Label(text="Log Admin Actions", size_hint_x=0.7))
        self.log_actions_toggle = ToggleButton(text="Enabled", size_hint_x=0.3)
        log_actions_layout.add_widget(self.log_actions_toggle)
        layout.add_widget(log_actions_layout)
        
        # Log destination
        log_dest_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100))
        log_dest_layout.add_widget(Label(text="Log Destination:", size_hint_y=None, height=dp(30), halign='left'))
        
        log_options = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        self.log_channel_btn = ToggleButton(
            text="Channel",
            group="log_destination",
            state="down",
            size_hint_x=0.5
        )
        log_options.add_widget(self.log_channel_btn)
        
        self.log_file_btn = ToggleButton(
            text="File",
            group="log_destination",
            size_hint_x=0.5
        )
        log_options.add_widget(self.log_file_btn)
        
        log_dest_layout.add_widget(log_options)
        layout.add_widget(log_dest_layout)
        
        # Log channel selection
        self.log_channel_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80))
        self.log_channel_layout.add_widget(Label(text="Select Log Channel:", size_hint_y=None, height=dp(30), halign='left'))
        
        self.log_channel_spinner = Spinner(
            text="Select a channel",
            values=self.get_channels(),
            size_hint_y=None,
            height=dp(50)
        )
        self.log_channel_layout.add_widget(self.log_channel_spinner)
        layout.add_widget(self.log_channel_layout)
        
        # View logs button
        view_logs_button = Button(
            text="View Recent Logs",
            size_hint_y=None,
            height=dp(50),
            background_color=ButtonStyles.SECONDARY['background_color']
        )
        view_logs_button.bind(on_press=self.view_logs)
        layout.add_widget(view_logs_button)
        
        # Wrap in scroll view
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(layout)
        return scroll_view
    
    def get_channels(self):
        """
        Get list of channels from backend.
        """
        # In a real app, you would fetch channels from the database or Telegram API
        # For now, we'll use dummy data
        return ["Log Channel 1", "Log Channel 2", "Log Channel 3"]
    
    def save_settings(self, instance):
        """
        Save group management settings.
        """
        if not self.selected_group:
            self.status_label.text = "Please select a group first"
            return
        
        # In a real app, you would save settings to the database and update the bot
        # For now, we'll just show a success message
        self.status_label.text = f"Settings saved for {self.selected_group}"
    
    def view_logs(self, instance):
        """
        View recent logs for the selected group.
        """
        if not self.selected_group:
            self.status_label.text = "Please select a group first"
            return
        
        # In a real app, you would fetch and display logs
        # For now, we'll just show a message
        self.status_label.text = f"Viewing logs for {self.selected_group}"
    
    def go_back(self, instance):
        """
        Go back to dashboard screen.
        """
        self.manager.transition.direction = "right"
        self.manager.current = "dashboard"