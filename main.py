"""
Main application entry point - Updated with Login System
"""

import tkinter as tk
from tkinter import messagebox
import logging
from db.setup_database import DatabaseSetup
from ui.views.login_view import LoginView
from ui.views.dashboard import DashboardView

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class MovieRentalApp:
    """Main application class."""
    
    def __init__(self):
        self.root = None
        self.current_user = None
    
    def initialize_application(self):
        """Initialize the application and database."""
        try:
            logger.info("Starting Movie Rental System initialization...")
            
            # Initialize database
            setup = DatabaseSetup()
            if not setup.setup_database():
                messagebox.showerror(
                    "Database Error", 
                    "Failed to initialize database. Please check your MySQL installation and credentials."
                )
                return False
            
            logger.info("Application initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Application initialization failed: {e}")
            messagebox.showerror("Initialization Error", str(e))
            return False
    
    def on_login_success(self, employee_data):
        """Handle successful login."""
        self.current_user = employee_data
        logger.info(f"User logged in: {employee_data['username']}")
        
        # Close login window and open dashboard
        self.root.destroy()
        self.show_dashboard(employee_data)
    
    def show_dashboard(self, employee_data):
        """Show the main dashboard."""
        dashboard_root = tk.Tk()
        dashboard_root.title("Movie Rental System - Dashboard")
        dashboard_root.geometry("1000x700")
        
        from ui.views.dashboard import DashboardView
        dashboard_view = DashboardView(dashboard_root, employee_data)
        dashboard_view.pack(fill=tk.BOTH, expand=True)
        
        # Handle window close
        dashboard_root.protocol("WM_DELETE_WINDOW", self.on_app_close)
        
        dashboard_root.mainloop()
    
    def on_app_close(self):
        """Handle application closure."""
        if self.current_user:
            logger.info(f"User logged out: {self.current_user['username']}")
        logger.info("Application closed")
        self.root.quit()
    
    def run(self):
        """Run the main application."""
        try:
            # Create main window
            self.root = tk.Tk()
            
            # Initialize application
            if not self.initialize_application():
                return
            
            # Show login screen
            login_view = LoginView(self.root, login_callback=self.on_login_success)
            login_view.pack(fill=tk.BOTH, expand=True)
            
            # Handle window close
            self.root.protocol("WM_DELETE_WINDOW", self.on_app_close)
            
            # Start application
            logger.info("Application started successfully")
            self.root.mainloop()
            
        except Exception as e:
            logger.error(f"Application error: {e}")
            messagebox.showerror("Application Error", str(e))
        finally:
            logger.info("Application shutdown")

def main():
    """Main entry point."""
    app = MovieRentalApp()
    app.run()

if __name__ == "__main__":
    main()