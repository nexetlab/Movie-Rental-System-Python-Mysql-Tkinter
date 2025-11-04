"""
Main Dashboard with Toggle Navigation
"""

import tkinter as tk
from tkinter import ttk
import logging
from .movie_management import MovieManagementView
from .customer_management import CustomerManagementView
from .rental_management import RentalManagementView
# Add this import at the top
from .reports_view import ReportsView
from ui.styles.theme import ModernTheme

logger = logging.getLogger(__name__)

class DashboardView(ttk.Frame):
    """Main dashboard view with navigation toggle buttons."""
    
    def __init__(self, parent, employee_data):
        super().__init__(parent)
        self.parent = parent
        self.employee_data = employee_data
        self.current_view = None
        
        # Apply modern theme
        self.theme = ModernTheme()
        self.style, self.colors = self.theme.configure_styles()
        
        self.setup_window()
        self.create_widgets()
        
        # Show default view
        self.show_movie_management()
    
    def setup_window(self):
        """Configure the main window."""
        self.parent.title("Movie Rental System - Dashboard")
        self.parent.geometry("1200x800")
        self.parent.minsize(1000, 600)
    
    def create_widgets(self):
        """Create dashboard widgets."""
        # Main container
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.create_header(main_container)
        
        # Content area
        self.create_content_area(main_container)
    
    def create_header(self, parent):
        """Create header with user info and logout."""
        header_frame = ttk.Frame(parent, style='Header.TFrame')
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Welcome message
        welcome_frame = ttk.Frame(header_frame, style='Header.TFrame')
        welcome_frame.pack(side=tk.LEFT)
        
        welcome_label = ttk.Label(
            welcome_frame,
            text=f"Welcome, {self.employee_data['first_name']} {self.employee_data['last_name']}!",
            font=('Arial', 16, 'bold'),
            style='Header.TLabel'
        )
        welcome_label.pack(anchor=tk.W)
        
        role_label = ttk.Label(
            welcome_frame,
            text=f"Role: {self.employee_data['role'].title()}",
            font=('Arial', 12),
            style='Header.TLabel'
        )
        role_label.pack(anchor=tk.W)
        
        # Logout button
        logout_btn = ttk.Button(
            header_frame,
            text="Logout",
            command=self.logout,
            style='Logout.TButton'
        )
        logout_btn.pack(side=tk.RIGHT)
    
    def create_content_area(self, parent):
        """Create navigation and content area."""
        content_frame = ttk.Frame(parent)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Navigation sidebar
        self.create_navigation_sidebar(content_frame)
        
        # Main content area
        self.create_main_content(content_frame)
    
    def create_navigation_sidebar(self, parent):
        """Create navigation sidebar with toggle buttons."""
        sidebar_frame = ttk.Frame(parent, width=200, style='Sidebar.TFrame')
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar_frame.pack_propagate(False)
        
        # Navigation title
        nav_title = ttk.Label(
            sidebar_frame,
            text="Navigation",
            font=('Arial', 14, 'bold'),
            style='Sidebar.TLabel'
        )
        nav_title.pack(pady=(0, 20))
        
        # Navigation buttons
        nav_buttons = [
            ("🎬 Movie Management", self.show_movie_management),
            ("👥 Customer Management", self.show_customer_management),
            ("📦 Rental Management", self.show_rental_management),
            ("📊 Reports", self.show_reports),
        ]
        
        self.nav_buttons = {}
        for text, command in nav_buttons:
            btn = ttk.Button(
                sidebar_frame,
                text=text,
                command=command,
                style='Nav.TButton',
                width=20
            )
            btn.pack(fill=tk.X, pady=5)
            self.nav_buttons[text] = btn
        
        # Set initial active button
        self.set_active_nav("🎬 Movie Management")
    
    def create_main_content(self, parent):
        """Create main content area where views will be displayed."""
        self.content_frame = ttk.Frame(parent, style='Content.TFrame')
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def set_active_nav(self, active_text):
        """Set active navigation button style."""
        for text, button in self.nav_buttons.items():
            if text == active_text:
                button.configure(style='ActiveNav.TButton')
            else:
                button.configure(style='Nav.TButton')
    
    def clear_content(self):
        """Clear the current content view."""
        if self.current_view:
            self.current_view.destroy()
            self.current_view = None
    
    def show_movie_management(self):
        """Show movie management view."""
        self.clear_content()
        self.set_active_nav("🎬 Movie Management")
        
        self.current_view = MovieManagementView(self.content_frame)
        self.current_view.pack(fill=tk.BOTH, expand=True)
        logger.info("Switched to Movie Management view")
    
    def show_customer_management(self):
        """Show customer management view."""
        self.clear_content()
        self.set_active_nav("👥 Customer Management")
        
        self.current_view = CustomerManagementView(self.content_frame)
        self.current_view.pack(fill=tk.BOTH, expand=True)
        logger.info("Switched to Customer Management view")
    
    def show_rental_management(self):
        """Show rental management view."""
        self.clear_content()
        self.set_active_nav("📦 Rental Management")
        
        self.current_view = RentalManagementView(self.content_frame, self.employee_data)
        self.current_view.pack(fill=tk.BOTH, expand=True)
        logger.info("Switched to Rental Management view")
    
    def show_reports(self):
        """Show reports view."""
        self.clear_content()
        self.set_active_nav("📊 Reports")
        
        self.current_view = ReportsView(self.content_frame)
        self.current_view.pack(fill=tk.BOTH, expand=True)
        logger.info("Switched to Reports view")
    
    def logout(self):
        """Handle logout."""
        from tkinter import messagebox
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            logger.info(f"User logged out: {self.employee_data['username']}")
            self.parent.destroy()
    
    def apply_styling(self):
        """Apply modern styling to dashboard."""
        style = ttk.Style()
        
        # Color scheme
        colors = {
            'primary': '#3498db',
            'primary_dark': '#2980b9',
            'secondary': '#2c3e50',
            'background': '#ecf0f1',
            'surface': '#ffffff',
            'sidebar': '#34495e',
            'text_light': '#ffffff',
            'text_dark': '#2c3e50'
        }
        
        # Configure styles
        style.configure('TFrame', background=colors['background'])
        
        # Header
        style.configure('Header.TFrame', background=colors['surface'])
        style.configure('Header.TLabel', background=colors['surface'], foreground=colors['text_dark'])
        
        # Sidebar
        style.configure('Sidebar.TFrame', background=colors['sidebar'])
        style.configure('Sidebar.TLabel', background=colors['sidebar'], foreground=colors['text_light'])
        
        # Content
        style.configure('Content.TFrame', background=colors['surface'])
        style.configure('Content.TLabel', background=colors['surface'], foreground=colors['text_dark'])
        
        # Navigation buttons
        style.configure('Nav.TButton', 
                       background=colors['sidebar'],
                       foreground=colors['text_light'],
                       borderwidth=0,
                       font=('Arial', 11),
                       focuscolor='none')
        
        style.map('Nav.TButton',
                 background=[('active', '#2c3e50'),
                           ('pressed', '#2c3e50')])
        
        # Active navigation button
        style.configure('ActiveNav.TButton', 
                       background=colors['primary'],
                       foreground=colors['text_light'],
                       borderwidth=0,
                       font=('Arial', 11, 'bold'))
        
        style.map('ActiveNav.TButton',
                 background=[('active', colors['primary_dark']),
                           ('pressed', colors['primary_dark'])])
        
        # Logout button
        style.configure('Logout.TButton',
                       background='#e74c3c',
                       foreground=colors['text_light'])
        
        style.map('Logout.TButton',
                 background=[('active', '#c0392b'),
                           ('pressed', '#c0392b')])