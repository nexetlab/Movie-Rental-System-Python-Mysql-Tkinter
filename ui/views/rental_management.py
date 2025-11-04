"""
Rental Management GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import logging
from models.rental_model import RentalModel
from models.movie_model import MovieModel
from models.customer_model import CustomerModel

logger = logging.getLogger(__name__)

class RentalManagementView(ttk.Frame):
    """Rental management interface with rent/return functionality."""
    
    def __init__(self, parent, employee_data):
        super().__init__(parent)
        self.parent = parent
        self.employee_data = employee_data
        self.rental_model = RentalModel()
        self.movie_model = MovieModel()
        self.customer_model = CustomerModel()
        
        self.create_widgets()
        self.apply_styling()
        self.show_view_rentals()  # Default view
    
    def create_widgets(self):
        """Create rental management widgets."""
        # Title
        title_label = ttk.Label(
            self,
            text="Rental Management",
            font=('Arial', 18, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Mode toggle buttons
        mode_frame = ttk.Frame(self)
        mode_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.create_mode_buttons(mode_frame)
        
        # Content area
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
    
    def create_mode_buttons(self, parent):
        """Create mode toggle buttons."""
        modes = [
            ("📋 View Rentals", self.show_view_rentals),
            ("🎬 Rent Movie", self.show_rent_movie),
            ("↩️ Return Movie", self.show_return_movie),
        ]
        
        for text, command in modes:
            btn = ttk.Button(
                parent,
                text=text,
                command=command,
                style='Mode.TButton',
                width=15
            )
            btn.pack(side=tk.LEFT, padx=5)
    
    def clear_content(self):
        """Clear the content area."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_view_rentals(self):
        """Show view rentals interface."""
        self.clear_content()
        
        # Search filters
        filter_frame = ttk.LabelFrame(self.content_frame, text="Filter Rentals", padding=10)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Filter options
        filter_options = ttk.Frame(filter_frame)
        filter_options.pack(fill=tk.X)
        
        ttk.Label(filter_options, text="Status:").pack(side=tk.LEFT, padx=(0, 5))
        self.status_var = tk.StringVar(value="all")
        status_combo = ttk.Combobox(filter_options, textvariable=self.status_var, 
                                   values=["all", "active", "returned", "overdue"], 
                                   state="readonly", width=10)
        status_combo.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Button(filter_options, text="Apply Filters", 
                  command=self.load_rentals).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(filter_options, text="Show Overdue", 
                  command=self.show_overdue_rentals, style='Warning.TButton').pack(side=tk.LEFT, padx=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.content_frame, text="Rentals", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_rentals_table(results_frame)
        self.load_rentals()
    
    def show_rent_movie(self):
        """Show rent movie interface."""
        self.clear_content()
        
        form_frame = ttk.LabelFrame(self.content_frame, text="Rent Movie", padding=15)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Customer selection
        customer_frame = ttk.Frame(form_frame)
        customer_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(customer_frame, text="Select Customer:").pack(side=tk.LEFT)
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(customer_frame, textvariable=self.customer_var, 
                                          state="readonly", width=40)
        self.customer_combo.pack(side=tk.LEFT, padx=10)
        self.customer_combo.bind('<<ComboboxSelected>>', self.on_customer_select)
        
        ttk.Button(customer_frame, text="Refresh", 
                  command=self.load_customers).pack(side=tk.LEFT)
        
        # Movie selection
        movie_frame = ttk.Frame(form_frame)
        movie_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(movie_frame, text="Select Movie:").pack(side=tk.LEFT)
        self.movie_var = tk.StringVar()
        self.movie_combo = ttk.Combobox(movie_frame, textvariable=self.movie_var, 
                                       state="readonly", width=40)
        self.movie_combo.pack(side=tk.LEFT, padx=10)
        self.movie_combo.bind('<<ComboboxSelected>>', self.on_movie_select)
        
        ttk.Button(movie_frame, text="Refresh", 
                  command=self.load_available_movies).pack(side=tk.LEFT)
        
        # Due date
        due_frame = ttk.Frame(form_frame)
        due_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(due_frame, text="Due Date:").pack(side=tk.LEFT)
        self.due_date_var = tk.StringVar()
        self.due_date_entry = ttk.Entry(due_frame, textvariable=self.due_date_var, width=15)
        self.due_date_entry.pack(side=tk.LEFT, padx=10)
        
        # Set default due date (7 days from now)
        default_due = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        self.due_date_var.set(default_due)
        
        # Rental info
        self.info_frame = ttk.LabelFrame(form_frame, text="Rental Information", padding=10)
        self.info_frame.pack(fill=tk.X, pady=10)
        
        self.rental_info_label = ttk.Label(self.info_frame, text="Select a customer and movie to see rental details")
        self.rental_info_label.pack()
        
        # Rent button
        rent_btn = ttk.Button(form_frame, text="Rent Movie", 
                             command=self.rent_movie, style='Success.TButton')
        rent_btn.pack(pady=20)
        
        # Load data
        self.load_customers()
        self.load_available_movies()
    
    def show_return_movie(self):
        """Show return movie interface."""
        self.clear_content()
        
        form_frame = ttk.LabelFrame(self.content_frame, text="Return Movie", padding=15)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Active rentals list
        ttk.Label(form_frame, text="Select Rental to Return:", 
                 font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        # Create active rentals table
        tree_frame = ttk.Frame(form_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        columns = ('Rental ID', 'Customer', 'Movie', 'Rental Date', 'Due Date', 'Days Overdue')
        self.return_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.return_tree.heading(col, text=col)
            self.return_tree.column(col, width=100)
        
        self.return_tree.column('Customer', width=120)
        self.return_tree.column('Movie', width=150)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.return_tree.yview)
        self.return_tree.configure(yscrollcommand=scrollbar.set)
        
        self.return_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.return_tree.bind('<<TreeviewSelect>>', self.on_return_select)
        
        # Return info
        self.return_info_frame = ttk.LabelFrame(form_frame, text="Return Information", padding=10)
        self.return_info_frame.pack(fill=tk.X, pady=10)
        
        self.return_info_label = ttk.Label(self.return_info_frame, text="Select a rental to see return details")
        self.return_info_label.pack()
        
        # Return button
        self.return_btn = ttk.Button(form_frame, text="Return Movie", 
                                    command=self.return_movie, style='Primary.TButton',
                                    state='disabled')
        self.return_btn.pack(pady=20)
        
        # Load active rentals
        self.load_active_rentals()
    
    def create_rentals_table(self, parent):
        """Create rentals results table."""
        # Create treeview with scrollbar
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = ('Rental ID', 'Customer', 'Movie', 'Rental Date', 'Due Date', 
                  'Return Date', 'Status', 'Total Charge', 'Late Fee')
        self.rentals_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        for col in columns:
            self.rentals_tree.heading(col, text=col)
            self.rentals_tree.column(col, width=90)
        
        # Specific column widths
        self.rentals_tree.column('Customer', width=120)
        self.rentals_tree.column('Movie', width=150)
        self.rentals_tree.column('Rental Date', width=100)
        self.rentals_tree.column('Due Date', width=100)
        self.rentals_tree.column('Return Date', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.rentals_tree.yview)
        self.rentals_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        self.rentals_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def apply_styling(self):
        """Apply styling to widgets."""
        style = ttk.Style()
        
        # Mode buttons
        style.configure('Mode.TButton', font=('Arial', 10, 'bold'))
        
        # Color buttons
        for color, hex_color in [('Success.TButton', '#27ae60'), ('Primary.TButton', '#3498db'), 
                               ('Warning.TButton', '#f39c12'), ('Danger.TButton', '#e74c3c')]:
            style.configure(color, background=hex_color, foreground='white')
    
    def load_rentals(self):
        """Load rentals based on filters."""
        status = self.status_var.get()
        status = None if status == "all" else status
        
        success, message, rentals = self.rental_model.search_rentals(status=status)
        if success:
            self.populate_rentals_table(rentals)
        else:
            messagebox.showerror("Error", message)
    
    def populate_rentals_table(self, rentals):
        """Populate rentals table with data."""
        # Clear existing data
        for item in self.rentals_tree.get_children():
            self.rentals_tree.delete(item)
        
        # Add rentals to table
        for rental in rentals:
            self.rentals_tree.insert('', tk.END, values=(
                rental['rental_id'],
                f"{rental['customer_first_name']} {rental['customer_last_name']}",
                rental['movie_title'],
                rental['rental_date'].strftime('%Y-%m-%d'),
                rental['due_date'].strftime('%Y-%m-%d'),
                rental['actual_return_date'].strftime('%Y-%m-%d') if rental['actual_return_date'] else '',
                rental['rental_status'].title(),
                f"${rental['total_charge']:.2f}",
                f"${rental['late_fee']:.2f}"
            ))
    
    def show_overdue_rentals(self):
        """Show overdue rentals."""
        success, message, rentals = self.rental_model.get_overdue_rentals()
        if success:
            self.populate_rentals_table(rentals)
        else:
            messagebox.showerror("Error", message)
    
    def load_customers(self):
        """Load customers for combo box."""
        success, message, customers = self.customer_model.get_all_customers()
        if success:
            customer_list = [f"{c['customer_id']}: {c['first_name']} {c['last_name']}" for c in customers]
            self.customer_combo['values'] = customer_list
        else:
            messagebox.showerror("Error", message)
    
    def load_available_movies(self):
        """Load available movies for combo box."""
        success, message, movies = self.movie_model.search_movies(available_only=True)
        if success:
            movie_list = [f"{m['movie_id']}: {m['title']} (${m['rental_rate']:.2f}/day)" for m in movies]
            self.movie_combo['values'] = movie_list
        else:
            messagebox.showerror("Error", message)
    
    def on_customer_select(self, event):
        """Handle customer selection."""
        self.update_rental_info()
    
    def on_movie_select(self, event):
        """Handle movie selection."""
        self.update_rental_info()
    
    def update_rental_info(self):
        """Update rental information display."""
        customer_text = self.customer_var.get()
        movie_text = self.movie_var.get()
        due_date = self.due_date_var.get()
        
        if customer_text and movie_text and due_date:
            try:
                # Extract movie ID and get movie details
                movie_id = int(movie_text.split(':')[0])
                success, message, movie = self.movie_model.get_movie_by_id(movie_id)
                
                if success:
                    # Calculate rental days and charge
                    rental_days = (datetime.strptime(due_date, '%Y-%m-%d') - datetime.now()).days
                    if rental_days > 0:
                        total_charge = movie['rental_rate'] * rental_days
                        
                        info_text = (f"Rental Details:\n"
                                   f"• Movie: {movie['title']}\n"
                                   f"• Rental Rate: ${movie['rental_rate']:.2f}/day\n"
                                   f"• Rental Period: {rental_days} days\n"
                                   f"• Total Charge: ${total_charge:.2f}")
                        
                        self.rental_info_label.config(text=info_text)
                    else:
                        self.rental_info_label.config(text="Error: Due date must be in the future")
                else:
                    self.rental_info_label.config(text="Error: Could not load movie details")
                    
            except ValueError:
                self.rental_info_label.config(text="Error: Invalid selection")
        else:
            self.rental_info_label.config(text="Select a customer and movie to see rental details")
    
    def rent_movie(self):
        """Process movie rental."""
        customer_text = self.customer_var.get()
        movie_text = self.movie_var.get()
        due_date_str = self.due_date_var.get()
        
        if not all([customer_text, movie_text, due_date_str]):
            messagebox.showerror("Error", "Please select customer, movie, and due date")
            return
        
        try:
            customer_id = int(customer_text.split(':')[0])
            movie_id = int(movie_text.split(':')[0])
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            
            # Rent the movie
            success, message, rental_id = self.rental_model.rent_movie(
                customer_id, movie_id, self.employee_data['employee_id'], due_date
            )
            
            if success:
                messagebox.showinfo("Success", message)
                # Clear form
                self.customer_var.set('')
                self.movie_var.set('')
                self.load_available_movies()  # Refresh available movies
                self.rental_info_label.config(text="Select a customer and movie to see rental details")
            else:
                messagebox.showerror("Error", message)
                
        except ValueError as e:
            messagebox.showerror("Error", "Invalid data format")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def load_active_rentals(self):
        """Load active rentals for return."""
        success, message, rentals = self.rental_model.get_active_rentals()
        if success:
            self.populate_return_table(rentals)
        else:
            messagebox.showerror("Error", message)
    
    def populate_return_table(self, rentals):
        """Populate return table with active rentals."""
        # Clear existing data
        for item in self.return_tree.get_children():
            self.return_tree.delete(item)
        
        # Add rentals to table
        for rental in rentals:
            due_date = rental['due_date']
            today = datetime.now().date()
            days_overdue = max(0, (today - due_date).days)
            
            self.return_tree.insert('', tk.END, values=(
                rental['rental_id'],
                f"{rental['customer_first_name']} {rental['customer_last_name']}",
                rental['movie_title'],
                rental['rental_date'].strftime('%Y-%m-%d'),
                due_date.strftime('%Y-%m-%d'),
                days_overdue if days_overdue > 0 else ''
            ))
    
    def on_return_select(self, event):
        """Handle rental selection for return."""
        selection = self.return_tree.selection()
        if selection:
            item = selection[0]
            values = self.return_tree.item(item, 'values')
            rental_id = int(values[0])
            
            # Calculate late fee
            due_date = datetime.strptime(values[4], '%Y-%m-%d').date()
            late_days, late_fee = self.rental_model.calculate_late_fee(due_date)
            
            info_text = (f"Return Details:\n"
                       f"• Rental ID: {rental_id}\n"
                       f"• Customer: {values[1]}\n"
                       f"• Movie: {values[2]}\n"
                       f"• Due Date: {values[4]}\n"
                       f"• Days Overdue: {late_days}\n"
                       f"• Late Fee: ${late_fee:.2f}")
            
            self.return_info_label.config(text=info_text)
            self.selected_rental_id = rental_id
            self.return_btn.config(state='normal')
        else:
            self.return_info_label.config(text="Select a rental to see return details")
            self.selected_rental_id = None
            self.return_btn.config(state='disabled')
    
    def return_movie(self):
        """Process movie return."""
        if not hasattr(self, 'selected_rental_id') or not self.selected_rental_id:
            messagebox.showerror("Error", "Please select a rental to return")
            return
        
        if messagebox.askyesno("Confirm Return", "Are you sure you want to return this movie?"):
            success, message, return_data = self.rental_model.return_movie(
                self.selected_rental_id, self.employee_data['employee_id']
            )
            
            if success:
                messagebox.showinfo("Success", message)
                # Refresh the interface
                self.load_active_rentals()
                self.return_info_label.config(text="Select a rental to see return details")
                self.return_btn.config(state='disabled')
            else:
                messagebox.showerror("Error", message)