"""
Login View for Movie Rental Management System
Clean, professional login interface with secure authentication.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from models.employee_model import EmployeeModel

logger = logging.getLogger(__name__)

class LoginView(ttk.Frame):
    """Login window for employee authentication."""
    
    def __init__(self, parent, login_callback=None):
        """
        Initialize login view.
        
        Args:
            parent: Parent window
            login_callback: Function to call after successful login
        """
        super().__init__(parent)
        self.parent = parent
        self.login_callback = login_callback
        self.employee_model = EmployeeModel()
        
        self.setup_window()
        self.create_widgets()
        self.apply_styling()
        
        # Bind Enter key to login
        self.parent.bind('<Return>', lambda event: self.handle_login())
    
    def setup_window(self):
        """Configure the main window."""
        self.parent.title("Movie Rental System - Login")
        self.parent.geometry("400x500")
        self.parent.resizable(False, False)
        
        # Center the window on screen
        self.parent.eval('tk::PlaceWindow . center')
        
        # Set window icon (if available)
        try:
            self.parent.iconbitmap('assets/icons/app_icon.ico')
        except:
            pass  # Icon file not available
    
    def create_widgets(self):
        """Create and arrange all UI widgets."""
        # Main container with padding
        main_container = ttk.Frame(self, padding="40")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header section
        self.create_header(main_container)
        
        # Login form section
        self.create_login_form(main_container)
        
        # Footer section
        self.create_footer(main_container)
    
    def create_header(self, parent):
        """Create header with logo and title."""
        header_frame = ttk.Frame(parent)
        header_frame.pack(pady=(0, 30))
        
        # Application title
        title_label = ttk.Label(
            header_frame,
            text="Movie Rental System",
            font=('Arial', 20, 'bold'),
            foreground='#2c3e50'
        )
        title_label.pack(pady=(0, 10))
        
        # Subtitle
        subtitle_label = ttk.Label(
            header_frame,
            text="Employee Login",
            font=('Arial', 12),
            foreground='#7f8c8d'
        )
        subtitle_label.pack()
        
        # Separator
        separator = ttk.Separator(parent, orient='horizontal')
        separator.pack(fill=tk.X, pady=20)
    
    def create_login_form(self, parent):
        """Create login form with username and password fields."""
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Username field
        username_label = ttk.Label(
            form_frame,
            text="Username:",
            font=('Arial', 10, 'bold'),
            foreground='#2c3e50'
        )
        username_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.username_entry = ttk.Entry(
            form_frame,
            font=('Arial', 11),
            width=25
        )
        self.username_entry.pack(fill=tk.X, pady=(0, 15))
        self.username_entry.focus()  # Focus on username field by default
        
        # Password field
        password_label = ttk.Label(
            form_frame,
            text="Password:",
            font=('Arial', 10, 'bold'),
            foreground='#2c3e50'
        )
        password_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.password_entry = ttk.Entry(
            form_frame,
            font=('Arial', 11),
            width=25,
            show="•"  # Show bullets for password
        )
        self.password_entry.pack(fill=tk.X, pady=(0, 20))
        
        # Error message label
        self.error_label = ttk.Label(
            form_frame,
            text="",
            font=('Arial', 9),
            foreground='#e74c3c',
            wraplength=300
        )
        self.error_label.pack(pady=(0, 20))
        
        # Login button
        self.login_button = ttk.Button(
            form_frame,
            text="Login",
            command=self.handle_login,
            style='Accent.TButton'
        )
        self.login_button.pack(fill=tk.X, pady=(0, 15))
        
        # Forgot password label (placeholder)
        forgot_label = ttk.Label(
            form_frame,
            text="Forgot password? Contact administrator.",
            font=('Arial', 9),
            foreground='#95a5a6',
            cursor="hand2"
        )
        forgot_label.pack()
        # You can add click event later if needed
    
    def create_footer(self, parent):
        """Create footer with version and copyright."""
        footer_frame = ttk.Frame(parent)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))
        
        # Version info
        version_label = ttk.Label(
            footer_frame,
            text="Version 1.0.0",
            font=('Arial', 8),
            foreground='#bdc3c7'
        )
        version_label.pack()
        
        # Copyright
        copyright_label = ttk.Label(
            footer_frame,
            text="© 2025 Movie Rental System",
            font=('Arial', 8),
            foreground='#bdc3c7'
        )
        copyright_label.pack()
    
    def apply_styling(self):
        """Apply modern styling to widgets."""
        style = ttk.Style()
        
        # Configure styles for modern look
        style.configure('TFrame', background='#ffffff')
        style.configure('TLabel', background='#ffffff')
        style.configure('TButton', font=('Arial', 10))
        
        # Accent button style
        style.configure('Accent.TButton', 
                       font=('Arial', 11, 'bold'),
                       foreground='white',
                       background='#3498db',
                       focuscolor='none')
        
        style.map('Accent.TButton',
                 background=[('active', '#2980b9'),
                           ('pressed', '#2471a3')])
        
        # Entry styling
        style.configure('TEntry', 
                       font=('Arial', 11),
                       padding=8,
                       relief='flat',
                       borderwidth=1)
        
        # Configure the main frame background
        self.configure(style='TFrame')
    
    def handle_login(self):
        """Handle login button click."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        # Validate inputs
        if not username or not password:
            self.show_error("Please enter both username and password")
            return
        
        # Clear previous errors
        self.clear_error()
        
        # Disable login button during authentication
        self.set_login_state(disabled=True)
        
        # Authenticate with employee model
        success, message, employee_data = self.employee_model.login_employee(username, password)
        
        if success:
            self.on_login_success(employee_data)
        else:
            self.on_login_failure(message)
        
        # Re-enable login button
        self.set_login_state(disabled=False)
    
    def set_login_state(self, disabled=True):
        """Enable or disable login controls."""
        state = 'disabled' if disabled else 'normal'
        
        self.username_entry.config(state=state)
        self.password_entry.config(state=state)
        self.login_button.config(state=state)
        
        if disabled:
            self.login_button.config(text="Authenticating...")
        else:
            self.login_button.config(text="Login")
        
        # Update UI immediately
        self.parent.update_idletasks()
    
    def clear_error(self):
        """Clear error message."""
        self.error_label.config(text="")
    
    def show_error(self, message):
        """Display error message."""
        self.error_label.config(text=message)
        # Focus on username field for correction
        self.username_entry.focus()
        self.username_entry.select_range(0, tk.END)
    
    def on_login_success(self, employee_data):
        """Handle successful login."""
        logger.info(f"Login successful for user: {employee_data['username']}")
        
        # Clear password field for security
        self.password_entry.delete(0, tk.END)
        
        # Show success message
        messagebox.showinfo(
            "Login Successful",
            f"Welcome back, {employee_data['first_name']} {employee_data['last_name']}!"
        )
        
        # Call login callback if provided
        if self.login_callback:
            self.login_callback(employee_data)
        else:
            # Default behavior: close login window
            self.parent.destroy()
    
    def on_login_failure(self, message):
        """Handle failed login."""
        logger.warning(f"Login failed: {message}")
        self.show_error(message)
        
        # Clear password field and focus on it for retry
        self.password_entry.delete(0, tk.END)
        self.password_entry.focus()
    
    def clear_form(self):
        """Clear all form fields."""
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.clear_error()
        self.username_entry.focus()

# Demo/test function
def main():
    """Test the login view independently."""
    root = tk.Tk()
    
    def on_login_success(employee_data):
        print(f"Login successful: {employee_data}")
        root.quit()
    
    login_view = LoginView(root, login_callback=on_login_success)
    login_view.pack(fill=tk.BOTH, expand=True)
    
    root.mainloop()

if __name__ == "__main__":
    main()