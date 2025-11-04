"""
Modern theme configuration for Tkinter widgets with contemporary styling.
"""

import tkinter as tk
from tkinter import ttk
import logging

logger = logging.getLogger(__name__)

class ModernTheme:
    """Modern theme configuration with contemporary colors and styling."""
    
    def __init__(self):
        self.colors = {
            # Modern color palette
            'primary': '#4361ee',      # Vibrant blue
            'primary_dark': '#3a56d4', # Darker blue
            'secondary': '#7209b7',    # Purple
            'accent': '#f72585',       # Pink accent
            'success': '#4cc9f0',      # Cyan success
            'warning': '#f8961e',      # Orange warning
            'error': '#e63946',        # Red error
            'dark': '#1d3557',         # Dark blue
            'light': '#f1faee',        # Light background
            'white': '#ffffff',        # Pure white
            'gray_light': '#a8dadc',   # Light gray
            'gray_dark': '#457b9d',    # Dark gray
            'background': '#f8f9fa',   # Page background
            'surface': '#ffffff',      # Card surface
            'text_primary': '#1d3557', # Primary text
            'text_secondary': '#457b9d', # Secondary text
            'border': '#dee2e6'        # Border color
        }
        
        self.fonts = {
            'h1': ('Segoe UI', 24, 'bold'),
            'h2': ('Segoe UI', 20, 'bold'),
            'h3': ('Segoe UI', 16, 'bold'),
            'body': ('Segoe UI', 11),
            'body_bold': ('Segoe UI', 11, 'bold'),
            'caption': ('Segoe UI', 10),
            'button': ('Segoe UI', 11, 'bold')
        }
    
    def configure_styles(self):
        """Configure modern ttk styles."""
        style = ttk.Style()
        
        # Use a modern theme as base
        available_themes = style.theme_names()
        if 'vista' in available_themes:
            style.theme_use('vista')
        elif 'xpnative' in available_themes:
            style.theme_use('xpnative')
        else:
            style.theme_use('clam')
        
        # Configure main styles
        self._configure_base_styles(style)
        self._configure_button_styles(style)
        self._configure_frame_styles(style)
        self._configure_entry_styles(style)
        self._configure_treeview_styles(style)
        self._configure_label_styles(style)
        self._configure_combobox_styles(style)
        
        return style, self.colors
    
    def _configure_base_styles(self, style):
        """Configure base widget styles."""
        style.configure('.', 
                       background=self.colors['background'],
                       foreground=self.colors['text_primary'],
                       font=self.fonts['body'])
        
        style.configure('TFrame', background=self.colors['background'])
        style.configure('TLabel', background=self.colors['background'])
        style.configure('TLabelframe', 
                       background=self.colors['background'],
                       relief='flat',
                       borderwidth=1)
        style.configure('TLabelframe.Label', 
                       background=self.colors['surface'],
                       foreground=self.colors['text_primary'],
                       font=self.fonts['body_bold'])
    
    def _configure_button_styles(self, style):
        """Configure modern button styles."""
        # Primary button
        style.configure('Primary.TButton',
                       background=self.colors['primary'],
                       foreground=self.colors['white'],
                       borderwidth=0,
                       focuscolor='none',
                       font=self.fonts['button'],
                       padding=(20, 10))
        
        style.map('Primary.TButton',
                 background=[('active', self.colors['primary_dark']),
                           ('pressed', self.colors['primary_dark'])])
        
        # Secondary button
        style.configure('Secondary.TButton',
                       background=self.colors['secondary'],
                       foreground=self.colors['white'],
                       borderwidth=0,
                       focuscolor='none',
                       font=self.fonts['button'],
                       padding=(20, 10))
        
        style.map('Secondary.TButton',
                 background=[('active', '#5a08a0'),
                           ('pressed', '#5a08a0')])
        
        # Success button
        style.configure('Success.TButton',
                       background=self.colors['success'],
                       foreground=self.colors['dark'],
                       borderwidth=0,
                       focuscolor='none',
                       font=self.fonts['button'],
                       padding=(20, 10))
        
        # Warning button
        style.configure('Warning.TButton',
                       background=self.colors['warning'],
                       foreground=self.colors['white'],
                       borderwidth=0,
                       focuscolor='none',
                       font=self.fonts['button'],
                       padding=(20, 10))
        
        # Danger button
        style.configure('Danger.TButton',
                       background=self.colors['error'],
                       foreground=self.colors['white'],
                       borderwidth=0,
                       focuscolor='none',
                       font=self.fonts['button'],
                       padding=(20, 10))
        
        # Accent button
        style.configure('Accent.TButton',
                       background=self.colors['accent'],
                       foreground=self.colors['white'],
                       borderwidth=0,
                       focuscolor='none',
                       font=self.fonts['button'],
                       padding=(20, 10))
    
    def _configure_frame_styles(self, style):
        """Configure modern frame styles."""
        # Card frame (elevated)
        style.configure('Card.TFrame',
                       background=self.colors['surface'],
                       relief='raised',
                       borderwidth=1)
        
        # Header frame
        style.configure('Header.TFrame',
                       background=self.colors['dark'])
        
        style.configure('Header.TLabel',
                       background=self.colors['dark'],
                       foreground=self.colors['white'],
                       font=self.fonts['h3'])
        
        # Sidebar frame
        style.configure('Sidebar.TFrame',
                       background=self.colors['dark'])
        
        style.configure('Sidebar.TLabel',
                       background=self.colors['dark'],
                       foreground=self.colors['white'])
    
    def _configure_entry_styles(self, style):
        """Configure modern entry styles."""
        style.configure('TEntry',
                       fieldbackground=self.colors['white'],
                       background=self.colors['white'],
                       borderwidth=1,
                       relief='solid',
                       padding=(8, 6))
        
        style.map('TEntry',
                 fieldbackground=[('focus', self.colors['white']),
                                ('disabled', self.colors['gray_light'])],
                 foreground=[('disabled', self.colors['gray_dark'])])
    
    def _configure_treeview_styles(self, style):
        """Configure modern treeview styles."""
        style.configure('Treeview',
                       background=self.colors['white'],
                       foreground=self.colors['text_primary'],
                       fieldbackground=self.colors['white'],
                       borderwidth=0,
                       font=self.fonts['body'])
        
        style.configure('Treeview.Heading',
                       background=self.colors['primary'],
                       foreground=self.colors['white'],
                       borderwidth=0,
                       font=self.fonts['body_bold'],
                       padding=(10, 5))
        
        style.map('Treeview',
                 background=[('selected', self.colors['primary']),
                           ('focus', self.colors['primary'])],
                 foreground=[('selected', self.colors['white'])])
        
        style.map('Treeview.Heading',
                 background=[('active', self.colors['primary_dark'])])
    
    def _configure_label_styles(self, style):
        """Configure modern label styles."""
        style.configure('Title.TLabel',
                       font=self.fonts['h1'],
                       foreground=self.colors['text_primary'])
        
        style.configure('Subtitle.TLabel',
                       font=self.fonts['h2'],
                       foreground=self.colors['text_primary'])
        
        style.configure('Heading.TLabel',
                       font=self.fonts['h3'],
                       foreground=self.colors['text_primary'])
        
        style.configure('Body.TLabel',
                       font=self.fonts['body'],
                       foreground=self.colors['text_primary'])
        
        style.configure('Caption.TLabel',
                       font=self.fonts['caption'],
                       foreground=self.colors['text_secondary'])
    
    def _configure_combobox_styles(self, style):
        """Configure modern combobox styles."""
        style.configure('TCombobox',
                       fieldbackground=self.colors['white'],
                       background=self.colors['white'],
                       borderwidth=1,
                       relief='solid',
                       padding=(8, 6))
        
        style.map('TCombobox',
                 fieldbackground=[('focus', self.colors['white']),
                                ('disabled', self.colors['gray_light'])],
                 foreground=[('disabled', self.colors['gray_dark'])])