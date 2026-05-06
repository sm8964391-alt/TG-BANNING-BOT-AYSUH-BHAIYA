#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Telegram Super-Manager App - Mass Messaging Screen
Screen for mass messaging features, including mass DM and mass forward with filtering options.
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
from kivy.uix.checkbox import CheckBox
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, NumericProperty

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import styles
from frontend.styles.theme import ButtonStyles, InputStyles, FontSizes, Spacing


class MassMessagingScreen(Screen):
    """
    Screen for mass messaging features.
    """
    selected_source = StringProperty("")
    message_type = StringProperty("dm")  # 'dm' or 'forward'
    
    def __init__(self, **kwargs):
        super(MassMessagingScreen, self).__init__(**kwargs)
        
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
            text="Mass Messaging",
            font_size=dp(20),
            size_hint_x=0.8
        )
        top_bar.add_widget(title)
        
        layout.add_widget(top_bar)
        
        # Message type selection
        message_type_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        self.dm_btn = ToggleButton(
            text="Mass DM",
            group="message_type",
            state="down",
            size_hint_x=0.5
        )
        self.dm_btn.bind(on_press=lambda x: self.set_message_type("dm"))
        message_type_layout.add_widget(self.dm_btn)
        
        self.forward_btn = ToggleButton(
            text="Mass Forward",
            group="message_type",
            size_hint_x=0.5
        )
        self.forward_btn.bind(on_press=lambda x: self.set_message_type("forward"))
        message_type_layout.add_widget(self.forward_btn)
        
        layout.add_widget(message_type_layout)
        
        # Content area (will be filled with selected message type content)
        self.content_layout = BoxLayout(orientation='vertical', padding=dp(10))
        
        # Create message type layouts
        self.dm_layout = self.create_dm_layout()
        self.forward_layout = self.create_forward_layout()
        
        # Add DM layout by default
        self.content_layout.add_widget(self.dm_layout)
        
        layout.add_widget(self.content_layout)
        
        # Status label
        self.status_label = Label(
            text="",
            size_hint_y=None,
            height=dp(30)
        )
        layout.add_widget(self.status_label)
        
        self.add_widget(layout)
    
    def set_message_type(self, message_type):
        """
        Switch between mass DM and mass forward.
        """
        self.message_type = message_type
        self.content_layout.clear_widgets()
        
        if message_type == "dm":
            self.content_layout.add_widget(self.dm_layout)
        else:
            self.content_layout.add_widget(self.forward_layout)
    
    def create_dm_layout(self):
        """
        Create layout for mass DM.
        """
        layout = GridLayout(cols=1, spacing=dp(15), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        # Source selection
        source_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80))
        source_layout.add_widget(Label(text="Select Channel (subscribers will receive DM):", size_hint_y=None, height=dp(30), halign='left'))
        
        self.source_spinner = Spinner(
            text="Select a channel",
            values=self.get_channels(),
            size_hint_y=None,
            height=dp(50)
        )
        self.source_spinner.bind(text=self.on_source_select)
        source_layout.add_widget(self.source_spinner)
        
        layout.add_widget(source_layout)
        
        # Filtering options
        filter_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(150))
        filter_layout.add_widget(Label(text="Filter Options:", size_hint_y=None, height=dp(30), halign='left'))
        
        # Active users filter
        active_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        active_layout.add_widget(Label(text="Only Active Users", size_hint_x=0.7, halign='left'))
        self.active_check = CheckBox(active=True, size_hint_x=0.3)
        active_layout.add_widget(self.active_check)
        filter_layout.add_widget(active_layout)
        
        # Activity period
        activity_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        activity_layout.add_widget(Label(text="Active Within (days):", size_hint_x=0.7, halign='left'))
        self.activity_input = TextInput(
            text="30",
            input_filter="int",
            multiline=False,
            size_hint_x=0.3
        )
        activity_layout.add_widget(self.activity_input)
        filter_layout.add_widget(activity_layout)
        
        # Exclude bots
        bots_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        bots_layout.add_widget(Label(text="Exclude Bots", size_hint_x=0.7, halign='left'))
        self.bots_check = CheckBox(active=True, size_hint_x=0.3)
        bots_layout.add_widget(self.bots_check)
        filter_layout.add_widget(bots_layout)
        
        layout.add_widget(filter_layout)
        
        # Message content
        message_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(200))
        message_layout.add_widget(Label(text="Message Content:", size_hint_y=None, height=dp(30), halign='left'))
        
        self.message_text = TextInput(
            hint_text="Enter your message here...",
            multiline=True,
            size_hint_y=None,
            height=dp(150)
        )
        message_layout.add_widget(self.message_text)
        
        layout.add_widget(message_layout)
        
        # Variables explanation
        layout.add_widget(Label(
            text="Available variables: {user} - username, {first_name}, {last_name}",
            size_hint_y=None,
            height=dp(40),
            font_size=FontSizes.SMALL
        ))
        
        # Speed control
        speed_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100))
        speed_layout.add_widget(Label(text="Speed Control:", size_hint_y=None, height=dp(30), halign='left'))
        
        delay_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        delay_layout.add_widget(Label(text="Delay Between Messages (seconds):", size_hint_x=0.7, halign='left'))
        self.delay_input = TextInput(
            text="5",
            input_filter="float",
            multiline=False,
            size_hint_x=0.3
        )
        delay_layout.add_widget(self.delay_input)
        speed_layout.add_widget(delay_layout)
        
        layout.add_widget(speed_layout)
        
        # Send button
        send_button = Button(
            text="Send Mass DM",
            size_hint_y=None,
            height=dp(50),
            background_color=ButtonStyles.PRIMARY['background_color']
        )
        send_button.bind(on_press=self.send_mass_dm)
        layout.add_widget(send_button)
        
        # Wrap in scroll view
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(layout)
        return scroll_view
    
    def create_forward_layout(self):
        """
        Create layout for mass forward.
        """
        layout = GridLayout(cols=1, spacing=dp(15), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        # Source message selection
        source_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(150))
        source_layout.add_widget(Label(text="Source Message:", size_hint_y=None, height=dp(30), halign='left'))
        
        # Channel selection
        channel_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        channel_layout.add_widget(Label(text="Channel:", size_hint_x=0.3, halign='left'))
        
        self.channel_spinner = Spinner(
            text="Select channel",
            values=self.get_channels(),
            size_hint_x=0.7
        )
        channel_layout.add_widget(self.channel_spinner)
        source_layout.add_widget(channel_layout)
        
        # Message ID input
        message_id_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        message_id_layout.add_widget(Label(text="Message ID:", size_hint_x=0.3, halign='left'))
        
        self.message_id_input = TextInput(
            hint_text="Enter message ID",
            input_filter="int",
            multiline=False,
            size_hint_x=0.7
        )
        message_id_layout.add_widget(self.message_id_input)
        source_layout.add_widget(message_id_layout)
        
        layout.add_widget(source_layout)
        
        # Target selection
        target_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(200))
        target_layout.add_widget(Label(text="Target Groups/Channels:", size_hint_y=None, height=dp(30), halign='left'))
        
        # Target list
        targets_grid = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        targets_grid.bind(minimum_height=targets_grid.setter('height'))
        
        for target in self.get_targets():
            target_item = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
            target_item.add_widget(Label(text=target, size_hint_x=0.7, halign='left'))
            target_check = CheckBox(active=False, size_hint_x=0.3)
            target_item.add_widget(target_check)
            targets_grid.add_widget(target_item)
            setattr(self, f"target_{target.replace(' ', '_').lower()}_check", target_check)
        
        targets_scroll = ScrollView(size_hint_y=None, height=dp(150))
        targets_scroll.add_widget(targets_grid)
        target_layout.add_widget(targets_scroll)
        
        layout.add_widget(target_layout)
        
        # Speed control
        speed_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100))
        speed_layout.add_widget(Label(text="Speed Control:", size_hint_y=None, height=dp(30), halign='left'))
        
        delay_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        delay_layout.add_widget(Label(text="Delay Between Forwards (seconds):", size_hint_x=0.7, halign='left'))
        self.forward_delay_input = TextInput(
            text="5",
            input_filter="float",
            multiline=False,
            size_hint_x=0.3
        )
        delay_layout.add_widget(self.forward_delay_input)
        speed_layout.add_widget(delay_layout)
        
        layout.add_widget(speed_layout)
        
        # Forward button
        forward_button = Button(
            text="Forward Message",
            size_hint_y=None,
            height=dp(50),
            background_color=ButtonStyles.PRIMARY['background_color']
        )
        forward_button.bind(on_press=self.send_mass_forward)
        layout.add_widget(forward_button)
        
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
        return ["Channel 1", "Channel 2", "Channel 3"]
    
    def get_targets(self):
        """
        Get list of potential target groups and channels for forwarding.
        """
        # In a real app, you would fetch groups and channels from the database or Telegram API
        # For now, we'll use dummy data
        return ["Group 1", "Group 2", "Group 3", "Channel 1", "Channel 2"]
    
    def on_source_select(self, spinner, text):
        """
        Handle source selection for mass DM.
        """
        self.selected_source = text
        self.status_label.text = f"Selected channel: {text}"
    
    def send_mass_dm(self, instance):
        """
        Send mass DM to subscribers of selected channel.
        """
        if not self.selected_source:
            self.status_label.text = "Please select a source channel"
            return
        
        if not self.message_text.text.strip():
            self.status_label.text = "Please enter a message"
            return
        
        # Get filter settings
        active_only = self.active_check.active
        activity_days = self.activity_input.text
        exclude_bots = self.bots_check.active
        delay = self.delay_input.text
        
        # In a real app, you would call the backend to send mass DM
        # For now, we'll just show a success message
        self.status_label.text = f"Sending mass DM to subscribers of {self.selected_source}..."
        
        # Simulate sending process
        import threading
        threading.Thread(target=self.simulate_sending, args=("dm",)).start()
    
    def send_mass_forward(self, instance):
        """
        Forward message to selected targets.
        """
        channel = self.channel_spinner.text
        message_id = self.message_id_input.text.strip()
        
        if channel == "Select channel" or not message_id:
            self.status_label.text = "Please select a source channel and enter message ID"
            return
        
        # Get selected targets
        selected_targets = []
        for target in self.get_targets():
            target_attr = f"target_{target.replace(' ', '_').lower()}_check"
            if hasattr(self, target_attr) and getattr(self, target_attr).active:
                selected_targets.append(target)
        
        if not selected_targets:
            self.status_label.text = "Please select at least one target"
            return
        
        # Get delay setting
        delay = self.forward_delay_input.text
        
        # In a real app, you would call the backend to forward message
        # For now, we'll just show a success message
        targets_str = ", ".join(selected_targets)
        self.status_label.text = f"Forwarding message from {channel} to {targets_str}..."
        
        # Simulate sending process
        import threading
        threading.Thread(target=self.simulate_sending, args=("forward",)).start()
    
    def simulate_sending(self, message_type):
        """
        Simulate sending process.
        """
        import time
        from kivy.clock import Clock
        
        # Simulate progress updates
        for i in range(1, 6):
            time.sleep(1)  # Simulate delay
            message = f"Sending {message_type}... {i*20}% complete"
            Clock.schedule_once(lambda dt, msg=message: setattr(self.status_label, 'text', msg), 0)
        
        # Simulate completion
        time.sleep(1)
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', f"{message_type.upper()} sent successfully!"), 0)
    
    def go_back(self, instance):
        """
        Go back to dashboard screen.
        """
        self.manager.transition.direction = "right"
        self.manager.current = "dashboard"