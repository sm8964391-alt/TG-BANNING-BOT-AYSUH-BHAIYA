#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Telegram Super-Manager App - Frontend Styles
Theme and styling definitions for the Kivy-based mobile UI.
"""

from kivy.utils import get_color_from_hex
from kivy.metrics import dp

# Theme colors
class ThemeColors:
    # Light theme
    LIGHT = {
        'primary': get_color_from_hex('#2196F3'),  # Blue
        'primary_dark': get_color_from_hex('#1976D2'),
        'accent': get_color_from_hex('#FF4081'),  # Pink
        'background': get_color_from_hex('#FFFFFF'),  # White
        'card': get_color_from_hex('#F5F5F5'),  # Light Gray
        'text_primary': get_color_from_hex('#212121'),  # Almost Black
        'text_secondary': get_color_from_hex('#757575'),  # Gray
        'divider': get_color_from_hex('#BDBDBD'),  # Light Gray
        'success': get_color_from_hex('#4CAF50'),  # Green
        'warning': get_color_from_hex('#FFC107'),  # Amber
        'error': get_color_from_hex('#F44336'),  # Red
        'info': get_color_from_hex('#2196F3'),  # Blue
    }
    
    # Dark theme
    DARK = {
        'primary': get_color_from_hex('#2196F3'),  # Blue
        'primary_dark': get_color_from_hex('#1976D2'),
        'accent': get_color_from_hex('#FF4081'),  # Pink
        'background': get_color_from_hex('#121212'),  # Dark Gray
        'card': get_color_from_hex('#1E1E1E'),  # Slightly lighter Dark Gray
        'text_primary': get_color_from_hex('#FFFFFF'),  # White
        'text_secondary': get_color_from_hex('#B0B0B0'),  # Light Gray
        'divider': get_color_from_hex('#323232'),  # Gray
        'success': get_color_from_hex('#4CAF50'),  # Green
        'warning': get_color_from_hex('#FFC107'),  # Amber
        'error': get_color_from_hex('#F44336'),  # Red
        'info': get_color_from_hex('#2196F3'),  # Blue
    }

# Font sizes
class FontSizes:
    TINY = dp(10)
    SMALL = dp(12)
    MEDIUM = dp(14)
    REGULAR = dp(16)
    LARGE = dp(18)
    XLARGE = dp(20)
    XXLARGE = dp(24)
    XXXLARGE = dp(30)

# Spacing
class Spacing:
    TINY = dp(2)
    SMALL = dp(4)
    MEDIUM = dp(8)
    REGULAR = dp(12)
    LARGE = dp(16)
    XLARGE = dp(24)
    XXLARGE = dp(32)
    XXXLARGE = dp(48)

# Button styles
class ButtonStyles:
    PRIMARY = {
        'background_normal': '',
        'background_color': (0.13, 0.59, 0.95, 1),  # Primary blue
        'color': (1, 1, 1, 1),  # White text
        'font_size': FontSizes.REGULAR,
        'height': dp(50),
        'border_radius': [dp(5),]
    }
    
    SECONDARY = {
        'background_normal': '',
        'background_color': (0.9, 0.9, 0.9, 1),  # Light gray
        'color': (0.13, 0.13, 0.13, 1),  # Dark text
        'font_size': FontSizes.REGULAR,
        'height': dp(50),
        'border_radius': [dp(5),]
    }
    
    DANGER = {
        'background_normal': '',
        'background_color': (0.96, 0.26, 0.21, 1),  # Red
        'color': (1, 1, 1, 1),  # White text
        'font_size': FontSizes.REGULAR,
        'height': dp(50),
        'border_radius': [dp(5),]
    }
    
    SUCCESS = {
        'background_normal': '',
        'background_color': (0.3, 0.69, 0.31, 1),  # Green
        'color': (1, 1, 1, 1),  # White text
        'font_size': FontSizes.REGULAR,
        'height': dp(50),
        'border_radius': [dp(5),]
    }
    
    WARNING = {
        'background_normal': '',
        'background_color': (1, 0.76, 0.03, 1),  # Amber
        'color': (0.13, 0.13, 0.13, 1),  # Dark text
        'font_size': FontSizes.REGULAR,
        'height': dp(50),
        'border_radius': [dp(5),]
    }

# Input styles
class InputStyles:
    DEFAULT = {
        'background_normal': '',
        'background_color': (0.95, 0.95, 0.95, 1),  # Light gray
        'foreground_color': (0.13, 0.13, 0.13, 1),  # Dark text
        'cursor_color': (0.13, 0.59, 0.95, 1),  # Primary blue
        'font_size': FontSizes.REGULAR,
        'height': dp(40),
        'padding': [dp(10), dp(10), dp(10), dp(10)],
        'multiline': False
    }
    
    DARK = {
        'background_normal': '',
        'background_color': (0.2, 0.2, 0.2, 1),  # Dark gray
        'foreground_color': (0.9, 0.9, 0.9, 1),  # Light text
        'cursor_color': (0.13, 0.59, 0.95, 1),  # Primary blue
        'font_size': FontSizes.REGULAR,
        'height': dp(40),
        'padding': [dp(10), dp(10), dp(10), dp(10)],
        'multiline': False
    }

# Card styles
class CardStyles:
    DEFAULT = {
        'background_color': (1, 1, 1, 1),  # White
        'border_radius': [dp(5),],
        'elevation': 1,
        'padding': [dp(16), dp(16), dp(16), dp(16)],
        'spacing': dp(8)
    }
    
    DARK = {
        'background_color': (0.12, 0.12, 0.12, 1),  # Dark gray
        'border_radius': [dp(5),],
        'elevation': 1,
        'padding': [dp(16), dp(16), dp(16), dp(16)],
        'spacing': dp(8)
    }

# Helper function to apply theme
def apply_theme(widget, theme='light'):
    """
    Apply theme to a widget and its children recursively.
    
    Args:
        widget: The Kivy widget to apply theme to
        theme: 'light' or 'dark'
    """
    theme_colors = ThemeColors.LIGHT if theme == 'light' else ThemeColors.DARK
    
    # Apply theme based on widget type
    from kivy.uix.button import Button
    from kivy.uix.textinput import TextInput
    from kivy.uix.label import Label
    from kivy.uix.boxlayout import BoxLayout
    
    if isinstance(widget, Button):
        widget.background_color = theme_colors['primary']
        widget.color = (1, 1, 1, 1) if theme == 'dark' else (1, 1, 1, 1)
    
    elif isinstance(widget, TextInput):
        widget.background_color = theme_colors['card']
        widget.foreground_color = theme_colors['text_primary']
        widget.cursor_color = theme_colors['primary']
    
    elif isinstance(widget, Label):
        widget.color = theme_colors['text_primary']
    
    elif isinstance(widget, BoxLayout):
        widget.canvas.before.clear()
        with widget.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*theme_colors['background'])
            Rectangle(pos=widget.pos, size=widget.size)
    
    # Apply theme to children
    if hasattr(widget, 'children'):
        for child in widget.children:
            apply_theme(child, theme)