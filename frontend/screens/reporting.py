#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Telegram Super-Manager App - Reporting Screen
Screen for reporting and security features, including automated reporting and multi-account reporting.
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
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, ListProperty

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import styles
from frontend.styles.theme import ButtonStyles, InputStyles, FontSizes, Spacing


class ReportingScreen(Screen):
    """
    Screen for reporting and security features.
    """
    report_type = StringProperty("user")
    active_sessions = ListProperty([])
    
    def __init__(self, **kwargs):
        super(ReportingScreen, self).__init__(**kwargs)
        
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
            text="Reporting & Security",
            font_size=dp(20),
            size_hint_x=0.8
        )
        top_bar.add_widget(title)
        
        layout.add_widget(top_bar)
        
        # Tabs for different features
        tabs_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        self.report_btn = ToggleButton(
            text="Report",
            group="reporting_tabs",
            state="down",
            size_hint_x=0.33
        )
        self.report_btn.bind(on_press=lambda x: self.switch_tab("report"))
        tabs_layout.add_widget(self.report_btn)
        
        self.sessions_btn = ToggleButton(
            text="Sessions",
            group="reporting_tabs",
            size_hint_x=0.33
        )
        self.sessions_btn.bind(on_press=lambda x: self.switch_tab("sessions"))
        tabs_layout.add_widget(self.sessions_btn)
        
        self.logs_btn = ToggleButton(
            text="Logs",
            group="reporting_tabs",
            size_hint_x=0.33
        )
        self.logs_btn.bind(on_press=lambda x: self.switch_tab("logs"))
        tabs_layout.add_widget(self.logs_btn)
        
        layout.add_widget(tabs_layout)
        
        # Content area (will be filled with selected tab content)
        self.content_layout = BoxLayout(orientation='vertical', padding=dp(10))
        
        # Create tab content layouts
        self.report_layout = self.create_report_layout()
        self.sessions_layout = self.create_sessions_layout()
        self.logs_layout = self.create_logs_layout()
        
        # Add report layout by default
        self.content_layout.add_widget(self.report_layout)
        
        layout.add_widget(self.content_layout)
        
        # Status label
        self.status_label = Label(
            text="",
            size_hint_y=None,
            height=dp(30)
        )
        layout.add_widget(self.status_label)
        
        self.add_widget(layout)
        
        # Load active sessions
        self.load_active_sessions()
    
    def switch_tab(self, tab_name):
        """
        Switch between tabs.
        """
        self.content_layout.clear_widgets()
        
        if tab_name == "report":
            self.content_layout.add_widget(self.report_layout)
        elif tab_name == "sessions":
            self.content_layout.add_widget(self.sessions_layout)
        elif tab_name == "logs":
            self.content_layout.add_widget(self.logs_layout)
    
    def create_report_layout(self):
        """
        Create layout for reporting.
        """
        layout = GridLayout(cols=1, spacing=dp(15), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        # Report type selection
        report_type_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100))
        report_type_layout.add_widget(Label(text="Report Type:", size_hint_y=None, height=dp(30), halign='left'))
        
        report_buttons = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        self.user_btn = ToggleButton(
            text="User",
            group="report_type",
            state="down",
            size_hint_x=0.33
        )
        self.user_btn.bind(on_press=lambda x: self.set_report_type("user"))
        report_buttons.add_widget(self.user_btn)
        
        self.group_btn = ToggleButton(
            text="Group",
            group="report_type",
            size_hint_x=0.33
        )
        self.group_btn.bind(on_press=lambda x: self.set_report_type("group"))
        report_buttons.add_widget(self.group_btn)
        
        self.message_btn = ToggleButton(
            text="Message",
            group="report_type",
            size_hint_x=0.33
        )
        self.message_btn.bind(on_press=lambda x: self.set_report_type("message"))
        report_buttons.add_widget(self.message_btn)
        
        report_type_layout.add_widget(report_buttons)
        layout.add_widget(report_type_layout)
        
        # Target input
        target_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100))
        
        # User target input
        self.user_target_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80))
        self.user_target_layout.add_widget(Label(text="User ID or Username:", size_hint_y=None, height=dp(30), halign='left'))
        self.user_target_input = TextInput(
            hint_text="Enter user ID or username",
            multiline=False,
            size_hint_y=None,
            height=dp(50)
        )
        self.user_target_layout.add_widget(self.user_target_input)
        
        # Group target input
        self.group_target_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80))
        self.group_target_layout.add_widget(Label(text="Group ID or Username:", size_hint_y=None, height=dp(30), halign='left'))
        self.group_target_input = TextInput(
            hint_text="Enter group ID or username",
            multiline=False,
            size_hint_y=None,
            height=dp(50)
        )
        self.group_target_layout.add_widget(self.group_target_input)
        
        # Message target input
        self.message_target_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(150))
        self.message_target_layout.add_widget(Label(text="Message Details:", size_hint_y=None, height=dp(30), halign='left'))
        
        message_chat_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        message_chat_layout.add_widget(Label(text="Chat:", size_hint_x=0.3, halign='left'))
        self.message_chat_input = TextInput(
            hint_text="Enter chat ID or username",
            multiline=False,
            size_hint_x=0.7
        )
        message_chat_layout.add_widget(self.message_chat_input)
        self.message_target_layout.add_widget(message_chat_layout)
        
        message_id_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        message_id_layout.add_widget(Label(text="Message ID:", size_hint_x=0.3, halign='left'))
        self.message_id_input = TextInput(
            hint_text="Enter message ID",
            input_filter="int",
            multiline=False,
            size_hint_x=0.7
        )
        message_id_layout.add_widget(self.message_id_input)
        self.message_target_layout.add_widget(message_id_layout)
        
        # Add user target layout by default
        target_layout.add_widget(self.user_target_layout)
        layout.add_widget(target_layout)
        
        # Reason selection
        reason_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100))
        reason_layout.add_widget(Label(text="Report Reason:", size_hint_y=None, height=dp(30), halign='left'))
        
        self.reason_spinner = Spinner(
            text="Select reason",
            values=["Spam", "Fake Account", "Pornography", "Violence", "Child Abuse", "Other"],
            size_hint_y=None,
            height=dp(50)
        )
        reason_layout.add_widget(self.reason_spinner)
        
        layout.add_widget(reason_layout)
        
        # Additional details
        details_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(150))
        details_layout.add_widget(Label(text="Additional Details (Optional):", size_hint_y=None, height=dp(30), halign='left'))
        
        self.details_input = TextInput(
            hint_text="Enter additional details about the report",
            multiline=True,
            size_hint_y=None,
            height=dp(100)
        )
        details_layout.add_widget(self.details_input)
        
        layout.add_widget(details_layout)
        
        # Multi-account reporting
        multi_account_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100))
        multi_account_layout.add_widget(Label(text="Multi-Account Reporting:", size_hint_y=None, height=dp(30), halign='left'))
        
        multi_account_toggle_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        multi_account_toggle_layout.add_widget(Label(text="Use All Active Sessions", size_hint_x=0.7, halign='left'))
        self.multi_account_toggle = ToggleButton(
            text="Enabled",
            size_hint_x=0.3
        )
        multi_account_toggle_layout.add_widget(self.multi_account_toggle)
        multi_account_layout.add_widget(multi_account_toggle_layout)
        
        layout.add_widget(multi_account_layout)
        
        # Report button
        report_button = Button(
            text="Submit Report",
            size_hint_y=None,
            height=dp(50),
            background_color=ButtonStyles.DANGER['background_color']
        )
        report_button.bind(on_press=self.submit_report)
        layout.add_widget(report_button)
        
        # Wrap in scroll view
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(layout)
        return scroll_view
    
    def create_sessions_layout(self):
        """
        Create layout for managing sessions.
        """
        layout = GridLayout(cols=1, spacing=dp(15), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        # Add session section
        add_session_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(150))
        add_session_layout.add_widget(Label(text="Add New Session:", size_hint_y=None, height=dp(30), halign='left'))
        
        self.session_input = TextInput(
            hint_text="Enter session string",
            multiline=False,
            size_hint_y=None,
            height=dp(50)
        )
        add_session_layout.add_widget(self.session_input)
        
        add_button = Button(
            text="Add Session",
            size_hint_y=None,
            height=dp(50),
            background_color=ButtonStyles.PRIMARY['background_color']
        )
        add_button.bind(on_press=self.add_session)
        add_session_layout.add_widget(add_button)
        
        layout.add_widget(add_session_layout)
        
        # Active sessions section
        active_sessions_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(300))
        active_sessions_layout.add_widget(Label(text="Active Sessions:", size_hint_y=None, height=dp(30), halign='left'))
        
        # Sessions list
        self.sessions_grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None)
        self.sessions_grid.bind(minimum_height=self.sessions_grid.setter('height'))
        
        # Will be populated in load_active_sessions()
        
        sessions_scroll = ScrollView(size_hint_y=None, height=dp(250))
        sessions_scroll.add_widget(self.sessions_grid)
        active_sessions_layout.add_widget(sessions_scroll)
        
        layout.add_widget(active_sessions_layout)
        
        # Wrap in scroll view
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(layout)
        return scroll_view
    
    def create_logs_layout(self):
        """
        Create layout for viewing report logs.
        """
        layout = GridLayout(cols=1, spacing=dp(15), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        # Filter options
        filter_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100))
        filter_layout.add_widget(Label(text="Filter Logs:", size_hint_y=None, height=dp(30), halign='left'))
        
        filter_options = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        self.filter_spinner = Spinner(
            text="All Reports",
            values=["All Reports", "User Reports", "Group Reports", "Message Reports"],
            size_hint_x=0.7
        )
        filter_options.add_widget(self.filter_spinner)
        
        refresh_button = Button(
            text="Refresh",
            size_hint_x=0.3
        )
        refresh_button.bind(on_press=self.refresh_logs)
        filter_options.add_widget(refresh_button)
        
        filter_layout.add_widget(filter_options)
        layout.add_widget(filter_layout)
        
        # Logs list
        logs_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(400))
        
        self.logs_grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None)
        self.logs_grid.bind(minimum_height=self.logs_grid.setter('height'))
        
        # Add some dummy logs
        self.add_log_entries()
        
        logs_scroll = ScrollView(size_hint_y=None, height=dp(400))
        logs_scroll.add_widget(self.logs_grid)
        logs_layout.add_widget(logs_scroll)
        
        layout.add_widget(logs_layout)
        
        # Wrap in scroll view
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(layout)
        return scroll_view
    
    def set_report_type(self, report_type):
        """
        Set report type and update UI accordingly.
        """
        self.report_type = report_type
        
        # Remove all target layouts
        for layout in [self.user_target_layout, self.group_target_layout, self.message_target_layout]:
            if layout.parent:
                layout.parent.remove_widget(layout)
        
        # Add appropriate target layout
        if report_type == "user":
            self.report_layout.children[0].children[0].add_widget(self.user_target_layout, index=len(self.report_layout.children[0].children[0].children)-3)
        elif report_type == "group":
            self.report_layout.children[0].children[0].add_widget(self.group_target_layout, index=len(self.report_layout.children[0].children[0].children)-3)
        elif report_type == "message":
            self.report_layout.children[0].children[0].add_widget(self.message_target_layout, index=len(self.report_layout.children[0].children[0].children)-3)
    
    def load_active_sessions(self):
        """
        Load active sessions from backend.
        """
        # In a real app, you would fetch sessions from the database
        # For now, we'll use dummy data
        self.active_sessions = [
            {"id": 1, "name": "Main Account", "type": "user"},
            {"id": 2, "name": "Secondary Account", "type": "user"},
            {"id": 3, "name": "Bot Account", "type": "bot"}
        ]
        
        # Update sessions grid
        self.update_sessions_grid()
    
    def update_sessions_grid(self):
        """
        Update sessions grid with current active sessions.
        """
        self.sessions_grid.clear_widgets()
        
        for session in self.active_sessions:
            session_item = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60))
            
            # Session info
            info_layout = BoxLayout(orientation='vertical', size_hint_x=0.7)
            info_layout.add_widget(Label(text=session["name"], halign='left', font_size=FontSizes.REGULAR))
            info_layout.add_widget(Label(text=f"Type: {session['type']}", halign='left', font_size=FontSizes.SMALL))
            
            session_item.add_widget(info_layout)
            
            # Remove button
            remove_button = Button(
                text="Remove",
                size_hint_x=0.3,
                background_color=ButtonStyles.DANGER['background_color']
            )
            remove_button.bind(on_press=lambda x, s=session: self.remove_session(s))
            session_item.add_widget(remove_button)
            
            self.sessions_grid.add_widget(session_item)
    
    def add_log_entries(self):
        """
        Add dummy log entries to logs grid.
        """
        self.logs_grid.clear_widgets()
        
        # Dummy log data
        logs = [
            {"id": 1, "type": "user", "target": "@spammer123", "reason": "Spam", "date": "2023-05-15 14:30", "status": "Submitted"},
            {"id": 2, "type": "group", "target": "@scam_group", "reason": "Fake", "date": "2023-05-14 10:15", "status": "Processed"},
            {"id": 3, "type": "message", "target": "Message in @channel", "reason": "Pornography", "date": "2023-05-13 18:45", "status": "Submitted"},
            {"id": 4, "type": "user", "target": "@fake_account", "reason": "Fake Account", "date": "2023-05-12 09:20", "status": "Processed"},
            {"id": 5, "type": "message", "target": "Message in @group", "reason": "Violence", "date": "2023-05-11 16:30", "status": "Submitted"}
        ]
        
        for log in logs:
            log_item = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80), padding=dp(10))
            log_item.canvas.before.clear()
            from kivy.graphics import Color, Rectangle
            with log_item.canvas.before:
                Color(0.9, 0.9, 0.9, 1)  # Light gray background
                Rectangle(pos=log_item.pos, size=log_item.size)
            
            # Header row
            header_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
            header_row.add_widget(Label(text=f"Report #{log['id']} - {log['type'].capitalize()}", halign='left', size_hint_x=0.7, color=(0.2, 0.2, 0.2, 1)))
            header_row.add_widget(Label(text=log['date'], halign='right', size_hint_x=0.3, font_size=FontSizes.SMALL, color=(0.5, 0.5, 0.5, 1)))
            log_item.add_widget(header_row)
            
            # Content row
            content_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
            content_row.add_widget(Label(text=f"Target: {log['target']}", halign='left', size_hint_x=0.7, color=(0.2, 0.2, 0.2, 1)))
            
            status_color = (0.2, 0.6, 0.2, 1) if log['status'] == "Processed" else (0.6, 0.6, 0.2, 1)  # Green for processed, yellow for submitted
            content_row.add_widget(Label(text=log['status'], halign='right', size_hint_x=0.3, color=status_color))
            log_item.add_widget(content_row)
            
            # Reason row
            reason_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(20))
            reason_row.add_widget(Label(text=f"Reason: {log['reason']}", halign='left', font_size=FontSizes.SMALL, color=(0.4, 0.4, 0.4, 1)))
            log_item.add_widget(reason_row)
            
            self.logs_grid.add_widget(log_item)
    
    def add_session(self, instance):
        """
        Add a new session.
        """
        session_string = self.session_input.text.strip()
        
        if not session_string:
            self.status_label.text = "Please enter a session string"
            return
        
        # In a real app, you would validate and add the session to the backend
        # For now, we'll just add a dummy session
        new_session = {
            "id": len(self.active_sessions) + 1,
            "name": f"Session {len(self.active_sessions) + 1}",
            "type": "user"
        }
        
        self.active_sessions.append(new_session)
        self.update_sessions_grid()
        
        self.session_input.text = ""
        self.status_label.text = "Session added successfully"
    
    def remove_session(self, session):
        """
        Remove a session.
        """
        # In a real app, you would remove the session from the backend
        # For now, we'll just remove it from our local list
        self.active_sessions = [s for s in self.active_sessions if s["id"] != session["id"]]
        self.update_sessions_grid()
        
        self.status_label.text = f"Session {session['name']} removed"
    
    def refresh_logs(self, instance):
        """
        Refresh report logs.
        """
        # In a real app, you would fetch logs from the backend based on filter
        # For now, we'll just refresh our dummy logs
        self.add_log_entries()
        
        self.status_label.text = "Logs refreshed"
    
    def submit_report(self, instance):
        """
        Submit a report.
        """
        # Validate inputs
        if self.reason_spinner.text == "Select reason":
            self.status_label.text = "Please select a report reason"
            return
        
        target = ""
        if self.report_type == "user":
            target = self.user_target_input.text.strip()
            if not target:
                self.status_label.text = "Please enter a user ID or username"
                return
        elif self.report_type == "group":
            target = self.group_target_input.text.strip()
            if not target:
                self.status_label.text = "Please enter a group ID or username"
                return
        elif self.report_type == "message":
            chat = self.message_chat_input.text.strip()
            message_id = self.message_id_input.text.strip()
            if not chat or not message_id:
                self.status_label.text = "Please enter both chat and message ID"
                return
            target = f"{chat}:{message_id}"
        
        # Get multi-account setting
        use_multi_account = self.multi_account_toggle.state == "down"
        
        # In a real app, you would call the backend to submit the report
        # For now, we'll just show a success message
        self.status_label.text = f"Submitting {self.report_type} report for {target}..."
        
        # Simulate report submission
        import threading
        threading.Thread(target=self.simulate_report_submission).start()
    
    def simulate_report_submission(self):
        """
        Simulate report submission process.
        """
        import time
        from kivy.clock import Clock
        
        # Simulate progress updates
        time.sleep(1)  # Simulate delay
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', "Validating report details..."), 0)
        
        time.sleep(1)  # Simulate delay
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', "Submitting report..."), 0)
        
        time.sleep(1)  # Simulate delay
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', "Report submitted successfully!"), 0)
        
        # Clear inputs
        Clock.schedule_once(self.clear_report_inputs, 0)
    
    def clear_report_inputs(self, dt):
        """
        Clear report inputs after submission.
        """
        if self.report_type == "user":
            self.user_target_input.text = ""
        elif self.report_type == "group":
            self.group_target_input.text = ""
        elif self.report_type == "message":
            self.message_chat_input.text = ""
            self.message_id_input.text = ""
        
        self.reason_spinner.text = "Select reason"
        self.details_input.text = ""
    
    def go_back(self, instance):
        """
        Go back to dashboard screen.
        """
        self.manager.transition.direction = "right"
        self.manager.current = "dashboard"